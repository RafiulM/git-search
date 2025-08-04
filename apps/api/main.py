from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging
import os
from app.routers import repo_analysis, tasks

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Git-Search Repository Analysis API",
    description="Backend API for analyzing GitHub repositories using repo2text",
    version="1.0.0"
)

logger.info("Starting Git-Search Repository Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(repo_analysis.router, prefix="/api/analysis", tags=["repository-analysis"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["background-tasks"])

@app.get("/")
async def root():
    return {
        "message": "Git-Search Repository Analysis API", 
        "description": "API for analyzing GitHub repositories using repo2text",
        "endpoints": {
            "docs": "/docs",
            "analysis": "/api/analysis",
            "tasks": "/api/tasks"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "repository-analysis"}

if __name__ == "__main__":
    import uvicorn
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Git-Search Repository Analysis API")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument("--port", type=int, default=8888, help="Port to bind the server to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code changes")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    
    args = parser.parse_args()
    
    # Run the server
    uvicorn.run(
        "main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,  # Workers must be 1 when reload is enabled
        log_level="info"
    )