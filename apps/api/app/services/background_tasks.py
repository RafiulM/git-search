import os
import tempfile
import shutil
from typing import Dict, Any, Optional, List
from uuid import uuid4, UUID
from datetime import datetime
import asyncio
from urllib.parse import urlparse
import json
import logging
from dotenv import load_dotenv
import requests
import io

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Import for Supabase
from supabase import create_client, Client

from repo2text.core import RepoAnalyzer

from app.services.database import db_service
from app.services.gemini_ai import gemini_service
from app.services.firecrawl_service import firecrawl_service
from app.services.twitter_service import twitter_service
from app.services.document_generation import document_generation_service
from app.services.github_service import github_service
from app.services.fork_management_service import get_fork_management_service
from app.utils.repo_utils import extract_repo_info
from app.services.simple_markdown_to_image import (
    simple_markdown_to_image_sync,
    get_default_branch,
)
from app.services.github_screenshot import screenshot_github_readme_smart_sync
from app.services.readme_blob_screenshot import screenshot_readme_blob_sync
from app.services.image_cropper import crop_top_and_crop_to_size
from app.models import (
    RepositoryInsert,
    RepositoryAnalysisInsert,
    DocumentInsert,
    BatchProcessingInsert,
    BatchProcessingUpdate,
    BatchStatus,
    TwitterPostingStatus,
    SimpleScrapeStatus,
    ExtractedRepoInfo,
    RepositoryProcessingStatus,
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


def get_github_readme(owner: str, repo: str) -> Optional[str]:
    """Fetch README content from GitHub"""
    github_token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github.v3+json"}

    if github_token:
        headers["Authorization"] = f"token {github_token}"

    # Try different README file names
    readme_files = ["README.md", "readme.md", "Readme.md"]

    for filename in readme_files:
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filename}"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # The content is base64 encoded
                import base64

                content = base64.b64decode(data["content"]).decode("utf-8")
                return content
        except Exception as e:
            logger.warning(f"Failed to fetch {filename} for {owner}/{repo}: {str(e)}")
            continue

    logger.warning(f"No README found for {owner}/{repo}")
    return None


# Old complex functions removed - now using simple_markdown_to_image.py


def markdown_to_image_sync(
    markdown_content: str,
    output_path: str,
    repo_owner: str | None = None,
    repo_name: str | None = None,
    dark_mode: bool = False,
):
    """Convert markdown content to image using the simple, reliable approach"""
    if repo_owner and repo_name:
        default_branch = get_default_branch(repo_owner, repo_name)
    else:
        raise ValueError("repo_owner and repo_name are required")

    return simple_markdown_to_image_sync(
        markdown_content, output_path, repo_owner, repo_name, default_branch, dark_mode
    )


def upload_image_to_supabase(
    file_path: str, owner: str, repo_name: str
) -> Optional[str]:
    """Upload image to Supabase Storage and return public URL"""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if not supabase_url or not supabase_key:
            logger.error("Supabase URL or Key not configured")
            return None

        supabase: Client = create_client(supabase_url, supabase_key)

        # Generate timestamp for unique filename
        import time

        timestamp = int(time.time())
        file_name = f"{owner}/{repo_name}/{timestamp}_{repo_name}.png"

        # Upload file to storage
        with open(file_path, "rb") as f:
            response = supabase.storage.from_("content").upload(
                file=f, path=file_name, file_options={"content-type": "image/png"}
            )

        # Get public URL
        public_url = supabase.storage.from_("content").get_public_url(file_name)
        return public_url

    except Exception as e:
        logger.error(f"Failed to upload image to Supabase: {str(e)}")
        return None


