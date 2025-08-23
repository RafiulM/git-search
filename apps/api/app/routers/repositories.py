from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.repository import (
    RepositoryResponse,
    RepositoryProcessingStatus,
    RepositoryWithAnalysis,
    RepositoryAnalysisSummary,
)
from app.models.repository_analysis import RepositoryAnalysisResponse
from app.models.document import DocumentResponse, DocumentSummary
from app.services.database import get_database_service, DatabaseService
from app.services.auth import require_api_key

router = APIRouter(
    prefix="/repositories",
    tags=["repositories"],
    dependencies=[Depends(require_api_key)],
)


@router.get(
    "",
    response_model=dict,
    summary="List Repositories",
    description="Get paginated list of repositories with optional filtering and analysis data",
    response_description="Paginated list of repositories with optional analysis and document counts",
)
async def list_repositories(
    skip: int = Query(default=0, ge=0, description="Number of items to skip"),
    limit: int = Query(
        default=10, ge=1, le=100, description="Number of items to return"
    ),
    author: Optional[str] = Query(
        default=None, description="Filter by repository author"
    ),
    status: Optional[RepositoryProcessingStatus] = Query(
        default=None, description="Filter by processing status", example="completed"
    ),
    search: Optional[str] = Query(
        default=None, description="Search repositories by name or URL"
    ),
    include_analysis: bool = Query(
        default=False,
        description="Include latest analysis and document counts",
        example=True,
    ),
    include_ai_summary: bool = Query(
        default=False,
        description="Include AI summary in analysis data (can be large)",
        example=False,
    ),
    db: DatabaseService = Depends(get_database_service),
):
    """Get paginated list of repositories with optional filtering and analysis data"""
    try:
        repositories, total = await db.list_repositories(
            skip=skip,
            limit=limit,
            author=author,
            status=status.value if status else None,
            search=search,
        )

        # Build repository list with optional analysis data
        repo_list = []

        for repo in repositories:
            # Remove full_text (always)
            repo.full_text = None

            # Conditionally remove ai_summary if not requested
            if not include_ai_summary and repo.analysis:
                repo.analysis.ai_summary = None

            if not include_analysis:
                repo_list.append(RepositoryResponse.model_validate(repo).model_dump())
            else:
                repo_list.append(
                    RepositoryWithAnalysis.model_validate(repo).model_dump()
                )

        return {
            "repositories": repo_list,
            "pagination": {
                "total": total,
                "page": (skip // limit) + 1,
                "per_page": limit,
                "has_more": skip + limit < total,
                "total_pages": (total + limit - 1) // limit,
            },
            "options": {"include_analysis": include_analysis},
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list repositories: {str(e)}"
        )


@router.get(
    "/{repo_id}",
    response_model=dict,
    summary="Get Repository",
    description="Get detailed information about a specific repository with optional analysis data",
    response_description="Repository details with optional analysis and document counts",
)
async def get_repository(
    repo_id: UUID,
    include_analysis: bool = Query(
        default=False,
        description="Include latest analysis and document counts",
        example=True,
    ),
    include_ai_summary: bool = Query(
        default=False,
        description="Include AI summary in analysis data (can be large)",
        example=False,
    ),
    db: DatabaseService = Depends(get_database_service),
):
    """Get repository by ID with optional analysis data"""
    try:
        repository = await db.get_repository(repo_id)

        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        if include_analysis:
            # Get latest analysis for this repository
            analysis = await db.get_latest_repository_analysis(repo_id)

            analysis_summary = None
            if analysis:
                analysis_summary = RepositoryAnalysisSummary(
                    id=analysis.id,
                    repository_id=analysis.repository_id,
                    analysis_version=analysis.analysis_version,
                    total_files_found=analysis.total_files_found,
                    total_directories=analysis.total_directories,
                    files_processed=analysis.files_processed,
                    total_lines=analysis.total_lines,
                    total_characters=analysis.total_characters,
                    estimated_tokens=analysis.estimated_tokens,
                    estimated_size_bytes=analysis.estimated_size_bytes,
                    large_files_skipped=analysis.large_files_skipped,
                    tree_structure=analysis.tree_structure,
                    binary_files_skipped=analysis.binary_files_skipped,
                    encoding_errors=analysis.encoding_errors,
                    readme_image_src=analysis.readme_image_src,
                    ai_summary=analysis.ai_summary if include_ai_summary else None,
                    description=analysis.description,
                    forked_repo_url=analysis.forked_repo_url,
                    twitter_link=analysis.twitter_link,
                    created_at=(
                        analysis.created_at.isoformat() if analysis.created_at else None
                    ),
                )

            # Create repository with analysis
            repo_with_analysis = RepositoryWithAnalysis(
                **RepositoryResponse.from_orm(repository).dict(),
                analysis=analysis_summary,
            )
            return repo_with_analysis.dict()

        return RepositoryResponse.from_orm(repository).dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get repository: {str(e)}"
        )


