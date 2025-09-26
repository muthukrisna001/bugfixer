#!/usr/bin/env python3
"""
Test the simplified analysis workflow
"""
import requests
import json
import time

def test_analysis():
    # Test log content with a clear error
    test_log = """
2024-01-15 10:30:45 ERROR [calculator.py:25] ZeroDivisionError: division by zero
Traceback (most recent call last):
  File "calculator.py", line 25, in divide
    result = a / b
ZeroDivisionError: division by zero

2024-01-15 10:31:12 ERROR [app.py:42] KeyError: 'user_id'
Traceback (most recent call last):
  File "app.py", line 42, in get_user
    user_id = request.data['user_id']
KeyError: 'user_id'
"""

    # Start analysis
    print("🚀 Starting analysis...")
    response = requests.post("http://127.0.0.1:8001/api/analyze", json={
        "github_repo_url": "https://github.com/octocat/Hello-World.git",
        "github_token": "test_token",
        "log_content": test_log,
        "branch_name": "main",
        "create_pr": False
    })
    
    if response.status_code != 200:
        print(f"❌ Analysis failed: {response.status_code} - {response.text}")
        return
    
    result = response.json()
    analysis_id = result["analysis_id"]
    print(f"✅ Analysis started: {analysis_id}")
    
    # Poll for progress
    print("📊 Polling for progress...")
    for i in range(30):  # Poll for up to 30 seconds
        progress_response = requests.get(f"http://127.0.0.1:8001/api/progress/{analysis_id}")
        if progress_response.status_code == 200:
            progress = progress_response.json()
            print(f"   Progress: {progress['progress']}% - {progress['message']}")
            
            if progress['status'] == 'completed':
                print("🎉 Analysis completed!")
                
                # Get issues
                issues_response = requests.get(f"http://127.0.0.1:8001/api/issues/{analysis_id}")
                if issues_response.status_code == 200:
                    issues_data = issues_response.json()
                    print(f"📋 Found {len(issues_data.get('issues', []))} issues:")
                    
                    for i, issue in enumerate(issues_data.get('issues', []), 1):
                        error = issue['original_error']
                        analysis = issue['copilot_analysis']
                        print(f"\n🐛 Issue #{i}:")
                        print(f"   Type: {error['error_type']}")
                        print(f"   File: {error['file_path']}:{error['line_number']}")
                        print(f"   Root Cause: {analysis['root_cause']}")
                        print(f"   Fix Approach: {analysis['fix_approach']}")
                        print(f"   Confidence: {analysis['confidence']*100:.0f}%")
                else:
                    print(f"❌ Failed to get issues: {issues_response.status_code}")
                break
            elif progress['status'] == 'error':
                print(f"❌ Analysis failed: {progress.get('error', 'Unknown error')}")
                break
        else:
            print(f"❌ Failed to get progress: {progress_response.status_code}")
            break
            
        time.sleep(1)
    else:
        print("⏰ Analysis timed out")

if __name__ == "__main__":
    test_analysis()
