"""Tenant schemas."""

from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TenantBase(BaseModel):
    """Base tenant schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Tenant name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly identifier")


class TenantCreate(TenantBase):
    """Schema for creating a new tenant."""

    settings: Dict[str, Any] = Field(default={}, description="Tenant-specific settings")


class TenantUpdate(BaseModel):
    """Schema for updating a tenant."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Tenant name")
    slug: Optional[str] = Field(None, min_length=1, max_length=100, description="URL-friendly identifier")
    settings: Optional[Dict[str, Any]] = Field(None, description="Tenant-specific settings")


class TenantResponse(TenantBase):
    """Schema for tenant response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Tenant ID")
    settings: Dict[str, Any] = Field(..., description="Tenant-specific settings")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class TenantList(BaseModel):
    """Schema for paginated tenant list."""

    items: list[TenantResponse] = Field(..., description="List of tenants")
    total: int = Field(..., description="Total number of tenants")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum number of items returned")
