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

            result = self.client.table("repositories").insert(data).execute()

            if result.data:
                return Repository(**result.data[0])
            else:
                raise Exception("Failed to create repository")

        except Exception as e:
            raise Exception(f"Database error creating repository: {str(e)}")

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

    # Document operations
    async def create_document(self, doc_data: DocumentInsert) -> Document:
        """Create a new document"""
        try:
            # Create a clean JSON object with only the fields that exist in the schema
            data = {}

            # Generate a new UUID
            data["id"] = str(uuid4())

            # Map repository_id (required field)
            if doc_data.repository_id:
                data["repository_id"] = str(doc_data.repository_id)
            else:
                raise ValueError("repository_id is required")

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

    async def get_documents_by_repository(
        self, repo_id: UUID, document_type: Optional[str] = None
    ) -> List[Document]:
        """Get documents by repository ID"""
        try:
            query = (
                self.client.table("documents")
                .select("*")
                .eq("repository_id", str(repo_id))
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

    async def get_current_documents(self, repo_id: UUID) -> List[Document]:
        """Get current documents for a repository"""
        try:
            result = (
                self.client.table("documents")
                .select("*")
                .eq("repository_id", str(repo_id))
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

    # Helper method to get current AI summary
    async def get_current_ai_summary(self, repo_id: UUID) -> Optional[Document]:
        """Get current AI summary for a repository"""
        try:
            result = (
                self.client.table("documents")
                .select("*")
                .eq("repository_id", str(repo_id))
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

    async def mark_previous_documents_not_current(
        self, repo_id: UUID, document_type: str
    ) -> None:
        """Mark all previous documents of a specific type as not current"""
        try:
            self.client.table("documents").update({"is_current": False}).eq(
                "repository_id", str(repo_id)
            ).eq("document_type", document_type).execute()
        except Exception as e:
            raise Exception(f"Database error updating previous documents: {str(e)}")


# Global database service instance
db_service = DatabaseService()


# Dependency function for FastAPI
async def get_database_service() -> DatabaseService:
    """FastAPI dependency to get database service"""
    return db_service
