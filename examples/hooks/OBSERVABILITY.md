# Hook Observability Integration

This directory contains hook scripts integrated with the observability framework for comprehensive monitoring, logging, and error tracking.

## Overview

The hook scripts are enhanced with observability capabilities:

- **Structured Logging**: JSON/text formatted logs with correlation IDs and context
- **Metrics Collection**: Prometheus and Datadog metrics for hook execution
- **Error Tracking**: Sentry integration for error capture and alerting
- **Analytics**: CLI command usage tracking and performance monitoring

## Architecture

### Components

1. **Hook Scripts** (Bash)
   - `PreToolUse__sql-validation.sh`: SQL query validation before execution
   - `PostToolUse__auto-formatting.sh`: Auto-format code files after writes
   - `PostToolUse__cost-tracking.sh`: Track BigQuery query costs

2. **Observability Library** (Python)
   - `lib/hook_observability.py`: Bridge between bash and observability framework
   - Provides functions for logging, metrics, and error tracking

3. **Observability Framework** (Python)
   - `../../observability/logger.py`: Structured logging
   - `../../observability/metrics.py`: Prometheus/Datadog metrics
   - `../../observability/analytics.py`: Usage analytics
   - `../../observability/errors.py`: Error tracking with Sentry

### Integration Pattern

Each hook follows this pattern:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Hook identification
HOOK_NAME="PreToolUse__example"
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Initialize observability
START_TIME=$(date +%s.%N)

# Helper function to call Python observability
call_observability() {
    local action="$1"
    shift
    python3 "$HOOK_DIR/lib/hook_observability.py" "$action" "$HOOK_NAME" "$@" 2>/dev/null || true
}

# Log hook start
call_observability "start"

# ... hook logic ...

# Track specific metrics
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_counter('hook.example.metric', tags={'hook': '$HOOK_NAME'})
" 2>/dev/null || true

# Calculate duration and log completion
END_TIME=$(date +%s.%N)
DURATION=$(echo "$END_TIME - $START_TIME" | bc)
call_observability "end" "true"
```

## Metrics Tracked

### SQL Validation Hook

- `hook.invocation`: Hook invocation count
- `hook.sql_validation.queries_processed`: SQL queries validated
- `hook.sql_validation.validation_passed`: Successful validations
- `hook.sql_validation.validation_failed`: Failed validations
- `hook.sql_validation.warnings`: Validation warnings count
- `hook.sql_validation.extraction_error`: SQL extraction failures
- `hook.sql_validation.duration.seconds`: Validation duration

### Auto-Formatting Hook

- `hook.invocation`: Hook invocation count
- `hook.auto_format.files_formatted`: Files successfully formatted
- `hook.auto_format.files_unchanged`: Files with no changes needed
- `hook.auto_format.format_failed`: Formatting failures
- `hook.auto_format.unsupported_type`: Unsupported file types
- `hook.auto_format.formatter_missing`: Missing formatter tools
- `hook.auto_format.duration.seconds`: Formatting duration

### Cost Tracking Hook

- `hook.invocation`: Hook invocation count
- `hook.cost_tracking.budget_exceeded`: Budget exceeded alerts
- `hook.cost_tracking.budget_warning`: Budget warnings
- `hook.cost_tracking.expensive_query`: Expensive query alerts
- `hook.cost_tracking.session_total_usd`: Current session total cost (gauge)
- `hook.cost_tracking.daily_total_usd`: Current daily total cost (gauge)
- `hook.cost_tracking.session_budget_percent`: Session budget usage (gauge)
- `hook.cost_tracking.daily_budget_percent`: Daily budget usage (gauge)
- `hook.cost_tracking.duration.seconds`: Hook execution duration
- `bigquery.bytes_processed`: Bytes scanned per query (histogram)
- `bigquery.cost.usd`: Query cost in USD (histogram)
- `bigquery.total_cost.usd`: Cumulative cost counter
- `bigquery.query.duration.seconds`: Query execution time
- `bigquery.query.rows_returned`: Rows returned per query
- `bigquery.cost_alert`: High-cost query alerts

## Configuration

### Environment Variables

#### Logging
- `LOG_LEVEL`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) - default: INFO
- `LOG_FORMAT`: Log format (json, text) - default: json
- `LOG_FILE`: Optional log file path

#### Metrics
- `METRICS_ENABLED`: Enable metrics collection - default: true
- `PROMETHEUS_PORT`: Prometheus metrics server port - default: 8000

#### Datadog
- `DATADOG_ENABLED`: Enable Datadog metrics - default: false
- `DATADOG_API_KEY`: Datadog API key
- `DATADOG_SITE`: Datadog site - default: datadoghq.com
- `DATADOG_SERVICE`: Service name for Datadog - default: decentclaude
- `DATADOG_ENV`: Environment name - default: dev

#### Sentry
- `SENTRY_ENABLED`: Enable Sentry error tracking - default: false
- `SENTRY_DSN`: Sentry DSN
- `SENTRY_ENVIRONMENT`: Environment name - default: dev
- `SENTRY_TRACES_SAMPLE_RATE`: Sample rate for traces - default: 0.1

#### Cost Tracking
- `COST_ALERT_THRESHOLD_USD`: Alert threshold in USD - default: 100.0
- `COST_TRACKING_ENABLED`: Enable cost tracking - default: true

## Usage

### Testing Observability

Test the observability integration:

```bash
# Test the observability module
python3 lib/hook_observability.py test test_hook

