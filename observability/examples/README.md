# Observability Integration Examples

This directory contains examples of how to integrate the DecentClaude observability framework with existing CLI utilities and scripts.

## Quick Start

### 1. Basic Integration

Add observability to any CLI script:

```python
#!/usr/bin/env python3
"""My CLI utility with observability."""

import sys
from observability import (
    init_observability,
    get_logger,
    track_cli_command,
    with_error_tracking,
)

# Initialize observability (do this once at startup)
init_observability()

logger = get_logger(__name__)

@with_error_tracking(context={"module": "my_cli"})
def main():
    """Main function with error tracking."""
    with track_cli_command("my-cli", args={"arg1": "value1"}):
        logger.info("Starting my CLI utility")
        # Your code here
        logger.info("Completed successfully")

if __name__ == "__main__":
    main()
```

### 2. BigQuery Operations with Cost Tracking

```python
from observability import (
    get_logger,
    track_cost,
    track_query_performance,
    track_performance,
)

logger = get_logger(__name__)

def estimate_query_cost(query: str):
    """Estimate query cost with observability."""

    with track_performance("estimate_query_cost"):
        from google.cloud import bigquery

        client = bigquery.Client()

        # Dry run to get cost estimate
        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        query_job = client.query(query, job_config=job_config)

        bytes_processed = query_job.total_bytes_processed
        cost_per_tb = 5.0  # $5 per TB
        estimated_cost = (bytes_processed / (1024**4)) * cost_per_tb

        # Track the cost
        track_cost(
            operation="query_cost_estimate",
            bytes_processed=bytes_processed,
            estimated_cost_usd=estimated_cost,
            tags={"query_type": "estimate"},
        )

        logger.info(
            "Query cost estimated",
            bytes_processed=bytes_processed,
            estimated_cost_usd=estimated_cost,
        )

        return estimated_cost
```

### 3. Data Quality Checks with Observability

```python
from observability import get_logger, get_analytics
import time

logger = get_logger(__name__)
analytics = get_analytics()

class DataQualityCheck:
    """Base class with observability."""

    def run(self):
        """Run the check with tracking."""
        start_time = time.time()

        try:
            result = self.execute()
            duration = time.time() - start_time

            analytics.track_data_quality_check(
                check_name=self.__class__.__name__,
                passed=result.passed,
                duration_seconds=duration,
                details={"message": result.message},
            )

            return result
        except Exception as e:
            duration = time.time() - start_time
            analytics.track_data_quality_check(
                check_name=self.__class__.__name__,
                passed=False,
                duration_seconds=duration,
                details={"error": str(e)},
            )
            raise

    def execute(self):
        """Override this method with your check logic."""
        raise NotImplementedError
```

### 4. Health Checks

```python
from observability import run_health_checks, get_logger
import json

logger = get_logger(__name__)

def check_system_health():
    """Check overall system health."""
    results = run_health_checks()

    logger.info(
        "Health check completed",
        overall_status=results["status"],
        checks_count=len(results["checks"]),
    )

    print(json.dumps(results, indent=2))

    # Exit with error if unhealthy
    if results["status"] != "healthy":
        sys.exit(1)
```

## Configuration

Configure observability using environment variables:

```bash
# Logging
export LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL
export LOG_FORMAT=json             # json or text
export LOG_FILE=/var/log/app.log   # Optional file logging

# Metrics
export METRICS_ENABLED=true
export PROMETHEUS_PORT=8000

# Datadog
export DATADOG_ENABLED=true
export DATADOG_API_KEY=your_api_key
export DATADOG_SITE=datadoghq.com
export DATADOG_SERVICE=decentclaude
export DATADOG_ENV=production

# Sentry Error Tracking
export SENTRY_ENABLED=true
export SENTRY_DSN=https://your_sentry_dsn
export SENTRY_ENVIRONMENT=production
export SENTRY_TRACES_SAMPLE_RATE=0.1

# Cost Monitoring
export COST_ALERT_THRESHOLD_USD=100.0
export COST_TRACKING_ENABLED=true

# General
export SERVICE_NAME=decentclaude
export ENVIRONMENT=production
```

## Example CLI Wrappers

See the example files in this directory:
- `bq_query_cost_with_observability.py` - BigQuery cost estimation with full observability
- `data_quality_with_observability.py` - Data quality checks with tracking

## Viewing Metrics

### Prometheus Metrics

Access metrics at: `http://localhost:8000/metrics`

Example metrics:
- `operation_duration_seconds` - Operation execution time
- `bigquery_bytes_processed` - Bytes processed by queries
- `bigquery_cost_usd` - Estimated query costs
- `cli_command_success` - Successful command executions
- `data_quality_check_passed` - Passed quality checks

### Datadog Dashboard

View metrics in Datadog:
1. Go to Metrics Explorer
2. Search for `decentclaude.*`
3. Create dashboards and monitors

### Sentry Error Tracking

View errors in Sentry:
1. Go to Issues
2. Filter by `decentclaude` project
3. Set up alerts for critical errors

## Best Practices

1. **Always initialize observability at startup**:
   ```python
   from observability import init_observability
   init_observability()
   ```

2. **Use context managers for operations**:
   ```python
   with track_performance("my_operation"):
       # your code
   ```

3. **Log with structured fields**:
   ```python
   logger.info("Query executed", rows=100, duration_seconds=1.5)
   ```

4. **Track costs for BigQuery operations**:
   ```python
   track_cost("query", bytes_processed, estimated_cost_usd)
   ```

5. **Use correlation IDs for distributed tracing**:
   ```python
   from observability import LogContext

   with LogContext(correlation_id="req-123", operation="my_op"):
       # All logs will include correlation_id
   ```

6. **Capture exceptions automatically**:
   ```python
   @with_error_tracking(context={"module": "my_module"})
   def my_function():
       # Exceptions automatically tracked
   ```
