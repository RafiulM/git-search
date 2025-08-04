from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field
from uuid import UUID

class TimestampedModel(BaseModel):
    """Base model with timestamp fields"""
    created_at: datetime
    updated_at: datetime

class DatabaseModel(TimestampedModel):
    """Base model for database entities with ID and timestamps"""
    id: UUID

class DatabaseInsertModel(BaseModel):
    """Base model for database inserts (no ID or timestamps)"""
    pass

class DatabaseUpdateModel(BaseModel):
    """Base model for database updates (optional fields)"""
    pass

# Type alias for JSON fields
JsonData = Optional[Dict[str, Any]]