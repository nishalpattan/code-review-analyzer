"""
Database models for the Code Review Analyzer
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Repository(Base):
    """Repository model to store analyzed repositories"""
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    branch = Column(String(100), default="main")
    language = Column(String(50))
    owner = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    analyses = relationship("Analysis", back_populates="repository", cascade="all, delete-orphan")

class Analysis(Base):
    """Analysis model to store code analysis results"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    commit_hash = Column(String(40))
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    
    # Overall scores
    confidence_score = Column(Float)  # 0-100
    quality_score = Column(Float)     # 0-100
    
    # Individual analysis results
    pylint_score = Column(Float)
    bandit_issues = Column(Integer, default=0)
    complexity_score = Column(Float)
    coverage_percentage = Column(Float)
    code_style_issues = Column(Integer, default=0)
    dead_code_lines = Column(Integer, default=0)
    
    # Detailed results (JSON)
    pylint_results = Column(JSON)
    bandit_results = Column(JSON)
    complexity_results = Column(JSON)
    coverage_results = Column(JSON)
    style_results = Column(JSON)
    
    # Metadata
    total_files = Column(Integer, default=0)
    total_lines = Column(Integer, default=0)
    analysis_duration = Column(Float)  # seconds
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    repository = relationship("Repository", back_populates="analyses")
    file_analyses = relationship("FileAnalysis", back_populates="analysis", cascade="all, delete-orphan")

class FileAnalysis(Base):
    """Individual file analysis results"""
    __tablename__ = "file_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50))
    
    # File-specific metrics
    lines_of_code = Column(Integer, default=0)
    complexity = Column(Float)
    maintainability_index = Column(Float)
    
    # Issues found
    pylint_issues = Column(Integer, default=0)
    bandit_issues = Column(Integer, default=0)
    style_issues = Column(Integer, default=0)
    
    # Detailed results
    issues = Column(JSON)  # Detailed list of all issues
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    analysis = relationship("Analysis", back_populates="file_analyses")
