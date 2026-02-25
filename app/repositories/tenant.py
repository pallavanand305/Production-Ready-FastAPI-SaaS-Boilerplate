"""Tenant repository with tenant-specific queries."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.tenant import Tenant
from app.repositories.base import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    """Repository for Tenant model with tenant-specific methods."""

    def __init__(self, db: Session):
        """Initialize tenant repository."""
        super().__init__(Tenant, db)

    def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """
        Get tenant by slug.
        
        Args:
            slug: Tenant slug (URL-friendly identifier)
            
        Returns:
            Tenant instance or None if not found
        """
        query = select(Tenant).where(
            Tenant.slug == slug,
            Tenant.is_deleted == False,
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def get_by_name(self, name: str) -> Optional[Tenant]:
        """
        Get tenant by name.
        
        Args:
            name: Tenant name
            
        Returns:
            Tenant instance or None if not found
        """
        query = select(Tenant).where(
            Tenant.name == name,
            Tenant.is_deleted == False,
        )
        result = self.db.execute(query)
        return result.scalar_one_or_none()

    def update_settings(self, tenant_id: int, settings: dict) -> Optional[Tenant]:
        """
        Update tenant settings.
        
        Args:
            tenant_id: Tenant ID
            settings: Dictionary of settings to update
            
        Returns:
            Updated tenant instance or None if not found
        """
        tenant = self.get(id=tenant_id)
        if tenant is None:
            return None
        
        # Merge new settings with existing settings
        current_settings = tenant.settings or {}
        current_settings.update(settings)
        tenant.settings = current_settings
        
        self.db.commit()
        self.db.refresh(tenant)
        return tenant

    def get_setting(self, tenant_id: int, key: str, default: any = None) -> any:
        """
        Get a specific setting value for a tenant.
        
        Args:
            tenant_id: Tenant ID
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        tenant = self.get(id=tenant_id)
        if tenant is None or tenant.settings is None:
            return default
        
        return tenant.settings.get(key, default)
