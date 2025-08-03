"""
Core analysis engine for code quality assessment
"""
import subprocess
import json
import tempfile
import os
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
import structlog

from app.core.config import settings

logger = structlog.get_logger()

class CodeAnalyzer:
    """Main code analysis engine"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.results = {}
        
    def analyze_all(self) -> Dict[str, Any]:
        """Run all available analyses"""
        start_time = time.time()
        
        try:
            # Run individual analyzers
            self.results['pylint'] = self._run_pylint()
            self.results['bandit'] = self._run_bandit()
            self.results['complexity'] = self._run_radon()
            self.results['style'] = self._run_flake8()
            self.results['dead_code'] = self._run_vulture()
            
            # Calculate overall scores
            self.results['confidence_score'] = self._calculate_confidence_score()
            self.results['quality_score'] = self._calculate_quality_score()
            
            # Metadata
            self.results['analysis_duration'] = time.time() - start_time
            self.results['total_files'] = self._count_python_files()
            self.results['total_lines'] = self._count_total_lines()
            
            logger.info("Analysis completed", duration=self.results['analysis_duration'])
            return self.results
            
        except Exception as e:
            logger.error("Analysis failed", error=str(e))
            raise
    
    def _run_pylint(self) -> Dict[str, Any]:
        """Run pylint analysis"""
        try:
            cmd = [
                'pylint',
                '--output-format=json',
                '--disable=C0103,C0111',  # Disable some overly strict rules
                str(self.repo_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            
            # Pylint returns non-zero exit codes for issues, which is expected
            if result.stdout:
                issues = json.loads(result.stdout)
            else:
                issues = []
            
            # Calculate pylint score (10 - (issues per file))
            python_files = self._count_python_files()
            if python_files > 0:
                score = max(0, 10 - (len(issues) / python_files))
            else:
                score = 10
            
            return {
                'score': score,
                'issues': issues,
                'issue_count': len(issues)
            }
            
        except subprocess.CalledProcessError as e:
            logger.warning("Pylint analysis failed", error=str(e))
            return {'score': 0, 'issues': [], 'issue_count': 0, 'error': str(e)}
        except Exception as e:
            logger.error("Pylint execution error", error=str(e))
            return {'score': 0, 'issues': [], 'issue_count': 0, 'error': str(e)}
    
    def _run_bandit(self) -> Dict[str, Any]:
        """Run bandit security analysis"""
        try:
            cmd = [
                'bandit',
                '-r',
                '-f', 'json',
                str(self.repo_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            
            if result.stdout:
                data = json.loads(result.stdout)
                issues = data.get('results', [])
            else:
                issues = []
            
            # Categorize by severity
            high_issues = [i for i in issues if i.get('issue_severity') == 'HIGH']
            medium_issues = [i for i in issues if i.get('issue_severity') == 'MEDIUM']
            low_issues = [i for i in issues if i.get('issue_severity') == 'LOW']
            
            return {
                'total_issues': len(issues),
                'high_issues': len(high_issues),
                'medium_issues': len(medium_issues),
                'low_issues': len(low_issues),
                'issues': issues
            }
            
        except subprocess.CalledProcessError as e:
            logger.warning("Bandit analysis failed", error=str(e))
            return {'total_issues': 0, 'issues': [], 'error': str(e)}
        except Exception as e:
            logger.error("Bandit execution error", error=str(e))
            return {'total_issues': 0, 'issues': [], 'error': str(e)}
    
    def _run_radon(self) -> Dict[str, Any]:
        """Run radon complexity analysis"""
        try:
            cmd = [
                'radon',
                'cc',
                '-j',  # JSON output
                str(self.repo_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            
            if result.stdout:
                data = json.loads(result.stdout)
            else:
                data = {}
            
            # Calculate average complexity
            total_complexity = 0
            function_count = 0
            
            for file_path, file_data in data.items():
                for item in file_data:
                    if item.get('type') in ['function', 'method']:
                        total_complexity += item.get('complexity', 0)
                        function_count += 1
            
            avg_complexity = (total_complexity / function_count) if function_count > 0 else 0
            
            return {
                'average_complexity': avg_complexity,
                'total_functions': function_count,
                'complexity_data': data
            }
            
        except subprocess.CalledProcessError as e:
            logger.warning("Radon analysis failed", error=str(e))
            return {'average_complexity': 0, 'total_functions': 0, 'error': str(e)}
        except Exception as e:
            logger.error("Radon execution error", error=str(e))
            return {'average_complexity': 0, 'total_functions': 0, 'error': str(e)}
    
    def _run_flake8(self) -> Dict[str, Any]:
        """Run flake8 style analysis"""
        try:
            cmd = [
                'flake8',
                '--format=json',
                str(self.repo_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            
            # Parse flake8 output (it doesn't output valid JSON by default)
            issues = []
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(':', 4)
                        if len(parts) >= 4:
                            issues.append({
                                'file': parts[0],
                                'line': int(parts[1]) if parts[1].isdigit() else 0,
                                'column': int(parts[2]) if parts[2].isdigit() else 0,
                                'code': parts[3].strip(),
                                'message': parts[4].strip() if len(parts) > 4 else ''
                            })
            
            return {
                'total_issues': len(issues),
                'issues': issues
            }
            
        except subprocess.CalledProcessError as e:
            logger.warning("Flake8 analysis failed", error=str(e))
            return {'total_issues': 0, 'issues': [], 'error': str(e)}
        except Exception as e:
            logger.error("Flake8 execution error", error=str(e))
            return {'total_issues': 0, 'issues': [], 'error': str(e)}
    
    def _run_vulture(self) -> Dict[str, Any]:
        """Run vulture dead code analysis"""
        try:
            cmd = [
                'vulture',
                str(self.repo_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.repo_path)
            
            # Parse vulture output
            dead_code_lines = 0
            issues = []
            
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line and ':' in line:
                        dead_code_lines += 1
                        issues.append(line.strip())
            
            return {
                'dead_code_lines': dead_code_lines,
                'issues': issues
            }
            
        except subprocess.CalledProcessError as e:
            logger.warning("Vulture analysis failed", error=str(e))
            return {'dead_code_lines': 0, 'issues': [], 'error': str(e)}
        except Exception as e:
            logger.error("Vulture execution error", error=str(e))
            return {'dead_code_lines': 0, 'issues': [], 'error': str(e)}
    
    def _calculate_confidence_score(self) -> float:
        """Calculate overall confidence score (0-100)"""
        try:
            # Get individual scores
            pylint_score = self.results.get('pylint', {}).get('score', 0)
            bandit_issues = self.results.get('bandit', {}).get('total_issues', 0)
            complexity = self.results.get('complexity', {}).get('average_complexity', 0)
            style_issues = self.results.get('style', {}).get('total_issues', 0)
            
            # Normalize scores (0-10 scale)
            pylint_normalized = min(10, max(0, pylint_score))
            bandit_normalized = max(0, 10 - (bandit_issues * 0.5))  # Penalize security issues
            complexity_normalized = max(0, 10 - complexity)  # Lower complexity is better
            style_normalized = max(0, 10 - (style_issues * 0.1))  # Penalize style issues
            
            # Weighted average
            confidence = (
                pylint_normalized * settings.PYLINT_WEIGHT +
                bandit_normalized * settings.BANDIT_WEIGHT +
                complexity_normalized * settings.COMPLEXITY_WEIGHT +
                style_normalized * settings.CODE_STYLE_WEIGHT
            ) / (settings.PYLINT_WEIGHT + settings.BANDIT_WEIGHT + 
                 settings.COMPLEXITY_WEIGHT + settings.CODE_STYLE_WEIGHT)
            
            # Convert to 0-100 scale
            return min(100, max(0, confidence * 10))
            
        except Exception as e:
            logger.error("Confidence score calculation failed", error=str(e))
            return 0.0
    
    def _calculate_quality_score(self) -> float:
        """Calculate overall quality score (0-100)"""
        # For now, use the same logic as confidence score
        # In the future, this could include additional metrics like test coverage
        return self._calculate_confidence_score()
    
    def _count_python_files(self) -> int:
        """Count total Python files in the repository"""
        count = 0
        for file_path in self.repo_path.rglob("*.py"):
            if file_path.is_file():
                count += 1
        return count
    
    def _count_total_lines(self) -> int:
        """Count total lines of code in Python files"""
        total_lines = 0
        for file_path in self.repo_path.rglob("*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        total_lines += len(f.readlines())
                except Exception:
                    continue  # Skip files that can't be read
        return total_lines