@router.get(
    "",
    response_model=dict,
    summary="Get Repository by URL",
    description="Get repository by GitHub URL with optional analysis data",
    response_description="Repository details with optional analysis and document counts",
)
async def get_repository_by_url(
    repo_url: str = Query(..., description="GitHub repository URL"),
    include_analysis: bool = Query(
        default=False,
        description="Include latest analysis and document counts",
        example=True,
    ),
    include_ai_summary: bool = Query(
        default=False,
        description="Include AI summary in analysis data (can be large)",
        example=False,
    ),
    db: DatabaseService = Depends(get_database_service),
):
    """Get repository by GitHub URL with optional analysis data"""
    try:
        repository = await db.get_repository_by_url(repo_url)

        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        if include_analysis:
            # Get latest analysis for this repository
            analysis = await db.get_latest_repository_analysis(repository.id)

            analysis_summary = None
            if analysis:
                analysis_summary = RepositoryAnalysisSummary(
                    id=analysis.id,
                    repository_id=analysis.repository_id,
                    analysis_version=analysis.analysis_version,
                    total_files_found=analysis.total_files_found,
                    total_directories=analysis.total_directories,
                    files_processed=analysis.files_processed,
                    total_lines=analysis.total_lines,
                    total_characters=analysis.total_characters,
                    estimated_tokens=analysis.estimated_tokens,
                    estimated_size_bytes=analysis.estimated_size_bytes,
                    large_files_skipped=analysis.large_files_skipped,
                    binary_files_skipped=analysis.binary_files_skipped,
                    encoding_errors=analysis.encoding_errors,
                    readme_image_src=analysis.readme_image_src,
                    ai_summary=analysis.ai_summary if include_ai_summary else None,
                    description=analysis.description,
                    forked_repo_url=analysis.forked_repo_url,
                    twitter_link=analysis.twitter_link,
                    created_at=(
                        analysis.created_at.isoformat() if analysis.created_at else None
                    ),
                )

            # Create repository with analysis
            repo_with_analysis = RepositoryWithAnalysis(
                **RepositoryResponse.from_orm(repository).dict(),
                analysis=analysis_summary,
            )
            return repo_with_analysis.dict()

        return RepositoryResponse.from_orm(repository).dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get repository by URL: {str(e)}"
        )


@router.get("/{repo_id}/analysis", response_model=RepositoryAnalysisResponse)
async def get_repository_analysis(
    repo_id: UUID,
    version: Optional[int] = Query(
        None, description="Specific analysis version (latest if not provided)"
    ),
    db: DatabaseService = Depends(get_database_service),
):
    """Get repository analysis by ID"""
    try:
        # Verify repository exists
        repository = await db.get_repository(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Get analysis (latest or specific version)
        if version:
            analysis = await db.get_repository_analysis_by_version(repo_id, version)
        else:
            analysis = await db.get_latest_repository_analysis(repo_id)

        if not analysis:
            raise HTTPException(status_code=404, detail="Repository analysis not found")

        return RepositoryAnalysisResponse.from_orm(analysis)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get repository analysis: {str(e)}"
        )


