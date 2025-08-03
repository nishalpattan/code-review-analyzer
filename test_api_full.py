#!/usr/bin/env python3
"""
Full API test script
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def test_create_repository():
    """Create a test repository"""
    repo_data = {
        "name": "requests-test",
        "url": "https://github.com/psf/requests.git",
        "branch": "main",
        "description": "Python HTTP library"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/repositories/", json=repo_data)
    print(f"Create repository: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        return response.json()["id"]
    return None

def test_analyze(repo_id):
    """Test analysis"""
    analysis_data = {"repository_id": repo_id}
    response = requests.post(f"{BASE_URL}/api/v1/analysis/analyze", json=analysis_data)
    print(f"Analysis: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200

def main():
    print("🧪 Testing Code Review Analyzer API\n")
    
    # Test health
    if not test_health():
        print("❌ Health check failed")
        return
    
    print("✅ Health check passed\n")
    
    # Create repository  
    repo_id = test_create_repository()
    if not repo_id:
        print("❌ Repository creation failed")
        return
        
    print(f"✅ Repository created with ID: {repo_id}\n")
    
    # Test analysis
    if test_analyze(repo_id):
        print("✅ Analysis initiated successfully")
    else:
        print("❌ Analysis failed")

if __name__ == "__main__":
    main()
