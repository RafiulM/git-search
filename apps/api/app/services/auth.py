import os
import logging
from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class APIKeyAuth:
    """API Key authentication service"""
    
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        if not self.api_key:
            logger.warning("API_KEY not found in environment variables. API authentication will be disabled.")
        
        # Security scheme for Swagger UI
        self.security = HTTPBearer(
            scheme_name="API Key",
            description="Enter your API key as a Bearer token"
        )
    
    def is_enabled(self) -> bool:
        """Check if API key authentication is enabled"""
        return self.api_key is not None and len(self.api_key) > 0
    
    def validate_api_key(self, api_key: str) -> bool:
        """Validate the provided API key"""
        if not self.is_enabled():
            # If API key auth is not configured, allow all requests
            return True
        
        return api_key == self.api_key
    
    async def get_api_key(self, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())) -> str:
        """
        FastAPI dependency to extract and validate API key from Authorization header
        Expected format: Authorization: Bearer <api_key>
        """
        if not self.is_enabled():
            # If API key auth is not configured, allow all requests
            return "no-auth-required"
        
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required. Please provide your API key in the Authorization header as a Bearer token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        api_key = credentials.credentials
        
        if not self.validate_api_key(api_key):
            logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug("API key validation successful")
        return api_key

    async def get_optional_api_key(self, credentials: Optional[HTTPAuthorizationCredentials] = Security(HTTPBearer(auto_error=False))) -> Optional[str]:
        """
        Optional API key dependency for endpoints that can work with or without authentication
        """
        if not self.is_enabled():
            return "no-auth-required"
        
        if not credentials:
            return None
        
        api_key = credentials.credentials
        
        if not self.validate_api_key(api_key):
            return None
        
        return api_key

# Global API key service instance
api_key_auth = APIKeyAuth()

# FastAPI dependency functions
async def require_api_key(api_key: str = Security(api_key_auth.get_api_key)) -> str:
    """FastAPI dependency that requires a valid API key"""
    return api_key

async def optional_api_key(api_key: Optional[str] = Security(api_key_auth.get_optional_api_key)) -> Optional[str]:
    """FastAPI dependency for optional API key authentication"""
    return api_key