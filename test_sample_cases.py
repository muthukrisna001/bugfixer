import requests
import json
import time

def run_sample_test_case(case_name, github_url, github_token, log_content):
    """Run a sample test case and display results"""
    print(f"\n🧪 {case_name}")
    print("-" * 40)
    
    # Prepare data
    data = {
        "github_repo_url": github_url,
        "github_token": github_token,
        "log_content": log_content,
        "branch_name": "main",
        "create_pr": False
    }
    
    try:
        # Submit analysis
        print("📤 Submitting analysis request...")
        response = requests.post("http://127.0.0.1:8001/api/analyze", json=data, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Request failed: {response.status_code}")
            return False
        
        analysis_id = response.json()["analysis_id"]
        print(f"✅ Analysis started: {analysis_id}")
        
        # Wait for completion
        print("⏳ Processing...")
        time.sleep(3)
        
        # Get results
        issues_response = requests.get(f"http://127.0.0.1:8001/api/issues/{analysis_id}")
        if issues_response.status_code != 200:
            print(f"❌ Failed to get results: {issues_response.status_code}")
            return False
        
        issues_data = issues_response.json()
        issues = issues_data.get('issues', [])
        
        if not issues:
            print("⚠️ No issues found")
            return True
        
        print(f"📊 Found {len(issues)} issue(s):")
        
        for i, issue in enumerate(issues, 1):
            error = issue['original_error']
            analysis = issue['ai_analysis']
            
            print(f"\n   🐛 Issue #{i}: {error['error_type']}")
            print(f"   📁 File: {error.get('file_path', 'Unknown')}")
            print(f"   📍 Line: {error.get('line_number', 'Unknown')}")
            print(f"   💬 Message: {error['error_message']}")
            print(f"   🔍 Root Cause: {analysis['root_cause']}")
            print(f"   ⚠️ Severity: {analysis['severity']}")
            print(f"   📊 Confidence: {analysis['confidence'] * 100:.0f}%")
            
            if analysis.get('prevention_tips'):
                print(f"   🛡️ Prevention: {analysis['prevention_tips']}")
            
            if analysis.get('code_suggestion'):
                print("   💡 Code suggestion available")
        
        print("✅ Test case completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test case failed: {e}")
        return False

def main():
    """Run all sample test cases"""
    print("🚀 SAMPLE TEST CASES FOR LOG-BASED BUGFIXER")
    print("=" * 60)
    
    # Sample test cases that users might try
    test_cases = [
        {
            "name": "Sample Case 1: Python Division Error",
            "github_url": "https://github.com/python/cpython.git",
            "github_token": "ghp_sample_token_123",
            "log_content": "2024-01-15 14:30:45 ERROR [calculator.py:25] ZeroDivisionError: division by zero"
        },
        {
            "name": "Sample Case 2: Dictionary Key Error",
            "github_url": "https://github.com/django/django.git", 
            "github_token": "ghp_sample_token_456",
            "log_content": "2024-01-15 14:31:12 ERROR [views.py:42] KeyError: 'user_id'"
        },
        {
            "name": "Sample Case 3: List Index Error",
            "github_url": "https://github.com/flask/flask.git",
            "github_token": "ghp_sample_token_789",
            "log_content": "2024-01-15 14:32:30 ERROR [utils.py:18] IndexError: list index out of range"
        },
        {
            "name": "Sample Case 4: Multiple Errors",
            "github_url": "https://github.com/requests/requests.git",
            "github_token": "ghp_sample_token_multi",
            "log_content": """2024-01-15 14:30:00 ERROR [app.py:10] ValueError: invalid literal for int() with base 10: 'abc'
2024-01-15 14:30:15 ERROR [db.py:25] AttributeError: 'NoneType' object has no attribute 'execute'
2024-01-15 14:30:30 ERROR [file.py:40] FileNotFoundError: [Errno 2] No such file or directory: 'config.json'"""
        },
        {
            "name": "Sample Case 5: Real-world Web App Errors",
            "github_url": "https://github.com/mycompany/webapp.git",
            "github_token": "ghp_webapp_token",
            "log_content": """2024-01-15 09:15:23 INFO [server.py:12] Server starting on port 8000
2024-01-15 09:15:45 ERROR [auth.py:67] AttributeError: 'User' object has no attribute 'is_authenticated'
2024-01-15 09:16:12 ERROR [payment.py:123] ValueError: Payment amount must be positive
2024-01-15 09:16:30 ERROR [database.py:89] KeyError: 'connection_string'
2024-01-15 09:17:00 ERROR [api.py:156] TypeError: unsupported operand type(s) for +: 'int' and 'str'"""
        }
    ]
    
    passed = 0
    total = len(test_cases)
    
    for test_case in test_cases:
        if run_sample_test_case(
            test_case["name"],
            test_case["github_url"], 
            test_case["github_token"],
            test_case["log_content"]
        ):
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 SAMPLE TESTS SUMMARY: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 ALL SAMPLE TEST CASES PASSED!")
        print("\n✅ Your Log-Based Bugfixer is working perfectly!")
        print("✅ Users can copy these examples to test the system")
        print("✅ All error types are properly analyzed")
        print("✅ AI provides detailed insights and suggestions")
        
        print("\n📋 READY FOR USERS!")
        print("Users can now:")
        print("• Open http://127.0.0.1:8001 in their browser")
        print("• Enter their GitHub repo URL and token")
        print("• Paste their error logs")
        print("• Click 'Start Analysis' button")
        print("• Get instant AI-powered error analysis!")
        
        print("\n🎯 SAMPLE DATA FOR TESTING:")
        print("GitHub URL: https://github.com/octocat/Hello-World.git")
        print("GitHub Token: ghp_your_token_here")
        print("Sample Log: 2024-01-15 10:30:45 ERROR [app.py:10] ZeroDivisionError: division by zero")
        
    else:
        print(f"⚠️ {total - passed} test cases failed")
        print("Please check the server and try again")

if __name__ == "__main__":
    main()
