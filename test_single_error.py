#!/usr/bin/env python3
"""
Test single error with actual code retrieval
"""

import requests
import json
import time
import os

def test_single_error():
    """Test with a single error that should find actual code"""
    
    print("🧪 SINGLE ERROR TEST - Enhanced Code Retrieval")
    print("=" * 55)
    
    # Test with a single ZeroDivisionError that references our sample file
    sample_logs = """2024-01-15 10:30:45 ERROR: ZeroDivisionError: division by zero
  File "sample_app/calculator.py", line 26, in divide
    result = a / b
ZeroDivisionError: division by zero"""
    
    test_data = {
        "github_repo_url": "https://github.com/octocat/Hello-World.git",
        "github_token": "ghp_test_token_for_demo_only",
        "log_content": sample_logs,
        "branch_name": "bugfix-single-test",
        "create_pr": False  # Skip PR creation for now
    }
    
    try:
        print("🚀 Starting single error analysis...")
        response = requests.post(
            "http://127.0.0.1:8001/api/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis_id = result.get('analysis_id')
            print(f"✅ Analysis started: {analysis_id}")
            
            # Monitor analysis progress
            print(f"\n📊 Monitoring analysis progress...")
            
            for i in range(15):
                try:
                    progress_response = requests.get(f"http://127.0.0.1:8001/api/progress/{analysis_id}")
                    if progress_response.status_code == 200:
                        progress = progress_response.json()
                        status = progress.get('status')
                        message = progress.get('message', 'No message')
                        progress_pct = progress.get('progress', 0)
                        
                        print(f"   Step {i+1}: {status} ({progress_pct}%) - {message}")
                        
                        if status == 'awaiting_review':
                            print(f"\n🎉 Analysis completed! Checking fix details...")
                            
                            # Get results and check for actual code
                            results_response = requests.get(f"http://127.0.0.1:8001/api/results/{analysis_id}")
                            if results_response.status_code == 200:
                                results = results_response.json()
                                fixes = results.get('proposed_fixes', [])
                                print(f"   ✅ Found {len(fixes)} fixes")
                                
                                # Check the first fix in detail
                                if fixes:
                                    fix = fixes[0]
                                    original_code = fix['fix']['original_code']
                                    fixed_code = fix['fix']['fixed_code']
                                    confidence = fix['fix']['confidence']
                                    error_type = fix['error']['type']
                                    
                                    print(f"\n🔍 DETAILED FIX ANALYSIS:")
                                    print(f"   Error Type: {error_type}")
                                    print(f"   Confidence: {confidence:.1%}")
                                    print(f"   Original Code: '{original_code}'")
                                    print(f"   Fixed Code Preview: '{fixed_code[:100]}...'")
                                    
                                    # Check if this is actual code (not template)
                                    if "result = a / b" in original_code:
                                        print(f"\n🎉 SUCCESS! FOUND ACTUAL CODE!")
                                        print(f"   ✅ Retrieved real problematic line from repository")
                                        print(f"   ✅ Enhanced fix generator working correctly")
                                        return True, True
                                    elif "# Original code not found" in original_code:
                                        print(f"\n⚠️ Template fallback used")
                                        print(f"   📝 Enhanced fix generator fell back to templates")
                                        print(f"   🔍 Code search may have failed")
                                        return True, False
                                    else:
                                        print(f"\n🤔 Unexpected code format")
                                        print(f"   📝 Code: {original_code}")
                                        return True, False
                                else:
                                    print(f"\n❌ No fixes generated")
                                    return False, False
                            else:
                                print(f"   ❌ Results retrieval failed: {results_response.status_code}")
                                return False, False
                                
                        elif status in ['completed', 'error']:
                            print(f"\n Analysis ended with status: {status}")
                            return status == 'completed', False
                            
                except Exception as e:
                    print(f"   ⚠️ Progress check error: {e}")
                
                time.sleep(1)
            
            print(f"\n⏰ Analysis timeout")
            return False, False
            
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False, False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False, False

def main():
    """Main test function"""
    success, actual_code = test_single_error()
    
    print("\n" + "=" * 55)
    print("🏁 SINGLE ERROR TEST RESULTS")
    print("=" * 55)
    
    if success:
        print("🎉 ANALYSIS SUCCESS!")
        print("✅ Error detection working")
        print("✅ Fix generation working")
        
        if actual_code:
            print("🚀 ACTUAL CODE RETRIEVAL SUCCESS!")
            print("   ✅ Found real code: 'result = a / b'")
            print("   ✅ Enhanced fix generator working")
            print("   ✅ Repository integration functional")
            print("\n🎯 READY FOR PRODUCTION!")
        else:
            print("⚠️ Using template fallback")
            print("   📝 Template-based fixes generated")
            print("   🔍 Enhanced code search needs debugging")
            print("\n🔧 NEEDS CODE RETRIEVAL FIX")
    else:
        print("❌ ANALYSIS FAILED")
        print("• Check server logs for errors")
        print("• Verify basic functionality")
    
    print("=" * 55)

if __name__ == "__main__":
    main()
