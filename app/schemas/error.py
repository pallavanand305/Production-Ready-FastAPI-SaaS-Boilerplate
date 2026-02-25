"""Error response schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """Schema for error detail."""

    field: Optional[str] = Field(None, description="Field name that caused the error")
    message: str = Field(..., description="Error message")
    type: Optional[str] = Field(None, description="Error type")


class ErrorResponse(BaseModel):
    """Schema for error response."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[List[ErrorDetail]] = Field(None, description="List of error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")


class ErrorResponseWrapper(BaseModel):
    """Wrapper for error response."""

    error: ErrorResponse = Field(..., description="Error details")
