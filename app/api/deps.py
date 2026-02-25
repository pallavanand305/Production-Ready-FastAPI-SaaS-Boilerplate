"""API dependencies for authentication and authorization."""

from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.security import verify_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.core.logging import get_logger

logger = get_logger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        db: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user ID from token
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user_repo = UserRepository(db)
    user = user_repo.get(id=int(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account",
        )
    
    return current_user


def require_role(required_role: str):
    """
    Dependency factory for requiring specific role.
    
    Args:
        required_role: Required role name
        
    Returns:
        Dependency function
        
    Example:
        @app.get("/admin", dependencies=[Depends(require_role("admin"))])
        def admin_endpoint():
            return {"message": "Admin access granted"}
    """
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not current_user.has_role(required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required",
            )
        return current_user
    
    return role_checker


def require_permission(resource: str, action: str):
    """
    Dependency factory for requiring specific permission.
    
    Args:
        resource: Resource name (e.g., 'users', 'tenants')
        action: Action name (e.g., 'read', 'write', 'delete')
        
    Returns:
        Dependency function
        
    Example:
        @app.delete("/users/{id}", dependencies=[Depends(require_permission("users", "delete"))])
        def delete_user(id: int):
            return {"message": "User deleted"}
    """
    def permission_checker(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ) -> User:
        from app.services.auth import AuthService
        
        auth_service = AuthService(db)
        if not auth_service.check_permission(current_user, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {action} on {resource}",
            )
        return current_user
    
    return permission_checker


def get_tenant_context(request: Request) -> Optional[int]:
    """
    Get tenant context from request state.
    
    Args:
        request: FastAPI request
        
    Returns:
        Tenant ID or None
    """
    return getattr(request.state, "tenant_id", None)


def require_tenant_context(request: Request) -> int:
    """
    Require tenant context to be present.
    
    Args:
        request: FastAPI request
        
    Returns:
        Tenant ID
        
    Raises:
        HTTPException: If tenant context not found
    """
    tenant_id = get_tenant_context(request)
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant context required",
        )
    return tenant_id


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    
    Args:
        credentials: Optional HTTP Bearer credentials
        db: Database session
        
    Returns:
        Current user or None
    """
    if credentials is None:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