# Test individual hooks
echo '{"tool": "mcp__bigquery__run_query", "arguments": {"sql": "SELECT 1"}}' | ./PreToolUse__sql-validation.sh
```

### Viewing Metrics

If Prometheus is enabled, metrics are available at:
```
http://localhost:8000/metrics
```

### Viewing Logs

Logs are output to stdout/stderr in the configured format. To view structured logs:

```bash
# Set JSON format
export LOG_FORMAT=json
export LOG_LEVEL=DEBUG

# Run a hook
echo '{"tool": "Write", "arguments": {"file_path": "test.py"}}' | ./PostToolUse__auto-formatting.sh
```

### Accessing Sentry

If Sentry is enabled, errors are automatically captured and sent to your Sentry project. View them in the Sentry dashboard.

## Error Handling

The observability integration is designed to be non-intrusive:

- If observability fails to initialize, hooks continue to work
- Python errors are caught and logged but don't block hook execution
- All observability calls use `|| true` to prevent failures from breaking hooks

## Metrics Dashboard

Example Prometheus queries for monitoring:

```promql
# Hook invocation rate
rate(hook_invocation[5m])

# Hook success rate
rate(hook_success[5m]) / rate(hook_invocation[5m])

# Average hook duration
rate(hook_duration_seconds_sum[5m]) / rate(hook_duration_seconds_count[5m])

# BigQuery cost per hour
rate(bigquery_total_cost_usd[1h])

# Budget usage
hook_cost_tracking_session_budget_percent
hook_cost_tracking_daily_budget_percent
```

## Development

### Adding Observability to New Hooks

1. Add the hook identification section:
```bash
HOOK_NAME="YourHook__name"
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
```

2. Add the observability helper:
```bash
call_observability() {
    local action="$1"
    shift
    python3 "$HOOK_DIR/lib/hook_observability.py" "$action" "$HOOK_NAME" "$@" 2>/dev/null || true
}
```

3. Track start and end:
```bash
START_TIME=$(date +%s.%N)
call_observability "start"
# ... hook logic ...
call_observability "end" "true"
```

4. Add custom metrics:
```bash
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_counter('hook.your_metric', tags={'hook': '$HOOK_NAME'})
" 2>/dev/null || true
```

## Troubleshooting

### Observability Not Working

1. Check Python path is correct:
```bash
python3 -c "import sys; sys.path.insert(0, '../../'); from observability import logger; print('OK')"
```

2. Check environment variables:
```bash
env | grep -E '(LOG_|METRICS_|DATADOG_|SENTRY_)'
```

3. Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
export LOG_FORMAT=text
```

### High Memory Usage

If metrics collection causes high memory usage:

1. Disable Prometheus:
```bash
export METRICS_ENABLED=false
```

2. Or use Datadog StatsD instead (lighter weight)

### Missing Dependencies

Install required Python packages:

```bash
pip install prometheus-client datadog sentry-sdk
```

## Best Practices

1. **Always use `|| true`** on observability calls to prevent failures
2. **Keep metrics cardinality low** - avoid high-cardinality tags
3. **Use structured logging** for searchability
4. **Track both success and failure** paths
5. **Include context** in error messages
6. **Use correlation IDs** for distributed tracing
7. **Monitor resource usage** of observability components

## Security Considerations

1. **Redact sensitive data** from logs and metrics
2. **Don't log credentials** or secrets
3. **Sanitize SQL queries** before logging
4. **Use environment variables** for API keys
5. **Limit log retention** for compliance
6. **Encrypt logs in transit** when sending to remote services

## Performance Impact

Observability overhead per hook execution:

- Logging: ~1-5ms
- Metrics: ~1-3ms
- Error tracking: ~5-10ms (only on errors)

Total overhead: ~5-10ms per hook execution (negligible for most use cases)