@router.get("/{repo_id}/documents", response_model=dict)
async def get_repository_documents(
    repo_id: UUID,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    current_only: bool = Query(
        False, description="Only return current version documents"
    ),
    summary_only: bool = Query(
        False, description="Return document summaries without content"
    ),
    db: DatabaseService = Depends(get_database_service),
):
    """Get paginated documents for a repository"""
    try:
        # Verify repository exists
        repository = await db.get_repository(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Get documents
        if current_only:
            documents = await db.get_current_documents(repo_id)
            total = len(documents)
            # Apply pagination manually for current documents
            documents = documents[skip : skip + limit]
        else:
            documents, total = await db.get_paginated_documents_by_repository(
                repo_id, skip, limit, document_type
            )

        # Convert to appropriate response model
        if summary_only:
            document_list = []
            for doc in documents:
                new_doc = DocumentSummary.model_validate(doc)
                if doc.created_at:
                    new_doc.created_at = doc.created_at.isoformat()
                document_list.append(new_doc)
        else:
            document_list = []
            for doc in documents:
                new_doc = DocumentResponse(
                    id=doc.id,
                    repository_analysis_id=doc.repository_analysis_id,
                    title=doc.title,
                    content=doc.content,
                    document_type=doc.document_type,
                    version=doc.version,
                    created_at=doc.created_at.isoformat(),
                )

                document_list.append(new_doc)

        return {
            "documents": document_list,
            "pagination": {
                "total": total,
                "page": (skip // limit) + 1,
                "per_page": limit,
                "has_more": skip + limit < total,
                "total_pages": (total + limit - 1) // limit,
            },
            "filters": {
                "document_type": document_type,
                "current_only": current_only,
                "summary_only": summary_only,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get repository documents: {str(e)}"
        )


@router.get("/{repo_id}/documents/{document_id}", response_model=DocumentResponse)
async def get_repository_document(
    repo_id: UUID,
    document_id: UUID,
    db: DatabaseService = Depends(get_database_service),
):
    """Get specific document by repository and document ID"""
    try:
        # Verify repository exists
        repository = await db.get_repository(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Get document
        document = await db.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Verify document belongs to this repository
        analysis = await db.get_repository_analysis(document.repository_analysis_id)
        if not analysis or analysis.repository_id != repo_id:
            raise HTTPException(
                status_code=404, detail="Document not found for this repository"
            )

        return DocumentResponse.from_orm(document)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")


@router.get("/{repo_id}/overview", response_model=dict)
async def get_repository_overview(
    repo_id: UUID, db: DatabaseService = Depends(get_database_service)
):
    """Get complete repository overview including repository, analysis, and document summaries"""
    try:
        # Get repository
        repository = await db.get_repository(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Get latest analysis
        analysis = await db.get_latest_repository_analysis(repo_id)

        # Get current documents (summaries only)
        current_documents = await db.get_current_documents(repo_id)
        document_summaries = [
            DocumentSummary.from_orm(doc) for doc in current_documents
        ]

        # Get document counts by type
        document_counts = {}
        for doc in current_documents:
            doc_type = doc.document_type
            document_counts[doc_type] = document_counts.get(doc_type, 0) + 1

        return {
            "repository": RepositoryResponse.from_orm(repository),
            "analysis": (
                RepositoryAnalysisResponse.from_orm(analysis) if analysis else None
            ),
            "documents": {
                "current_documents": document_summaries,
                "total_current": len(current_documents),
                "counts_by_type": document_counts,
            },
            "stats": {
                "has_analysis": analysis is not None,
                "has_documents": len(current_documents) > 0,
                "processing_complete": (
                    repository.processing_status == RepositoryProcessingStatus.COMPLETED
                ),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get repository overview: {str(e)}"
        )


@router.get("/{repo_id}/stats", response_model=dict)
async def get_repository_statistics(
    repo_id: UUID, db: DatabaseService = Depends(get_database_service)
):
    """Get detailed statistics for a repository"""
    try:
        # Verify repository exists
        repository = await db.get_repository(repo_id)
        if not repository:
            raise HTTPException(status_code=404, detail="Repository not found")

        # Get repository-specific statistics
        stats = await db.get_repository_statistics(repo_id)
        return stats

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get repository statistics: {str(e)}"
        )
