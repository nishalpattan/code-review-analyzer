from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from app.models import models, schemas
from app.core.database import get_db
from app.utils.git_utils import extract_repo_info

router = APIRouter()

@router.post("/", response_model=schemas.RepositoryResponse)
async def create_repository(
    repository: schemas.RepositoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new repository entry"""
    # Extract additional info from URL
    repo_info = extract_repo_info(str(repository.url))
    
    db_repo = models.Repository(
        name=repository.name,
        url=str(repository.url),
        branch=repository.branch,
        description=repository.description,
        owner=repo_info.get('owner'),
        language='python'  # Default to Python for now
    )
    db.add(db_repo)
    db.commit()
    db.refresh(db_repo)
    return db_repo

@router.get("/", response_model=List[schemas.RepositoryResponse])
async def list_repositories(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """List all repositories with pagination support"""
    repositories = db.query(models.Repository).offset(skip).limit(limit).all()
    return repositories

@router.delete("/{repo_id}", response_model=schemas.RepositoryResponse)
async def delete_repository(
    repo_id: int, 
    db: Session = Depends(get_db)
):
    """Delete a repository by ID"""
    repository = db.query(models.Repository).filter(models.Repository.id == repo_id).first()
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    db.delete(repository)
    db.commit()
    return repository
