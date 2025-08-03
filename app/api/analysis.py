from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models import models, schemas
from app.core.database import get_db
from app.utils.analysis_utils import analyze_repository

router = APIRouter()

@router.post("/analyze", response_model=schemas.AnalysisResponse)
async def analyze_repository_endpoint(
    analysis_request: schemas.AnalysisCreate,
    db: Session = Depends(get_db)
):
    """Endpoint to perform a complete analysis on a given repository"""
    repository = db.query(models.Repository).filter(models.Repository.id == analysis_request.repository_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    analysis = analyze_repository(repository, analysis_request, db)
    return analysis

@router.get("/{analysis_id}", response_model=schemas.AnalysisResponse)
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """Get analysis results by ID"""
    analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

