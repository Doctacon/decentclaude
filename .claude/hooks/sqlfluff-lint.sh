#!/bin/bash
# SQLFluff Lint Hook
# Lints SQL files to enforce style guidelines and best practices
set -e

echo "================================"
echo "Running SQLFluff lint..."
echo "================================"

# Check if sqlfluff is installed
if ! command -v sqlfluff &> /dev/null; then
  echo "Warning: sqlfluff is not installed. Install with: pip install sqlfluff" >&2
  exit 0
fi

# Find SQL files to lint
sql_files=$(find . -type f -name "*.sql" ! -path "*/target/*" ! -path "*/.git/*" ! -path "*/venv/*" 2>/dev/null || true)

if [ -z "$sql_files" ]; then
  echo "No SQL files found to lint"
  exit 0
fi

# Count files
file_count=$(echo "$sql_files" | wc -l | tr -d ' ')
echo "Linting $file_count SQL file(s)..."

# Run sqlfluff lint with BigQuery dialect
if echo "$sql_files" | xargs sqlfluff lint --dialect bigquery 2>&1; then
  echo "✓ SQLFluff lint passed"
  exit 0
else
  echo "✗ SQLFluff lint failed" >&2
  echo "Fix linting issues or run 'sqlfluff fix' to auto-fix" >&2
  exit 1
fi
