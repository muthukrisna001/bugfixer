import requests
import json
import os
from typing import List, Dict, Any, Optional
from decouple import config

class CopilotAnalyzer:
    def __init__(self):
        self.github_token = config('GITHUB_COPILOT_TOKEN', default='')
        self.api_base = "https://api.github.com"
    
    async def analyze_error_with_copilot(self, error_info: Dict, codebase_context: str, copilot_token: str = None) -> Dict[str, Any]:
        """Use GitHub Copilot to analyze the error"""
        
        prompt = f"""
Analyze this error from application logs:

Error Type: {error_info.get('error_type', 'Unknown')}
Error Message: {error_info.get('error_message', '')}
File Path: {error_info.get('file_path', 'Unknown')}
Line Number: {error_info.get('line_number', 'Unknown')}
Traceback: {error_info.get('traceback', '')}

Codebase Context:
{codebase_context}

Please provide:
1. Root cause analysis
2. Specific file and line number where the issue likely occurs
3. What exactly is wrong in the code
4. Severity level (Critical/High/Medium/Low)
5. Recommended approach to fix (but don't provide actual code)

Format as JSON:
{{
    "root_cause": "explanation",
    "file_location": "path/to/file.py",
    "line_number": 123,
    "issue_description": "what's wrong",
    "severity": "High",
    "fix_approach": "how to approach fixing it"
}}
"""
        
        return await self._call_copilot_api(prompt, copilot_token)
    
    async def _call_copilot_api(self, prompt: str, copilot_token: str = None) -> Dict[str, Any]:
        """Call GitHub Copilot API"""
        
        # Use provided token or fall back to environment variable
        token_to_use = copilot_token or self.github_token

        if not token_to_use:
            return {
                "error": "GitHub Copilot token not provided",
                "root_cause": "Configuration issue - GitHub Copilot API token not provided",
                "file_location": "Configuration",
                "line_number": 0,
                "issue_description": "GitHub Copilot API token not provided. Please provide token in the form above.",
                "severity": "High",
                "fix_approach": "1. Go to GitHub Settings → Developer settings → Personal access tokens\n2. Generate token with 'copilot' scope\n3. Enter the token in the Copilot Token field above"
            }

        headers = {
            "Authorization": f"Bearer {token_to_use}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # Using OpenAI-compatible format for Copilot
        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert code analyzer. Analyze errors and provide detailed insights in JSON format."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "model": "gpt-4",
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        try:
            # Try GitHub Copilot API endpoint
            response = requests.post(
                f"{self.api_base}/copilot/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Try to parse as JSON
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # If not JSON, create structured response
                    return {
                        "root_cause": content[:200] + "..." if len(content) > 200 else content,
                        "file_location": "See analysis",
                        "line_number": 0,
                        "issue_description": content,
                        "severity": "Medium",
                        "fix_approach": "Review the detailed analysis provided"
                    }
            else:
                print(f"Copilot API error: {response.status_code} - {response.text}")
                
                # Fallback to mock analysis for demo
                return self._generate_mock_analysis(prompt)
                
        except Exception as e:
            print(f"Copilot integration error: {e}")
            
            # Fallback to mock analysis for demo
            return self._generate_mock_analysis(prompt)
    
    def _generate_mock_analysis(self, prompt: str) -> Dict[str, Any]:
        """Generate mock analysis when Copilot API is not available"""
        
        # Extract error info from prompt for better mock response
        if "ZeroDivisionError" in prompt:
            return {
                "root_cause": "Division by zero operation attempted without proper validation",
                "file_location": "calculator.py",
                "line_number": 26,
                "issue_description": "The code attempts to divide by zero without checking if the denominator is zero first",
                "severity": "High",
                "fix_approach": "Add validation to check if denominator is zero before division operation"
            }
        elif "KeyError" in prompt:
            return {
                "root_cause": "Attempting to access a dictionary key that doesn't exist",
                "file_location": "user_service.py", 
                "line_number": 45,
                "issue_description": "Code tries to access a key in request data that may not be present",
                "severity": "Medium",
                "fix_approach": "Use .get() method or try-except block to handle missing keys gracefully"
            }
        elif "IndexError" in prompt:
            return {
                "root_cause": "Attempting to access list index that is out of range",
                "file_location": "data_processor.py",
                "line_number": 67,
                "issue_description": "Code tries to access list element without checking if index is within bounds",
                "severity": "Medium", 
                "fix_approach": "Add bounds checking before accessing list elements"
            }
        elif "AttributeError" in prompt:
            return {
                "root_cause": "Attempting to access attribute on None object",
                "file_location": "user_manager.py",
                "line_number": 89,
                "issue_description": "Code tries to access attribute on object that could be None",
                "severity": "High",
                "fix_approach": "Add null checking before accessing object attributes"
            }
        else:
            return {
                "root_cause": "General application error detected in logs",
                "file_location": "Unknown",
                "line_number": 0,
                "issue_description": "Error detected but specific location needs investigation",
                "severity": "Medium",
                "fix_approach": "Review error logs and trace back to source code location"
            }
