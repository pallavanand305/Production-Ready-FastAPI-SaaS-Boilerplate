"""Health check API endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.cache import cache_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "healthy"}


@router.get("/health/ready", status_code=status.HTTP_200_OK)
def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness probe - checks if application is ready to serve requests.
    
    Checks:
    - Database connectivity
    - Redis connectivity
    
    Args:
        db: Database session
        
    Returns:
        Readiness status with dependency checks
    """
    checks = {
        "database": False,
        "cache": False,
    }
    
    # Check database connectivity
    try:
        db.execute("SELECT 1")
        checks["database"] = True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
    
    # Check Redis connectivity
    try:
        if cache_service.is_available():
            checks["cache"] = True
    except Exception as e:
        logger.error(f"Cache health check failed: {str(e)}")
    
    # Determine overall status
    all_healthy = all(checks.values())
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
    }


@router.get("/health/live", status_code=status.HTTP_200_OK)
def liveness_check():
    """
    Liveness probe - checks if application is running.
    
    Returns:
        Liveness status
    """
    return {"status": "alive"}
