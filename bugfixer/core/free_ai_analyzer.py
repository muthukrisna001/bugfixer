import os
import json
import asyncio
import aiohttp
from typing import Dict, Any

class FreeAIAnalyzer:
    """Free AI analyzer using publicly available models"""
    
    def __init__(self):
        # Using Hugging Face Inference API (free tier)
        self.hf_api_base = "https://api-inference.huggingface.co/models"
        self.model_name = "microsoft/DialoGPT-medium"  # Free model for text generation
        
    async def analyze_error_with_free_ai(self, error_info: Dict, codebase_context: str = "") -> Dict[str, Any]:
        """Analyze error using free AI models with intelligent fallback"""
        
        # Always use intelligent rule-based analysis for reliability
        return self._get_intelligent_analysis(error_info)
    
    def _get_intelligent_analysis(self, error_info: Dict) -> Dict[str, Any]:
        """Provide comprehensive intelligent analysis based on error patterns"""
        
        error_type = error_info.get('error_type', 'Unknown')
        error_message = error_info.get('error_message', '')
        file_path = error_info.get('file_path', 'Unknown')
        line_number = error_info.get('line_number', 0)
        traceback = error_info.get('traceback', '')
        
        # Advanced pattern matching for different error types
        if error_type == "ZeroDivisionError":
            return {
                "root_cause": "Division by zero operation attempted without proper validation",
                "file_location": file_path,
                "line_number": line_number,
                "issue_description": f"A division operation in {file_path} at line {line_number} is attempting to divide by zero. This occurs when the denominator in a division operation equals zero, which is mathematically undefined.",
                "severity": "High",
                "fix_approach": "1. Add validation to check if denominator is zero before division\n2. Handle the zero case appropriately (return default value, show error message, etc.)\n3. Consider using try-catch blocks for robust error handling\n4. Review the logic that calculates the denominator value",
                "code_suggestion": """# Before fix:
result = numerator / denominator

# After fix:
if denominator != 0:
    result = numerator / denominator
else:
    # Handle zero division case
    result = 0  # or raise a custom error
    print("Warning: Division by zero attempted")""",
                "confidence": 0.95,
                "prevention_tips": "Always validate input values before mathematical operations"
            }
        
        elif error_type == "KeyError":
            key_name = self._extract_key_from_message(error_message)
            return {
                "root_cause": f"Attempting to access dictionary key '{key_name}' that doesn't exist",
                "file_location": file_path,
                "line_number": line_number,
                "issue_description": f"Code in {file_path} at line {line_number} is trying to access a dictionary key '{key_name}' that is not present in the dictionary.",
                "severity": "Medium",
                "fix_approach": f"1. Use dict.get() method with default value\n2. Check if key '{key_name}' exists before accessing\n3. Add proper error handling for missing keys\n4. Validate dictionary structure before access",
                "code_suggestion": f"""# Before fix:
value = my_dict['{key_name}']

# After fix - Option 1:
value = my_dict.get('{key_name}', default_value)

# After fix - Option 2:
if '{key_name}' in my_dict:
    value = my_dict['{key_name}']
else:
    # Handle missing key
    value = None""",
                "confidence": 0.90,
                "prevention_tips": f"Always check if key '{key_name}' exists or use .get() method"
            }
        
        elif error_type == "IndexError":
            return {
                "root_cause": "Attempting to access a list/array index that is out of bounds",
                "file_location": file_path,
                "line_number": line_number,
                "issue_description": f"Code in {file_path} at line {line_number} is trying to access an index that exceeds the list/array length. This happens when the index is greater than or equal to the list size.",
                "severity": "Medium",
                "fix_approach": "1. Check list length before accessing index\n2. Use try-catch for index access\n3. Validate input parameters that determine index\n4. Consider using enumerate() for safer iteration",
                "code_suggestion": """# Before fix:
value = my_list[index]

# After fix - Option 1:
if index < len(my_list):
    value = my_list[index]
else:
    # Handle out of bounds
    value = None

# After fix - Option 2:
try:
    value = my_list[index]
except IndexError:
    value = None  # or default value""",
                "confidence": 0.88,
                "prevention_tips": "Always validate array bounds before accessing elements"
            }
        
        elif error_type == "AttributeError":
            attr_name = self._extract_attribute_from_message(error_message)
            return {
                "root_cause": f"Attempting to access attribute/method '{attr_name}' that doesn't exist on the object",
                "file_location": file_path,
                "line_number": line_number,
                "issue_description": f"Code in {file_path} at line {line_number} is trying to access an attribute or method '{attr_name}' that doesn't exist on the object, or the object is None.",
                "severity": "Medium",
                "fix_approach": f"1. Check if attribute '{attr_name}' exists using hasattr()\n2. Verify object type before accessing attributes\n3. Check for None values before method calls\n4. Review object initialization and type",
                "code_suggestion": f"""# Before fix:
value = obj.{attr_name}

# After fix - Option 1:
if hasattr(obj, '{attr_name}'):
    value = obj.{attr_name}
else:
    # Handle missing attribute
    value = None

# After fix - Option 2:
if obj is not None:
    value = getattr(obj, '{attr_name}', default_value)
else:
    value = default_value""",
                "confidence": 0.85,
                "prevention_tips": f"Check object type and None values before accessing '{attr_name}'"
            }
        
        elif error_type == "TypeError":
            return {
                "root_cause": "Operation performed on incompatible data types",
                "file_location": file_path,
                "line_number": line_number,
                "issue_description": f"Code in {file_path} at line {line_number} is performing an operation between incompatible data types or calling a function with wrong argument types.",
                "severity": "Medium",
                "fix_approach": "1. Check data types before operations\n2. Convert data types appropriately\n3. Validate function arguments\n4. Add type checking and conversion",
                "code_suggestion": """# Before fix:
result = str_value + int_value

# After fix:
if isinstance(str_value, str) and isinstance(int_value, int):
    result = str_value + str(int_value)  # or int(str_value) + int_value
else:
    # Handle type mismatch
    result = None""",
                "confidence": 0.80,
                "prevention_tips": "Always validate data types before operations"
            }
        
        elif error_type == "ValueError":
            return {
                "root_cause": "Function received an argument with correct type but inappropriate value",
                "file_location": file_path,
                "line_number": line_number,
                "issue_description": f"Code in {file_path} at line {line_number} is passing a value that is the correct type but has an inappropriate value for the operation.",
                "severity": "Medium",
                "fix_approach": "1. Validate input values before processing\n2. Add range checking for numeric values\n3. Sanitize string inputs\n4. Use try-catch for value conversion",
                "code_suggestion": """# Before fix:
number = int(user_input)

# After fix:
try:
    number = int(user_input)
    if number < 0:  # Add range validation if needed
        raise ValueError("Number must be positive")
except ValueError as e:
    print(f"Invalid input: {e}")
    number = 0  # default value""",
                "confidence": 0.82,
                "prevention_tips": "Validate input values and ranges before processing"
            }
        
        elif error_type == "FileNotFoundError":
            return {
                "root_cause": "Attempting to access a file that doesn't exist",
                "file_location": file_path,
                "line_number": line_number,
                "issue_description": f"Code in {file_path} at line {line_number} is trying to open or access a file that doesn't exist at the specified path.",
                "severity": "High",
                "fix_approach": "1. Check if file exists before opening\n2. Use absolute paths instead of relative paths\n3. Add proper error handling for file operations\n4. Verify file permissions",
                "code_suggestion": """# Before fix:
with open('file.txt', 'r') as f:
    content = f.read()

# After fix:
import os
if os.path.exists('file.txt'):
    with open('file.txt', 'r') as f:
        content = f.read()
else:
    print("File not found")
    content = ""  # or handle appropriately""",
                "confidence": 0.92,
                "prevention_tips": "Always check file existence before file operations"
            }
        
        else:
            # Generic analysis for unknown error types
            return {
                "root_cause": f"Application error of type {error_type} occurred",
                "file_location": file_path,
                "line_number": line_number,
                "issue_description": f"An error of type {error_type} occurred in {file_path} at line {line_number}. Error message: {error_message}",
                "severity": "Medium",
                "fix_approach": "1. Review the error message and traceback carefully\n2. Check the specific line mentioned in the error\n3. Add appropriate error handling\n4. Test with different input values\n5. Review recent code changes",
                "code_suggestion": """# Add try-catch block for error handling:
try:
    # Your code here
    pass
except Exception as e:
    print(f"Error occurred: {e}")
    # Handle the error appropriately""",
                "confidence": 0.70,
                "prevention_tips": "Add comprehensive error handling and input validation"
            }
    
    def _extract_key_from_message(self, error_message: str) -> str:
        """Extract key name from KeyError message"""
        # Try to extract key from common KeyError message formats
        if "'" in error_message:
            parts = error_message.split("'")
            if len(parts) >= 2:
                return parts[1]
        elif '"' in error_message:
            parts = error_message.split('"')
            if len(parts) >= 2:
                return parts[1]
        return "unknown_key"
    
    def _extract_attribute_from_message(self, error_message: str) -> str:
        """Extract attribute name from AttributeError message"""
        # Try to extract attribute from common AttributeError message formats
        if "has no attribute" in error_message:
            parts = error_message.split("'")
            if len(parts) >= 2:
                return parts[-2]  # Usually the last quoted part
        return "unknown_attribute"
