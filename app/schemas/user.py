"""User schemas."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")
    is_active: bool = Field(default=True, description="Whether user account is active")


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, description="User password")
    roles: List[str] = Field(default=["user"], description="List of role names")


class UserUpdate(BaseModel):
    """Schema for updating a user."""

    email: Optional[EmailStr] = Field(None, description="User email address")
    full_name: Optional[str] = Field(None, max_length=255, description="User's full name")
    is_active: Optional[bool] = Field(None, description="Whether user account is active")
    password: Optional[str] = Field(None, min_length=8, description="New password")
    roles: Optional[List[str]] = Field(None, description="List of role names")


class UserResponse(UserBase):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="User ID")
    tenant_id: int = Field(..., description="Tenant ID")
    roles: List[str] = Field(default=[], description="List of role names")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserList(BaseModel):
    """Schema for paginated user list."""

    items: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Maximum number of items returned")
