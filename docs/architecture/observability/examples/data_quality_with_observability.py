#!/usr/bin/env python3
"""
Data Quality Framework with Observability

Example of integrating the observability framework with data quality checks.
Demonstrates how to track check execution, failures, and performance.
"""

import sys
import time
from pathlib import Path
from typing import List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from observability import (
    LogContext,
    get_analytics,
    get_logger,
    init_observability,
    track_performance,
    with_error_tracking,
)

# Initialize observability
init_observability()

logger = get_logger(__name__)
analytics = get_analytics()


class CheckResult:
    """Result of a data quality check."""

    def __init__(self, passed: bool, message: str):
        self.passed = passed
        self.message = message

    def __repr__(self):
        status = "PASSED" if self.passed else "FAILED"
        return f"CheckResult({status}: {self.message})"


class DataQualityCheck:
    """
    Base class for data quality checks with observability.

    All checks automatically track:
    - Execution time
    - Pass/fail status
    - Error details
    """

    def __init__(self, name: str = None):
        self.name = name or self.__class__.__name__
        self.logger = get_logger(f"data_quality.{self.name}")

    @with_error_tracking(context={"module": "data_quality"})
    def run(self) -> CheckResult:
        """
        Run the check with full observability tracking.

        Returns:
            CheckResult with pass/fail status
        """
        start_time = time.time()

        with LogContext(operation=f"data_quality_check.{self.name}"):
            self.logger.info(f"Starting data quality check: {self.name}")

            try:
                # Execute the check
                with track_performance(f"data_quality.{self.name}"):
                    result = self.execute()

                duration = time.time() - start_time

                # Track the check execution
                analytics.track_data_quality_check(
                    check_name=self.name,
                    passed=result.passed,
                    duration_seconds=duration,
                    details={"message": result.message},
                )

                # Log the result
                if result.passed:
                    self.logger.info(
                        f"Check passed: {self.name}",
                        message=result.message,
                        duration_seconds=round(duration, 3),
                    )
                else:
                    self.logger.warning(
                        f"Check failed: {self.name}",
                        message=result.message,
                        duration_seconds=round(duration, 3),
                    )

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Track the failed check
                analytics.track_data_quality_check(
                    check_name=self.name,
                    passed=False,
                    duration_seconds=duration,
                    details={"error": str(e), "error_type": type(e).__name__},
                )

                self.logger.error(
                    f"Check raised exception: {self.name}",
                    error=str(e),
                    error_type=type(e).__name__,
                    duration_seconds=round(duration, 3),
                )

                raise

    def execute(self) -> CheckResult:
        """
        Execute the actual check logic.
        Override this in subclasses.

        Returns:
            CheckResult with pass/fail status
        """
        raise NotImplementedError(f"Check {self.name} must implement execute()")


class SQLFileExistsCheck(DataQualityCheck):
    """Check that SQL files exist in a directory."""

    def __init__(self, directory: str):
        super().__init__("SQLFileExists")
        self.directory = Path(directory)

    def execute(self) -> CheckResult:
        """Check if directory exists and contains SQL files."""
        if not self.directory.exists():
            return CheckResult(
                passed=False,
                message=f"Directory does not exist: {self.directory}",
            )

        sql_files = list(self.directory.glob("*.sql"))

        if not sql_files:
            return CheckResult(
                passed=False,
                message=f"No SQL files found in {self.directory}",
            )

        return CheckResult(
            passed=True,
            message=f"Found {len(sql_files)} SQL files in {self.directory}",
        )


class NoHardcodedSecretsCheck(DataQualityCheck):
    """Check for hardcoded secrets in SQL files."""

    def __init__(self, directory: str):
        super().__init__("NoHardcodedSecrets")
        self.directory = Path(directory)
        self.secret_patterns = [
            "password",
            "api_key",
            "secret",
            "token",
            "credential",
        ]

    def execute(self) -> CheckResult:
        """Scan SQL files for secret patterns."""
        sql_files = list(self.directory.glob("**/*.sql"))

        findings = []
        for sql_file in sql_files:
            content = sql_file.read_text().lower()
            for pattern in self.secret_patterns:
                if pattern in content:
                    findings.append(f"{sql_file.name}: contains '{pattern}'")

        if findings:
            return CheckResult(
                passed=False,
                message=f"Found potential secrets in {len(findings)} locations:\n"
                + "\n".join(findings[:5]),
            )

        return CheckResult(
            passed=True,
            message=f"No hardcoded secrets found in {len(sql_files)} files",
        )


class TableRowCountCheck(DataQualityCheck):
    """Check that a BigQuery table has minimum row count."""

    def __init__(self, table_id: str, min_rows: int):
        super().__init__("TableRowCount")
        self.table_id = table_id
        self.min_rows = min_rows

    def execute(self) -> CheckResult:
        """Check row count in BigQuery table."""
        try:
            from google.cloud import bigquery

            client = bigquery.Client()

            # Get table
            table = client.get_table(self.table_id)
            row_count = table.num_rows

            # Track the BigQuery operation
            analytics.track_bigquery_operation(
                operation_type="table_row_count_check",
                table=self.table_id,
                rows_affected=row_count,
            )

            if row_count < self.min_rows:
                return CheckResult(
                    passed=False,
                    message=f"Table {self.table_id} has {row_count} rows, expected at least {self.min_rows}",
                )

            return CheckResult(
                passed=True,
                message=f"Table {self.table_id} has {row_count} rows (>= {self.min_rows})",
            )

        except Exception as e:
            return CheckResult(
                passed=False,
                message=f"Failed to check table {self.table_id}: {str(e)}",
            )


def run_checks(checks: List[DataQualityCheck]) -> dict:
    """
    Run a suite of data quality checks with observability.

    Args:
        checks: List of checks to run

    Returns:
        Summary of check results
    """
    logger.info(f"Starting data quality check suite", total_checks=len(checks))

    results = {"total": len(checks), "passed": 0, "failed": 0, "errors": 0}

    for check in checks:
        try:
            result = check.run()
            if result.passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            results["errors"] += 1
            logger.error(f"Check {check.name} raised exception", error=str(e))

    logger.info(
        "Data quality check suite completed",
        total=results["total"],
        passed=results["passed"],
        failed=results["failed"],
        errors=results["errors"],
    )

    return results


def main():
    """Example usage of data quality checks with observability."""
    print("Data Quality Framework with Observability")
    print("=" * 50)

    # Define checks
    checks = [
        SQLFileExistsCheck("examples"),
        NoHardcodedSecretsCheck("examples"),
        # TableRowCountCheck("project.dataset.table", min_rows=1000),  # Example
    ]

    # Run checks
    results = run_checks(checks)

    # Print summary
    print(f"\nResults:")
    print(f"  Total:  {results['total']}")
    print(f"  Passed: {results['passed']}")
    print(f"  Failed: {results['failed']}")
    print(f"  Errors: {results['errors']}")

    # Exit with error if any checks failed
    if results["failed"] > 0 or results["errors"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
