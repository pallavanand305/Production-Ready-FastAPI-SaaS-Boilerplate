"""Tenant API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse, TenantList
from app.repositories.tenant import TenantRepository
from app.api.deps import get_current_active_user, require_role
from app.models.user import User
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("", response_model=TenantList, status_code=status.HTTP_200_OK)
def get_tenants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get list of tenants with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Paginated list of tenants
    """
    tenant_repo = TenantRepository(db)
    
    tenants = tenant_repo.get_multi(skip=skip, limit=limit)
    total = tenant_repo.count()
    
    tenant_responses = [
        TenantResponse(
            id=tenant.id,
            name=tenant.name,
            slug=tenant.slug,
            settings=tenant.settings,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
        )
        for tenant in tenants
    ]
    
    return TenantList(items=tenant_responses, total=total, skip=skip, limit=limit)


@router.get("/{tenant_id}", response_model=TenantResponse, status_code=status.HTTP_200_OK)
def get_tenant(
    tenant_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get tenant by ID.
    
    Args:
        tenant_id: Tenant ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Tenant details
        
    Raises:
        HTTPException: If tenant not found
    """
    tenant_repo = TenantRepository(db)
    tenant = tenant_repo.get(id=tenant_id)
    
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        settings=tenant.settings,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
    )


@router.post(
    "",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("admin"))],
)
def create_tenant(
    tenant_data: TenantCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new tenant (admin only).
    
    Args:
        tenant_data: Tenant creation data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Created tenant
        
    Raises:
        HTTPException: If slug already exists
    """
    tenant_repo = TenantRepository(db)
    
    # Check if slug already exists
    existing = tenant_repo.get_by_slug(tenant_data.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tenant with slug '{tenant_data.slug}' already exists",
        )
    
    tenant = tenant_repo.create({
        "name": tenant_data.name,
        "slug": tenant_data.slug,
        "settings": tenant_data.settings,
    })
    
    logger.info(f"Tenant created: {tenant.slug}", extra={"tenant_id": tenant.id})
    
    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        settings=tenant.settings,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
    )


@router.put(
    "/{tenant_id}",
    response_model=TenantResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role("admin"))],
)
def update_tenant(
    tenant_id: int,
    tenant_data: TenantUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update tenant (admin only).
    
    Args:
        tenant_id: Tenant ID
        tenant_data: Tenant update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated tenant
        
    Raises:
        HTTPException: If tenant not found
    """
    tenant_repo = TenantRepository(db)
    
    update_data = {}
    if tenant_data.name is not None:
        update_data["name"] = tenant_data.name
    if tenant_data.slug is not None:
        update_data["slug"] = tenant_data.slug
    if tenant_data.settings is not None:
        update_data["settings"] = tenant_data.settings
    
    tenant = tenant_repo.update(id=tenant_id, obj_in=update_data)
    
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    logger.info(f"Tenant updated: {tenant.slug}", extra={"tenant_id": tenant_id})
    
    return TenantResponse(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        settings=tenant.settings,
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
    )
