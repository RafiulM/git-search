from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl
from enum import Enum

class SimpleScrapeStatus(str, Enum):
    """Simple scraping status enum"""
    PENDING = "pending"
    SCRAPING = "scraping"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    FAILED = "failed"

class SimpleScrapeRequest(BaseModel):
    """Request model for simple website scraping"""
    website_url: HttpUrl = Field(..., description="Website URL to scrape")
    scraping_type: str = Field("single_page", description="Type of scraping: 'single_page' or 'crawl'")
    max_pages: int = Field(10, ge=1, le=50, description="Maximum pages to crawl (for crawl type)")
    auto_save: bool = Field(True, description="Automatically save extracted repositories")

class ExtractedRepoInfo(BaseModel):
    """Information about an extracted repository"""
    name: str
    url: str
    author: Optional[str] = None
    description: Optional[str] = None
    confidence_score: float = 0.0

class SimpleScrapeTaskResponse(BaseModel):
    """Response model for starting a scraping task"""
    task_id: str
    status: SimpleScrapeStatus
    message: str
    website_url: str

class SimpleScrapeResult(BaseModel):
    """Final result of a scraping operation"""
    task_id: str
    status: SimpleScrapeStatus
    website_url: str
    repositories_found: int
    repositories_saved: int
    extracted_repositories: List[ExtractedRepoInfo]
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None