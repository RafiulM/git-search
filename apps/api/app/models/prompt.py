from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from enum import Enum

from .base import DatabaseModel, DatabaseInsertModel, DatabaseUpdateModel

class PromptType(str, Enum):
    """Prompt type enum"""
    REPOSITORY_SUMMARY = "repository_summary"
    CODE_REVIEW = "code_review"
    ARCHITECTURE_ANALYSIS = "architecture_analysis"
    DOCUMENTATION_GENERATION = "documentation_generation"
    CUSTOM = "custom"

class Prompt(DatabaseModel):
    """Prompt table model"""
    name: str
    type: PromptType
    content: str
    version: int = 1
    is_active: bool = True
    description: Optional[str] = None
    metadata: Optional[dict] = None

class PromptInsert(DatabaseInsertModel):
    """Prompt insert model"""
    name: str
    type: PromptType
    content: str
    version: int = 1
    is_active: bool = True
    description: Optional[str] = None
    metadata: Optional[dict] = None

class PromptUpdate(DatabaseUpdateModel):
    """Prompt update model"""
    name: Optional[str] = None
    type: Optional[PromptType] = None
    content: Optional[str] = None
    version: Optional[int] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
    metadata: Optional[dict] = None

class PromptResponse(BaseModel):
    """Prompt response model for API"""
    id: UUID
    name: str
    type: PromptType
    content: str
    version: int
    is_active: bool
    description: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True