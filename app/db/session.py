"""Database session management with SQLAlchemy."""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import Pool
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.DB_ECHO,
    future=True,  # Use SQLAlchemy 2.0 style
)


# Event listener to log connection pool statistics
@event.listens_for(Pool, "connect")
def receive_connect(dbapi_conn: any, connection_record: any) -> None:
    """Log database connection events."""
    logger.debug("Database connection established")


@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_conn: any, connection_record: any, connection_proxy: any) -> None:
    """Log connection checkout from pool."""
    logger.debug("Connection checked out from pool")


# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,  # Use SQLAlchemy 2.0 style
)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for database sessions.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Database session closed")


def init_db() -> None:
    """Initialize database connection and verify connectivity."""
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}", exc_info=True)
        raise
