import os
from typing import Optional, List, Dict, Any, Union
from supabase import create_client, Client
from uuid import UUID, uuid4
import json
from datetime import datetime
from dotenv import load_dotenv


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


# Load environment variables
load_dotenv()

from app.models import (
    Repository,
    RepositoryInsert,
    RepositoryUpdate,
    RepositoryAnalysis,
    RepositoryAnalysisInsert,
    RepositoryAnalysisUpdate,
    Document,
    DocumentInsert,
    DocumentUpdate,
    BatchProcessing,
    BatchProcessingInsert,
    BatchProcessingUpdate,
    RepositoryWithAnalysis,
    RepositoryAnalysisSummary,
    Prompt,
    PromptInsert,
    PromptUpdate,
)


class DatabaseService:
    """Database service for Supabase operations"""

    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    # Repository operations
    async def create_repository(self, repo_data: RepositoryInsert) -> Repository:
        """Create a new repository"""
        try:
            # Create a clean JSON object with only the fields that exist in the schema
            data = {}

            # Generate a new UUID
            data["id"] = str(uuid4())

            # Map required fields
            if repo_data.name:
                data["name"] = repo_data.name
            else:
                raise ValueError("name is required")

            if repo_data.repo_url:
                data["repo_url"] = repo_data.repo_url
            else:
                raise ValueError("repo_url is required")

            # Map optional fields
            if repo_data.author is not None:
                data["author"] = repo_data.author
            if repo_data.branch is not None:
                data["branch"] = repo_data.branch

            # Content storage fields
            if repo_data.content_url is not None:
                data["content_url"] = repo_data.content_url
            if repo_data.content_expires_at is not None:
                # Convert datetime to ISO format string for Supabase
                if isinstance(repo_data.content_expires_at, datetime):
                    data["content_expires_at"] = (
                        repo_data.content_expires_at.isoformat()
                    )
                else:
                    data["content_expires_at"] = repo_data.content_expires_at
            if repo_data.full_text is not None:
                data["full_text"] = repo_data.full_text
            if repo_data.full_text_path is not None:
                data["full_text_path"] = repo_data.full_text_path

            # Twitter link
            if repo_data.twitter_link is not None:
                data["twitter_link"] = repo_data.twitter_link

            # Processing status
            if repo_data.processing_status is not None:
                data["processing_status"] = repo_data.processing_status.value
            else:
                # Default to PENDING if not specified
                data["processing_status"] = "pending"

            result = self.client.table("repositories").insert(data).execute()

            if result.data:
                return Repository(**result.data[0])
            else:
                raise Exception("Failed to create repository")

        except Exception as e:
            raise Exception(f"Database error creating repository: {str(e)}")

    async def upsert_repositories(
        self, repo_data_list: List[RepositoryInsert]
    ) -> List[Repository]:
        """Bulk upsert repositories (create if not exists, update if exists) using Supabase upsert"""
        try:
            # Convert list of RepositoryInsert objects to list of dictionaries
            data_list = []

            for repo_data in repo_data_list:
                # Create a clean JSON object with only the fields that exist in the schema
                data = {}

                # Extract repository name from URL (part after the last slash)
                if repo_data.repo_url:
                    # Get the repository name from the URL (part after the last slash)
                    repo_name = repo_data.repo_url.rstrip("/").split("/")[-1]
                    # Remove .git suffix if present
                    if repo_name.endswith(".git"):
                        repo_name = repo_name[:-4]
                    data["name"] = repo_name
                    data["repo_url"] = repo_data.repo_url
                else:
                    raise ValueError("repo_url is required")

                # Map optional fields
                if repo_data.author is not None:
                    data["author"] = repo_data.author
                if repo_data.branch is not None:
                    data["branch"] = repo_data.branch

                # Content storage fields
                if repo_data.content_url is not None:
                    data["content_url"] = repo_data.content_url
                if repo_data.content_expires_at is not None:
                    # Convert datetime to ISO format string for Supabase
                    if isinstance(repo_data.content_expires_at, datetime):
                        data["content_expires_at"] = (
                            repo_data.content_expires_at.isoformat()
                        )
                    else:
                        data["content_expires_at"] = repo_data.content_expires_at
                if repo_data.full_text is not None:
                    data["full_text"] = repo_data.full_text
                if repo_data.full_text_path is not None:
                    data["full_text_path"] = repo_data.full_text_path

                # Twitter link
                if repo_data.twitter_link is not None:
                    data["twitter_link"] = repo_data.twitter_link

                # Processing status
                if repo_data.processing_status is not None:
                    data["processing_status"] = repo_data.processing_status.value
                else:
                    # Default to PENDING if not specified
                    data["processing_status"] = "pending"

                data_list.append(data)

            # Use Supabase bulk upsert with on_conflict on repo_url
            result = (
                self.client.table("repositories")
                .upsert(data_list, on_conflict="repo_url")
                .execute()
            )

            if result.data:
                return [Repository(**repo_data) for repo_data in result.data]
            else:
                raise Exception("Failed to upsert repositories")

        except Exception as e:
            raise Exception(f"Database error upserting repositories: {str(e)}")

    async def get_repository(self, repo_id: UUID) -> Optional[Repository]:
        """Get repository by ID"""
        try:
            result = (
                self.client.table("repositories")
                .select("*")
                .eq("id", str(repo_id))
                .execute()
            )

            if result.data:
                return Repository(**result.data[0])
            return None

        except Exception as e:
            raise Exception(f"Database error getting repository: {str(e)}")

    async def get_repository_by_url(self, repo_url: str) -> Optional[Repository]:
        """Get repository by URL"""
        try:
            result = (
                self.client.table("repositories")
                .select("*")
                .eq("repo_url", repo_url)
                .execute()
            )

            if result.data:
                return Repository(**result.data[0])
            return None

        except Exception as e:
            raise Exception(f"Database error getting repository by URL: {str(e)}")

    async def update_repository(
        self, repo_id: UUID, update_data: Union[RepositoryUpdate, Dict[str, Any]]
    ) -> Optional[Repository]:
        """Update repository"""
        try:
            # Create a clean JSON object with only the fields that exist in the schema
            data = {}

            # Extract values from either Dict or Pydantic model
            if isinstance(update_data, Dict):
                # It's a dictionary
                source = update_data
                get_value = lambda key: source.get(key)
            else:
                # It's a Pydantic model
                source = update_data
                get_value = lambda key: getattr(source, key, None)

            # Map fields explicitly based on the schema
            # Repository identification
            if get_value("name") is not None:
                data["name"] = get_value("name")
            if get_value("repo_url") is not None:
                data["repo_url"] = get_value("repo_url")
            if get_value("author") is not None:
                data["author"] = get_value("author")
            if get_value("branch") is not None:
                data["branch"] = get_value("branch")

            # Content storage
            if get_value("full_text") is not None:
                data["full_text"] = get_value("full_text")
            if get_value("full_text_path") is not None:
                data["full_text_path"] = get_value("full_text_path")
            if get_value("content_url") is not None:
                data["content_url"] = get_value("content_url")
            if get_value("content_expires_at") is not None:
                # Convert datetime to ISO format string for Supabase
                content_expires = get_value("content_expires_at")
                if isinstance(content_expires, datetime):
                    data["content_expires_at"] = content_expires.isoformat()
                else:
                    data["content_expires_at"] = content_expires

            # Twitter link
            if get_value("twitter_link") is not None:
                data["twitter_link"] = get_value("twitter_link")

            # Processing status
            if get_value("processing_status") is not None:
                processing_status = get_value("processing_status")
                # Handle both enum and string values
                if hasattr(processing_status, "value"):
                    data["processing_status"] = processing_status.value
                else:
                    data["processing_status"] = processing_status

            if not data:
                return await self.get_repository(repo_id)

            result = (
                self.client.table("repositories")
                .update(data)
                .eq("id", str(repo_id))
                .execute()
            )

            if result.data:
                return Repository(**result.data[0])
            return None

        except Exception as e:
            raise Exception(f"Database error updating repository: {str(e)}")

    async def list_repositories(
        self,
        skip: int = 0,
        limit: int = 100,
        author: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[List[RepositoryWithAnalysis], int]:
        """List repositories with pagination and optional filtering"""
        try:
            # Build base query
            query = self.client.table("repositories").select(
                "*, repository_analysis(id, repository_id, analysis_version, total_files_found, total_directories, files_processed, tree_structure, total_lines, total_characters, estimated_tokens, estimated_size_bytes, large_files_skipped, binary_files_skipped, encoding_errors, readme_image_src, ai_summary, description, forked_repo_url, twitter_link)",
                count="exact",
            )

            # Apply author filter if provided
            if author:
                query = query.eq("author", author)

            # Apply status filter if provided
            if status:
                query = query.eq("processing_status", status)

            # Apply search filter if provided (search in name and repo_url)
            if search:
                # Use Supabase text search - search in both name and repo_url
                query = query.or_(f"name.ilike.%{search}%,repo_url.ilike.%{search}%")

            # Apply pagination and ordering
            result = (
                query.order("created_at", desc=True)
                .range(skip, skip + limit - 1)
                .execute()
            )

            if not result.data:
                return [], 0

            repositories = []
            for repo_data in result.data:
                repo_analysis_data = (
                    repo_data["repository_analysis"][0]
                    if repo_data["repository_analysis"]
                    else None
                )

                repository = Repository(**repo_data)

                repo = RepositoryWithAnalysis(
                    id=repository.id,
                    name=repository.name,
                    repo_url=repository.repo_url,
                    author=repository.author,
                    processing_status=repository.processing_status,
                    branch=repository.branch,
                    created_at=repository.created_at,
                    updated_at=repository.updated_at,
                    analysis=(
                        RepositoryAnalysisSummary(**repo_analysis_data)
                        if repo_analysis_data
                        else None
                    ),
                )

                repositories.append(repo)

            total_count = result.count if result.count is not None else 0
            return repositories, total_count

        except Exception as e:
            raise Exception(f"Database error listing repositories: {str(e)}")

    async def delete_repository(self, repo_id: UUID) -> bool:
        """Delete repository (cascades to analysis and documents)"""
        try:
            result = (
                self.client.table("repositories")
                .delete()
                .eq("id", str(repo_id))
                .execute()
            )

            return len(result.data) > 0 if result.data else False

        except Exception as e:
            raise Exception(f"Database error deleting repository: {str(e)}")

    # Repository Analysis operations
    async def create_repository_analysis(
        self, analysis_data: RepositoryAnalysisInsert
    ) -> RepositoryAnalysis:
        """Create repository analysis"""
        try:
            # Create a clean JSON object with only the fields that exist in the schema
            data = {}

            # Generate a new UUID
            data["id"] = str(uuid4())

            # Map repository_id (required field)
            if analysis_data.repository_id:
                data["repository_id"] = str(analysis_data.repository_id)
            else:
                raise ValueError("repository_id is required")

            # Map fields explicitly based on the schema
            # Analysis version
            data["analysis_version"] = analysis_data.analysis_version

            # File processing stats
            if analysis_data.files_processed is not None:
                data["files_processed"] = analysis_data.files_processed
            if analysis_data.binary_files_skipped is not None:
                data["binary_files_skipped"] = analysis_data.binary_files_skipped
            if analysis_data.large_files_skipped is not None:
                data["large_files_skipped"] = analysis_data.large_files_skipped
            if analysis_data.encoding_errors is not None:
                data["encoding_errors"] = analysis_data.encoding_errors

            # Content metrics
            if analysis_data.total_characters is not None:
                data["total_characters"] = analysis_data.total_characters
            if analysis_data.total_lines is not None:
                data["total_lines"] = analysis_data.total_lines
            if analysis_data.total_files_found is not None:
                data["total_files_found"] = analysis_data.total_files_found
            if analysis_data.total_directories is not None:
                data["total_directories"] = analysis_data.total_directories

            # Size estimates
            if analysis_data.estimated_tokens is not None:
                data["estimated_tokens"] = analysis_data.estimated_tokens
            if analysis_data.estimated_size_bytes is not None:
                data["estimated_size_bytes"] = analysis_data.estimated_size_bytes

            # Tree structure
            if analysis_data.tree_structure is not None:
                data["tree_structure"] = analysis_data.tree_structure

            # README image source
            if analysis_data.readme_image_src is not None:
                data["readme_image_src"] = analysis_data.readme_image_src

            # Analysis data as JSON
            if analysis_data.analysis_data is not None:
                data["analysis_data"] = json.dumps(
                    analysis_data.analysis_data, cls=DateTimeEncoder
                )

            result = self.client.table("repository_analysis").insert(data).execute()

            if result.data:
                # Parse JSON string back to dict for Pydantic model
                row_data = result.data[0]
                if isinstance(row_data.get("analysis_data"), str):
                    try:
                        row_data["analysis_data"] = json.loads(
                            row_data["analysis_data"]
                        )
                    except json.JSONDecodeError:
                        # If it's not valid JSON, keep as is
                        pass

                return RepositoryAnalysis(**row_data)
            else:
                raise Exception("Failed to create repository analysis")

        except Exception as e:
            raise Exception(f"Database error creating repository analysis: {str(e)}")

    async def get_latest_repository_analysis(
        self, repo_id: UUID
    ) -> Optional[RepositoryAnalysis]:
        """Get latest repository analysis"""
        try:
            result = (
                self.client.table("repository_analysis")
                .select("*")
                .eq("repository_id", str(repo_id))
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            if result.data:
                # Parse JSON string back to dict for Pydantic model
                row_data = result.data[0]
                if isinstance(row_data.get("analysis_data"), str):
                    try:
                        row_data["analysis_data"] = json.loads(
                            row_data["analysis_data"]
                        )
                    except json.JSONDecodeError:
                        # If it's not valid JSON, keep as is
                        pass

                return RepositoryAnalysis(**row_data)
            return None

        except Exception as e:
            raise Exception(f"Database error getting repository analysis: {str(e)}")

    async def list_repository_analyses(
        self, repo_id: UUID, skip: int = 0, limit: int = 100
    ) -> tuple[List[RepositoryAnalysis], int]:
        """List repository analyses with pagination"""
        try:
            # Build query with count
            query = (
                self.client.table("repository_analysis")
                .select("*", count="exact")
                .eq("repository_id", str(repo_id))
            )

            # Apply pagination and ordering
            result = (
                query.order("created_at", desc=True)
                .range(skip, skip + limit - 1)
                .execute()
            )

            analyses = []
            if result.data:
                for analysis_data in result.data:
                    # Parse JSON string back to dict for Pydantic model
                    if isinstance(analysis_data.get("analysis_data"), str):
                        try:
                            analysis_data["analysis_data"] = json.loads(
                                analysis_data["analysis_data"]
                            )
                        except json.JSONDecodeError:
                            pass
                    analyses.append(RepositoryAnalysis(**analysis_data))

            total_count = result.count if result.count is not None else 0
            return analyses, total_count

        except Exception as e:
            raise Exception(f"Database error listing repository analyses: {str(e)}")

    async def get_repository_analysis(
        self, analysis_id: UUID
    ) -> Optional[RepositoryAnalysis]:
        """Get repository analysis by ID"""
        try:
            result = (
                self.client.table("repository_analysis")
                .select("*")
                .eq("id", str(analysis_id))
                .execute()
            )

            if result.data:
                # Parse JSON string back to dict for Pydantic model
                row_data = result.data[0]
                if isinstance(row_data.get("analysis_data"), str):
                    try:
                        row_data["analysis_data"] = json.loads(
                            row_data["analysis_data"]
                        )
                    except json.JSONDecodeError:
                        pass

                return RepositoryAnalysis(**row_data)
            return None

        except Exception as e:
            raise Exception(f"Database error getting repository analysis: {str(e)}")

    async def get_repository_analysis_without_fork_url(
        self,
    ) -> Optional[RepositoryAnalysis]:
        """Get a repository analysis that doesn't have a forked_repo_url"""
        try:
            result = (
                self.client.table("repository_analysis")
                .select("*")
                .is_("forked_repo_url", "null")
                .limit(1)
                .execute()
            )

            if result.data:
                # Parse JSON string back to dict for Pydantic model
                row_data = result.data[0]
                if isinstance(row_data.get("analysis_data"), str):
                    try:
                        row_data["analysis_data"] = json.loads(
                            row_data["analysis_data"]
                        )
                    except json.JSONDecodeError:
                        pass

                return RepositoryAnalysis(**row_data)
            return None

        except Exception as e:
            raise Exception(
                f"Database error getting repository analysis without fork URL: {str(e)}"
            )

    async def update_repository_analysis(
        self,
        analysis_id: UUID,
        update_data: Union[RepositoryAnalysisUpdate, Dict[str, Any]],
    ) -> Optional[RepositoryAnalysis]:
        """Update repository analysis"""
        try:
            # Create a clean JSON object with only the fields that exist in the schema
            data = {}

            # Extract values from either Dict or Pydantic model
            if isinstance(update_data, Dict):
                source = update_data
                get_value = lambda key: source.get(key)
            else:
                source = update_data
                get_value = lambda key: getattr(source, key, None)

            # Map fields explicitly based on the schema
            if get_value("repository_id") is not None:
                data["repository_id"] = str(get_value("repository_id"))
            if get_value("analysis_version") is not None:
                data["analysis_version"] = get_value("analysis_version")

            # File processing stats
            if get_value("files_processed") is not None:
                data["files_processed"] = get_value("files_processed")
            if get_value("binary_files_skipped") is not None:
                data["binary_files_skipped"] = get_value("binary_files_skipped")
            if get_value("large_files_skipped") is not None:
                data["large_files_skipped"] = get_value("large_files_skipped")
            if get_value("encoding_errors") is not None:
                data["encoding_errors"] = get_value("encoding_errors")

            # Content metrics
            if get_value("total_characters") is not None:
                data["total_characters"] = get_value("total_characters")
            if get_value("total_lines") is not None:
                data["total_lines"] = get_value("total_lines")
            if get_value("total_files_found") is not None:
                data["total_files_found"] = get_value("total_files_found")
            if get_value("total_directories") is not None:
                data["total_directories"] = get_value("total_directories")

            # Size estimates
            if get_value("estimated_tokens") is not None:
                data["estimated_tokens"] = get_value("estimated_tokens")
            if get_value("estimated_size_bytes") is not None:
                data["estimated_size_bytes"] = get_value("estimated_size_bytes")

            # Tree structure
            if get_value("tree_structure") is not None:
                data["tree_structure"] = get_value("tree_structure")

            # README image source
            if get_value("readme_image_src") is not None:
                data["readme_image_src"] = get_value("readme_image_src")

            # Analysis data as JSON
            if get_value("analysis_data") is not None:
                data["analysis_data"] = json.dumps(
                    get_value("analysis_data"), cls=DateTimeEncoder
                )

            if get_value("twitter_link") is not None:
                data["twitter_link"] = get_value("twitter_link")

            if get_value("ai_summary") is not None:
                data["ai_summary"] = get_value("ai_summary")

            if get_value("description") is not None:
                data["description"] = get_value("description")

            if get_value("forked_repo_url") is not None:
                data["forked_repo_url"] = get_value("forked_repo_url")

            if not data:
                return await self.get_repository_analysis(analysis_id)

            result = (
                self.client.table("repository_analysis")
                .update(data)
                .eq("id", str(analysis_id))
                .execute()
            )

            if result.data:
                # Parse JSON string back to dict for Pydantic model
                row_data = result.data[0]
                if isinstance(row_data.get("analysis_data"), str):
                    try:
                        row_data["analysis_data"] = json.loads(
                            row_data["analysis_data"]
                        )
                    except json.JSONDecodeError:
                        pass

                return RepositoryAnalysis(**row_data)
            return None

        except Exception as e:
            raise Exception(f"Database error updating repository analysis: {str(e)}")

    async def delete_repository_analysis(self, analysis_id: UUID) -> bool:
        """Delete repository analysis"""
        try:
            result = (
                self.client.table("repository_analysis")
                .delete()
                .eq("id", str(analysis_id))
                .execute()
            )

            return len(result.data) > 0 if result.data else False

        except Exception as e:
            raise Exception(f"Database error deleting repository analysis: {str(e)}")

    async def get_repository_statistics(
        self, repo_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """Get statistics for repositories and their analyses"""
        try:
            stats = {}

            # Repository statistics
            if repo_id:
                # Statistics for a specific repository
                repo_query = (
                    self.client.table("repositories").select("*").eq("id", str(repo_id))
                )

                analysis_query = (
                    self.client.table("repository_analysis")
                    .select("*")
                    .eq("repository_id", str(repo_id))
                )
            else:
                # Global statistics
                repo_query = self.client.table("repositories").select("*")
                analysis_query = self.client.table("repository_analysis").select("*")

            # Execute queries
            repo_result = repo_query.execute()
            analysis_result = analysis_query.execute()

            # Calculate repository stats
            repositories = repo_result.data if repo_result.data else []
            stats["total_repositories"] = len(repositories)

            if repositories:
                authors = set()
                for repo in repositories:
                    if repo.get("author"):
                        authors.add(repo["author"])
                stats["unique_authors"] = len(authors)
            else:
                stats["unique_authors"] = 0

            # Calculate analysis stats
            analyses = analysis_result.data if analysis_result.data else []
            stats["total_analyses"] = len(analyses)

            if analyses:
                # Aggregate analysis metrics
                total_files = sum(a.get("total_files_found", 0) or 0 for a in analyses)
                total_dirs = sum(a.get("total_directories", 0) or 0 for a in analyses)
                total_lines = sum(a.get("total_lines", 0) or 0 for a in analyses)
                total_chars = sum(a.get("total_characters", 0) or 0 for a in analyses)
                total_tokens = sum(a.get("estimated_tokens", 0) or 0 for a in analyses)
                total_bytes = sum(
                    a.get("estimated_size_bytes", 0) or 0 for a in analyses
                )

                # Processing stats
                files_processed = sum(
                    a.get("files_processed", 0) or 0 for a in analyses
                )
                binary_skipped = sum(
                    a.get("binary_files_skipped", 0) or 0 for a in analyses
                )
                large_skipped = sum(
                    a.get("large_files_skipped", 0) or 0 for a in analyses
                )
                encoding_errors = sum(
                    a.get("encoding_errors", 0) or 0 for a in analyses
                )

                stats.update(
                    {
                        "aggregate_metrics": {
                            "total_files_found": total_files,
                            "total_directories": total_dirs,
                            "total_lines": total_lines,
                            "total_characters": total_chars,
                            "estimated_tokens": total_tokens,
                            "estimated_size_bytes": total_bytes,
                        },
                        "processing_stats": {
                            "files_processed": files_processed,
                            "binary_files_skipped": binary_skipped,
                            "large_files_skipped": large_skipped,
                            "encoding_errors": encoding_errors,
                        },
                    }
                )

                # Latest analysis (for single repo) or average metrics (for global)
                if repo_id and analyses:
                    latest_analysis = max(
                        analyses, key=lambda x: x.get("created_at", "")
                    )
                    stats["latest_analysis"] = {
                        "id": latest_analysis.get("id"),
                        "created_at": latest_analysis.get("created_at"),
                        "analysis_version": latest_analysis.get("analysis_version"),
                    }
                elif not repo_id and analyses:
                    # Calculate averages for global stats
                    count = len(analyses)
                    stats["average_metrics"] = {
                        "avg_files_per_repo": total_files / count,
                        "avg_lines_per_repo": total_lines / count,
                        "avg_tokens_per_repo": total_tokens / count,
                        "avg_size_bytes_per_repo": total_bytes / count,
                    }
            else:
                stats.update(
                    {
                        "aggregate_metrics": {
                            "total_files_found": 0,
                            "total_directories": 0,
                            "total_lines": 0,
                            "total_characters": 0,
                            "estimated_tokens": 0,
                            "estimated_size_bytes": 0,
                        },
                        "processing_stats": {
                            "files_processed": 0,
                            "binary_files_skipped": 0,
                            "large_files_skipped": 0,
                            "encoding_errors": 0,
                        },
                    }
                )

            return stats

        except Exception as e:
            raise Exception(f"Database error getting repository statistics: {str(e)}")

    async def get_repositories_needing_processing(
        self, limit: int = 100
    ) -> List[Repository]:
        """Get repositories that need analysis, AI summary/description, or documents (comprehensive check)"""
        try:
            repositories_needing_processing = []

            # 1. Get repositories without any analysis
            repos_without_analysis = await self.get_repositories_without_analysis(limit)
            repositories_needing_processing.extend(repos_without_analysis)

            # If we've reached the limit, return early
            if len(repositories_needing_processing) >= limit:
                return repositories_needing_processing[:limit]

            # 2. Get repositories with analysis but missing AI summary or description
            remaining_limit = limit - len(repositories_needing_processing)
            repos_needing_ai = (
                await self.get_repositories_needing_ai_summary_or_description(
                    remaining_limit
                )
            )

            # Add repos that aren't already in the list
            existing_repo_ids = {
                str(repo.id) for repo in repositories_needing_processing
            }
            for repo in repos_needing_ai:
                if (
                    str(repo.id) not in existing_repo_ids
                    and len(repositories_needing_processing) < limit
                ):
                    repositories_needing_processing.append(repo)
                    existing_repo_ids.add(str(repo.id))

            # If we've reached the limit, return early
            if len(repositories_needing_processing) >= limit:
                return repositories_needing_processing[:limit]

            # 3. Get repositories with AI summary and description but missing documents
            remaining_limit = limit - len(repositories_needing_processing)
            repos_needing_docs = (
                await self.get_repositories_needing_documents_with_ai_ready(
                    remaining_limit
                )
            )

            # Add repos that aren't already in the list
            for repo in repos_needing_docs:
                if (
                    str(repo.id) not in existing_repo_ids
                    and len(repositories_needing_processing) < limit
                ):
                    repositories_needing_processing.append(repo)
                    existing_repo_ids.add(str(repo.id))

            # If we've reached the limit, return early
            if len(repositories_needing_processing) >= limit:
                return repositories_needing_processing[:limit]

            # 4. Get repositories with orphaned/incomplete documents that need regeneration
            remaining_limit = limit - len(repositories_needing_processing)
            repos_with_orphaned_docs = (
                await self.get_repositories_with_orphaned_documents(remaining_limit)
            )

            # Add repos that aren't already in the list
            for repo in repos_with_orphaned_docs:
                if (
                    str(repo.id) not in existing_repo_ids
                    and len(repositories_needing_processing) < limit
                ):
                    repositories_needing_processing.append(repo)
                    existing_repo_ids.add(str(repo.id))

            return repositories_needing_processing[:limit]

        except Exception as e:
            raise Exception(
                f"Database error getting repositories needing processing: {str(e)}"
            )

    async def get_repositories_without_analysis(
        self, limit: int = 100
    ) -> List[Repository]:
        """Get repositories that don't have any repository analysis"""
        try:
            # First get all repository IDs that have analysis
            analysis_result = (
                self.client.table("repository_analysis")
                .select("repository_id")
                .execute()
            )

            analyzed_repo_ids = []
            if analysis_result.data:
                analyzed_repo_ids = [
                    row["repository_id"] for row in analysis_result.data
                ]

            # Then get repositories not in that list
            query = self.client.table("repositories").select("*")

            if analyzed_repo_ids:
                query = query.not_.in_("id", analyzed_repo_ids)

            result = (
                query.order("created_at", desc=False)  # Process oldest first
                .limit(limit)
                .execute()
            )

            repositories = []
            if result.data:
                for repo in result.data:
                    repositories.append(Repository(**repo))

            return repositories

        except Exception as e:
            raise Exception(
                f"Database error getting repositories without analysis: {str(e)}"
            )

    async def get_repositories_without_documents(
        self, limit: int = 100
    ) -> List[Repository]:
        """Get repositories that don't have any documents (via their latest analysis)"""
        try:
            # Get all repositories with their latest analysis that have documents
            docs_result = (
                self.client.table("documents")
                .select("repository_analysis_id")
                .execute()
            )

            documented_analysis_ids = []
            if docs_result.data:
                documented_analysis_ids = [
                    row["repository_analysis_id"] for row in docs_result.data
                ]

            # Get repository IDs from analyses that have documents
            documented_repo_ids = []
            if documented_analysis_ids:
                analysis_result = (
                    self.client.table("repository_analysis")
                    .select("repository_id")
                    .in_("id", documented_analysis_ids)
                    .execute()
                )

                if analysis_result.data:
                    documented_repo_ids = [
                        row["repository_id"] for row in analysis_result.data
                    ]

            # Then get repositories not in that list
            query = self.client.table("repositories").select("*")

            if documented_repo_ids:
                query = query.not_.in_("id", documented_repo_ids)

            result = (
                query.order("created_at", desc=False)  # Process oldest first
                .limit(limit)
                .execute()
            )

            repositories = []
            if result.data:
                for repo in result.data:
                    repositories.append(Repository(**repo))

            return repositories

        except Exception as e:
            raise Exception(
                f"Database error getting repositories without documents: {str(e)}"
            )

    # Document operations
    async def create_document(self, doc_data: DocumentInsert) -> Document:
        """Create a new document"""

        import logging

        logger = logging.getLogger(__name__)

        try:
            # Create a clean JSON object with only the fields that exist in the schema
            data = {}

            # Generate a new UUID
            data["id"] = str(uuid4())

            # Map repository_analysis_id (required field)
            if doc_data.repository_analysis_id:
                data["repository_analysis_id"] = str(doc_data.repository_analysis_id)
            else:
                raise ValueError("repository_analysis_id is required")

            # Map document metadata fields (required fields)
            if doc_data.document_type:
                data["document_type"] = doc_data.document_type
            else:
                raise ValueError("document_type is required")

            if doc_data.title:
                data["title"] = doc_data.title
            else:
                raise ValueError("title is required")

            # Document content (required)
            if doc_data.content:
                data["content"] = doc_data.content
            else:
                raise ValueError("content is required")

            # Optional fields
            if doc_data.description is not None:
                data["description"] = doc_data.description

            # Generation metadata
            if doc_data.generated_by is not None:
                data["generated_by"] = doc_data.generated_by
            if doc_data.generation_prompt is not None:
                data["generation_prompt"] = doc_data.generation_prompt
            if doc_data.model_used is not None:
                data["model_used"] = doc_data.model_used

            # Version control
            if doc_data.version is not None:
                data["version"] = doc_data.version
            if doc_data.is_current is not None:
                data["is_current"] = doc_data.is_current
            if doc_data.parent_document_id is not None:
                data["parent_document_id"] = str(doc_data.parent_document_id)

            # Additional metadata as JSON
            if doc_data.metadata is not None:
                data["metadata"] = json.dumps(doc_data.metadata, cls=DateTimeEncoder)

            logger.info(f"Creating document: {data.keys()}")

            if "repository_id" in data:
                logger.info(
                    f"Removing repository_id from data: {data['repository_id']}"
                )
                data.pop("repository_id")

            result = self.client.table("documents").insert(data).execute()

            if result.data:
                # Parse JSON string back to dict for Pydantic model
                row_data = result.data[0]
                if isinstance(row_data.get("metadata"), str):
                    try:
                        row_data["metadata"] = json.loads(row_data["metadata"])
                    except json.JSONDecodeError:
                        # If it's not valid JSON, keep as is
                        pass

                return Document(**row_data)
            else:
                raise Exception("Failed to create document")

        except Exception as e:
            raise Exception(f"Database error creating document: {str(e)}")

    async def get_documents_by_repository_analysis(
        self, analysis_id: UUID, document_type: Optional[str] = None
    ) -> List[Document]:
        """Get documents by repository analysis ID"""
        try:
            query = (
                self.client.table("documents")
                .select("*")
                .eq("repository_analysis_id", str(analysis_id))
            )

            if document_type:
                query = query.eq("document_type", document_type)

            result = query.order("created_at", desc=True).execute()

            documents = []
            if result.data:
                for doc in result.data:
                    # Parse JSON string back to dict for Pydantic model
                    if isinstance(doc.get("metadata"), str):
                        try:
                            doc["metadata"] = json.loads(doc["metadata"])
                        except json.JSONDecodeError:
                            # If it's not valid JSON, keep as is
                            pass
                    documents.append(Document(**doc))
            return documents

        except Exception as e:
            raise Exception(f"Database error getting documents: {str(e)}")

    async def get_documents_by_repository(
        self, repo_id: UUID, document_type: Optional[str] = None
    ) -> List[Document]:
        """Get documents by repository ID (via latest analysis)"""
        try:
            # Get the latest repository analysis
            latest_analysis = await self.get_latest_repository_analysis(repo_id)
            if not latest_analysis:
                return []

            # Get documents for the latest analysis
            return await self.get_documents_by_repository_analysis(
                latest_analysis.id, document_type
            )

        except Exception as e:
            raise Exception(f"Database error getting documents by repository: {str(e)}")

    async def get_current_documents_by_analysis(
        self, analysis_id: UUID
    ) -> List[Document]:
        """Get current documents for a repository analysis"""
        try:
            result = (
                self.client.table("documents")
                .select("*")
                .eq("repository_analysis_id", str(analysis_id))
                .eq("is_current", True)
                .order("created_at", desc=True)
                .execute()
            )

            documents = []
            if result.data:
                for doc in result.data:
                    # Parse JSON string back to dict for Pydantic model
                    if isinstance(doc.get("metadata"), str):
                        try:
                            doc["metadata"] = json.loads(doc["metadata"])
                        except json.JSONDecodeError:
                            # If it's not valid JSON, keep as is
                            pass
                    documents.append(Document(**doc))
            return documents

        except Exception as e:
            raise Exception(f"Database error getting current documents: {str(e)}")

    async def get_current_documents(self, repo_id: UUID) -> List[Document]:
        """Get current documents for a repository (via latest analysis)"""
        try:
            # Get the latest repository analysis
            latest_analysis = await self.get_latest_repository_analysis(repo_id)
            if not latest_analysis:
                return []

            # Get current documents for the latest analysis
            return await self.get_current_documents_by_analysis(latest_analysis.id)

        except Exception as e:
            raise Exception(
                f"Database error getting current documents by repository: {str(e)}"
            )

    # Helper method to get current AI summary
    async def get_current_ai_summary_by_analysis(
        self, analysis_id: UUID
    ) -> Optional[Document]:
        """Get current AI summary for a repository analysis"""
        try:
            result = (
                self.client.table("documents")
                .select("*")
                .eq("repository_analysis_id", str(analysis_id))
                .eq("document_type", "ai_summary")
                .eq("is_current", True)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )

            if result.data:
                # Parse JSON string back to dict for Pydantic model
                row_data = result.data[0]
                if isinstance(row_data.get("metadata"), str):
                    try:
                        row_data["metadata"] = json.loads(row_data["metadata"])
                    except json.JSONDecodeError:
                        # If it's not valid JSON, keep as is
                        pass

                return Document(**row_data)
            return None

        except Exception as e:
            raise Exception(f"Database error getting current AI summary: {str(e)}")

    async def get_current_ai_summary(self, repo_id: UUID) -> Optional[Document]:
        """Get current AI summary for a repository (via latest analysis)"""
        try:
            # Get the latest repository analysis
            latest_analysis = await self.get_latest_repository_analysis(repo_id)
            if not latest_analysis:
                return None

            # Get current AI summary for the latest analysis
            return await self.get_current_ai_summary_by_analysis(latest_analysis.id)

        except Exception as e:
            raise Exception(
                f"Database error getting current AI summary by repository: {str(e)}"
            )

    async def mark_previous_documents_not_current_by_analysis(
        self, analysis_id: UUID, document_type: str
    ) -> None:
        """Mark all previous documents of a specific type as not current for a repository analysis"""
        try:
            self.client.table("documents").update({"is_current": False}).eq(
                "repository_analysis_id", str(analysis_id)
            ).eq("document_type", document_type).execute()
        except Exception as e:
            raise Exception(f"Database error updating previous documents: {str(e)}")

    async def mark_previous_documents_not_current(
        self, repo_id: UUID, document_type: str
    ) -> None:
        """Mark all previous documents of a specific type as not current (via latest analysis)"""
        try:
            # Get the latest repository analysis
            latest_analysis = await self.get_latest_repository_analysis(repo_id)
            if not latest_analysis:
                return  # No analysis exists, nothing to mark

            # Mark previous documents as not current for the latest analysis
            await self.mark_previous_documents_not_current_by_analysis(
                latest_analysis.id, document_type
            )
        except Exception as e:
            raise Exception(
                f"Database error updating previous documents by repository: {str(e)}"
            )

    # Batch processing operations
    async def create_batch_processing(
        self, batch_data: BatchProcessingInsert
    ) -> BatchProcessing:
        """Create a new batch processing entry"""
        try:
            # Create a clean JSON object with only the fields that exist in the schema
            data = {}

            # Generate a new UUID
            data["id"] = str(uuid4())

            # Map required fields
            if batch_data.batch_name:
                data["batch_name"] = batch_data.batch_name
            else:
                raise ValueError("batch_name is required")

            if batch_data.total_repositories is not None:
                data["total_repositories"] = batch_data.total_repositories
            else:
                raise ValueError("total_repositories is required")

            # Map optional fields with defaults
            data["processed_repositories"] = batch_data.processed_repositories or 0
            data["successful_repositories"] = batch_data.successful_repositories or 0
            data["failed_repositories"] = batch_data.failed_repositories or 0
            data["status"] = batch_data.status or "pending"

            # Handle arrays as JSON
            if batch_data.repository_ids is not None:
                data["repository_ids"] = json.dumps(batch_data.repository_ids)
            else:
                data["repository_ids"] = json.dumps([])

            if batch_data.task_ids is not None:
                data["task_ids"] = json.dumps(batch_data.task_ids)
            else:
                data["task_ids"] = json.dumps([])

            # Optional fields
            if batch_data.error_message is not None:
                data["error_message"] = batch_data.error_message
            if batch_data.started_at is not None:
                if isinstance(batch_data.started_at, datetime):
                    data["started_at"] = batch_data.started_at.isoformat()
                else:
                    data["started_at"] = batch_data.started_at
            if batch_data.completed_at is not None:
                if isinstance(batch_data.completed_at, datetime):
                    data["completed_at"] = batch_data.completed_at.isoformat()
                else:
                    data["completed_at"] = batch_data.completed_at

            result = self.client.table("batch_processing").insert(data).execute()

            if result.data:
                # Parse JSON strings back to lists for Pydantic model
                row_data = result.data[0]
                if isinstance(row_data.get("repository_ids"), str):
                    try:
                        row_data["repository_ids"] = json.loads(
                            row_data["repository_ids"]
                        )
                    except json.JSONDecodeError:
                        row_data["repository_ids"] = []
                if isinstance(row_data.get("task_ids"), str):
                    try:
                        row_data["task_ids"] = json.loads(row_data["task_ids"])
                    except json.JSONDecodeError:
                        row_data["task_ids"] = []

                return BatchProcessing(**row_data)
            else:
                raise Exception("Failed to create batch processing")

        except Exception as e:
            raise Exception(f"Database error creating batch processing: {str(e)}")

    async def get_batch_processing(self, batch_id: UUID) -> Optional[BatchProcessing]:
        """Get batch processing by ID"""
        try:
            result = (
                self.client.table("batch_processing")
                .select("*")
                .eq("id", str(batch_id))
                .execute()
            )

            if result.data:
                # Parse JSON strings back to lists for Pydantic model
                row_data = result.data[0]
                if isinstance(row_data.get("repository_ids"), str):
                    try:
                        row_data["repository_ids"] = json.loads(
                            row_data["repository_ids"]
                        )
                    except json.JSONDecodeError:
                        row_data["repository_ids"] = []
                if isinstance(row_data.get("task_ids"), str):
                    try:
                        row_data["task_ids"] = json.loads(row_data["task_ids"])
                    except json.JSONDecodeError:
                        row_data["task_ids"] = []

                return BatchProcessing(**row_data)
            return None

        except Exception as e:
            raise Exception(f"Database error getting batch processing: {str(e)}")

    async def update_batch_processing(
        self, batch_id: UUID, update_data: Union[BatchProcessingUpdate, Dict[str, Any]]
    ) -> Optional[BatchProcessing]:
        """Update batch processing"""
        try:
            # Create a clean JSON object with only the fields that exist in the schema
            data = {}

            # Extract values from either Dict or Pydantic model
            if isinstance(update_data, Dict):
                source = update_data
                get_value = lambda key: source.get(key)
            else:
                source = update_data
                get_value = lambda key: getattr(source, key, None)

            # Map fields explicitly
            if get_value("batch_name") is not None:
                data["batch_name"] = get_value("batch_name")
            if get_value("total_repositories") is not None:
                data["total_repositories"] = get_value("total_repositories")
            if get_value("processed_repositories") is not None:
                data["processed_repositories"] = get_value("processed_repositories")
            if get_value("successful_repositories") is not None:
                data["successful_repositories"] = get_value("successful_repositories")
            if get_value("failed_repositories") is not None:
                data["failed_repositories"] = get_value("failed_repositories")
            if get_value("status") is not None:
                data["status"] = str(get_value("status"))
            if get_value("error_message") is not None:
                data["error_message"] = get_value("error_message")

            # Handle arrays as JSON
            if get_value("repository_ids") is not None:
                data["repository_ids"] = json.dumps(get_value("repository_ids"))
            if get_value("task_ids") is not None:
                data["task_ids"] = json.dumps(get_value("task_ids"))

            # Handle datetime fields
            if get_value("started_at") is not None:
                started_at = get_value("started_at")
                if isinstance(started_at, datetime):
                    data["started_at"] = started_at.isoformat()
                else:
                    data["started_at"] = started_at
            if get_value("completed_at") is not None:
                completed_at = get_value("completed_at")
                if isinstance(completed_at, datetime):
                    data["completed_at"] = completed_at.isoformat()
                else:
                    data["completed_at"] = completed_at

            if not data:
                return await self.get_batch_processing(batch_id)

            result = (
                self.client.table("batch_processing")
                .update(data)
                .eq("id", str(batch_id))
                .execute()
            )

            if result.data:
                # Parse JSON strings back to lists for Pydantic model
                row_data = result.data[0]
                if isinstance(row_data.get("repository_ids"), str):
                    try:
                        row_data["repository_ids"] = json.loads(
                            row_data["repository_ids"]
                        )
                    except json.JSONDecodeError:
                        row_data["repository_ids"] = []
                if isinstance(row_data.get("task_ids"), str):
                    try:
                        row_data["task_ids"] = json.loads(row_data["task_ids"])
                    except json.JSONDecodeError:
                        row_data["task_ids"] = []

                return BatchProcessing(**row_data)
            return None

        except Exception as e:
            raise Exception(f"Database error updating batch processing: {str(e)}")

    async def list_batch_processing(
        self, skip: int = 0, limit: int = 100, status: Optional[str] = None
    ) -> tuple[List[BatchProcessing], int]:
        """List batch processing entries with pagination"""
        try:
            # Build base query
            query = self.client.table("batch_processing").select("*", count="exact")

            # Apply status filter if provided
            if status:
                query = query.eq("status", status)

            # Apply pagination and ordering
            result = (
                query.order("created_at", desc=True)
                .range(skip, skip + limit - 1)
                .execute()
            )

            batches = []
            if result.data:
                for batch_data in result.data:
                    # Parse JSON strings back to lists for Pydantic model
                    if isinstance(batch_data.get("repository_ids"), str):
                        try:
                            batch_data["repository_ids"] = json.loads(
                                batch_data["repository_ids"]
                            )
                        except json.JSONDecodeError:
                            batch_data["repository_ids"] = []
                    if isinstance(batch_data.get("task_ids"), str):
                        try:
                            batch_data["task_ids"] = json.loads(batch_data["task_ids"])
                        except json.JSONDecodeError:
                            batch_data["task_ids"] = []
                    batches.append(BatchProcessing(**batch_data))

            total_count = result.count if result.count is not None else 0
            return batches, total_count

        except Exception as e:
            raise Exception(f"Database error listing batch processing: {str(e)}")

    # Twitter posting operations
    async def get_repositories_without_twitter_links(
        self, limit: int = 50
    ) -> List[Repository]:
        """Get repositories that have forked_repo_url but don't have Twitter links"""
        try:
            # Get all repositories first
            all_repos_result = (
                self.client.table("repositories")
                .select("*")
                .order("created_at", desc=False)  # Oldest first
                .execute()
            )

            if not all_repos_result.data:
                return []

            repositories_without_links = []

            for repo_data in all_repos_result.data:
                repo_id = repo_data["id"]

                # Check if this repository has analysis with forked_repo_url but no twitter_link
                analysis_result = (
                    self.client.table("repository_analysis")
                    .select("twitter_link, forked_repo_url")
                    .eq("repository_id", repo_id)
                    .not_.is_("forked_repo_url", "null")  # Must have forked repo URL
                    .limit(1)
                    .execute()
                )

                # If repository has forked_repo_url, check if it needs Twitter posting
                if analysis_result.data:
                    analysis = analysis_result.data[0]
                    # Only include if it has forked_repo_url but no twitter_link
                    if analysis.get("forked_repo_url") and not analysis.get(
                        "twitter_link"
                    ):
                        repositories_without_links.append(Repository(**repo_data))

                        # Stop if we've reached the limit
                        if len(repositories_without_links) >= limit:
                            break

            return repositories_without_links

        except Exception as e:
            raise Exception(
                f"Database error getting repositories without Twitter links: {str(e)}"
            )

    # Prompt operations
    async def create_prompt(self, prompt_data: PromptInsert) -> Prompt:
        """Create a new prompt"""
        try:
            # Create a clean JSON object with only the fields that exist in the schema
            data = {}

            # Generate a new UUID
            data["id"] = str(uuid4())

            # Map required fields
            if prompt_data.name:
                data["name"] = prompt_data.name
            else:
                raise ValueError("name is required")

            if prompt_data.type:
                data["type"] = prompt_data.type.value
            else:
                raise ValueError("type is required")

            if prompt_data.content:
                data["content"] = prompt_data.content
            else:
                raise ValueError("content is required")

            # Map optional fields
            data["version"] = prompt_data.version
            data["is_active"] = prompt_data.is_active
            if prompt_data.description is not None:
                data["description"] = prompt_data.description
            if prompt_data.metadata is not None:
                data["metadata"] = json.dumps(prompt_data.metadata, cls=DateTimeEncoder)

            result = self.client.table("prompts").insert(data).execute()

            if result.data:
                # Parse JSON string back to dict for Pydantic model
                row_data = result.data[0]
                if isinstance(row_data.get("metadata"), str):
                    try:
                        row_data["metadata"] = json.loads(row_data["metadata"])
                    except json.JSONDecodeError:
                        row_data["metadata"] = {}
                return Prompt(**row_data)
            else:
                raise Exception("Failed to create prompt")

        except Exception as e:
            raise Exception(f"Database error creating prompt: {str(e)}")

    async def get_prompt(self, prompt_id: UUID) -> Optional[Prompt]:
        """Get prompt by ID"""
        try:
            result = (
                self.client.table("prompts")
                .select("*")
                .eq("id", str(prompt_id))
                .execute()
            )

            if result.data:
                # Parse JSON string back to dict for Pydantic model
                row_data = result.data[0]
                if isinstance(row_data.get("metadata"), str):
                    try:
                        row_data["metadata"] = json.loads(row_data["metadata"])
                    except json.JSONDecodeError:
                        row_data["metadata"] = {}
                return Prompt(**row_data)
            return None

        except Exception as e:
            raise Exception(f"Database error getting prompt: {str(e)}")

    async def get_prompt_by_name_and_type(
        self, name: str, type: str
    ) -> Optional[Prompt]:
        """Get active prompt by name and type"""
        try:
            result = (
                self.client.table("prompts")
                .select("*")
                .eq("name", name)
                .eq("type", type)
                .eq("is_active", True)
                .execute()
            )

            if result.data:
                # Parse JSON string back to dict for Pydantic model
                row_data = result.data[0]
                if isinstance(row_data.get("metadata"), str):
                    try:
                        row_data["metadata"] = json.loads(row_data["metadata"])
                    except json.JSONDecodeError:
                        row_data["metadata"] = {}
                return Prompt(**row_data)
            return None

        except Exception as e:
            raise Exception(f"Database error getting prompt by name and type: {str(e)}")

    async def update_prompt(
        self, prompt_id: UUID, update_data: Union[PromptUpdate, Dict[str, Any]]
    ) -> Optional[Prompt]:
        """Update prompt"""
        try:
            # Create a clean JSON object with only the fields that exist in the schema
            data = {}

            # Extract values from either Dict or Pydantic model
            if isinstance(update_data, Dict):
                source = update_data
                get_value = lambda key: source.get(key)
            else:
                source = update_data
                get_value = lambda key: getattr(source, key, None)

            # Map fields explicitly
            if get_value("name") is not None:
                data["name"] = get_value("name")
            if get_value("type") is not None:
                prompt_type = get_value("type")
                data["type"] = (
                    prompt_type.value if hasattr(prompt_type, "value") else prompt_type
                )
            if get_value("content") is not None:
                data["content"] = get_value("content")
            if get_value("version") is not None:
                data["version"] = get_value("version")
            if get_value("is_active") is not None:
                data["is_active"] = get_value("is_active")
            if get_value("description") is not None:
                data["description"] = get_value("description")
            if get_value("metadata") is not None:
                data["metadata"] = json.dumps(
                    get_value("metadata"), cls=DateTimeEncoder
                )

            if not data:
                return await self.get_prompt(prompt_id)

            result = (
                self.client.table("prompts")
                .update(data)
                .eq("id", str(prompt_id))
                .execute()
            )

            if result.data:
                # Parse JSON string back to dict for Pydantic model
                row_data = result.data[0]
                if isinstance(row_data.get("metadata"), str):
                    try:
                        row_data["metadata"] = json.loads(row_data["metadata"])
                    except json.JSONDecodeError:
                        row_data["metadata"] = {}
                return Prompt(**row_data)
            return None

        except Exception as e:
            raise Exception(f"Database error updating prompt: {str(e)}")

    async def list_prompts(
        self, skip: int = 0, limit: int = 100, type: Optional[str] = None
    ) -> tuple[List[Prompt], int]:
        """List prompts with pagination and optional filtering by type"""
        try:
            # Build base query
            query = self.client.table("prompts").select("*", count="exact")

            # Apply type filter if provided
            if type:
                query = query.eq("type", type)

            # Apply pagination and ordering
            result = (
                query.order("created_at", desc=True)
                .range(skip, skip + limit - 1)
                .execute()
            )

            prompts = []
            if result.data:
                for prompt_data in result.data:
                    # Parse JSON string back to dict for Pydantic model
                    if isinstance(prompt_data.get("metadata"), str):
                        try:
                            prompt_data["metadata"] = json.loads(
                                prompt_data["metadata"]
                            )
                        except json.JSONDecodeError:
                            prompt_data["metadata"] = {}
                    prompts.append(Prompt(**prompt_data))

            total_count = result.count if result.count is not None else 0
            return prompts, total_count

        except Exception as e:
            raise Exception(f"Database error listing prompts: {str(e)}")

    async def get_system_prompt(
        self, prompt_type: str, prompt_name: str = "default"
    ) -> Optional[str]:
        """Get system prompt content by type and name"""
        try:
            prompt = await self.get_prompt_by_name_and_type(prompt_name, prompt_type)
            return prompt.content if prompt else None
        except Exception as e:
            raise Exception(f"Database error getting system prompt: {str(e)}")

    # Helper methods for batch processing to check what needs to be generated
    async def get_repositories_needing_ai_summary_or_description(
        self, limit: int = 100
    ) -> List[Repository]:
        """Get repositories with analysis but missing AI summary or description"""
        try:
            # Get repositories that have analysis but are missing ai_summary or description
            result = (
                self.client.table("repository_analysis")
                .select("repository_id, ai_summary, description")
                .order("created_at", desc=False)
                .execute()
            )

            repos_needing_ai_generation = []
            seen_repo_ids = set()

            if result.data:
                for analysis in result.data:
                    repo_id = analysis["repository_id"]

                    # Skip if we've already processed this repository
                    if repo_id in seen_repo_ids:
                        continue
                    seen_repo_ids.add(repo_id)

                    # Check if ai_summary or description is missing/None
                    needs_ai_summary = not analysis.get("ai_summary")
                    needs_description = not analysis.get("description")

                    if needs_ai_summary or needs_description:
                        # Get the repository details
                        repo_result = (
                            self.client.table("repositories")
                            .select("*")
                            .eq("id", repo_id)
                            .limit(1)
                            .execute()
                        )

                        if repo_result.data:
                            repos_needing_ai_generation.append(
                                Repository(**repo_result.data[0])
                            )

                            if len(repos_needing_ai_generation) >= limit:
                                break

            return repos_needing_ai_generation

        except Exception as e:
            raise Exception(
                f"Database error getting repositories needing AI generation: {str(e)}"
            )

    async def get_repositories_needing_documents_with_ai_ready(
        self, limit: int = 100
    ) -> List[Repository]:
        """Get repositories that have AI summary and description but are missing documents"""
        try:
            # Get all repository analysis that have both ai_summary and description
            analysis_result = (
                self.client.table("repository_analysis")
                .select("repository_id, id, ai_summary, description")
                .not_.is_("ai_summary", "null")
                .not_.is_("description", "null")
                .order("created_at", desc=False)
                .execute()
            )

            if not analysis_result.data:
                return []

            # Get all analysis IDs that have documents
            docs_result = (
                self.client.table("documents")
                .select("repository_analysis_id")
                .execute()
            )

            documented_analysis_ids = set()
            if docs_result.data:
                documented_analysis_ids = {
                    row["repository_analysis_id"] for row in docs_result.data
                }

            repos_needing_docs = []
            seen_repo_ids = set()

            for analysis in analysis_result.data:
                repo_id = analysis["repository_id"]
                analysis_id = analysis["id"]

                # Skip if we've already processed this repository or if it has documents
                if repo_id in seen_repo_ids or analysis_id in documented_analysis_ids:
                    continue
                seen_repo_ids.add(repo_id)

                # Check if both ai_summary and description exist and are not empty
                has_ai_summary = (
                    analysis.get("ai_summary") and analysis["ai_summary"].strip()
                )
                has_description = (
                    analysis.get("description") and analysis["description"].strip()
                )

                if has_ai_summary and has_description:
                    # Get the repository details
                    repo_result = (
                        self.client.table("repositories")
                        .select("*")
                        .eq("id", repo_id)
                        .limit(1)
                        .execute()
                    )

                    if repo_result.data:
                        repos_needing_docs.append(Repository(**repo_result.data[0]))

                        if len(repos_needing_docs) >= limit:
                            break

            return repos_needing_docs

        except Exception as e:
            raise Exception(
                f"Database error getting repositories needing documents: {str(e)}"
            )

    async def get_repositories_with_orphaned_documents(
        self, limit: int = 100
    ) -> List[Repository]:
        """Get repositories that have documents but missing or incomplete repository analysis"""
        try:
            # Get all documents and their analysis IDs
            docs_result = (
                self.client.table("documents")
                .select("repository_analysis_id")
                .execute()
            )

            if not docs_result.data:
                return []

            # Get unique analysis IDs from documents
            analysis_ids_in_docs = list(
                set(row["repository_analysis_id"] for row in docs_result.data)
            )

            # Check which of these analysis IDs actually exist in repository_analysis table
            analysis_result = (
                self.client.table("repository_analysis")
                .select("id, repository_id, tree_structure")
                .in_("id", analysis_ids_in_docs)
                .execute()
            )

            existing_analysis_ids = set()
            incomplete_analysis_repo_ids = set()
            existing_repo_ids = set()

            if analysis_result.data:
                for analysis in analysis_result.data:
                    analysis_id = analysis["id"]
                    repo_id = analysis["repository_id"]
                    tree_structure = analysis.get("tree_structure")

                    existing_analysis_ids.add(analysis_id)
                    existing_repo_ids.add(repo_id)

                    # Check if analysis is incomplete (missing tree_structure)
                    if not tree_structure:
                        incomplete_analysis_repo_ids.add(repo_id)

            # Find analysis IDs that are referenced in documents but don't exist
            orphaned_analysis_ids = set(analysis_ids_in_docs) - existing_analysis_ids

            # Get repository IDs for orphaned analyses (if any exist in some other table)
            orphaned_repo_ids = set()
            if orphaned_analysis_ids:
                # We can't easily map orphaned analysis IDs to repo IDs without the analysis records
                # So we'll find repositories that might have been affected
                logger.warning(
                    f"Found {len(orphaned_analysis_ids)} orphaned analysis IDs in documents"
                )

            # Combine repo IDs that need regeneration: those with incomplete analysis
            repo_ids_needing_regen = incomplete_analysis_repo_ids

            # Get repository details for repos that need regeneration
            repositories_needing_regen = []

            if repo_ids_needing_regen:
                repos_result = (
                    self.client.table("repositories")
                    .select("*")
                    .in_("id", list(repo_ids_needing_regen))
                    .order("created_at", desc=False)
                    .limit(limit)
                    .execute()
                )

                if repos_result.data:
                    for repo_data in repos_result.data:
                        repositories_needing_regen.append(Repository(**repo_data))

            return repositories_needing_regen[:limit]

        except Exception as e:
            raise Exception(
                f"Database error getting repositories with orphaned documents: {str(e)}"
            )

    # Bulk operations for performance optimization
    async def get_latest_repository_analyses_bulk(
        self, repo_ids: List[UUID]
    ) -> Dict[UUID, Optional[RepositoryAnalysis]]:
        """Get latest analyses for multiple repositories in one query"""
        try:
            if not repo_ids:
                return {}

            # Convert UUIDs to strings for Supabase query
            str_repo_ids = [str(repo_id) for repo_id in repo_ids]

            # Get all analyses for these repositories, ordered by creation date
            result = (
                self.client.table("repository_analysis")
                .select("*")
                .in_("repository_id", str_repo_ids)
                .order("created_at", desc=True)
                .execute()
            )

            # Group analyses by repository_id and take the latest (first) one for each
            analyses_dict = {}

            # Initialize with None for all requested repo_ids
            for repo_id in repo_ids:
                analyses_dict[repo_id] = None

            if result.data:
                for row_data in result.data:
                    repo_id = UUID(row_data["repository_id"])

                    # Only keep the first (latest) analysis for each repository
                    if repo_id in analyses_dict and analyses_dict[repo_id] is None:
                        # Parse JSON string back to dict for Pydantic model
                        if isinstance(row_data.get("analysis_data"), str):
                            try:
                                row_data["analysis_data"] = json.loads(
                                    row_data["analysis_data"]
                                )
                            except json.JSONDecodeError:
                                pass

                        analyses_dict[repo_id] = RepositoryAnalysis(**row_data)

            return analyses_dict

        except Exception as e:
            raise Exception(
                f"Database error getting latest repository analyses bulk: {str(e)}"
            )

    async def get_documents_by_analysis_ids_bulk(
        self, analysis_ids: List[UUID]
    ) -> List[Document]:
        """Get all documents for multiple analysis IDs in one query"""
        try:
            if not analysis_ids:
                return []

            # Convert UUIDs to strings for Supabase query
            str_analysis_ids = [str(analysis_id) for analysis_id in analysis_ids]

            result = (
                self.client.table("documents")
                .select("*")
                .in_("repository_analysis_id", str_analysis_ids)
                .execute()
            )

            documents = []
            if result.data:
                for row_data in result.data:
                    # Parse JSON metadata if it exists
                    if isinstance(row_data.get("metadata"), str):
                        try:
                            row_data["metadata"] = json.loads(row_data["metadata"])
                        except json.JSONDecodeError:
                            pass

                    documents.append(Document(**row_data))

            return documents

        except Exception as e:
            raise Exception(
                f"Database error getting documents by analysis IDs bulk: {str(e)}"
            )


# Global database service instance
db_service = DatabaseService()


# Dependency function for FastAPI
async def get_database_service() -> DatabaseService:
    """FastAPI dependency to get database service"""
    return db_service
