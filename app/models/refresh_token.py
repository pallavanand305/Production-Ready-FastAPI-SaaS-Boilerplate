"""RefreshToken model for JWT token rotation."""

from sqlalchemy import Column, String, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class RefreshToken(BaseModel):
    """
    RefreshToken model for storing and managing refresh tokens.
    
    Attributes:
        token_id: Unique token identifier (JWT jti claim)
        user_id: Foreign key to user who owns the token
        expires_at: Timestamp when token expires
        is_revoked: Whether token has been revoked
        user: Relationship to User model
    """

    __tablename__ = "refresh_tokens"

    token_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique token identifier (JWT jti claim)",
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to user who owns the token",
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Timestamp when token expires",
    )
    is_revoked = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        comment="Whether token has been revoked",
    )

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    def revoke(self) -> None:
        """Revoke this refresh token."""
        self.is_revoked = True

    def is_valid(self) -> bool:
        """Check if token is valid (not revoked and not expired)."""
        from datetime import datetime
        return not self.is_revoked and datetime.utcnow() < self.expires_at

    def __repr__(self) -> str:
        """String representation of refresh token."""
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, is_revoked={self.is_revoked})>"
