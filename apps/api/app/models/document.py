from typing import Optional
from pydantic import BaseModel
from uuid import UUID

from .base import DatabaseModel, DatabaseInsertModel, DatabaseUpdateModel, JsonData

class Document(DatabaseModel):
    """Document table model"""
    repository_analysis_id: UUID
    title: str
    content: str
    document_type: str
    description: Optional[str] = None
    version: int
    is_current: Optional[bool] = None
    parent_document_id: Optional[UUID] = None
    generated_by: Optional[str] = None
    model_used: Optional[str] = None
    generation_prompt: Optional[str] = None
    metadata: JsonData = None

class DocumentInsert(DatabaseInsertModel):
    """Document insert model"""
    repository_analysis_id: UUID
    title: str
    content: str
    document_type: str
    description: Optional[str] = None
    version: int = 1
    is_current: Optional[bool] = True
    parent_document_id: Optional[UUID] = None
    generated_by: Optional[str] = None
    model_used: Optional[str] = None
    generation_prompt: Optional[str] = None
    metadata: JsonData = None

class DocumentUpdate(DatabaseUpdateModel):
    """Document update model"""
    repository_analysis_id: Optional[UUID] = None
    title: Optional[str] = None
    content: Optional[str] = None
    document_type: Optional[str] = None
    description: Optional[str] = None
    version: Optional[int] = None
    is_current: Optional[bool] = None
    parent_document_id: Optional[UUID] = None
    generated_by: Optional[str] = None
    model_used: Optional[str] = None
    generation_prompt: Optional[str] = None
    metadata: JsonData = None

class DocumentResponse(BaseModel):
    """Document response model for API"""
    id: UUID
    repository_analysis_id: UUID
    title: str
    content: str
    document_type: str
    description: Optional[str] = None
    version: int
    is_current: Optional[bool] = None
    
    class Config:
        from_attributes = True

class DocumentSummary(BaseModel):
    """Document summary model (without content)"""
    id: UUID
    repository_analysis_id: UUID
    title: str
    document_type: str
    description: Optional[str] = None
    version: int
    is_current: Optional[bool] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True