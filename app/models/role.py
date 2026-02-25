"""Role and Permission models for RBAC (Role-Based Access Control)."""

from sqlalchemy import Column, String, ForeignKey, Integer, Table
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, Base

# Many-to-many relationship table for roles and permissions
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(BaseModel):
    """
    Role model for RBAC.
    
    Attributes:
        name: Unique role name (e.g., 'admin', 'user', 'guest')
        description: Human-readable description of the role
        users: Many-to-many relationship to User model
        permissions: Many-to-many relationship to Permission model
    """

    __tablename__ = "roles"

    name = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique role name (e.g., 'admin', 'user', 'guest')",
    )
    description = Column(
        String(255),
        nullable=True,
        comment="Human-readable description of the role",
    )

    # Relationships
    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        lazy="dynamic",
    )
    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin",
    )

    def has_permission(self, resource: str, action: str) -> bool:
        """Check if role has a specific permission."""
        return any(
            perm.resource == resource and perm.action == action
            for perm in self.permissions
        )

    def __repr__(self) -> str:
        """String representation of role."""
        return f"<Role(id={self.id}, name='{self.name}')>"


class Permission(BaseModel):
    """
    Permission model for fine-grained access control.
    
    Attributes:
        resource: Resource name (e.g., 'users', 'tenants', 'tasks')
        action: Action name (e.g., 'read', 'write', 'delete', 'admin')
        roles: Many-to-many relationship to Role model
    """

    __tablename__ = "permissions"

    resource = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Resource name (e.g., 'users', 'tenants', 'tasks')",
    )
    action = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Action name (e.g., 'read', 'write', 'delete', 'admin')",
    )

    # Relationships
    roles = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        """String representation of permission."""
        return f"<Permission(id={self.id}, resource='{self.resource}', action='{self.action}')>"
