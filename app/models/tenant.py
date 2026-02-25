"""Tenant model for multi-tenant architecture."""

from sqlalchemy import Column, String, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Tenant(BaseModel):
    """
    Tenant model representing an isolated customer organization.
    
    Attributes:
        name: Display name of the tenant
        slug: URL-friendly unique identifier
        settings: JSON field for tenant-specific configuration
        users: Relationship to User model
    """

    __tablename__ = "tenants"

    name = Column(
        String(255),
        nullable=False,
        comment="Display name of the tenant",
    )
    slug = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="URL-friendly unique identifier",
    )
    settings = Column(
        JSON,
        nullable=False,
        default=dict,
        server_default="{}",
        comment="Tenant-specific configuration (rate limits, features, etc.)",
    )

    # Relationships
    users = relationship(
        "User",
        back_populates="tenant",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        """String representation of tenant."""
        return f"<Tenant(id={self.id}, name='{self.name}', slug='{self.slug}')>"
