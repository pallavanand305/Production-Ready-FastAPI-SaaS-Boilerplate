"""Structured JSON logging configuration."""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    SENSITIVE_FIELDS = {
        "password",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "api_key",
        "authorization",
        "credit_card",
        "ssn",
        "hashed_password",
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra context from record
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "tenant_id"):
            log_data["tenant_id"] = record.tenant_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info),
            }

        # Sanitize sensitive data
        log_data = self._sanitize_data(log_data)

        return json.dumps(log_data)

    def _sanitize_data(self, data: Any) -> Any:
        """Recursively sanitize sensitive data from logs."""
        if isinstance(data, dict):
            return {
                key: "***REDACTED***" if key.lower() in self.SENSITIVE_FIELDS else self._sanitize_data(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._sanitize_data(item) for item in data]
        elif isinstance(data, str):
            # Check if string contains sensitive patterns
            lower_data = data.lower()
            for field in self.SENSITIVE_FIELDS:
                if field in lower_data:
                    return "***REDACTED***"
        return data


def setup_logging() -> None:
    """Configure application logging with JSON formatter."""
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Set specific log levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)


# Initialize logging on module import
setup_logging()
