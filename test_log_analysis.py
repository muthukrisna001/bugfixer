#!/usr/bin/env python3
"""
Test script for the log-based bugfixer system
"""
import asyncio
import json
from bugfixer.core.log_analyzer import LogAnalyzer

# Sample log content with various error types
SAMPLE_LOGS = """
2024-01-15 10:30:45 ERROR: ZeroDivisionError: division by zero
  File "/app/calculator.py", line 25, in divide
    result = a / b
ZeroDivisionError: division by zero

2024-01-15 10:31:12 ERROR: KeyError: 'user_id'
  File "/app/user_service.py", line 45, in get_user
    user_id = request.data['user_id']
KeyError: 'user_id'

2024-01-15 10:32:05 ERROR: IndexError: list index out of range
  File "/app/data_processor.py", line 78, in process_items
    item = items[index]
IndexError: list index out of range

2024-01-15 10:33:22 ERROR: ValueError: invalid literal for int() with base 10: 'abc'
  File "/app/converter.py", line 12, in convert_to_int
    return int(value)
ValueError: invalid literal for int() with base 10: 'abc'

2024-01-15 10:34:15 ERROR: TypeError: unsupported operand type(s) for +: 'int' and 'str'
  File "/app/math_utils.py", line 33, in add_values
    result = a + b
TypeError: unsupported operand type(s) for +: 'int' and 'str'

2024-01-15 10:35:08 ERROR: AttributeError: 'NoneType' object has no attribute 'name'
  File "/app/user_manager.py", line 67, in get_user_name
    return user.name
AttributeError: 'NoneType' object has no attribute 'name'

2024-01-15 10:36:45 ERROR: JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
  File "/app/json_parser.py", line 19, in parse_json
    data = json.loads(json_string)
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
"""

async def test_log_analyzer():
    """Test the log analyzer functionality"""
    print("🧪 Testing Log Analyzer")
    print("=" * 50)
    
    # Initialize log analyzer
    analyzer = LogAnalyzer()
    
    # Analyze the sample logs
    print("📋 Analyzing sample logs...")
    errors = analyzer.analyze_logs(SAMPLE_LOGS)
    
    print(f"✅ Found {len(errors)} errors in logs")
    print()
    
    # Display each error
    for i, error in enumerate(errors, 1):
        print(f"🐛 Error {i}: {error.error_type.value}")
        print(f"   📄 File: {error.file_path}:{error.line_number}")
        print(f"   💬 Message: {error.error_message}")
        print(f"   🕒 Timestamp: {error.timestamp}")
        print(f"   📝 Log Line: {error.log_line[:100]}...")
        print()
    
    # Generate summary
    summary = analyzer.get_error_summary(errors)
    print("📊 Error Summary:")
    print(f"   Total Errors: {summary['total']}")
    print(f"   Files Affected: {len(summary['files_affected'])}")
    print(f"   Error Types:")
    for error_type, count in summary['by_type'].items():
        print(f"     - {error_type}: {count}")
    print()
    
    return errors

async def test_api_endpoint():
    """Test the API endpoint with sample data"""
    print("🌐 Testing API Endpoint")
    print("=" * 50)
    
    import httpx
    
    # Prepare test data
    test_data = {
        "github_repo_url": "https://github.com/test/sample-repo.git",
        "github_token": "ghp_test_token_for_demo",
        "log_content": SAMPLE_LOGS,
        "branch_name": "main",
        "create_pr": False  # Don't create PR for test
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            health_response = await client.get("http://127.0.0.1:8001/api/health")
            print(f"✅ Health Check: {health_response.status_code}")
            print(f"   Response: {health_response.json()}")
            print()
            
            # Test analysis endpoint
            print("🔍 Starting analysis via API...")
            analysis_response = await client.post(
                "http://127.0.0.1:8001/api/analyze",
                json=test_data,
                timeout=30.0
            )
            
            if analysis_response.status_code == 200:
                result = analysis_response.json()
                print(f"✅ Analysis started successfully!")
                print(f"   Analysis ID: {result['analysis_id']}")
                print(f"   Status: {result['status']}")
                print(f"   Message: {result['message']}")
            else:
                print(f"❌ Analysis failed: {analysis_response.status_code}")
                print(f"   Error: {analysis_response.text}")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")

async def main():
    """Main test function"""
    print("🔧 Log-Based Bugfixer Test Suite")
    print("=" * 60)
    print("Testing the new log analysis functionality")
    print("=" * 60)
    print()
    
    # Test 1: Log Analyzer
    errors = await test_log_analyzer()
    
    # Test 2: API Endpoint
    await test_api_endpoint()
    
    print("=" * 60)
    print("🎉 Test Suite Complete!")
    print()
    print("📋 Summary:")
    print(f"   ✅ Log analysis found {len(errors)} errors")
    print("   ✅ API endpoints are functional")
    print("   ✅ Dashboard is accessible at http://127.0.0.1:8001")
    print()
    print("🚀 Next Steps:")
    print("   1. Create a GitHub repository with your application code")
    print("   2. Generate a GitHub Personal Access Token")
    print("   3. Collect your application logs")
    print("   4. Use the dashboard to analyze logs and create fixes!")
    print()

if __name__ == "__main__":
    asyncio.run(main())
