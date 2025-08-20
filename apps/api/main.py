from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
import logging
import os
from app.routers import repo_analysis, tasks, prompts
from app.services.auth import require_api_key, optional_api_key

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
# Validate log level
if not hasattr(logging, log_level):
    log_level = "INFO"  # Default to INFO if level is not valid

logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Git-Search Repository Analysis API",
    description="""
    Backend API for analyzing GitHub repositories using repo2text
    
    ## Authentication
    This API requires authentication via API key in the Authorization header:
    ```
    Authorization: Bearer <your-api-key>
    ```
    
    ## Environment Variables Required
    - `API_KEY`: Your API key for authentication
    - `FIRECRAWL_API_KEY`: Firecrawl API key for website scraping
    - `GOOGLE_AI_API_KEY`: Google AI API key for Gemini models
    - `SUPABASE_URL`: Supabase database URL
    - `SUPABASE_KEY`: Supabase API key
    - `TWITTER_CONSUMER_KEY`: Twitter API consumer key (optional, for tweeting)
    - `TWITTER_CONSUMER_SECRET`: Twitter API consumer secret (optional)
    - `TWITTER_ACCESS_TOKEN`: Twitter API access token (optional)
    - `TWITTER_ACCESS_TOKEN_SECRET`: Twitter API access token secret (optional)
    - `TWITTER_BEARER_TOKEN`: Twitter API bearer token (optional)
    """,
    version="1.0.0",
)

logger.info("Starting Git-Search Repository Analysis API")

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    repo_analysis.router, prefix="/api/analysis", tags=["repository-analysis"]
)
app.include_router(tasks.router, prefix="/api/tasks", tags=["background-tasks"])
app.include_router(prompts.router, prefix="/api/prompts", tags=["prompts"])


@app.get("/")
async def root(api_key: str = Depends(optional_api_key)):
    """Root endpoint - provides API information"""
    auth_status = "authenticated" if api_key else "unauthenticated"

    return {
        "message": "Git-Search Repository Analysis API",
        "description": "API for analyzing GitHub repositories using repo2text",
        "authentication": auth_status,
        "endpoints": {
            "docs": "/docs",
            "analysis": "/api/analysis",
            "tasks": "/api/tasks",
        },
        "note": "All endpoints except /health require API key authentication",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "repository-analysis"}


if __name__ == "__main__":
    import uvicorn
    import argparse
    import os

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Git-Search Repository Analysis API")
    parser.add_argument(
        "--host", default="127.0.0.1", help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=int(os.getenv("API_PORT", 8888)), help="Port to bind the server to"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload on code changes"
    )
    parser.add_argument(
        "--workers", type=int, default=1, help="Number of worker processes"
    )

    args = parser.parse_args()

    # Run the server
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=(
            args.workers if not args.reload else 1
        ),  # Workers must be 1 when reload is enabled
        log_level="info",
    )
