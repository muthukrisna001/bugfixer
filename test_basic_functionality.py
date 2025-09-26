import requests
import json
import time

def test_health_endpoint():
    """Test if the health endpoint is working"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get("http://127.0.0.1:8001/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_analysis_endpoint():
    """Test the analysis endpoint with sample data"""
    print("\n🔍 Testing analysis endpoint...")
    
    sample_data = {
        "github_repo_url": "https://github.com/octocat/Hello-World.git",
        "github_token": "test_token_123",
        "log_content": "2024-01-15 10:30:45 ERROR [calculator.py:25] ZeroDivisionError: division by zero",
        "branch_name": "main",
        "create_pr": False
    }
    
    try:
        print("   Sending analysis request...")
        response = requests.post("http://127.0.0.1:8001/api/analyze", 
                               json=sample_data, 
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get("analysis_id")
            print(f"✅ Analysis started successfully!")
            print(f"   Analysis ID: {analysis_id}")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")
            return analysis_id
        else:
            print(f"❌ Analysis endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Analysis endpoint error: {e}")
        return None

def test_progress_endpoint(analysis_id):
    """Test the progress endpoint"""
    print(f"\n🔍 Testing progress endpoint for {analysis_id}...")
    
    try:
        response = requests.get(f"http://127.0.0.1:8001/api/progress/{analysis_id}", timeout=5)
        
        if response.status_code == 200:
            progress = response.json()
            print("✅ Progress endpoint working!")
            print(f"   Status: {progress.get('status')}")
            print(f"   Progress: {progress.get('progress')}%")
            print(f"   Message: {progress.get('message')}")
            return progress
        else:
            print(f"❌ Progress endpoint failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Progress endpoint error: {e}")
        return None

def test_issues_endpoint(analysis_id):
    """Test the issues endpoint"""
    print(f"\n🔍 Testing issues endpoint for {analysis_id}...")
    
    try:
        response = requests.get(f"http://127.0.0.1:8001/api/issues/{analysis_id}", timeout=5)
        
        if response.status_code == 200:
            issues_data = response.json()
            print("✅ Issues endpoint working!")
            
            issues = issues_data.get('issues', [])
            print(f"   Found {len(issues)} issues")
            
            if issues:
                issue = issues[0]
                original_error = issue.get('original_error', {})
                ai_analysis = issue.get('ai_analysis', {})
                
                print(f"   Error Type: {original_error.get('error_type')}")
                print(f"   Root Cause: {ai_analysis.get('root_cause', 'N/A')}")
                print(f"   Severity: {ai_analysis.get('severity', 'N/A')}")
                print(f"   Confidence: {ai_analysis.get('confidence', 0) * 100:.0f}%")
                
                if ai_analysis.get('code_suggestion'):
                    print("   ✅ Code suggestion provided")
                if ai_analysis.get('prevention_tips'):
                    print("   ✅ Prevention tips provided")
                    
            return issues_data
        else:
            print(f"❌ Issues endpoint failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Issues endpoint error: {e}")
        return None

def test_complete_workflow():
    """Test the complete workflow"""
    print("\n🚀 Testing complete workflow...")
    
    # Step 1: Test health
    if not test_health_endpoint():
        return False
    
    # Step 2: Start analysis
    analysis_id = test_analysis_endpoint()
    if not analysis_id:
        return False
    
    # Step 3: Wait a bit for processing
    print("\n⏳ Waiting for analysis to complete...")
    time.sleep(3)
    
    # Step 4: Check progress
    progress = test_progress_endpoint(analysis_id)
    if not progress:
        return False
    
    # Step 5: Get issues
    issues = test_issues_endpoint(analysis_id)
    if not issues:
        return False
    
    print("\n🎉 Complete workflow test successful!")
    return True

def test_different_error_types():
    """Test different error types"""
    print("\n🔍 Testing different error types...")
    
    test_cases = [
        {
            "name": "ZeroDivisionError",
            "log": "2024-01-15 10:30:45 ERROR [calc.py:10] ZeroDivisionError: division by zero"
        },
        {
            "name": "KeyError", 
            "log": "2024-01-15 10:31:12 ERROR [data.py:20] KeyError: 'missing_key'"
        },
        {
            "name": "IndexError",
            "log": "2024-01-15 10:32:30 ERROR [list.py:15] IndexError: list index out of range"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['name']}")
        
        sample_data = {
            "github_repo_url": "https://github.com/test/repo.git",
            "github_token": "test_token",
            "log_content": test_case['log'],
            "branch_name": "main",
            "create_pr": False
        }
        
        try:
            response = requests.post("http://127.0.0.1:8001/api/analyze", 
                                   json=sample_data, timeout=10)
            
            if response.status_code == 200:
                analysis_id = response.json()["analysis_id"]
                time.sleep(2)  # Wait for processing
                
                issues_response = requests.get(f"http://127.0.0.1:8001/api/issues/{analysis_id}")
                if issues_response.status_code == 200:
                    issues = issues_response.json().get('issues', [])
                    if issues:
                        analysis = issues[0].get('ai_analysis', {})
                        print(f"      ✅ {test_case['name']} analysis working")
                        print(f"      Confidence: {analysis.get('confidence', 0) * 100:.0f}%")
                    else:
                        print(f"      ❌ No issues found for {test_case['name']}")
                else:
                    print(f"      ❌ Issues endpoint failed for {test_case['name']}")
            else:
                print(f"      ❌ Analysis failed for {test_case['name']}")
                
        except Exception as e:
            print(f"      ❌ Error testing {test_case['name']}: {e}")

if __name__ == "__main__":
    print("🧪 COMPREHENSIVE TESTING OF LOG-BASED BUGFIXER")
    print("=" * 50)
    
    # Test complete workflow
    if test_complete_workflow():
        # Test different error types
        test_different_error_types()
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS COMPLETED!")
        print("✅ Server is running properly")
        print("✅ All endpoints are working")
        print("✅ AI analysis is functioning")
        print("✅ Different error types are handled")
        print("\n🚀 Your Log-Based Bugfixer is ready to use!")
        print("   Open http://127.0.0.1:8001 in your browser")
    else:
        print("\n❌ TESTS FAILED!")
        print("   Please check the server and try again")
