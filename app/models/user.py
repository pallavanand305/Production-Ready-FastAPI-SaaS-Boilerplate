"""User model with authentication and RBAC support."""

from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Integer, Boolean, DateTime, Table
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, Base

# Many-to-many relationship table for users and roles
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class User(BaseModel):
    """
    User model with authentication and multi-tenant support.
    
    Attributes:
        email: Unique email address for authentication
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        is_active: Whether user account is active
        tenant_id: Foreign key to tenant (for multi-tenancy)
        failed_login_attempts: Counter for failed login attempts
        locked_until: Timestamp until which account is locked
        tenant: Relationship to Tenant model
        roles: Many-to-many relationship to Role model
        refresh_tokens: Relationship to RefreshToken model
    """

    __tablename__ = "users"

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique email address for authentication",
    )
    hashed_password = Column(
        String(255),
        nullable=False,
        comment="Bcrypt hashed password",
    )
    full_name = Column(
        String(255),
        nullable=True,
        comment="User's full name",
    )
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        comment="Whether user account is active",
    )
    tenant_id = Column(
        Integer,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to tenant for multi-tenancy",
    )
    failed_login_attempts = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Counter for failed login attempts",
    )
    locked_until = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp until which account is locked",
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="selectin",
    )
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def is_locked(self) -> bool:
        """Check if user account is currently locked."""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until

    def increment_failed_login(self) -> None:
        """Increment failed login attempts counter."""
        self.failed_login_attempts += 1

    def reset_failed_login(self) -> None:
        """Reset failed login attempts counter."""
        self.failed_login_attempts = 0
        self.locked_until = None

    def lock_account(self, duration_minutes: int) -> None:
        """Lock account for specified duration."""
        from datetime import timedelta
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)

    def __repr__(self) -> str:
        """String representation of user."""
        return f"<User(id={self.id}, email='{self.email}', tenant_id={self.tenant_id})>"
