"""Authentication service with JWT token management and RBAC."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4
from sqlalchemy.orm import Session
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.config import settings
from app.core.logging import get_logger
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.repositories.user import UserRepository

logger = get_logger(__name__)


class TokenPair:
    """Data class for access and refresh token pair."""

    def __init__(self, access_token: str, refresh_token: str, token_type: str = "bearer"):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


class AuthService:
    """
    Authentication service handling user authentication and token management.
    
    Features:
    - User authentication with email/password
    - JWT token generation (access + refresh)
    - Refresh token rotation
    - Token revocation
    - Account lockout protection
    - RBAC permission checking
    """

    def __init__(self, db: Session):
        """Initialize authentication service."""
        self.db = db
        self.user_repo = UserRepository(db)

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email address
            password: Plain text password
            
        Returns:
            User instance if authentication successful, None otherwise
        """
        user = self.user_repo.get_by_email(email)
        
        if user is None:
            logger.warning(f"Authentication failed: user not found - {email}")
            return None
        
        # Check if account is locked
        if user.is_locked():
            logger.warning(f"Authentication failed: account locked - {email}")
            return None
        
        # Check if account is active
        if not user.is_active:
            logger.warning(f"Authentication failed: account inactive - {email}")
            return None
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            # Increment failed login attempts
            user.increment_failed_login()
            
            # Lock account if max attempts reached
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.lock_account(settings.LOCKOUT_DURATION_MINUTES)
                logger.warning(
                    f"Account locked due to failed login attempts - {email}",
                    extra={"user_id": user.id, "tenant_id": user.tenant_id},
                )
            
            self.db.commit()
            logger.warning(f"Authentication failed: invalid password - {email}")
            return None
        
        # Reset failed login attempts on successful authentication
        user.reset_failed_login()
        self.db.commit()
        
        logger.info(
            f"User authenticated successfully - {email}",
            extra={"user_id": user.id, "tenant_id": user.tenant_id},
        )
        return user

    def create_token_pair(self, user: User) -> TokenPair:
        """
        Create access and refresh token pair for user.
        
        Args:
            user: User instance
            
        Returns:
            TokenPair with access and refresh tokens
        """
        # Get user roles
        roles = [role.name for role in user.roles]
        
        # Create access token
        access_token = create_access_token(
            subject=str(user.id),
            tenant_id=user.tenant_id,
            roles=roles,
        )
        
        # Create refresh token with unique ID
        token_id = str(uuid4())
        refresh_token = create_refresh_token(
            subject=str(user.id),
            tenant_id=user.tenant_id,
            token_id=token_id,
        )
        
        # Store refresh token in database
        refresh_token_record = RefreshToken(
            token_id=token_id,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(refresh_token_record)
        self.db.commit()
        
        logger.info(
            "Token pair created",
            extra={"user_id": user.id, "tenant_id": user.tenant_id},
        )
        
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    def refresh_access_token(self, refresh_token: str) -> Optional[TokenPair]:
        """
        Refresh access token using refresh token (with token rotation).
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New TokenPair or None if refresh token invalid
        """
        # Verify refresh token
        payload = verify_token(refresh_token, token_type="refresh")
        if payload is None:
            logger.warning("Refresh token verification failed")
            return None
        
        # Get token record from database
        token_id = payload.get("jti")
        token_record = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_id == token_id)
            .first()
        )
        
        if token_record is None or not token_record.is_valid():
            logger.warning(f"Refresh token invalid or revoked - {token_id}")
            return None
        
        # Get user
        user = self.user_repo.get(id=token_record.user_id)
        if user is None or not user.is_active:
            logger.warning(f"User not found or inactive - {token_record.user_id}")
            return None
        
        # Revoke old refresh token
        token_record.revoke()
        
        # Create new token pair
        new_token_pair = self.create_token_pair(user)
        
        logger.info(
            "Access token refreshed",
            extra={"user_id": user.id, "tenant_id": user.tenant_id},
        )
        
        return new_token_pair

    def revoke_refresh_token(self, token_id: str) -> bool:
        """
        Revoke a refresh token.
        
        Args:
            token_id: Token ID (jti claim)
            
        Returns:
            True if revoked, False if not found
        """
        token_record = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_id == token_id)
            .first()
        )
        
        if token_record is None:
            return False
        
        token_record.revoke()
        self.db.commit()
        
        logger.info(f"Refresh token revoked - {token_id}")
        return True

    def check_permission(self, user: User, resource: str, action: str) -> bool:
        """
        Check if user has permission for action on resource.
        
        Args:
            user: User instance
            resource: Resource name (e.g., 'users', 'tenants')
            action: Action name (e.g., 'read', 'write', 'delete')
            
        Returns:
            True if user has permission, False otherwise
        """
        # Admin role has all permissions
        if user.has_role("admin"):
            return True
        
        # Check if any of user's roles have the required permission
        for role in user.roles:
            if role.has_permission(resource, action):
                return True
        
        return False

    def register_user(
        self,
        email: str,
        password: str,
        full_name: str,
        tenant_id: int,
        roles: Optional[list[str]] = None,
    ) -> User:
        """
        Register a new user.
        
        Args:
            email: User email address
            password: Plain text password
            full_name: User's full name
            tenant_id: Tenant ID
            roles: Optional list of role names (defaults to ['user'])
            
        Returns:
            Created user instance
            
        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        existing_user = self.user_repo.get_by_email(email)
        if existing_user is not None:
            raise ValueError(f"Email already registered: {email}")
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Create user
        user_data = {
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name,
            "tenant_id": tenant_id,
            "is_active": True,
        }
        
        user = self.user_repo.create(user_data)
        
        # Assign roles
        if roles is None:
            roles = ["user"]
        
        from app.models.role import Role
        for role_name in roles:
            role = self.db.query(Role).filter(Role.name == role_name).first()
            if role:
                user.roles.append(role)
        
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(
            f"User registered - {email}",
            extra={"user_id": user.id, "tenant_id": tenant_id},
        )
        
        return user
