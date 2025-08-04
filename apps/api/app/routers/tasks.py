from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models import TaskStatusResponse, TaskStatus
from app.services.background_tasks import get_task_status, task_storage

router = APIRouter()

@router.get("/", response_model=List[TaskStatusResponse])
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    limit: int = Query(10, ge=1, le=100, description="Number of tasks to return")
):
    """List background tasks from in-memory storage"""
    try:
        all_tasks = []
        
        # Get tasks from in-memory storage
        for task_id, task_data in list(task_storage.items())[:limit]:
            if not status or task_data.get('status') == status.value:
                all_tasks.append(TaskStatusResponse(
                    task_id=task_id,
                    status=TaskStatus(task_data.get('status', 'pending')),
                    message=task_data.get('message', ''),
                    progress=task_data.get('progress'),
                    repo_id=task_data.get('repo_id'),
                    result=task_data.get('result'),
                    error=task_data.get('error')
                ))
        
        return all_tasks[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list tasks: {str(e)}"
        )

@router.get("/{task_id}", response_model=TaskStatusResponse)
async def get_task_status_endpoint(task_id: str):
    """Get specific task status"""
    try:
        task_info = get_task_status(task_id)
        
        if task_info.get('status') == 'not_found':
            raise HTTPException(status_code=404, detail="Task not found")
            
        return TaskStatusResponse(
            task_id=task_info["task_id"],
            status=TaskStatus(task_info["status"]),
            message=task_info.get("message", ""),
            progress=task_info.get("progress"),
            repo_id=task_info.get("repo_id"),
            result=task_info.get("result"),
            error=task_info.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )

@router.delete("/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a background task (simplified - just removes from storage)"""
    try:
        if task_id not in task_storage:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Since FastAPI BackgroundTasks can't be cancelled once started,
        # we can only remove it from our tracking storage
        del task_storage[task_id]
        
        return {
            "message": f"Task {task_id} removed from tracking",
            "note": "FastAPI BackgroundTasks cannot be cancelled once started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel task: {str(e)}"
        )

@router.get("/stats/overview")
async def get_task_stats():
    """Get simple task statistics"""
    try:
        total_tasks = len(task_storage)
        
        status_counts = {}
        for task_data in task_storage.values():
            status = task_data.get('status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "total_tasks": total_tasks,
            "status_breakdown": status_counts,
            "system": "FastAPI BackgroundTasks",
            "note": "Tasks are stored in memory and will be lost on server restart"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task stats: {str(e)}"
        )