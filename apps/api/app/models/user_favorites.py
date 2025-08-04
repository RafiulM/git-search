from typing import Optional
from pydantic import BaseModel
from uuid import UUID

from .base import DatabaseModel, DatabaseInsertModel, DatabaseUpdateModel

class UserFavorites(DatabaseModel):
    """User favorites table model"""
    user_id: str  # Clerk user ID (string)
    repository_id: UUID

class UserFavoritesInsert(DatabaseInsertModel):
    """User favorites insert model"""
    user_id: str  # Clerk user ID (string)
    repository_id: UUID

class UserFavoritesUpdate(DatabaseUpdateModel):
    """User favorites update model"""
    user_id: Optional[str] = None
    repository_id: Optional[UUID] = None

class UserFavoritesResponse(BaseModel):
    """User favorites response model for API"""
    id: UUID
    user_id: str
    repository_id: UUID
    created_at: str
    
    class Config:
        from_attributes = True

class FavoriteToggleRequest(BaseModel):
    """Request model for toggling favorites"""
    repository_id: UUID

class FavoriteStatusResponse(BaseModel):
    """Response model for favorite status"""
    repository_id: UUID
    is_favorited: bool
    favorite_count: Optional[int] = None