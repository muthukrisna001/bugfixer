import os
import json
import asyncio
import aiohttp
from typing import Dict, Any
from decouple import config

class AugmentAnalyzer:
    def __init__(self):
        self.api_base = "https://api.augmentcode.com"  # Update with actual Augment API endpoint
        self.default_api_key = config('AUGMENT_API_KEY', default='')
    
    async def analyze_error_with_augment(self, error_info: Dict, codebase_context: str, augment_api_key: str = None, openai_api_key: str = None) -> Dict[str, Any]:
        """Use Augment Code to analyze the error"""
        
        prompt = f"""
Analyze this error from application logs and provide detailed insights:

Error Type: {error_info.get('error_type', 'Unknown')}
Error Message: {error_info.get('error_message', '')}
File Path: {error_info.get('file_path', 'Unknown')}
Line Number: {error_info.get('line_number', 'Unknown')}
Traceback: {error_info.get('traceback', '')}

Codebase Context: {codebase_context}

Please provide:
1. Root cause analysis
2. Specific file location and line number where the issue occurs
3. Detailed explanation of what went wrong
4. Step-by-step fix approach
5. Code suggestions if applicable
6. Confidence level (0.0 to 1.0)

Respond in JSON format:
{{
    "root_cause": "detailed root cause analysis",
    "file_location": "specific file path",
    "line_number": line_number_if_known,
    "issue_description": "detailed description of the issue",
    "severity": "Low|Medium|High|Critical",
    "fix_approach": "step-by-step fix instructions",
    "code_suggestion": "suggested code fix if applicable",
    "confidence": 0.95
}}
"""
        
        return await self._call_augment_api(prompt, augment_api_key, openai_api_key, error_info)
    
    async def _call_augment_api(self, prompt: str, augment_api_key: str = None, openai_api_key: str = None, error_info: Dict = None) -> Dict[str, Any]:
        """Call Augment Code API"""
        
        # Try Augment first, then OpenAI, then mock analysis
        api_key_to_use = augment_api_key or self.default_api_key

        if api_key_to_use:
            # Try Augment API
            return await self._try_augment_api(prompt, api_key_to_use, error_info)
        elif openai_api_key:
            # Try OpenAI API as fallback
            return await self._try_openai_api(prompt, openai_api_key, error_info)
        else:
            # Use mock analysis
            return self._get_mock_analysis(error_info or {}, "No API keys provided - using intelligent mock analysis")

    async def _try_augment_api(self, prompt: str, api_key: str, error_info: Dict = None) -> Dict[str, Any]:
        """Try Augment API specifically"""
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Augment API payload structure (adjust based on actual API)
        payload = {
            "model": "augment-analysis",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert code analyzer specializing in debugging and error analysis."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/v1/chat/completions",  # Adjust endpoint as needed
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Extract content from Augment response
                        if 'choices' in result and len(result['choices']) > 0:
                            content = result['choices'][0]['message']['content']
                            
                            # Try to parse JSON response
                            try:
                                analysis = json.loads(content)
                                return analysis
                            except json.JSONDecodeError:
                                # If not JSON, create structured response
                                return {
                                    "root_cause": "Error analysis completed",
                                    "file_location": error_info.get('file_path', 'Unknown') if error_info else 'Unknown',
                                    "line_number": error_info.get('line_number', 0) if error_info else 0,
                                    "issue_description": content,
                                    "severity": "Medium",
                                    "fix_approach": "Review the analysis above for detailed fix instructions",
                                    "confidence": 0.8
                                }
                        else:
                            return self._get_mock_analysis(error_info or {})
                    
                    elif response.status == 401:
                        return {
                            "error": "Invalid Augment API key",
                            "root_cause": "Authentication failed - Invalid API key",
                            "file_location": "Configuration",
                            "line_number": 0,
                            "issue_description": "The provided Augment API key is invalid or expired.",
                            "severity": "High",
                            "fix_approach": "1. Check your API key in Augment Dashboard\n2. Generate a new API key if needed\n3. Ensure the key has proper permissions",
                            "confidence": 1.0
                        }
                    
                    elif response.status == 429:
                        return {
                            "error": "API rate limit exceeded",
                            "root_cause": "Too many requests to Augment API",
                            "file_location": "API Limits",
                            "line_number": 0,
                            "issue_description": "Augment API rate limit exceeded. Please try again later.",
                            "severity": "Medium",
                            "fix_approach": "Wait a few minutes and try again, or upgrade your Augment plan for higher limits",
                            "confidence": 1.0
                        }
                    
                    else:
                        # Fall back to mock analysis for other errors
                        return self._get_mock_analysis(error_info or {})

        except asyncio.TimeoutError:
            return self._get_mock_analysis(error_info or {}, "Augment API timeout")
        except Exception as e:
            return self._get_mock_analysis(error_info or {}, f"Augment API error: {str(e)}")

    async def _try_openai_api(self, prompt: str, api_key: str, error_info: Dict = None) -> Dict[str, Any]:
        """Try OpenAI API as fallback"""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # OpenAI API payload
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert code analyzer specializing in debugging and error analysis. Respond in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                ) as response:

                    if response.status == 200:
                        result = await response.json()

                        if 'choices' in result and len(result['choices']) > 0:
                            content = result['choices'][0]['message']['content']

                            # Try to parse JSON response
                            try:
                                analysis = json.loads(content)
                                return analysis
                            except json.JSONDecodeError:
                                # If not JSON, create structured response
                                return {
                                    "root_cause": "Error analysis completed with OpenAI",
                                    "file_location": error_info.get('file_path', 'Unknown') if error_info else 'Unknown',
                                    "line_number": error_info.get('line_number', 0) if error_info else 0,
                                    "issue_description": content,
                                    "severity": "Medium",
                                    "fix_approach": "Review the analysis above for detailed fix instructions",
                                    "confidence": 0.8
                                }
                        else:
                            return self._get_mock_analysis(error_info or {}, "OpenAI returned empty response")

                    elif response.status == 401:
                        return self._get_mock_analysis(error_info or {}, "Invalid OpenAI API key")
                    elif response.status == 429:
                        return self._get_mock_analysis(error_info or {}, "OpenAI API rate limit exceeded")
                    else:
                        return self._get_mock_analysis(error_info or {}, f"OpenAI API error: {response.status}")

        except asyncio.TimeoutError:
            return self._get_mock_analysis(error_info or {}, "OpenAI API timeout")
        except Exception as e:
            return self._get_mock_analysis(error_info or {}, f"OpenAI API error: {str(e)}")

    def _get_mock_analysis(self, error_info: Dict, error_reason: str = None) -> Dict[str, Any]:
        """Provide intelligent mock analysis when API is unavailable"""
        
        error_type = error_info.get('error_type', 'Unknown')
        file_path = error_info.get('file_path', 'Unknown')
        line_number = error_info.get('line_number', 0)
        
        # Intelligent analysis based on error type
        if error_type == "ZeroDivisionError":
            return {
                "root_cause": "Division by zero operation attempted without proper validation",
                "file_location": file_path,
                "line_number": line_number,
                "issue_description": f"A division operation in {file_path} is attempting to divide by zero, which is mathematically undefined.",
                "severity": "High",
                "fix_approach": "1. Add validation to check if denominator is zero before division\n2. Handle the zero case appropriately (return default value, show error, etc.)\n3. Consider using try-catch for robust error handling",
                "code_suggestion": "if denominator != 0:\n    result = numerator / denominator\nelse:\n    # Handle zero division case\n    result = 0  # or appropriate default",
                "confidence": 0.9
            }
        
        elif error_type == "KeyError":
            return {
                "root_cause": "Attempting to access a dictionary key that doesn't exist",
                "file_location": file_path,
                "line_number": line_number,
                "issue_description": f"Code in {file_path} is trying to access a dictionary key that is not present.",
                "severity": "Medium",
                "fix_approach": "1. Use dict.get() method with default value\n2. Check if key exists before accessing\n3. Add proper error handling for missing keys",
                "code_suggestion": "# Use get() with default\nvalue = my_dict.get('key', default_value)\n\n# Or check existence\nif 'key' in my_dict:\n    value = my_dict['key']",
                "confidence": 0.85
            }
        
        elif error_type == "IndexError":
            return {
                "root_cause": "Attempting to access a list/array index that is out of bounds",
                "file_location": file_path,
                "line_number": line_number,
                "issue_description": f"Code in {file_path} is trying to access an index that exceeds the list/array length.",
                "severity": "Medium",
                "fix_approach": "1. Check list length before accessing index\n2. Use try-catch for index access\n3. Validate input parameters that determine index",
                "code_suggestion": "if index < len(my_list):\n    value = my_list[index]\nelse:\n    # Handle out of bounds case\n    value = None",
                "confidence": 0.85
            }
        
        elif error_type == "AttributeError":
            return {
                "root_cause": "Attempting to access an attribute or method that doesn't exist on the object",
                "file_location": file_path,
                "line_number": line_number,
                "issue_description": f"Code in {file_path} is trying to access an attribute/method that doesn't exist on the object.",
                "severity": "Medium",
                "fix_approach": "1. Check if attribute exists using hasattr()\n2. Verify object type before accessing attributes\n3. Check for None values before method calls",
                "code_suggestion": "if hasattr(obj, 'attribute_name'):\n    value = obj.attribute_name\nelse:\n    # Handle missing attribute",
                "confidence": 0.8
            }
        
        else:
            return {
                "root_cause": f"Application error of type {error_type} occurred",
                "file_location": file_path,
                "line_number": line_number,
                "issue_description": f"An error of type {error_type} occurred in {file_path}. {error_reason or 'Using mock analysis as Augment API is unavailable.'}",
                "severity": "Medium",
                "fix_approach": "1. Review the error message and traceback\n2. Check the specific line mentioned in the error\n3. Add appropriate error handling\n4. Test with different input values",
                "confidence": 0.7
            }
