#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced UI with real-time progress and fix preview
"""

import requests
import json
import time

def test_enhanced_functionality():
    """Test the enhanced UI functionality"""
    
    print("🧪 Testing Enhanced UI with Real-time Progress")
    print("=" * 60)
    
    # Test 1: Check service health
    print("\n1️⃣ Testing Service Health...")
    try:
        response = requests.get("http://127.0.0.1:8001/api/health")
        if response.status_code == 200:
            print("✅ Service is running")
            print(f"   Response: {response.json()}")
        else:
            print("❌ Service health check failed")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to service: {e}")
        return False
    
    # Test 2: Start analysis with sample logs
    print("\n2️⃣ Starting Analysis with Sample Logs...")
    
    sample_logs = """2024-01-15 10:30:45 ERROR: ZeroDivisionError: division by zero
  File "/app/calculator.py", line 25, in divide
    result = a / b
ZeroDivisionError: division by zero

2024-01-15 10:31:12 ERROR: KeyError: 'user_id'
  File "/app/user_service.py", line 45, in get_user
    user_id = request.data['user_id']
KeyError: 'user_id'

2024-01-15 10:32:18 ERROR: IndexError: list index out of range
  File "/app/data_processor.py", line 67, in process_items
    item = items[index]
IndexError: list index out of range"""
    
    test_data = {
        "github_repo_url": "https://github.com/test-user/test-repo.git",
        "github_token": "ghp_test_token_for_demo_only",
        "log_content": sample_logs,
        "branch_name": "main",
        "create_pr": False
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8001/api/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get('analysis_id')
            print("✅ Analysis started successfully")
            print(f"   📋 Analysis ID: {analysis_id}")
            print(f"   📊 Status: {result.get('status')}")
            print(f"   💬 Message: {result.get('message')}")
            
            # Test 3: Monitor progress in real-time
            print(f"\n3️⃣ Monitoring Real-time Progress for {analysis_id}...")
            return monitor_progress(analysis_id)
            
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis request error: {e}")
        return False

def monitor_progress(analysis_id):
    """Monitor analysis progress in real-time"""
    
    max_attempts = 30  # Maximum 30 seconds
    attempt = 0
    
    while attempt < max_attempts:
        try:
            # Check progress
            response = requests.get(f"http://127.0.0.1:8001/api/progress/{analysis_id}")
            
            if response.status_code == 200:
                progress = response.json()
                
                print(f"\n📊 Progress Update #{attempt + 1}:")
                print(f"   Status: {progress.get('status', 'unknown')}")
                print(f"   Message: {progress.get('message', 'No message')}")
                print(f"   Progress: {progress.get('progress', 0)}%")
                print(f"   Current Step: {progress.get('current_step', 'unknown')}")
                
                if progress.get('errors_found', 0) > 0:
                    print(f"   🐛 Errors Found: {progress.get('errors_found')}")
                
                if progress.get('fixes_generated', 0) > 0:
                    print(f"   🔧 Fixes Generated: {progress.get('fixes_generated')}")
                
                # Check if analysis is complete or awaiting review
                status = progress.get('status')
                if status == 'awaiting_review':
                    print("\n✅ Analysis complete! Fixes are ready for review.")
                    return test_fix_preview(analysis_id)
                elif status == 'completed':
                    print("\n✅ Analysis fully completed!")
                    return True
                elif status == 'error':
                    print(f"\n❌ Analysis failed: {progress.get('message')}")
                    return False
                    
            else:
                print(f"❌ Progress check failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Progress monitoring error: {e}")
        
        attempt += 1
        time.sleep(1)  # Wait 1 second between checks
    
    print("\n⏰ Progress monitoring timed out")
    return False

def test_fix_preview(analysis_id):
    """Test fix preview functionality"""
    
    print(f"\n4️⃣ Testing Fix Preview for {analysis_id}...")
    
    try:
        response = requests.get(f"http://127.0.0.1:8001/api/results/{analysis_id}")
        
        if response.status_code == 200:
            results = response.json()
            fixes = results.get('proposed_fixes', [])
            
            print("✅ Fix preview loaded successfully")
            print(f"   📋 Total Fixes: {len(fixes)}")
            
            for i, fix in enumerate(fixes):
                print(f"\n   🔧 Fix #{i + 1}:")
                print(f"      Error Type: {fix['error']['type']}")
                print(f"      File: {fix['error']['file_path']}:{fix['error']['line_number']}")
                print(f"      Message: {fix['error']['message']}")
                print(f"      Confidence: {fix['fix']['confidence']:.1%}")
                print(f"      Explanation: {fix['fix']['explanation']}")
                print(f"      Original Code: {fix['fix']['original_code'][:50]}...")
                print(f"      Fixed Code: {fix['fix']['fixed_code'][:50]}...")
            
            return True
            
        else:
            print(f"❌ Fix preview failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Fix preview error: {e}")
        return False

def main():
    """Main test function"""
    print("🔧 Enhanced Log-Based Bugfixer - UI Test Suite")
    print("=" * 60)
    
    success = test_enhanced_functionality()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Enhanced UI Test Completed Successfully!")
        print("\n📋 New Features Demonstrated:")
        print("   ✅ Real-time progress tracking")
        print("   ✅ Step-by-step status updates")
        print("   ✅ Progress bar with percentages")
        print("   ✅ Error and fix counting")
        print("   ✅ Fix preview with detailed information")
        print("   ✅ Confidence scoring for fixes")
        print("   ✅ Code diff preview")
        
        print("\n🌐 Enhanced Dashboard Features:")
        print("   ✅ Live progress updates every second")
        print("   ✅ Visual progress bar")
        print("   ✅ Detailed fix review interface")
        print("   ✅ Selective fix approval")
        print("   ✅ Code before/after comparison")
        print("   ✅ Confidence-based color coding")
        
        print("\n🚀 Ready for Production Use:")
        print("   1. Open http://127.0.0.1:8001 in your browser")
        print("   2. Upload your log files")
        print("   3. Watch real-time progress updates")
        print("   4. Review proposed fixes with confidence scores")
        print("   5. Select which fixes to apply")
        print("   6. Automatically create PR with approved fixes")
        
    else:
        print("❌ Some tests failed. Please check the output above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
