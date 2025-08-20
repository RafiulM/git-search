from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID
from enum import Enum

from .base import DatabaseModel, DatabaseInsertModel, DatabaseUpdateModel

class RepositoryProcessingStatus(str, Enum):
    """Repository processing status enum"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    DOCS_GENERATED = "docs_generated"
    COMPLETED = "completed"
    FAILED = "failed"

class Repository(DatabaseModel):
    """Repository table model"""
    name: str
    repo_url: str
    author: Optional[str] = None
    branch: Optional[str] = None
    content_url: Optional[str] = None
    content_expires_at: Optional[datetime] = None
    full_text: Optional[str] = None
    full_text_path: Optional[str] = None
    twitter_link: Optional[str] = None
    processing_status: RepositoryProcessingStatus = RepositoryProcessingStatus.PENDING

class RepositoryInsert(DatabaseInsertModel):
    """Repository insert model"""
    name: str
    repo_url: str
    author: Optional[str] = None
    branch: Optional[str] = None
    content_url: Optional[str] = None
    content_expires_at: Optional[datetime] = None
    full_text: Optional[str] = None
    full_text_path: Optional[str] = None
    twitter_link: Optional[str] = None
    processing_status: RepositoryProcessingStatus = RepositoryProcessingStatus.PENDING

class RepositoryUpdate(DatabaseUpdateModel):
    """Repository update model"""
    name: Optional[str] = None
    repo_url: Optional[str] = None
    author: Optional[str] = None
    branch: Optional[str] = None
    content_url: Optional[str] = None
    content_expires_at: Optional[datetime] = None
    full_text: Optional[str] = None
    full_text_path: Optional[str] = None
    twitter_link: Optional[str] = None
    processing_status: Optional[RepositoryProcessingStatus] = None

class RepositoryResponse(BaseModel):
    """Repository response model for API"""
    id: UUID
    name: str
    repo_url: str
    author: Optional[str] = None
    branch: Optional[str] = None
    twitter_link: Optional[str] = None
    processing_status: RepositoryProcessingStatus = RepositoryProcessingStatus.PENDING
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True