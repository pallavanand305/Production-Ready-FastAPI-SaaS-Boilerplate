"""Seed database with sample data for development."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.tenant import Tenant
from app.core.security import hash_password
from app.core.logging import get_logger

logger = get_logger(__name__)


def seed_sample_users():
    """Create sample users with different roles."""
    db = SessionLocal()
    
    try:
        # Get default tenant
        tenant = db.query(Tenant).filter(Tenant.slug == "default").first()
        if not tenant:
            logger.error("Default tenant not found. Run init_db.py first.")
            return
        
        # Get roles
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        user_role = db.query(Role).filter(Role.name == "user").first()
        guest_role = db.query(Role).filter(Role.name == "guest").first()
        
        # Create admin user
        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@example.com",
                hashed_password=hash_password("admin123"),
                full_name="Admin User",
                tenant_id=tenant.id,
                is_active=True,
            )
            if admin_role:
                admin_user.roles.append(admin_role)
            db.add(admin_user)
            logger.info("Created admin user: admin@example.com / admin123")
        
        # Create regular user
        regular_user = db.query(User).filter(User.email == "user@example.com").first()
        if not regular_user:
            regular_user = User(
                email="user@example.com",
                hashed_password=hash_password("user123"),
                full_name="Regular User",
                tenant_id=tenant.id,
                is_active=True,
            )
            if user_role:
                regular_user.roles.append(user_role)
            db.add(regular_user)
            logger.info("Created regular user: user@example.com / user123")
        
        # Create guest user
        guest_user = db.query(User).filter(User.email == "guest@example.com").first()
        if not guest_user:
            guest_user = User(
                email="guest@example.com",
                hashed_password=hash_password("guest123"),
                full_name="Guest User",
                tenant_id=tenant.id,
                is_active=True,
            )
            if guest_role:
                guest_user.roles.append(guest_role)
            db.add(guest_user)
            logger.info("Created guest user: guest@example.com / guest123")
        
        db.commit()
        logger.info("Sample users created successfully")
        
    except Exception as e:
        logger.error(f"Error seeding sample users: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def seed_additional_tenants():
    """Create additional sample tenants."""
    db = SessionLocal()
    
    try:
        # Create enterprise tenant
        enterprise_tenant = db.query(Tenant).filter(Tenant.slug == "enterprise").first()
        if not enterprise_tenant:
            enterprise_tenant = Tenant(
                name="Enterprise Corp",
                slug="enterprise",
                settings={"tier": "enterprise", "max_users": 1000},
            )
            db.add(enterprise_tenant)
            logger.info("Created enterprise tenant")
        
        # Create startup tenant
        startup_tenant = db.query(Tenant).filter(Tenant.slug == "startup").first()
        if not startup_tenant:
            startup_tenant = Tenant(
                name="Startup Inc",
                slug="startup",
                settings={"tier": "standard", "max_users": 50},
            )
            db.add(startup_tenant)
            logger.info("Created startup tenant")
        
        db.commit()
        logger.info("Additional tenants created successfully")
        
    except Exception as e:
        logger.error(f"Error seeding additional tenants: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Seeding database with sample data...")
    seed_sample_users()
    seed_additional_tenants()
    logger.info("Database seeding complete")
    logger.info("\nSample credentials:")
    logger.info("  Admin: admin@example.com / admin123")
    logger.info("  User:  user@example.com / user123")
    logger.info("  Guest: guest@example.com / guest123")
