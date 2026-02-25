"""Custom decorators for caching and other cross-cutting concerns."""

from functools import wraps
from typing import Callable, Optional, Any
import hashlib
import json
from app.services.cache import cache_service


def cached(
    ttl: int = 300,
    key_prefix: str = "",
    tenant_aware: bool = False,
) -> Callable:
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds (default: 300)
        key_prefix: Prefix for cache key (default: function name)
        tenant_aware: Whether to include tenant_id in cache key
        
    Example:
        @cached(ttl=600, key_prefix="user")
        def get_user(user_id: int) -> User:
            return db.query(User).filter(User.id == user_id).first()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key from function name and arguments
            prefix = key_prefix or func.__name__
            
            # Create a hash of arguments for the cache key
            args_str = json.dumps(
                {"args": [str(arg) for arg in args], "kwargs": {k: str(v) for k, v in kwargs.items()}},
                sort_keys=True,
            )
            args_hash = hashlib.md5(args_str.encode()).hexdigest()
            cache_key = f"{prefix}:{args_hash}"
            
            # Extract tenant_id if tenant_aware
            tenant_id = None
            if tenant_aware:
                tenant_id = kwargs.get("tenant_id")
            
            # Try to get from cache
            cached_value = cache_service.get(cache_key, tenant_id=tenant_id)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl=ttl, tenant_id=tenant_id)
            return result
        
        return wrapper
    return decorator


def cache_invalidate(
    key_pattern: str,
    tenant_aware: bool = False,
) -> Callable:
    """
    Decorator for invalidating cache entries after function execution.
    
    Args:
        key_pattern: Pattern for cache keys to invalidate (e.g., "user:*")
        tenant_aware: Whether to include tenant_id in cache key
        
    Example:
        @cache_invalidate(key_pattern="user:*", tenant_aware=True)
        def update_user(user_id: int, data: dict, tenant_id: int) -> User:
            # Update user logic
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Execute function first
            result = func(*args, **kwargs)
            
            # Extract tenant_id if tenant_aware
            tenant_id = None
            if tenant_aware:
                tenant_id = kwargs.get("tenant_id")
            
            # Invalidate cache
            cache_service.delete_pattern(key_pattern, tenant_id=tenant_id)
            
            return result
        
        return wrapper
    return decorator


def async_cached(
    ttl: int = 300,
    key_prefix: str = "",
    tenant_aware: bool = False,
) -> Callable:
    """
    Decorator for caching async function results.
    
    Args:
        ttl: Time to live in seconds (default: 300)
        key_prefix: Prefix for cache key (default: function name)
        tenant_aware: Whether to include tenant_id in cache key
        
    Example:
        @async_cached(ttl=600, key_prefix="user")
        async def get_user(user_id: int) -> User:
            return await db.query(User).filter(User.id == user_id).first()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key from function name and arguments
            prefix = key_prefix or func.__name__
            
            # Create a hash of arguments for the cache key
            args_str = json.dumps(
                {"args": [str(arg) for arg in args], "kwargs": {k: str(v) for k, v in kwargs.items()}},
                sort_keys=True,
            )
            args_hash = hashlib.md5(args_str.encode()).hexdigest()
            cache_key = f"{prefix}:{args_hash}"
            
            # Extract tenant_id if tenant_aware
            tenant_id = None
            if tenant_aware:
                tenant_id = kwargs.get("tenant_id")
            
            # Try to get from cache
            cached_value = cache_service.get(cache_key, tenant_id=tenant_id)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl=ttl, tenant_id=tenant_id)
            return result
        
        return wrapper
    return decorator
