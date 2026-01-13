# DecentClaude Observability Framework

Comprehensive monitoring and observability framework for data engineering workflows. Provides structured logging, metrics collection, distributed tracing, error tracking, cost monitoring, and health checks.

## Features

- **Structured Logging**: JSON and text formats with context propagation
- **Metrics Collection**: Prometheus and Datadog integration
- **Query Performance Tracking**: Monitor BigQuery query execution and costs
- **Cost Monitoring**: Track and alert on BigQuery costs
- **Error Tracking**: Sentry integration for exception tracking
- **Usage Analytics**: Track CLI command usage patterns
- **Health Checks**: Monitor system component health
- **Distributed Tracing**: Correlation IDs for request tracing

## Quick Start

### Installation

```bash
# Install core dependencies (already in main project)
pip install google-cloud-bigquery

# Install optional observability dependencies
pip install -r observability/requirements.txt
```

### Basic Usage

```python
from observability import init_observability, get_logger, track_cli_command

# Initialize (do this once at startup)
init_observability()

# Get a logger
logger = get_logger(__name__)

# Track a CLI command
with track_cli_command("my-command"):
    logger.info("Doing work")
    # Your code here
```

## Configuration

Configure using environment variables:

```bash
# Logging
export LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR, CRITICAL
export LOG_FORMAT=json             # json or text
export LOG_FILE=/var/log/app.log   # Optional

# Metrics (Prometheus)
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

# Cost Monitoring
export COST_ALERT_THRESHOLD_USD=100.0

# General
export ENVIRONMENT=production
export SERVICE_NAME=decentclaude
```

## Core Components

### 1. Structured Logging (`logger.py`)

Provides structured logging with context propagation and multiple output formats.

```python
from observability import get_logger, LogContext

logger = get_logger(__name__)

# Simple logging
logger.info("Query executed", rows=100, duration_seconds=1.5)

# With context
with LogContext(operation="data_pipeline", correlation_id="req-123"):
    logger.info("Processing data")  # Includes correlation_id automatically
```

**Features**:
- JSON and text output formats
- Context variables (correlation ID, user, operation)
- Colored console output for text format
- File and console handlers
- Automatic inclusion of module, function, and line number

### 2. Metrics Collection (`metrics.py`)

Track performance metrics with Prometheus and Datadog backends.

```python
from observability import (
    track_performance,
    track_cost,
    track_query_performance,
    performance_monitor,
)

# Track operation performance
with track_performance("my_operation"):
    # Your code here
    pass

# Track BigQuery cost
track_cost(
    operation="query_execution",
    bytes_processed=1024**3,  # 1 GB
    estimated_cost_usd=0.005,
    tags={"dataset": "analytics"},
)

# Track query performance
track_query_performance(
    query_type="select",
    duration_seconds=2.5,
    rows_returned=1000,
    bytes_processed=1024**3,
)

# Decorator for automatic tracking
@performance_monitor(operation="process_data")
def process_data():
    pass
```

**Metrics tracked**:
- `operation.duration.seconds` - Operation execution time
- `operation.success` / `operation.failure` - Success/failure counts
- `bigquery.bytes_processed` - Bytes processed by queries
- `bigquery.cost.usd` - Query costs
- `bigquery.query.duration.seconds` - Query execution time
- `cli.command.duration.seconds` - CLI command execution time
- `data_quality.check.passed` / `failed` - Data quality check results

### 3. Error Tracking (`errors.py`)

Capture and track errors with Sentry integration.

```python
from observability import (
    capture_exception,
    capture_message,
    with_error_tracking,
)

# Manual exception capture
try:
    raise ValueError("Something went wrong")
except Exception as e:
    capture_exception(e, context={"user_id": "123", "operation": "import"})

# Automatic exception tracking
@with_error_tracking(context={"module": "data_pipeline"})
def my_function():
    # Exceptions automatically captured and re-raised
    raise ValueError("Error")

# Capture informational messages
capture_message("High memory usage detected", level="warning")
```

**Features**:
- Automatic exception capture and reporting
- Context attachment (tags, user info, custom data)
- Breadcrumb trail for debugging
- Stack trace capture
- Integration with logging

### 4. Health Checks (`health.py`)

Monitor system component health.

```python
from observability import run_health_checks, register_health_check, HealthCheck

# Run all health checks
results = run_health_checks()
print(f"Overall status: {results['status']}")

# Create custom health check
class CustomHealthCheck(HealthCheck):
    def __init__(self):
        super().__init__("custom_service")

    def check(self):
        # Your health check logic
        return HealthCheckResult(
            name=self.name,
            status=HealthStatus.HEALTHY,
            message="Service is healthy",
        )

# Register custom check
register_health_check(CustomHealthCheck())
```

**Built-in health checks**:
- BigQuery connectivity
- Sentry error tracking
- Prometheus metrics server

### 5. Usage Analytics (`analytics.py`)

Track CLI command usage and patterns.

```python
from observability import get_analytics, track_cli_command

analytics = get_analytics()

# Track command execution
with track_cli_command("bq-query-cost", args={"format": "json"}):
    # Command code
    pass

# Track BigQuery operations
analytics.track_bigquery_operation(
    operation_type="query",
    dataset="my_dataset",
    table="my_table",
    bytes_processed=1024**3,
    rows_affected=1000,
)

# Track data quality checks
analytics.track_data_quality_check(
    check_name="NoHardcodedSecrets",
    passed=True,
    duration_seconds=0.5,
)
```

