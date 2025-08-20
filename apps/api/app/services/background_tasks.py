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

# Import for Playwright
from playwright.async_api import async_playwright

from repo2text.core import RepoAnalyzer

from app.services.database import db_service
from app.services.gemini_ai import gemini_service
from app.services.firecrawl_service import firecrawl_service
from app.services.twitter_service import twitter_service
from app.services.document_generation import document_generation_service
from app.services.simple_markdown_to_image import simple_markdown_to_image_sync, get_default_branch
from app.services.github_screenshot import screenshot_github_readme_smart_sync
from app.models import (
    RepositoryInsert,
    RepositoryAnalysisInsert,
    DocumentInsert,
    BatchProcessingInsert,
    BatchProcessingUpdate,
    BatchStatus,
    TwitterPostingInsert,
    TwitterPostingUpdate,
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


def extract_repo_info(github_url: str) -> Dict[str, str]:
    """Extract repository information from GitHub URL"""
    try:
        # Handle different GitHub URL formats
        if github_url.endswith(".git"):
            github_url = github_url[:-4]

        # Parse URL
        parsed = urlparse(github_url)
        path_parts = parsed.path.strip("/").split("/")

        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub URL format")

        owner = path_parts[0]
        repo_name = path_parts[1]

        return {
            "owner": owner,
            "repo_name": repo_name,
            "full_name": f"{owner}/{repo_name}",
            "clone_url": f"https://github.com/{owner}/{repo_name}.git",
        }
    except Exception as e:
        raise ValueError(f"Invalid GitHub URL: {str(e)}")


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


def markdown_to_image_sync(markdown_content: str, output_path: str, repo_owner: str = None, repo_name: str = None, dark_mode: bool = False):
    """Convert markdown content to image using the simple, reliable approach"""
    if repo_owner and repo_name:
        default_branch = get_default_branch(repo_owner, repo_name)
    else:
        default_branch = "main"
    
    return simple_markdown_to_image_sync(
        markdown_content, 
        output_path, 
        repo_owner, 
        repo_name, 
        default_branch,
        dark_mode
    )


def upload_image_to_supabase(file_path: str, owner: str, repo_name: str) -> Optional[str]:
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
        with open(file_path, 'rb') as f:
            response = supabase.storage.from_("content").upload(
                file=f,
                path=file_name,
                file_options={"content-type": "image/png"}
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
                {"processing_status": RepositoryProcessingStatus.PROCESSING}
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
            repo_id, 
            {"processing_status": RepositoryProcessingStatus.ANALYZED}
        )

        # Read the generated output file to get the full content
        output_file_path = result["output_file"]
        repo_content = ""
        if os.path.exists(output_file_path):
            with open(output_file_path, "r", encoding="utf-8") as f:
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
            "estimated_tokens": int(
                result["total_characters"] / 4
            ),  # Rough token estimate
            "total_size_bytes": result["total_characters"],
        }

        # Extract tree structure from repo2text result
        tree_structure = result.get("tree_structure", None)

        # Update task state
        update_task_status(
            task_id,
            TaskStatus.STARTED,
            "Saving analysis to database",
            75,
            repo_id=str(repo_id),
        )

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
            # Fetch README from GitHub
            readme_content = get_github_readme(repo_info["owner"], repo_info["repo_name"])
            
            if readme_content:
                # Create temporary file for image
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
                    image_path = tmp_img.name
                
                try:
                    # Convert markdown to image with dark mode support
                    logger.info(f"Creating README image for {repo_info['full_name']} with dark mode support")
                    success = simple_markdown_to_image_sync(
                        readme_content,
                        image_path,
                        repo_info["owner"],
                        repo_info["repo_name"],
                        get_default_branch(repo_info["owner"], repo_info["repo_name"]),
                        dark_mode=False  # Default to light mode for consistency with existing behavior
                    )
                    
                    if not success:
                        logger.warning(f"Failed to create README image for {repo_info['full_name']}")
                        readme_image_url = None
                    else:
                        # Upload image to Supabase only if conversion was successful
                        readme_image_url = upload_image_to_supabase(image_path, repo_info['owner'], repo_info['repo_name'])
                    
                    if readme_image_url:
                        logger.info(f"README image uploaded successfully for {repo_info['full_name']}")
                    else:
                        logger.warning(f"Failed to upload README image for {repo_info['full_name']}")
                finally:
                    # Clean up temporary image file
                    if os.path.exists(image_path):
                        os.unlink(image_path)
            else:
                logger.info(f"No README found for {repo_info['full_name']}")
        except Exception as readme_error:
            logger.error(f"Error processing README for {repo_info['full_name']}: {str(readme_error)}")
            
        # Update repository analysis with README image URL if available
        if readme_image_url:
            try:
                await db_service.update_repository_analysis(
                    analysis.id, 
                    {"readme_image_src": readme_image_url}
                )
                logger.info(f"Updated repository analysis with README image URL for {repo_info['full_name']}")
            except Exception as update_error:
                logger.error(f"Failed to update repository analysis with README image URL: {str(update_error)}")

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
            repo_id, 
            {"processing_status": RepositoryProcessingStatus.DOCS_GENERATED}
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
                # Generate AI summary but don't save it as a document
                logger.info(
                    f"AI summary generated successfully for repo {repo_id} (not saved to documents table)"
                )
                # Store the summary in generated_documents without creating a database entry
                generated_documents["ai_summary"] = "generated_but_not_saved"
                
                # Generate additional documents using the document generation service
                try:
                    # Generate multiple documents from the summary
                    document_results = await document_generation_service.generate_multiple_documents_from_summary(
                        repository_id=repo_id,
                        document_types=document_generation_service.DEFAULT_DOCUMENT_TYPES,
                        repository_summary=summary_result["summary"],
                        repository_info=repository_info,
                        analysis_data={
                            "tree_structure": tree_structure,
                            "stats": stats
                        }
                    )
                    
                    # Store the IDs of successfully generated documents
                    for doc_type, document in document_results.items():
                        if document:
                            generated_documents[doc_type] = str(document.id)
                            logger.info(f"Generated {doc_type} for repo {repo_id}: {document.id}")
                        else:
                            logger.warning(f"Failed to generate {doc_type} for repo {repo_id}")
                            
                except Exception as doc_error:
                    logger.error(
                        f"Document generation error for repo {repo_id}: {str(doc_error)}"
                    )
                    # Continue without failing the entire task
            else:
                logger.warning(
                    f"AI summary generation failed for repo {repo_id}: {summary_result.get('error', 'Unknown error')}"
                )

        except Exception as ai_error:
            logger.error(
                f"AI summary generation error for repo {repo_id}: {str(ai_error)}"
            )
            # Continue without failing the entire task

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
            repo_id, 
            {"processing_status": RepositoryProcessingStatus.COMPLETED}
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
            "document_id": str(document.id) if "document" in locals() else None,
            "ai_summary_id": None,  # AI summary is no longer saved as a document
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
        if 'repo_id' in locals():
            await db_service.update_repository(
                repo_id, 
                {"processing_status": RepositoryProcessingStatus.FAILED}
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
    progress: int = None,
    repo_id: str = None,
    error: str = None,
    repo_info: Dict = None,
    result: Dict = None,
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
        # Update batch status to processing
        await db_service.update_batch_processing(
            batch_id,
            BatchProcessingUpdate(
                status=BatchStatus.PROCESSING, started_at=datetime.utcnow()
            ),
        )

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
                    repository = await db_service.get_repository(repo_id)
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

                    # Update batch progress
                    await db_service.update_batch_processing(
                        batch_id,
                        BatchProcessingUpdate(
                            processed_repositories=processed_count,
                            successful_repositories=successful_count,
                            failed_repositories=failed_count,
                            task_ids=task_ids,
                        ),
                    )

                except Exception as e:
                    logger.error(
                        f"Task {task_id} for repository {repo_id} failed: {str(e)}"
                    )
                    failed_count += 1
                    processed_count += 1

                    # Update batch progress
                    await db_service.update_batch_processing(
                        batch_id,
                        BatchProcessingUpdate(
                            processed_repositories=processed_count,
                            successful_repositories=successful_count,
                            failed_repositories=failed_count,
                            task_ids=task_ids,
                        ),
                    )

            logger.info(
                f"Completed batch {i//max_concurrent + 1}. Progress: {processed_count}/{len(repository_ids)}"
            )

        # Mark batch as completed
        final_status = (
            BatchStatus.COMPLETED if failed_count == 0 else BatchStatus.COMPLETED
        )

        await db_service.update_batch_processing(
            batch_id,
            BatchProcessingUpdate(
                status=final_status,
                processed_repositories=processed_count,
                successful_repositories=successful_count,
                failed_repositories=failed_count,
                task_ids=task_ids,
                completed_at=datetime.utcnow(),
            ),
        )

        logger.info(
            f"Batch processing {batch_id} completed. Success: {successful_count}, Failed: {failed_count}"
        )

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Batch processing {batch_id} failed: {error_msg}")

        # Mark batch as failed
        await db_service.update_batch_processing(
            batch_id,
            BatchProcessingUpdate(
                status=BatchStatus.FAILED,
                error_message=error_msg,
                completed_at=datetime.utcnow(),
            ),
        )


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
):
    """Background task to post repository tweets"""
    logger.info(
        f"Starting Twitter posting task {posting_id} for {max_repositories} repositories"
    )

    try:
        # Check if Twitter service is configured
        if not twitter_service.is_configured():
            await db_service.update_twitter_posting(
                UUID(posting_id),
                TwitterPostingUpdate(
                    status=TwitterPostingStatus.FAILED,
                    error_message="Twitter service is not configured",
                    completed_at=datetime.utcnow(),
                ),
            )
            return {
                "status": "failed",
                "error": "Twitter service is not configured",
                "posting_id": posting_id,
            }

        # Update task to processing status
        await db_service.update_twitter_posting(
            UUID(posting_id),
            TwitterPostingUpdate(
                status=TwitterPostingStatus.PROCESSING, started_at=datetime.utcnow()
            ),
        )

        # Get repositories without Twitter links
        repositories = await db_service.get_repositories_without_twitter_links(
            limit=max_repositories
        )

        if not repositories:
            await db_service.update_twitter_posting(
                UUID(posting_id),
                TwitterPostingUpdate(
                    status=TwitterPostingStatus.COMPLETED,
                    error_message="No repositories found without Twitter links",
                    completed_at=datetime.utcnow(),
                ),
            )
            return {
                "status": "completed",
                "message": "No repositories found without Twitter links",
                "posting_id": posting_id,
                "processed": 0,
            }

        # Initialize counters
        processed_count = 0
        successful_posts = 0
        failed_posts = 0
        rate_limited_posts = 0
        posted_tweet_urls = []
        repository_ids = []

        logger.info(f"Found {len(repositories)} repositories to post")

        # Update status to posting
        await db_service.update_twitter_posting(
            UUID(posting_id),
            TwitterPostingUpdate(
                status=TwitterPostingStatus.POSTING,
                total_repositories=len(repositories),
                repository_ids=[str(repo.id) for repo in repositories],
            ),
        )

        # Process each repository
        for i, repository in enumerate(repositories):
            try:
                processed_count += 1
                repository_ids.append(str(repository.id))

                logger.info(
                    f"Processing repository {i+1}/{len(repositories)}: {repository.name}"
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
                if include_analysis:
                    try:
                        analysis = await db_service.get_repository_analysis_by_repo_id(
                            repository.id
                        )
                        if analysis and analysis.summary:
                            # Add summary to description (truncated)
                            repo_info["description"] = (
                                analysis.summary[:150] + "..."
                                if len(analysis.summary) > 150
                                else analysis.summary
                            )
                    except Exception as e:
                        logger.warning(
                            f"Could not get analysis for repository {repository.name}: {str(e)}"
                        )

                # Post tweet
                result = await twitter_service.post_repository_tweet(repo_info)

                if result["success"]:
                    successful_posts += 1
                    posted_tweet_urls.append(result["tweet_url"])

                    # Update repository with Twitter link
                    await db_service.update_repository_twitter_link(
                        repository.id, result["tweet_url"]
                    )

                    logger.info(
                        f"Successfully posted tweet for {repository.name}: {result['tweet_url']}"
                    )
                else:
                    failed_posts += 1
                    error_msg = result.get("error", "Unknown error")
                    logger.error(
                        f"Failed to post tweet for {repository.name}: {error_msg}"
                    )

                    # Check if it's a rate limit error
                    if "rate limit" in error_msg.lower():
                        rate_limited_posts += 1

                # Update progress
                await db_service.update_twitter_posting(
                    UUID(posting_id),
                    TwitterPostingUpdate(
                        processed_repositories=processed_count,
                        successful_posts=successful_posts,
                        failed_posts=failed_posts,
                        rate_limited_posts=rate_limited_posts,
                        posted_tweet_urls=posted_tweet_urls,
                    ),
                )

                # Delay between posts (except for the last one)
                if i < len(repositories) - 1:
                    logger.info(
                        f"Waiting {delay_between_posts} seconds before next post..."
                    )
                    await asyncio.sleep(delay_between_posts)

            except Exception as e:
                failed_posts += 1
                processed_count += 1
                error_msg = str(e)
                logger.error(
                    f"Error processing repository {repository.name}: {error_msg}"
                )

                # Update progress with error
                await db_service.update_twitter_posting(
                    UUID(posting_id),
                    TwitterPostingUpdate(
                        processed_repositories=processed_count,
                        failed_posts=failed_posts,
                        error_message=f"Last error: {error_msg}",
                    ),
                )

        # Mark task as completed
        await db_service.update_twitter_posting(
            UUID(posting_id),
            TwitterPostingUpdate(
                status=TwitterPostingStatus.COMPLETED,
                processed_repositories=processed_count,
                successful_posts=successful_posts,
                failed_posts=failed_posts,
                rate_limited_posts=rate_limited_posts,
                posted_tweet_urls=posted_tweet_urls,
                completed_at=datetime.utcnow(),
            ),
        )

        logger.info(
            f"Twitter posting task {posting_id} completed. Processed: {processed_count}, Successful: {successful_posts}, Failed: {failed_posts}"
        )

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
        logger.error(f"Twitter posting task failed for {posting_id}: {error_msg}")

        # Mark posting as failed
        await db_service.update_twitter_posting(
            UUID(posting_id),
            TwitterPostingUpdate(
                status=TwitterPostingStatus.FAILED,
                error_message=error_msg,
                completed_at=datetime.utcnow(),
            ),
        )

        logger.error(f"Task {posting_id} failed: {error_msg}")

        return {
            "status": "failed",
            "error": error_msg,
            "posting_id": posting_id,
            "processed": 0,
        }
