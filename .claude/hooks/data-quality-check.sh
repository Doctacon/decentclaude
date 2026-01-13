#!/bin/bash
# Data Quality Check Hook
# Runs custom data quality checks using the Python framework
set -e

echo "================================"
echo "Running data quality checks..."
echo "================================"

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
  echo "Warning: python3 is not installed. Cannot run data quality checks." >&2
  exit 0
fi

# Check if the data quality script exists
if [ ! -f "scripts/data_quality.py" ]; then
  echo "Warning: scripts/data_quality.py not found. Skipping data quality checks." >&2
  exit 0
fi

# Run the data quality checks
if python3 scripts/data_quality.py; then
  echo "✓ Data quality checks passed"
  exit 0
else
  echo "✗ Data quality checks failed" >&2
  echo "Fix quality issues before proceeding" >&2
  exit 1
fi
