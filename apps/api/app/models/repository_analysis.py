from typing import Optional
from pydantic import BaseModel
from uuid import UUID

from .base import DatabaseModel, DatabaseInsertModel, DatabaseUpdateModel, JsonData

class RepositoryAnalysis(DatabaseModel):
    """Repository analysis table model"""
    repository_id: UUID
    analysis_version: int
    analysis_data: JsonData = None
    tree_structure: Optional[str] = None
    total_files_found: Optional[int] = None
    total_directories: Optional[int] = None
    files_processed: Optional[int] = None
    total_lines: Optional[int] = None
    total_characters: Optional[int] = None
    estimated_tokens: Optional[int] = None
    estimated_size_bytes: Optional[int] = None
    large_files_skipped: Optional[int] = None
    binary_files_skipped: Optional[int] = None
    encoding_errors: Optional[int] = None

class RepositoryAnalysisInsert(DatabaseInsertModel):
    """Repository analysis insert model"""
    repository_id: UUID
    analysis_version: int = 1
    analysis_data: JsonData = None
    tree_structure: Optional[str] = None
    total_files_found: Optional[int] = None
    total_directories: Optional[int] = None
    files_processed: Optional[int] = None
    total_lines: Optional[int] = None
    total_characters: Optional[int] = None
    estimated_tokens: Optional[int] = None
    estimated_size_bytes: Optional[int] = None
    large_files_skipped: Optional[int] = None
    binary_files_skipped: Optional[int] = None
    encoding_errors: Optional[int] = None

class RepositoryAnalysisUpdate(DatabaseUpdateModel):
    """Repository analysis update model"""
    repository_id: Optional[UUID] = None
    analysis_version: Optional[int] = None
    analysis_data: JsonData = None
    tree_structure: Optional[str] = None
    total_files_found: Optional[int] = None
    total_directories: Optional[int] = None
    files_processed: Optional[int] = None
    total_lines: Optional[int] = None
    total_characters: Optional[int] = None
    estimated_tokens: Optional[int] = None
    estimated_size_bytes: Optional[int] = None
    large_files_skipped: Optional[int] = None
    binary_files_skipped: Optional[int] = None
    encoding_errors: Optional[int] = None

class RepositoryAnalysisResponse(BaseModel):
    """Repository analysis response model for API"""
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
    binary_files_skipped: Optional[int] = None
    encoding_errors: Optional[int] = None
    
    class Config:
        from_attributes = True

class RepositoryAnalysisStats(BaseModel):
    """Repository analysis statistics model"""
    total_files_found: Optional[int] = None
    total_directories: Optional[int] = None
    files_processed: Optional[int] = None
    total_lines: Optional[int] = None
    total_characters: Optional[int] = None
    estimated_tokens: Optional[int] = None
    estimated_size_bytes: Optional[int] = None
    processing_stats: dict = {
        "large_files_skipped": 0,
        "binary_files_skipped": 0,
        "encoding_errors": 0
    }
    
    class Config:
        from_attributes = True