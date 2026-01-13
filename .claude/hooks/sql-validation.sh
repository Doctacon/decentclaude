#!/bin/bash
# SQL File Validation Hook
# Validates SQL files before they are written to disk
set -e

# Parse the hook input from stdin
input=$(cat)

# Extract the file path from the tool input
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')

# If no file path or not a SQL file, allow the operation
if [ -z "$file_path" ] || [ "$file_path" = "null" ]; then
  exit 0
fi

# Only validate SQL files
if [[ ! "$file_path" =~ \.(sql|SQL)$ ]]; then
  exit 0
fi

# Wait a moment for the file to be written
sleep 0.1

# Check if file exists (it should have just been written)
if [ ! -f "$file_path" ]; then
  exit 0
fi

# Validate SQL syntax using sqlparse
if command -v python3 &> /dev/null; then
  validation_result=$(python3 -c "
import sys
import sqlparse

try:
    with open('$file_path', 'r') as f:
        content = f.read()

    if not content.strip():
        # Empty file is okay
        sys.exit(0)

    parsed = sqlparse.parse(content)
    if not parsed:
        print('Invalid SQL: Could not parse SQL file', file=sys.stderr)
        sys.exit(2)

    # Check for basic SQL syntax errors
    for statement in parsed:
        if statement.get_type() == 'UNKNOWN':
            print('Invalid SQL: Unknown statement type', file=sys.stderr)
            sys.exit(2)

    print('SQL file syntax is valid')
    sys.exit(0)
except Exception as e:
    print(f'Invalid SQL: {str(e)}', file=sys.stderr)
    sys.exit(2)
" 2>&1)
  exit_code=$?

  if [ $exit_code -ne 0 ]; then
    echo "SQL validation failed for $file_path: $validation_result" >&2
    exit 2
  fi
fi

# Check for hardcoded secrets
if grep -iE "(password|api_key|secret|token|credentials)\s*=\s*['\"]" "$file_path" &> /dev/null; then
  echo "Warning: Potential hardcoded secrets detected in $file_path" >&2
  echo "Please review the file before committing" >&2
  # Don't block, just warn
fi

exit 0