async def analyze_repository_task(task_id: str, github_url: str):
    """Background task to analyze a GitHub repository using repo2text"""
    logger.info(f"Starting repository analysis task {task_id} for {github_url}")
    repo_info = None
    temp_clone_dir = None
    temp_output_dir = None

    try:
        # Update repository processing status to PROCESSING
        existing_repo = await db_service.get_repository_by_url(github_url)
        if existing_repo:
            await db_service.update_repository(
                existing_repo.id,
                {"processing_status": RepositoryProcessingStatus.PROCESSING},
            )
            repo_id = existing_repo.id
        else:
            # Create new repository entry
            repo_info = extract_repo_info(github_url)
            repo_data = RepositoryInsert(
                name=repo_info["repo_name"],
                repo_url=github_url,
                author=repo_info["owner"],
                processing_status=RepositoryProcessingStatus.PROCESSING,
            )

            new_repo = await db_service.create_repository(repo_data)
            repo_id = new_repo.id
            logger.info(f"Created new repository {repo_id} for {github_url}")

        # Update task state
        update_task_status(
            task_id, TaskStatus.STARTED, "Extracting repository information", 10
        )

        # Extract repository information (if not already done)
        if not repo_info:
            repo_info = extract_repo_info(github_url)

        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Initializing repository analyzer",
            20,
            repo_id=str(repo_id),
        )

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
            max_file_size_mb=10,
        )

        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Processing repository with repo2text",
            30,
            repo_id=str(repo_id),
        )

        # Process repository using repo2text
        result = analyzer.process_repository(github_url, keep_clone=False)

        if not result.get("success"):
            raise Exception(
                f"repo2text analysis failed: {result.get('error', 'Unknown error')}"
            )

        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Extracting analysis data",
            60,
            repo_id=str(repo_id),
        )

        # Update repository processing status to ANALYZED
        await db_service.update_repository(
            repo_id, {"processing_status": RepositoryProcessingStatus.ANALYZED}
        )

        # Read the generated output file to get the full content
        output_file_path = result.get("output_file", "")
        repo_content = ""
        if os.path.exists(output_file_path):
            with open(output_file_path, "r", encoding="utf-8") as f:
                repo_content = f.read()

        # Prepare statistics from repo2text result
        # Use files_processed as fallback for total_files if not available
        files_count = result.get("total_files", result.get("files_processed", 0))

        # Debug logging for repo2text result keys
        logger.debug(f"repo2text result keys: {list(result.keys())}")
        logger.debug(
            f"Using files_count: {files_count} (from total_files or files_processed)"
        )

        stats = {
            "files_processed": result.get("files_processed", 0),
            "binary_files_skipped": result.get("binary_files_skipped", 0),
            "large_files_skipped": result.get("large_files_skipped", 0),
            "encoding_errors": result.get("encoding_errors", 0),
            "total_characters": result.get("total_characters", 0),
            "total_lines": result.get("total_lines", 0),
            "total_files": files_count,
            "total_directories": result.get("total_directories", 0),
            "estimated_tokens": int(
                result.get("total_characters", 0) / 4
            ),  # Rough token estimate
            "total_size_bytes": result.get("total_characters", 0),
        }

        # Extract tree structure from repo2text result
        tree_structure = result.get("tree_structure", None)

        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Forking repository",
            70,
            repo_id=str(repo_id),
        )

        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Saving analysis to database",
            75,
            repo_id=str(repo_id),
        )

        # Create repository analysis entry with forked repo URL
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
            encoding_errors=stats["encoding_errors"],
        )

        analysis = await db_service.create_repository_analysis(analysis_data)

        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Saving repository content",
            85,
            repo_id=str(repo_id),
        )

        # Save repository content as document
        if repo_content:
            doc_data = DocumentInsert(
                repository_analysis_id=analysis.id,
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
                    "output_file": os.path.basename(output_file_path),
                },
            )

            document = await db_service.create_document(doc_data)

        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Processing README image",
            88,
            repo_id=str(repo_id),
        )

        # Process README to image and upload to Supabase
        readme_image_url = None
        try:
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
                    logger.warning(
                        f"Failed to create README image for {repo_info['full_name']}"
                    )
                    readme_image_url = None
                else:
                    # Crop the image by 260px from top and then crop to 850x850 from top-left
                    crop_success = crop_top_and_crop_to_size(
                        image_path, top_crop=260, size=(850, 850)
                    )
                    if not crop_success:
                        logger.warning(
                            f"Failed to crop image for {repo_info['full_name']}"
                        )
                        readme_image_url = None
                    else:
                        # Upload image to Supabase only if conversion was successful
                        readme_image_url = upload_image_to_supabase(
                            image_path, repo_info["owner"], repo_info["repo_name"]
                        )

                if readme_image_url:
                    logger.info(
                        f"README image uploaded successfully for {repo_info['full_name']}"
                    )
                else:
                    logger.warning(
                        f"Failed to upload README image for {repo_info['full_name']}"
                    )
            finally:
                # Clean up temporary image file
                if os.path.exists(image_path):
                    os.unlink(image_path)
        except Exception as readme_error:
            logger.error(
                f"Error processing README for {repo_info['full_name']}: {str(readme_error)}"
            )

        # Update repository analysis with README image URL if available
        if readme_image_url:
            try:
                await db_service.update_repository_analysis(
                    analysis.id, {"readme_image_src": readme_image_url}
                )
                logger.info(
                    f"Updated repository analysis with README image URL for {repo_info['full_name']}"
                )
            except Exception as update_error:
                logger.error(
                    f"Failed to update repository analysis with README image URL: {str(update_error)}"
                )

        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Generating AI summary",
            90,
            repo_id=str(repo_id),
        )

        # Update repository processing status to DOCS_GENERATED
        await db_service.update_repository(
            repo_id, {"processing_status": RepositoryProcessingStatus.DOCS_GENERATED}
        )

        # Generate AI summary using Gemini
        summary_result = None
        generated_documents = {}
        try:
            # Get system prompt from database or use default
            system_prompt = await gemini_service.get_system_prompt("repository_summary")

            # Prepare repository info for AI summary
            repository_info = {
                "repository_url": github_url,
                "name": repo_info["repo_name"],
                "author": repo_info["owner"],
                "statistics": {
                    "files_processed": stats["files_processed"],
                    "binary_files_skipped": stats["binary_files_skipped"],
                    "large_files_skipped": stats["large_files_skipped"],
                    "encoding_errors": stats["encoding_errors"],
                    "total_characters": stats["total_characters"],
                    "total_lines": stats["total_lines"],
                    "total_files_found": stats["total_files"],
                    "total_directories": stats["total_directories"],
                },
            }

            # Generate AI summary
            summary_result = await gemini_service.generate_repository_summary(
                full_text=repo_content,
                repository_info=repository_info,
                system_prompt=system_prompt,
            )

            if summary_result and summary_result.get("success"):
                # AI summary generated successfully
                ai_summary = summary_result["summary"]
                logger.info(
                    f"AI summary generated successfully for repo {repo_id} ({len(ai_summary)} chars)"
                )

                # Save to repository analysis
                await db_service.update_repository_analysis(
                    analysis.id, {"ai_summary": ai_summary}
                )

                # Generate short description from AI summary
                short_description = None
                try:
                    logger.info(
                        f"Generating short description from AI summary for repo {repo_id}"
                    )

                    short_desc_result = await gemini_service.generate_short_description(
                        summary=ai_summary,
                        repository_info=repository_info,
                        max_length=150,
                    )

                    if short_desc_result["success"]:
                        short_description = short_desc_result["short_description"]
                        logger.info(
                            f"Short description generated successfully for repo {repo_id} ({short_desc_result['length']} chars)"
                        )

                        # Save to repository analysis
                        await db_service.update_repository_analysis(
                            analysis.id, {"description": short_description}
                        )
                    else:
                        logger.warning(
                            f"Failed to generate short description for repo {repo_id}: {short_desc_result.get('error')}"
                        )

                except Exception as short_desc_error:
                    logger.error(
                        f"Error generating short description for repo {repo_id}: {str(short_desc_error)}"
                    )

                # Update repository analysis with AI summary and short description
                try:
                    analysis_updates = {"ai_summary": ai_summary}

                    if short_description:
                        analysis_updates["description"] = short_description

                    await db_service.update_repository_analysis(
                        analysis.id, analysis_updates
                    )

                    logger.info(
                        f"Updated repository analysis {analysis.id} with AI summary and description:"
                    )
                    logger.info(f"  AI Summary: {len(ai_summary)} characters")
                    if short_description:
                        logger.info(
                            f"  Description: {len(short_description)} characters"
                        )
                    else:
                        logger.info(f"  Description: Not generated")

                except Exception as analysis_update_error:
                    logger.error(
                        f"Failed to update repository analysis with AI data: {str(analysis_update_error)}"
                    )

                # Store the summary in generated_documents (for backwards compatibility)
                generated_documents["ai_summary"] = "saved_to_analysis_table"
                generated_documents["short_description"] = (
                    "saved_to_analysis_table"
                    if short_description
                    else "generation_failed"
                )

                # Check if we have both AI summary and short description before generating documents
                updated_analysis = await db_service.get_repository_analysis(analysis.id)

                if not updated_analysis:
                    logger.error(
                        f"Repository {repo_id} has no analysis, skipping document generation"
                    )
                    raise Exception(
                        f"Repository {repo_id} has no analysis, skipping document generation"
                    )

                has_ai_summary = (
                    updated_analysis.ai_summary and updated_analysis.ai_summary.strip()
                )
                has_description = (
                    updated_analysis.description
                    and updated_analysis.description.strip()
                )

                if has_ai_summary and has_description:
                    logger.info(
                        f"Repository {repo_id} has both AI summary and description, proceeding with document generation"
                    )

                    # Generate additional documents using the document generation service
                    try:
                        # Generate multiple documents from the summary
                        document_results = await document_generation_service.generate_multiple_documents_from_summary(
                            document_types=document_generation_service.DEFAULT_DOCUMENT_TYPES,
                            repository_summary=summary_result["summary"],
                            repository_info=repository_info,
                            analysis_data={
                                "tree_structure": tree_structure,
                                "stats": stats,
                            },
                            repository_analysis_id=analysis.id,
                        )

                        # Store the IDs of successfully generated documents
                        for doc_type, document in document_results.items():
                            if document:
                                generated_documents[doc_type] = str(document.id)
                                logger.info(
                                    f"Generated {doc_type} for repo {repo_id}: {document.id}"
                                )
                            else:
                                logger.warning(
                                    f"Failed to generate {doc_type} for repo {repo_id}"
                                )

                    except Exception as doc_error:
                        logger.error(
                            f"Document generation error for repo {repo_id}: {str(doc_error)}"
                        )
                        # Continue without failing the entire task
                else:
                    logger.warning(
                        f"Repository {repo_id} is missing AI summary or description - skipping document generation"
                    )
                    logger.info(
                        f"  has_ai_summary: {has_ai_summary}, has_description: {has_description}"
                    )
                    generated_documents["document_generation_skipped"] = (
                        "missing_ai_summary_or_description"
                    )
            else:
                logger.warning(
                    f"AI summary generation failed for repo {repo_id}: {summary_result.get('error', 'Unknown error')}"
                )

        except Exception as ai_error:
            logger.error(
                f"AI summary generation error for repo {repo_id}: {str(ai_error)}"
            )
            # Continue without failing the entire task

        # Create knowledge base fork if analysis is complete and has required data
        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Creating knowledge base fork",
            95,
            repo_id=str(repo_id),
        )

        logger.info(f"Attempting to create knowledge base for repo {repo_id}")

        # Get fork management service
        fork_service = get_fork_management_service(db_service)

        # Get the current repository and analysis
        repository = await db_service.get_repository(repo_id)
        current_analysis = await db_service.get_repository_analysis(analysis.id)

        if not current_analysis:
            logger.error(
                f"Repository {repo_id} has no analysis, skipping knowledge base creation"
            )
            raise Exception(
                f"Repository {repo_id} has no analysis, skipping knowledge base creation"
            )

        # Check if we have the required data for knowledge base creation
        has_ai_summary = (
            current_analysis.ai_summary and current_analysis.ai_summary.strip()
        )
        has_description = (
            current_analysis.description and current_analysis.description.strip()
        )

        # Get documents for this analysis (we might have just created them)
        knowledge_documents = await db_service.get_documents_by_repository_analysis(
            analysis.id
        )

        if has_ai_summary and has_description and knowledge_documents:
            logger.info(
                f"Repository {repo_id} has all required data for knowledge base creation: "
                f"AI summary, description, and {len(knowledge_documents)} documents"
            )

            # Create knowledge base
            fork_result, fork_error = (
                await fork_service.create_knowledge_base_for_analysis(
                    current_analysis, repository, knowledge_documents
                )
            )

            if fork_error:
                if "already has a forked repo URL" in fork_error:
                    logger.info(
                        f"Repository {repo_id} already has a fork, skipping knowledge base creation"
                    )
                    generated_documents["knowledge_base_fork"] = "already_exists"
                else:
                    logger.error(
                        f"Failed to create knowledge base for repo {repo_id}: {fork_error}"
                    )
                    raise Exception(
                        f"Knowledge base fork creation failed: {fork_error}"
                    )

            if not fork_result:
                logger.error(
                    f"Failed to create knowledge base for repo {repo_id}: {fork_error}"
                )
                raise Exception(f"Knowledge base fork creation failed: {fork_error}")

            logger.info(
                f"Successfully created knowledge base fork for repo {repo_id}: {fork_result['fork_url']}"
            )
            generated_documents["knowledge_base_fork"] = fork_result["fork_url"]

            # Update repository analysis with forked repo URL
            await db_service.update_repository_analysis(
                analysis.id, {"forked_repo_url": fork_result["fork_url"]}
            )
        else:
            logger.info(
                f"Repository {repo_id} is not ready for knowledge base creation - "
                f"has_ai_summary: {has_ai_summary}, has_description: {has_description}, "
                f"documents: {len(knowledge_documents) if knowledge_documents else 0}"
            )
            generated_documents["knowledge_base_fork"] = "not_ready"

        # Update repository with content info
        content_preview = (
            repo_content[:1000] + "..." if len(repo_content) > 1000 else repo_content
        )
        repo_update_data = {
            "full_text": content_preview,
            "content_expires_at": None,
            "updated_at": datetime.utcnow(),
        }

        await db_service.update_repository(repo_id, repo_update_data)

        # Update repository processing status to COMPLETED
        await db_service.update_repository(
            repo_id, {"processing_status": RepositoryProcessingStatus.COMPLETED}
        )

        # Prepare final result
        final_result = {
            "status": "completed",
            "repo_id": str(repo_id),
            "analysis_id": str(analysis.id),
            "repository": {
                "name": repo_info["repo_name"],
                "author": repo_info["owner"],
                "url": github_url,
                "full_name": repo_info["full_name"],
            },
            "stats": stats,
            "tree_structure": tree_structure,
            "generated_documents": generated_documents,
            "ai_summary_success": (
                summary_result.get("success", False) if summary_result else False
            ),
            "output_file": output_file_path,
            "progress": 100,
        }

        # Update task state to completion with final result
        update_task_status(
            task_id,
            TaskStatus.SUCCESS,
            "Analysis completed successfully",
            100,
            repo_id=str(repo_id),
            result=final_result,
        )

        logger.info(
            f"Repository analysis completed successfully for task {task_id}, repo {repo_id}"
        )

    except Exception as e:
        # Log error and return failure
        error_msg = str(e)
        logger.error(f"Repository analysis failed for {github_url}: {error_msg}")

        # Update repository processing status to FAILED
        if "repo_id" in locals():
            await db_service.update_repository(
                repo_id, {"processing_status": RepositoryProcessingStatus.FAILED}
            )

        # Update task state with error
        update_task_status(
            task_id,
            TaskStatus.FAILURE,
            "Analysis failed",
            error=error_msg,
            repo_info=repo_info,
        )

    finally:
        # Cleanup temporary directories
        for temp_dir in [temp_clone_dir, temp_output_dir]:
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as cleanup_error:
                    logger.warning(
                        f"Failed to cleanup temp directory {temp_dir}: {cleanup_error}"
                    )


