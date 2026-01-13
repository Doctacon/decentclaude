#!/usr/bin/env bash
#
# PostToolUse__cost-tracking.sh
#
# Hook that tracks BigQuery query costs to help monitor spending and prevent
# budget overruns during development and analysis.
#
# Triggers: After BigQuery run_query execution
# Input: JSON object via stdin containing tool result
# Output: Updated cost log and budget warnings
#
# Features:
# - Logs every query with cost estimate and bytes scanned
# - Maintains running total of session costs
# - Warns when approaching daily/session budget thresholds
# - Provides cost breakdown by project/dataset
# - Supports multiple cost tiers and alerting levels
# - Integrated observability (logging, metrics, error tracking)
#
# Installation:
#   chmod +x PostToolUse__cost-tracking.sh
#   cp PostToolUse__cost-tracking.sh ~/.claude/hooks/
#
# Configuration via environment variables:
#   COST_TRACKING_DISABLED=1          - Disable this hook
#   COST_TRACKING_LOG=~/.claude/bigquery-costs.log - Log file location
#   COST_TRACKING_DAILY_BUDGET=100    - Daily budget in USD (default: 100)
#   COST_TRACKING_SESSION_BUDGET=10   - Per-session budget in USD (default: 10)
#   COST_TRACKING_WARN_THRESHOLD=0.8  - Warn at 80% of budget (default: 0.8)
#   COST_TRACKING_PRICE_PER_TB=6.25   - BigQuery price per TB (default: $6.25)
#

set -euo pipefail

# Hook name for observability
HOOK_NAME="PostToolUse__cost-tracking"
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration
DISABLED="${COST_TRACKING_DISABLED:-0}"
LOG_FILE="${COST_TRACKING_LOG:-${HOME}/.claude/bigquery-costs.log}"
DAILY_BUDGET="${COST_TRACKING_DAILY_BUDGET:-100}"
SESSION_BUDGET="${COST_TRACKING_SESSION_BUDGET:-10}"
WARN_THRESHOLD="${COST_TRACKING_WARN_THRESHOLD:-0.8}"
PRICE_PER_TB="${COST_TRACKING_PRICE_PER_TB:-6.25}"  # $6.25 per TB as of 2024
SESSION_FILE="${HOME}/.claude/bigquery-session-${PPID}.costs"

# Color codes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[Cost Tracking]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[Cost Tracking]${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}[Cost Tracking Warning]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[Cost Tracking Alert]${NC} $*" >&2
}

log_stats() {
    echo -e "${CYAN}[Cost Stats]${NC} $*" >&2
}

# Initialize observability and track start time
START_TIME=$(date +%s.%N)
OBSERVABILITY_ERROR=""

# Helper function to call Python observability
call_observability() {
    local action="$1"
    shift
    if [[ -z "$OBSERVABILITY_ERROR" ]]; then
        python3 "$HOOK_DIR/lib/hook_observability.py" "$action" "$HOOK_NAME" "$@" 2>/dev/null || {
            OBSERVABILITY_ERROR="1"
        }
    fi
}

# Log hook start
call_observability "start" || true

# Exit early if disabled
if [[ "$DISABLED" == "1" ]]; then
    call_observability "end" "true" || true
    exit 0
fi

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null || true
mkdir -p "$(dirname "$SESSION_FILE")" 2>/dev/null || true

# Initialize session file if it doesn't exist
if [[ ! -f "$SESSION_FILE" ]]; then
    echo "0" > "$SESSION_FILE"
fi

# Read JSON input from stdin
INPUT=$(cat)

# Extract tool name
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool // .name // "unknown"')

# Only process BigQuery run_query calls
if [[ "$TOOL_NAME" != "mcp__bigquery__run_query" ]]; then
    call_observability "end" "true" || true
    exit 0
fi

# Extract query and result information
SQL=$(echo "$INPUT" | jq -r '.arguments.sql // .params.sql // "N/A"')
BYTES_SCANNED=$(echo "$INPUT" | jq -r '.result.bytes_processed // .result.totalBytesProcessed // 0' 2>/dev/null || echo "0")
ROWS_RETURNED=$(echo "$INPUT" | jq -r '.result.total_rows // .result.totalRows // 0' 2>/dev/null || echo "0")
EXECUTION_TIME=$(echo "$INPUT" | jq -r '.result.execution_time_ms // .result.totalTimeMs // 0' 2>/dev/null || echo "0")

# Calculate cost
# BigQuery charges $6.25 per TB (as of 2024)
# Cost = (bytes_scanned / 1_099_511_627_776) * price_per_tb
COST_USD=$(awk "BEGIN {printf \"%.6f\", ($BYTES_SCANNED / 1099511627776.0) * $PRICE_PER_TB}")

