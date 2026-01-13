#!/bin/bash
# dbt Compile Hook
# Compiles dbt models to validate SQL and Jinja templating
set -e

echo "================================"
echo "Running dbt compile..."
echo "================================"

# Check if dbt is installed
if ! command -v dbt &> /dev/null; then
  echo "Warning: dbt is not installed. Install with: pip install dbt-core dbt-bigquery" >&2
  exit 0
fi

# Check if this is a dbt project
if [ ! -f "dbt_project.yml" ]; then
  echo "No dbt_project.yml found. Skipping dbt compile." >&2
  exit 0
fi

# Set PYTHONPATH for sqlmesh compatibility if needed
export PYTHONPATH="${PYTHONPATH:+$PYTHONPATH:}./"

# Compile dbt models
if dbt compile --profiles-dir ~/.dbt 2>&1; then
  echo "✓ dbt compile succeeded"
  exit 0
else
  echo "✗ dbt compile failed" >&2
  echo "Fix compilation errors before proceeding" >&2
  exit 1
fi
