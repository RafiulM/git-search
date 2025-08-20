from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl
from uuid import UUID
from enum import Enum

from .base import DatabaseModel, DatabaseInsertModel, DatabaseUpdateModel

class ScrapingStatus(str, Enum):
    """Website scraping status enum"""
    PENDING = "pending"
    SCRAPING = "scraping"
    PROCESSING = "processing"
    EXTRACTING = "extracting"
    SAVING = "saving"
    COMPLETED = "completed"
    FAILED = "failed"

class ExtractedRepositoryInfo(BaseModel):
    """Schema for extracted repository information"""
    url: str = Field(..., description="The repository URL (must be a valid Git repository URL)")
    name: Optional[str] = Field(None, description="Repository name (extracted from URL or context)")
    author: Optional[str] = Field(None, description="Repository owner/author")
    description: Optional[str] = Field(None, description="Repository description if available")
    language: Optional[str] = Field(None, description="Primary programming language")
    stars: Optional[int] = Field(None, description="Number of stars if available")
    
class ExtractedRepositories(BaseModel):
    """Schema for structured output from Gemini containing list of repositories"""
    repositories: List[ExtractedRepositoryInfo] = Field(
        ..., 
        description="List of repository information extracted from the website content"
    )
    total_found: int = Field(
        ..., 
        description="Total number of repositories found"
    )
    extraction_confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence score of the extraction (0.0 to 1.0)"
    )
    notes: Optional[str] = Field(
        None, 
        description="Additional notes about the extraction process"
    )

class WebsiteScraping(DatabaseModel):
    """Website scraping table model"""
    website_url: str
    scraping_type: str = "single_page"  # "single_page" or "crawl"
    status: ScrapingStatus = ScrapingStatus.PENDING
    scraped_content: Optional[str] = None
    extracted_repositories: Optional[List[str]] = []  # List of repository URLs
    repositories_saved: int = 0
    total_repositories_found: int = 0
    extraction_confidence: Optional[float] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = None

class WebsiteScrapingInsert(DatabaseInsertModel):
    """Website scraping insert model"""
    website_url: str
    scraping_type: str = "single_page"
    status: ScrapingStatus = ScrapingStatus.PENDING
    scraped_content: Optional[str] = None
    extracted_repositories: Optional[List[str]] = []
    repositories_saved: int = 0
    total_repositories_found: int = 0
    extraction_confidence: Optional[float] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = None

class WebsiteScrapingUpdate(DatabaseUpdateModel):
    """Website scraping update model"""
    website_url: Optional[str] = None
    scraping_type: Optional[str] = None
    status: Optional[ScrapingStatus] = None
    scraped_content: Optional[str] = None
    extracted_repositories: Optional[List[str]] = None
    repositories_saved: Optional[int] = None
    total_repositories_found: Optional[int] = None
    extraction_confidence: Optional[float] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Optional[dict] = None

class WebsiteScrapingResponse(BaseModel):
    """Website scraping response model for API"""
    id: UUID
    website_url: str
    scraping_type: str
    status: ScrapingStatus
    scraped_content: Optional[str] = None
    extracted_repositories: List[str]
    repositories_saved: int
    total_repositories_found: int
    extraction_confidence: Optional[float] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    metadata: Optional[dict] = None
    
    class Config:
        from_attributes = True

class WebsiteScrapingRequest(BaseModel):
    """Request model for website scraping"""
    website_url: HttpUrl = Field(..., description="Website URL to scrape")
    scraping_type: str = Field("single_page", description="Type of scraping: 'single_page' or 'crawl'")
    max_pages: int = Field(10, ge=1, le=50, description="Maximum pages to crawl (for crawl type)")
    auto_save: bool = Field(True, description="Automatically save extracted repositories to database")
    
class WebsiteScrapingTaskResponse(BaseModel):
    """Response model for starting website scraping task"""
    scraping_id: UUID
    status: ScrapingStatus
    message: str
    website_url: str