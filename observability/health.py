"""
Health check framework for system components.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

from .config import get_config
from .logger import get_logger
from .metrics import get_metrics_collector

logger = get_logger(__name__)


class HealthStatus(Enum):
    """Health check status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a health check."""

    name: str
    status: HealthStatus
    message: str = ""
    duration_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "duration_seconds": round(self.duration_seconds, 3),
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


class HealthCheck:
    """Base class for health checks."""

    def __init__(self, name: str, timeout_seconds: float = 10.0):
        self.name = name
        self.timeout_seconds = timeout_seconds

    def check(self) -> HealthCheckResult:
        """
        Perform the health check.

        Returns:
            HealthCheckResult with the check status
        """
        raise NotImplementedError


class BigQueryHealthCheck(HealthCheck):
    """Health check for BigQuery connectivity."""

    def __init__(self):
        super().__init__("bigquery", timeout_seconds=5.0)

    def check(self) -> HealthCheckResult:
        """Check BigQuery connectivity and quota."""
        start_time = time.time()

        try:
            from google.cloud import bigquery

            client = bigquery.Client()

            # Try a simple query to verify connectivity
            query = "SELECT 1 as test"
            query_job = client.query(query)
            result = list(query_job.result())

            duration = time.time() - start_time

            if result and result[0]["test"] == 1:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="BigQuery connection successful",
                    duration_seconds=duration,
                    details={"project": client.project},
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message="BigQuery query returned unexpected result",
                    duration_seconds=duration,
                )

        except ImportError:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message="BigQuery client library not installed",
                duration_seconds=time.time() - start_time,
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"BigQuery health check failed: {str(e)}",
                duration_seconds=time.time() - start_time,
                details={"error": str(e), "error_type": type(e).__name__},
            )


class SentryHealthCheck(HealthCheck):
    """Health check for Sentry error tracking."""

    def __init__(self):
        super().__init__("sentry", timeout_seconds=2.0)

    def check(self) -> HealthCheckResult:
        """Check Sentry connectivity."""
        start_time = time.time()
        config = get_config()

        if not config.sentry_enabled:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Sentry disabled",
                duration_seconds=time.time() - start_time,
            )

        try:
            import sentry_sdk

            # Check if Sentry is initialized
            client = sentry_sdk.Hub.current.client
            if client and client.dsn:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="Sentry initialized",
                    duration_seconds=time.time() - start_time,
                    details={"environment": config.sentry_environment},
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message="Sentry not properly initialized",
                    duration_seconds=time.time() - start_time,
                )

        except ImportError:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message="Sentry SDK not installed",
                duration_seconds=time.time() - start_time,
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Sentry health check failed: {str(e)}",
                duration_seconds=time.time() - start_time,
            )


class PrometheusHealthCheck(HealthCheck):
    """Health check for Prometheus metrics."""

    def __init__(self):
        super().__init__("prometheus", timeout_seconds=2.0)

    def check(self) -> HealthCheckResult:
        """Check Prometheus metrics server."""
        start_time = time.time()
        config = get_config()

        if not config.metrics_enabled:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.HEALTHY,
                message="Prometheus metrics disabled",
                duration_seconds=time.time() - start_time,
            )

        try:
            import requests

            # Try to access the Prometheus metrics endpoint
            url = f"http://localhost:{config.prometheus_port}/metrics"
            response = requests.get(url, timeout=self.timeout_seconds)

            if response.status_code == 200:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.HEALTHY,
                    message="Prometheus metrics available",
                    duration_seconds=time.time() - start_time,
                    details={"port": config.prometheus_port},
                )
            else:
                return HealthCheckResult(
                    name=self.name,
                    status=HealthStatus.UNHEALTHY,
                    message=f"Prometheus metrics server returned status {response.status_code}",
                    duration_seconds=time.time() - start_time,
                )

        except ImportError:
            # requests not available, can't check HTTP endpoint
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.DEGRADED,
                message="Cannot verify Prometheus (requests library not installed)",
                duration_seconds=time.time() - start_time,
            )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Prometheus health check failed: {str(e)}",
                duration_seconds=time.time() - start_time,
            )


class HealthChecker:
    """Manages and runs health checks."""

    def __init__(self):
        self.checks: dict[str, HealthCheck] = {}
        self.config = get_config()
        self._register_default_checks()

    def _register_default_checks(self) -> None:
        """Register default health checks."""
        if self.config.health_check_enabled:
            self.register_check(BigQueryHealthCheck())
            self.register_check(SentryHealthCheck())
            self.register_check(PrometheusHealthCheck())

    def register_check(self, check: HealthCheck) -> None:
        """Register a health check."""
        self.checks[check.name] = check
        logger.debug(f"Registered health check: {check.name}")

    def run_check(self, name: str) -> HealthCheckResult:
        """Run a specific health check."""
        if name not in self.checks:
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check '{name}' not found",
            )

        check = self.checks[name]
        logger.debug(f"Running health check: {name}")

        try:
            result = check.check()

            # Record metrics
            collector = get_metrics_collector()
            collector.record_gauge(
                "health_check.status",
                1 if result.status == HealthStatus.HEALTHY else 0,
                tags={"check": name},
            )
            collector.record_histogram(
                "health_check.duration.seconds",
                result.duration_seconds,
                tags={"check": name},
            )

            return result
        except Exception as e:
            logger.error(f"Health check {name} failed with exception", error=str(e))
            return HealthCheckResult(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed with exception: {str(e)}",
            )

    def run_all_checks(self) -> dict[str, HealthCheckResult]:
        """Run all registered health checks."""
        results = {}
        for name in self.checks:
            results[name] = self.run_check(name)
        return results

    def get_overall_status(self) -> HealthStatus:
        """Get the overall health status across all checks."""
        results = self.run_all_checks()

        if not results:
            return HealthStatus.UNKNOWN

        # If any check is unhealthy, overall is unhealthy
        if any(r.status == HealthStatus.UNHEALTHY for r in results.values()):
            return HealthStatus.UNHEALTHY

        # If any check is degraded, overall is degraded
        if any(r.status == HealthStatus.DEGRADED for r in results.values()):
            return HealthStatus.DEGRADED

        # If all checks are healthy
        if all(r.status == HealthStatus.HEALTHY for r in results.values()):
            return HealthStatus.HEALTHY

        return HealthStatus.UNKNOWN


# Global health checker
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get or create the global health checker."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker


def register_health_check(check: HealthCheck) -> None:
    """Register a custom health check."""
    get_health_checker().register_check(check)


def run_health_checks() -> dict[str, Any]:
    """
    Run all health checks and return results.

    Returns:
        Dictionary with overall status and individual check results
    """
    checker = get_health_checker()
    results = checker.run_all_checks()
    overall_status = checker.get_overall_status()

    return {
        "status": overall_status.value,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {name: result.to_dict() for name, result in results.items()},
    }
