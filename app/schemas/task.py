"""Task schemas for Celery task management."""

from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    task_type: str = Field(..., description="Type of task to execute")
    params: Dict[str, Any] = Field(default={}, description="Task parameters")


class TaskStatusResponse(BaseModel):
    """Schema for task status response."""

    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Task status (pending, started, completed, failed, retrying)")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    started_at: Optional[datetime] = Field(None, description="Task start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")
    created_at: datetime = Field(..., description="Task creation timestamp")