def update_task_status(
    task_id: str,
    status: str,
    message: str,
    progress: int | None = None,
    repo_id: str | None = None,
    error: str | None = None,
    repo_info: dict | None = None,
    result: dict | None = None,
):
    """Update task status in storage"""
    if task_id not in task_storage:
        task_storage[task_id] = {
            "task_id": task_id,
            "status": TaskStatus.PENDING,
            "message": "Task created",
            "created_at": datetime.utcnow(),
        }

    task_storage[task_id].update(
        {"status": status, "message": message, "updated_at": datetime.utcnow()}
    )

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
                "message": "Task not found",
            }

        return task_storage[task_id]

    except Exception as e:
        return {
            "task_id": task_id,
            "status": "error",
            "error": str(e),
            "message": "Failed to get task status",
        }


def create_task(task_id: str) -> Dict[str, Any]:
    """Create a new task entry"""
    task_storage[task_id] = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "message": "Task created",
        "created_at": datetime.utcnow(),
        "progress": 0,
    }
    return task_storage[task_id]


async def batch_process_repositories_task(
    batch_id: str, repository_ids: List[str], max_concurrent: int = 5
):
    """Background task to process multiple repositories in batches"""
    logger.info(
        f"Starting batch processing {batch_id} for {len(repository_ids)} repositories"
    )

    try:
        # Process repositories in batches of max_concurrent
        processed_count = 0
        successful_count = 0
        failed_count = 0
        task_ids = []

        # Process in chunks of max_concurrent
        for i in range(0, len(repository_ids), max_concurrent):
            batch_repos = repository_ids[i : i + max_concurrent]
            batch_tasks = []

            logger.info(
                f"Processing batch {i//max_concurrent + 1} with {len(batch_repos)} repositories"
            )

            # Create tasks for this batch
            for repo_id in batch_repos:
                try:
                    # Get repository details
                    repository = await db_service.get_repository(UUID(repo_id))
                    if not repository:
                        logger.warning(f"Repository {repo_id} not found, skipping")
                        failed_count += 1
                        processed_count += 1
                        continue

                    # Create individual task
                    task_id = str(uuid4())
                    create_task(task_id)
                    task_ids.append(task_id)

                    # Create background task
                    task = asyncio.create_task(
                        analyze_repository_task(task_id, repository.repo_url)
                    )
                    batch_tasks.append((task_id, task, repo_id))

                    logger.info(
                        f"Created task {task_id} for repository {repository.name}"
                    )

                except Exception as e:
                    logger.error(
                        f"Failed to create task for repository {repo_id}: {str(e)}"
                    )
                    failed_count += 1
                    processed_count += 1

            # Wait for all tasks in this batch to complete
            for task_id, task, repo_id in batch_tasks:
                try:
                    await task

                    # Check task status
                    status_info = get_task_status(task_id)
                    if status_info.get("status") == TaskStatus.SUCCESS:
                        successful_count += 1
                        logger.info(f"Successfully processed repository {repo_id}")
                    else:
                        failed_count += 1
                        logger.warning(
                            f"Failed to process repository {repo_id}: {status_info.get('error', 'Unknown error')}"
                        )

                    processed_count += 1

                except Exception as e:
                    logger.error(
                        f"Task {task_id} for repository {repo_id} failed: {str(e)}"
                    )
                    failed_count += 1
                    processed_count += 1

            logger.info(
                f"Completed batch {i//max_concurrent + 1}. Progress: {processed_count}/{len(repository_ids)}"
            )

        # Mark batch as completed
        final_status = (
            BatchStatus.COMPLETED if failed_count == 0 else BatchStatus.COMPLETED
        )

        logger.info(
            f"Batch processing {batch_id} completed. Success: {successful_count}, Failed: {failed_count}"
        )

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Batch processing {batch_id} failed: {error_msg}")


