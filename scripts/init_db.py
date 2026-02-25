"""Initialize database with default roles and permissions."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.models.role import Role, Permission
from app.models.tenant import Tenant
from app.core.logging import get_logger

logger = get_logger(__name__)


def create_default_roles():
    """Create default roles and permissions."""
    db = SessionLocal()
    
    try:
        # Create permissions
        permissions = [
            # User permissions
            Permission(resource="users", action="read"),
            Permission(resource="users", action="write"),
            Permission(resource="users", action="delete"),
            Permission(resource="users", action="admin"),
            # Tenant permissions
            Permission(resource="tenants", action="read"),
            Permission(resource="tenants", action="write"),
            Permission(resource="tenants", action="delete"),
            Permission(resource="tenants", action="admin"),
            # Task permissions
            Permission(resource="tasks", action="read"),
            Permission(resource="tasks", action="write"),
            Permission(resource="tasks", action="delete"),
        ]
        
        for perm in permissions:
            existing = db.query(Permission).filter(
                Permission.resource == perm.resource,
                Permission.action == perm.action,
            ).first()
            if not existing:
                db.add(perm)
                logger.info(f"Created permission: {perm.resource}:{perm.action}")
        
        db.commit()
        
        # Create roles
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator with full access")
            # Admin gets all permissions
            admin_role.permissions = db.query(Permission).all()
            db.add(admin_role)
            logger.info("Created admin role")
        
        user_role = db.query(Role).filter(Role.name == "user").first()
        if not user_role:
            user_role = Role(name="user", description="Standard user")
            # User gets read permissions
            user_role.permissions = db.query(Permission).filter(
                Permission.action == "read"
            ).all()
            db.add(user_role)
            logger.info("Created user role")
        
        guest_role = db.query(Role).filter(Role.name == "guest").first()
        if not guest_role:
            guest_role = Role(name="guest", description="Guest with limited access")
            db.add(guest_role)
            logger.info("Created guest role")
        
        db.commit()
        logger.info("Default roles and permissions created successfully")
        
    except Exception as e:
        logger.error(f"Error creating default roles: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def create_default_tenant():
    """Create a default tenant for testing."""
    db = SessionLocal()
    
    try:
        tenant = db.query(Tenant).filter(Tenant.slug == "default").first()
        if not tenant:
            tenant = Tenant(
                name="Default Tenant",
                slug="default",
                settings={"tier": "standard"},
            )
            db.add(tenant)
            db.commit()
            logger.info("Created default tenant")
        else:
            logger.info("Default tenant already exists")
    except Exception as e:
        logger.error(f"Error creating default tenant: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Initializing database...")
    create_default_roles()
    create_default_tenant()
    logger.info("Database initialization complete")
