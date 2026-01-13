#!/usr/bin/env bash
#
# test-observability.sh
#
# Test script to verify observability integration in hooks
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Testing Hook Observability Integration ===${NC}\n"

# Test 1: Test the observability module directly
echo -e "${YELLOW}Test 1: Observability module CLI${NC}"
if python3 "$SCRIPT_DIR/lib/hook_observability.py" test test_hook 2>&1; then
    echo -e "${GREEN}✓ Observability module test passed${NC}\n"
else
    echo -e "${RED}✗ Observability module test failed${NC}\n"
fi

# Test 2: Test SQL validation hook
echo -e "${YELLOW}Test 2: SQL Validation Hook${NC}"
TEST_INPUT='{"tool": "mcp__bigquery__run_query", "arguments": {"sql": "SELECT * FROM table LIMIT 10"}}'
if echo "$TEST_INPUT" | "$SCRIPT_DIR/PreToolUse__sql-validation.sh" 2>&1 | head -20; then
    echo -e "${GREEN}✓ SQL validation hook executed${NC}\n"
else
    echo -e "${RED}✗ SQL validation hook failed${NC}\n"
fi

# Test 3: Test auto-formatting hook with a dummy file
echo -e "${YELLOW}Test 3: Auto-Formatting Hook${NC}"
TEST_FILE="/tmp/test_format_$(date +%s).py"
echo "def test():pass" > "$TEST_FILE"
TEST_INPUT="{\"tool\": \"Write\", \"arguments\": {\"file_path\": \"$TEST_FILE\"}}"
if echo "$TEST_INPUT" | "$SCRIPT_DIR/PostToolUse__auto-formatting.sh" 2>&1 | head -20; then
    echo -e "${GREEN}✓ Auto-formatting hook executed${NC}"
    rm -f "$TEST_FILE" "$TEST_FILE.bak"
else
    echo -e "${RED}✗ Auto-formatting hook failed${NC}"
    rm -f "$TEST_FILE" "$TEST_FILE.bak"
fi
echo ""

# Test 4: Test cost tracking hook
echo -e "${YELLOW}Test 4: Cost Tracking Hook${NC}"
TEST_INPUT='{"tool": "mcp__bigquery__run_query", "arguments": {"sql": "SELECT 1"}, "result": {"bytes_processed": 1024000, "total_rows": 100, "execution_time_ms": 500}}'
if echo "$TEST_INPUT" | "$SCRIPT_DIR/PostToolUse__cost-tracking.sh" 2>&1 | head -30; then
    echo -e "${GREEN}✓ Cost tracking hook executed${NC}\n"
else
    echo -e "${RED}✗ Cost tracking hook failed${NC}\n"
fi

# Test 5: Check if metrics are being collected (if Prometheus is enabled)
echo -e "${YELLOW}Test 5: Metrics Collection${NC}"
if command -v curl >/dev/null 2>&1; then
    PROMETHEUS_PORT="${PROMETHEUS_PORT:-8000}"
    if curl -s "http://localhost:$PROMETHEUS_PORT/metrics" 2>/dev/null | grep -q "hook_"; then
        echo -e "${GREEN}✓ Prometheus metrics available at http://localhost:$PROMETHEUS_PORT/metrics${NC}\n"
    else
        echo -e "${YELLOW}⚠ Prometheus metrics not available (server may not be running)${NC}\n"
    fi
else
    echo -e "${YELLOW}⚠ curl not available, skipping metrics check${NC}\n"
fi

# Test 6: Verify Python dependencies
echo -e "${YELLOW}Test 6: Python Dependencies${NC}"
MISSING_DEPS=0

if python3 -c "import prometheus_client" 2>/dev/null; then
    echo -e "${GREEN}✓ prometheus_client installed${NC}"
else
    echo -e "${YELLOW}⚠ prometheus_client not installed (optional)${NC}"
    MISSING_DEPS=1
fi

if python3 -c "import datadog" 2>/dev/null; then
    echo -e "${GREEN}✓ datadog installed${NC}"
else
    echo -e "${YELLOW}⚠ datadog not installed (optional)${NC}"
    MISSING_DEPS=1
fi

if python3 -c "import sentry_sdk" 2>/dev/null; then
    echo -e "${GREEN}✓ sentry-sdk installed${NC}"
else
    echo -e "${YELLOW}⚠ sentry-sdk not installed (optional)${NC}"
    MISSING_DEPS=1
fi

if [[ $MISSING_DEPS -eq 1 ]]; then
    echo -e "\n${YELLOW}To install optional dependencies:${NC}"
    echo "  pip install prometheus-client datadog sentry-sdk"
fi
echo ""

# Test 7: Verify observability configuration
echo -e "${YELLOW}Test 7: Observability Configuration${NC}"
python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR/../../')
from observability.config import get_config

config = get_config()
print(f'Service Name: {config.service_name}')
print(f'Environment: {config.environment}')
print(f'Log Level: {config.log_level}')
print(f'Log Format: {config.log_format}')
print(f'Metrics Enabled: {config.metrics_enabled}')
print(f'Datadog Enabled: {config.datadog_enabled}')
print(f'Sentry Enabled: {config.sentry_enabled}')

issues = config.validate()
if issues:
    print(f'\nConfiguration Issues:')
    for issue in issues:
        print(f'  - {issue}')
else:
    print('\n✓ Configuration valid')
" 2>&1
echo ""

# Summary
echo -e "${BLUE}=== Test Summary ===${NC}"
echo -e "All hook scripts have been tested with observability integration."
echo -e "Check the output above for any errors or warnings."
echo -e ""
echo -e "Next steps:"
echo -e "  1. Set environment variables for production (see OBSERVABILITY.md)"
echo -e "  2. Configure Prometheus/Datadog/Sentry if needed"
echo -e "  3. Install hooks in ~/.claude/hooks/ directory"
echo -e "  4. Monitor metrics at http://localhost:8000/metrics"
echo -e ""
echo -e "${GREEN}Testing complete!${NC}"
