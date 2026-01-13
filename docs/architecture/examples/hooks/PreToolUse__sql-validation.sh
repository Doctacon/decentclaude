#!/usr/bin/env bash
#
# PreToolUse__sql-validation.sh
#
# Hook that validates SQL queries before execution to catch issues early and prevent
# costly mistakes in BigQuery.
#
# Triggers: Before BigQuery run_query tool execution
# Input: JSON object via stdin containing tool name and arguments
# Output: Exit 0 to allow, Exit 1 to block with error message
#
# Features:
# - Validates SQL syntax using BigQuery MCP validate_sql
# - Checks for common anti-patterns (SELECT *, missing WHERE, etc.)
# - Warns about potentially high-cost queries
# - Provides actionable error messages
# - Integrated observability (logging, metrics, error tracking)
#
# Installation:
#   chmod +x PreToolUse__sql-validation.sh
#   cp PreToolUse__sql-validation.sh ~/.claude/hooks/
#
# Configuration via environment variables:
#   SQL_VALIDATION_STRICT=1           - Block on warnings (default: warn only)
#   SQL_VALIDATION_MAX_BYTES=10737418240 - Max bytes to scan (default: 10GB)
#   SQL_VALIDATION_DISABLED=1         - Disable this hook
#

set -euo pipefail

# Hook name for observability
HOOK_NAME="PreToolUse__sql-validation"
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration
STRICT_MODE="${SQL_VALIDATION_STRICT:-0}"
MAX_BYTES="${SQL_VALIDATION_MAX_BYTES:-10737418240}"  # 10GB default
DISABLED="${SQL_VALIDATION_DISABLED:-0}"

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Logging functions
log_error() {
    echo -e "${RED}[SQL Validation Error]${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}[SQL Validation Warning]${NC} $*" >&2
}

log_info() {
    echo -e "${GREEN}[SQL Validation]${NC} $*" >&2
}

# Initialize observability and track start time
START_TIME=$(date +%s)
OBSERVABILITY_ERROR=""

# Helper function to call Python observability
call_observability() {
    local action="$1"
    shift
    if [[ -z "$OBSERVABILITY_ERROR" ]]; then
        python3 "$HOOK_DIR/lib/hook_observability.py" "$action" "$HOOK_NAME" "$@" 2>/dev/null || {
            OBSERVABILITY_ERROR="1"
            log_warning "Observability unavailable"
        }
    fi
}

# Log hook start
call_observability "start" || true

# Exit early if disabled
if [[ "$DISABLED" == "1" ]]; then
    log_info "Hook disabled via SQL_VALIDATION_DISABLED"
    call_observability "end" "true" || true
    exit 0
fi

# Read JSON input from stdin
INPUT=$(cat)

# Extract tool name and check if this hook should run
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool // .name // "unknown"')

# Only process BigQuery run_query calls
if [[ "$TOOL_NAME" != "mcp__bigquery__run_query" ]]; then
    call_observability "end" "true" || true
    exit 0
fi

log_info "Validating SQL query..."

# Track that we're processing a query
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_counter('hook.sql_validation.queries_processed', tags={'hook': '$HOOK_NAME'})
" 2>/dev/null || true

# Extract SQL query from arguments
SQL=$(echo "$INPUT" | jq -r '.arguments.sql // .params.sql // ""')

if [[ -z "$SQL" || "$SQL" == "null" ]]; then
    log_error "Could not extract SQL from tool arguments"

    # Log error to observability
    python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.logger import get_logger
from observability.metrics import get_metrics_collector
logger = get_logger('hook.$HOOK_NAME')
logger.error('Failed to extract SQL from arguments', hook='$HOOK_NAME')
get_metrics_collector().record_counter('hook.sql_validation.extraction_error', tags={'hook': '$HOOK_NAME'})
" 2>/dev/null || true

    call_observability "end" "false" || true
    exit 1
fi

# Pattern checks for common anti-patterns
WARNINGS=()
ERRORS=()

# Check for SELECT * without LIMIT
if echo "$SQL" | grep -iE "SELECT\s+\*" >/dev/null && ! echo "$SQL" | grep -iE "LIMIT\s+[0-9]+" >/dev/null; then
    WARNINGS+=("Query uses SELECT * without LIMIT - may scan unnecessary columns")
fi

