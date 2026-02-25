"""Task management endpoints."""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from celery.result import AsyncResult

from app.worker.celery_app import celery_app
from app.worker.tasks import send_email, process_data
from app.schemas.task import TaskCreate, TaskStatusResponse
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


@router.post("/", response_model=Dict[str, str], status_code=status.HTTP_202_ACCEPTED)
def enqueue_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, str]:
    """
    Enqueue a background task.
    
    Args:
        task_data: Task data
        current_user: Current authenticated user
        
    Returns:
        Task ID
    """
    # Route to appropriate task based on task_type
    if task_data.task_type == "send_email":
        task = send_email.delay(
            recipient=task_data.data.get("recipient"),
            subject=task_data.data.get("subject"),
            body=task_data.data.get("body")
        )
    elif task_data.task_type == "process_data":
        task = process_data.delay(data=task_data.data)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown task type: {task_data.task_type}"
        )
    
    return {
        "task_id": task.id,
        "status": "queued",
        "message": f"Task {task_data.task_type} enqueued successfully"
    }


@router.get("/{task_id}/status", response_model=TaskStatusResponse)
def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
) -> TaskStatusResponse:
    """
    Get task status by ID.
    
    Args:
        task_id: Task ID
        current_user: Current authenticated user
        
    Returns:
        Task status
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    # Map Celery states to our response
    state_mapping = {
        "PENDING": "pending",
        "STARTED": "running",
        "SUCCESS": "completed",
        "FAILURE": "failed",
        "RETRY": "retrying",
        "REVOKED": "cancelled"
    }
    
    status_value = state_mapping.get(task_result.state, "unknown")
    
    response = TaskStatusResponse(
        task_id=task_id,
        status=status_value,
        result=task_result.result if task_result.successful() else None,
        error=str(task_result.info) if task_result.failed() else None
    )
    
    return response
