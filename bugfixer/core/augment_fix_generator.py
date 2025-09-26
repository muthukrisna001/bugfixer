"""
Augment-powered Fix Generator
Uses Augment's API for intelligent code analysis and fix generation
"""
import os
import json
import httpx
from typing import Optional, List, Dict, Any
from ..models.schemas import BugReport, FixSuggestion

class AugmentFixGenerator:
    """
    Fix generator that uses Augment's API for intelligent debugging and fix generation
    """
    
    def __init__(self):
        self.augment_api_base = "https://api.augmentcode.com"  # Replace with actual Augment API URL
        self.augment_api_key = os.getenv("AUGMENT_API_KEY")  # API key from environment
        
    async def generate_fix_with_augment(self, bug_report: BugReport, repo_path: str) -> Optional[FixSuggestion]:
        """
        Generate a fix using Augment's API for code analysis and debugging
        """
        try:
            # Step 1: Use Augment's codebase retrieval to find relevant code
            relevant_code = await self._retrieve_relevant_code(bug_report, repo_path)
            
            if not relevant_code:
                return await self._generate_template_fix(bug_report)
            
            # Step 2: Use Augment's analysis to understand the error context
            error_analysis = await self._analyze_error_with_augment(bug_report, relevant_code)
            
            # Step 3: Generate fix using Augment's code generation
            fix_suggestion = await self._generate_fix_with_augment_api(bug_report, relevant_code, error_analysis)
            
            return fix_suggestion
            
        except Exception as e:
            print(f"Augment fix generation failed: {e}")
            # Fallback to template-based fix
            return await self._generate_template_fix(bug_report)
    
    async def _retrieve_relevant_code(self, bug_report: BugReport, repo_path: str) -> Optional[Dict[str, Any]]:
        """
        Use Augment's codebase retrieval to find code relevant to the error
        """
        try:
            error_info = bug_report.error_info
            
            # Create search query based on error information
            search_query = f"""
            Find code related to {error_info.error_type.value} error:
            - Error message: {error_info.error_message}
            - File path: {error_info.file_path or 'unknown'}
            - Line number: {error_info.line_number or 'unknown'}
            - Function or method that might contain this error
            - Similar error patterns in the codebase
            """
            
            # Simulate Augment API call (replace with actual API)
            if self.augment_api_key:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.augment_api_base}/codebase-retrieval",
                        headers={
                            "Authorization": f"Bearer {self.augment_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "query": search_query,
                            "repo_path": repo_path,
                            "max_results": 5
                        }
                    )
                    
                    if response.status_code == 200:
                        return response.json()
            
            # Fallback: Try to find the file locally
            return await self._find_local_code(bug_report, repo_path)
            
        except Exception as e:
            print(f"Code retrieval failed: {e}")
            return None
    
    async def _find_local_code(self, bug_report: BugReport, repo_path: str) -> Optional[Dict[str, Any]]:
        """
        Fallback method to find relevant code locally
        """
        try:
            error_info = bug_report.error_info
            file_path = error_info.file_path
            
            if not file_path:
                return None
            
            # Try different possible file locations
            possible_paths = [
                os.path.join(repo_path, file_path),
                os.path.join(repo_path, file_path.lstrip('/')),
                os.path.join(repo_path, os.path.basename(file_path))
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    return {
                        "file_path": path,
                        "content": content,
                        "line_number": error_info.line_number,
                        "error_context": self._extract_error_context(content, error_info.line_number)
                    }
            
            return None
            
        except Exception as e:
            print(f"Local code search failed: {e}")
            return None
    
    def _extract_error_context(self, content: str, line_number: Optional[int]) -> str:
        """
        Extract relevant code context around the error line
        """
        if not line_number:
            return content[:500]  # Return first 500 chars if no line number
        
        lines = content.split('\n')
        if line_number > len(lines):
            return content[:500]
        
        # Get 5 lines before and after the error line
        start = max(0, line_number - 6)
        end = min(len(lines), line_number + 5)
        
        context_lines = []
        for i in range(start, end):
            marker = " -> " if i == line_number - 1 else "    "
            context_lines.append(f"{i+1:3d}{marker}{lines[i]}")
        
        return '\n'.join(context_lines)
    
    async def _analyze_error_with_augment(self, bug_report: BugReport, relevant_code: Dict[str, Any]) -> str:
        """
        Use Augment's analysis capabilities to understand the error
        """
        try:
            error_info = bug_report.error_info
            
            analysis_prompt = f"""
            Analyze this {error_info.error_type.value} error:
            
            Error Message: {error_info.error_message}
            Traceback: {error_info.traceback}
            
            Relevant Code:
            {relevant_code.get('error_context', 'No code context available')}
            
            Please provide:
            1. Root cause analysis
            2. Why this error occurred
            3. Best approach to fix it
            4. Potential side effects to consider
            """
            
            # Simulate Augment analysis (replace with actual API)
            if self.augment_api_key:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.augment_api_base}/analyze",
                        headers={
                            "Authorization": f"Bearer {self.augment_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "prompt": analysis_prompt,
                            "context": relevant_code
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return result.get('analysis', 'Analysis not available')
            
            # Fallback analysis
            return self._generate_basic_analysis(bug_report)
            
        except Exception as e:
            print(f"Error analysis failed: {e}")
            return self._generate_basic_analysis(bug_report)
    
    def _generate_basic_analysis(self, bug_report: BugReport) -> str:
        """
        Generate basic error analysis without Augment API
        """
        error_info = bug_report.error_info
        error_type = error_info.error_type.value
        
        analysis_templates = {
            "ZeroDivisionError": "Division by zero error. Need to add validation to check if denominator is zero before division.",
            "KeyError": f"Missing key '{error_info.error_message}' in dictionary. Need to check if key exists or use .get() method.",
            "IndexError": "List index out of range. Need to validate list length before accessing elements.",
            "AttributeError": "Attribute access on None or wrong object type. Need to add null checks.",
            "TypeError": "Type mismatch error. Need to validate input types before operations.",
            "ValueError": "Invalid value provided. Need to add input validation.",
            "FileNotFoundError": "File not found. Need to check if file exists before accessing.",
            "ImportError": "Module import failed. Need to check if module is installed and available."
        }
        
        return analysis_templates.get(error_type, f"Error of type {error_type} occurred. Need to investigate the specific cause.")
    
    async def _generate_fix_with_augment_api(self, bug_report: BugReport, relevant_code: Dict[str, Any], analysis: str) -> Optional[FixSuggestion]:
        """
        Generate actual fix code using Augment's code generation
        """
        try:
            error_info = bug_report.error_info
            
            fix_prompt = f"""
            Generate a fix for this {error_info.error_type.value} error:
            
            Error Analysis: {analysis}
            
            Current Code:
            {relevant_code.get('error_context', 'No code available')}
            
            Please provide:
            1. Fixed version of the code
            2. Explanation of the fix
            3. Confidence level (0.0 to 1.0)
            """
            
            # Simulate Augment code generation (replace with actual API)
            if self.augment_api_key:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.augment_api_base}/generate-fix",
                        headers={
                            "Authorization": f"Bearer {self.augment_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "prompt": fix_prompt,
                            "context": relevant_code,
                            "error_info": {
                                "type": error_info.error_type.value,
                                "message": error_info.error_message
                            }
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return FixSuggestion(
                            description=result.get('explanation', 'Fix generated by Augment'),
                            original_code=relevant_code.get('error_context', ''),
                            fixed_code=result.get('fixed_code', ''),
                            confidence=result.get('confidence', 0.8),
                            explanation=result.get('explanation', 'Augment-generated fix')
                        )
            
            # Fallback to template fix
            return await self._generate_template_fix(bug_report)
            
        except Exception as e:
            print(f"Fix generation failed: {e}")
            return await self._generate_template_fix(bug_report)
    
    async def _generate_template_fix(self, bug_report: BugReport) -> Optional[FixSuggestion]:
        """
        Generate a template-based fix as fallback
        """
        error_info = bug_report.error_info
        error_type = error_info.error_type.value
        
        fix_templates = {
            "ZeroDivisionError": {
                "description": "Add zero division check",
                "original_code": "result = a / b",
                "fixed_code": "if b != 0:\n    result = a / b\nelse:\n    result = 0  # or handle appropriately",
                "confidence": 0.9,
                "explanation": "Added check to prevent division by zero"
            },
            "KeyError": {
                "description": "Use safe dictionary access",
                "original_code": f"value = data['{error_info.error_message}']",
                "fixed_code": f"value = data.get('{error_info.error_message}', default_value)",
                "confidence": 0.85,
                "explanation": "Use .get() method to safely access dictionary keys"
            },
            "IndexError": {
                "description": "Add bounds checking",
                "original_code": "item = items[index]",
                "fixed_code": "if 0 <= index < len(items):\n    item = items[index]\nelse:\n    item = None  # or handle appropriately",
                "confidence": 0.8,
                "explanation": "Added bounds checking before list access"
            },
            "AttributeError": {
                "description": "Add null check",
                "original_code": "result = obj.attribute",
                "fixed_code": "if obj is not None:\n    result = obj.attribute\nelse:\n    result = None  # or handle appropriately",
                "confidence": 0.75,
                "explanation": "Added null check before attribute access"
            }
        }
        
        template = fix_templates.get(error_type)
        if template:
            return FixSuggestion(**template)
        
        return None
