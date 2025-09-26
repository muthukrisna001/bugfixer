import requests
import json

print("Testing analysis with Copilot token...")

try:
    response = requests.post("http://127.0.0.1:8001/api/analyze", json={
        "github_repo_url": "https://github.com/octocat/Hello-World.git",
        "github_token": "test_repo_token", 
        "copilot_token": "test_copilot_token",  # This will trigger mock analysis
        "log_content": "2024-01-15 10:30:45 ERROR [calculator.py:25] ZeroDivisionError: division by zero",
        "branch_name": "main",
        "create_pr": False
    })
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {result}")
    
    if response.status_code == 200:
        analysis_id = result["analysis_id"]
        print(f"\n✅ Analysis started: {analysis_id}")
        
        # Wait a moment for analysis to complete
        import time
        time.sleep(2)
        
        # Check progress
        progress_response = requests.get(f"http://127.0.0.1:8001/api/progress/{analysis_id}")
        if progress_response.status_code == 200:
            progress = progress_response.json()
            print(f"📊 Progress: {progress['progress']}% - {progress['message']}")
            
            if progress['status'] == 'completed':
                # Get issues
                issues_response = requests.get(f"http://127.0.0.1:8001/api/issues/{analysis_id}")
                if issues_response.status_code == 200:
                    issues_data = issues_response.json()
                    print(f"\n📋 Found {len(issues_data.get('issues', []))} issues:")
                    
                    for i, issue in enumerate(issues_data.get('issues', []), 1):
                        error = issue['original_error']
                        analysis = issue['copilot_analysis']
                        print(f"\n🐛 Issue #{i}:")
                        print(f"   Type: {error['error_type']}")
                        print(f"   Root Cause: {analysis['root_cause']}")
                        print(f"   Fix Approach: {analysis['fix_approach']}")
                        
                        # Check if it's using mock analysis or real Copilot
                        if 'error' in analysis:
                            print(f"   ⚠️ Note: {analysis['error']}")
                        else:
                            print(f"   ✅ Real Copilot analysis!")
                else:
                    print(f"❌ Failed to get issues: {issues_response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")