async def scrape_website_and_extract_repositories_task(
    task_id: str,
    website_url: str,
    scraping_type: str = "single_page",
    max_pages: int = 10,
    auto_save: bool = True,
):
    """Background task to scrape a website and extract repository information (saves directly to repositories table)"""
    logger.info(f"Starting website scraping task {task_id} for {website_url}")
    start_time = datetime.utcnow()

    # Store task status in memory
    task_storage[task_id] = {
        "task_id": task_id,
        "status": SimpleScrapeStatus.SCRAPING,
        "website_url": website_url,
        "repositories_found": 0,
        "repositories_saved": 0,
        "extracted_repositories": [],
        "error_message": None,
        "started_at": start_time,
        "completed_at": None,
    }

    try:
        # Check if Firecrawl service is configured
        if not firecrawl_service.is_configured():
            raise Exception(
                "Firecrawl service is not configured. Please set FIRECRAWL_API_KEY environment variable."
            )

        # Scrape the website
        logger.info(f"Scraping website {website_url} with type {scraping_type}")

        if scraping_type == "crawl":
            scrape_result = await firecrawl_service.crawl_website(
                website_url, max_pages
            )
            scraped_content = scrape_result.get("combined_content", "")
            logger.debug(
                f"Crawl result keys: {list(scrape_result.keys()) if scrape_result else 'None'}"
            )
        else:
            scrape_result = await firecrawl_service.scrape_website(website_url)
            scraped_content = scrape_result.get("markdown", "")
            logger.debug(
                f"Single page scrape result keys: {list(scrape_result.keys()) if scrape_result else 'None'}"
            )

        if not scraped_content:
            logger.error(
                f"No content found in scrape result. Available keys: {list(scrape_result.keys()) if scrape_result else 'None'}"
            )
            logger.error(f"Scrape result: {scrape_result}")
            raise Exception("No content could be scraped from the website")

        logger.info(
            f"Successfully scraped {len(scraped_content)} characters from {website_url}"
        )

        # Update status to extracting
        task_storage[task_id]["status"] = SimpleScrapeStatus.EXTRACTING

        # Use Gemini to extract repository information
        logger.info("Extracting repository URLs using Gemini AI")
        extraction_result = await gemini_service.extract_repositories_from_content(
            scraped_content, website_url
        )

        logger.info(f"Extraction result: {extraction_result}")

        # Check if extraction was successful
        if not extraction_result.get("success", False):
            logger.warning(
                f"Repository extraction failed: {extraction_result.get('error', 'Unknown error')}"
            )
            repositories = []
            total_found = 0
        else:
            # With structured output, we can directly access the parsed data
            extracted_data = extraction_result.get("extracted_data")
            if extracted_data:
                repositories = extracted_data
                total_found = len(repositories)
                logger.info(
                    f"Successfully parsed {total_found} repositories from AI response"
                )
            else:
                repositories = []
                total_found = 0
                logger.warning("No extracted data in AI response")

        logger.info(f"Found {total_found} repositories in scraped content")

        # Convert to our model format
        extracted_repo_infos = []
        for repo in repositories:
            # If repo is already an ExtractedRepoInfo instance, use it directly
            if isinstance(repo, ExtractedRepoInfo):
                extracted_repo_infos.append(repo)
            else:
                # Otherwise, create a new instance from the attributes
                extracted_repo_infos.append(
                    ExtractedRepoInfo(
                        name=getattr(repo, "name", ""),
                        url=getattr(repo, "url", ""),
                        author=getattr(repo, "author", None),
                        description=getattr(repo, "description", None),
                        confidence_score=getattr(repo, "confidence_score", 0.0),
                    )
                )

        # Save repositories if auto_save is enabled
        repositories_saved = 0
        if auto_save and len(extracted_repo_infos) > 0:
            logger.info(
                f"Auto-saving {len(extracted_repo_infos)} repositories to database"
            )

            # Convert to list of RepositoryInsert
            repo_inserts = [
                RepositoryInsert(
                    name=repo.name,
                    repo_url=repo.url,
                    author=repo.author,
                    processing_status=RepositoryProcessingStatus.PENDING,
                )
                for repo in extracted_repo_infos
            ]

            await db_service.upsert_repositories(repo_inserts)
            # for repo_info in repositories:
            #     try:
            #         # Check if repository already exists
            #         existing_repo = await db_service.get_repository_by_url(
            #             repo_info.url
            #         )
            #         if existing_repo:
            #             logger.debug(
            #                 f"Repository {repo_info.url} already exists, skipping"
            #             )
            #             continue

            #         # Create new repository
            #         repo_data = RepositoryInsert(
            #             name=repo_info.name,
            #             repo_url=repo_info.url,
            #             author=repo_info.author,
            #         )

            #         await db_service.create_repository(repo_data)
            #         repositories_saved += 1
            #         logger.debug(f"Saved repository: {repo_info.name}")

            #     except Exception as e:
            #         logger.error(f"Failed to save repository {repo_info.url}: {str(e)}")
            #         continue

            # logger.info(
            #     f"Successfully saved {repositories_saved} out of {len(repositories)} repositories"
            # )

        # Update final status
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()

        task_storage[task_id].update(
            {
                "status": SimpleScrapeStatus.COMPLETED,
                "repositories_found": total_found,
                "repositories_saved": repositories_saved,
                "extracted_repositories": extracted_repo_infos,
                "completed_at": end_time,
                "processing_time_seconds": processing_time,
            }
        )

        logger.info(
            f"Website scraping completed successfully for {website_url}. Found {total_found} repositories, saved {repositories_saved}"
        )

        return {
            "status": "completed",
            "task_id": task_id,
            "repositories_found": total_found,
            "repositories_saved": repositories_saved,
        }

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Website scraping failed for {website_url}: {error_msg}")

        # Update task status with error
        task_storage[task_id].update(
            {
                "status": SimpleScrapeStatus.FAILED,
                "error_message": error_msg,
                "completed_at": datetime.utcnow(),
            }
        )

        return {"status": "failed", "error": error_msg, "task_id": task_id}


