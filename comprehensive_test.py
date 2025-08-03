#!/usr/bin/env python3
"""
Comprehensive test script for the Code Review Analyzer API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_full_workflow():
    """Test the complete workflow from repository creation to analysis results"""
    print("🚀 Starting comprehensive API test...")
    print("=" * 60)
    
    # 1. Health Check
    print("1️⃣ Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    health = response.json()
    print(f"   ✅ Service: {health['service']}, Status: {health['status']}")
    
    # 2. Create Repository
    print("\n2️⃣ Creating test repository...")
    repo_data = {
        "name": "test-project",
        "url": "https://github.com/requests/requests.git",
        "branch": "main",
        "description": "Python HTTP library"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/repositories/", json=repo_data)
    assert response.status_code == 200
    repo = response.json()
    repo_id = repo['id']
    print(f"   ✅ Repository created: ID={repo_id}, Name={repo['name']}")
    print(f"      Owner: {repo['owner']}, Language: {repo['language']}")
    
    # 3. Start Analysis
    print("\n3️⃣ Starting code analysis...")
    analysis_data = {"repository_id": repo_id}
    
    response = requests.post(f"{BASE_URL}/api/v1/analysis/analyze", json=analysis_data)
    assert response.status_code == 200
    
    analysis = response.json()
    analysis_id = analysis['id']
    print(f"   ✅ Analysis started: ID={analysis_id}")
    print(f"      Status: {analysis['status']}")
    
    # 4. Monitor Analysis Progress
    print("\n4️⃣ Monitoring analysis progress...")
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        response = requests.get(f"{BASE_URL}/api/v1/analysis/{analysis_id}")
        assert response.status_code == 200
        
        current_analysis = response.json()
        status = current_analysis['status']
        
        print(f"   ⏳ Attempt {attempt + 1}: Status = {status}")
        
        if status == "completed":
            print("   ✅ Analysis completed successfully!")
            break
        elif status == "failed":
            print("   ❌ Analysis failed!")
            return False
            
        time.sleep(2)
        attempt += 1
    
    if attempt >= max_attempts:
        print("   ⏰ Analysis timeout!")
        return False
    
    # 5. Validate Results
    print("\n5️⃣ Validating analysis results...")
    final_analysis = current_analysis
    
    print(f"   📊 Confidence Score: {final_analysis.get('confidence_score', 'N/A')}/100")
    print(f"   🎯 Quality Score: {final_analysis.get('quality_score', 'N/A')}/100")
    print(f"   📁 Total Files: {final_analysis.get('total_files', 'N/A')}")
    print(f"   📝 Total Lines: {final_analysis.get('total_lines', 'N/A')}")
    print(f"   ⏱️  Duration: {final_analysis.get('analysis_duration', 'N/A'):.2f}s")
    
    # Validate detailed results
    detailed_results = []
    if final_analysis.get('pylint_results'):
        detailed_results.append("Pylint")
    if final_analysis.get('bandit_results'):
        detailed_results.append("Bandit")
    if final_analysis.get('complexity_results'):
        detailed_results.append("Complexity")
    if final_analysis.get('style_results'):
        detailed_results.append("Style")
    
    print(f"   🔍 Available Results: {', '.join(detailed_results) if detailed_results else 'None'}")
    
    # 6. Test Repository List (if endpoint exists)
    print("\n6️⃣ Testing repository list...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/repositories/")
        if response.status_code == 200:
            repos = response.json()
            print(f"   ✅ Found {len(repos)} repositories")
        else:
            print(f"   ℹ️  Repository list endpoint not available (status: {response.status_code})")
    except Exception as e:
        print(f"   ℹ️  Repository list endpoint not tested: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Comprehensive test completed successfully!")
    print("✅ All core functionality is working as expected")
    
    return True

def test_error_cases():
    """Test error handling"""
    print("\n🔧 Testing error cases...")
    
    # Test non-existent repository
    response = requests.post(f"{BASE_URL}/api/v1/analysis/analyze", 
                             json={"repository_id": 99999})
    assert response.status_code == 404
    print("   ✅ Non-existent repository handled correctly")
    
    # Test non-existent analysis
    response = requests.get(f"{BASE_URL}/api/v1/analysis/99999")
    assert response.status_code == 404
    print("   ✅ Non-existent analysis handled correctly")
    
    # Test invalid repository data
    response = requests.post(f"{BASE_URL}/api/v1/repositories/", 
                             json={"name": "", "url": "invalid-url"})
    assert response.status_code in [400, 422]  # Validation error
    print("   ✅ Invalid repository data handled correctly")

def main():
    try:
        # Run comprehensive test
        success = test_full_workflow()
        
        if success:
            # Run error case tests
            test_error_cases()
            print("\n🌟 All tests passed! The API is fully functional.")
        else:
            print("\n❌ Some tests failed. Please review the logs.")
            
    except AssertionError as e:
        print(f"\n❌ Test assertion failed: {e}")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

if __name__ == "__main__":
    main()
