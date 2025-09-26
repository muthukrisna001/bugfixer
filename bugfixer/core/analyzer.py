"""
Code Analysis Module
Analyzes Python code to identify bugs and their locations
"""
import ast
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from ..models.schemas import ErrorInfo, ErrorType, CodeLocation, BugReport

class CodeAnalyzer:
    """Analyzes code to find bugs and their locations"""
    
    def __init__(self):
        self.error_analyzers = {
            ErrorType.ZERO_DIVISION: self._analyze_zero_division,
            ErrorType.KEY_ERROR: self._analyze_key_error,
            ErrorType.INDEX_ERROR: self._analyze_index_error,
            ErrorType.VALUE_ERROR: self._analyze_value_error,
            ErrorType.TYPE_ERROR: self._analyze_type_error,
            ErrorType.ATTRIBUTE_ERROR: self._analyze_attribute_error,
            ErrorType.JSON_DECODE_ERROR: self._analyze_json_decode_error,
        }
    
    async def analyze_error(self, repo_path: str, error_info: ErrorInfo) -> Optional[BugReport]:
        """
        Analyze an error and find its location in the code
        """
        try:
            # Find the relevant file based on endpoint
            file_path = self._find_file_for_endpoint(repo_path, error_info.endpoint)
            if not file_path:
                return None
            
            # Analyze the specific error type
            analyzer = self.error_analyzers.get(error_info.error_type)
            if not analyzer:
                return None
            
            code_location, analysis = await analyzer(file_path, error_info)
            if not code_location:
                return None
            
            # Create bug report
            bug_report = BugReport(
                id=f"bug_{hash(f'{file_path}_{error_info.endpoint}_{error_info.error_type}')}",
                error_info=error_info,
                code_location=code_location,
                analysis=analysis,
                severity=self._determine_severity(error_info.error_type),
                created_at=error_info.timestamp,
                updated_at=error_info.timestamp
            )
            
            return bug_report
            
        except Exception as e:
            print(f"Error analyzing code: {e}")
            return None
    
    def _find_file_for_endpoint(self, repo_path: str, endpoint: str) -> Optional[str]:
        """
        Find the Python file that likely contains the endpoint code
        """
        # For Django projects, look in views.py files
        possible_files = []
        
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.py') and ('views' in file or 'api' in file):
                    possible_files.append(os.path.join(root, file))
        
        # For now, return the first views.py file found
        # In a real implementation, we'd parse URL patterns to find the exact file
        for file_path in possible_files:
            if 'views.py' in file_path:
                return file_path
        
        return possible_files[0] if possible_files else None
    
    async def _analyze_zero_division(self, file_path: str, error_info: ErrorInfo) -> Tuple[Optional[CodeLocation], str]:
        """
        Analyze ZeroDivisionError
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Find division operations
            for node in ast.walk(tree):
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                    line_number = node.lineno
                    
                    # Get function context
                    function_name = self._find_function_containing_line(tree, line_number)
                    
                    code_location = CodeLocation(
                        file_path=file_path,
                        line_number=line_number,
                        function_name=function_name
                    )
                    
                    analysis = f"Division operation found at line {line_number} in function {function_name}. " \
                              f"The denominator may be zero, causing ZeroDivisionError."
                    
                    return code_location, analysis
            
            return None, "Could not locate division operation"
            
        except Exception as e:
            return None, f"Analysis failed: {e}"
    
    async def _analyze_key_error(self, file_path: str, error_info: ErrorInfo) -> Tuple[Optional[CodeLocation], str]:
        """
        Analyze KeyError
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Find dictionary access operations
            for node in ast.walk(tree):
                if isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Load):
                    line_number = node.lineno
                    function_name = self._find_function_containing_line(tree, line_number)
                    
                    code_location = CodeLocation(
                        file_path=file_path,
                        line_number=line_number,
                        function_name=function_name
                    )
                    
                    analysis = f"Dictionary access found at line {line_number} in function {function_name}. " \
                              f"The key may not exist in the dictionary, causing KeyError."
                    
                    return code_location, analysis
            
            return None, "Could not locate dictionary access"
            
        except Exception as e:
            return None, f"Analysis failed: {e}"
    
    async def _analyze_index_error(self, file_path: str, error_info: ErrorInfo) -> Tuple[Optional[CodeLocation], str]:
        """
        Analyze IndexError
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Find list/array access operations
            for node in ast.walk(tree):
                if isinstance(node, ast.Subscript) and isinstance(node.ctx, ast.Load):
                    line_number = node.lineno
                    function_name = self._find_function_containing_line(tree, line_number)
                    
                    code_location = CodeLocation(
                        file_path=file_path,
                        line_number=line_number,
                        function_name=function_name
                    )
                    
                    analysis = f"List/array access found at line {line_number} in function {function_name}. " \
                              f"The index may be out of bounds, causing IndexError."
                    
                    return code_location, analysis
            
            return None, "Could not locate list access"
            
        except Exception as e:
            return None, f"Analysis failed: {e}"
    
    async def _analyze_value_error(self, file_path: str, error_info: ErrorInfo) -> Tuple[Optional[CodeLocation], str]:
        """
        Analyze ValueError
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Look for math operations that might cause ValueError
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'math.sqrt' in line or 'sqrt' in line:
                    function_name = self._find_function_containing_line_simple(content, i)
                    
                    code_location = CodeLocation(
                        file_path=file_path,
                        line_number=i,
                        function_name=function_name
                    )
                    
                    analysis = f"Square root operation found at line {i} in function {function_name}. " \
                              f"Negative numbers cause ValueError in math.sqrt()."
                    
                    return code_location, analysis
            
            return None, "Could not locate value error source"
            
        except Exception as e:
            return None, f"Analysis failed: {e}"
    
    async def _analyze_type_error(self, file_path: str, error_info: ErrorInfo) -> Tuple[Optional[CodeLocation], str]:
        """
        Analyze TypeError
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Find binary operations that might cause type errors
            for node in ast.walk(tree):
                if isinstance(node, ast.BinOp):
                    line_number = node.lineno
                    function_name = self._find_function_containing_line(tree, line_number)
                    
                    code_location = CodeLocation(
                        file_path=file_path,
                        line_number=line_number,
                        function_name=function_name
                    )
                    
                    analysis = f"Binary operation found at line {line_number} in function {function_name}. " \
                              f"Incompatible types may cause TypeError."
                    
                    return code_location, analysis
            
            return None, "Could not locate type error source"
            
        except Exception as e:
            return None, f"Analysis failed: {e}"
    
    async def _analyze_attribute_error(self, file_path: str, error_info: ErrorInfo) -> Tuple[Optional[CodeLocation], str]:
        """
        Analyze AttributeError
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Find attribute access operations
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute):
                    line_number = node.lineno
                    function_name = self._find_function_containing_line(tree, line_number)
                    
                    code_location = CodeLocation(
                        file_path=file_path,
                        line_number=line_number,
                        function_name=function_name
                    )
                    
                    analysis = f"Attribute access found at line {line_number} in function {function_name}. " \
                              f"The object may be None or lack the attribute, causing AttributeError."
                    
                    return code_location, analysis
            
            return None, "Could not locate attribute access"
            
        except Exception as e:
            return None, f"Analysis failed: {e}"
    
    async def _analyze_json_decode_error(self, file_path: str, error_info: ErrorInfo) -> Tuple[Optional[CodeLocation], str]:
        """
        Analyze JSONDecodeError
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Look for JSON operations
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'json.loads' in line or 'json.load' in line:
                    function_name = self._find_function_containing_line_simple(content, i)
                    
                    code_location = CodeLocation(
                        file_path=file_path,
                        line_number=i,
                        function_name=function_name
                    )
                    
                    analysis = f"JSON parsing found at line {i} in function {function_name}. " \
                              f"Invalid JSON format causes JSONDecodeError."
                    
                    return code_location, analysis
            
            return None, "Could not locate JSON parsing"
            
        except Exception as e:
            return None, f"Analysis failed: {e}"
    
    def _find_function_containing_line(self, tree: ast.AST, line_number: int) -> Optional[str]:
        """
        Find the function that contains a specific line number
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    if node.lineno <= line_number <= (node.end_lineno or node.lineno):
                        return node.name
        return None
    
    def _find_function_containing_line_simple(self, content: str, line_number: int) -> Optional[str]:
        """
        Simple function finder for when AST parsing fails
        """
        lines = content.split('\n')
        current_function = None
        
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('def '):
                # Extract function name
                match = re.match(r'\s*def\s+(\w+)', line)
                if match:
                    current_function = match.group(1)
            
            if i == line_number:
                return current_function
        
        return None
    
    def _determine_severity(self, error_type: ErrorType) -> str:
        """
        Determine bug severity based on error type
        """
        high_severity = [ErrorType.ZERO_DIVISION, ErrorType.ATTRIBUTE_ERROR]
        medium_severity = [ErrorType.KEY_ERROR, ErrorType.INDEX_ERROR, ErrorType.VALUE_ERROR]
        
        if error_type in high_severity:
            return "high"
        elif error_type in medium_severity:
            return "medium"
        else:
            return "low"
