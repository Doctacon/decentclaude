#!/usr/bin/env bash
#
# PostToolUse__auto-formatting.sh
#
# Hook that automatically formats code files after Write/Edit operations to maintain
# consistent code style across the project.
#
# Triggers: After Write or Edit tool execution
# Input: JSON object via stdin containing tool result and file path
# Output: Formatted file (or original if formatting fails)
#
# Features:
# - Auto-detects file type from extension
# - Runs appropriate formatter (black, sqlfluff, prettier, etc.)
# - Gracefully handles missing formatters
# - Preserves original file if formatting fails
# - Logs formatting actions for audit trail
#
# Installation:
#   chmod +x PostToolUse__auto-formatting.sh
#   cp PostToolUse__auto-formatting.sh ~/.claude/hooks/
#
# Configuration via environment variables:
#   AUTO_FORMAT_DISABLED=1       - Disable this hook
#   AUTO_FORMAT_PYTHON=black     - Python formatter (default: black)
#   AUTO_FORMAT_SQL=sqlfluff     - SQL formatter (default: sqlfluff)
#   AUTO_FORMAT_JS=prettier      - JS/TS formatter (default: prettier)
#   AUTO_FORMAT_BACKUP=1         - Create .bak files (default: 0)
#

set -euo pipefail

# Configuration
DISABLED="${AUTO_FORMAT_DISABLED:-0}"
PYTHON_FORMATTER="${AUTO_FORMAT_PYTHON:-black}"
SQL_FORMATTER="${AUTO_FORMAT_SQL:-sqlfluff}"
JS_FORMATTER="${AUTO_FORMAT_JS:-prettier}"
CREATE_BACKUP="${AUTO_FORMAT_BACKUP:-0}"
LOG_FILE="${AUTO_FORMAT_LOG:-${HOME}/.claude/auto-format.log}"

# Color codes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[Auto-Format]${NC} $*" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $*" >> "$LOG_FILE" 2>/dev/null || true
}

log_success() {
    echo -e "${GREEN}[Auto-Format]${NC} $*" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $*" >> "$LOG_FILE" 2>/dev/null || true
}

log_warning() {
    echo -e "${YELLOW}[Auto-Format]${NC} $*" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $*" >> "$LOG_FILE" 2>/dev/null || true
}

log_error() {
    echo -e "${RED}[Auto-Format]${NC} $*" >&2
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $*" >> "$LOG_FILE" 2>/dev/null || true
}

# Exit early if disabled
if [[ "$DISABLED" == "1" ]]; then
    exit 0
fi

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")" 2>/dev/null || true

# Read JSON input from stdin
INPUT=$(cat)

# Extract tool name
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool // .name // "unknown"')

# Only process Write and Edit tools
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]]; then
    exit 0
fi

# Extract file path
FILE_PATH=$(echo "$INPUT" | jq -r '.arguments.file_path // .result.file_path // ""')

if [[ -z "$FILE_PATH" || "$FILE_PATH" == "null" ]]; then
    log_warning "Could not extract file path from tool result"
    exit 0
fi

if [[ ! -f "$FILE_PATH" ]]; then
    log_warning "File does not exist: $FILE_PATH"
    exit 0
fi

# Get file extension
EXTENSION="${FILE_PATH##*.}"
FILENAME=$(basename "$FILE_PATH")

log_info "Processing $FILENAME"

# Determine formatter based on file extension
FORMATTER=""
FORMATTER_ARGS=()

case "$EXTENSION" in
    py)
        if command -v "$PYTHON_FORMATTER" >/dev/null 2>&1; then
            FORMATTER="$PYTHON_FORMATTER"
            if [[ "$PYTHON_FORMATTER" == "black" ]]; then
                FORMATTER_ARGS=("--quiet" "$FILE_PATH")
            elif [[ "$PYTHON_FORMATTER" == "autopep8" ]]; then
                FORMATTER_ARGS=("--in-place" "--aggressive" "--aggressive" "$FILE_PATH")
            elif [[ "$PYTHON_FORMATTER" == "yapf" ]]; then
                FORMATTER_ARGS=("--in-place" "$FILE_PATH")
            fi
        fi
        ;;

    sql)
        if command -v "$SQL_FORMATTER" >/dev/null 2>&1; then
            FORMATTER="$SQL_FORMATTER"
            if [[ "$SQL_FORMATTER" == "sqlfluff" ]]; then
                FORMATTER_ARGS=("format" "--nocolor" "$FILE_PATH")
            elif [[ "$SQL_FORMATTER" == "pg_format" ]]; then
                FORMATTER_ARGS=("--inplace" "$FILE_PATH")
            fi
        fi
        ;;

    js|jsx|ts|tsx|json|yaml|yml|md|css|scss|html)
        if command -v "$JS_FORMATTER" >/dev/null 2>&1; then
            FORMATTER="$JS_FORMATTER"
            if [[ "$JS_FORMATTER" == "prettier" ]]; then
                FORMATTER_ARGS=("--write" "$FILE_PATH")
            fi
        fi
        ;;

    sh|bash)
        if command -v shfmt >/dev/null 2>&1; then
            FORMATTER="shfmt"
            FORMATTER_ARGS=("-w" "-i" "2" "-ci" "$FILE_PATH")
        fi
        ;;

    go)
        if command -v gofmt >/dev/null 2>&1; then
            FORMATTER="gofmt"
            FORMATTER_ARGS=("-w" "$FILE_PATH")
        fi
        ;;

    rs)
        if command -v rustfmt >/dev/null 2>&1; then
            FORMATTER="rustfmt"
            FORMATTER_ARGS=("$FILE_PATH")
        fi
        ;;

    *)
        log_info "No formatter configured for .$EXTENSION files"
        exit 0
        ;;
esac

# No formatter available
if [[ -z "$FORMATTER" ]]; then
    log_warning "Formatter not found: $([[ -n "${PYTHON_FORMATTER:-}" ]] && echo "$PYTHON_FORMATTER" || echo "unknown")"
    log_info "Install with: pip install black (Python) or npm install -g prettier (JS/TS)"
    exit 0
fi

# Create backup if requested
if [[ "$CREATE_BACKUP" == "1" ]]; then
    cp "$FILE_PATH" "$FILE_PATH.bak"
    log_info "Created backup: $FILE_PATH.bak"
fi

# Get original file hash for comparison
ORIGINAL_HASH=$(shasum -a 256 "$FILE_PATH" | cut -d' ' -f1)

# Run formatter
log_info "Running $FORMATTER on $FILENAME"
if "$FORMATTER" "${FORMATTER_ARGS[@]}" 2>&1 | head -20; then
    # Check if file was actually modified
    NEW_HASH=$(shasum -a 256 "$FILE_PATH" | cut -d' ' -f1)

    if [[ "$ORIGINAL_HASH" != "$NEW_HASH" ]]; then
        log_success "Formatted $FILENAME with $FORMATTER ✓"
    else
        log_info "No changes needed for $FILENAME"
    fi
else
    log_error "Formatting failed for $FILENAME"

    # Restore from backup if it exists
    if [[ -f "$FILE_PATH.bak" ]]; then
        mv "$FILE_PATH.bak" "$FILE_PATH"
        log_warning "Restored original file from backup"
    fi

    # Don't fail the hook - just warn
    exit 0
fi

# Clean up backup if not requested
if [[ "$CREATE_BACKUP" == "0" ]] && [[ -f "$FILE_PATH.bak" ]]; then
    rm "$FILE_PATH.bak"
fi

exit 0
