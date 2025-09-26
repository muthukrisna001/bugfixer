"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ErrorType(str, Enum):
    ZERO_DIVISION = "ZeroDivisionError"
    KEY_ERROR = "KeyError"
    INDEX_ERROR = "IndexError"
    VALUE_ERROR = "ValueError"
    TYPE_ERROR = "TypeError"
    ATTRIBUTE_ERROR = "AttributeError"
    JSON_DECODE_ERROR = "JSONDecodeError"
    IMPORT_ERROR = "ImportError"
    NAME_ERROR = "NameError"

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class FixStatus(str, Enum):
    PENDING = "pending"
    GENERATED = "generated"
    APPLIED = "applied"
    PR_CREATED = "pr_created"
    FAILED = "failed"

class ProjectConfig(BaseModel):
    """Configuration for project analysis"""
    github_token: Optional[str] = None
    branch_name: str = "main"
    create_pr: bool = True
    auto_merge: bool = False
    test_command: Optional[str] = None

class AnalysisRequest(BaseModel):
    """Request to start project analysis"""
    github_repo_url: str
    github_token: str
    log_content: str
    branch_name: str = "main"
    create_pr: bool = True

class AnalysisResponse(BaseModel):
    """Response for analysis request"""
    status: str
    message: str
    analysis_id: str

class ErrorInfo(BaseModel):
    """Information about a detected error from logs"""
    error_type: ErrorType
    error_message: str
    traceback: str
    log_line: str
    timestamp: datetime
    file_path: Optional[str] = None
    line_number: Optional[int] = None

class CodeLocation(BaseModel):
    """Location of code in repository"""
    file_path: str
    line_number: int
    function_name: Optional[str] = None
    class_name: Optional[str] = None

class BugReport(BaseModel):
    """Bug report with analysis results"""
    id: str
    error_info: ErrorInfo
    code_location: CodeLocation
    analysis: str
    severity: str = "medium"
    status: AnalysisStatus = AnalysisStatus.PENDING
    created_at: datetime
    updated_at: datetime

class FixSuggestion(BaseModel):
    """Suggested fix for a bug"""
    description: str
    original_code: str
    fixed_code: str
    explanation: str
    confidence: float  # 0.0 to 1.0

class FixResult(BaseModel):
    """Result of applying a fix"""
    bug_id: str
    fix_suggestion: FixSuggestion
    status: FixStatus
    branch_name: Optional[str] = None
    pr_url: Optional[str] = None
    commit_hash: Optional[str] = None
    test_results: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

class MonitoringConfig(BaseModel):
    """Configuration for application monitoring"""
    target_url: HttpUrl
    check_interval: int = 30  # seconds
    endpoints_to_test: List[str] = []
    auth_token: Optional[str] = None
    timeout: int = 10  # seconds

class ProjectStatus(BaseModel):
    """Overall status of a project being monitored"""
    project_url: str
    target_app_url: str
    total_bugs_found: int
    bugs_fixed: int
    bugs_pending: int
    last_check: datetime
    status: AnalysisStatus
