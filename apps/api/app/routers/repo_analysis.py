from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
import logging
import asyncio

# Import fungsi dari background_tasks
from app.services.background_tasks import (
    analyze_repository_task,
    generate_ai_summary_and_description_task,
    generate_documents_with_ai_ready_task,
    comprehensive_repository_processing_task,
    get_task_status,
    create_task,
    scrape_website_and_extract_repositories_task,
    extract_repo_info,
    upload_image_to_supabase,
)
from app.services.readme_blob_screenshot import screenshot_readme_blob_sync
from app.services.image_cropper import (
    crop_top_and_crop_to_size,
)

from app.models import (
    RepositoryAnalysisTaskRequest,
    TaskResponse,
    TaskStatusResponse,
    RepositoryAnalysisResult,
    TaskStatus,
    RepositoryResponse,
    RepositoryAnalysisResponse,
    RepositoryAnalysisInsert,
    RepositoryAnalysisUpdate,
    DocumentResponse,
    BatchProcessing,
    BatchProcessingRequest,
    BatchProcessingResponse,
    BatchProcessingInsert,
    BatchStatus,
    TwitterPostingRequest,
    TwitterPostingTaskResponse,
    TwitterPostingStatus,
    SimpleScrapeRequest,
    SimpleScrapeTaskResponse,
    SimpleScrapeResult,
    SimpleScrapeStatus,
    RepositoryProcessingStatus,
)
from app.services.database import get_database_service, DatabaseService
from app.services.document_generation import DocumentGenerationService
from app.services.auth import require_api_key
import tempfile
import os

logger = logging.getLogger(__name__)
router = APIRouter(
    dependencies=[
        Depends(require_api_key)
    ]  # Apply API key requirement to all routes in this router
)


@router.post("/analyze", response_model=TaskResponse)
async def start_repository_analysis(
    request: RepositoryAnalysisTaskRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseService = Depends(get_database_service),
):
    """Start background analysis of a GitHub repository"""
    try:
        # Validate GitHub URL format
        github_url = str(request.github_url)
        if not github_url.startswith(("https://github.com/", "http://github.com/")):
            logger.warning(f"Invalid GitHub URL format received: {github_url}")
            raise HTTPException(
                status_code=400,
                detail="Invalid GitHub URL. Must start with https://github.com/",
            )

        # Generate task ID and create task entry
        task_id = str(uuid4())
        create_task(task_id)

        logger.info(f"Created repository analysis task {task_id} for {github_url}")

        # Start background task
        background_tasks.add_task(analyze_repository_task, task_id, github_url)

        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            message=f"Repository analysis started for {github_url}",
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(
            f"Failed to start repository analysis for {github_url}: {error_msg}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to start repository analysis: {error_msg}"
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
            error=status_info.get("error"),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get task status: {str(e)}"
        )


@router.get("/tasks/{task_id}/result")
async def get_analysis_result(
    task_id: str, db: DatabaseService = Depends(get_database_service)
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
                error=status_info.get("error"),
                repo_id=status_info.get("repo_id"),
                result=status_info.get("result"),
            )

        # Get detailed result
        result = status_info.get("result", {})
        repo_id = result.get("repo_id")

        if not repo_id:
            raise HTTPException(
                status_code=404, detail="Repository ID not found in task result"
            )

        # Get repository details
        repository = await db.get_repository(UUID(repo_id))
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Get analysis details
        analysis = await db.get_latest_repository_analysis(UUID(repo_id))

        # Get documents
        documents = await db.get_current_documents(UUID(repo_id))

        return {
            "task_id": task_id,
            "status": TaskStatus.SUCCESS,
            "repository": RepositoryResponse.from_orm(repository),
            "analysis": (
                RepositoryAnalysisResponse.from_orm(analysis) if analysis else None
            ),
            "documents": [DocumentResponse.from_orm(doc) for doc in documents],
            "result": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get analysis result: {str(e)}"
        )


@router.get("/repositories/{repo_id}", response_model=RepositoryResponse)
async def get_repository(
    repo_id: UUID, db: DatabaseService = Depends(get_database_service)
):
    """Get repository details by ID"""
    try:
        repository = await db.get_repository(repo_id)

        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        return RepositoryResponse.from_orm(repository)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get repository: {str(e)}"
        )


@router.get(
    "/repositories/{repo_id}/analysis", response_model=RepositoryAnalysisResponse
)
async def get_repository_analysis(
    repo_id: UUID, db: DatabaseService = Depends(get_database_service)
):
    """Get the latest analysis for a repository"""
    try:
        analysis = await db.get_latest_repository_analysis(repo_id)

        if not analysis:
            raise HTTPException(
                status_code=404, detail="No analysis found for this repository"
            )

        return RepositoryAnalysisResponse.from_orm(analysis)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get repository analysis: {str(e)}"
        )


@router.get("/repositories/{repo_id}/documents")
async def get_repository_documents(
    repo_id: UUID,
    document_type: Optional[str] = None,
    current_only: bool = False,
    db: DatabaseService = Depends(get_database_service),
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
            "total": len(documents),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get repository documents: {str(e)}"
        )


@router.get("/repositories")
async def list_repositories(
    skip: int = 0,
    limit: int = 10,
    author: Optional[str] = None,
    db: DatabaseService = Depends(get_database_service),
):
    """List all repositories with pagination"""
    try:
        repositories, total = await db.list_repositories(skip, limit, author)

        return {
            "repositories": [
                RepositoryResponse.from_orm(repo) for repo in repositories
            ],
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "per_page": limit,
            "has_more": skip + limit < total,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list repositories: {str(e)}"
        )


