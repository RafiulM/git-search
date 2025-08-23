from datetime import datetime
from typing import Optional, List
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
    full_text: Optional[str] = None

    class Config:
        from_attributes = True


class RepositoryAnalysisSummary(BaseModel):
    """Repository analysis summary for API responses"""

    id: UUID
    repository_id: UUID
    analysis_version: int
    total_files_found: Optional[int] = None
    total_directories: Optional[int] = None
    files_processed: Optional[int] = None
    total_lines: Optional[int] = None
    total_characters: Optional[int] = None
    estimated_tokens: Optional[int] = None
    estimated_size_bytes: Optional[int] = None
    large_files_skipped: Optional[int] = None
    tree_structure: Optional[str] = None
    binary_files_skipped: Optional[int] = None
    encoding_errors: Optional[int] = None
    readme_image_src: Optional[str] = None
    ai_summary: Optional[str] = None
    description: Optional[str] = None
    forked_repo_url: Optional[str] = None
    twitter_link: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class RepositoryWithAnalysis(RepositoryResponse):
    """Repository response model with optional analysis data"""

    analysis: Optional[RepositoryAnalysisSummary] = None

    class Config:
        from_attributes = True
