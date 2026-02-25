"""Security headers middleware."""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware for adding security headers to all responses.
    
    Headers added:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security: max-age=31536000; includeSubDomains (production only)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Add HSTS header in production
        from app.core.config import settings
        if settings.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for limiting request body size.
    
    Rejects requests exceeding the configured maximum size with 413 status code.
    """

    def __init__(self, app, max_size: int = None):
        """
        Initialize request size limiter.
        
        Args:
            app: FastAPI application
            max_size: Maximum request size in bytes
        """
        super().__init__(app)
        from app.core.config import settings
        self.max_size = max_size or settings.MAX_REQUEST_SIZE

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check request size before processing."""
        # Get content length from headers
        content_length = request.headers.get("content-length")
        
        if content_length:
            content_length = int(content_length)
            if content_length > self.max_size:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"Request body too large. Maximum size: {self.max_size} bytes",
                )
        
        response = await call_next(request)
        return response


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to redirect HTTP to HTTPS in production.
    
    Only enforces HTTPS when not in debug mode.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Redirect HTTP to HTTPS if in production."""
        from app.core.config import settings
        from fastapi.responses import RedirectResponse
        from fastapi import status
        
        # Only enforce HTTPS in production
        if not settings.DEBUG and request.url.scheme == "http":
            # Redirect to HTTPS
            url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(url), status_code=status.HTTP_301_MOVED_PERMANENTLY)
        
        return await call_next(request)
