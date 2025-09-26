"""
Fix Generation Module
Generates code fixes for detected bugs
"""
import re
from typing import Optional, Dict, Any
from ..models.schemas import BugReport, FixSuggestion, ErrorType

class FixGenerator:
    """Generates fixes for detected bugs"""
    
    def __init__(self):
        self.fix_templates = {
            ErrorType.ZERO_DIVISION: self._generate_zero_division_fix,
            ErrorType.KEY_ERROR: self._generate_key_error_fix,
            ErrorType.INDEX_ERROR: self._generate_index_error_fix,
            ErrorType.VALUE_ERROR: self._generate_value_error_fix,
            ErrorType.TYPE_ERROR: self._generate_type_error_fix,
            ErrorType.ATTRIBUTE_ERROR: self._generate_attribute_error_fix,
            ErrorType.JSON_DECODE_ERROR: self._generate_json_decode_error_fix,
        }
    
    async def generate_fix(self, bug_report: BugReport) -> Optional[FixSuggestion]:
        """
        Generate a fix suggestion for a bug report
        """
        try:
            # Get the original code
            original_code = self._get_original_code(bug_report)
            if not original_code:
                return None
            
            # Generate fix based on error type
            fix_generator = self.fix_templates.get(bug_report.error_info.error_type)
            if not fix_generator:
                return None
            
            return await fix_generator(bug_report, original_code)
            
        except Exception as e:
            print(f"Error generating fix: {e}")
            return None
    
    def _get_original_code(self, bug_report: BugReport) -> Optional[str]:
        """
        Extract the original code from the file
        """
        try:
            with open(bug_report.code_location.file_path, 'r') as f:
                lines = f.readlines()
            
            # Get the problematic line and some context
            line_num = bug_report.code_location.line_number
            start_line = max(0, line_num - 3)
            end_line = min(len(lines), line_num + 2)
            
            return ''.join(lines[start_line:end_line])
            
        except Exception as e:
            print(f"Error reading original code: {e}")
            return None
    
    async def _generate_zero_division_fix(self, bug_report: BugReport, original_code: str) -> FixSuggestion:
        """
        Generate fix for ZeroDivisionError
        """
        # Find the division operation
        lines = original_code.split('\n')
        fixed_lines = []
        
        for line in lines:
            if '/' in line and not line.strip().startswith('#'):
                # Add zero check before division
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Extract variable names (simplified)
                parts = line.split('/')
                if len(parts) >= 2:
                    denominator = parts[1].strip().split()[0]
                    
                    fixed_lines.append(f"{indent_str}if {denominator} == 0:")
                    fixed_lines.append(f"{indent_str}    return Response({{'error': 'Division by zero not allowed'}}, status=status.HTTP_400_BAD_REQUEST)")
                    fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        fixed_code = '\n'.join(fixed_lines)
        
        return FixSuggestion(
            description="Add zero division check",
            original_code=original_code,
            fixed_code=fixed_code,
            explanation="Added a check to prevent division by zero by returning an error response when denominator is zero.",
            confidence=0.9
        )
    
    async def _generate_key_error_fix(self, bug_report: BugReport, original_code: str) -> FixSuggestion:
        """
        Generate fix for KeyError
        """
        lines = original_code.split('\n')
        fixed_lines = []
        
        for line in lines:
            if '[' in line and ']' in line and '=' in line and not line.strip().startswith('#'):
                # Replace direct key access with .get() method
                # This is a simplified approach
                if "data['" in line or 'data["' in line:
                    # Extract the key
                    key_match = re.search(r"data\[(['\"])([^'\"]+)\1\]", line)
                    if key_match:
                        key = key_match.group(2)
                        fixed_line = line.replace(f"data['{key}']", f"data.get('{key}')")
                        fixed_line = fixed_line.replace(f'data["{key}"]', f'data.get("{key}")')
                        
                        # Add validation
                        indent = len(line) - len(line.lstrip())
                        indent_str = ' ' * indent
                        
                        var_name = line.split('=')[0].strip()
                        fixed_lines.append(fixed_line)
                        fixed_lines.append(f"{indent_str}if {var_name} is None:")
                        fixed_lines.append(f"{indent_str}    return Response({{'error': 'Missing required field: {key}'}}, status=status.HTTP_400_BAD_REQUEST)")
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        fixed_code = '\n'.join(fixed_lines)
        
        return FixSuggestion(
            description="Replace direct key access with safe .get() method",
            original_code=original_code,
            fixed_code=fixed_code,
            explanation="Replaced direct dictionary key access with .get() method and added validation to handle missing keys gracefully.",
            confidence=0.85
        )
    
    async def _generate_index_error_fix(self, bug_report: BugReport, original_code: str) -> FixSuggestion:
        """
        Generate fix for IndexError
        """
        lines = original_code.split('\n')
        fixed_lines = []
        
        for line in lines:
            if '[' in line and ']' in line and not line.strip().startswith('#'):
                # Add bounds checking
                if 'users[' in line:
                    indent = len(line) - len(line.lstrip())
                    indent_str = ' ' * indent
                    
                    # Extract index variable
                    index_match = re.search(r'users\[([^\]]+)\]', line)
                    if index_match:
                        index_var = index_match.group(1)
                        
                        fixed_lines.append(f"{indent_str}if {index_var} >= len(users) or {index_var} < 0:")
                        fixed_lines.append(f"{indent_str}    return Response({{'error': 'User index out of range'}}, status=status.HTTP_400_BAD_REQUEST)")
                        fixed_lines.append(line)
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        fixed_code = '\n'.join(fixed_lines)
        
        return FixSuggestion(
            description="Add bounds checking for list access",
            original_code=original_code,
            fixed_code=fixed_code,
            explanation="Added bounds checking to ensure the index is within the valid range before accessing list elements.",
            confidence=0.9
        )
    
    async def _generate_value_error_fix(self, bug_report: BugReport, original_code: str) -> FixSuggestion:
        """
        Generate fix for ValueError (e.g., negative square root)
        """
        lines = original_code.split('\n')
        fixed_lines = []
        
        for line in lines:
            if 'math.sqrt' in line or 'sqrt(' in line:
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Extract the number variable
                sqrt_match = re.search(r'sqrt\(([^)]+)\)', line)
                if sqrt_match:
                    number_var = sqrt_match.group(1)
                    
                    fixed_lines.append(f"{indent_str}if {number_var} < 0:")
                    fixed_lines.append(f"{indent_str}    return Response({{'error': 'Cannot calculate square root of negative number'}}, status=status.HTTP_400_BAD_REQUEST)")
                    fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        fixed_code = '\n'.join(fixed_lines)
        
        return FixSuggestion(
            description="Add validation for negative numbers in square root",
            original_code=original_code,
            fixed_code=fixed_code,
            explanation="Added validation to check for negative numbers before calculating square root to prevent ValueError.",
            confidence=0.9
        )
    
    async def _generate_type_error_fix(self, bug_report: BugReport, original_code: str) -> FixSuggestion:
        """
        Generate fix for TypeError
        """
        lines = original_code.split('\n')
        fixed_lines = []
        
        for line in lines:
            if '+' in line and 'request.GET.get' in line:
                # Type conversion issue
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                # Add type conversion
                if 'number + 10' in line:
                    fixed_line = line.replace('number + 10', 'int(number) + 10')
                    fixed_lines.append(f"{indent_str}try:")
                    fixed_lines.append(f"{indent_str}    {fixed_line.strip()}")
                    fixed_lines.append(f"{indent_str}except (ValueError, TypeError):")
                    fixed_lines.append(f"{indent_str}    return Response({{'error': 'Invalid number format'}}, status=status.HTTP_400_BAD_REQUEST)")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        fixed_code = '\n'.join(fixed_lines)
        
        return FixSuggestion(
            description="Add type conversion and error handling",
            original_code=original_code,
            fixed_code=fixed_code,
            explanation="Added type conversion and try-catch block to handle type errors gracefully.",
            confidence=0.8
        )
    
    async def _generate_attribute_error_fix(self, bug_report: BugReport, original_code: str) -> FixSuggestion:
        """
        Generate fix for AttributeError
        """
        lines = original_code.split('\n')
        fixed_lines = []
        
        for line in lines:
            if '.username' in line and 'user' in line:
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                fixed_lines.append(f"{indent_str}if user is None:")
                fixed_lines.append(f"{indent_str}    return Response({{'error': 'User not found'}}, status=status.HTTP_404_NOT_FOUND)")
                fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        fixed_code = '\n'.join(fixed_lines)
        
        return FixSuggestion(
            description="Add null check before attribute access",
            original_code=original_code,
            fixed_code=fixed_code,
            explanation="Added null check to prevent AttributeError when trying to access attributes of None object.",
            confidence=0.9
        )
    
    async def _generate_json_decode_error_fix(self, bug_report: BugReport, original_code: str) -> FixSuggestion:
        """
        Generate fix for JSONDecodeError
        """
        lines = original_code.split('\n')
        fixed_lines = []
        
        for line in lines:
            if 'json.loads' in line:
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                
                fixed_lines.append(f"{indent_str}try:")
                fixed_lines.append(f"{indent_str}    {line.strip()}")
                fixed_lines.append(f"{indent_str}except json.JSONDecodeError:")
                fixed_lines.append(f"{indent_str}    return Response({{'error': 'Invalid JSON format'}}, status=status.HTTP_400_BAD_REQUEST)")
            else:
                fixed_lines.append(line)
        
        fixed_code = '\n'.join(fixed_lines)
        
        return FixSuggestion(
            description="Add JSON parsing error handling",
            original_code=original_code,
            fixed_code=fixed_code,
            explanation="Added try-catch block to handle JSON parsing errors gracefully.",
            confidence=0.9
        )
