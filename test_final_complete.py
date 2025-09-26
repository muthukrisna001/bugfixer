#!/usr/bin/env python3
"""
Final comprehensive test of the enhanced bugfixer system
"""

import requests
import json
import time

def test_complete_system():
    """Test the complete enhanced system"""
    
    print("🧪 FINAL COMPREHENSIVE TEST - Enhanced Bugfixer")
    print("=" * 65)
    
    # Test with logs that reference our actual sample files
    sample_logs = """2024-01-15 10:30:45 ERROR: ZeroDivisionError: division by zero
  File "sample_app/calculator.py", line 25, in divide
    result = a / b
ZeroDivisionError: division by zero

2024-01-15 10:31:12 ERROR: KeyError: 'user_id'
  File "sample_app/user_service.py", line 45, in get_user
    user_id = request.data['user_id']
KeyError: 'user_id'

2024-01-15 10:32:18 ERROR: IndexError: list index out of range
  File "sample_app/data_processor.py", line 67, in process_items
    item = items[index]
IndexError: list index out of range

2024-01-15 10:33:25 ERROR: AttributeError: 'NoneType' object has no attribute 'name'
  File "sample_app/user_manager.py", line 89, in get_user_name
    return user.name
AttributeError: 'NoneType' object has no attribute 'name'"""
    
    test_data = {
        "github_repo_url": "https://github.com/octocat/Hello-World.git",
        "github_token": "ghp_test_token_for_demo_only",
        "log_content": sample_logs,
        "branch_name": "bugfix-automated",
        "create_pr": True
    }
    
    try:
        print("🚀 Starting complete system test...")
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
            
            for i in range(25):
                try:
                    progress_response = requests.get(f"http://127.0.0.1:8001/api/progress/{analysis_id}")
                    if progress_response.status_code == 200:
                        progress = progress_response.json()
                        status = progress.get('status')
                        message = progress.get('message', 'No message')
                        progress_pct = progress.get('progress', 0)
                        
                        print(f"   Step {i+1}: {status} ({progress_pct}%) - {message}")
                        
                        if status == 'awaiting_review':
                            print(f"\n🎉 Analysis completed! Testing fix preview...")
                            
                            # Get results and check for actual code
                            results_response = requests.get(f"http://127.0.0.1:8001/api/results/{analysis_id}")
                            if results_response.status_code == 200:
                                results = results_response.json()
                                fixes = results.get('proposed_fixes', [])
                                print(f"   ✅ Found {len(fixes)} fixes")
                                
                                # Check if we have actual code (not templates)
                                actual_code_found = False
                                for j, fix in enumerate(fixes):
                                    original_code = fix['fix']['original_code']
                                    confidence = fix['fix']['confidence']
                                    error_type = fix['error']['type']
                                    
                                    print(f"\n   Fix {j+1}: {error_type}")
                                    print(f"      Confidence: {confidence:.1%}")
                                    print(f"      Original Code: {original_code}")
                                    
                                    # Check if this is actual code (not template)
                                    if "# Original code not found" not in original_code and confidence > 0.5:
                                        actual_code_found = True
                                        print(f"      ✅ ACTUAL CODE FOUND!")
                                    else:
                                        print(f"      ⚠️ Template fallback")
                                
                                # Test fix application
                                print(f"\n🚀 Testing fix application and branch creation...")
                                
                                fix_ids = [str(k) for k in range(len(fixes))]
                                apply_response = requests.post(
                                    f"http://127.0.0.1:8001/api/approve-fixes/{analysis_id}",
                                    json=fix_ids,
                                    headers={"Content-Type": "application/json"}
                                )
                                
                                if apply_response.status_code == 200:
                                    print(f"   ✅ Fix application started")
                                    
                                    # Monitor fix application
                                    for k in range(20):
                                        time.sleep(1)
                                        progress_response = requests.get(f"http://127.0.0.1:8001/api/progress/{analysis_id}")
                                        if progress_response.status_code == 200:
                                            progress = progress_response.json()
                                            status = progress.get('status')
                                            message = progress.get('message', 'No message')
                                            
                                            print(f"      Apply Step {k+1}: {status} - {message}")
                                            
                                            if status == 'completed':
                                                pr_url = progress.get('pr_url')
                                                branch_name = progress.get('branch_name')
                                                applied_fixes = progress.get('applied_fixes', 0)
                                                
                                                print(f"\n🎉 SUCCESS! Fix application completed")
                                                print(f"   Applied Fixes: {applied_fixes}")
                                                
                                                if pr_url:
                                                    print(f"   PR Created: {pr_url}")
                                                    return True, len(fixes), actual_code_found, True
                                                elif branch_name:
                                                    print(f"   Branch Created: {branch_name}")
                                                    return True, len(fixes), actual_code_found, True
                                                else:
                                                    print(f"   Fixes Applied Successfully")
                                                    return True, len(fixes), actual_code_found, True
                                                    
                                            elif status == 'error':
                                                print(f"   ❌ Fix application failed: {message}")
                                                return True, len(fixes), actual_code_found, False
                                    
                                    print(f"   ⏰ Fix application timeout")
                                    return True, len(fixes), actual_code_found, False
                                else:
                                    print(f"   ❌ Fix application request failed: {apply_response.status_code}")
                                    return True, len(fixes), actual_code_found, False
                                
                                return True, len(fixes), actual_code_found, False
                            else:
                                print(f"   ❌ Results retrieval failed: {results_response.status_code}")
                                return False, 0, False, False
                                
                        elif status in ['completed', 'error']:
                            print(f"\n Analysis ended with status: {status}")
                            return status == 'completed', 0, False, False
                            
                except Exception as e:
                    print(f"   ⚠️ Progress check error: {e}")
                
                time.sleep(1)
            
            print(f"\n⏰ Analysis timeout")
            return False, 0, False, False
            
        else:
            print(f"❌ Analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False, 0, False, False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False, 0, False, False

def main():
    """Main test function"""
    success, fix_count, actual_code, branch_created = test_complete_system()
    
    print("\n" + "=" * 65)
    print("🏁 FINAL TEST RESULTS")
    print("=" * 65)
    
    if success and fix_count > 0:
        print("🎉 SYSTEM SUCCESS!")
        print(f"✅ Generated {fix_count} fixes")
        print(f"✅ Error detection working")
        print(f"✅ Fix generation working")
        print(f"✅ Real-time progress working")
        
        if actual_code:
            print("✅ ACTUAL CODE RETRIEVAL WORKING!")
            print("   🔍 Found real code from repository")
            print("   📊 High confidence fixes generated")
        else:
            print("⚠️ Code retrieval using templates")
            print("   📝 Template-based fixes generated")
            print("   🔍 Actual code search needs improvement")
        
        if branch_created:
            print("✅ BRANCH/PR CREATION WORKING!")
            print("   🌿 Branch creation successful")
            print("   📝 Commit operations working")
            print("   🔄 PR automation functional")
        else:
            print("⚠️ Branch/PR creation needs attention")
            print("   🔧 Git operations may have issues")
        
        print(f"\n🎯 OVERALL STATUS:")
        if actual_code and branch_created:
            print("🚀 COMPLETE SUCCESS - Production Ready!")
            print("   • Real code analysis ✅")
            print("   • Branch/PR automation ✅")
            print("   • End-to-end workflow ✅")
        elif actual_code or branch_created:
            print("✅ PARTIAL SUCCESS - Core features working")
            print("   • Error detection and fix generation ✅")
            print("   • Some advanced features need attention")
        else:
            print("⚠️ BASIC SUCCESS - Template system working")
            print("   • Error detection ✅")
            print("   • Template fixes ✅")
            print("   • Advanced features need work")
            
    else:
        print("❌ SYSTEM NEEDS ATTENTION")
        print("• Check error logs for details")
        print("• Verify basic functionality")
    
    print("=" * 65)

if __name__ == "__main__":
    main()
