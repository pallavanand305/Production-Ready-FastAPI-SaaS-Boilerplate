"""User API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserList
from app.services.user import UserService
from app.api.deps import get_current_active_user, require_permission
from app.models.user import User
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=UserList, status_code=status.HTTP_200_OK)
def get_users(
    request: Request,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    search: Optional[str] = Query(None, description="Search term for email or name"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get list of users with pagination.
    
    Args:
        request: FastAPI request
        skip: Number of records to skip
        limit: Maximum number of records
        search: Optional search term
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of users
    """
    user_service = UserService(db)
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if search:
        users = user_service.search_users(
            search_term=search,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
        )
    else:
        users = user_service.get_users(skip=skip, limit=limit, tenant_id=tenant_id)
    
    total = user_service.count_users(tenant_id=tenant_id)
    
    # Convert users to response format
    user_responses = [
        UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            tenant_id=user.tenant_id,
            roles=[role.name for role in user.roles],
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        for user in users
    ]
    
    return UserList(items=user_responses, total=total, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        request: FastAPI request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        User details
        
    Raises:
        HTTPException: If user not found
    """
    user_service = UserService(db)
    tenant_id = getattr(request.state, "tenant_id", None)
    
    user = user_service.get_user(user_id=user_id, tenant_id=tenant_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        tenant_id=user.tenant_id,
        roles=[role.name for role in user.roles],
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("users", "write"))],
)
def create_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new user.
    
    Args:
        user_data: User creation data
        request: FastAPI request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created user
        
    Raises:
        HTTPException: If email already exists
    """
    user_service = UserService(db)
    tenant_id = getattr(request.state, "tenant_id", None)
    
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant context required",
        )
    
    try:
        user = user_service.create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            tenant_id=tenant_id,
            roles=user_data.roles,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        tenant_id=user.tenant_id,
        roles=[role.name for role in user.roles],
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission("users", "write"))],
)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update user.
    
    Args:
        user_id: User ID
        user_data: User update data
        request: FastAPI request
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user
        
    Raises:
        HTTPException: If user not found
    """
    user_service = UserService(db)
    tenant_id = getattr(request.state, "tenant_id", None)
    
    user = user_service.update_user(
        user_id=user_id,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        is_active=user_data.is_active,
        roles=user_data.roles,
        tenant_id=tenant_id,
    )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        tenant_id=user.tenant_id,
        roles=[role.name for role in user.roles],
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("users", "delete"))],
)
def delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete user (soft delete).
    
    Args:
        user_id: User ID
        request: FastAPI request
        current_user: Current authenticated user
        db: Database session
        
    Raises:
        HTTPException: If user not found
    """
    user_service = UserService(db)
    tenant_id = getattr(request.state, "tenant_id", None)
    
    result = user_service.delete_user(user_id=user_id, tenant_id=tenant_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return None
