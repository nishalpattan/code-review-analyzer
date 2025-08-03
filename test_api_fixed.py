#!/usr/bin/env python3
"""
Test script to verify the analysis API fix
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Health: {response.json()}")
    else:
        print(f"❌ Health failed: {response.text}")
    return response.status_code == 200

def test_create_repository():
    """Create a test repository"""
    repo_data = {
        "name": "flask",
        "url": "https://github.com/pallets/flask.git",
        "branch": "main",
        "description": "A micro web framework written in Python"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/repositories/", json=repo_data)
    print(f"Create repository: {response.status_code}")
    
    if response.status_code == 200:
        repo = response.json()
        print(f"✅ Repository created with ID: {repo['id']}")
        return repo['id']
    else:
        print(f"❌ Repository creation failed: {response.text}")
        return None

def test_start_analysis(repo_id):
    """Start analysis for the repository"""
    analysis_data = {
        "repository_id": repo_id
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/analysis/analyze", json=analysis_data)
    print(f"Start analysis: {response.status_code}")
    
    if response.status_code == 200:
        try:
            analysis = response.json()
            print(f"✅ Analysis started with ID: {analysis['id']}")
            return analysis['id']
        except json.JSONDecodeError as e:
            print(f"❌ Failed to decode analysis response: {e}")
            print(f"Response content: {response.text}")
            return None
    else:
        print(f"❌ Analysis failed: {response.text}")
        return None

def test_get_analysis(analysis_id):
    """Get analysis result"""
    response = requests.get(f"{BASE_URL}/api/v1/analysis/{analysis_id}")
    print(f"Get analysis {analysis_id}: {response.status_code}")
    
    if response.status_code == 200:
        try:
            analysis = response.json()
            print(f"✅ Analysis status: {analysis['status']}")
            print(f"   Confidence score: {analysis.get('confidence_score', 'N/A')}")
            return analysis
        except json.JSONDecodeError as e:
            print(f"❌ Failed to decode analysis response: {e}")
            print(f"Response content: {response.text}")
            return None
    else:
        print(f"❌ Get analysis failed: {response.text}")
        return None

def main():
    print("🧪 Testing Code Review Analyzer API...")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ Health check failed. Server might not be running.")
        return
    
    # Create repository
    repo_id = test_create_repository()
    if not repo_id:
        print("❌ Cannot proceed without repository")
        return
    
    # Start analysis
    analysis_id = test_start_analysis(repo_id)
    if not analysis_id:
        print("❌ Analysis failed to start")
        return
    
    # Wait and check analysis result
    print("⏳ Waiting for analysis to complete...")
    time.sleep(2)
    
    analysis = test_get_analysis(analysis_id)
    if analysis:
        print(f"🎉 Analysis completed successfully!")
        print(f"   Status: {analysis['status']}")
        print(f"   Confidence Score: {analysis.get('confidence_score', 'N/A')}")
        print(f"   Total Files: {analysis.get('total_files', 'N/A')}")
    
    print("=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main()
