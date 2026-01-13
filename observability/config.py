"""
Observability configuration management.
"""

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ObservabilityConfig:
    """Configuration for observability framework."""

    # Logging configuration
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_format: str = field(default_factory=lambda: os.getenv("LOG_FORMAT", "json"))  # json or text
    log_file: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE"))

    # Metrics configuration
    metrics_enabled: bool = field(default_factory=lambda: os.getenv("METRICS_ENABLED", "true").lower() == "true")
    prometheus_port: int = field(default_factory=lambda: int(os.getenv("PROMETHEUS_PORT", "8000")))

    # Datadog configuration
    datadog_enabled: bool = field(default_factory=lambda: os.getenv("DATADOG_ENABLED", "false").lower() == "true")
    datadog_api_key: Optional[str] = field(default_factory=lambda: os.getenv("DATADOG_API_KEY"))
    datadog_site: str = field(default_factory=lambda: os.getenv("DATADOG_SITE", "datadoghq.com"))
    datadog_service: str = field(default_factory=lambda: os.getenv("DATADOG_SERVICE", "decentclaude"))
    datadog_env: str = field(default_factory=lambda: os.getenv("DATADOG_ENV", "dev"))

    # Error tracking (Sentry) configuration
    sentry_enabled: bool = field(default_factory=lambda: os.getenv("SENTRY_ENABLED", "false").lower() == "true")
    sentry_dsn: Optional[str] = field(default_factory=lambda: os.getenv("SENTRY_DSN"))
    sentry_environment: str = field(default_factory=lambda: os.getenv("SENTRY_ENVIRONMENT", "dev"))
    sentry_traces_sample_rate: float = field(default_factory=lambda: float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")))

    # Cost monitoring configuration
    cost_alert_threshold_usd: float = field(default_factory=lambda: float(os.getenv("COST_ALERT_THRESHOLD_USD", "100.0")))
    cost_tracking_enabled: bool = field(default_factory=lambda: os.getenv("COST_TRACKING_ENABLED", "true").lower() == "true")

    # Health check configuration
    health_check_enabled: bool = field(default_factory=lambda: os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true")
    health_check_interval_seconds: int = field(default_factory=lambda: int(os.getenv("HEALTH_CHECK_INTERVAL_SECONDS", "60")))

    # Tracing configuration
    tracing_enabled: bool = field(default_factory=lambda: os.getenv("TRACING_ENABLED", "false").lower() == "true")
    tracing_sample_rate: float = field(default_factory=lambda: float(os.getenv("TRACING_SAMPLE_RATE", "0.1")))

    # General settings
    service_name: str = field(default_factory=lambda: os.getenv("SERVICE_NAME", "decentclaude"))
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "dev"))

    def validate(self) -> list[str]:
        """Validate configuration and return list of issues."""
        issues = []

        if self.datadog_enabled and not self.datadog_api_key:
            issues.append("Datadog enabled but DATADOG_API_KEY not set")

        if self.sentry_enabled and not self.sentry_dsn:
            issues.append("Sentry enabled but SENTRY_DSN not set")

        if self.log_format not in ["json", "text"]:
            issues.append(f"Invalid LOG_FORMAT: {self.log_format} (must be 'json' or 'text')")

        if not 0 <= self.tracing_sample_rate <= 1.0:
            issues.append(f"Invalid TRACING_SAMPLE_RATE: {self.tracing_sample_rate} (must be 0.0-1.0)")

        if not 0 <= self.sentry_traces_sample_rate <= 1.0:
            issues.append(f"Invalid SENTRY_TRACES_SAMPLE_RATE: {self.sentry_traces_sample_rate} (must be 0.0-1.0)")

        return issues


# Global configuration instance
_config: Optional[ObservabilityConfig] = None


def get_config() -> ObservabilityConfig:
    """Get or create the global observability configuration."""
    global _config
    if _config is None:
        _config = ObservabilityConfig()
    return _config


def set_config(config: ObservabilityConfig) -> None:
    """Set the global observability configuration."""
    global _config
    _config = config
