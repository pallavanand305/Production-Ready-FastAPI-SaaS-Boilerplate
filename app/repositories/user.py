"""User repository with authentication-specific queries."""

from typing import Optional
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model with authentication-specific methods."""

    def __init__(self, db: Session):
        """Initialize user repository."""
        super().__init__(User, db)

    def get_by_email(self, email: str, tenant_id: Optional[int] = None) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User email address
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            User instance or None if not found
        """
        query = select(User).where(
            User.email == email,
            User.is_deleted == False,
        )
        
        if tenant_id is not None:
            query = query.where(User.tenant_id == tenant_id)
        
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def search(
        self,
        search_term: str,
        tenant_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        Search users by email or full name.
        
        Args:
            search_term: Search term to match against email or full_name
            tenant_id: Optional tenant ID for filtering
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of matching users
        """
        search_pattern = f"%{search_term}%"
        query = select(User).where(
            User.is_deleted == False,
            or_(
                User.email.ilike(search_pattern),
                User.full_name.ilike(search_pattern),
            ),
        )
        
        if tenant_id is not None:
            query = query.where(User.tenant_id == tenant_id)
        
        query = query.offset(skip).limit(limit)
        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_active_users(
        self,
        tenant_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        Get all active users.
        
        Args:
            tenant_id: Optional tenant ID for filtering
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active users
        """
        query = select(User).where(
            User.is_deleted == False,
            User.is_active == True,
        )
        
        if tenant_id is not None:
            query = query.where(User.tenant_id == tenant_id)
        
        query = query.offset(skip).limit(limit)
        result = self.db.execute(query)
        return list(result.scalars().all())

    def get_by_role(
        self,
        role_name: str,
        tenant_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[User]:
        """
        Get users by role name.
        
        Args:
            role_name: Role name to filter by
            tenant_id: Optional tenant ID for filtering
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of users with the specified role
        """
        from app.models.role import Role
        
        query = (
            select(User)
            .join(User.roles)
            .where(
                User.is_deleted == False,
                Role.name == role_name,
            )
        )
        
        if tenant_id is not None:
            query = query.where(User.tenant_id == tenant_id)
        
        query = query.offset(skip).limit(limit)
        result = self.db.execute(query)
        return list(result.scalars().all())
