"""
Configuration settings for the Code Review Analyzer
"""
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import validator
import os

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Code Review Analyzer"
    
    # Database
    DATABASE_URL: str = "sqlite:///./code_analyzer.db"
    
    # Redis (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Analysis Settings
    MAX_FILE_SIZE_MB: int = 50
    MAX_REPO_SIZE_MB: int = 500
    TEMP_DIR: str = "/tmp/code_analyzer"
    
    # Background Tasks
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Scoring Weights (for confidence calculation)
    PYLINT_WEIGHT: float = 0.25
    BANDIT_WEIGHT: float = 0.20
    COMPLEXITY_WEIGHT: float = 0.15
    COVERAGE_WEIGHT: float = 0.20
    CODE_STYLE_WEIGHT: float = 0.10
    DOCUMENTATION_WEIGHT: float = 0.10
    
    # Email Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    REPORT_EMAIL: str = "nishal.pattan@gmail.com"
    
    @validator("TEMP_DIR")
    def create_temp_dir(cls, v):
        """Ensure temp directory exists"""
        os.makedirs(v, exist_ok=True)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
