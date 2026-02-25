"""Celery tasks for background processing."""

from typing import Dict, Any
from celery import Task
from app.worker.celery_app import celery_app
from app.core.logging import get_logger

logger = get_logger(__name__)


class BaseTask(Task):
    """Base task with automatic retry on failure."""

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes
    retry_jitter = True


@celery_app.task(base=BaseTask, bind=True, name="app.worker.tasks.send_email")
def send_email(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
    """
    Send email asynchronously.
    
    Args:
        recipient: Email recipient
        subject: Email subject
        body: Email body
        
    Returns:
        Result dictionary
    """
    try:
        logger.info(f"Sending email to {recipient}: {subject}")
        
        # TODO: Implement actual email sending logic
        # For now, just log the email
        logger.info(f"Email sent successfully to {recipient}")
        
        return {
            "status": "success",
            "recipient": recipient,
            "subject": subject,
        }
    except Exception as exc:
        logger.error(f"Failed to send email to {recipient}: {str(exc)}")
        self.retry(exc=exc)


@celery_app.task(base=BaseTask, bind=True, name="app.worker.tasks.process_data")
def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process data asynchronously.
    
    Args:
        data: Data to process
        
    Returns:
        Processed data
    """
    try:
        logger.info(f"Processing data: {data}")
        
        # TODO: Implement actual data processing logic
        # For now, just return the data
        processed_data = {
            "original": data,
            "processed": True,
            "timestamp": "2024-01-01T00:00:00Z",
        }
        
        logger.info("Data processed successfully")
        return processed_data
    except Exception as exc:
        logger.error(f"Failed to process data: {str(exc)}")
        self.retry(exc=exc)


@celery_app.task(name="app.worker.tasks.cleanup_old_tokens")
def cleanup_old_tokens() -> Dict[str, Any]:
    """
    Cleanup expired refresh tokens (scheduled task).
    
    Returns:
        Cleanup result
    """
    from datetime import datetime
    from app.db.session import SessionLocal
    from app.models.refresh_token import RefreshToken
    
    logger.info("Starting cleanup of expired refresh tokens")
    
    db = SessionLocal()
    try:
        # Delete expired tokens
        deleted_count = db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.utcnow()
        ).delete()
        
        db.commit()
        logger.info(f"Cleaned up {deleted_count} expired refresh tokens")
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
        }
    except Exception as e:
        logger.error(f"Failed to cleanup tokens: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
