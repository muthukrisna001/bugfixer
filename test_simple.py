import requests
import json

print("Testing analysis endpoint...")

try:
    response = requests.post("http://127.0.0.1:8001/api/analyze", json={
        "github_repo_url": "https://github.com/octocat/Hello-World.git",
        "github_token": "test_token", 
        "log_content": "2024-01-15 10:30:45 ERROR [test.py:10] ZeroDivisionError: division by zero",
        "branch_name": "main",
        "create_pr": False
    })
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")
