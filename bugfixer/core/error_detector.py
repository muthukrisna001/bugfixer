"""
Error Detection Module
Monitors target applications and detects exceptions
"""
import httpx
import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.schemas import ErrorInfo, ErrorType, MonitoringConfig

class ErrorDetector:
    """Detects errors by monitoring application endpoints"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)
        self.error_patterns = {
            ErrorType.ZERO_DIVISION: r"ZeroDivisionError|division by zero",
            ErrorType.KEY_ERROR: r"KeyError",
            ErrorType.INDEX_ERROR: r"IndexError|list index out of range",
            ErrorType.VALUE_ERROR: r"ValueError",
            ErrorType.TYPE_ERROR: r"TypeError",
            ErrorType.ATTRIBUTE_ERROR: r"AttributeError",
            ErrorType.JSON_DECODE_ERROR: r"JSONDecodeError|Invalid JSON",
            ErrorType.IMPORT_ERROR: r"ImportError|ModuleNotFoundError",
            ErrorType.NAME_ERROR: r"NameError"
        }
    
    async def monitor_application(self, target_url: str, config: Optional[MonitoringConfig] = None) -> List[ErrorInfo]:
        """
        Monitor application endpoints and detect errors
        """
        if config is None:
            config = MonitoringConfig(target_url=target_url)
        
        errors = []
        
        # Test predefined buggy endpoints
        test_endpoints = [
            {"path": "/api/divide/", "method": "GET", "params": {"numerator": 10, "denominator": 0}},
            {"path": "/api/user-data/", "method": "POST", "json": {"incomplete": "data"}},
            {"path": "/api/user-by-index/", "method": "GET", "params": {"index": 10}},
            {"path": "/api/square-root/", "method": "POST", "json": {"number": -4}},
            {"path": "/api/parse-json/", "method": "GET", "params": {"data": "{invalid: json}"}},
            {"path": "/api/user-attribute/", "method": "GET"},
            {"path": "/api/type-error/", "method": "GET", "params": {"number": "not_a_number"}},
        ]
        
        for endpoint_config in test_endpoints:
            try:
                error_info = await self._test_endpoint(target_url, endpoint_config)
                if error_info:
                    errors.append(error_info)
            except Exception as e:
                print(f"Failed to test endpoint {endpoint_config['path']}: {e}")
        
        return errors
    
    async def _test_endpoint(self, base_url: str, endpoint_config: Dict[str, Any]) -> Optional[ErrorInfo]:
        """
        Test a specific endpoint and detect errors
        """
        url = f"{base_url.rstrip('/')}{endpoint_config['path']}"
        method = endpoint_config.get("method", "GET")
        params = endpoint_config.get("params", {})
        json_data = endpoint_config.get("json", {})
        
        try:
            if method == "GET":
                response = await self.client.get(url, params=params)
            elif method == "POST":
                response = await self.client.post(url, json=json_data, params=params)
            else:
                return None
            
            # If we get here without exception, check response for error indicators
            if response.status_code >= 500:
                # Server error - likely contains traceback
                error_text = response.text
                return self._parse_error_response(error_text, endpoint_config['path'])
            
        except httpx.RequestError as e:
            # Network error
            return None
        except Exception as e:
            # Other errors
            return self._create_error_info(
                error_type=ErrorType.TYPE_ERROR,
                error_message=str(e),
                traceback=str(e),
                endpoint=endpoint_config['path']
            )
        
        return None
    
    def _parse_error_response(self, error_text: str, endpoint: str) -> Optional[ErrorInfo]:
        """
        Parse error response to extract error information
        """
        # Try to extract error type from response
        error_type = self._detect_error_type(error_text)
        
        # Extract error message
        error_message = self._extract_error_message(error_text)
        
        # Use the full response as traceback for now
        traceback = error_text
        
        if error_type and error_message:
            return self._create_error_info(
                error_type=error_type,
                error_message=error_message,
                traceback=traceback,
                endpoint=endpoint
            )
        
        return None
    
    def _detect_error_type(self, error_text: str) -> Optional[ErrorType]:
        """
        Detect error type from error text using regex patterns
        """
        for error_type, pattern in self.error_patterns.items():
            if re.search(pattern, error_text, re.IGNORECASE):
                return error_type
        return None
    
    def _extract_error_message(self, error_text: str) -> str:
        """
        Extract error message from error text
        """
        # Try to find the actual error message
        lines = error_text.split('\n')
        for line in lines:
            line = line.strip()
            if any(error_type.value in line for error_type in ErrorType):
                return line
        
        # Fallback to first non-empty line
        for line in lines:
            line = line.strip()
            if line:
                return line[:200]  # Limit length
        
        return "Unknown error"
    
    def _create_error_info(self, error_type: ErrorType, error_message: str, 
                          traceback: str, endpoint: str) -> ErrorInfo:
        """
        Create ErrorInfo object
        """
        return ErrorInfo(
            error_type=error_type,
            error_message=error_message,
            traceback=traceback,
            endpoint=endpoint,
            timestamp=datetime.utcnow()
        )
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
