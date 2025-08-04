from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional, List
from uuid import UUID, uuid4
import logging

from app.models import (
    RepositoryAnalysisTaskRequest,
    TaskResponse,
    TaskStatusResponse,
    RepositoryAnalysisResult,
    TaskStatus,
    RepositoryResponse,
    RepositoryAnalysisResponse,
    DocumentResponse
)
from app.services.background_tasks import analyze_repository_task, get_task_status, create_task
from app.services.database import get_database_service, DatabaseService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze", response_model=TaskResponse)
async def start_repository_analysis(
    request: RepositoryAnalysisTaskRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseService = Depends(get_database_service)
):
    """Start background analysis of a GitHub repository"""
    try:
        # Validate GitHub URL format
        github_url = str(request.github_url)
        if not github_url.startswith(("https://github.com/", "http://github.com/")):
            logger.warning(f"Invalid GitHub URL format received: {github_url}")
            raise HTTPException(
                status_code=400,
                detail="Invalid GitHub URL. Must start with https://github.com/"
            )
        
        # Generate task ID and create task entry
        task_id = str(uuid4())
        create_task(task_id)
        
        logger.info(f"Created repository analysis task {task_id} for {github_url}")
        
        # Start background task
        background_tasks.add_task(
            analyze_repository_task,
            task_id,
            github_url
        )
        
        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message=f"Repository analysis started for {github_url}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to start repository analysis for {github_url}: {error_msg}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start repository analysis: {error_msg}"
        )

@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_analysis_task_status(task_id: str):
    """Get the status of a repository analysis task"""
    try:
        status_info = get_task_status(task_id)
        
        return TaskStatusResponse(
            task_id=status_info["task_id"],
            status=TaskStatus(status_info["status"]),
            message=status_info["message"],
            progress=status_info.get("progress"),
            repo_id=status_info.get("repo_id"),
            result=status_info.get("result"),
            error=status_info.get("error")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )

@router.get("/tasks/{task_id}/result")
async def get_analysis_result(
    task_id: str,
    db: DatabaseService = Depends(get_database_service)
):
    """Get the full result of a completed repository analysis task"""
    try:
        # Get task status
        status_info = get_task_status(task_id)
        
        if status_info["status"] != TaskStatus.SUCCESS:
            return TaskStatusResponse(
                task_id=status_info["task_id"],
                status=TaskStatus(status_info["status"]),
                message=status_info["message"],
                progress=status_info.get("progress"),
                error=status_info.get("error")
            )
        
        # Get detailed result
        result = status_info.get("result", {})
        repo_id = result.get("repo_id")
        
        if not repo_id:
            raise HTTPException(
                status_code=404,
                detail="Repository ID not found in task result"
            )
        
        # Get repository details
        repository = await db.get_repository(UUID(repo_id))
        if not repository:
            raise HTTPException(
                status_code=404,
                detail="Repository not found"
            )
        
        # Get analysis details
        analysis = await db.get_latest_repository_analysis(UUID(repo_id))
        
        # Get documents
        documents = await db.get_current_documents(UUID(repo_id))
        
        return {
            "task_id": task_id,
            "status": TaskStatus.SUCCESS,
            "repository": RepositoryResponse.from_orm(repository),
            "analysis": RepositoryAnalysisResponse.from_orm(analysis) if analysis else None,
            "documents": [DocumentResponse.from_orm(doc) for doc in documents],
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analysis result: {str(e)}"
        )

@router.get("/repositories/{repo_id}", response_model=RepositoryResponse)
async def get_repository(
    repo_id: UUID,
    db: DatabaseService = Depends(get_database_service)
):
    """Get repository details by ID"""
    try:
        repository = await db.get_repository(repo_id)
        
        if not repository:
            raise HTTPException(
                status_code=404,
                detail="Repository not found"
            )
        
        return RepositoryResponse.from_orm(repository)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get repository: {str(e)}"
        )

@router.get("/repositories/{repo_id}/analysis", response_model=RepositoryAnalysisResponse)
async def get_repository_analysis(
    repo_id: UUID,
    db: DatabaseService = Depends(get_database_service)
):
    """Get the latest analysis for a repository"""
    try:
        analysis = await db.get_latest_repository_analysis(repo_id)
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail="No analysis found for this repository"
            )
        
        return RepositoryAnalysisResponse.from_orm(analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get repository analysis: {str(e)}"
        )

@router.get("/repositories/{repo_id}/documents")
async def get_repository_documents(
    repo_id: UUID,
    document_type: Optional[str] = None,
    current_only: bool = False,
    db: DatabaseService = Depends(get_database_service)
):
    """Get documents for a repository"""
    try:
        if current_only:
            documents = await db.get_current_documents(repo_id)
        else:
            documents = await db.get_documents_by_repository(repo_id, document_type)
        
        return {
            "repository_id": str(repo_id),
            "documents": [DocumentResponse.from_orm(doc) for doc in documents],
            "total": len(documents)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get repository documents: {str(e)}"
        )

@router.get("/repositories")
async def list_repositories(
    skip: int = 0,
    limit: int = 10,
    db: DatabaseService = Depends(get_database_service)
):
    """List all repositories with pagination"""
    try:
        # This would need a list method in DatabaseService
        # For now, return empty list with proper structure
        return {
            "repositories": [],
            "total": 0,
            "page": skip // limit + 1 if limit > 0 else 1,
            "per_page": limit,
            "message": "Repository listing not yet implemented"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list repositories: {str(e)}"
        )

@router.delete("/repositories/{repo_id}")
async def delete_repository(
    repo_id: UUID,
    db: DatabaseService = Depends(get_database_service)
):
    """Delete a repository and all its associated data"""
    try:
        # Check if repository exists
        repository = await db.get_repository(repo_id)
        if not repository:
            raise HTTPException(
                status_code=404,
                detail="Repository not found"
            )
        
        # TODO: Implement cascade delete for repository, analysis, and documents
        # This would require additional methods in DatabaseService
        
        return {
            "message": "Repository deletion not yet implemented",
            "repository_id": str(repo_id)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete repository: {str(e)}"
        )