"""
DecentClaude Observability Framework

Comprehensive monitoring and observability for data engineering workflows.
Provides structured logging, metrics, tracing, error tracking, and health checks.
"""

from .analytics import get_analytics, track_cli_command
from .config import ObservabilityConfig, get_config, set_config
from .errors import capture_exception, init_error_tracking, with_error_tracking
from .health import HealthChecker, register_health_check, run_health_checks
from .logger import LogContext, get_logger, init_logging, set_correlation_id
from .metrics import (
    MetricsCollector,
    performance_monitor,
    track_cost,
    track_performance,
    track_query_performance,
)

__all__ = [
    "get_logger",
    "init_logging",
    "set_correlation_id",
    "LogContext",
    "MetricsCollector",
    "track_performance",
    "track_cost",
    "track_query_performance",
    "performance_monitor",
    "init_error_tracking",
    "capture_exception",
    "with_error_tracking",
    "HealthChecker",
    "register_health_check",
    "run_health_checks",
    "ObservabilityConfig",
    "get_config",
    "set_config",
    "get_analytics",
    "track_cli_command",
]

__version__ = "1.0.0"


def init_observability(config: ObservabilityConfig = None) -> None:
    """
    Initialize the complete observability framework.

    Args:
        config: Custom observability configuration (uses defaults if None)
    """
    if config:
        set_config(config)

    # Initialize all components
    init_logging()
    init_error_tracking()

    logger = get_logger(__name__)
    logger.info(
        "Observability framework initialized",
        version=__version__,
        environment=get_config().environment,
    )
