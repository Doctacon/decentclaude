"""
Structured logging framework with multiple backend support.
"""

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .config import get_config

# Context variables for distributed tracing
_correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)
_user_context: ContextVar[Optional[str]] = ContextVar("user_context", default=None)
_operation_context: ContextVar[Optional[str]] = ContextVar("operation_context", default=None)


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": get_config().service_name,
            "environment": get_config().environment,
        }

        # Add correlation ID if available
        correlation_id = _correlation_id.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id

        # Add user context if available
        user = _user_context.get()
        if user:
            log_data["user"] = user

        # Add operation context if available
        operation = _operation_context.get()
        if operation:
            log_data["operation"] = operation

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from the record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add standard fields
        log_data["module"] = record.module
        log_data["function"] = record.funcName
        log_data["line"] = record.lineno

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Human-readable text formatter for console output."""

    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        level = f"{color}{record.levelname:8s}{reset}"
        message = record.getMessage()

        # Build context string
        context_parts = []
        correlation_id = _correlation_id.get()
        if correlation_id:
            context_parts.append(f"id={correlation_id[:8]}")

        operation = _operation_context.get()
        if operation:
            context_parts.append(f"op={operation}")

        user = _user_context.get()
        if user:
            context_parts.append(f"user={user}")

        context = f" [{', '.join(context_parts)}]" if context_parts else ""

        # Add extra fields if present
        extra = ""
        if hasattr(record, "extra_fields"):
            extra_fields = " ".join(f"{k}={v}" for k, v in record.extra_fields.items())
            extra = f" | {extra_fields}"

        return f"{timestamp} {level} {message}{context}{extra}"


class StructuredLogger:
    """Logger with structured logging support and context management."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name

    def _log(self, level: int, message: str, **kwargs: Any) -> None:
        """Internal log method that adds extra fields."""
        extra_fields = {k: v for k, v in kwargs.items() if v is not None}
        extra = {"extra_fields": extra_fields} if extra_fields else {}
        self.logger.log(level, message, extra=extra)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug message with optional structured fields."""
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info message with optional structured fields."""
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning message with optional structured fields."""
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error message with optional structured fields."""
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log critical message with optional structured fields."""
        self._log(logging.CRITICAL, message, **kwargs)

    def exception(self, message: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        extra_fields = {k: v for k, v in kwargs.items() if v is not None}
        extra = {"extra_fields": extra_fields} if extra_fields else {}
        self.logger.exception(message, extra=extra)


def init_logging() -> None:
    """Initialize logging with configured backends."""
    config = get_config()

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.log_level.upper()))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    if config.log_format == "json":
        console_handler.setFormatter(StructuredFormatter())
    else:
        console_handler.setFormatter(TextFormatter())
    root_logger.addHandler(console_handler)

    # Add file handler if configured
    if config.log_file:
        log_path = Path(config.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(config.log_file)
        file_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(file_handler)

    # Log initialization
    logger = get_logger(__name__)
    logger.info(
        "Logging initialized",
        log_level=config.log_level,
        log_format=config.log_format,
        environment=config.environment,
    )


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)


def set_correlation_id(correlation_id: Optional[str] = None) -> str:
    """Set correlation ID for distributed tracing. Generates one if not provided."""
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    _correlation_id.set(correlation_id)
    return correlation_id


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID."""
    return _correlation_id.get()


def set_user_context(user: Optional[str]) -> None:
    """Set user context for logging."""
    _user_context.set(user)


def set_operation_context(operation: Optional[str]) -> None:
    """Set operation context for logging."""
    _operation_context.set(operation)


class LogContext:
    """Context manager for setting logging context."""

    def __init__(
        self,
        operation: Optional[str] = None,
        user: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ):
        self.operation = operation
        self.user = user
        self.correlation_id = correlation_id
        self.prev_operation = None
        self.prev_user = None
        self.prev_correlation_id = None

    def __enter__(self):
        if self.operation:
            self.prev_operation = _operation_context.get()
            set_operation_context(self.operation)

        if self.user:
            self.prev_user = _user_context.get()
            set_user_context(self.user)

        if self.correlation_id:
            self.prev_correlation_id = _correlation_id.get()
            set_correlation_id(self.correlation_id)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.operation:
            set_operation_context(self.prev_operation)

        if self.user:
            set_user_context(self.prev_user)

        if self.correlation_id:
            set_correlation_id(self.prev_correlation_id)
