"""Rate limiting middleware using token bucket algorithm."""

from datetime import datetime
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.cache import cache_service
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm with Redis.
    
    Features:
    - Per-user rate limiting (based on JWT subject)
    - Per-IP rate limiting for unauthenticated requests
    - Configurable rate limits per endpoint
    - Tiered rate limits (premium users get higher limits)
    - Returns 429 with Retry-After header when exceeded
    """

    def __init__(self, app, requests: int = None, window: int = None):
        """
        Initialize rate limiter.
        
        Args:
            app: FastAPI application
            requests: Number of requests allowed per window
            window: Time window in seconds
        """
        super().__init__(app)
        self.requests = requests or settings.RATE_LIMIT_REQUESTS
        self.window = window or settings.RATE_LIMIT_WINDOW

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit before processing request."""
        # Skip rate limiting for health check endpoints
        if request.url.path.startswith("/health"):
            return await call_next(request)
        
        # Determine rate limit key (user_id or IP)
        user_id = getattr(request.state, "user_id", None)
        tenant_id = getattr(request.state, "tenant_id", None)
        
        if user_id:
            rate_limit_key = f"rate_limit:user:{user_id}"
            # Check if user has premium tier (higher rate limit)
            limit = self._get_user_rate_limit(tenant_id)
        else:
            # Use IP address for unauthenticated requests
            client_ip = request.client.host if request.client else "unknown"
            rate_limit_key = f"rate_limit:ip:{client_ip}"
            limit = self.requests
        
        # Check rate limit
        if not await self._check_rate_limit(rate_limit_key, limit):
            logger.warning(
                f"Rate limit exceeded",
                extra={
                    "rate_limit_key": rate_limit_key,
                    "user_id": user_id,
                    "tenant_id": tenant_id,
                    "request_id": getattr(request.state, "request_id", None),
                },
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(self.window)},
            )
        
        response = await call_next(request)
        return response

    async def _check_rate_limit(self, key: str, limit: int) -> bool:
        """
        Check if request is within rate limit using token bucket algorithm.
        
        Args:
            key: Rate limit key
            limit: Maximum number of requests allowed
            
        Returns:
            True if within limit, False otherwise
        """
        if not cache_service.is_available():
            # If Redis is unavailable, allow request (fail open)
            logger.warning("Rate limiting disabled: Redis unavailable")
            return True
        
        try:
            now = datetime.utcnow().timestamp()
            window_start = now - self.window
            
            # Use Redis sorted set for sliding window
            # Remove old entries
            cache_service.redis.zremrangebyscore(key, 0, window_start)
            
            # Count requests in current window
            request_count = cache_service.redis.zcard(key)
            
            if request_count >= limit:
                return False
            
            # Add current request
            cache_service.redis.zadd(key, {str(now): now})
            cache_service.redis.expire(key, self.window)
            
            return True
        except Exception as e:
            logger.error(f"Rate limit check error: {str(e)}")
            # Fail open if error occurs
            return True

    def _get_user_rate_limit(self, tenant_id: Optional[int]) -> int:
        """
        Get rate limit for user based on tenant tier.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Rate limit for user
        """
        if tenant_id is None:
            return self.requests
        
        # Check if tenant has premium tier
        # This would typically check tenant settings from database
        # For now, use default premium limit from settings
        try:
            from app.repositories.tenant import TenantRepository
            from app.db.session import SessionLocal
            
            db = SessionLocal()
            tenant_repo = TenantRepository(db)
            tier = tenant_repo.get_setting(tenant_id, "tier", "standard")
            db.close()
            
            if tier == "premium":
                return settings.RATE_LIMIT_PREMIUM_REQUESTS
        except Exception as e:
            logger.warning(f"Error getting tenant tier: {str(e)}")
        
        return self.requests