@router.delete("/repositories/{repo_id}")
async def delete_repository(
    repo_id: UUID, db: DatabaseService = Depends(get_database_service)
):
    """Delete a repository and all its associated data"""
    try:
        # Check if repository exists
        repository = await db.get_repository(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Delete repository (cascades to analysis and documents via foreign key constraints)
        deleted = await db.delete_repository(repo_id)

        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete repository")

        return {
            "message": f"Repository '{repository.name}' and all associated data deleted successfully",
            "repository_id": str(repo_id),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete repository: {str(e)}"
        )


# Repository Analysis CRUD endpoints


@router.post(
    "/repositories/{repo_id}/analysis", response_model=RepositoryAnalysisResponse
)
async def create_repository_analysis(
    repo_id: UUID,
    analysis_data: RepositoryAnalysisInsert,
    db: DatabaseService = Depends(get_database_service),
):
    """Create a new repository analysis"""
    try:
        # Verify repository exists
        repository = await db.get_repository(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Set repository_id from URL parameter
        analysis_data.repository_id = repo_id

        # Create analysis
        analysis = await db.create_repository_analysis(analysis_data)

        return RepositoryAnalysisResponse.from_orm(analysis)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create repository analysis: {str(e)}"
        )


@router.get("/repositories/{repo_id}/analyses")
async def list_repository_analyses(
    repo_id: UUID,
    skip: int = 0,
    limit: int = 10,
    db: DatabaseService = Depends(get_database_service),
):
    """List all analyses for a repository with pagination"""
    try:
        # Verify repository exists
        repository = await db.get_repository(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        analyses, total = await db.list_repository_analyses(repo_id, skip, limit)

        return {
            "repository_id": str(repo_id),
            "analyses": [
                RepositoryAnalysisResponse.from_orm(analysis) for analysis in analyses
            ],
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "per_page": limit,
            "has_more": skip + limit < total,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list repository analyses: {str(e)}"
        )


@router.get("/analysis/{analysis_id}", response_model=RepositoryAnalysisResponse)
async def get_analysis_by_id(
    analysis_id: UUID, db: DatabaseService = Depends(get_database_service)
):
    """Get repository analysis by ID"""
    try:
        analysis = await db.get_repository_analysis(analysis_id)

        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return RepositoryAnalysisResponse.from_orm(analysis)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analysis: {str(e)}")


@router.put("/analysis/{analysis_id}", response_model=RepositoryAnalysisResponse)
async def update_repository_analysis(
    analysis_id: UUID,
    update_data: RepositoryAnalysisUpdate,
    db: DatabaseService = Depends(get_database_service),
):
    """Update repository analysis"""
    try:
        # Check if analysis exists
        existing_analysis = await db.get_repository_analysis(analysis_id)
        if not existing_analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Update analysis
        updated_analysis = await db.update_repository_analysis(analysis_id, update_data)

        if not updated_analysis:
            raise HTTPException(status_code=500, detail="Failed to update analysis")

        return RepositoryAnalysisResponse.from_orm(updated_analysis)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update repository analysis: {str(e)}"
        )


@router.delete("/analysis/{analysis_id}")
async def delete_repository_analysis(
    analysis_id: UUID, db: DatabaseService = Depends(get_database_service)
):
    """Delete repository analysis"""
    try:
        # Check if analysis exists
        analysis = await db.get_repository_analysis(analysis_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        # Delete analysis
        deleted = await db.delete_repository_analysis(analysis_id)

        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete analysis")

        return {
            "message": f"Analysis {analysis_id} deleted successfully",
            "analysis_id": str(analysis_id),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete repository analysis: {str(e)}"
        )


# Statistics endpoints


@router.get("/statistics")
async def get_global_statistics(db: DatabaseService = Depends(get_database_service)):
    """Get global repository and analysis statistics"""
    try:
        stats = await db.get_repository_statistics()
        return stats

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get global statistics: {str(e)}"
        )


@router.get("/repositories/{repo_id}/statistics")
async def get_repository_statistics(
    repo_id: UUID, db: DatabaseService = Depends(get_database_service)
):
    """Get statistics for a specific repository"""
    try:
        # Verify repository exists
        repository = await db.get_repository(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        stats = await db.get_repository_statistics(repo_id)
        return stats

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get repository statistics: {str(e)}"
        )


# Batch processing endpoints


@router.post("/batch/process", response_model=BatchProcessingResponse)
async def start_batch_processing(
    request: BatchProcessingRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseService = Depends(get_database_service),
):
    """Start batch processing of repositories that need analysis/docs/AI summary/description"""
    try:
        # Find repositories that need processing based on request type
        repositories = []

        if request.process_type == "analysis_only":
            repositories = await db.get_repositories_without_analysis(
                request.max_repositories
            )
        elif request.process_type == "docs_only":
            repositories = await db.get_repositories_without_documents(
                request.max_repositories
            )
        elif request.process_type == "ai_summary_and_description":
            # New process type: repositories with analysis but missing AI summary or description
            repositories = await db.get_repositories_needing_ai_summary_or_description(
                request.max_repositories
            )
        elif request.process_type == "docs_with_ai_ready":
            # New process type: repositories with AI summary and description but missing documents
            repositories = await db.get_repositories_needing_documents_with_ai_ready(
                request.max_repositories
            )
        elif request.process_type == "orphaned_documents":
            # New process type: repositories with orphaned/incomplete documents that need regeneration
            repositories = await db.get_repositories_with_orphaned_documents(
                request.max_repositories
            )
        else:  # "analysis_and_docs" (default)
            repositories = await db.get_repositories_needing_processing(
                request.max_repositories
            )

        if not repositories:
            raise HTTPException(
                status_code=404,
                detail=f"No repositories found that need {request.process_type}",
            )

        # Generate batch name if not provided
        batch_name = (
            request.batch_name
            or f"Batch {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Create a mock batch processing entry (in-memory only)
        mock_batch = BatchProcessing(
            id=uuid4(),
            batch_name=batch_name,
            total_repositories=len(repositories),
            processed_repositories=0,
            successful_repositories=0,
            failed_repositories=0,
            status=BatchStatus.PENDING,
            repository_ids=[str(repo.id) for repo in repositories],
            task_ids=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        logger.info(f"Created batch processing for {len(repositories)} repositories")

        # Create tasks for each repository
        task_ids = []
        for repo in repositories:
            # Generate task ID and create task entry
            task_id = str(uuid4())
            create_task(task_id)
            task_ids.append(task_id)

            # Start appropriate background task based on process type
            if request.process_type == "analysis_only":
                # Pure repository analysis only
                background_tasks.add_task(analyze_repository_task, task_id, repo.repo_url)
            elif request.process_type == "ai_summary_and_description":
                background_tasks.add_task(
                    generate_ai_summary_and_description_task, task_id, repo.repo_url
                )
            elif request.process_type == "docs_with_ai_ready":
                background_tasks.add_task(
                    generate_documents_with_ai_ready_task, task_id, repo.repo_url
                )
            elif request.process_type == "docs_only":
                # Only generate documents (assuming AI summary/description exist)
                background_tasks.add_task(
                    generate_documents_with_ai_ready_task, task_id, repo.repo_url
                )
            elif request.process_type == "orphaned_documents":
                # Regenerate analysis for repositories with orphaned/incomplete documents
                background_tasks.add_task(analyze_repository_task, task_id, repo.repo_url)
            else:
                # Default "analysis_and_docs": comprehensive processing that determines what's needed
                background_tasks.add_task(
                    comprehensive_repository_processing_task, task_id, repo.repo_url
                )

        logger.info(f"Started {len(task_ids)} repository analysis tasks")

        # Update mock batch with task IDs
        mock_batch.task_ids = task_ids
        mock_batch.status = BatchStatus.PROCESSING
        mock_batch.updated_at = datetime.now()

        return BatchProcessingResponse.from_orm(mock_batch)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to start batch processing: {error_msg}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start batch processing: {error_msg}"
        )


@router.get("/batch/status/{batch_id}", response_model=BatchProcessingResponse)
async def get_batch_status(
    batch_id: UUID, db: DatabaseService = Depends(get_database_service)
):
    """Get the status of a batch processing job"""
    try:
        # Since there's no batch_processing table, we'll return a mock response
        mock_batch = BatchProcessing(
            id=batch_id,
            batch_name="Mock Batch",
            total_repositories=0,
            processed_repositories=0,
            successful_repositories=0,
            failed_repositories=0,
            status=BatchStatus.COMPLETED,
            repository_ids=[],
            task_ids=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        return BatchProcessingResponse.from_orm(mock_batch)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get batch status: {str(e)}"
        )


@router.get("/batch/list")
async def list_batch_processing(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    db: DatabaseService = Depends(get_database_service),
):
    """List batch processing jobs with pagination"""
    try:
        # Since there's no batch_processing table, we'll return an empty list
        return {
            "batches": [],
            "total": 0,
            "page": skip // limit + 1 if limit > 0 else 1,
            "per_page": limit,
            "has_more": False,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list batch processing jobs: {str(e)}"
        )


@router.get("/repositories/needs-processing")
async def get_repositories_needing_processing(
    limit: int = 50,
    process_type: str = "analysis_and_docs",
    db: DatabaseService = Depends(get_database_service),
):
    """Get repositories that need processing (analysis, AI summary, description, or documents)"""
    try:
        repositories = []

        if process_type == "analysis_only":
            repositories = await db.get_repositories_without_analysis(limit)
        elif process_type == "docs_only":
            repositories = await db.get_repositories_without_documents(limit)
        elif process_type == "ai_summary_and_description":
            repositories = await db.get_repositories_needing_ai_summary_or_description(
                limit
            )
        elif process_type == "docs_with_ai_ready":
            repositories = await db.get_repositories_needing_documents_with_ai_ready(
                limit
            )
        elif process_type == "orphaned_documents":
            repositories = await db.get_repositories_with_orphaned_documents(limit)
        else:  # "analysis_and_docs" (default)
            repositories = await db.get_repositories_needing_processing(limit)

        return {
            "repositories": [
                RepositoryResponse.from_orm(repo) for repo in repositories
            ],
            "total": len(repositories),
            "process_type": process_type,
            "message": f"Found {len(repositories)} repositories needing {process_type}",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get repositories needing processing: {str(e)}",
        )


# Website Scraping Endpoints (saves directly to repositories table)
@router.post("/scrape/website", response_model=SimpleScrapeTaskResponse)
async def scrape_website_for_repositories(
    request: SimpleScrapeRequest,
    background_tasks: BackgroundTasks,
    db: DatabaseService = Depends(get_database_service),
):
    """Scrape a website and extract repository URLs (saves directly to repositories table)"""
    try:
        website_url = str(request.website_url)
        logger.info(f"Starting simple website scraping for {website_url}")

        # Generate task ID
        task_id = str(uuid4())

        # Start website scraping background task
        background_tasks.add_task(
            scrape_website_and_extract_repositories_task,
            task_id,
            website_url,
            request.scraping_type,
            request.max_pages,
            request.auto_save,
        )

        logger.info(f"Started scraping task {task_id} for {website_url}")

        return SimpleScrapeTaskResponse(
            task_id=task_id,
            status=SimpleScrapeStatus.PENDING,
            message=f"Website scraping started for {website_url}",
            website_url=website_url,
        )

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to start website scraping for {website_url}: {error_msg}")
        raise HTTPException(
            status_code=500, detail=f"Failed to start website scraping: {error_msg}"
        )


@router.get("/scrape/status/{task_id}", response_model=SimpleScrapeResult)
async def get_scraping_task_status(task_id: str):
    """Get the status of a website scraping task"""
    try:
        # Import task_storage from background_tasks
        from app.services.background_tasks import task_storage

        if task_id not in task_storage:
            raise HTTPException(status_code=404, detail="Scraping task not found")

        task_data = task_storage[task_id]

        return SimpleScrapeResult(
            task_id=task_data["task_id"],
            status=task_data["status"],
            website_url=task_data["website_url"],
            repositories_found=task_data["repositories_found"],
            repositories_saved=task_data["repositories_saved"],
            extracted_repositories=task_data["extracted_repositories"],
            error_message=task_data.get("error_message"),
            started_at=task_data.get("started_at"),
            completed_at=task_data.get("completed_at"),
            processing_time_seconds=task_data.get("processing_time_seconds"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get scraping task status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get scraping task status: {str(e)}"
        )


# Twitter Posting Endpoints
@router.post("/twitter/post")
async def post_repository_tweets(
    request: TwitterPostingRequest,
    db: DatabaseService = Depends(get_database_service),
):
    """Post tweets for repositories without Twitter links (synchronous)"""
    try:
        # Import Twitter service
        from app.services.twitter_service import twitter_service

        # Generate posting ID for tracking
        posting_id = str(uuid4())

        logger.info(f"🚀 Starting synchronous Twitter posting {posting_id}")
        logger.info(
            f"📊 Parameters: max={request.max_repositories}, delay={request.delay_between_posts}s, analysis={request.include_analysis}, media={request.include_media}"
        )

        # Check if Twitter service is configured
        logger.info("🔧 Checking Twitter service configuration...")
        if not twitter_service.is_configured():
            error_msg = "Twitter service is not configured"
            logger.error(f"❌ {error_msg}")

            # Run detailed credential validation
            logger.info("🔍 Running detailed credential validation...")
            validation_results = twitter_service.validate_credentials()

            logger.info("📋 Credential validation results:")
            logger.info(
                f"   Credentials present: {'✅' if validation_results['credentials_present'] else '❌'}"
            )
            logger.info(
                f"   Bearer token valid: {'✅' if validation_results['bearer_token_valid'] else '❌'}"
            )
            logger.info(
                f"   OAuth tokens valid: {'✅' if validation_results['oauth_tokens_valid'] else '❌'}"
            )

            if validation_results["user_info"]:
                user_info = validation_results["user_info"]
                logger.info(
                    f"   User info: @{user_info['username']} ({user_info['name']})"
                )

            if validation_results["errors"]:
                logger.error("🚨 Credential errors:")
                for error in validation_results["errors"]:
                    logger.error(f"   - {error}")

            raise HTTPException(
                status_code=401,
                detail=f"{error_msg} - check logs for detailed validation results",
            )

        logger.info("✅ Twitter service is properly configured")

        # Get repositories without Twitter links
        logger.info(
            f"🔍 Searching for repositories without Twitter links (limit: {request.max_repositories})..."
        )
        repositories = await db.get_repositories_without_twitter_links(
            limit=request.max_repositories
        )

        if not repositories:
            logger.warning("⚠️ No repositories found without Twitter links")
            raise HTTPException(
                status_code=404, detail="No repositories found without Twitter links"
            )

        logger.info(f"📋 Found {len(repositories)} repositories to process:")
        for i, repo in enumerate(repositories, 1):
            logger.info(f"  {i}. {repo.name} by {repo.author} - {repo.repo_url}")

        # Initialize results
        results = {
            "posting_id": posting_id,
            "total_repositories": len(repositories),
            "processed": 0,
            "successful_posts": 0,
            "failed_posts": 0,
            "rate_limited_posts": 0,
            "posted_tweets": [],
            "errors": [],
        }

        # Process each repository synchronously
        for i, repository in enumerate(repositories):
            try:
                logger.info(
                    f"📝 [{i+1}/{len(repositories)}] Processing repository: {repository.name}"
                )

                # Prepare repository info for tweet
                repo_info = {
                    "id": str(repository.id),
                    "name": repository.name,
                    "author": repository.author,
                    "repo_url": repository.repo_url,
                    "description": (
                        f"Repository by {repository.author}"
                        if repository.author
                        else "GitHub repository"
                    ),
                }

                # If include_analysis is True, try to get repository analysis
                if request.include_analysis:
                    logger.info(
                        "   🔬 Fetching repository analysis for enhanced description..."
                    )
                    try:
                        analysis = await db.get_latest_repository_analysis(
                            repository.id
                        )
                        if analysis:
                            # First try to use existing description (short description)
                            if (
                                hasattr(analysis, "description")
                                and analysis.description
                            ):
                                repo_info["description"] = analysis.description
                                logger.info(
                                    f"   ✅ Using existing description ({len(analysis.description)} chars)"
                                )
                            # If no short description but we have ai_summary, generate one
                            elif (
                                hasattr(analysis, "ai_summary") and analysis.ai_summary
                            ):
                                logger.info(
                                    "   🤖 Generating short description from AI summary..."
                                )
                                try:
                                    from app.services.gemini_ai import gemini_service

                                    repo_context = {
                                        "name": repository.name,
                                        "author": repository.author,
                                        "repository_url": repository.repo_url,
                                    }

                                    short_desc_result = (
                                        await gemini_service.generate_short_description(
                                            summary=analysis.ai_summary,
                                            repository_info=repo_context,
                                            max_length=150,
                                        )
                                    )

                                    if short_desc_result["success"]:
                                        repo_info["description"] = short_desc_result[
                                            "short_description"
                                        ]
                                        # Save the generated short description
                                        try:
                                            await db.update_repository_analysis(
                                                analysis.id,
                                                {
                                                    "description": short_desc_result[
                                                        "short_description"
                                                    ]
                                                },
                                            )
                                            logger.info(
                                                f"   ✅ Generated and saved description ({short_desc_result['length']} chars)"
                                            )
                                        except Exception:
                                            logger.info(
                                                f"   ✅ Generated description ({short_desc_result['length']} chars) - could not save"
                                            )
                                    else:
                                        logger.warning(
                                            f"   ⚠️ Failed to generate short description: {short_desc_result.get('error')}"
                                        )
                                        # Fallback to truncated summary
                                        if (
                                            hasattr(analysis, "summary")
                                            and analysis.summary
                                        ):
                                            repo_info["description"] = (
                                                analysis.summary[:150] + "..."
                                                if len(analysis.summary) > 150
                                                else analysis.summary
                                            )
                                except Exception as gen_error:
                                    logger.warning(
                                        f"   ⚠️ Error generating short description: {str(gen_error)}"
                                    )
                            # Fallback to regular summary if available
                            elif hasattr(analysis, "summary") and analysis.summary:
                                repo_info["description"] = (
                                    analysis.summary[:150] + "..."
                                    if len(analysis.summary) > 150
                                    else analysis.summary
                                )
                                logger.info(f"   ✅ Using truncated summary")
                            else:
                                logger.info("   ℹ️ No summary or AI summary available")
                        else:
                            logger.info("   ℹ️ No analysis available")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Could not get analysis: {str(e)}")

                # If include_media is True, try to get README image URL
                if request.include_media:
                    logger.info("   🖼️ Fetching README image for media attachment...")
                    try:
                        analysis = await db.get_latest_repository_analysis(
                            repository.id
                        )
                        if analysis and analysis.readme_image_src:
                            repo_info["readme_image_url"] = analysis.readme_image_src
                            logger.info(
                                f"   ✅ Found README image: {analysis.readme_image_src}"
                            )
                        else:
                            error_msg = f"README image required but not found for repository {repository.name}"
                            logger.error(f"   ❌ {error_msg}")
                            results["errors"].append(
                                {"repository": repository.name, "error": error_msg}
                            )
                            results["failed_posts"] += 1
                            results["processed"] += 1
                            continue  # Skip this repository
                    except Exception as e:
                        error_msg = f"Could not get README image for repository {repository.name}: {str(e)}"
                        logger.error(f"   ❌ {error_msg}")
                        results["errors"].append(
                            {"repository": repository.name, "error": error_msg}
                        )
                        results["failed_posts"] += 1
                        results["processed"] += 1
                        continue  # Skip this repository

                # Post tweet
                logger.info(f"   🐦 Posting tweet to Twitter...")
                result = await twitter_service.post_repository_tweet(
                    repo_info, request.include_media
                )

                # Log the complete Twitter response
                logger.info(f"   📋 Twitter API Response:")
                logger.info(f"      Success: {result.get('success', 'Unknown')}")
                logger.info(f"      Tweet ID: {result.get('tweet_id', 'None')}")
                logger.info(f"      Tweet URL: {result.get('tweet_url', 'None')}")
                logger.info(
                    f"      Media Included: {result.get('included_media', False)}"
                )
                logger.info(f"      Media IDs: {result.get('media_ids', 'None')}")
                logger.info(
                    f"      Repository ID: {result.get('repository_id', 'None')}"
                )
                logger.info(
                    f"      Repository Name: {result.get('repository_name', 'None')}"
                )
                if result.get("error"):
                    logger.info(f"      Error: {result['error']}")
                if result.get("tweet_text"):
                    logger.info(f"      Tweet Text: {result['tweet_text'][:100]}...")

                if result["success"]:
                    # Update repository analysis with Twitter link (moved from repositories table)
                    logger.info(
                        f"   📝 Updating repository analysis with Twitter link..."
                    )
                    try:
                        # Get the latest analysis for this repository
                        analysis = await db.get_latest_repository_analysis(
                            repository.id
                        )
                        if analysis:
                            # Update the analysis with Twitter link
                            await db.update_repository_analysis(
                                analysis.id, {"twitter_link": result["tweet_url"]}
                            )
                            logger.info(
                                f"   ✅ Updated analysis {analysis.id} with Twitter link"
                            )
                        else:
                            logger.warning(
                                f"   ⚠️ No analysis found for repository {repository.name} to update with Twitter link"
                            )
                    except Exception as update_error:
                        logger.error(
                            f"   ❌ Failed to update analysis with Twitter link: {str(update_error)}"
                        )

                    logger.info(
                        f"   ✅ Tweet posted successfully! URL: {result['tweet_url']}"
                    )
                    if result.get("included_media"):
                        logger.info("   🖼️ Tweet includes media attachment")

                    results["successful_posts"] += 1
                    results["posted_tweets"].append(
                        {
                            "repository": repository.name,
                            "tweet_url": result["tweet_url"],
                            "tweet_id": result.get("tweet_id"),
                            "included_media": result.get("included_media", False),
                        }
                    )
                else:
                    error_msg = result.get("error", "Unknown error")
                    logger.error(f"   ❌ Failed to post tweet: {error_msg}")

                    if "rate limit" in error_msg.lower():
                        results["rate_limited_posts"] += 1

                    results["failed_posts"] += 1
                    results["errors"].append(
                        {"repository": repository.name, "error": error_msg}
                    )

                results["processed"] += 1

                # Log progress
                success_rate = (
                    (results["successful_posts"] / results["processed"] * 100)
                    if results["processed"] > 0
                    else 0
                )
                logger.info(
                    f"📊 Progress: {results['processed']}/{len(repositories)} | ✅ {results['successful_posts']} | ❌ {results['failed_posts']} | {success_rate:.1f}%"
                )

                # Delay between posts (except for the last one)
                if i < len(repositories) - 1:
                    logger.info(
                        f"   ⏳ Waiting {request.delay_between_posts} seconds..."
                    )
                    await asyncio.sleep(request.delay_between_posts)

            except Exception as e:
                error_msg = str(e)
                logger.error(
                    f"   💥 Exception while processing {repository.name}: {error_msg}"
                )
                results["failed_posts"] += 1
                results["processed"] += 1
                results["errors"].append(
                    {"repository": repository.name, "error": error_msg}
                )

        # Log final results
        logger.info("🏁 " + "=" * 60)
        logger.info(f"🏁 Twitter posting completed!")
        logger.info(f"📊 Final Results:")
        logger.info(f"   📋 Total repositories: {len(repositories)}")
        logger.info(f"   ✅ Successful posts: {results['successful_posts']}")
        logger.info(f"   ❌ Failed posts: {results['failed_posts']}")
        logger.info(f"   🚫 Rate limited posts: {results['rate_limited_posts']}")
        logger.info(
            f"   📈 Success rate: {(results['successful_posts']/len(repositories)*100):.1f}%"
        )
        logger.info("🏁 " + "=" * 60)

        return {
            "status": "completed",
            "posting_id": posting_id,
            "summary": {
                "total_repositories": results["total_repositories"],
                "processed": results["processed"],
                "successful_posts": results["successful_posts"],
                "failed_posts": results["failed_posts"],
                "rate_limited_posts": results["rate_limited_posts"],
                "success_rate": f"{(results['successful_posts']/len(repositories)*100):.1f}%",
            },
            "posted_tweets": results["posted_tweets"],
            "errors": results["errors"],
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Failed to post Twitter tweets: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to post Twitter tweets: {str(e)}"
        )


@router.get("/twitter/post/{posting_id}")
async def get_twitter_posting_status(posting_id: UUID):
    """Get Twitter posting job status (mock response since no database table)"""
    try:
        # Since there's no Twitter posting table, return a mock response
        return {
            "id": posting_id,
            "job_name": "Mock Twitter Posting Job",
            "total_repositories": 0,
            "processed_repositories": 0,
            "successful_posts": 0,
            "failed_posts": 0,
            "rate_limited_posts": 0,
            "status": "completed",
            "repository_ids": [],
            "posted_tweet_urls": [],
            "error_message": None,
            "started_at": None,
            "completed_at": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "metadata": None,
            "message": "Twitter posting table does not exist - this is a mock response",
        }

    except Exception as e:
        logger.error(f"Failed to get Twitter posting status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get Twitter posting status: {str(e)}"
        )


@router.get("/twitter/post")
async def list_twitter_posting_jobs(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    db: DatabaseService = Depends(get_database_service),
):
    """List Twitter posting jobs with pagination"""
    try:
        # This would need a list method in DatabaseService for Twitter posting
        # For now, return a basic structure
        return {
            "posting_jobs": [],
            "total": 0,
            "page": skip // limit + 1 if limit > 0 else 1,
            "per_page": limit,
            "has_more": False,
            "message": "Twitter posting listing not yet implemented",
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list Twitter posting jobs: {str(e)}"
        )


@router.get("/repositories/without-twitter")
async def get_repositories_without_twitter_links(
    limit: int = 10, db: DatabaseService = Depends(get_database_service)
):
    """Get repositories that don't have Twitter links"""
    try:
        repositories = await db.get_repositories_without_twitter_links(limit=limit)

        return {
            "repositories": [
                {
                    "id": str(repo.id),
                    "name": repo.name,
                    "author": repo.author,
                    "repo_url": repo.repo_url,
                    "created_at": repo.created_at,
                    "updated_at": repo.updated_at,
                }
                for repo in repositories
            ],
            "count": len(repositories),
            "limit": limit,
        }

    except Exception as e:
        logger.error(f"Failed to get repositories without Twitter links: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get repositories without Twitter links: {str(e)}",
        )


@router.get("/twitter/validate-credentials")
async def validate_twitter_credentials():
    """Validate Twitter API credentials for debugging"""
    try:
        from app.services.twitter_service import twitter_service

        logger.info("🔍 Validating Twitter credentials...")
        validation_results = twitter_service.validate_credentials()

        return {
            "credentials_present": validation_results["credentials_present"],
            "bearer_token_valid": validation_results["bearer_token_valid"],
            "oauth_tokens_valid": validation_results["oauth_tokens_valid"],
            "user_info": validation_results["user_info"],
            "errors": validation_results["errors"],
            "is_configured": twitter_service.is_configured(),
            "message": "Check logs for detailed validation information",
        }

    except Exception as e:
        logger.error(f"Failed to validate Twitter credentials: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to validate credentials: {str(e)}"
        )


# AI Generation Endpoints
@router.post("/repositories/{repo_id}/generate-short-description")
async def generate_repository_short_description(
    repo_id: UUID,
    max_length: int = 150,
    db: DatabaseService = Depends(get_database_service),
):
    """Generate a short description from repository analysis summary using Gemini 2.5 Pro"""
    try:
        # Verify repository exists
        repository = await db.get_repository(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Get repository analysis with summary
        analysis = await db.get_latest_repository_analysis(repo_id)
        if not analysis or not analysis.ai_summary:
            raise HTTPException(
                status_code=404,
                detail="No AI summary found for this repository - run analysis first",
            )

        logger.info(f"Generating short description for repository {repository.name}")

        # Import Gemini service
        from app.services.gemini_ai import gemini_service

        # Prepare repository info for context
        repository_info = {
            "name": repository.name,
            "author": repository.author,
            "repository_url": repository.repo_url,
        }

        # Generate short description
        result = await gemini_service.generate_short_description(
            summary=analysis.ai_summary,
            repository_info=repository_info,
            max_length=max_length,
        )

        if result["success"]:
            # Update the analysis with the short description
            try:
                await db.update_repository_analysis(
                    analysis.id, {"description": result["short_description"]}
                )
                logger.info(f"Updated analysis {analysis.id} with description")
            except Exception as update_error:
                logger.error(
                    f"Failed to save description to analysis: {str(update_error)}"
                )
                # Continue without failing the request

            return {
                "repository_id": str(repo_id),
                "repository_name": repository.name,
                "analysis_id": str(analysis.id),
                "short_description": result["short_description"],
                "length": result["length"],
                "max_length": max_length,
                "model_used": result["model_used"],
                "original_summary_length": result["original_summary_length"],
                "message": "Short description generated successfully",
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate short description: {result.get('error', 'Unknown error')}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to generate short description for repository {repo_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to generate short description: {str(e)}"
        )


# Document Generation Endpoints
@router.post("/repositories/{repo_id}/generate-documents")
async def generate_repository_documents(
    repo_id: UUID,
    document_types: List[str] = DocumentGenerationService.DEFAULT_DOCUMENT_TYPES,
    db: DatabaseService = Depends(get_database_service),
):
    """Generate multiple documents for a repository"""
    try:
        # Verify repository exists
        repository = await db.get_repository(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Get repository analysis
        analysis = await db.get_latest_repository_analysis(repo_id)

        # Get repository content
        documents = await db.get_documents_by_repository(repo_id, "repository_analysis")
        if not documents:
            raise HTTPException(
                status_code=404, detail="Repository analysis content not found"
            )

        repository_content = documents[0].content
        repository_info = {
            "repository_url": repository.repo_url,
            "name": repository.name,
            "author": repository.author,
            "statistics": (
                {
                    "files_processed": analysis.files_processed if analysis else 0,
                    "binary_files_skipped": (
                        analysis.binary_files_skipped if analysis else 0
                    ),
                    "large_files_skipped": (
                        analysis.large_files_skipped if analysis else 0
                    ),
                    "encoding_errors": analysis.encoding_errors if analysis else 0,
                    "total_characters": analysis.total_characters if analysis else 0,
                    "total_lines": analysis.total_lines if analysis else 0,
                    "total_files_found": analysis.total_files_found if analysis else 0,
                    "total_directories": analysis.total_directories if analysis else 0,
                }
                if analysis
                else {}
            ),
        }

        analysis_data = (
            {
                "tree_structure": analysis.tree_structure if analysis else None,
                "stats": (
                    {
                        "files_processed": analysis.files_processed if analysis else 0,
                        "binary_files_skipped": (
                            analysis.binary_files_skipped if analysis else 0
                        ),
                        "large_files_skipped": (
                            analysis.large_files_skipped if analysis else 0
                        ),
                        "encoding_errors": analysis.encoding_errors if analysis else 0,
                        "total_characters": (
                            analysis.total_characters if analysis else 0
                        ),
                        "total_lines": analysis.total_lines if analysis else 0,
                        "total_files_found": (
                            analysis.total_files_found if analysis else 0
                        ),
                        "total_directories": (
                            analysis.total_directories if analysis else 0
                        ),
                    }
                    if analysis
                    else {}
                ),
            }
            if analysis
            else None
        )

        # Generate documents using the document generation service
        from app.services.document_generation import document_generation_service

        document_results = (
            await document_generation_service.generate_multiple_documents(
                repository_id=repo_id,
                document_types=document_types,
                repository_content=repository_content,
                repository_info=repository_info,
                analysis_data=analysis_data,
            )
        )

        success_count = sum(1 for doc in document_results.values() if doc is not None)
        failure_count = len(document_results) - success_count

        return {
            "message": f"Document generation completed: {success_count} successful, {failure_count} failed",
            "repository_id": str(repo_id),
            "requested_documents": document_types,
            "generated_documents": {
                doc_type: str(doc.id) if doc else None
                for doc_type, doc in document_results.items()
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate documents for repository {repo_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate documents: {str(e)}"
        )


@router.post("/repositories/{repo_id}/generate-document/{document_type}")
async def generate_single_repository_document(
    repo_id: UUID,
    document_type: str,
    db: DatabaseService = Depends(get_database_service),
):
    """Generate a single document type for a repository"""
    try:
        # Verify repository exists
        repository = await db.get_repository(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Get repository analysis
        analysis = await db.get_latest_repository_analysis(repo_id)

        # Get repository content
        documents = await db.get_documents_by_repository(repo_id, "repository_analysis")
        if not documents:
            raise HTTPException(
                status_code=404, detail="Repository analysis content not found"
            )

        repository_content = documents[0].content
        repository_info = {
            "repository_url": repository.repo_url,
            "name": repository.name,
            "author": repository.author,
            "statistics": (
                {
                    "files_processed": analysis.files_processed if analysis else 0,
                    "binary_files_skipped": (
                        analysis.binary_files_skipped if analysis else 0
                    ),
                    "large_files_skipped": (
                        analysis.large_files_skipped if analysis else 0
                    ),
                    "encoding_errors": analysis.encoding_errors if analysis else 0,
                    "total_characters": analysis.total_characters if analysis else 0,
                    "total_lines": analysis.total_lines if analysis else 0,
                    "total_files_found": analysis.total_files_found if analysis else 0,
                    "total_directories": analysis.total_directories if analysis else 0,
                }
                if analysis
                else {}
            ),
        }

        analysis_data = (
            {
                "tree_structure": analysis.tree_structure if analysis else None,
                "stats": (
                    {
                        "files_processed": analysis.files_processed if analysis else 0,
                        "binary_files_skipped": (
                            analysis.binary_files_skipped if analysis else 0
                        ),
                        "large_files_skipped": (
                            analysis.large_files_skipped if analysis else 0
                        ),
                        "encoding_errors": analysis.encoding_errors if analysis else 0,
                        "total_characters": (
                            analysis.total_characters if analysis else 0
                        ),
                        "total_lines": analysis.total_lines if analysis else 0,
                        "total_files_found": (
                            analysis.total_files_found if analysis else 0
                        ),
                        "total_directories": (
                            analysis.total_directories if analysis else 0
                        ),
                    }
                    if analysis
                    else {}
                ),
            }
            if analysis
            else None
        )

        # Generate document using the document generation service
        from app.services.document_generation import document_generation_service

        document = await document_generation_service.generate_document(
            repository_id=repo_id,
            document_type=document_type,
            repository_content=repository_content,
            repository_info=repository_info,
            analysis_data=analysis_data,
        )

        if document:
            return {
                "message": f"Document '{document_type}' generated successfully",
                "repository_id": str(repo_id),
                "document_id": str(document.id),
                "document_type": document_type,
            }
        else:
            raise HTTPException(
                status_code=500, detail=f"Failed to generate document '{document_type}'"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to generate document {document_type} for repository {repo_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to generate document: {str(e)}"
        )


# New endpoint for converting README to image
@router.post("/convert-readme-to-image", response_model=dict)
async def convert_readme_to_image(github_url: str, dark_mode: bool = False):
    """Convert README.md from a GitHub repository to an image and save to Supabase Storage"""
    try:
        # Extract repository information
        repo_info = extract_repo_info(github_url)

        # Create temporary file for image
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
            image_path = tmp_img.name

        try:
            # Take README blob screenshot with narrow width and minimal scrolling
            success = screenshot_readme_blob_sync(
                repo_info["owner"],
                repo_info["repo_name"],
                image_path,
                width=850,  # Narrow width to avoid side cropping
                scroll_pixels=200,  # Scroll 200 pixels to get past file navigation
                auto_detect_branch=True,  # Try main/master branches
            )

            if not success:
                raise HTTPException(
                    status_code=500, detail="Failed to convert README to image"
                )

            # Crop the image by 260px from top and then crop to 800x800 from top-left
            crop_success = crop_top_and_crop_to_size(
                image_path, top_crop=260, size=(850, 850)
            )
            if not crop_success:
                raise HTTPException(
                    status_code=500, detail="Failed to crop image from top and to size"
                )

            # Upload image to Supabase with timestamp and directory structure
            readme_image_url = upload_image_to_supabase(
                image_path, repo_info["owner"], repo_info["repo_name"]
            )

            if not readme_image_url:
                raise HTTPException(
                    status_code=500, detail="Failed to upload image to Supabase Storage"
                )

            return {
                "message": "README converted to image successfully",
                "repository": repo_info["full_name"],
                "image_url": readme_image_url,
                "dark_mode": dark_mode,
            }

        finally:
            # Clean up temporary image file
            if os.path.exists(image_path):
                os.unlink(image_path)

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Failed to convert README to image for {github_url}: {error_msg}")
        raise HTTPException(
            status_code=500, detail=f"Failed to convert README to image: {error_msg}"
        )