async def post_repository_tweets_task(
    posting_id: str,
    max_repositories: int = 5,
    delay_between_posts: int = 30,
    include_analysis: bool = False,
    include_media: bool = False,
):
    """Background task to post repository tweets"""
    start_time = datetime.utcnow()
    logger.info(
        f"🚀 Starting Twitter posting task {posting_id} at {start_time.isoformat()}"
    )
    logger.info(
        f"📊 Task parameters: max_repositories={max_repositories}, "
        f"delay={delay_between_posts}s, include_analysis={include_analysis}, "
        f"include_media={include_media}"
    )

    try:
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

            logger.info(
                "💡 Please check your Twitter API credentials in the Developer Portal"
            )
            return {
                "status": "failed",
                "error": f"{error_msg} - check logs for detailed validation results",
                "posting_id": posting_id,
            }

        logger.info("✅ Twitter service is properly configured")

        # Get repositories without Twitter links
        logger.info(
            f"🔍 Searching for repositories without Twitter links (limit: {max_repositories})..."
        )
        repositories = await db_service.get_repositories_without_twitter_links(
            limit=max_repositories
        )

        if not repositories:
            logger.warning("⚠️ No repositories found without Twitter links")
            return {
                "status": "completed",
                "message": "No repositories found without Twitter links",
                "posting_id": posting_id,
                "processed": 0,
            }

        logger.info(f"📋 Found {len(repositories)} repositories to process:")
        for i, repo in enumerate(repositories, 1):
            logger.info(f"  {i}. {repo.name} by {repo.author} - {repo.repo_url}")

        # Initialize counters
        processed_count = 0
        successful_posts = 0
        failed_posts = 0
        rate_limited_posts = 0
        posted_tweet_urls = []
        repository_ids = []

        logger.info(
            f"🏁 Starting to process {len(repositories)} repositories with {delay_between_posts}s delay between posts"
        )

        # Process each repository
        for i, repository in enumerate(repositories):
            try:
                processed_count += 1
                repository_ids.append(str(repository.id))

                logger.info(
                    f"📝 [{i+1}/{len(repositories)}] Processing repository: {repository.name}"
                )
                logger.info(f"   Repository ID: {repository.id}")
                logger.info(f"   Author: {repository.author}")
                logger.info(f"   URL: {repository.repo_url}")

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

                # Always try to get repository analysis for short description (REQUIRED)
                logger.info(
                    "   🔬 Fetching repository analysis for description (REQUIRED)..."
                )
                try:
                    analysis = await db_service.get_latest_repository_analysis(
                        repository.id
                    )

                    description_found = False

                    # First priority: Use the dedicated short description if available
                    if (
                        analysis
                        and analysis.description
                        and analysis.description.strip()
                    ):
                        original_desc = repo_info["description"]
                        repo_info["description"] = analysis.description.strip()
                        description_found = True
                        logger.info(
                            f"   ✅ Using AI-generated short description (was: '{original_desc}', now: '{repo_info['description'][:50]}...')"
                        )

                    # ERROR: No meaningful description available
                    if not description_found:
                        error_msg = f"Repository {repository.name} (ID: {repository.id}) has no AI-generated short description or analysis summary available. Cannot post to Twitter without meaningful description."
                        logger.error(f"   ❌ {error_msg}")

                        failed_posts += 1
                        processed_repositories += 1
                        continue  # Skip this repository and move to next

                except Exception as e:
                    error_msg = f"Could not get analysis for repository {repository.name}: {str(e)}"
                    logger.error(f"   ❌ {error_msg}")

                    failed_posts += 1
                    processed_repositories += 1
                    continue  # Skip this repository and move to next

                # If include_media is True, try to get README image URL
                if include_media:
                    logger.info("   🖼️ Fetching README image for media attachment...")
                    try:
                        analysis = await db_service.get_latest_repository_analysis(
                            repository.id
                        )
                        if analysis and analysis.readme_image_src:
                            repo_info["readme_image_url"] = analysis.readme_image_src
                            logger.info(
                                f"   ✅ Found README image: {analysis.readme_image_src}"
                            )
                        else:
                            logger.info(
                                f"   ℹ️ No README image available for {repository.name}"
                            )
                    except Exception as e:
                        logger.warning(
                            f"   ⚠️ Could not get README image for repository {repository.name}: {str(e)}"
                        )

                # Post tweet with or without media
                logger.info(f"   🐦 Posting tweet to Twitter...")
                result = await twitter_service.post_repository_tweet(
                    repo_info, include_media
                )

                if result["success"]:
                    successful_posts += 1
                    posted_tweet_urls.append(result["tweet_url"])

                    # Update repository analysis with Twitter link (new location)
                    logger.info(
                        f"   📝 Updating repository analysis with Twitter link..."
                    )
                    try:
                        analysis = await db_service.get_latest_repository_analysis(
                            repository.id
                        )
                        if analysis:
                            await db_service.update_repository_analysis(
                                analysis.id, {"twitter_link": result["tweet_url"]}
                            )
                            logger.info(
                                f"   ✅ Updated analysis {analysis.id} with Twitter link"
                            )
                        else:
                            logger.warning(
                                f"   ⚠️ No analysis found for repository {repository.name}"
                            )
                    except Exception as update_error:
                        logger.error(
                            f"   ❌ Failed to update analysis: {str(update_error)}"
                        )

                    logger.info(
                        f"   ✅ Tweet posted successfully! URL: {result['tweet_url']}"
                    )
                    if result.get("included_media"):
                        logger.info("   🖼️ Tweet includes media attachment")
                    if result.get("tweet_id"):
                        logger.info(f"   🆔 Tweet ID: {result['tweet_id']}")
                else:
                    failed_posts += 1
                    error_msg = result.get("error", "Unknown error")
                    logger.error(
                        f"   ❌ Failed to post tweet for {repository.name}: {error_msg}"
                    )

                    # Check if it's a rate limit error
                    if "rate limit" in error_msg.lower():
                        rate_limited_posts += 1
                        logger.warning(
                            f"   🚫 Rate limit detected for {repository.name}"
                        )

                # Log progress summary
                success_rate = (
                    (successful_posts / processed_count * 100)
                    if processed_count > 0
                    else 0
                )
                logger.info(
                    f"📊 Progress: {processed_count}/{len(repositories)} processed | ✅ {successful_posts} successful | ❌ {failed_posts} failed | 🚫 {rate_limited_posts} rate limited | {success_rate:.1f}% success rate"
                )

                # Delay between posts (except for the last one)
                if i < len(repositories) - 1:
                    logger.info(
                        f"   ⏳ Waiting {delay_between_posts} seconds before next post to respect rate limits..."
                    )
                    await asyncio.sleep(delay_between_posts)
                    logger.info("   ⏰ Wait complete, proceeding to next repository")

            except Exception as e:
                failed_posts += 1
                processed_count += 1
                error_msg = str(e)
                logger.error(
                    f"   💥 Exception while processing repository {repository.name}: {error_msg}"
                )
                logger.error(f"   📍 Exception occurred at step: repository processing")

        # Log final results
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        logger.info("🏁 " + "=" * 60)
        logger.info(f"🏁 Twitter posting task {posting_id} completed!")
        logger.info(f"⏰ Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        logger.info(f"📊 Final Results:")
        logger.info(f"   📋 Total repositories: {len(repositories)}")
        logger.info(f"   ✅ Successful posts: {successful_posts}")
        logger.info(f"   ❌ Failed posts: {failed_posts}")
        logger.info(f"   🚫 Rate limited posts: {rate_limited_posts}")
        logger.info(
            f"   📈 Success rate: {(successful_posts/len(repositories)*100):.1f}%"
        )

        if posted_tweet_urls:
            logger.info(f"🐦 Posted tweet URLs:")
            for j, url in enumerate(posted_tweet_urls, 1):
                logger.info(f"   {j}. {url}")

        if failed_posts > 0:
            logger.warning(
                f"⚠️ {failed_posts} repositories failed to post - check individual error messages above"
            )

        if rate_limited_posts > 0:
            logger.warning(
                f"🚫 {rate_limited_posts} repositories were rate limited - consider increasing delay_between_posts"
            )

        logger.info("🏁 " + "=" * 60)

        return {
            "status": "completed",
            "posting_id": posting_id,
            "processed": processed_count,
            "successful": successful_posts,
            "failed": failed_posts,
            "rate_limited": rate_limited_posts,
            "tweet_urls": posted_tweet_urls,
        }

    except Exception as e:
        error_msg = str(e)
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        logger.error("💥 " + "=" * 60)
        logger.error(f"💥 FATAL ERROR in Twitter posting task {posting_id}!")
        logger.error(f"⏰ Task failed after {duration:.1f} seconds")
        logger.error(f"❌ Error: {error_msg}")
        logger.error(f"📍 Task failed at top-level exception handling")
        logger.error("💥 " + "=" * 60)

        return {
            "status": "failed",
            "error": error_msg,
            "posting_id": posting_id,
            "processed": 0,
        }


async def generate_ai_summary_and_description_task(task_id: str, github_url: str):
    """Background task to generate AI summary and description for repositories that have analysis but are missing these fields"""
    logger.info(
        f"Starting AI summary/description generation task {task_id} for {github_url}"
    )

    try:
        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Finding repository and analysis",
            10,
        )

        # Find the repository
        existing_repo = await db_service.get_repository_by_url(github_url)
        if not existing_repo:
            raise Exception(f"Repository not found for URL: {github_url}")

        repo_id = existing_repo.id
        repo_info = {
            "repo_name": existing_repo.name,
            "owner": existing_repo.author,
            "full_name": (
                f"{existing_repo.author}/{existing_repo.name}"
                if existing_repo.author
                else existing_repo.name
            ),
        }

        # Get the latest repository analysis
        analysis = await db_service.get_latest_repository_analysis(repo_id)
        if not analysis:
            raise Exception(
                f"No analysis found for repository {repo_info['full_name']}"
            )

        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Checking what needs to be generated",
            20,
            repo_id=str(repo_id),
        )

        # Check what needs to be generated
        needs_ai_summary = not analysis.ai_summary or not analysis.ai_summary.strip()
        needs_description = not analysis.description or not analysis.description.strip()

        logger.info(
            f"Repository {repo_info['full_name']}: needs_ai_summary={needs_ai_summary}, needs_description={needs_description}"
        )

        if not needs_ai_summary and not needs_description:
            # Nothing to generate, task completed
            update_task_status(
                task_id,
                TaskStatus.SUCCESS,
                "AI summary and description already exist",
                100,
                repo_id=str(repo_id),
                result={
                    "status": "completed",
                    "message": "AI summary and description already exist",
                    "repository_id": str(repo_id),
                    "analysis_id": str(analysis.id),
                },
            )
            return

        # Get the repository content from documents
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Getting repository content",
            30,
            repo_id=str(repo_id),
        )

        documents = await db_service.get_documents_by_repository(
            repo_id, "repository_analysis"
        )
        if not documents:
            raise Exception(
                f"No repository analysis content found for {repo_info['full_name']}"
            )

        repo_content = documents[0].content

        # Prepare repository info for AI processing
        repository_info = {
            "repository_url": github_url,
            "name": repo_info["repo_name"],
            "author": repo_info["owner"],
            "statistics": {
                "files_processed": analysis.files_processed or 0,
                "binary_files_skipped": analysis.binary_files_skipped or 0,
                "large_files_skipped": analysis.large_files_skipped or 0,
                "encoding_errors": analysis.encoding_errors or 0,
                "total_characters": analysis.total_characters or 0,
                "total_lines": analysis.total_lines or 0,
                "total_files_found": analysis.total_files_found or 0,
                "total_directories": analysis.total_directories or 0,
            },
        }

        generated_data = {}

        # Generate AI summary if needed
        if needs_ai_summary:
            update_task_status(
                task_id,
                TaskStatus.STARTED,
                "Generating AI summary",
                50,
                repo_id=str(repo_id),
            )

            try:
                # Get system prompt from database or use default
                system_prompt = await gemini_service.get_system_prompt(
                    "repository_summary"
                )

                # Generate AI summary using Gemini
                summary_result = await gemini_service.generate_repository_summary(
                    full_text=repo_content,
                    repository_info=repository_info,
                    system_prompt=system_prompt,
                )

                if summary_result and summary_result.get("success"):
                    ai_summary = summary_result["summary"]
                    generated_data["ai_summary"] = ai_summary
                    logger.info(
                        f"AI summary generated successfully for {repo_info['full_name']} ({len(ai_summary)} chars)"
                    )
                else:
                    logger.warning(
                        f"Failed to generate AI summary for {repo_info['full_name']}: {summary_result.get('error', 'Unknown error')}"
                    )

            except Exception as ai_error:
                logger.error(
                    f"Error generating AI summary for {repo_info['full_name']}: {str(ai_error)}"
                )
        else:
            # Use existing AI summary
            generated_data["ai_summary"] = analysis.ai_summary

        # Generate description if needed and we have AI summary
        if needs_description and generated_data.get("ai_summary"):
            update_task_status(
                task_id,
                TaskStatus.STARTED,
                "Generating short description",
                70,
                repo_id=str(repo_id),
            )

            if not generated_data["ai_summary"]:
                raise Exception(f"No AI summary found for {repo_info['full_name']}")

            try:
                short_desc_result = await gemini_service.generate_short_description(
                    summary=generated_data["ai_summary"],
                    repository_info=repository_info,
                    max_length=150,
                )

                if short_desc_result["success"]:
                    short_description = short_desc_result["short_description"]
                    generated_data["description"] = short_description
                    logger.info(
                        f"Short description generated successfully for {repo_info['full_name']} ({short_desc_result['length']} chars)"
                    )
                else:
                    logger.warning(
                        f"Failed to generate short description for {repo_info['full_name']}: {short_desc_result.get('error')}"
                    )

            except Exception as desc_error:
                logger.error(
                    f"Error generating short description for {repo_info['full_name']}: {str(desc_error)}"
                )
        elif analysis.description:
            # Use existing description
            generated_data["description"] = analysis.description

        # Update the repository analysis with generated data
        if generated_data:
            update_task_status(
                task_id,
                TaskStatus.STARTED,
                "Saving generated data",
                90,
                repo_id=str(repo_id),
            )

            try:
                await db_service.update_repository_analysis(analysis.id, generated_data)
                logger.info(
                    f"Updated repository analysis {analysis.id} with generated data"
                )
            except Exception as update_error:
                logger.error(
                    f"Failed to update repository analysis: {str(update_error)}"
                )
                raise update_error

        # Task completed successfully
        result_data = {
            "status": "completed",
            "repository_id": str(repo_id),
            "analysis_id": str(analysis.id),
            "repository": {
                "name": repo_info["repo_name"],
                "author": repo_info["owner"],
                "url": github_url,
                "full_name": repo_info["full_name"],
            },
            "generated": {
                "ai_summary": bool(
                    generated_data.get("ai_summary") and needs_ai_summary
                ),
                "description": bool(
                    generated_data.get("description") and needs_description
                ),
            },
            "progress": 100,
        }

        update_task_status(
            task_id,
            TaskStatus.SUCCESS,
            "AI summary and description generation completed",
            100,
            repo_id=str(repo_id),
            result=result_data,
        )

        logger.info(
            f"Completed AI summary/description generation for {repo_info['full_name']}"
        )

    except Exception as e:
        error_msg = str(e)
        logger.error(
            f"AI summary/description generation failed for {github_url}: {error_msg}"
        )

        # Update task state with error
        update_task_status(
            task_id,
            TaskStatus.FAILURE,
            "AI summary/description generation failed",
            error=error_msg,
        )


