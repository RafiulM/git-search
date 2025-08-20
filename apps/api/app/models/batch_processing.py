from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from uuid import UUID
from enum import Enum

from .base import DatabaseModel, DatabaseInsertModel, DatabaseUpdateModel

class BatchStatus(str, Enum):
    """Batch processing status enum"""
    PENDING = "pending"
    PROCESSING = "processing" 
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class BatchProcessing(DatabaseModel):
    """Batch processing table model"""
    batch_name: str
    total_repositories: int
    processed_repositories: int = 0
    successful_repositories: int = 0
    failed_repositories: int = 0
    status: BatchStatus = BatchStatus.PENDING
    repository_ids: List[str] = []
    task_ids: List[str] = []
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class BatchProcessingInsert(DatabaseInsertModel):
    """Batch processing insert model"""
    batch_name: str
    total_repositories: int
    processed_repositories: int = 0
    successful_repositories: int = 0
    failed_repositories: int = 0
    status: BatchStatus = BatchStatus.PENDING
    repository_ids: List[str] = []
    task_ids: List[str] = []
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class BatchProcessingUpdate(DatabaseUpdateModel):
    """Batch processing update model"""
    batch_name: Optional[str] = None
    total_repositories: Optional[int] = None
    processed_repositories: Optional[int] = None
    successful_repositories: Optional[int] = None
    failed_repositories: Optional[int] = None
    status: Optional[BatchStatus] = None
    repository_ids: Optional[List[str]] = None
    task_ids: Optional[List[str]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class BatchProcessingResponse(BaseModel):
    """Batch processing response model for API"""
    id: UUID
    batch_name: str
    total_repositories: int
    processed_repositories: int
    successful_repositories: int
    failed_repositories: int
    status: BatchStatus
    repository_ids: List[str]
    task_ids: List[str]
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BatchProcessingRequest(BaseModel):
    """Request model for starting batch processing"""
    batch_name: Optional[str] = None
    max_repositories: int = 5
    process_type: str = "analysis_and_docs"  # "analysis_only", "docs_only", "analysis_and_docs"