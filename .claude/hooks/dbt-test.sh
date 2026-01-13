#!/bin/bash
# dbt Test Hook
# Runs dbt tests to validate data quality and model integrity
set -e

echo "================================"
echo "Running dbt tests..."
echo "================================"

# Check if dbt is installed
if ! command -v dbt &> /dev/null; then
  echo "Warning: dbt is not installed. Install with: pip install dbt-core dbt-bigquery" >&2
  exit 0
fi

# Check if this is a dbt project
if [ ! -f "dbt_project.yml" ]; then
  echo "No dbt_project.yml found. Skipping dbt tests." >&2
  exit 0
fi

# Set PYTHONPATH for sqlmesh compatibility if needed
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}./"

# Run dbt tests
if dbt test --profiles-dir ~/.dbt 2>&1; then
  echo "✓ dbt tests passed"
  exit 0
else
  echo "✗ dbt tests failed" >&2
  echo "Fix test failures before proceeding" >&2
  exit 1
fi
