from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID
from enum import Enum

from .base import DatabaseModel, DatabaseInsertModel, DatabaseUpdateModel

class TwitterPostingStatus(str, Enum):
    """Twitter posting status enum"""
    PENDING = "pending"
    PROCESSING = "processing"
    POSTING = "posting"
    COMPLETED = "completed"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"

class TwitterPosting(DatabaseModel):
    """Twitter posting job table model"""
    job_name: str
    total_repositories: int
    processed_repositories: int = 0
    successful_posts: int = 0
    failed_posts: int = 0
    rate_limited_posts: int = 0
    status: TwitterPostingStatus = TwitterPostingStatus.PENDING
    repository_ids: List[str] = []
    posted_tweet_urls: List[str] = []
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = None

class TwitterPostingInsert(DatabaseInsertModel):
    """Twitter posting insert model"""
    job_name: str
    total_repositories: int
    processed_repositories: int = 0
    successful_posts: int = 0
    failed_posts: int = 0
    rate_limited_posts: int = 0
    status: TwitterPostingStatus = TwitterPostingStatus.PENDING
    repository_ids: List[str] = []
    posted_tweet_urls: List[str] = []
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = None

class TwitterPostingUpdate(DatabaseUpdateModel):
    """Twitter posting update model"""
    job_name: Optional[str] = None
    total_repositories: Optional[int] = None
    processed_repositories: Optional[int] = None
    successful_posts: Optional[int] = None
    failed_posts: Optional[int] = None
    rate_limited_posts: Optional[int] = None
    status: Optional[TwitterPostingStatus] = None
    repository_ids: Optional[List[str]] = None
    posted_tweet_urls: Optional[List[str]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = None

class TwitterPostingResponse(BaseModel):
    """Twitter posting response model for API"""
    id: UUID
    job_name: str
    total_repositories: int
    processed_repositories: int
    successful_posts: int
    failed_posts: int
    rate_limited_posts: int
    status: TwitterPostingStatus
    repository_ids: List[str]
    posted_tweet_urls: List[str]
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict] = None
    
    class Config:
        from_attributes = True

class TwitterPostingRequest(BaseModel):
    """Request model for Twitter posting"""
    job_name: Optional[str] = Field(None, description="Name for this Twitter posting job")
    max_repositories: int = Field(5, ge=1, le=50, description="Maximum number of repositories to post (1-50)")
    delay_between_posts: int = Field(30, ge=10, le=300, description="Delay in seconds between posts (10-300)")
    include_analysis: bool = Field(False, description="Include repository analysis data in tweets")
    
class TwitterPostingTaskResponse(BaseModel):
    """Response model for starting Twitter posting task"""
    posting_id: UUID
    status: TwitterPostingStatus
    message: str
    total_repositories: int