async def generate_documents_with_ai_ready_task(task_id: str, github_url: str):
    """Background task to generate documents for repositories that have AI summary and description ready"""
    logger.info(
        f"Starting document generation task (AI ready) {task_id} for {github_url}"
    )

    try:
        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Finding repository and analysis",
            10,
        )

        # Find the repository
        existing_repo = await db_service.get_repository_by_url(github_url)
        if not existing_repo:
            raise Exception(f"Repository not found for URL: {github_url}")

        repo_id = existing_repo.id
        repo_info = {
            "repo_name": existing_repo.name,
            "owner": existing_repo.author,
            "full_name": (
                f"{existing_repo.author}/{existing_repo.name}"
                if existing_repo.author
                else existing_repo.name
            ),
        }

        # Get the latest repository analysis
        analysis = await db_service.get_latest_repository_analysis(repo_id)
        if not analysis:
            raise Exception(
                f"No analysis found for repository {repo_info['full_name']}"
            )

        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Checking if AI summary and description are ready",
            20,
            repo_id=str(repo_id),
        )

        # Check if AI summary and description are available
        has_ai_summary = analysis.ai_summary and analysis.ai_summary.strip()
        has_description = analysis.description and analysis.description.strip()

        logger.info(
            f"Repository {repo_info['full_name']}: has_ai_summary={has_ai_summary}, has_description={has_description}"
        )

        if not has_ai_summary or not has_description:
            raise Exception(
                f"Repository {repo_info['full_name']} is missing required AI summary or description. Cannot generate documents."
            )

        # Check if documents already exist
        existing_documents = await db_service.get_documents_by_repository_analysis(
            analysis.id
        )
        if existing_documents:
            logger.info(
                f"Repository {repo_info['full_name']} already has {len(existing_documents)} documents"
            )

            # Task completed - documents already exist
            update_task_status(
                task_id,
                TaskStatus.SUCCESS,
                "Documents already exist",
                100,
                repo_id=str(repo_id),
                result={
                    "status": "completed",
                    "message": "Documents already exist",
                    "repository_id": str(repo_id),
                    "analysis_id": str(analysis.id),
                    "existing_documents": len(existing_documents),
                },
            )
            return

        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Generating documents from AI summary",
            50,
            repo_id=str(repo_id),
        )

        # Prepare repository info for document generation
        repository_info = {
            "repository_url": github_url,
            "name": repo_info["repo_name"],
            "author": repo_info["owner"],
            "statistics": {
                "files_processed": analysis.files_processed or 0,
                "binary_files_skipped": analysis.binary_files_skipped or 0,
                "large_files_skipped": analysis.large_files_skipped or 0,
                "encoding_errors": analysis.encoding_errors or 0,
                "total_characters": analysis.total_characters or 0,
                "total_lines": analysis.total_lines or 0,
                "total_files_found": analysis.total_files_found or 0,
                "total_directories": analysis.total_directories or 0,
            },
        }

        analysis_data = {
            "tree_structure": analysis.tree_structure,
            "stats": repository_info["statistics"],
        }

        # Generate documents using the document generation service
        try:
            if not analysis.ai_summary:
                raise Exception(f"No AI summary found for {repo_info['full_name']}")

            document_results = await document_generation_service.generate_multiple_documents_from_summary(
                repository_analysis_id=analysis.id,
                document_types=document_generation_service.DEFAULT_DOCUMENT_TYPES,
                repository_summary=analysis.ai_summary,
                repository_info=repository_info,
                analysis_data=analysis_data,
            )

            # Count successful and failed generations
            successful_docs = {}
            failed_docs = []

            for doc_type, document in document_results.items():
                if document:
                    successful_docs[doc_type] = str(document.id)
                    logger.info(
                        f"Generated {doc_type} for {repo_info['full_name']}: {document.id}"
                    )
                else:
                    failed_docs.append(doc_type)
                    logger.warning(
                        f"Failed to generate {doc_type} for {repo_info['full_name']}"
                    )

        except Exception as doc_error:
            logger.error(
                f"Document generation error for {repo_info['full_name']}: {str(doc_error)}"
            )
            raise doc_error

        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Document generation completed",
            90,
            repo_id=str(repo_id),
        )

        # Task completed successfully
        result_data = {
            "status": "completed",
            "repository_id": str(repo_id),
            "analysis_id": str(analysis.id),
            "repository": {
                "name": repo_info["repo_name"],
                "author": repo_info["owner"],
                "url": github_url,
                "full_name": repo_info["full_name"],
            },
            "generated_documents": successful_docs,
            "failed_documents": failed_docs,
            "success_count": len(successful_docs),
            "failure_count": len(failed_docs),
            "total_requested": len(document_generation_service.DEFAULT_DOCUMENT_TYPES),
            "progress": 100,
        }

        update_task_status(
            task_id,
            TaskStatus.SUCCESS,
            f"Document generation completed: {len(successful_docs)} successful, {len(failed_docs)} failed",
            100,
            repo_id=str(repo_id),
            result=result_data,
        )

        logger.info(
            f"Completed document generation for {repo_info['full_name']}: {len(successful_docs)} successful, {len(failed_docs)} failed"
        )

    except Exception as e:
        error_msg = str(e)
        logger.error(
            f"Document generation (AI ready) failed for {github_url}: {error_msg}"
        )

        # Update task state with error
        update_task_status(
            task_id,
            TaskStatus.FAILURE,
            "Document generation failed",
            error=error_msg,
        )


