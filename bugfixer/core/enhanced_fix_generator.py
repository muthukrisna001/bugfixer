"""
Enhanced Fix Generator that shows actual code from repository
"""
import os
import re
from typing import Optional, List, Dict, Any
from ..models.schemas import BugReport, FixSuggestion

class EnhancedFixGenerator:
    """
    Fix generator that finds and shows actual code from the repository
    """
    
    def __init__(self):
        self.repo_path = None
        
    def set_repository_path(self, repo_path: str):
        """Set the current repository path for analysis"""
        self.repo_path = repo_path
    
    async def generate_real_code_fix(self, bug_report: BugReport) -> Optional[FixSuggestion]:
        """
        Generate fix with actual code from repository
        """
        try:
            error_info = bug_report.error_info
            print(f"🔍 Finding actual code for {error_info.error_type.value}")
            
            # Find the actual problematic code
            code_info = await self._find_actual_code(error_info)
            
            if not code_info:
                print("❌ Could not find actual code, using template")
                print(f"   Error info: {error_info}")
                print(f"   File path: {error_info.file_path}")
                print(f"   Line number: {error_info.line_number}")
                return self._generate_template_fix(error_info)
            
            print(f"✅ Found actual code in: {code_info['file_path']}")
            
            # Generate fix based on actual code
            fix = await self._generate_fix_from_actual_code(error_info, code_info)
            
            return fix
            
        except Exception as e:
            print(f"Enhanced fix generation error: {e}")
            return self._generate_template_fix(error_info)
    
    async def _find_actual_code(self, error_info) -> Optional[Dict[str, Any]]:
        """Find actual code from repository"""
        print(f"🔍 Enhanced fix generator searching for code...")
        print(f"   Repository path: {self.repo_path}")
        print(f"   Path exists: {os.path.exists(self.repo_path) if self.repo_path else False}")

        # If no repository path is set, try using current directory
        search_path = self.repo_path
        if not search_path or not os.path.exists(search_path):
            search_path = os.getcwd()
            print(f"🔄 Using current directory as fallback: {search_path}")

        if not os.path.exists(search_path):
            print(f"❌ No valid search path available")
            return None

        # Temporarily set the search path
        original_repo_path = self.repo_path
        self.repo_path = search_path
        
        file_path = error_info.file_path
        line_number = error_info.line_number
        
        print(f"🔍 Searching for: {file_path} line {line_number}")
        
        # Strategy 1: Direct file path match
        if file_path:
            code_info = await self._try_direct_file_match(file_path, line_number)
            if code_info:
                # Restore original repository path
                self.repo_path = original_repo_path
                return code_info

        # Strategy 2: Search by filename
        if file_path:
            filename = os.path.basename(file_path)
            code_info = await self._search_by_filename(filename, error_info)
            if code_info:
                # Restore original repository path
                self.repo_path = original_repo_path
                return code_info

        # Strategy 3: Search by error pattern
        code_info = await self._search_by_error_pattern(error_info)
        if code_info:
            # Restore original repository path
            self.repo_path = original_repo_path
            return code_info
        
        print("❌ No actual code found in repository")

        # Restore original repository path
        self.repo_path = original_repo_path
        return None
    
    async def _try_direct_file_match(self, file_path: str, line_number: Optional[int]) -> Optional[Dict[str, Any]]:
        """Try to find file directly"""
        try:
            # Remove common prefixes
            clean_paths = [
                file_path,
                file_path.lstrip('/'),
                file_path.replace('/app/', ''),
                file_path.replace('\\app\\', ''),
                os.path.basename(file_path)
            ]
            
            for clean_path in clean_paths:
                full_path = os.path.join(self.repo_path, clean_path)
                if os.path.exists(full_path):
                    return await self._read_file_content(full_path, line_number)
            
            return None
        except Exception as e:
            print(f"Direct file match error: {e}")
            return None
    
    async def _search_by_filename(self, filename: str, error_info) -> Optional[Dict[str, Any]]:
        """Search for file by name in repository"""
        try:
            print(f"🔍 Searching for filename: {filename}")
            
            for root, dirs, files in os.walk(self.repo_path):
                if filename in files:
                    file_path = os.path.join(root, filename)
                    print(f"✅ Found file: {file_path}")
                    return await self._read_file_content(file_path, error_info.line_number)
            
            return None
        except Exception as e:
            print(f"Filename search error: {e}")
            return None
    
    async def _search_by_error_pattern(self, error_info) -> Optional[Dict[str, Any]]:
        """Search for code by error patterns"""
        try:
            error_type = error_info.error_type.value
            error_message = error_info.error_message
            
            print(f"🔍 Searching by pattern for {error_type}")
            
            # Define search patterns for each error type
            patterns = self._get_search_patterns(error_type, error_message)
            
            for root, dirs, files in os.walk(self.repo_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                            
                            # Check if file matches patterns
                            if self._content_matches_patterns(content, patterns):
                                print(f"✅ Found matching code in: {file_path}")
                                line_num = self._find_problematic_line(content, error_type, error_message)
                                problematic_line = self._extract_line(content, line_num)

                                print(f"🔍 Initial search result: line {line_num}, code: '{problematic_line}'")

                                # Always use specific search for better results
                                print(f"🔄 Using specific error line search...")
                                specific_line_num = self._find_specific_error_line(content, error_type, error_message)
                                specific_problematic_line = self._extract_line(content, specific_line_num)
                                print(f"🎯 Specific search result: line {specific_line_num}, code: '{specific_problematic_line}'")

                                # Use specific result if it's better
                                if specific_problematic_line and not specific_problematic_line.startswith("#") and "module" not in specific_problematic_line.lower():
                                    line_num = specific_line_num
                                    problematic_line = specific_problematic_line

                                return {
                                    "file_path": file_path,
                                    "content": content,
                                    "line_number": line_num,
                                    "problematic_line": problematic_line
                                }
                        except Exception:
                            continue
            
            return None
        except Exception as e:
            print(f"Pattern search error: {e}")
            return None
    
    def _get_search_patterns(self, error_type: str, error_message: str) -> List[str]:
        """Get search patterns for error type"""
        patterns = {
            "ZeroDivisionError": [r"/\s*[a-zA-Z_]", r"divide", r"division"],
            "KeyError": [f"['\"]?{re.escape(error_message.strip('\"\''))}['\"]?", r"\[.*\]", r"\.get\("],
            "IndexError": [r"\[.*\]", r"list", r"index"],
            "AttributeError": [r"\.[a-zA-Z_]", r"None", r"attribute"],
            "NameError": [f"{error_message.split()[-1] if error_message else 'undefined'}", r"name.*not.*defined"],
            "TypeError": [r"function", r"argument", r"type"],
            "ValueError": [r"value", r"convert", r"invalid"],
            "ImportError": [r"import", r"module"]
        }
        
        return patterns.get(error_type, [error_type.lower()])
    
    def _content_matches_patterns(self, content: str, patterns: List[str]) -> bool:
        """Check if content matches search patterns"""
        try:
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return True
            return False
        except Exception:
            return False
    
    def _find_problematic_line(self, content: str, error_type: str, error_message: str) -> Optional[int]:
        """Find the line number of problematic code"""
        try:
            lines = content.split('\n')

            # First, try to find exact matches based on error type and context
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith('#'):
                    continue

                # Look for specific patterns based on error type
                if error_type == "ZeroDivisionError":
                    # Look for division operations that could cause the error
                    if "/" in line and not line_stripped.startswith("//") and not line_stripped.startswith("#") and "=" in line:
                        print(f"🎯 Found ZeroDivisionError line {i+1}: {line_stripped}")
                        return i + 1

                elif error_type == "KeyError":
                    # Look for dictionary access with the specific key
                    key = error_message.strip("'\"")
                    if f"['{key}']" in line or f'["{key}"]' in line or f"[{key}]" in line:
                        print(f"🎯 Found KeyError line {i+1}: {line_stripped}")
                        return i + 1

                elif error_type == "IndexError":
                    # Look for list/array indexing
                    if "[" in line and "]" in line and "=" in line and not "dict" in line.lower():
                        print(f"🎯 Found IndexError line {i+1}: {line_stripped}")
                        return i + 1

                elif error_type == "AttributeError":
                    # Look for attribute access that could be on None
                    if "." in line and "return" in line and not "self." in line:
                        print(f"🎯 Found AttributeError line {i+1}: {line_stripped}")
                        return i + 1

            # Fallback: find any line with the relevant pattern
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith('#'):
                    continue

                if error_type == "ZeroDivisionError" and "/" in line:
                    return i + 1
                elif error_type == "KeyError" and ("[" in line or "get(" in line):
                    return i + 1
                elif error_type == "IndexError" and "[" in line:
                    return i + 1
                elif error_type == "AttributeError" and "." in line:
                    return i + 1

            return 1  # Default to first line
        except Exception as e:
            print(f"Error finding problematic line: {e}")
            return 1

    def _find_specific_error_line(self, content: str, error_type: str, error_message: str) -> Optional[int]:
        """Find specific error line with more targeted search"""
        try:
            lines = content.split('\n')

            for i, line in enumerate(lines):
                line_stripped = line.strip()
                if not line_stripped or line_stripped.startswith('#'):
                    continue

                # Very specific searches for each error type
                if error_type == "ZeroDivisionError":
                    if "/" in line and "result" in line and "=" in line:
                        print(f"🎯 Found specific ZeroDivisionError line {i+1}: {line_stripped}")
                        return i + 1

                elif error_type == "KeyError":
                    key = error_message.strip("'\"")
                    if key in line and "[" in line and "]" in line:
                        print(f"🎯 Found specific KeyError line {i+1}: {line_stripped}")
                        return i + 1

                elif error_type == "IndexError":
                    if "items[" in line or "list[" in line:
                        print(f"🎯 Found specific IndexError line {i+1}: {line_stripped}")
                        return i + 1

                elif error_type == "AttributeError":
                    if ".name" in line or ".attribute" in line:
                        print(f"🎯 Found specific AttributeError line {i+1}: {line_stripped}")
                        return i + 1

            # If still not found, return first meaningful line
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                if line_stripped and not line_stripped.startswith('#') and not line_stripped.startswith('"""'):
                    return i + 1

            return 1
        except Exception as e:
            print(f"Error in specific line search: {e}")
            return 1
    
    async def _read_file_content(self, file_path: str, line_number: Optional[int]) -> Dict[str, Any]:
        """Read file content and extract relevant information"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Use enhanced line extraction
            problematic_line = self._extract_line(content, line_number)

            # If we got a docstring or comment, try to find the actual problematic line
            if (not problematic_line or
                problematic_line.startswith("#") or
                "module" in problematic_line.lower() or
                "docstring" in problematic_line.lower() or
                problematic_line.startswith('"""') or
                problematic_line.startswith("'''")):

                print(f"🔄 Docstring/comment found, searching for actual code...")
                # Try to find specific error line based on common patterns
                specific_line_num = self._find_specific_error_line(content, "ZeroDivisionError", "division by zero")
                if specific_line_num:
                    line_number = specific_line_num
                    problematic_line = self._extract_line(content, line_number)
                    print(f"🎯 Found actual problematic line {line_number}: {problematic_line}")

            return {
                "file_path": file_path,
                "content": content,
                "line_number": line_number,
                "problematic_line": problematic_line
            }
        except Exception as e:
            print(f"File read error: {e}")
            return None
    
    def _extract_line(self, content: str, line_number: Optional[int]) -> str:
        """Extract specific line from content"""
        try:
            lines = content.split('\n')

            if not line_number:
                # Find first meaningful line if no line number specified
                for line in lines:
                    line_stripped = line.strip()
                    if line_stripped and not line_stripped.startswith('#') and not line_stripped.startswith('"""') and not line_stripped.startswith("'''"):
                        return line_stripped
                return lines[0].strip() if lines else "# No code found"

            if line_number <= len(lines):
                return lines[line_number - 1].strip()

            return lines[0].strip() if lines else "# No code found"
        except Exception:
            return "# Error extracting line"
    
    async def _generate_fix_from_actual_code(self, error_info, code_info: Dict[str, Any]) -> FixSuggestion:
        """Generate fix based on actual code"""
        try:
            error_type = error_info.error_type.value
            original_code = code_info.get("problematic_line", "# Code not found")
            file_path = code_info.get("file_path", "unknown")
            
            print(f"🔧 Generating fix for actual code: {original_code}")
            
            # Generate specific fix based on actual code and error type
            if error_type == "ZeroDivisionError":
                fixed_code = self._fix_zero_division(original_code)
                explanation = f"Added zero division check to prevent error in {os.path.basename(file_path)}"
                confidence = 0.9
                
            elif error_type == "KeyError":
                fixed_code = self._fix_key_error(original_code, error_info.error_message)
                explanation = f"Replaced direct key access with safe .get() method in {os.path.basename(file_path)}"
                confidence = 0.85
                
            elif error_type == "IndexError":
                fixed_code = self._fix_index_error(original_code)
                explanation = f"Added bounds checking for list access in {os.path.basename(file_path)}"
                confidence = 0.8
                
            elif error_type == "AttributeError":
                fixed_code = self._fix_attribute_error(original_code)
                explanation = f"Added null checking before attribute access in {os.path.basename(file_path)}"
                confidence = 0.75
                
            else:
                fixed_code = f"# TODO: Fix {error_type} in the following line:\n{original_code}"
                explanation = f"Manual fix required for {error_type} in {os.path.basename(file_path)}"
                confidence = 0.5
            
            return FixSuggestion(
                description=f"Fix {error_type} in {os.path.basename(file_path)}",
                original_code=original_code,
                fixed_code=fixed_code,
                confidence=confidence,
                explanation=explanation
            )
            
        except Exception as e:
            print(f"Fix generation error: {e}")
            return self._generate_template_fix(error_info)
    
    def _fix_zero_division(self, original_code: str) -> str:
        """Fix zero division error in actual code"""
        # Find the division operation
        if "/" in original_code:
            parts = original_code.split("=", 1)
            if len(parts) == 2:
                var_name = parts[0].strip()
                expression = parts[1].strip()
                
                # Extract denominator (simplified)
                if "/" in expression:
                    operands = expression.split("/")
                    if len(operands) >= 2:
                        denominator = operands[1].strip()
                        return f"""if {denominator} != 0:
    {original_code}
else:
    {var_name} = 0  # or handle division by zero appropriately
    print(f"Warning: Division by zero prevented")"""
        
        return f"""# Add zero division check before:
if denominator != 0:
    {original_code}
else:
    # Handle division by zero
    pass"""
    
    def _fix_key_error(self, original_code: str, error_message: str) -> str:
        """Fix key error in actual code"""
        key = error_message.strip("'\"")
        
        if "[" in original_code and "]" in original_code:
            # Replace dict[key] with dict.get(key)
            fixed = re.sub(r'\[([\'"]?)' + re.escape(key) + r'\1\]', f".get('{key}')", original_code)
            if fixed != original_code:
                return f"""{fixed}
# Added safe dictionary access - check if value is None"""
        
        return f"""# Replace direct key access with safe access:
# Original: {original_code}
# Use: data.get('{key}', default_value) instead"""
    
    def _fix_index_error(self, original_code: str) -> str:
        """Fix index error in actual code"""
        if "[" in original_code and "]" in original_code:
            # Extract variable names (simplified)
            parts = original_code.split("=", 1)
            if len(parts) == 2:
                var_name = parts[0].strip()
                expression = parts[1].strip()
                
                return f"""# Add bounds checking:
if 0 <= index < len(items):
    {original_code}
else:
    {var_name} = None  # or handle out of bounds
    print(f"Warning: Index out of bounds")"""
        
        return f"""# Add bounds checking before:
if 0 <= index < len(list_variable):
    {original_code}
else:
    # Handle index out of bounds
    pass"""
    
    def _fix_attribute_error(self, original_code: str) -> str:
        """Fix attribute error in actual code"""
        if "." in original_code:
            parts = original_code.split(".", 1)
            if len(parts) >= 2:
                obj_name = parts[0].split()[-1]  # Get the object name
                
                return f"""# Add null checking:
if {obj_name} is not None:
    {original_code}
else:
    # Handle None object
    print(f"Warning: {obj_name} is None")"""
        
        return f"""# Add null checking before:
if obj is not None:
    {original_code}
else:
    # Handle None object
    pass"""
    
    def _generate_template_fix(self, error_info) -> FixSuggestion:
        """Generate template fix as fallback"""
        error_type = error_info.error_type.value
        
        return FixSuggestion(
            description=f"Template fix for {error_type}",
            original_code="# Original code not found in repository",
            fixed_code=f"# Add appropriate error handling for {error_type}",
            confidence=0.3,
            explanation=f"Template-based fix for {error_type} - actual code not found in repository"
        )
