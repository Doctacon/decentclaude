#!/usr/bin/env bash
#
# example-observability-integration.sh
#
# Template for creating new hooks with observability integration.
# This is a complete example showing all observability features.
#
# Copy this file and replace the hook logic with your own.
#

set -euo pipefail

##############################################################################
# STEP 1: Hook Identification
##############################################################################
# Set the hook name (used in metrics and logs)
HOOK_NAME="Example__observability-integration"
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

##############################################################################
# STEP 2: Configuration
##############################################################################
# Add your configuration variables here
EXAMPLE_CONFIG="${EXAMPLE_CONFIG:-default_value}"
DISABLED="${EXAMPLE_DISABLED:-0}"

##############################################################################
# STEP 3: Logging Functions (Optional - for colored console output)
##############################################################################
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[Example]${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}[Example Warning]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[Example Error]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[Example]${NC} $*" >&2
}

##############################################################################
# STEP 4: Observability Integration
##############################################################################
# Track start time for duration calculation
START_TIME=$(date +%s.%N)
OBSERVABILITY_ERROR=""

# Helper function to call Python observability
# This function handles errors gracefully so observability failures don't break the hook
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

##############################################################################
# STEP 5: Early Exit Conditions
##############################################################################
# Exit early if disabled
if [[ "$DISABLED" == "1" ]]; then
    log_info "Hook disabled via EXAMPLE_DISABLED"
    call_observability "end" "true" || true
    exit 0
fi

##############################################################################
# STEP 6: Read Input
##############################################################################
# Read JSON input from stdin
INPUT=$(cat)

# Extract tool name
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool // .name // "unknown"')

# Only process specific tools (customize this)
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]]; then
    call_observability "end" "true" || true
    exit 0
fi

log_info "Processing $TOOL_NAME operation"

##############################################################################
# STEP 7: Main Hook Logic
##############################################################################
# Extract data from input (customize based on your needs)
FILE_PATH=$(echo "$INPUT" | jq -r '.arguments.file_path // ""')

if [[ -z "$FILE_PATH" || "$FILE_PATH" == "null" ]]; then
    log_warning "Could not extract file path from tool arguments"

    # Track extraction error in observability
    python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.logger import get_logger
from observability.metrics import get_metrics_collector
logger = get_logger('hook.$HOOK_NAME')
logger.error('Failed to extract file path', hook='$HOOK_NAME')
get_metrics_collector().record_counter('hook.example.extraction_error', tags={'hook': '$HOOK_NAME'})
" 2>/dev/null || true

    call_observability "end" "false" || true
    exit 1
fi

log_info "Processing file: $FILE_PATH"

##############################################################################
# STEP 8: Your Hook Logic Here
##############################################################################
# This is where you implement your hook's functionality
# In this example, we'll just count lines in a file

if [[ ! -f "$FILE_PATH" ]]; then
    log_error "File does not exist: $FILE_PATH"
    call_observability "end" "false" || true
    exit 1
fi

# Example: Count lines
LINE_COUNT=$(wc -l < "$FILE_PATH" | tr -d ' ')
log_info "File has $LINE_COUNT lines"

# Track custom metric - line count
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_gauge('hook.example.line_count', $LINE_COUNT, tags={'hook': '$HOOK_NAME'})
" 2>/dev/null || true

# Example: Check if file is too large
MAX_LINES=1000
if [[ $LINE_COUNT -gt $MAX_LINES ]]; then
    log_warning "File exceeds maximum lines: $LINE_COUNT > $MAX_LINES"

    # Track large file warning
    python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.logger import get_logger
from observability.metrics import get_metrics_collector
logger = get_logger('hook.$HOOK_NAME')
logger.warning('Large file detected', hook='$HOOK_NAME', line_count=$LINE_COUNT, max_lines=$MAX_LINES)
get_metrics_collector().record_counter('hook.example.large_file', tags={'hook': '$HOOK_NAME'})
" 2>/dev/null || true
else
    log_success "File size is acceptable"

    # Track successful processing
    python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_counter('hook.example.processed', tags={'hook': '$HOOK_NAME'})
" 2>/dev/null || true
fi

##############################################################################
# STEP 9: Additional Observability Examples
##############################################################################