async def comprehensive_repository_processing_task(task_id: str, github_url: str):
    """Background task for comprehensive repository processing - determines what needs to be done and does it"""
    logger.info(
        f"Starting comprehensive repository processing task {task_id} for {github_url}"
    )

    try:
        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Analyzing repository state",
            5,
        )

        # Find the repository
        existing_repo = await db_service.get_repository_by_url(github_url)
        if not existing_repo:
            logger.info(f"Repository not found, will run full analysis: {github_url}")
            # Repository doesn't exist - run full analysis
            await analyze_repository_task(task_id, github_url)
            return

        repo_id = existing_repo.id
        repo_info = {
            "repo_name": existing_repo.name,
            "owner": existing_repo.author,
            "full_name": (
                f"{existing_repo.author}/{existing_repo.name}"
                if existing_repo.author
                else existing_repo.name
            ),
        }

        # Get the latest repository analysis
        analysis = await db_service.get_latest_repository_analysis(repo_id)
        if not analysis:
            logger.info(
                f"Repository exists but has no analysis, will run full analysis: {repo_info['full_name']}"
            )
            # Repository exists but no analysis - run full analysis
            await analyze_repository_task(task_id, github_url)
            return

        # Check if there are documents that reference a repository_analysis_id that doesn't exist
        # This can happen if analysis was deleted but documents remain
        documents_for_repo = await db_service.get_documents_by_repository_analysis(
            analysis.id
        )

        # Also check if there are any documents in the table that reference this repository's analysis
        # but the analysis might be corrupted or incomplete
        try:
            # Try to get all documents that might reference analyses for this repository
            all_analyses_for_repo = await db_service.list_repository_analyses(
                repo_id, skip=0, limit=1000
            )
            analyses_list = all_analyses_for_repo[0] if all_analyses_for_repo else []

            # Check if any analysis exists but is missing critical data
            if analysis and not analysis.tree_structure:
                logger.warning(
                    f"Repository {repo_info['full_name']} has analysis but missing tree_structure - regenerating"
                )
                await analyze_repository_task(task_id, github_url)
                return

            # Check if analysis exists but no repository analysis document exists
            repo_analysis_docs = await db_service.get_documents_by_repository_analysis(
                analysis.id, "repository_analysis"
            )
            if not repo_analysis_docs:
                logger.warning(
                    f"Repository {repo_info['full_name']} has analysis record but no repository analysis document - regenerating"
                )
                await analyze_repository_task(task_id, github_url)
                return

        except Exception as doc_check_error:
            logger.warning(
                f"Error checking document consistency for {repo_info['full_name']}: {str(doc_check_error)}"
            )
            # If we can't verify document consistency, regenerate to be safe
            logger.info(
                f"Regenerating analysis due to document consistency check failure: {repo_info['full_name']}"
            )
            await analyze_repository_task(task_id, github_url)
            return

        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Determining what processing is needed",
            15,
            repo_id=str(repo_id),
        )

        # Check what needs to be generated
        needs_ai_summary = not analysis.ai_summary or not analysis.ai_summary.strip()
        needs_description = not analysis.description or not analysis.description.strip()

        # Check if documents exist
        existing_documents = await db_service.get_documents_by_repository_analysis(
            analysis.id
        )
        needs_documents = len(existing_documents) == 0

        logger.info(f"Repository {repo_info['full_name']} status:")
        logger.info(f"  needs_ai_summary: {needs_ai_summary}")
        logger.info(f"  needs_description: {needs_description}")
        logger.info(f"  needs_documents: {needs_documents}")
        logger.info(f"  existing_documents: {len(existing_documents)}")

        # Determine processing path
        if needs_ai_summary or needs_description:
            logger.info(
                f"Repository {repo_info['full_name']} needs AI summary/description generation"
            )
            # Generate AI summary and/or description
            await generate_ai_summary_and_description_task(task_id, github_url)

            # After generating AI summary/description, check if we also need documents
            if needs_documents:
                logger.info(
                    f"Repository {repo_info['full_name']} will also need documents after AI generation"
                )
                # Note: Documents will be generated in the next batch run since AI data is now available
                # We don't generate documents in the same task to avoid complexity

        elif needs_documents:
            logger.info(
                f"Repository {repo_info['full_name']} has AI data but needs documents"
            )
            # Has AI summary and description, but missing documents
            await generate_documents_with_ai_ready_task(task_id, github_url)

        else:
            logger.info(
                f"Repository {repo_info['full_name']} appears to be fully processed"
            )
            # Repository appears to be fully processed
            update_task_status(
                task_id,
                TaskStatus.SUCCESS,
                "Repository is already fully processed",
                100,
                repo_id=str(repo_id),
                result={
                    "status": "completed",
                    "message": "Repository is already fully processed",
                    "repository_id": str(repo_id),
                    "analysis_id": str(analysis.id),
                    "has_ai_summary": bool(
                        analysis.ai_summary and analysis.ai_summary.strip()
                    ),
                    "has_description": bool(
                        analysis.description and analysis.description.strip()
                    ),
                    "document_count": len(existing_documents),
                },
            )

    except Exception as e:
        error_msg = str(e)
        logger.error(
            f"Comprehensive repository processing failed for {github_url}: {error_msg}"
        )

        # Update task state with error
        update_task_status(
            task_id,
            TaskStatus.FAILURE,
            "Comprehensive processing failed",
            error=error_msg,
        )
