"""Tenant context middleware for multi-tenant architecture."""

from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.security import verify_token
from app.core.logging import get_logger

logger = get_logger(__name__)


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware for extracting and setting tenant context from JWT token.
    
    Features:
    - Extracts tenant_id from JWT token
    - Sets tenant_id in request state for downstream use
    - Handles requests without authentication gracefully
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Extract tenant context from JWT token."""
        # Initialize tenant_id as None
        request.state.tenant_id = None
        request.state.user_id = None
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
            # Verify token and extract tenant_id
            payload = verify_token(token, token_type="access")
            if payload:
                request.state.tenant_id = payload.get("tenant_id")
                request.state.user_id = payload.get("sub")
                
                logger.debug(
                    "Tenant context set",
                    extra={
                        "tenant_id": request.state.tenant_id,
                        "user_id": request.state.user_id,
                        "request_id": getattr(request.state, "request_id", None),
                    },
                )
        
        response = await call_next(request)
        return response
