#!/usr/bin/env bash
#
# Test script for hook examples
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Testing Claude Code Hook Examples"
echo "================================="
echo

# Test 1: SQL Validation Hook - Good Query
echo -e "${GREEN}Test 1: SQL Validation - Valid Query${NC}"
echo '{"tool": "mcp__bigquery__run_query", "arguments": {"sql": "SELECT id, name FROM dataset.table WHERE date >= CURRENT_DATE() LIMIT 10"}}' | \
    "$SCRIPT_DIR/PreToolUse__sql-validation.sh" && \
    echo -e "${GREEN}✓ PASSED${NC}\n" || \
    echo -e "${RED}✗ FAILED${NC}\n"

# Test 2: SQL Validation Hook - SELECT * without LIMIT
echo -e "${YELLOW}Test 2: SQL Validation - SELECT * (should warn)${NC}"
echo '{"tool": "mcp__bigquery__run_query", "arguments": {"sql": "SELECT * FROM big_table WHERE id = 1"}}' | \
    "$SCRIPT_DIR/PreToolUse__sql-validation.sh" && \
    echo -e "${GREEN}✓ Warning issued${NC}\n" || \
    echo -e "${YELLOW}⚠ Blocked or warned${NC}\n"

# Test 3: SQL Validation Hook - Invalid SQL
echo -e "${RED}Test 3: SQL Validation - Invalid SQL (should fail)${NC}"
echo '{"tool": "mcp__bigquery__run_query", "arguments": {"sql": "INVALID SQL QUERY"}}' | \
    "$SCRIPT_DIR/PreToolUse__sql-validation.sh" && \
    echo -e "${RED}✗ Should have failed${NC}\n" || \
    echo -e "${GREEN}✓ Correctly blocked${NC}\n"

# Test 4: SQL Validation Hook - Unmatched parentheses
echo -e "${RED}Test 4: SQL Validation - Unmatched Parentheses (should fail)${NC}"
echo '{"tool": "mcp__bigquery__run_query", "arguments": {"sql": "SELECT func(col FROM table"}}' | \
    "$SCRIPT_DIR/PreToolUse__sql-validation.sh" && \
    echo -e "${RED}✗ Should have failed${NC}\n" || \
    echo -e "${GREEN}✓ Correctly blocked${NC}\n"

# Test 5: Auto-formatting Hook - Python file
echo -e "${GREEN}Test 5: Auto-formatting - Python file${NC}"
TEMP_PY="/tmp/test_format.py"
echo "def hello():print('test')" > "$TEMP_PY"
echo "{\"tool\": \"Write\", \"arguments\": {\"file_path\": \"$TEMP_PY\"}, \"result\": {\"success\": true}}" | \
    "$SCRIPT_DIR/PostToolUse__auto-formatting.sh" && \
    echo -e "${GREEN}✓ PASSED${NC}\n" || \
    echo -e "${YELLOW}⚠ No formatter or failed${NC}\n"

# Test 6: Cost Tracking Hook
echo -e "${GREEN}Test 6: Cost Tracking - BigQuery Query${NC}"
echo '{
  "tool": "mcp__bigquery__run_query",
  "arguments": {"sql": "SELECT * FROM table LIMIT 100"},
  "result": {
    "bytes_processed": 1073741824,
    "total_rows": 100,
    "execution_time_ms": 1500
  }
}' | "$SCRIPT_DIR/PostToolUse__cost-tracking.sh" && \
    echo -e "${GREEN}✓ PASSED${NC}\n" || \
    echo -e "${RED}✗ FAILED${NC}\n"

# Test 7: Hook skips non-matching tools
echo -e "${GREEN}Test 7: Hooks Skip Non-matching Tools${NC}"
echo '{"tool": "SomethingElse", "arguments": {}}' | \
    "$SCRIPT_DIR/PreToolUse__sql-validation.sh" && \
    echo -e "${GREEN}✓ Correctly skipped${NC}\n" || \
    echo -e "${RED}✗ Should not have blocked${NC}\n"

echo "================================="
echo "Test suite completed"
echo
echo "Check logs at:"
echo "  - Auto-format: ~/.claude/auto-format.log"
echo "  - Cost tracking: ~/.claude/bigquery-costs.log"
