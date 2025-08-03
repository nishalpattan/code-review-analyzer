"""
Email utilities for sending analysis reports
"""
import json
import structlog
from typing import Dict, Any
from datetime import datetime

logger = structlog.get_logger()

def format_analysis_report(results: Dict[str, Any], repository_name: str) -> str:
    """Format analysis results into a readable email report"""
    
    report = f"""
Code Analysis Report - {repository_name}
{'=' * 50}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY SCORES:
📊 Confidence Score: {results.get('confidence_score', 'N/A')}/100
📊 Quality Score: {results.get('quality_score', 'N/A')}/100

DETAILED METRICS:
🔍 Pylint Score: {results.get('pylint', {}).get('score', 'N/A')}/10
🚨 Security Issues (Bandit): {results.get('bandit', {}).get('total_issues', 'N/A')}
🔄 Average Complexity: {results.get('complexity', {}).get('average_complexity', 'N/A')}
🎨 Style Issues: {results.get('style', {}).get('total_issues', 'N/A')}
💀 Dead Code Lines: {results.get('dead_code', {}).get('dead_code_lines', 'N/A')}

PROJECT STATISTICS:
📁 Total Files: {results.get('total_files', 'N/A')}
📝 Total Lines: {results.get('total_lines', 'N/A')}
⏱️ Analysis Duration: {results.get('analysis_duration', 'N/A')} seconds

SECURITY ANALYSIS:
"""
    
    # Add security issues if any
    bandit_results = results.get('bandit', {}).get('issues', [])
    if bandit_results:
        report += f"Found {len(bandit_results)} security issues:\n"
        for i, issue in enumerate(bandit_results[:5], 1):  # Show first 5 issues
            report += f"  {i}. {issue.get('issue_text', 'Security issue')} (Severity: {issue.get('issue_severity', 'Unknown')})\n"
        if len(bandit_results) > 5:
            report += f"  ... and {len(bandit_results) - 5} more issues\n"
    else:
        report += "✅ No security issues found!\n"
    
    report += f"""
CODE QUALITY ISSUES:
"""
    
    # Add pylint issues if any
    pylint_results = results.get('pylint', {}).get('issues', [])
    if pylint_results:
        report += f"Found {len(pylint_results)} code quality issues:\n"
        for i, issue in enumerate(pylint_results[:5], 1):  # Show first 5 issues
            report += f"  {i}. {issue.get('message', 'Code quality issue')} (Line: {issue.get('line', 'Unknown')})\n"
        if len(pylint_results) > 5:
            report += f"  ... and {len(pylint_results) - 5} more issues\n"
    else:
        report += "✅ No major code quality issues found!\n"
    
    report += f"""
RECOMMENDATIONS:
"""
    
    # Add recommendations based on scores
    confidence_score = results.get('confidence_score', 0)
    if confidence_score >= 80:
        report += "🎉 Excellent code quality! Keep up the good work.\n"
    elif confidence_score >= 60:
        report += "👍 Good code quality with room for improvement.\n"
    else:
        report += "⚠️ Code quality needs attention. Consider addressing the issues found.\n"
    
    report += f"""
---
This report was generated automatically by Code Review Analyzer.
For detailed results, check the API response or web dashboard.
"""
    
    return report

def save_report_to_file(report: str, repository_name: str) -> str:
    """Save the report to a file and return the file path"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"analysis_report_{repository_name}_{timestamp}.txt"
    filepath = f"/tmp/{filename}"
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Failed to save report: {str(e)}")
        return None

def send_analysis_report(results: Dict[str, Any], repository_name: str, recipient_email: str = "nishal.pattan@gmail.com"):
    """Send analysis report via email (simulated for demo)"""
    try:
        # Format the report
        report = format_analysis_report(results, repository_name)
        
        # Save to file (since we don't have SMTP configured)
        filepath = save_report_to_file(report, repository_name)
        
        # Log the email sending (simulated)
        logger.info(f"📧 Analysis report would be sent to: {recipient_email}")
        logger.info(f"📄 Report saved locally: {filepath}")
        logger.info(f"📊 Summary: Confidence Score: {results.get('confidence_score', 'N/A')}/100")
        
        # In production, you would actually send the email here:
        # send_smtp_email(recipient_email, "Code Analysis Report", report)
        
        return True
    except Exception as e:
        logger.error(f"Failed to send analysis report: {str(e)}")
        return False
