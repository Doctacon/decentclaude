"""
Metrics collection and monitoring with Prometheus and Datadog support.
"""

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Optional

from .config import get_config
from .logger import get_logger

logger = get_logger(__name__)


@dataclass
class MetricValue:
    """Represents a metric data point."""

    name: str
    value: float
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metric_type: str = "gauge"  # gauge, counter, histogram


class MetricsCollector:
    """Central metrics collection and dispatch to backends."""

    def __init__(self):
        self.config = get_config()
        self.prometheus_client = None
        self.datadog_client = None
        self._initialize_backends()

    def _initialize_backends(self) -> None:
        """Initialize metrics backends based on configuration."""
        # Initialize Prometheus if enabled
        if self.config.metrics_enabled:
            try:
                from prometheus_client import Counter, Gauge, Histogram, start_http_server

                self._prometheus_counters = {}
                self._prometheus_gauges = {}
                self._prometheus_histograms = {}

                # Start Prometheus metrics server
                try:
                    start_http_server(self.config.prometheus_port)
                    logger.info(
                        "Prometheus metrics server started",
                        port=self.config.prometheus_port,
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to start Prometheus server",
                        error=str(e),
                        port=self.config.prometheus_port,
                    )

                self.prometheus_client = {
                    "Counter": Counter,
                    "Gauge": Gauge,
                    "Histogram": Histogram,
                }
            except ImportError:
                logger.warning("prometheus_client not installed, Prometheus metrics disabled")

        # Initialize Datadog if enabled
        if self.config.datadog_enabled:
            try:
                from datadog import initialize, statsd

                initialize(
                    api_key=self.config.datadog_api_key,
                    app_key=None,
                    statsd_host="127.0.0.1",
                    statsd_port=8125,
                )
                self.datadog_client = statsd
                logger.info(
                    "Datadog client initialized",
                    service=self.config.datadog_service,
                    environment=self.config.datadog_env,
                )
            except ImportError:
                logger.warning("datadog package not installed, Datadog metrics disabled")
            except Exception as e:
                logger.error("Failed to initialize Datadog", error=str(e))

    def _get_prometheus_metric(self, name: str, metric_type: str, description: str = ""):
        """Get or create a Prometheus metric."""
        if not self.prometheus_client:
            return None

        metric_class = self.prometheus_client.get(metric_type)
        if not metric_class:
            return None

        cache_key = f"{metric_type}_{name}"
        cache = getattr(self, f"_prometheus_{metric_type.lower()}s")

        if cache_key not in cache:
            # Create new metric
            cache[cache_key] = metric_class(
                name.replace(".", "_").replace("-", "_"),
                description or f"{name} metric",
                labelnames=["environment", "service"],
            )

        return cache[cache_key]

    def record_counter(self, name: str, value: float = 1, tags: Optional[dict[str, str]] = None) -> None:
        """Record a counter metric (monotonically increasing)."""
        tags = tags or {}

        # Send to Prometheus
        if self.prometheus_client:
            metric = self._get_prometheus_metric(name, "Counter")
            if metric:
                metric.labels(
                    environment=self.config.environment,
                    service=self.config.service_name,
                ).inc(value)

        # Send to Datadog
        if self.datadog_client:
            dd_tags = [f"{k}:{v}" for k, v in tags.items()]
            dd_tags.extend([
                f"environment:{self.config.datadog_env}",
                f"service:{self.config.datadog_service}",
            ])
            self.datadog_client.increment(name, value=value, tags=dd_tags)

    def record_gauge(self, name: str, value: float, tags: Optional[dict[str, str]] = None) -> None:
        """Record a gauge metric (can go up or down)."""
        tags = tags or {}

        # Send to Prometheus
        if self.prometheus_client:
            metric = self._get_prometheus_metric(name, "Gauge")
            if metric:
                metric.labels(
                    environment=self.config.environment,
                    service=self.config.service_name,
                ).set(value)

        # Send to Datadog
        if self.datadog_client:
            dd_tags = [f"{k}:{v}" for k, v in tags.items()]
            dd_tags.extend([
                f"environment:{self.config.datadog_env}",
                f"service:{self.config.datadog_service}",
            ])
            self.datadog_client.gauge(name, value, tags=dd_tags)

    def record_histogram(self, name: str, value: float, tags: Optional[dict[str, str]] = None) -> None:
        """Record a histogram metric (distribution of values)."""
        tags = tags or {}

        # Send to Prometheus
        if self.prometheus_client:
            metric = self._get_prometheus_metric(name, "Histogram")
            if metric:
                metric.labels(
                    environment=self.config.environment,
                    service=self.config.service_name,
                ).observe(value)

        # Send to Datadog
        if self.datadog_client:
            dd_tags = [f"{k}:{v}" for k, v in tags.items()]
            dd_tags.extend([
                f"environment:{self.config.datadog_env}",
                f"service:{self.config.datadog_service}",
            ])
            self.datadog_client.histogram(name, value, tags=dd_tags)


