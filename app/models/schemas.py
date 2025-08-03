"""
Pydantic schemas for API request/response models
"""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# Repository Schemas
class RepositoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    url: HttpUrl
    branch: str = "main"
    description: Optional[str] = None

class RepositoryCreate(RepositoryBase):
    pass

class RepositoryResponse(RepositoryBase):
    id: int
    language: Optional[str]
    owner: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Analysis Schemas
class AnalysisCreate(BaseModel):
    repository_id: int
    commit_hash: Optional[str] = None

class FileIssue(BaseModel):
    type: str  # pylint, bandit, style, etc.
    severity: str  # error, warning, info
    message: str
    line: Optional[int]
    column: Optional[int]
    rule: Optional[str]

class FileAnalysisResponse(BaseModel):
    id: int
    file_path: str
    file_type: Optional[str]
    lines_of_code: int
    complexity: Optional[float]
    maintainability_index: Optional[float]
    pylint_issues: int
    bandit_issues: int
    style_issues: int
    issues: List[FileIssue] = []
    
    class Config:
        from_attributes = True

class AnalysisResponse(BaseModel):
    id: int
    repository_id: int
    commit_hash: Optional[str]
    status: AnalysisStatus
    
    # Scores
    confidence_score: Optional[float] = Field(None, ge=0, le=100)
    quality_score: Optional[float] = Field(None, ge=0, le=100)
    
    # Individual metrics
    pylint_score: Optional[float]
    bandit_issues: int = 0
    complexity_score: Optional[float]
    coverage_percentage: Optional[float]
    code_style_issues: int = 0
    dead_code_lines: int = 0
    
    # Metadata
    total_files: int = 0
    total_lines: int = 0
    analysis_duration: Optional[float]
    
    # Timestamps
    created_at: datetime
    completed_at: Optional[datetime]
    
    # Detailed results
    pylint_results: Optional[Dict[str, Any]] = None
    bandit_results: Optional[Dict[str, Any]] = None
    complexity_results: Optional[Dict[str, Any]] = None
    coverage_results: Optional[Dict[str, Any]] = None
    style_results: Optional[Dict[str, Any]] = None
    
    # File analyses
    file_analyses: List[FileAnalysisResponse] = []
    
    class Config:
        from_attributes = True

class AnalysisSummary(BaseModel):
    """Lightweight analysis summary for list views"""
    id: int
    repository_id: int
    status: AnalysisStatus
    confidence_score: Optional[float]
    quality_score: Optional[float]
    total_files: int
    total_lines: int
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# Quick Analysis Schemas (for single file/code snippet analysis)
class QuickAnalysisRequest(BaseModel):
    code: str = Field(..., min_length=1)
    language: str = "python"
    filename: Optional[str] = "temp.py"

class QuickAnalysisResponse(BaseModel):
    confidence_score: float = Field(..., ge=0, le=100)
    quality_score: float = Field(..., ge=0, le=100)
    pylint_score: Optional[float]
    bandit_issues: int
    complexity_score: Optional[float]
    style_issues: int
    issues: List[FileIssue]
    analysis_duration: float
    
    # Detailed breakdown
    metrics: Dict[str, Any] = {}
