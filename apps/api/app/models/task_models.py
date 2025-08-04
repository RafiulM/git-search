from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

class TaskStatus(str, Enum):
    """Task status enum"""
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"

class RepositoryAnalysisTaskRequest(BaseModel):
    """Request model for repository analysis task"""
    github_url: HttpUrl = Field(..., description="GitHub repository URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "github_url": "https://github.com/owner/repository"
            }
        }

class TaskResponse(BaseModel):
    """Response model for task creation"""
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    message: str = Field(..., description="Human-readable status message")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True

class TaskStatusResponse(BaseModel):
    """Response model for task status"""
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    message: str = Field(..., description="Human-readable status message")
    progress: Optional[int] = Field(None, ge=0, le=100, description="Progress percentage (0-100)")
    repo_id: Optional[str] = Field(None, description="Repository ID (when available)")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result (when completed)")
    error: Optional[str] = Field(None, description="Error message (when failed)")
    
    class Config:
        use_enum_values = True

class RepositoryAnalysisResult(BaseModel):
    """Repository analysis result model"""
    repo_id: str
    analysis_id: str
    repository: Dict[str, str]
    stats: Dict[str, Any]
    status: str = "completed"
    progress: int = 100

class TaskListResponse(BaseModel):
    """Response model for task list"""
    tasks: list[TaskStatusResponse]
    total: int
    page: int = 1
    per_page: int = 10

class RepositoryInfo(BaseModel):
    """Repository information model"""
    name: str
    author: str
    url: str
    full_name: str

class AnalysisStats(BaseModel):
    """Analysis statistics model"""
    total_files: int = 0
    total_directories: int = 0
    files_processed: int = 0
    total_lines: int = 0
    total_characters: int = 0
    estimated_tokens: int = 0
    total_size_bytes: int = 0
    large_files_skipped: int = 0
    binary_files_skipped: int = 0
    encoding_errors: int = 0

class RepositoryAnalysisTaskResult(BaseModel):
    """Complete repository analysis task result"""
    task_id: str
    status: TaskStatus
    repository: Optional[RepositoryInfo] = None
    analysis: Optional[Dict[str, Any]] = None
    stats: Optional[AnalysisStats] = None
    progress: int = 0
    message: str = ""
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True