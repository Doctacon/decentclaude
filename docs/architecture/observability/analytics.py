"""
Usage analytics for tracking CLI command usage and patterns.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .logger import get_logger, set_operation_context
from .metrics import get_metrics_collector

logger = get_logger(__name__)


@dataclass
class CommandExecution:
    """Represents a CLI command execution."""

    command: str
    args: dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    success: bool = False
    error: Optional[str] = None
    user: Optional[str] = None

    def duration_seconds(self) -> float:
        """Get execution duration in seconds."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "command": self.command,
            "args": self.args,
            "duration_seconds": round(self.duration_seconds(), 3),
            "success": self.success,
            "error": self.error,
            "user": self.user,
            "timestamp": datetime.fromtimestamp(self.start_time).isoformat(),
        }


class UsageAnalytics:
    """Track and analyze CLI usage patterns."""

    def __init__(self):
        self.collector = get_metrics_collector()
        self.current_execution: Optional[CommandExecution] = None

    def start_command(
        self,
        command: str,
        args: Optional[dict[str, Any]] = None,
        user: Optional[str] = None,
    ) -> CommandExecution:
        """
        Start tracking a command execution.

        Args:
            command: Name of the command being executed
            args: Command arguments (sanitized, no secrets)
            user: User executing the command

        Returns:
            CommandExecution object for tracking
        """
        execution = CommandExecution(
            command=command,
            args=args or {},
            user=user,
        )

        self.current_execution = execution

        # Set operation context for logging
        set_operation_context(command)

        # Record command start
        self.collector.record_counter(
            "cli.command.started",
            tags={"command": command},
        )

        logger.info(
            f"Command started: {command}",
            command=command,
            args_count=len(args) if args else 0,
            user=user,
        )

        return execution

    def end_command(
        self,
        execution: CommandExecution,
        success: bool = True,
        error: Optional[str] = None,
    ) -> None:
        """
        End tracking a command execution.

        Args:
            execution: The CommandExecution to finalize
            success: Whether the command succeeded
            error: Error message if failed
        """
        execution.end_time = time.time()
        execution.success = success
        execution.error = error

        duration = execution.duration_seconds()

        # Record metrics
        self.collector.record_histogram(
            "cli.command.duration.seconds",
            duration,
            tags={"command": execution.command, "success": str(success).lower()},
        )

        if success:
            self.collector.record_counter(
                "cli.command.success",
                tags={"command": execution.command},
            )
        else:
            self.collector.record_counter(
                "cli.command.failure",
                tags={"command": execution.command},
            )

        # Log completion
        logger.info(
            f"Command completed: {execution.command}",
            command=execution.command,
            duration_seconds=round(duration, 3),
            success=success,
            error=error,
        )

        # Clear current execution
        if self.current_execution == execution:
            self.current_execution = None

    def track_command_argument(
        self,
        command: str,
        argument: str,
        value: Any,
    ) -> None:
        """
        Track usage of specific command arguments.

        Args:
            command: Command name
            argument: Argument name
            value: Argument value (will be converted to string)
        """
        # Don't log sensitive values
        if any(
            keyword in argument.lower()
            for keyword in ["password", "secret", "key", "token", "credential"]
        ):
            value = "[REDACTED]"

        self.collector.record_counter(
            "cli.command.argument",
            tags={
                "command": command,
                "argument": argument,
            },
        )

        logger.debug(
            f"Argument used: {argument}",
            command=command,
            argument=argument,
            value=str(value),
        )

    def track_feature_usage(
        self,
        feature: str,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Track usage of a specific feature.

        Args:
            feature: Feature name
            context: Additional context about the feature usage
        """
        context = context or {}

        self.collector.record_counter(
            "cli.feature.usage",
            tags={"feature": feature},
        )

        logger.debug(
            f"Feature used: {feature}",
            feature=feature,
            **context,
        )

    def track_bigquery_operation(
        self,
        operation_type: str,
        dataset: Optional[str] = None,
        table: Optional[str] = None,
        bytes_processed: Optional[int] = None,
        rows_affected: Optional[int] = None,
    ) -> None:
        """
        Track BigQuery-specific operations.

        Args:
            operation_type: Type of operation (query, scan, export, etc.)
            dataset: Dataset name
            table: Table name
            bytes_processed: Number of bytes processed
            rows_affected: Number of rows affected
        """
        tags = {"operation_type": operation_type}
        if dataset:
            tags["dataset"] = dataset

        self.collector.record_counter(
            "bigquery.operation",
            tags=tags,
        )

        log_data = {
            "operation_type": operation_type,
            "dataset": dataset,
            "table": table,
        }

        if bytes_processed is not None:
            self.collector.record_histogram(
                "bigquery.operation.bytes_processed",
                bytes_processed,
                tags=tags,
            )
            log_data["bytes_processed"] = bytes_processed

        if rows_affected is not None:
            self.collector.record_histogram(
                "bigquery.operation.rows_affected",
                rows_affected,
                tags=tags,
            )
            log_data["rows_affected"] = rows_affected

        logger.info(
            f"BigQuery operation: {operation_type}",
            **log_data,
        )

    def track_data_quality_check(
        self,
        check_name: str,
        passed: bool,
        duration_seconds: float,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Track data quality check execution.

        Args:
            check_name: Name of the check
            passed: Whether the check passed
            duration_seconds: Check execution time
            details: Additional check details
        """
        details = details or {}

        self.collector.record_counter(
            "data_quality.check.executed",
            tags={"check": check_name, "passed": str(passed).lower()},
        )

        self.collector.record_histogram(
            "data_quality.check.duration.seconds",
            duration_seconds,
            tags={"check": check_name},
        )

        if passed:
            self.collector.record_counter(
                "data_quality.check.passed",
                tags={"check": check_name},
            )
        else:
            self.collector.record_counter(
                "data_quality.check.failed",
                tags={"check": check_name},
            )

        logger.info(
            f"Data quality check: {check_name}",
            check=check_name,
            passed=passed,
            duration_seconds=round(duration_seconds, 3),
            **details,
        )


# Global analytics instance
_analytics: Optional[UsageAnalytics] = None


def get_analytics() -> UsageAnalytics:
    """Get or create the global usage analytics instance."""
    global _analytics
    if _analytics is None:
        _analytics = UsageAnalytics()
    return _analytics


def track_cli_command(command: str, args: Optional[dict[str, Any]] = None):
    """
    Context manager for tracking CLI command execution.

    Usage:
        with track_cli_command("bq-query-cost", args={"query": "SELECT 1"}):
            # execute command
            pass
    """

    class CommandTracker:
        def __init__(self, command: str, args: Optional[dict[str, Any]]):
            self.analytics = get_analytics()
            self.command = command
            self.args = args
            self.execution = None

        def __enter__(self):
            self.execution = self.analytics.start_command(self.command, self.args)
            return self.execution

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                self.analytics.end_command(self.execution, success=True)
            else:
                self.analytics.end_command(
                    self.execution,
                    success=False,
                    error=f"{exc_type.__name__}: {str(exc_val)}",
                )
            return False

    return CommandTracker(command, args)
