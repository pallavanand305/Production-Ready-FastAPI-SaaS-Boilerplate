"""Redis cache service with graceful degradation."""

import json
from typing import Optional, Any
from datetime import timedelta
import redis
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """
    Redis cache service with tenant namespacing and graceful degradation.
    
    Features:
    - Cache-aside pattern
    - TTL management
    - Tenant-scoped cache keys
    - Graceful degradation when Redis unavailable
    - JSON serialization
    """

    def __init__(self):
        """Initialize Redis client with connection pooling."""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
            )
            # Test connection
            self.redis.ping()
            self._available = True
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}. Cache will be disabled.")
            self.redis = None
            self._available = False

    def is_available(self) -> bool:
        """Check if Redis is available."""
        if not self._available or self.redis is None:
            return False
        
        try:
            self.redis.ping()
            return True
        except Exception:
            self._available = False
            return False

    def _make_key(self, key: str, tenant_id: Optional[int] = None) -> str:
        """
        Generate namespaced cache key.
        
        Args:
            key: Base cache key
            tenant_id: Optional tenant ID for namespacing
            
        Returns:
            Namespaced cache key
        """
        if tenant_id is not None:
            return f"tenant:{tenant_id}:{key}"
        return f"global:{key}"

    def get(self, key: str, tenant_id: Optional[int] = None) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            tenant_id: Optional tenant ID for namespacing
            
        Returns:
            Cached value or None if not found or cache unavailable
        """
        if not self.is_available():
            return None
        
        try:
            cache_key = self._make_key(key, tenant_id)
            value = self.redis.get(cache_key)
            
            if value is None:
                logger.debug(f"Cache miss: {cache_key}")
                return None
            
            logger.debug(f"Cache hit: {cache_key}")
            return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error: {str(e)}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tenant_id: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache with optional TTL.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (None for default TTL)
            tenant_id: Optional tenant ID for namespacing
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            cache_key = self._make_key(key, tenant_id)
            serialized_value = json.dumps(value)
            
            if ttl is None:
                ttl = settings.CACHE_DEFAULT_TTL
            
            self.redis.setex(cache_key, ttl, serialized_value)
            logger.debug(f"Cache set: {cache_key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {str(e)}")
            return False

    def delete(self, key: str, tenant_id: Optional[int] = None) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            tenant_id: Optional tenant ID for namespacing
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            cache_key = self._make_key(key, tenant_id)
            result = self.redis.delete(cache_key)
            logger.debug(f"Cache delete: {cache_key}")
            return result > 0
        except Exception as e:
            logger.warning(f"Cache delete error: {str(e)}")
            return False

    def delete_pattern(self, pattern: str, tenant_id: Optional[int] = None) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Pattern to match (e.g., "user:*")
            tenant_id: Optional tenant ID for namespacing
            
        Returns:
            Number of keys deleted
        """
        if not self.is_available():
            return 0
        
        try:
            cache_pattern = self._make_key(pattern, tenant_id)
            keys = self.redis.keys(cache_pattern)
            
            if not keys:
                return 0
            
            deleted = self.redis.delete(*keys)
            logger.debug(f"Cache delete pattern: {cache_pattern} ({deleted} keys)")
            return deleted
        except Exception as e:
            logger.warning(f"Cache delete pattern error: {str(e)}")
            return 0

    def exists(self, key: str, tenant_id: Optional[int] = None) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            tenant_id: Optional tenant ID for namespacing
            
        Returns:
            True if key exists, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            cache_key = self._make_key(key, tenant_id)
            return self.redis.exists(cache_key) > 0
        except Exception as e:
            logger.warning(f"Cache exists error: {str(e)}")
            return False

    def increment(
        self,
        key: str,
        amount: int = 1,
        tenant_id: Optional[int] = None,
    ) -> Optional[int]:
        """
        Increment a counter in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment by
            tenant_id: Optional tenant ID for namespacing
            
        Returns:
            New value after increment or None if failed
        """
        if not self.is_available():
            return None
        
        try:
            cache_key = self._make_key(key, tenant_id)
            return self.redis.incrby(cache_key, amount)
        except Exception as e:
            logger.warning(f"Cache increment error: {str(e)}")
            return None

    def expire(self, key: str, ttl: int, tenant_id: Optional[int] = None) -> bool:
        """
        Set expiration time for a key.
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
            tenant_id: Optional tenant ID for namespacing
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            cache_key = self._make_key(key, tenant_id)
            return self.redis.expire(cache_key, ttl)
        except Exception as e:
            logger.warning(f"Cache expire error: {str(e)}")
            return False

    def flush_tenant(self, tenant_id: int) -> int:
        """
        Flush all cache entries for a specific tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Number of keys deleted
        """
        return self.delete_pattern("*", tenant_id=tenant_id)

    def flush_all(self) -> bool:
        """
        Flush entire cache (use with caution).
        
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            self.redis.flushdb()
            logger.warning("Cache flushed (all keys deleted)")
            return True
        except Exception as e:
            logger.error(f"Cache flush error: {str(e)}")
            return False


# Global cache service instance
cache_service = CacheService()
