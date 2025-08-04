from typing import Optional
from pydantic import BaseModel
from uuid import UUID

from .base import DatabaseModel, DatabaseInsertModel, DatabaseUpdateModel, JsonData

class AISummary(DatabaseModel):
    """AI-generated repository summary table model"""
    repository_id: UUID
    summary_text: str
    summary_type: str = "ai_generated"  # ai_generated, manual, etc.
    model_used: Optional[str] = None  # e.g., "gemini-2.0-flash"
    processing_stats: JsonData = None
    chunk_count: Optional[int] = None
    successful_chunks: Optional[int] = None
    failed_chunks: Optional[int] = None
    summary_version: int = 1
    is_current: bool = True

class AISummaryInsert(DatabaseInsertModel):
    """AI summary insert model"""
    repository_id: UUID
    summary_text: str
    summary_type: str = "ai_generated"
    model_used: Optional[str] = None
    processing_stats: JsonData = None
    chunk_count: Optional[int] = None
    successful_chunks: Optional[int] = None
    failed_chunks: Optional[int] = None
    summary_version: int = 1
    is_current: bool = True

class AISummaryUpdate(DatabaseUpdateModel):
    """AI summary update model"""
    repository_id: Optional[UUID] = None
    summary_text: Optional[str] = None
    summary_type: Optional[str] = None
    model_used: Optional[str] = None
    processing_stats: JsonData = None
    chunk_count: Optional[int] = None
    successful_chunks: Optional[int] = None
    failed_chunks: Optional[int] = None
    summary_version: Optional[int] = None
    is_current: Optional[bool] = None

class AISummaryResponse(BaseModel):
    """AI summary response model for API"""
    id: UUID
    repository_id: UUID
    summary_text: str
    summary_type: str
    model_used: Optional[str] = None
    chunk_count: Optional[int] = None
    successful_chunks: Optional[int] = None
    failed_chunks: Optional[int] = None
    summary_version: int
    is_current: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True