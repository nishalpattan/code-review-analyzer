# API Testing Guide 🧪

This guide provides comprehensive testing examples for the Code Review Analyzer API.

## Quick Test Setup

### 1. Start the Server
```bash
./setup.sh  # First time setup
docker-compose up -d redis  # Start Redis
./run_dev.py  # Start the API server
```

### 2. Verify Server is Running
```bash
curl http://localhost:8000/health
```

Expected Response:
```json
{
  "status": "healthy",
  "service": "code-review-analyzer"
}
```

## 🔧 Postman Collection

### Environment Variables
Create a Postman environment with:
- `base_url`: `http://localhost:8000`
- `repo_id`: `1` (will be set dynamically)

### Collection Structure

#### 1. Health Checks
```http
GET {{base_url}}/
GET {{base_url}}/health
```

#### 2. Repository Management
```http
POST {{base_url}}/api/v1/repositories/
GET {{base_url}}/api/v1/repositories/
GET {{base_url}}/api/v1/repositories/{{repo_id}}
DELETE {{base_url}}/api/v1/repositories/{{repo_id}}
```

#### 3. Code Analysis
```http
POST {{base_url}}/api/v1/analysis/analyze
GET {{base_url}}/api/v1/analysis/{{repo_id}}
```

## 📝 Step-by-Step Testing

### Test 1: Health Check
```bash
curl -X GET http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "code-review-analyzer"
}
```

### Test 2: Create Repository (GitHub)
```bash
curl -X POST "http://localhost:8000/api/v1/repositories/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "requests-library",
    "url": "https://github.com/psf/requests.git",
    "branch": "main",
    "description": "Python HTTP library for humans"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "name": "requests-library",
  "url": "https://github.com/psf/requests.git",
  "branch": "main",
  "description": "Python HTTP library for humans",
  "language": "python",
  "owner": "psf",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null
}
```

### Test 3: List Repositories
```bash
curl -X GET "http://localhost:8000/api/v1/repositories/"
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "name": "requests-library",
    "url": "https://github.com/psf/requests.git",
    "branch": "main",
    "description": "Python HTTP library for humans",
    "language": "python",
    "owner": "psf",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": null
  }
]
```

### Test 4: Start Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_id": 1
  }'
```

**Expected Response (Initial):**
```json
{
  "id": 1,
  "repository_id": 1,
  "commit_hash": null,
  "status": "running",
  "confidence_score": null,
  "quality_score": null,
  "created_at": "2024-01-15T12:00:00Z",
  "completed_at": null
}
```

### Test 5: Check Analysis Progress
```bash
# Wait a few seconds, then check again
curl -X POST "http://localhost:8000/api/v1/analysis/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_id": 1
  }'
```

**Expected Response (Completed):**
```json
{
  "id": 1,
  "repository_id": 1,
  "status": "completed",
  "confidence_score": 78.5,
  "quality_score": 82.1,
  "pylint_score": 7.8,
  "bandit_issues": 3,
  "complexity_score": 4.2,
  "total_files": 45,
  "total_lines": 2841,
  "analysis_duration": 15.7
}
```

## 🧪 Advanced Testing Scenarios

### Test Error Handling

#### Invalid Repository URL
```bash
curl -X POST "http://localhost:8000/api/v1/repositories/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "invalid-repo",
    "url": "not-a-valid-url",
    "branch": "main"
  }'
```

**Expected Response (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "url"],
      "msg": "invalid or missing URL",
      "type": "value_error.url"
    }
  ]
}
```

#### Non-existent Repository Analysis
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repository_id": 999
  }'
```

**Expected Response (404):**
```json
{
  "detail": "Repository not found"
}
```

#### Missing Required Fields
```bash
curl -X POST "http://localhost:8000/api/v1/repositories/" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/user/repo.git"
  }'
```

**Expected Response (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Test Local Repository
```bash
curl -X POST "http://localhost:8000/api/v1/repositories/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "local-project",
    "url": "/path/to/local/python/project",
    "branch": "main",
    "description": "Local project analysis"
  }'
