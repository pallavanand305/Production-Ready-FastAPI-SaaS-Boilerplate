"""Base model with common fields for all database models."""

from datetime import datetime
from typing import Any
from sqlalchemy import Column, Integer, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class BaseModel(Base):
    """
    Abstract base model with common fields.
    
    Provides:
    - id: Primary key
    - created_at: Timestamp when record was created
    - updated_at: Timestamp when record was last updated
    - deleted_at: Timestamp when record was soft deleted (NULL if not deleted)
    - is_deleted: Boolean flag for soft delete status
    """

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment="Timestamp when record was created",
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
        comment="Timestamp when record was last updated",
    )
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when record was soft deleted",
    )
    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="Soft delete flag",
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower() + "s"

    def soft_delete(self) -> None:
        """Mark record as deleted without removing from database."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None

    def dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        """String representation of model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
