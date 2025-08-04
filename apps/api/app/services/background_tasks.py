import os
import tempfile
import shutil
from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime
import asyncio
from urllib.parse import urlparse
import json
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

from repo2text.core import RepoAnalyzer

from app.services.database import db_service
from app.services.gemini_ai import gemini_service
from app.models import (
    RepositoryInsert, 
    RepositoryAnalysisInsert,
    DocumentInsert
)

class TaskStatus:
    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"

# Simple in-memory task storage
# In production, you might want to use Redis or database for persistence
task_storage: Dict[str, Dict[str, Any]] = {}

def extract_repo_info(github_url: str) -> Dict[str, str]:
    """Extract repository information from GitHub URL"""
    try:
        # Handle different GitHub URL formats
        if github_url.endswith('.git'):
            github_url = github_url[:-4]
        
        # Parse URL
        parsed = urlparse(github_url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")
        
        owner = path_parts[0]
        repo_name = path_parts[1]
        
        return {
            "owner": owner,
            "repo_name": repo_name,
            "full_name": f"{owner}/{repo_name}",
            "clone_url": f"https://github.com/{owner}/{repo_name}.git"
        }
    except Exception as e:
        raise ValueError(f"Invalid GitHub URL: {str(e)}")

async def analyze_repository_task(task_id: str, github_url: str):
    """Background task to analyze a GitHub repository using repo2text"""
    logger.info(f"Starting repository analysis task {task_id} for {github_url}")
    repo_info = None
    temp_clone_dir = None
    temp_output_dir = None
    
    try:
        # Update task state
        update_task_status(task_id, TaskStatus.STARTED, "Extracting repository information", 10)
        
        # Extract repository information
        repo_info = extract_repo_info(github_url)
        
        # Check if repository already exists
        existing_repo = await db_service.get_repository_by_url(github_url)
        
        if existing_repo:
            repo_id = existing_repo.id
            logger.info(f"Using existing repository {repo_id} for {github_url}")
        else:
            # Create new repository entry
            repo_data = RepositoryInsert(
                name=repo_info["repo_name"],
                repo_url=github_url,
                author=repo_info["owner"]
            )
            
            new_repo = await db_service.create_repository(repo_data)
            repo_id = new_repo.id
            logger.info(f"Created new repository {repo_id} for {github_url}")
        
        # Update task state
        update_task_status(task_id, TaskStatus.STARTED, "Initializing repository analyzer", 20, repo_id=str(repo_id))
        
        # Create temporary directories
        temp_clone_dir = tempfile.mkdtemp(prefix="repo_clone_")
        temp_output_dir = tempfile.mkdtemp(prefix="repo_output_")
        
        # Get GitHub token if available
        github_token = os.getenv("GITHUB_TOKEN")
        
        # Initialize repo analyzer with proper parameters
        analyzer = RepoAnalyzer(
            token=github_token,
            clone_dir=temp_clone_dir,
            output_dir=temp_output_dir,
            max_file_size_mb=10
        )
        
        # Update task state
        update_task_status(task_id, TaskStatus.STARTED, "Processing repository with repo2text", 30, repo_id=str(repo_id))
        
        # Process repository using repo2text
        result = analyzer.process_repository(github_url, keep_clone=False)
        
        if not result.get("success"):
            raise Exception(f"repo2text analysis failed: {result.get('error', 'Unknown error')}")
        
        # Update task state
        update_task_status(task_id, TaskStatus.STARTED, "Extracting analysis data", 60, repo_id=str(repo_id))
        
        # Read the generated output file to get the full content
        output_file_path = result["output_file"]
        repo_content = ""
        if os.path.exists(output_file_path):
            with open(output_file_path, 'r', encoding='utf-8') as f:
                repo_content = f.read()
        
        # Prepare statistics from repo2text result
        stats = {
            "files_processed": result["files_processed"],
            "binary_files_skipped": result["binary_files_skipped"],
            "large_files_skipped": result["large_files_skipped"],
            "encoding_errors": result["encoding_errors"],
            "total_characters": result["total_characters"],
            "total_lines": result["total_lines"],
            "total_files": result["total_files"],
            "total_directories": result["total_directories"],
            "estimated_tokens": int(result["total_characters"] / 4),  # Rough token estimate
            "total_size_bytes": result["total_characters"]
        }
        
        # Extract tree structure from repo2text result
        tree_structure = result.get("tree_structure", None)
        
        # Update task state
        update_task_status(task_id, TaskStatus.STARTED, "Saving analysis to database", 75, repo_id=str(repo_id))
        
        # Create repository analysis entry
        analysis_data = RepositoryAnalysisInsert(
            repository_id=repo_id,
            analysis_version=1,
            analysis_data=stats,
            tree_structure=tree_structure,
            total_files_found=stats["total_files"],
            total_directories=stats["total_directories"],
            files_processed=stats["files_processed"],
            total_lines=stats["total_lines"],
            total_characters=stats["total_characters"],
            estimated_tokens=stats["estimated_tokens"],
            estimated_size_bytes=stats["total_size_bytes"],
            large_files_skipped=stats["large_files_skipped"],
            binary_files_skipped=stats["binary_files_skipped"],
            encoding_errors=stats["encoding_errors"]
        )
        
        analysis = await db_service.create_repository_analysis(analysis_data)
        
        # Update task state
        update_task_status(task_id, TaskStatus.STARTED, "Saving repository content", 85, repo_id=str(repo_id))
        
        # Save repository content as document
        if repo_content:
            doc_data = DocumentInsert(
                repository_id=repo_id,
                title="Repository Analysis",
                content=repo_content,
                document_type="repository_analysis",
                description=f"Complete repository analysis for {repo_info['full_name']} generated by repo2text",
                version=1,
                is_current=True,
                generated_by="repo2text",
                metadata={
                    "source": "repo2text",
                    "github_url": github_url,
                    "analysis_id": str(analysis.id),
                    "stats": stats,
                    "output_file": os.path.basename(output_file_path)
                }
            )
            
            document = await db_service.create_document(doc_data)
        
        # Update task state
        update_task_status(task_id, TaskStatus.STARTED, "Generating AI summary", 90, repo_id=str(repo_id))
        
        # Generate AI summary using Gemini
        summary_result = None
        try:
            # Default system prompt for repository analysis
            system_prompt = """You are an expert code reviewer and software architect. 
            Analyze the provided repository content and create a comprehensive summary that helps developers understand:
            1. What this codebase does (purpose and functionality)
            2. Key architecture and technology choices
            3. Main components and how they interact
            4. Notable patterns, configurations, or design decisions
            5. Overall code structure and organization
            
            Make your summary clear, technical, and actionable for developers who need to understand or work with this codebase."""
            
            # Prepare repository info for AI summary
            repository_info = {
                "repository_url": github_url,
                "statistics": {
                    "files_processed": stats["files_processed"],
                    "binary_files_skipped": stats["binary_files_skipped"], 
                    "large_files_skipped": stats["large_files_skipped"],
                    "encoding_errors": stats["encoding_errors"],
                    "total_characters": stats["total_characters"],
                    "total_lines": stats["total_lines"],
                    "total_files_found": stats["total_files"],
                    "total_directories": stats["total_directories"]
                }
            }
            
            # Generate AI summary
            summary_result = await gemini_service.generate_repository_summary(
                full_text=repo_content,
                repository_info=repository_info,
                system_prompt=system_prompt
            )
            
            if summary_result and summary_result.get("success"):
                # Mark previous summary documents as not current
                await db_service.mark_previous_documents_not_current(repo_id, "ai_summary")
                
                # Create AI summary as a document
                summary_doc_data = DocumentInsert(
                    repository_id=repo_id,
                    title="AI Summary",
                    content=summary_result["summary"],
                    document_type="ai_summary",
                    description="AI-generated repository summary",
                    version=1,
                    is_current=True,
                    generated_by="gemini-2.0-flash",
                    model_used="gemini-2.0-flash",
                    metadata={
                        "processing_stats": summary_result["processing_stats"],
                        "chunk_count": summary_result["chunks_processed"],
                        "successful_chunks": summary_result["successful_chunks"],
                        "failed_chunks": summary_result["failed_chunks"]
                    }
                )
                
                ai_summary_doc = await db_service.create_document(summary_doc_data)
                logger.info(f"AI summary document generated successfully for repo {repo_id}: {ai_summary_doc.id}")
            else:
                logger.warning(f"AI summary generation failed for repo {repo_id}: {summary_result.get('error', 'Unknown error')}")
                
        except Exception as ai_error:
            logger.error(f"AI summary generation error for repo {repo_id}: {str(ai_error)}")
            # Continue without failing the entire task
        
        # Update repository with content info
        content_preview = repo_content[:1000] + "..." if len(repo_content) > 1000 else repo_content
        repo_update_data = {
            "full_text": content_preview,
            "content_expires_at": None,
            "updated_at": datetime.utcnow()
        }
        
        await db_service.update_repository(repo_id, repo_update_data)
        
        # Prepare final result
        final_result = {
            "status": "completed",
            "repo_id": str(repo_id),
            "analysis_id": str(analysis.id),
            "repository": {
                "name": repo_info["repo_name"],
                "author": repo_info["owner"],
                "url": github_url,
                "full_name": repo_info["full_name"]
            },
            "stats": stats,
            "tree_structure": tree_structure,
            "document_id": str(document.id) if 'document' in locals() else None,
            "ai_summary_id": str(ai_summary_doc.id) if 'ai_summary_doc' in locals() else None,
            "ai_summary_success": summary_result.get("success", False) if summary_result else False,
            "output_file": output_file_path,
            "progress": 100
        }
        
        # Update task state to completion with final result
        update_task_status(task_id, TaskStatus.SUCCESS, "Analysis completed successfully", 100, 
                          repo_id=str(repo_id), result=final_result)
        
        logger.info(f"Repository analysis completed successfully for task {task_id}, repo {repo_id}")
        
    except Exception as e:
        # Log error and return failure
        error_msg = str(e)
        logger.error(f"Repository analysis failed for {github_url}: {error_msg}")
        
        # Update task state with error
        update_task_status(task_id, TaskStatus.FAILURE, "Analysis failed", error=error_msg, repo_info=repo_info)
        
    finally:
        # Cleanup temporary directories
        for temp_dir in [temp_clone_dir, temp_output_dir]:
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temp directory {temp_dir}: {cleanup_error}")

def update_task_status(task_id: str, status: str, message: str, progress: int = None, 
                      repo_id: str = None, error: str = None, repo_info: Dict = None, result: Dict = None):
    """Update task status in storage"""
    if task_id not in task_storage:
        task_storage[task_id] = {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "message": "Task created",
            "created_at": datetime.utcnow()
        }
    
    task_storage[task_id].update({
        "status": status,
        "message": message,
        "updated_at": datetime.utcnow()
    })
    
    if progress is not None:
        task_storage[task_id]["progress"] = progress
    if repo_id is not None:
        task_storage[task_id]["repo_id"] = repo_id
    if error is not None:
        task_storage[task_id]["error"] = error
    if repo_info is not None:
        task_storage[task_id]["repo_info"] = repo_info
    if result is not None:
        task_storage[task_id]["result"] = result

def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get the status of a background task"""
    try:
        if task_id not in task_storage:
            return {
                "task_id": task_id,
                "status": "not_found",
                "error": "Task not found",
                "message": "Task not found"
            }
        
        return task_storage[task_id]
        
    except Exception as e:
        return {
            "task_id": task_id,
            "status": "error",
            "error": str(e),
            "message": "Failed to get task status"
        }

def create_task(task_id: str) -> Dict[str, Any]:
    """Create a new task entry"""
    task_storage[task_id] = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "message": "Task created",
        "created_at": datetime.utcnow(),
        "progress": 0
    }
    return task_storage[task_id]