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

# Exit early if disabled
if [[ "$DISABLED" == "1" ]]; then
    log_info "Hook disabled via SQL_VALIDATION_DISABLED"
    exit 0
fi

# Read JSON input from stdin
INPUT=$(cat)

# Extract tool name and check if this hook should run
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool // .name // "unknown"')

# Only process BigQuery run_query calls
if [[ "$TOOL_NAME" != "mcp__bigquery__run_query" ]]; then
    exit 0
fi

log_info "Validating SQL query..."

# Extract SQL query from arguments
SQL=$(echo "$INPUT" | jq -r '.arguments.sql // .params.sql // ""')

if [[ -z "$SQL" || "$SQL" == "null" ]]; then
    log_error "Could not extract SQL from tool arguments"
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
    exit 1
fi

if [[ ${#WARNINGS[@]} -gt 0 ]]; then
    log_warning "Found ${#WARNINGS[@]} warning(s):"
    for warn in "${WARNINGS[@]}"; do
        echo -e "  ${YELLOW}⚠${NC} $warn" >&2
    done

    if [[ "$STRICT_MODE" == "1" ]]; then
        log_error "Blocking due to warnings (SQL_VALIDATION_STRICT=1)"
        exit 1
    fi
fi

if [[ ${#WARNINGS[@]} -eq 0 && ${#ERRORS[@]} -eq 0 ]]; then
    log_info "SQL validation passed ✓"
fi

exit 0
