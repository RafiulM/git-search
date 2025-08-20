from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from uuid import UUID

from app.models import (
    Prompt,
    PromptInsert,
    PromptUpdate,
    PromptResponse,
    PromptType,
)
from app.services.database import get_database_service, DatabaseService
from app.services.auth import require_api_key

router = APIRouter(
    dependencies=[Depends(require_api_key)]  # Apply API key requirement to all routes in this router
)

@router.post("/", response_model=PromptResponse)
async def create_prompt(
    prompt_data: PromptInsert,
    db: DatabaseService = Depends(get_database_service)
):
    """Create a new prompt"""
    try:
        prompt = await db.create_prompt(prompt_data)
        return PromptResponse.from_orm(prompt)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create prompt: {str(e)}"
        )

@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: UUID,
    db: DatabaseService = Depends(get_database_service)
):
    """Get prompt by ID"""
    try:
        prompt = await db.get_prompt(prompt_id)
        if not prompt:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )
        return PromptResponse.from_orm(prompt)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get prompt: {str(e)}"
        )

@router.get("/", response_model=List[PromptResponse])
async def list_prompts(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    db: DatabaseService = Depends(get_database_service)
):
    """List prompts with pagination and optional filtering by type"""
    try:
        prompts, total = await db.list_prompts(skip, limit, type)
        return [PromptResponse.from_orm(prompt) for prompt in prompts]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list prompts: {str(e)}"
        )

@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_id: UUID,
    update_data: PromptUpdate,
    db: DatabaseService = Depends(get_database_service)
):
    """Update prompt"""
    try:
        # Check if prompt exists
        existing_prompt = await db.get_prompt(prompt_id)
        if not existing_prompt:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )
        
        # Update prompt
        updated_prompt = await db.update_prompt(prompt_id, update_data)
        if not updated_prompt:
            raise HTTPException(
                status_code=500,
                detail="Failed to update prompt"
            )
        
        return PromptResponse.from_orm(updated_prompt)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update prompt: {str(e)}"
        )

@router.delete("/{prompt_id}")
async def delete_prompt(
    prompt_id: UUID,
    db: DatabaseService = Depends(get_database_service)
):
    """Delete prompt (soft delete by setting is_active to False)"""
    try:
        # Check if prompt exists
        existing_prompt = await db.get_prompt(prompt_id)
        if not existing_prompt:
            raise HTTPException(
                status_code=404,
                detail="Prompt not found"
            )
        
        # Soft delete by setting is_active to False
        updated_prompt = await db.update_prompt(prompt_id, {"is_active": False})
        if not updated_prompt:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete prompt"
            )
        
        return {"message": "Prompt deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete prompt: {str(e)}"
        )