# Models package

from .base import DatabaseModel, DatabaseInsertModel, DatabaseUpdateModel, JsonData
from .repository import (
    Repository,
    RepositoryInsert,
    RepositoryUpdate,
    RepositoryResponse,
    RepositoryProcessingStatus,
    RepositoryWithAnalysis,
    RepositoryAnalysisSummary,
)
from .document import (
    Document,
    DocumentInsert,
    DocumentUpdate,
    DocumentResponse,
    DocumentSummary,
)
from .repository_analysis import (
    RepositoryAnalysis,
    RepositoryAnalysisInsert,
    RepositoryAnalysisUpdate,
    RepositoryAnalysisResponse,
    RepositoryAnalysisStats,
)
from .user_favorites import (
    UserFavorites,
    UserFavoritesInsert,
    UserFavoritesUpdate,
    UserFavoritesResponse,
    FavoriteToggleRequest,
    FavoriteStatusResponse,
)
from .repository_summary import RepositorySummary, RepositorySummaryResponse
from .ai_summary import AISummary, AISummaryInsert, AISummaryUpdate, AISummaryResponse
from .task_models import (
    TaskStatus,
    RepositoryAnalysisTaskRequest,
    TaskResponse,
    TaskStatusResponse,
    RepositoryAnalysisResult,
    TaskListResponse,
    RepositoryInfo,
    AnalysisStats,
    RepositoryAnalysisTaskResult,
)
from .batch_processing import (
    BatchStatus,
    BatchProcessing,
    BatchProcessingInsert,
    BatchProcessingUpdate,
    BatchProcessingResponse,
    BatchProcessingRequest,
)

# Old website scraping models removed - using simple_scraping instead
from .twitter_posting import (
    TwitterPostingStatus,
    TwitterPosting,
    TwitterPostingInsert,
    TwitterPostingUpdate,
    TwitterPostingResponse,
    TwitterPostingRequest,
    TwitterPostingTaskResponse,
)
from .simple_scraping import (
    SimpleScrapeStatus,
    SimpleScrapeRequest,
    SimpleScrapeTaskResponse,
    SimpleScrapeResult,
    ExtractedRepoInfo,
)
from .prompt import (
    PromptType,
    Prompt,
    PromptInsert,
    PromptUpdate,
    PromptResponse,
)

__all__ = [
    # Base models
    "DatabaseModel",
    "DatabaseInsertModel",
    "DatabaseUpdateModel",
    "JsonData",
    # Repository models
    "Repository",
    "RepositoryInsert",
    "RepositoryUpdate",
    "RepositoryResponse",
    "RepositoryProcessingStatus",
    "RepositoryWithAnalysis",
    # Document models
    "Document",
    "DocumentInsert",
    "DocumentUpdate",
    "DocumentResponse",
    "DocumentSummary",
    # Repository analysis models
    "RepositoryAnalysis",
    "RepositoryAnalysisInsert",
    "RepositoryAnalysisUpdate",
    "RepositoryAnalysisResponse",
    "RepositoryAnalysisStats",
    # User favorites models
    "UserFavorites",
    "UserFavoritesInsert",
    "UserFavoritesUpdate",
    "UserFavoritesResponse",
    "FavoriteToggleRequest",
    "FavoriteStatusResponse",
    # Repository summary models
    "RepositorySummary",
    "RepositorySummaryResponse",
    # AI summary models
    "AISummary",
    "AISummaryInsert",
    "AISummaryUpdate",
    "AISummaryResponse",
    # Task models
    "TaskStatus",
    "RepositoryAnalysisTaskRequest",
    "TaskResponse",
    "TaskStatusResponse",
    "RepositoryAnalysisResult",
    "TaskListResponse",
    "RepositoryInfo",
    "AnalysisStats",
    "RepositoryAnalysisTaskResult",
    # Batch processing models
    "BatchStatus",
    "BatchProcessing",
    "BatchProcessingInsert",
    "BatchProcessingUpdate",
    "BatchProcessingResponse",
    "BatchProcessingRequest",
    # Twitter posting models
    "TwitterPostingStatus",
    "TwitterPosting",
    "TwitterPostingInsert",
    "TwitterPostingUpdate",
    "TwitterPostingResponse",
    "TwitterPostingRequest",
    "TwitterPostingTaskResponse",
    # Simple scraping models
    "SimpleScrapeStatus",
    "SimpleScrapeRequest",
    "SimpleScrapeTaskResponse",
    "SimpleScrapeResult",
    "ExtractedRepoInfo",
    # Prompt models
    "PromptType",
    "Prompt",
    "PromptInsert",
    "PromptUpdate",
    "PromptResponse",
]
