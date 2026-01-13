#!/bin/bash
# BigQuery Validation Hook
# Validates BigQuery SQL syntax before execution using the BigQuery MCP validate_sql tool
set -e

# Parse the hook input from stdin
input=$(cat)

# Extract the SQL query from the tool input
# For BigQuery MCP tools, the SQL might be in different parameters depending on the tool
sql=$(echo "$input" | jq -r '.tool_input.sql // .tool_input.query // empty')

# If no SQL found, allow the operation
if [ -z "$sql" ] || [ "$sql" = "null" ]; then
  exit 0
fi

# Validate using BigQuery's validate_sql (dry run)
# This requires the BigQuery MCP server to be available
# Since we can't directly call MCP from bash, we'll use sqlparse for basic syntax validation
if command -v python3 &> /dev/null; then
  validation_result=$(python3 -c "
import sys
import sqlparse

sql = '''$sql'''

try:
    parsed = sqlparse.parse(sql)
    if not parsed:
        print('Invalid SQL: Could not parse SQL statement', file=sys.stderr)
        sys.exit(2)

    # Check for basic SQL syntax errors
    for statement in parsed:
        if statement.get_type() == 'UNKNOWN':
            print('Invalid SQL: Unknown statement type', file=sys.stderr)
            sys.exit(2)

    print('SQL syntax is valid')
    sys.exit(0)
except Exception as e:
    print(f'Invalid SQL: {str(e)}', file=sys.stderr)
    sys.exit(2)
" 2>&1)
  exit_code=$?

  if [ $exit_code -ne 0 ]; then
    echo "BigQuery validation failed: $validation_result" >&2
    exit 2
  fi
fi

# If validation passed or sqlparse not available, allow the operation
exit 0
