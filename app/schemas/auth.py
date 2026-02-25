"""Authentication schemas."""

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")


class TokenPair(BaseModel):
    """Token pair response schema."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration time in seconds")


class RefreshRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str = Field(..., description="JWT refresh token")


class LogoutRequest(BaseModel):
    """Logout request schema."""

    refresh_token: str = Field(..., description="JWT refresh token to revoke")


class RegisterRequest(BaseModel):
    """User registration request schema."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: str = Field(..., min_length=1, max_length=255, description="User's full name")
    tenant_slug: str = Field(..., min_length=1, max_length=100, description="Tenant slug")


class TokenResponse(BaseModel):
    """Generic token response."""

    message: str = Field(..., description="Response message")
