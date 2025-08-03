"""
Tests for the main FastAPI application
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Code Review Analyzer API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "active"

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "code-review-analyzer"

def test_docs_available():
    """Test that API documentation is available"""
    response = client.get("/docs")
    assert response.status_code == 200
    
def test_redoc_available():
    """Test that ReDoc documentation is available"""
    response = client.get("/redoc")
    assert response.status_code == 200