## Integration Examples

### CLI Utility Integration

```python
#!/usr/bin/env python3
import sys
from observability import (
    init_observability,
    get_logger,
    track_cli_command,
    with_error_tracking,
)

init_observability()
logger = get_logger(__name__)

@with_error_tracking()
def main():
    with track_cli_command("my-cli"):
        logger.info("Starting CLI")
        # Your CLI code
        logger.info("Completed")

if __name__ == "__main__":
    main()
```

### BigQuery Cost Tracking

```python
from observability import track_cost, track_query_performance
from google.cloud import bigquery

client = bigquery.Client()

# Dry run for cost estimate
job_config = bigquery.QueryJobConfig(dry_run=True)
query_job = client.query(query, job_config=job_config)

bytes_processed = query_job.total_bytes_processed
estimated_cost = (bytes_processed / (1024**4)) * 5.0  # $5 per TB

track_cost(
    operation="query_estimate",
    bytes_processed=bytes_processed,
    estimated_cost_usd=estimated_cost,
)
```

### Data Quality Checks

```python
from observability import get_analytics
import time

analytics = get_analytics()

class DataQualityCheck:
    def run(self):
        start_time = time.time()
        try:
            result = self.execute()
            analytics.track_data_quality_check(
                check_name=self.__class__.__name__,
                passed=result.passed,
                duration_seconds=time.time() - start_time,
            )
            return result
        except Exception as e:
            analytics.track_data_quality_check(
                check_name=self.__class__.__name__,
                passed=False,
                duration_seconds=time.time() - start_time,
            )
            raise
```

## Viewing Metrics

### Prometheus

Access metrics at `http://localhost:8000/metrics` (configurable via `PROMETHEUS_PORT`).

Example queries:
```promql
# Average operation duration
rate(operation_duration_seconds_sum[5m]) / rate(operation_duration_seconds_count[5m])

# Total BigQuery cost
sum(bigquery_total_cost_usd)

# Command success rate
rate(cli_command_success[5m]) / (rate(cli_command_success[5m]) + rate(cli_command_failure[5m]))
```

### Datadog

Metrics are automatically sent to Datadog when `DATADOG_ENABLED=true`:

1. Go to Metrics Explorer
2. Search for metrics prefixed with `decentclaude.*`
3. Create dashboards and monitors

Example metrics:
- `decentclaude.operation.duration.seconds`
- `decentclaude.bigquery.cost.usd`
- `decentclaude.cli.command.success`

### Sentry

View errors and performance in Sentry dashboard:

1. Go to Issues for error tracking
2. Go to Performance for transaction traces
3. Set up alerts for error thresholds

## Architecture

```
observability/
├── __init__.py           # Main module exports
├── config.py             # Configuration management
├── logger.py             # Structured logging
├── metrics.py            # Metrics collection
├── errors.py             # Error tracking
├── health.py             # Health checks
├── analytics.py          # Usage analytics
├── requirements.txt      # Dependencies
├── examples/             # Integration examples
│   ├── README.md
│   ├── bq_query_cost_with_observability.py
│   └── data_quality_with_observability.py
└── README.md            # This file
```

## Best Practices

1. **Initialize early**: Call `init_observability()` at the start of your application
2. **Use context managers**: Prefer `with track_performance()` over manual timing
3. **Structure your logs**: Always include relevant fields: `logger.info("message", field=value)`
4. **Set correlation IDs**: Use `LogContext(correlation_id=...)` for distributed tracing
5. **Track costs**: Always call `track_cost()` for BigQuery operations
6. **Sanitize sensitive data**: Never log passwords, API keys, or secrets
7. **Use decorators**: Apply `@with_error_tracking()` to functions that should capture errors
8. **Monitor health**: Regularly call `run_health_checks()` in monitoring systems

## Performance Considerations

- Logging is asynchronous when using file handlers
- Metrics have minimal overhead (<1ms per call)
- Sentry sampling rates reduce noise (configurable via `SENTRY_TRACES_SAMPLE_RATE`)
- Health checks run on-demand, not continuously
- Prometheus metrics are scraped, not pushed

## Troubleshooting

### Metrics not appearing in Prometheus

1. Verify Prometheus server is running: `curl http://localhost:8000/metrics`
2. Check `METRICS_ENABLED=true` is set
3. Ensure `prometheus_client` is installed

### Errors not appearing in Sentry

1. Verify `SENTRY_ENABLED=true` and `SENTRY_DSN` is set
2. Check `sentry-sdk` is installed
3. Look for initialization errors in logs

### Logs not structured

1. Set `LOG_FORMAT=json` for JSON output
2. Verify `init_logging()` was called
3. Use `logger.info("msg", field=value)` syntax, not f-strings

## Examples

See the `examples/` directory for complete integration examples:

- `bq_query_cost_with_observability.py` - BigQuery cost estimation with full observability
- `data_quality_with_observability.py` - Data quality checks with tracking
- `README.md` - Detailed integration guide

## License

Part of the DecentClaude project.
