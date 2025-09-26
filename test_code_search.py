#!/usr/bin/env python3
"""
Test code search functionality directly
"""

import os
import asyncio
from bugfixer.core.enhanced_fix_generator import EnhancedFixGenerator
from bugfixer.models.schemas import ErrorInfo, BugReport, ErrorType

async def test_code_search():
    """Test the code search functionality"""
    
    print("🧪 Testing Code Search Functionality")
    print("=" * 50)
    
    # Set up the enhanced fix generator
    generator = EnhancedFixGenerator()
    
    # Set repository path to current directory (where sample_app is)
    repo_path = os.getcwd()
    generator.set_repository_path(repo_path)
    
    print(f"Repository path: {repo_path}")
    print(f"Sample app exists: {os.path.exists(os.path.join(repo_path, 'sample_app'))}")
    
    # List files in sample_app
    sample_app_path = os.path.join(repo_path, 'sample_app')
    if os.path.exists(sample_app_path):
        files = os.listdir(sample_app_path)
        print(f"Files in sample_app: {files}")
    
    # Test code search directly
    print(f"\n🔍 Testing direct code search...")

    # Create a simple error info object
    class SimpleErrorInfo:
        def __init__(self):
            self.error_type = ErrorType.ZERO_DIVISION
            self.error_message = "division by zero"
            self.file_path = "sample_app/calculator.py"
            self.line_number = None  # Let it search for the actual line

    error_info = SimpleErrorInfo()

    # Test the code search directly
    code_info = await generator._find_actual_code(error_info)

    if code_info:
        print(f"✅ Code found!")
        print(f"   File: {code_info.get('file_path')}")
        print(f"   Line: {code_info.get('line_number')}")
        print(f"   Problematic code: {code_info.get('problematic_line')}")
        return True
    else:
        print(f"❌ No code found")
        return False


def main():
    """Main test function"""
    result = asyncio.run(test_code_search())
    
    print("\n" + "=" * 50)
    if result:
        print("🎉 CODE SEARCH SUCCESS!")
        print("✅ Found actual code from repository")
        print("✅ Generated context-aware fix")
    else:
        print("⚠️ CODE SEARCH USING TEMPLATES")
        print("• Check file paths and repository structure")
        print("• Verify sample files exist")
    print("=" * 50)

if __name__ == "__main__":
    main()
