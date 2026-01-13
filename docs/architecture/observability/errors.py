"""
Error tracking and alerting with Sentry integration.
"""

import sys
import traceback
from functools import wraps
from typing import Any, Callable, Optional

from .config import get_config
from .logger import get_logger

logger = get_logger(__name__)


class ErrorTracker:
    """Error tracking and reporting to Sentry."""

    def __init__(self):
        self.config = get_config()
        self.sentry = None
        self._initialize_sentry()

    def _initialize_sentry(self) -> None:
        """Initialize Sentry SDK if enabled."""
        if not self.config.sentry_enabled:
            logger.info("Sentry error tracking disabled")
            return

        try:
            import sentry_sdk

            sentry_sdk.init(
                dsn=self.config.sentry_dsn,
                environment=self.config.sentry_environment,
                traces_sample_rate=self.config.sentry_traces_sample_rate,
                release=f"{self.config.service_name}@1.0.0",
                server_name=self.config.service_name,
                attach_stacktrace=True,
                send_default_pii=False,
            )

            self.sentry = sentry_sdk
            logger.info(
                "Sentry initialized",
                environment=self.config.sentry_environment,
                traces_sample_rate=self.config.sentry_traces_sample_rate,
            )
        except ImportError:
            logger.warning("sentry-sdk not installed, error tracking disabled")
        except Exception as e:
            logger.error("Failed to initialize Sentry", error=str(e))

    def capture_exception(
        self,
        error: Exception,
        context: Optional[dict[str, Any]] = None,
        level: str = "error",
    ) -> Optional[str]:
        """
        Capture an exception and send to Sentry.

        Args:
            error: The exception to capture
            context: Additional context to attach to the error
            level: Severity level (debug, info, warning, error, fatal)

        Returns:
            Event ID from Sentry, or None if Sentry is disabled
        """
        context = context or {}

        # Log the error
        logger.error(
            f"Exception captured: {type(error).__name__}: {str(error)}",
            error_type=type(error).__name__,
            error_message=str(error),
            **context,
        )

        # Send to Sentry if enabled
        if self.sentry:
            with self.sentry.push_scope() as scope:
                # Set level
                scope.level = level

                # Add context
                for key, value in context.items():
                    scope.set_tag(key, str(value))

                # Add extra data
                scope.set_context("additional_context", context)

                # Capture exception
                event_id = self.sentry.capture_exception(error)
                logger.debug("Exception sent to Sentry", event_id=event_id)
                return event_id

        return None

    def capture_message(
        self,
        message: str,
        level: str = "info",
        context: Optional[dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Capture a message and send to Sentry.

        Args:
            message: The message to capture
            level: Severity level (debug, info, warning, error, fatal)
            context: Additional context to attach

        Returns:
            Event ID from Sentry, or None if Sentry is disabled
        """
        context = context or {}

        # Log the message
        log_method = getattr(logger, level, logger.info)
        log_method(message, **context)

        # Send to Sentry if enabled
        if self.sentry:
            with self.sentry.push_scope() as scope:
                # Add context
                for key, value in context.items():
                    scope.set_tag(key, str(value))

                # Capture message
                event_id = self.sentry.capture_message(message, level=level)
                return event_id

        return None

    def set_user_context(self, user_id: str, email: Optional[str] = None, username: Optional[str] = None) -> None:
        """Set user context for error reports."""
        if self.sentry:
            self.sentry.set_user({
                "id": user_id,
                "email": email,
                "username": username,
            })

    def set_context(self, key: str, value: dict[str, Any]) -> None:
        """Set additional context for error reports."""
        if self.sentry:
            self.sentry.set_context(key, value)

    def add_breadcrumb(
        self,
        message: str,
        category: str = "default",
        level: str = "info",
        data: Optional[dict[str, Any]] = None,
    ) -> None:
        """Add a breadcrumb for error context."""
        if self.sentry:
            self.sentry.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                data=data or {},
            )


# Global error tracker
_tracker: Optional[ErrorTracker] = None


def get_error_tracker() -> ErrorTracker:
    """Get or create the global error tracker."""
    global _tracker
    if _tracker is None:
        _tracker = ErrorTracker()
    return _tracker


def init_error_tracking() -> None:
    """Initialize error tracking (creates the global tracker)."""
    get_error_tracker()
    logger.info("Error tracking initialized")


def capture_exception(
    error: Exception,
    context: Optional[dict[str, Any]] = None,
    level: str = "error",
) -> Optional[str]:
    """Capture an exception and send to error tracking service."""
    return get_error_tracker().capture_exception(error, context, level)


def capture_message(
    message: str,
    level: str = "info",
    context: Optional[dict[str, Any]] = None,
) -> Optional[str]:
    """Capture a message and send to error tracking service."""
    return get_error_tracker().capture_message(message, level, context)


def with_error_tracking(
    context: Optional[dict[str, Any]] = None,
    reraise: bool = True,
):
    """
    Decorator to automatically track errors in a function.

    Args:
        context: Additional context to attach to errors
        reraise: Whether to reraise the exception after capturing

    Usage:
        @with_error_tracking(context={"module": "data_quality"})
        def my_function():
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Capture the exception
                error_context = {
                    "function": func.__name__,
                    "module": func.__module__,
                }
                if context:
                    error_context.update(context)

                capture_exception(e, context=error_context)

                # Reraise if configured
                if reraise:
                    raise

        return wrapper

    return decorator


def setup_exception_hook() -> None:
    """Set up global exception hook to capture unhandled exceptions."""
    original_hook = sys.excepthook

    def exception_hook(exc_type, exc_value, exc_traceback):
        """Custom exception hook that captures to Sentry."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't capture keyboard interrupts
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Capture the exception
        capture_exception(
            exc_value,
            context={
                "exc_type": exc_type.__name__,
                "traceback": "".join(traceback.format_tb(exc_traceback)),
            },
            level="fatal",
        )

        # Call original hook
        original_hook(exc_type, exc_value, exc_traceback)

    sys.excepthook = exception_hook
    logger.debug("Global exception hook installed")
