"""API v1 router aggregation."""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, health, users, tenants, tasks

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(health.router, tags=["health"])
