"""Security utilities for password hashing and JWT token management."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Password hashing context with bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.BCRYPT_ROUNDS,
)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.warning(f"Password verification error: {str(e)}")
        return False


def create_access_token(
    subject: str,
    tenant_id: int,
    roles: list[str],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: Subject (usually user ID)
        tenant_id: Tenant ID for multi-tenancy
        roles: List of role names
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": str(subject),
        "tenant_id": tenant_id,
        "roles": roles,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return encoded_jwt


def create_refresh_token(
    subject: str,
    tenant_id: int,
    token_id: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        subject: Subject (usually user ID)
        tenant_id: Tenant ID for multi-tenancy
        token_id: Unique token identifier (jti)
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token
    """
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": str(subject),
        "tenant_id": tenant_id,
        "jti": token_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError as e:
        logger.warning(f"Token decode error: {str(e)}")
        raise


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify a JWT token and check its type.
    
    Args:
        token: JWT token to verify
        token_type: Expected token type ("access" or "refresh")
        
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = decode_token(token)
        
        # Verify token type
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
            return None
        
        # Verify expiration
        exp = payload.get("exp")
        if exp is None or datetime.fromtimestamp(exp) < datetime.utcnow():
            logger.warning("Token expired")
            return None
        
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        return None


def get_token_subject(token: str) -> Optional[str]:
    """
    Extract subject (user ID) from token.
    
    Args:
        token: JWT token
        
    Returns:
        Subject (user ID) or None if invalid
    """
    payload = verify_token(token)
    if payload is None:
        return None
    return payload.get("sub")


def get_token_tenant_id(token: str) -> Optional[int]:
    """
    Extract tenant ID from token.
    
    Args:
        token: JWT token
        
    Returns:
        Tenant ID or None if invalid
    """
    payload = verify_token(token)
    if payload is None:
        return None
    return payload.get("tenant_id")


def get_token_roles(token: str) -> list[str]:
    """
    Extract roles from token.
    
    Args:
        token: JWT token
        
    Returns:
        List of role names (empty list if invalid)
    """
    payload = verify_token(token)
    if payload is None:
        return []
    return payload.get("roles", [])
