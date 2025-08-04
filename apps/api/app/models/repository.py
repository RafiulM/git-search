from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from uuid import UUID

from .base import DatabaseModel, DatabaseInsertModel, DatabaseUpdateModel

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

class RepositoryResponse(BaseModel):
    """Repository response model for API"""
    id: UUID
    name: str
    repo_url: str
    author: Optional[str] = None
    branch: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True