```

### Test Different Branches
```bash
curl -X POST "http://localhost:8000/api/v1/repositories/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "develop-branch",
    "url": "https://github.com/user/repo.git",
    "branch": "develop",
    "description": "Testing develop branch"
  }'
```

## 🐍 Python Testing Script

Create `test_api.py`:

```python
#!/usr/bin/env python3
"""
API Testing Script for Code Review Analyzer
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_repository():
    """Test repository creation"""
    repo_data = {
        "name": "test-repo",
        "url": "https://github.com/psf/requests.git",
        "branch": "main",
        "description": "Test repository"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/repositories/", 
        json=repo_data
    )
    print(f"Create Repository: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    assert response.status_code == 200
    return response.json()["id"]

def test_list_repositories():
    """Test repository listing"""
    response = requests.get(f"{BASE_URL}/api/v1/repositories/")
    print(f"List Repositories: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    assert response.status_code == 200

def test_analyze_repository(repo_id):
    """Test repository analysis"""
    analysis_data = {"repository_id": repo_id}
    
    response = requests.post(
        f"{BASE_URL}/api/v1/analysis/analyze",
        json=analysis_data
    )
    print(f"Start Analysis: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    assert response.status_code == 200
    
    return response.json()["id"]

def test_delete_repository(repo_id):
    """Test repository deletion"""
    response = requests.delete(f"{BASE_URL}/api/v1/repositories/{repo_id}")
    print(f"Delete Repository: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    assert response.status_code == 200

def main():
    """Run all tests"""
    print("🧪 Starting API Tests\n")
    
    try:
        # Test 1: Health Check
        print("1. Testing Health Check...")
        test_health_check()
        print("✅ Health Check passed\n")
        
        # Test 2: Create Repository
        print("2. Testing Repository Creation...")
        repo_id = test_create_repository()
        print(f"✅ Repository created with ID: {repo_id}\n")
        
        # Test 3: List Repositories
        print("3. Testing Repository Listing...")
        test_list_repositories()
        print("✅ Repository listing passed\n")
        
        # Test 4: Analyze Repository
        print("4. Testing Repository Analysis...")
        analysis_id = test_analyze_repository(repo_id)
        print(f"✅ Analysis started with ID: {analysis_id}\n")
        
        # Wait for analysis to complete
        print("⏳ Waiting for analysis to complete...")
        time.sleep(10)
        
        # Test 5: Clean up
        print("5. Testing Repository Deletion...")
        test_delete_repository(repo_id)
        print("✅ Repository deleted\n")
        
        print("🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    main()
```

Run the test script:
```bash
python test_api.py
```

## 📊 Performance Testing

### Load Testing with Apache Bench
```bash
# Test health endpoint
ab -n 100 -c 10 http://localhost:8000/health

# Test repository listing
ab -n 50 -c 5 http://localhost:8000/api/v1/repositories/
```

### Stress Testing Scenarios
1. **Multiple Repository Creations**
2. **Concurrent Analysis Requests**
3. **Large Repository Analysis**
4. **High Frequency API Calls**

## 🔍 Debugging Tips

### Enable Debug Logging
Add to your `.env`:
```env
LOG_LEVEL=debug
```

### Check Analysis Logs
```bash
# Check the application logs
tail -f logs/app.log

# Check analysis specific logs
grep "analysis" logs/app.log
```

### Common Issues

1. **Redis Connection Error**
   - Ensure Redis is running: `docker-compose up -d redis`

2. **Git Clone Failures**
   - Check internet connection
   - Verify repository URL is accessible

3. **Analysis Timeout**
   - Large repositories may take longer
   - Check `MAX_REPO_SIZE_MB` setting

## 📋 Test Checklist

- [ ] Health check endpoint
- [ ] Repository CRUD operations
- [ ] Analysis workflow
- [ ] Error handling
- [ ] Input validation
- [ ] Response format consistency
- [ ] Performance benchmarks
- [ ] Security headers
- [ ] Rate limiting (if implemented)
- [ ] Documentation accuracy