# Format bytes for human readability
format_bytes() {
    local bytes=$1
    if [[ $bytes -lt 1024 ]]; then
        echo "${bytes}B"
    elif [[ $bytes -lt 1048576 ]]; then
        echo "$(awk "BEGIN {printf \"%.2f\", $bytes/1024}")KB"
    elif [[ $bytes -lt 1073741824 ]]; then
        echo "$(awk "BEGIN {printf \"%.2f\", $bytes/1048576}")MB"
    elif [[ $bytes -lt 1099511627776 ]]; then
        echo "$(awk "BEGIN {printf \"%.2f\", $bytes/1073741824}")GB"
    else
        echo "$(awk "BEGIN {printf \"%.2f\", $bytes/1099511627776}")TB"
    fi
}

BYTES_FORMATTED=$(format_bytes "$BYTES_SCANNED")

# Update session total
SESSION_TOTAL=$(cat "$SESSION_FILE")
NEW_SESSION_TOTAL=$(awk "BEGIN {printf \"%.6f\", $SESSION_TOTAL + $COST_USD}")
echo "$NEW_SESSION_TOTAL" > "$SESSION_FILE"

# Get today's date for daily tracking
TODAY=$(date +%Y-%m-%d)

# Calculate daily total
DAILY_TOTAL=$(grep "^$TODAY" "$LOG_FILE" 2>/dev/null | awk -F'|' '{sum+=$4} END {printf "%.6f", sum}')
if [[ -z "$DAILY_TOTAL" ]]; then
    DAILY_TOTAL="0"
fi
NEW_DAILY_TOTAL=$(awk "BEGIN {printf \"%.6f\", $DAILY_TOTAL + $COST_USD}")

# Create log entry
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
SQL_PREVIEW=$(echo "$SQL" | tr '\n' ' ' | cut -c1-100)
LOG_ENTRY="$TODAY|$TIMESTAMP|$BYTES_SCANNED|$COST_USD|$ROWS_RETURNED|$EXECUTION_TIME|$SQL_PREVIEW"

# Append to log file
echo "$LOG_ENTRY" >> "$LOG_FILE"

# Display cost information
log_info "Query completed"
log_stats "Bytes scanned: $BYTES_FORMATTED"
log_stats "Estimated cost: \$$COST_USD"
log_stats "Rows returned: $ROWS_RETURNED"

# Track cost metrics via observability framework
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import track_cost, track_query_performance

# Track cost
track_cost(
    operation='bigquery_query',
    bytes_processed=$BYTES_SCANNED,
    estimated_cost_usd=$COST_USD,
    tags={'hook': '$HOOK_NAME'}
)

# Track query performance
track_query_performance(
    query_type='select',
    duration_seconds=$EXECUTION_TIME / 1000.0,
    rows_returned=$ROWS_RETURNED,
    bytes_processed=$BYTES_SCANNED,
    tags={'hook': '$HOOK_NAME'}
)
" 2>/dev/null || true

# Check budget thresholds
SESSION_PERCENT=$(awk "BEGIN {printf \"%.0f\", ($NEW_SESSION_TOTAL / $SESSION_BUDGET) * 100}")
DAILY_PERCENT=$(awk "BEGIN {printf \"%.0f\", ($NEW_DAILY_TOTAL / $DAILY_BUDGET) * 100}")

# Session budget check
if (( $(echo "$NEW_SESSION_TOTAL > $SESSION_BUDGET" | bc -l) )); then
    log_error "Session budget exceeded!"
    log_error "Session total: \$$NEW_SESSION_TOTAL / \$$SESSION_BUDGET (${SESSION_PERCENT}%)"

    # Track budget exceeded
    python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
from observability.logger import get_logger
logger = get_logger('hook.$HOOK_NAME')
logger.warning('Session budget exceeded', hook='$HOOK_NAME', session_total=$NEW_SESSION_TOTAL, budget=$SESSION_BUDGET)
get_metrics_collector().record_counter('hook.cost_tracking.budget_exceeded', tags={'hook': '$HOOK_NAME', 'budget_type': 'session'})
" 2>/dev/null || true
elif (( $(echo "$NEW_SESSION_TOTAL > ($SESSION_BUDGET * $WARN_THRESHOLD)" | bc -l) )); then
    log_warning "Approaching session budget limit"
    log_warning "Session total: \$$NEW_SESSION_TOTAL / \$$SESSION_BUDGET (${SESSION_PERCENT}%)"

    # Track budget warning
    python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_counter('hook.cost_tracking.budget_warning', tags={'hook': '$HOOK_NAME', 'budget_type': 'session'})
" 2>/dev/null || true
else
    log_success "Session total: \$$NEW_SESSION_TOTAL / \$$SESSION_BUDGET (${SESSION_PERCENT}%)"
