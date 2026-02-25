"""User service with business logic."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.user import UserRepository
from app.core.security import hash_password
from app.services.cache import cache_service
from app.core.decorators import cached, cache_invalidate
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserService:
    """User service for business logic and caching."""

    def __init__(self, db: Session):
        """Initialize user service."""
        self.db = db
        self.user_repo = UserRepository(db)

    @cached(ttl=300, key_prefix="user", tenant_aware=True)
    def get_user(self, user_id: int, tenant_id: Optional[int] = None) -> Optional[User]:
        """
        Get user by ID with caching.
        
        Args:
            user_id: User ID
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            User instance or None
        """
        return self.user_repo.get(id=user_id, tenant_id=tenant_id)

    @cached(ttl=300, key_prefix="users", tenant_aware=True)
    def get_users(
        self,
        skip: int = 0,
        limit: int = 100,
        tenant_id: Optional[int] = None,
    ) -> List[User]:
        """
        Get users with pagination and caching.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            List of users
        """
        return self.user_repo.get_multi(skip=skip, limit=limit, tenant_id=tenant_id)

    def search_users(
        self,
        search_term: str,
        tenant_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[User]:
        """
        Search users by email or name.
        
        Args:
            search_term: Search term
            tenant_id: Optional tenant ID for filtering
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of matching users
        """
        return self.user_repo.search(
            search_term=search_term,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
        )

    @cache_invalidate(key_pattern="user:*", tenant_aware=True)
    def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        tenant_id: int,
        roles: Optional[List[str]] = None,
    ) -> User:
        """
        Create a new user.
        
        Args:
            email: User email
            password: Plain text password
            full_name: User's full name
            tenant_id: Tenant ID
            roles: Optional list of role names
            
        Returns:
            Created user
        """
        # Hash password
        hashed_password = hash_password(password)
        
        # Create user
        user_data = {
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "is_active": True,
        }
        
        user = self.user_repo.create(user_data, tenant_id=tenant_id)
        
        # Assign roles
        if roles:
            from app.models.role import Role
            for role_name in roles:
                role = self.db.query(Role).filter(Role.name == role_name).first()
                if role:
                    user.roles.append(role)
            self.db.commit()
            self.db.refresh(user)
        
        logger.info(f"User created: {email}", extra={"user_id": user.id, "tenant_id": tenant_id})
        return user

    @cache_invalidate(key_pattern="user:*", tenant_aware=True)
    def update_user(
        self,
        user_id: int,
        email: Optional[str] = None,
        password: Optional[str] = None,
        full_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        roles: Optional[List[str]] = None,
        tenant_id: Optional[int] = None,
    ) -> Optional[User]:
        """
        Update user.
        
        Args:
            user_id: User ID
            email: Optional new email
            password: Optional new password
            full_name: Optional new full name
            is_active: Optional new active status
            roles: Optional new roles
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            Updated user or None
        """
        update_data = {}
        
        if email is not None:
            update_data["email"] = email
        if password is not None:
            update_data["hashed_password"] = hash_password(password)
        if full_name is not None:
            update_data["full_name"] = full_name
        if is_active is not None:
            update_data["is_active"] = is_active
        
        user = self.user_repo.update(id=user_id, obj_in=update_data, tenant_id=tenant_id)
        
        if user and roles is not None:
            # Update roles
            user.roles.clear()
            from app.models.role import Role
            for role_name in roles:
                role = self.db.query(Role).filter(Role.name == role_name).first()
                if role:
                    user.roles.append(role)
            self.db.commit()
            self.db.refresh(user)
        
        if user:
            logger.info(f"User updated: {user.email}", extra={"user_id": user_id, "tenant_id": tenant_id})
        
        return user

    @cache_invalidate(key_pattern="user:*", tenant_aware=True)
    def delete_user(self, user_id: int, tenant_id: Optional[int] = None) -> bool:
        """
        Soft delete user.
        
        Args:
            user_id: User ID
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            True if deleted, False otherwise
        """
        result = self.user_repo.delete(id=user_id, tenant_id=tenant_id)
        if result:
            logger.info(f"User deleted", extra={"user_id": user_id, "tenant_id": tenant_id})
        return result

    def count_users(self, tenant_id: Optional[int] = None) -> int:
        """
        Count users.
        
        Args:
            tenant_id: Optional tenant ID for filtering
            
        Returns:
            Number of users
        """
        return self.user_repo.count(tenant_id=tenant_id)
