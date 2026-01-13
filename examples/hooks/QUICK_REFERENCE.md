# Hook Observability Quick Reference

## Quick Start

```bash
# Test the integration
./test-observability.sh

# View metrics (if Prometheus enabled)
curl http://localhost:8000/metrics | grep hook_

# Enable debug logging
export LOG_LEVEL=DEBUG
export LOG_FORMAT=text
```

## Environment Variables Cheatsheet

```bash
# Logging
export LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
export LOG_FORMAT=json                   # json or text
export LOG_FILE=/path/to/log.log         # Optional

# Metrics
export METRICS_ENABLED=true
export PROMETHEUS_PORT=8000

# Datadog (optional)
export DATADOG_ENABLED=false
export DATADOG_API_KEY=your_key
export DATADOG_SERVICE=decentclaude
export DATADOG_ENV=dev

# Sentry (optional)
export SENTRY_ENABLED=false
export SENTRY_DSN=your_dsn
export SENTRY_ENVIRONMENT=dev
export SENTRY_TRACES_SAMPLE_RATE=0.1

# Cost Tracking
export COST_ALERT_THRESHOLD_USD=100.0
export COST_TRACKING_ENABLED=true
```

## Key Metrics

### SQL Validation
```
hook_invocation{hook="PreToolUse__sql-validation"}
hook_sql_validation_queries_processed
hook_sql_validation_validation_passed
hook_sql_validation_validation_failed
hook_sql_validation_warnings
hook_sql_validation_duration_seconds
```

### Auto-Formatting
```
hook_invocation{hook="PostToolUse__auto-formatting"}
hook_auto_format_files_formatted
hook_auto_format_files_unchanged
hook_auto_format_format_failed
hook_auto_format_duration_seconds
```

### Cost Tracking
```
hook_invocation{hook="PostToolUse__cost-tracking"}
hook_cost_tracking_budget_exceeded
hook_cost_tracking_budget_warning
hook_cost_tracking_expensive_query
hook_cost_tracking_session_total_usd (gauge)
hook_cost_tracking_daily_total_usd (gauge)
hook_cost_tracking_session_budget_percent (gauge)
hook_cost_tracking_daily_budget_percent (gauge)
bigquery_bytes_processed
bigquery_cost_usd
bigquery_total_cost_usd
bigquery_query_duration_seconds
```

## Prometheus Queries

```promql
# Hook execution rate (per second)
rate(hook_invocation[5m])

# Hook success rate (%)
100 * rate(hook_success[5m]) / rate(hook_invocation[5m])

# Average hook duration (seconds)
rate(hook_duration_seconds_sum[5m]) / rate(hook_duration_seconds_count[5m])

# P95 hook duration (seconds)
histogram_quantile(0.95, rate(hook_duration_seconds_bucket[5m]))

# BigQuery cost per hour (USD)
rate(bigquery_total_cost_usd[1h])

# Current session budget usage (%)
100 * hook_cost_tracking_session_budget_percent

# Current daily budget usage (%)
100 * hook_cost_tracking_daily_budget_percent

# SQL validation failure rate (%)
100 * rate(hook_sql_validation_validation_failed[5m]) / rate(hook_sql_validation_queries_processed[5m])

# Auto-format success rate (%)
100 * rate(hook_auto_format_files_formatted[5m]) / (rate(hook_auto_format_files_formatted[5m]) + rate(hook_auto_format_format_failed[5m]))
```

## Common Tasks

### Add Observability to New Hook

```bash
#!/usr/bin/env bash
set -euo pipefail

HOOK_NAME="YourHook__name"
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
START_TIME=$(date +%s.%N)

call_observability() {
    local action="$1"; shift
    python3 "$HOOK_DIR/lib/hook_observability.py" "$action" "$HOOK_NAME" "$@" 2>/dev/null || true
}

call_observability "start"

# Your hook logic here

# Track custom metric
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_counter('hook.your_metric', tags={'hook': '$HOOK_NAME'})
" 2>/dev/null || true

END_TIME=$(date +%s.%N)
DURATION=$(echo "$END_TIME - $START_TIME" | bc)
call_observability "end" "true"
```

### Track Custom Metric

```bash
# Counter
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_counter('hook.my_counter', tags={'hook': '$HOOK_NAME', 'type': 'example'})
" 2>/dev/null || true

# Gauge
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_gauge('hook.my_gauge', 42.0, tags={'hook': '$HOOK_NAME'})
" 2>/dev/null || true

# Histogram
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_histogram('hook.my_histogram', 1.23, tags={'hook': '$HOOK_NAME'})
" 2>/dev/null || true
```

### Log Structured Event

```bash
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.logger import get_logger
logger = get_logger('hook.$HOOK_NAME')
logger.info('Event occurred', hook='$HOOK_NAME', key='value', count=42)
" 2>/dev/null || true
```

### Track Error

```bash
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.errors import capture_exception
try:
    # Your code
    raise Exception('Something went wrong')
except Exception as e:
    capture_exception(e, context={'hook': '$HOOK_NAME', 'detail': 'more info'})
" 2>/dev/null || true
```

## Testing Individual Hooks

```bash
# SQL Validation
echo '{"tool": "mcp__bigquery__run_query", "arguments": {"sql": "SELECT 1"}}' | \
  ./PreToolUse__sql-validation.sh

# Auto-Formatting
echo '{"tool": "Write", "arguments": {"file_path": "/tmp/test.py"}}' | \
  ./PostToolUse__auto-formatting.sh

# Cost Tracking
echo '{"tool": "mcp__bigquery__run_query", "arguments": {"sql": "SELECT 1"}, "result": {"bytes_processed": 1024000}}' | \
  ./PostToolUse__cost-tracking.sh
```

## Troubleshooting

### Observability not working
```bash
# Check Python path
python3 -c "import sys; sys.path.insert(0, '../../'); from observability import logger; print('OK')"

# Check dependencies
pip list | grep -E '(prometheus|datadog|sentry)'

# Enable verbose logging
export LOG_LEVEL=DEBUG
export LOG_FORMAT=text
```

### Metrics not appearing
```bash
# Check if Prometheus is running
curl http://localhost:8000/metrics

# Check if metrics are enabled
echo $METRICS_ENABLED

# Check for errors
export LOG_LEVEL=DEBUG
./test-observability.sh 2>&1 | grep -i error
```

### High memory usage
```bash
# Disable Prometheus
export METRICS_ENABLED=false

# Or use Datadog StatsD instead
export METRICS_ENABLED=false
export DATADOG_ENABLED=true
```

## File Locations

```
examples/hooks/
├── lib/
│   ├── __init__.py
│   └── hook_observability.py
├── PreToolUse__sql-validation.sh
├── PostToolUse__auto-formatting.sh
├── PostToolUse__cost-tracking.sh
├── test-observability.sh
├── OBSERVABILITY.md
├── INTEGRATION_SUMMARY.md
└── QUICK_REFERENCE.md (this file)
```

## Resources

- **Full Documentation**: See `OBSERVABILITY.md`
- **Integration Details**: See `INTEGRATION_SUMMARY.md`
- **Test Script**: Run `./test-observability.sh`
- **Observability Framework**: `/Users/crlough/gt/decentclaude/mayor/rig/observability/`

## Support

For issues or questions:
1. Check `OBSERVABILITY.md` for detailed documentation
2. Run `./test-observability.sh` to verify setup
3. Enable debug logging: `export LOG_LEVEL=DEBUG`
4. Check Prometheus metrics: `curl http://localhost:8000/metrics`
