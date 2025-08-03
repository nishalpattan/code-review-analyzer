"""
Git utilities for repository operations
"""
import os
import tempfile
import shutil
import git
from urllib.parse import urlparse
from pathlib import Path
import structlog

logger = structlog.get_logger()

def is_git_url(url: str) -> bool:
    """Check if a URL is a valid Git repository URL"""
    parsed = urlparse(url)
    return (
        parsed.scheme in ['http', 'https', 'git', 'ssh'] or
        url.startswith('git@') or
        url.endswith('.git')
    )

def is_local_path(path: str) -> bool:
    """Check if path is a local directory"""
    return os.path.isdir(path)

def clone_or_copy_repository(repo_url: str, repo_name: str, branch: str = "main") -> str:
    """
    Clone a Git repository or copy a local directory to a temporary location
    Returns the path to the temporary directory
    """
    temp_dir = tempfile.mkdtemp()
    target_path = os.path.join(temp_dir, repo_name)
    
    try:
        if is_git_url(repo_url):
            logger.info("Cloning Git repository", url=repo_url, branch=branch)
            git.Repo.clone_from(
                repo_url, 
                target_path, 
                branch=branch,
                depth=1  # Shallow clone for faster analysis
            )
        elif is_local_path(repo_url):
            logger.info("Copying local repository", path=repo_url)
            shutil.copytree(repo_url, target_path)
        else:
            raise ValueError(f"Invalid repository URL or path: {repo_url}")
            
        return target_path
        
    except Exception as e:
        # Clean up on failure
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        logger.error("Failed to clone/copy repository", url=repo_url, error=str(e))
        raise

def extract_repo_info(repo_url: str) -> dict:
    """Extract repository information from URL"""
    info = {
        'owner': None,
        'name': None,
        'platform': None
    }
    
    try:
        if 'github.com' in repo_url:
            info['platform'] = 'github'
            # Extract from URL like: https://github.com/owner/repo.git
            parts = repo_url.replace('.git', '').split('/')
            if len(parts) >= 2:
                info['owner'] = parts[-2]
                info['name'] = parts[-1]
        elif 'gitlab.com' in repo_url:
            info['platform'] = 'gitlab'
            parts = repo_url.replace('.git', '').split('/')
            if len(parts) >= 2:
                info['owner'] = parts[-2]
                info['name'] = parts[-1]
        else:
            # For local paths or other URLs
            path = Path(repo_url)
            info['name'] = path.name
            
    except Exception as e:
        logger.warning("Could not extract repo info", url=repo_url, error=str(e))
        
    return info

def get_commit_hash(repo_path: str) -> str:
    """Get the current commit hash from a repository"""
    try:
        repo = git.Repo(repo_path)
        return repo.head.commit.hexsha
    except Exception as e:
        logger.warning("Could not get commit hash", path=repo_path, error=str(e))
        return None
