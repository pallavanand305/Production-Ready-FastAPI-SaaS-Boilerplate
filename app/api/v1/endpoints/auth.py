"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    TokenPair,
    RefreshRequest,
    LogoutRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth import AuthService
from app.repositories.tenant import TenantRepository
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.post("/login", response_model=TokenPair, status_code=status.HTTP_200_OK)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate user and return access and refresh tokens.
    
    Args:
        login_data: Login credentials
        db: Database session
        
    Returns:
        Token pair (access + refresh tokens)
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService(db)
    
    # Authenticate user
    user = auth_service.authenticate_user(login_data.email, login_data.password)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Check if account is locked
    if user.is_locked():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account locked due to multiple failed login attempts",
        )
    
    # Create token pair
    token_pair = auth_service.create_token_pair(user)
    
    return TokenPair(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type,
        expires_in=token_pair.expires_in,
    )


@router.post("/refresh", response_model=TokenPair, status_code=status.HTTP_200_OK)
def refresh_token(
    refresh_data: RefreshRequest,
    db: Session = Depends(get_db),
):
    """
    Refresh access token using refresh token.
    
    Args:
        refresh_data: Refresh token
        db: Database session
        
    Returns:
        New token pair
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    auth_service = AuthService(db)
    
    # Refresh access token
    token_pair = auth_service.refresh_access_token(refresh_data.refresh_token)
    
    if token_pair is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    return TokenPair(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type,
        expires_in=token_pair.expires_in,
    )


@router.post("/logout", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def logout(
    logout_data: LogoutRequest,
    db: Session = Depends(get_db),
):
    """
    Logout user by revoking refresh token.
    
    Args:
        logout_data: Refresh token to revoke
        db: Database session
        
    Returns:
        Success message
    """
    auth_service = AuthService(db)
    
    # Extract token ID from refresh token
    from app.core.security import verify_token
    payload = verify_token(logout_data.refresh_token, token_type="refresh")
    
    if payload:
        token_id = payload.get("jti")
        if token_id:
            auth_service.revoke_refresh_token(token_id)
    
    return TokenResponse(message="Successfully logged out")


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
def register(
    register_data: RegisterRequest,
    db: Session = Depends(get_db),
):
    """
    Register a new user.
    
    Args:
        register_data: Registration data
        db: Database session
        
    Returns:
        Token pair for newly registered user
        
    Raises:
        HTTPException: If registration fails
    """
    auth_service = AuthService(db)
    tenant_repo = TenantRepository(db)
    
    # Get tenant by slug
    tenant = tenant_repo.get_by_slug(register_data.tenant_slug)
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tenant not found: {register_data.tenant_slug}",
        )
    
    # Register user
    try:
        user = auth_service.register_user(
            email=register_data.email,
            password=register_data.password,
            full_name=register_data.full_name,
            tenant_id=tenant.id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    
    # Create token pair
    token_pair = auth_service.create_token_pair(user)
    
    return TokenPair(
        access_token=token_pair.access_token,
        refresh_token=token_pair.refresh_token,
        token_type=token_pair.token_type,
        expires_in=token_pair.expires_in,
    )
