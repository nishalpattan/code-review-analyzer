"""
Code Review Analyzer - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.api.analysis import router as analysis_router
from app.api.repositories import router as repositories_router
from app.core.config import settings
from app.core.database import engine
from app.models import models

logger = structlog.get_logger()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Code Review Analyzer",
    description="A comprehensive code analysis platform for quality assessment and confidence scoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["analysis"])
app.include_router(repositories_router, prefix="/api/v1/repositories", tags=["repositories"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Code Review Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "code-review-analyzer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