fi

# Daily budget check
if (( $(echo "$NEW_DAILY_TOTAL > $DAILY_BUDGET" | bc -l) )); then
    log_error "Daily budget exceeded!"
    log_error "Daily total: \$$NEW_DAILY_TOTAL / \$$DAILY_BUDGET (${DAILY_PERCENT}%)"

    # Track budget exceeded
    python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
from observability.logger import get_logger
logger = get_logger('hook.$HOOK_NAME')
logger.warning('Daily budget exceeded', hook='$HOOK_NAME', daily_total=$NEW_DAILY_TOTAL, budget=$DAILY_BUDGET)
get_metrics_collector().record_counter('hook.cost_tracking.budget_exceeded', tags={'hook': '$HOOK_NAME', 'budget_type': 'daily'})
" 2>/dev/null || true
elif (( $(echo "$NEW_DAILY_TOTAL > ($DAILY_BUDGET * $WARN_THRESHOLD)" | bc -l) )); then
    log_warning "Approaching daily budget limit"
    log_warning "Daily total: \$$NEW_DAILY_TOTAL / \$$DAILY_BUDGET (${DAILY_PERCENT}%)"

    # Track budget warning
    python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_counter('hook.cost_tracking.budget_warning', tags={'hook': '$HOOK_NAME', 'budget_type': 'daily'})
" 2>/dev/null || true
else
    log_info "Daily total: \$$NEW_DAILY_TOTAL / \$$DAILY_BUDGET (${DAILY_PERCENT}%)"
fi

# Provide cost-saving tips if query was expensive
if (( $(echo "$COST_USD > 0.10" | bc -l) )); then
    log_warning "Expensive query detected (\$$COST_USD)"
    echo -e "${YELLOW}Cost-saving tips:${NC}" >&2
    echo "  • Use partition filters on _PARTITIONTIME or date columns" >&2
    echo "  • Select only needed columns instead of SELECT *" >&2
    echo "  • Use clustering for frequently filtered columns" >&2
    echo "  • Consider materializing complex queries" >&2

    # Track expensive query
    python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_counter('hook.cost_tracking.expensive_query', tags={'hook': '$HOOK_NAME', 'cost_usd': '$COST_USD'})
" 2>/dev/null || true
fi

# Generate daily summary on first run of the day
LAST_SUMMARY="${HOME}/.claude/.last-cost-summary"
if [[ ! -f "$LAST_SUMMARY" ]] || [[ "$(cat "$LAST_SUMMARY")" != "$TODAY" ]]; then
    echo "$TODAY" > "$LAST_SUMMARY"

    if [[ -f "$LOG_FILE" ]]; then
        echo "" >&2
        log_info "Cost Summary for $TODAY"
        log_info "----------------------------------------"

        # Count queries today
        QUERY_COUNT=$(grep -c "^$TODAY" "$LOG_FILE" 2>/dev/null || echo "0")
        log_stats "Total queries: $QUERY_COUNT"

        # Total bytes scanned today
        TOTAL_BYTES=$(grep "^$TODAY" "$LOG_FILE" 2>/dev/null | awk -F'|' '{sum+=$3} END {printf "%.0f", sum}')
        if [[ -n "$TOTAL_BYTES" && "$TOTAL_BYTES" != "0" ]]; then
            TOTAL_BYTES_FORMATTED=$(format_bytes "$TOTAL_BYTES")
            log_stats "Total data scanned: $TOTAL_BYTES_FORMATTED"
        fi

        # Total cost today
        log_stats "Total cost: \$$NEW_DAILY_TOTAL"
        log_info "----------------------------------------"
    fi
fi

# Track session and daily totals as gauges
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
collector = get_metrics_collector()
collector.record_gauge('hook.cost_tracking.session_total_usd', $NEW_SESSION_TOTAL, tags={'hook': '$HOOK_NAME'})
collector.record_gauge('hook.cost_tracking.daily_total_usd', $NEW_DAILY_TOTAL, tags={'hook': '$HOOK_NAME'})
collector.record_gauge('hook.cost_tracking.session_budget_percent', $SESSION_PERCENT / 100.0, tags={'hook': '$HOOK_NAME'})
collector.record_gauge('hook.cost_tracking.daily_budget_percent', $DAILY_PERCENT / 100.0, tags={'hook': '$HOOK_NAME'})
" 2>/dev/null || true

# Calculate duration and log completion
END_TIME=$(date +%s.%N)
DURATION=$(echo "$END_TIME - $START_TIME" | bc)

python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_histogram('hook.cost_tracking.duration.seconds', $DURATION, tags={'hook': '$HOOK_NAME', 'success': 'true'})
" 2>/dev/null || true

call_observability "end" "true" || true
exit 0