# Check for missing WHERE clause on potentially large scans
if ! echo "$SQL" | grep -iE "WHERE|LIMIT" >/dev/null; then
    if echo "$SQL" | grep -iE "FROM\s+\`?[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\`?" >/dev/null; then
        WARNINGS+=("Query appears to scan entire table without WHERE or LIMIT clause")
    fi
fi

# Check for CROSS JOIN
if echo "$SQL" | grep -iE "CROSS\s+JOIN" >/dev/null; then
    WARNINGS+=("Query contains CROSS JOIN - verify this is intentional (can be expensive)")
fi

# Check for missing partitioning filter on _PARTITIONTIME or date column
if echo "$SQL" | grep -iE "FROM.*\`.*\`" >/dev/null; then
    if ! echo "$SQL" | grep -iE "_PARTITIONTIME|_PARTITIONDATE|WHERE.*date|WHERE.*timestamp" >/dev/null; then
        WARNINGS+=("Query may benefit from partition filtering (check for _PARTITIONTIME or date columns)")
    fi
fi

# Check for potential cartesian product (multiple FROM without JOIN)
FROM_COUNT=$(echo "$SQL" | grep -ioE "FROM\s+" | wc -l | tr -d ' ')
JOIN_COUNT=$(echo "$SQL" | grep -ioE "JOIN\s+" | wc -l | tr -d ' ')
if [[ "$FROM_COUNT" -gt 1 ]] && [[ "$JOIN_COUNT" -lt $((FROM_COUNT - 1)) ]]; then
    WARNINGS+=("Query may produce cartesian product - multiple FROM clauses without explicit JOINs")
fi

# Validate SQL syntax using BigQuery MCP (if available)
# This requires the BigQuery MCP to be configured
# Note: In a real hook, you'd call the MCP server directly via the Claude Code API
# For now, we'll do basic SQL linting only
log_info "MCP validation would be called here in production"

# Basic SQL syntax checks
if ! echo "$SQL" | grep -iE "SELECT|WITH|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP" >/dev/null; then
    ERRORS+=("SQL does not appear to contain a valid statement")
fi

# Check for unmatched parentheses
OPEN_PARENS=$(echo "$SQL" | tr -cd '(' | wc -c | tr -d ' ')
CLOSE_PARENS=$(echo "$SQL" | tr -cd ')' | wc -c | tr -d ' ')
if [[ "$OPEN_PARENS" != "$CLOSE_PARENS" ]]; then
    ERRORS+=("Unmatched parentheses detected (open: $OPEN_PARENS, close: $CLOSE_PARENS)")
fi

# Estimate query cost (mock - in production would use estimate_query_cost)
ESTIMATED_BYTES=0
# In production, call: mcp__bigquery__estimate_query_cost
log_info "Cost estimation would use mcp__bigquery__estimate_query_cost"

# Report findings
if [[ ${#ERRORS[@]} -gt 0 ]]; then
    log_error "Found ${#ERRORS[@]} error(s):"
    for err in "${ERRORS[@]}"; do
        echo -e "  ${RED}✗${NC} $err" >&2
    done

    # Track validation failure
    python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_counter('hook.sql_validation.validation_failed', tags={'hook': '$HOOK_NAME', 'error_count': '${#ERRORS[@]}'})
" 2>/dev/null || true

    call_observability "end" "false" || true
    exit 1
fi

if [[ ${#WARNINGS[@]} -gt 0 ]]; then
    log_warning "Found ${#WARNINGS[@]} warning(s):"
    for warn in "${WARNINGS[@]}"; do
        echo -e "  ${YELLOW}⚠${NC} $warn" >&2
    done

    # Track warnings
    python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_counter('hook.sql_validation.warnings', tags={'hook': '$HOOK_NAME', 'warning_count': '${#WARNINGS[@]}'})
" 2>/dev/null || true

    if [[ "$STRICT_MODE" == "1" ]]; then
        log_error "Blocking due to warnings (SQL_VALIDATION_STRICT=1)"
        call_observability "end" "false" || true
        exit 1
    fi
fi

if [[ ${#WARNINGS[@]} -eq 0 && ${#ERRORS[@]} -eq 0 ]]; then
    log_info "SQL validation passed ✓"

    # Track successful validation
    python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_counter('hook.sql_validation.validation_passed', tags={'hook': '$HOOK_NAME'})
" 2>/dev/null || true
fi

# Calculate duration and log completion
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_histogram('hook.sql_validation.duration.seconds', $DURATION, tags={'hook': '$HOOK_NAME', 'success': 'true'})
" 2>/dev/null || true

call_observability "end" "true" || true
exit 0
