"""
Utility functions for code analysis
"""
from sqlalchemy.orm import Session
import structlog
from app.utils.git_utils import clone_or_copy_repository, extract_repo_info, get_commit_hash

from app.models.models import Repository, Analysis
from app.models.schemas import AnalysisCreate, AnalysisResponse
from app.analysis.analyzer import CodeAnalyzer
from app.core.config import settings
import json
from app.utils.email_utils import send_analysis_report

logger = structlog.get_logger()

def analyze_repository(
    repository: Repository,
    analysis_request: AnalysisCreate,
    db: Session
) -> AnalysisResponse:
    """
    Perform a full analysis of the given repository
    """
    # Create Analysis record
    analysis = Analysis(
        repository_id=repository.id,
        commit_hash=analysis_request.commit_hash,
        status="running"
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    analysis_id = analysis.id

    repo_info = extract_repo_info(repository.url)
    repo_path = clone_or_copy_repository(repo_url=repository.url, repo_name=repo_info['name'], branch=repository.branch)
    try:
        # Run code analysis
        analyzer = CodeAnalyzer(repo_path=repo_path)
        results = analyzer.analyze_all()

        # Send the report
        send_analysis_report(results, repo_info['name'], settings.REPORT_EMAIL)

        # Update analysis record
        analysis.confidence_score = results['confidence_score']
        analysis.quality_score = results['quality_score']
        analysis.total_files = results['total_files']
        analysis.total_lines = results['total_lines']
        analysis.analysis_duration = results['analysis_duration']
        analysis.status = "completed"
        analysis.pylint_score = results['pylint']['score']
        analysis.bandit_issues = results['bandit']['total_issues']
        analysis.complexity_score = results['complexity']['average_complexity']
        analysis.code_style_issues = results['style']['total_issues']
        analysis.dead_code_lines = results['dead_code']['dead_code_lines']

        # Store detailed results (JSON)
        analysis.pylint_results = results['pylint']  # Store complete pylint results dict
        analysis.bandit_results = results['bandit']  # Store complete bandit results dict
        analysis.complexity_results = results['complexity']['complexity_data']
        analysis.style_results = results['style']  # Store complete style results dict

        db.commit()
    except Exception as e:
        analysis.status = "failed"
        logger.error(f"Analysis {analysis_id} failed", error=str(e))
        db.commit()


    db.refresh(analysis)
    return analysis
