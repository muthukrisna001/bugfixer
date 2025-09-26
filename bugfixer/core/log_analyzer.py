"""
Log Analysis Module
Analyzes log files to detect errors and extract relevant information
"""
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.schemas import ErrorInfo, ErrorType

class LogAnalyzer:
    """Analyzes log files to detect errors and extract information"""
    
    def __init__(self):
        self.error_patterns = {
            ErrorType.ZERO_DIVISION: [
                r"ZeroDivisionError",
                r"division by zero",
                r"float division by zero"
            ],
            ErrorType.KEY_ERROR: [
                r"KeyError",
                r"key.*not found",
                r"missing key"
            ],
            ErrorType.INDEX_ERROR: [
                r"IndexError",
                r"list index out of range",
                r"index.*out of bounds"
            ],
            ErrorType.VALUE_ERROR: [
                r"ValueError",
                r"invalid literal",
                r"could not convert"
            ],
            ErrorType.TYPE_ERROR: [
                r"TypeError",
                r"unsupported operand type",
                r"can't multiply sequence"
            ],
            ErrorType.ATTRIBUTE_ERROR: [
                r"AttributeError",
                r"has no attribute",
                r"NoneType.*has no attribute"
            ],
            ErrorType.JSON_DECODE_ERROR: [
                r"JSONDecodeError",
                r"Expecting property name",
                r"Invalid JSON"
            ],
            ErrorType.IMPORT_ERROR: [
                r"ImportError",
                r"ModuleNotFoundError",
                r"No module named"
            ],
            ErrorType.NAME_ERROR: [
                r"NameError",
                r"name.*is not defined",
                r"global name.*is not defined"
            ]
        }
        
        # Common log timestamp patterns
        self.timestamp_patterns = [
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",  # 2024-01-01 12:00:00
            r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}",  # 01/01/2024 12:00:00
            r"\w{3} \d{2} \d{2}:\d{2}:\d{2}",        # Jan 01 12:00:00
        ]
        
        # File path and line number patterns
        self.file_line_patterns = [
            r'File "([^"]+)", line (\d+)',           # Python traceback
            r'at ([^:]+):(\d+)',                     # General format
            r'in ([^:]+) on line (\d+)',             # PHP style
            r'([^:]+):(\d+):\d+: error',             # Compiler style
        ]
    
    def analyze_logs(self, log_content: str) -> List[ErrorInfo]:
        """
        Analyze log content and extract error information
        """
        errors = []
        lines = log_content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check for error patterns
            error_type = self._detect_error_type(line)
            if error_type:
                error_info = self._extract_error_info(line, lines, i, error_type)
                if error_info:
                    errors.append(error_info)
        
        return errors
    
    def _detect_error_type(self, line: str) -> Optional[ErrorType]:
        """
        Detect error type from a log line
        """
        line_lower = line.lower()
        
        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return error_type
        
        return None
    
    def _extract_error_info(self, error_line: str, all_lines: List[str], 
                           line_index: int, error_type: ErrorType) -> Optional[ErrorInfo]:
        """
        Extract detailed error information from the log line and surrounding context
        """
        try:
            # Extract timestamp
            timestamp = self._extract_timestamp(error_line)
            
            # Extract file path and line number
            file_path, line_number = self._extract_file_info(error_line, all_lines, line_index)
            
            # Extract error message
            error_message = self._extract_error_message(error_line, error_type)
            
            # Extract traceback (look for surrounding lines)
            traceback = self._extract_traceback(all_lines, line_index)
            
            return ErrorInfo(
                error_type=error_type,
                error_message=error_message,
                traceback=traceback,
                log_line=error_line,
                timestamp=timestamp,
                file_path=file_path,
                line_number=line_number
            )
            
        except Exception as e:
            print(f"Error extracting error info: {e}")
            return None
    
    def _extract_timestamp(self, line: str) -> datetime:
        """
        Extract timestamp from log line
        """
        for pattern in self.timestamp_patterns:
            match = re.search(pattern, line)
            if match:
                timestamp_str = match.group(0)
                try:
                    # Try different datetime formats
                    formats = [
                        "%Y-%m-%d %H:%M:%S",
                        "%m/%d/%Y %H:%M:%S",
                        "%b %d %H:%M:%S"
                    ]
                    
                    for fmt in formats:
                        try:
                            return datetime.strptime(timestamp_str, fmt)
                        except ValueError:
                            continue
                            
                except ValueError:
                    pass
        
        # Default to current time if no timestamp found
        return datetime.utcnow()
    
    def _extract_file_info(self, error_line: str, all_lines: List[str], 
                          line_index: int) -> tuple[Optional[str], Optional[int]]:
        """
        Extract file path and line number from error line or surrounding context
        """
        # Check current line first
        for pattern in self.file_line_patterns:
            match = re.search(pattern, error_line)
            if match:
                return match.group(1), int(match.group(2))
        
        # Check surrounding lines (traceback context)
        start = max(0, line_index - 5)
        end = min(len(all_lines), line_index + 5)
        
        for i in range(start, end):
            line = all_lines[i]
            for pattern in self.file_line_patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(1), int(match.group(2))
        
        return None, None
    
    def _extract_error_message(self, line: str, error_type: ErrorType) -> str:
        """
        Extract the actual error message from the log line
        """
        # Try to find the error message after the error type
        error_name = error_type.value
        
        # Look for pattern: ErrorType: message
        pattern = rf"{error_name}:\s*(.+)"
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Look for the error type and take everything after it
        error_index = line.lower().find(error_name.lower())
        if error_index != -1:
            message_start = error_index + len(error_name)
            message = line[message_start:].strip()
            if message.startswith(':'):
                message = message[1:].strip()
            return message if message else line
        
        # Fallback to the entire line
        return line
    
    def _extract_traceback(self, all_lines: List[str], error_line_index: int) -> str:
        """
        Extract traceback information from surrounding lines
        """
        # Look for traceback context (usually a few lines before and after)
        start = max(0, error_line_index - 10)
        end = min(len(all_lines), error_line_index + 5)
        
        traceback_lines = []
        
        for i in range(start, end):
            line = all_lines[i].strip()
            if line and (
                'traceback' in line.lower() or
                'file "' in line.lower() or
                'at ' in line or
                'in ' in line or
                line.startswith('  ') or  # Indented lines often part of traceback
                any(error_type.value in line for error_type in ErrorType)
            ):
                traceback_lines.append(line)
        
        return '\n'.join(traceback_lines) if traceback_lines else all_lines[error_line_index]
    
    def get_error_summary(self, errors: List[ErrorInfo]) -> Dict[str, Any]:
        """
        Generate a summary of detected errors
        """
        if not errors:
            return {"total": 0, "by_type": {}, "files_affected": []}
        
        summary = {
            "total": len(errors),
            "by_type": {},
            "files_affected": [],
            "most_recent": None,
            "oldest": None
        }
        
        # Count by error type
        for error in errors:
            error_type = error.error_type.value
            summary["by_type"][error_type] = summary["by_type"].get(error_type, 0) + 1
        
        # Get affected files
        files = set()
        for error in errors:
            if error.file_path:
                files.add(error.file_path)
        summary["files_affected"] = list(files)
        
        # Get time range
        timestamps = [error.timestamp for error in errors]
        summary["most_recent"] = max(timestamps).isoformat()
        summary["oldest"] = min(timestamps).isoformat()
        
        return summary