# Global metrics collector
_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create the global metrics collector."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector()
    return _collector


@contextmanager
def track_performance(
    operation: str,
    tags: Optional[dict[str, str]] = None,
    record_success: bool = True,
):
    """
    Context manager to track operation performance.

    Records:
    - operation duration
    - success/failure count
    - error count
    """
    tags = tags or {}
    collector = get_metrics_collector()
    start_time = time.time()
    success = False

    try:
        yield
        success = True
    except Exception as e:
        collector.record_counter(
            f"operation.error",
            tags={**tags, "operation": operation, "error_type": type(e).__name__},
        )
        raise
    finally:
        duration = time.time() - start_time

        # Record duration
        collector.record_histogram(
            f"operation.duration.seconds",
            duration,
            tags={**tags, "operation": operation},
        )

        # Record success/failure
        if record_success:
            if success:
                collector.record_counter(
                    f"operation.success",
                    tags={**tags, "operation": operation},
                )
            else:
                collector.record_counter(
                    f"operation.failure",
                    tags={**tags, "operation": operation},
                )

        logger.debug(
            f"Operation {operation} completed",
            duration_seconds=round(duration, 3),
            success=success,
            **tags,
        )


def track_cost(
    operation: str,
    bytes_processed: int,
    estimated_cost_usd: float,
    tags: Optional[dict[str, str]] = None,
) -> None:
    """
    Track BigQuery query cost metrics.

    Args:
        operation: Name of the operation
        bytes_processed: Number of bytes processed by the query
        estimated_cost_usd: Estimated cost in USD
        tags: Additional tags for the metric
    """
    tags = tags or {}
    collector = get_metrics_collector()
    config = get_config()

    # Record bytes processed
    collector.record_histogram(
        "bigquery.bytes_processed",
        bytes_processed,
        tags={**tags, "operation": operation},
    )

    # Record cost
    collector.record_histogram(
        "bigquery.cost.usd",
        estimated_cost_usd,
        tags={**tags, "operation": operation},
    )

    # Record total cost counter
    collector.record_counter(
        "bigquery.total_cost.usd",
        estimated_cost_usd,
        tags={**tags, "operation": operation},
    )

    # Log cost information
    logger.info(
        f"BigQuery cost tracked for {operation}",
        bytes_processed=bytes_processed,
        estimated_cost_usd=round(estimated_cost_usd, 4),
        **tags,
    )

    # Alert if cost exceeds threshold
    if config.cost_tracking_enabled and estimated_cost_usd > config.cost_alert_threshold_usd:
        logger.warning(
            f"High cost alert for {operation}",
            bytes_processed=bytes_processed,
            estimated_cost_usd=round(estimated_cost_usd, 4),
            threshold_usd=config.cost_alert_threshold_usd,
            **tags,
        )
        collector.record_counter(
            "bigquery.cost_alert",
            tags={**tags, "operation": operation},
        )


def track_query_performance(
    query_type: str,
    duration_seconds: float,
    rows_returned: int,
    bytes_processed: int,
    tags: Optional[dict[str, str]] = None,
) -> None:
    """
    Track BigQuery query performance metrics.

    Args:
        query_type: Type of query (e.g., 'select', 'insert', 'update')
        duration_seconds: Query execution time in seconds
        rows_returned: Number of rows returned
        bytes_processed: Number of bytes processed
        tags: Additional tags for the metric
    """
    tags = tags or {}
    collector = get_metrics_collector()

    # Record query duration
    collector.record_histogram(
        "bigquery.query.duration.seconds",
        duration_seconds,
        tags={**tags, "query_type": query_type},
    )

    # Record rows returned
    collector.record_histogram(
        "bigquery.query.rows_returned",
        rows_returned,
        tags={**tags, "query_type": query_type},
    )

    # Record bytes processed
    collector.record_histogram(
        "bigquery.query.bytes_processed",
        bytes_processed,
        tags={**tags, "query_type": query_type},
    )

    # Record query count
    collector.record_counter(
        "bigquery.query.count",
        tags={**tags, "query_type": query_type},
    )

    logger.debug(
        f"Query performance tracked",
        query_type=query_type,
        duration_seconds=round(duration_seconds, 3),
        rows_returned=rows_returned,
        bytes_processed=bytes_processed,
        **tags,
    )


def performance_monitor(operation: Optional[str] = None, tags: Optional[dict[str, str]] = None):
    """
    Decorator to monitor function performance.

    Usage:
        @performance_monitor(operation="my_function")
        def my_function():
            pass
    """

    def decorator(func: Callable) -> Callable:
        op_name = operation or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            with track_performance(op_name, tags=tags):
                return func(*args, **kwargs)

        return wrapper

    return decorator