# Example: Log structured event with context
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.logger import get_logger
logger = get_logger('hook.$HOOK_NAME')
logger.info('File processed', hook='$HOOK_NAME', file='$FILE_PATH', lines=$LINE_COUNT)
" 2>/dev/null || true

# Example: Track histogram (for distribution of values)
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_histogram('hook.example.file_size_lines', $LINE_COUNT, tags={'hook': '$HOOK_NAME'})
" 2>/dev/null || true

# Example: Capture error with context (only if error occurs)
if false; then  # Change to true to test error tracking
    python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.errors import capture_exception
try:
    raise Exception('Example error for testing')
except Exception as e:
    capture_exception(e, context={'hook': '$HOOK_NAME', 'file': '$FILE_PATH'})
" 2>/dev/null || true
fi

##############################################################################
# STEP 10: Cleanup and Completion
##############################################################################
# Calculate duration
END_TIME=$(date +%s.%N)
DURATION=$(echo "$END_TIME - $START_TIME" | bc)

log_info "Hook completed in ${DURATION}s"

# Track duration metric
python3 -c "
import sys
sys.path.insert(0, '$HOOK_DIR/../../../')
from observability.metrics import get_metrics_collector
get_metrics_collector().record_histogram('hook.example.duration.seconds', $DURATION, tags={'hook': '$HOOK_NAME', 'success': 'true'})
" 2>/dev/null || true

# Log hook end (success)
call_observability "end" "true" || true

exit 0

##############################################################################
# OBSERVABILITY FEATURES DEMONSTRATED
##############################################################################
# 1. Hook start/end logging with duration tracking
# 2. Counter metrics (hook.example.processed, hook.example.large_file)
# 3. Gauge metrics (hook.example.line_count)
# 4. Histogram metrics (hook.example.file_size_lines, hook.example.duration.seconds)
# 5. Structured logging with context
# 6. Error tracking with Sentry
# 7. Graceful degradation (|| true on all observability calls)
# 8. Warning tracking
# 9. Custom metrics with tags
# 10. Integration with observability framework

##############################################################################
# METRICS GENERATED BY THIS HOOK
##############################################################################
# - hook.invocation{hook="Example__observability-integration"} - Counter
# - hook.success{hook="Example__observability-integration"} - Counter
# - hook.failure{hook="Example__observability-integration"} - Counter
# - hook.duration.seconds{hook="Example__observability-integration"} - Histogram
# - hook.example.extraction_error{hook="Example__observability-integration"} - Counter
# - hook.example.line_count{hook="Example__observability-integration"} - Gauge
# - hook.example.large_file{hook="Example__observability-integration"} - Counter
# - hook.example.processed{hook="Example__observability-integration"} - Counter
# - hook.example.file_size_lines{hook="Example__observability-integration"} - Histogram
# - hook.example.duration.seconds{hook="Example__observability-integration"} - Histogram

##############################################################################
# USAGE
##############################################################################
# 1. Copy this file to your new hook name
# 2. Update HOOK_NAME
# 3. Update configuration variables
# 4. Replace the hook logic (STEP 8)
# 5. Add custom metrics as needed
# 6. Test with: echo '{"tool": "Write", "arguments": {"file_path": "/tmp/test.txt"}}' | ./your-hook.sh
# 7. View metrics at: http://localhost:8000/metrics

##############################################################################
# PROMETHEUS QUERIES FOR THIS HOOK
##############################################################################
# Hook execution rate:
#   rate(hook_invocation{hook="Example__observability-integration"}[5m])
#
# Hook success rate:
#   rate(hook_success{hook="Example__observability-integration"}[5m]) /
#   rate(hook_invocation{hook="Example__observability-integration"}[5m])
#
# Average hook duration:
#   rate(hook_duration_seconds_sum{hook="Example__observability-integration"}[5m]) /
#   rate(hook_duration_seconds_count{hook="Example__observability-integration"}[5m])
#
# P95 duration:
#   histogram_quantile(0.95, rate(hook_duration_seconds_bucket{hook="Example__observability-integration"}[5m]))
#
# Average file size (lines):
#   avg(hook_example_line_count{hook="Example__observability-integration"})
#
# Large file rate:
#   rate(hook_example_large_file{hook="Example__observability-integration"}[5m])
