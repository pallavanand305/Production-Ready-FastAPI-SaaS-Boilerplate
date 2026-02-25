"""Exception handlers for FastAPI application."""

import logging
from typing import Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.schemas.error import ErrorResponse, ErrorDetail

logger = logging.getLogger(__name__)


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Handle HTTP exceptions."""
    request_id = getattr(request.state, "request_id", None)
    
    # Log the error
    logger.error(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={"request_id": request_id, "path": request.url.path}
    )
    
    error_response = ErrorResponse(
        code=f"HTTP_{exc.status_code}",
        message=str(exc.detail),
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": error_response.model_dump()}
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors."""
    request_id = getattr(request.state, "request_id", None)
    
    # Extract validation errors
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        details.append(
            ErrorDetail(
                field=field,
                message=error["msg"],
                type=error["type"]
            )
        )
    
    logger.warning(
        f"Validation error: {len(details)} field(s) failed validation",
        extra={"request_id": request_id, "path": request.url.path}
    )
    
    error_response = ErrorResponse(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details=details,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": error_response.model_dump()}
    )


async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """Handle database integrity errors."""
    request_id = getattr(request.state, "request_id", None)
    
    logger.error(
        f"Database integrity error: {str(exc)}",
        extra={"request_id": request_id, "path": request.url.path}
    )
    
    # Sanitize error message in production
    if settings.DEBUG:
        message = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
    else:
        message = "A database constraint was violated. Please check your input."
    
    error_response = ErrorResponse(
        code="INTEGRITY_ERROR",
        message=message,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"error": error_response.model_dump()}
    )


async def general_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle general exceptions."""
    request_id = getattr(request.state, "request_id", None)
    
    logger.exception(
        f"Unhandled exception: {type(exc).__name__}",
        extra={"request_id": request_id, "path": request.url.path},
        exc_info=exc
    )
    
    # Sanitize error message in production
    if settings.DEBUG:
        message = f"{type(exc).__name__}: {str(exc)}"
    else:
        message = "An internal server error occurred. Please try again later."
    
    error_response = ErrorResponse(
        code="INTERNAL_SERVER_ERROR",
        message=message,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": error_response.model_dump()}
    )


def register_exception_handlers(app) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
