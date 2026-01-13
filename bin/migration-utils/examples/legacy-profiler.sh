#!/bin/bash
#
# legacy-profiler.sh - Example legacy script using bq CLI
#
# This script demonstrates typical patterns that should be migrated
# to DecentClaude utilities
#

set -e

TABLE_ID="$1"

if [[ -z "$TABLE_ID" ]]; then
  echo "Usage: $0 <table_id>"
  exit 1
fi

echo "Profiling table: $TABLE_ID"

# Get basic table info
echo "Getting table metadata..."
bq show --format=prettyjson "$TABLE_ID" > table_info.json

# Extract row count
ROW_COUNT=$(cat table_info.json | jq -r '.numRows')
echo "Row count: $ROW_COUNT"

# Extract size
SIZE_BYTES=$(cat table_info.json | jq -r '.numBytes')
SIZE_GB=$(echo "scale=2; $SIZE_BYTES / 1024 / 1024 / 1024" | bc)
echo "Size: ${SIZE_GB} GB"

# Get schema
echo "Getting schema..."
bq show --schema --format=prettyjson "$TABLE_ID" > schema.json
COLUMN_COUNT=$(cat schema.json | jq '. | length')
echo "Columns: $COLUMN_COUNT"

# Check for nulls in each column (very slow!)
echo "Checking for null values..."
for column in $(cat schema.json | jq -r '.[].name'); do
  NULL_COUNT=$(bq query --format=csv --use_legacy_sql=false "
    SELECT COUNTIF($column IS NULL) as null_count
    FROM \`$TABLE_ID\`
  " | tail -1)

  if [[ $NULL_COUNT -gt 0 ]]; then
    echo "  $column: $NULL_COUNT nulls"
  fi
done

# Check for duplicates on first column (assuming it's an ID)
FIRST_COLUMN=$(cat schema.json | jq -r '.[0].name')
echo "Checking for duplicates on $FIRST_COLUMN..."
DUPLICATE_COUNT=$(bq query --format=csv --use_legacy_sql=false "
  SELECT COUNT(*) as dup_count
  FROM (
    SELECT $FIRST_COLUMN, COUNT(*) as cnt
    FROM \`$TABLE_ID\`
    GROUP BY $FIRST_COLUMN
    HAVING cnt > 1
  )
" | tail -1)

echo "Duplicate $FIRST_COLUMN: $DUPLICATE_COUNT"

# Calculate cost of a typical query
echo "Estimating query cost..."
QUERY="SELECT * FROM \`$TABLE_ID\` WHERE DATE(created_at) >= CURRENT_DATE() - 30"
bq query --dry_run --format=json "$QUERY" > dry_run.json
BYTES_PROCESSED=$(cat dry_run.json | jq -r '.totalBytesProcessed | tonumber')
COST=$(echo "scale=4; $BYTES_PROCESSED / 1099511627776 * 5" | bc)
echo "Typical query cost: \$${COST}"

echo "Profiling complete!"

# Cleanup temp files
rm -f table_info.json schema.json dry_run.json
