from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID

from .base import JsonData

class RepositorySummary(BaseModel):
    """Repository summary view model - read-only"""
    id: Optional[UUID] = None
    name: Optional[str] = None
    repo_url: Optional[str] = None
    author: Optional[str] = None
    branch: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Analysis data
    analysis_created_at: Optional[datetime] = None
    analysis_data: JsonData = None
    estimated_size_bytes: Optional[int] = None
    estimated_tokens: Optional[int] = None
    files_processed: Optional[int] = None
    total_characters: Optional[int] = None
    total_directories: Optional[int] = None
    total_files_found: Optional[int] = None
    total_lines: Optional[int] = None
    tree_structure: Optional[str] = None
    
    # Favorite data
    favorite_count: Optional[int] = None
    
    class Config:
        from_attributes = True

class RepositorySummaryResponse(BaseModel):
    """Repository summary response model for API"""
    id: UUID
    name: str
    repo_url: str
    author: Optional[str] = None
    branch: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Analysis stats
    stats: Optional[dict] = None
    favorite_count: Optional[int] = None
    
    class Config:
        from_attributes = True