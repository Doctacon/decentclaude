# Batch Utils Practical Examples

Complete working examples for common scenarios.

## Table of Contents

1. [Data Quality Monitoring](#data-quality-monitoring)
2. [Staging to Production Validation](#staging-to-production-validation)
3. [Cost Optimization Initiative](#cost-optimization-initiative)
4. [Migration Validation](#migration-validation)
5. [Daily Health Checks](#daily-health-checks)
6. [Schema Change Detection](#schema-change-detection)

## Data Quality Monitoring

### Setup

Create a list of tables to monitor:

**monitored_tables.csv**
```csv
table_id,name
project.analytics.fact_sales,Sales Facts
project.analytics.fact_orders,Order Facts
project.analytics.dim_customers,Customer Dimension
project.analytics.dim_products,Product Dimension
```

### Daily Quality Report

```bash
#!/bin/bash
# daily_quality_check.sh

DATE=$(date +%Y%m%d)
REPORT_DIR="reports"
LOG_DIR="logs"

mkdir -p "$REPORT_DIR" "$LOG_DIR"

echo "Running daily quality check for $DATE..."

# Profile all monitored tables with anomaly detection
batch-profile \
  --file=monitored_tables.csv \
  --detect-anomalies \
  --compare \
  --top=15 \
  --parallel=6 \
  --progress \
  --format=html \
  --output="${REPORT_DIR}/quality_${DATE}.html" \
  --log="${LOG_DIR}/quality_${DATE}.log"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "Quality check completed successfully"

  # Optional: Send email notification
  # mail -s "Daily Quality Report - $DATE" \
  #   -a "${REPORT_DIR}/quality_${DATE}.html" \
  #   team@example.com < /dev/null
else
  echo "Quality check failed with exit code $EXIT_CODE"
  echo "Check log: ${LOG_DIR}/quality_${DATE}.log"
fi

exit $EXIT_CODE
```

### Weekly Trend Analysis

```bash
#!/bin/bash
# weekly_quality_trend.sh

WEEK=$(date +%Y_week_%V)

# Profile with JSON output for trend analysis
batch-profile \
  --file=monitored_tables.csv \
  --compare \
  --format=json \
  --output="data/quality_${WEEK}.json" \
  --quiet

# Extract key metrics for trending
python3 << 'EOF'
import json
import sys

with open(f"data/quality_{sys.argv[1]}.json") as f:
    data = json.load(f)

analysis = data.get('comparative_analysis', {})
print(f"Week: {sys.argv[1]}")
print(f"Total Tables: {analysis.get('total_tables', 0)}")
print(f"Total Rows: {analysis.get('total_rows', 0):,}")
print(f"Total Size: {analysis.get('total_size_gb', 0):.2f} GB")
print(f"Partitioned: {analysis.get('partition_info', {}).get('partitioned', 0)}")
EOF
```

## Staging to Production Validation

### Setup

Create staging-to-production table pairs:

**staging_prod_pairs.txt**
```
project.staging.users:project.prod.users
project.staging.orders:project.prod.orders
project.staging.products:project.prod.products
project.staging.transactions:project.prod.transactions
```

### Pre-Deployment Validation

```bash
#!/bin/bash
# pre_deployment_validation.sh

set -e  # Exit on any error

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
VALIDATION_DIR="validation_${TIMESTAMP}"

mkdir -p "$VALIDATION_DIR"

echo "Starting pre-deployment validation..."

# Step 1: Compare all staging/prod pairs
echo "Step 1: Comparing staging to production tables..."
batch-compare \
  --file=staging_prod_pairs.txt \
  --critical-only \
  --threshold=5 \
  --parallel=8 \
  --progress \
  --format=json \
  --output="${VALIDATION_DIR}/comparison.json" \
  --log="${VALIDATION_DIR}/comparison.log"

# Step 2: Check for critical differences
echo "Step 2: Checking for critical differences..."
CRITICAL_COUNT=$(jq -r '.aggregate_analysis.critical_differences' "${VALIDATION_DIR}/comparison.json")

if [ "$CRITICAL_COUNT" -gt 0 ]; then
  echo "FAILED: Found $CRITICAL_COUNT critical differences!"

  # Generate detailed HTML report
  batch-compare \
    --file=staging_prod_pairs.txt \
    --critical-only \
    --format=html \
    --output="${VALIDATION_DIR}/critical_differences.html"

  echo "Review report: ${VALIDATION_DIR}/critical_differences.html"
  exit 1
fi

# Step 3: Profile staging tables
echo "Step 3: Profiling staging tables..."
grep -o '^[^:]*' staging_prod_pairs.txt | \
  batch-profile \
    --stdin \
    --compare \
    --format=markdown \
    --output="${VALIDATION_DIR}/staging_profile.md" \
    --quiet

echo "SUCCESS: All validation checks passed!"
echo "Reports saved to: $VALIDATION_DIR"
```

### Post-Deployment Verification

```bash
#!/bin/bash
# post_deployment_verification.sh

DEPLOYMENT_ID="${1:-$(date +%Y%m%d_%H%M%S)}"
REPORT_DIR="deployment_reports/$DEPLOYMENT_ID"

mkdir -p "$REPORT_DIR"

echo "Verifying deployment: $DEPLOYMENT_ID"

# Compare again to verify data was promoted correctly
batch-compare \
  --file=staging_prod_pairs.txt \
  --sample-size=1000 \
  --threshold=1 \
  --continue-on-error \
  --format=html \
  --output="${REPORT_DIR}/verification.html" \
  --log="${REPORT_DIR}/verification.log"

# Profile production tables post-deployment
grep -o ':.*' staging_prod_pairs.txt | sed 's/://' | \
  batch-profile \
    --stdin \
    --detect-anomalies \
    --format=json \
    --output="${REPORT_DIR}/prod_profile.json"

echo "Verification complete. Reports: $REPORT_DIR"
```

## Cost Optimization Initiative

### Setup

Organize queries by category:

```bash
# Find all production queries
find sql/production/ -name "*.sql" > production_queries.txt

# Find high-cost queries (if you have historical data)
# This example assumes you have a list
cat > high_cost_queries.txt << 'EOF'
sql/production/daily_sales_rollup.sql
sql/production/customer_lifetime_value.sql
sql/production/inventory_forecast.sql
EOF
```

### Weekly Cost Analysis

```bash
#!/bin/bash
# weekly_cost_analysis.sh

WEEK=$(date +%Y_week_%V)
REPORT_DIR="cost_reports"

mkdir -p "$REPORT_DIR"

echo "Running weekly cost analysis for $WEEK..."

# Analyze all production queries
batch-optimize \
  --dir=sql/production/ \
  --prioritize \
  --top=20 \
  --parallel=8 \
  --progress \
  --format=html \
  --output="${REPORT_DIR}/optimizations_${WEEK}.html" \
  --log="${REPORT_DIR}/optimizations_${WEEK}.log"

# Generate JSON for further analysis
batch-optimize \
  --dir=sql/production/ \
  --prioritize \
  --min-cost=10 \
  --format=json \
  --output="${REPORT_DIR}/optimizations_${WEEK}.json" \
  --quiet

# Extract top opportunities
python3 << EOF
import json

with open("${REPORT_DIR}/optimizations_${WEEK}.json") as f:
    data = json.load(f)

analysis = data.get('aggregate_analysis', {})
print(f"\n=== Cost Optimization Opportunities for $WEEK ===")
print(f"Total queries analyzed: {analysis.get('total_queries', 0)}")
print(f"Total GB processed: {analysis.get('total_gb_processed', 0):.2f}")
print(f"Total recommendations: {analysis.get('total_recommendations', 0)}")

print("\nTop 5 queries by cost:")
for i, query in enumerate(analysis.get('top_queries_by_cost', [])[:5], 1):
    gb = query.get('estimated_cost', {}).get('gb_processed', 0)
    print(f"{i}. {query.get('_query_name')}: {gb:.2f} GB")

print("\nTop 5 optimization opportunities:")
for i, query in enumerate(analysis.get('top_queries_by_optimization', [])[:5], 1):
    score = query.get('_optimization_score', 0)
    recs = len(query.get('recommendations', []))
    print(f"{i}. {query.get('_query_name')}: score {score:.1f} ({recs} recs)")
EOF
```

### Targeted Optimization Sprint

```bash
#!/bin/bash
# optimization_sprint.sh

SPRINT="sprint_$(date +%Y%m%d)"
mkdir -p "$SPRINT"

echo "Starting optimization sprint: $SPRINT"

# Focus on queries processing > 50 GB
batch-optimize \
  --dir=sql/production/ \
  --min-cost=50 \
  --prioritize \
  --format=markdown \
  --output="${SPRINT}/high_cost_queries.md"

# Also check largest tables
batch-profile \
  --dataset=project.warehouse \
  --compare \
  --top=10 \
  --quiet \
  --format=json \
  --output="${SPRINT}/largest_tables.json"

# Generate combined report
cat > "${SPRINT}/sprint_summary.md" << EOF
# Optimization Sprint Summary
Date: $(date +%Y-%m-%d)

## High-Cost Queries
See [high_cost_queries.md](high_cost_queries.md)

## Largest Tables
See [largest_tables.json](largest_tables.json)

## Next Steps
1. Review high-cost query recommendations
2. Implement partitioning on largest tables
3. Add clustering where appropriate
4. Re-run analysis next week to measure impact
EOF

echo "Sprint materials ready in: $SPRINT/"
```

## Migration Validation

### Setup

**migration_config.json**
```json
{
  "old_tables": [
    "project.old_system.users",
    "project.old_system.orders"
  ],
  "new_tables": [
    "project.new_system.users",
    "project.new_system.orders"
  ],
  "table_pairs": [
    {
      "table_a": "project.old_system.users",
      "table_b": "project.new_system.users",
      "name": "Users Migration"
    },
    {
      "table_a": "project.old_system.orders",
      "table_b": "project.new_system.orders",
      "name": "Orders Migration"
    }
  ]
}
```

### Pre-Migration Baseline

```bash
#!/bin/bash
# pre_migration_baseline.sh

MIGRATION_ID="${1:-migration_$(date +%Y%m%d)}"
BASELINE_DIR="migrations/${MIGRATION_ID}/baseline"

mkdir -p "$BASELINE_DIR"

echo "Creating baseline for migration: $MIGRATION_ID"

# Profile old system tables
jq -r '.old_tables[]' migration_config.json | \
  batch-profile \
    --stdin \
    --detect-anomalies \
    --format=json \
    --output="${BASELINE_DIR}/old_system_profile.json" \
    --log="${BASELINE_DIR}/old_system.log"

echo "Baseline created: $BASELINE_DIR"
```

### Post-Migration Validation

```bash
#!/bin/bash
# post_migration_validation.sh

MIGRATION_ID="${1:-migration_$(date +%Y%m%d)}"
VALIDATION_DIR="migrations/${MIGRATION_ID}/validation"

mkdir -p "$VALIDATION_DIR"

echo "Validating migration: $MIGRATION_ID"

# Create pairs file from config
jq -r '.table_pairs[] | "\(.table_a):\(.table_b)"' migration_config.json > "${VALIDATION_DIR}/pairs.txt"

# Compare old vs new
batch-compare \
  --file="${VALIDATION_DIR}/pairs.txt" \
  --sample-size=1000 \
  --continue-on-error \
  --progress \
  --format=html \
  --output="${VALIDATION_DIR}/comparison.html" \
  --log="${VALIDATION_DIR}/comparison.log"

# Profile new system
jq -r '.new_tables[]' migration_config.json | \
  batch-profile \
    --stdin \
    --detect-anomalies \
    --format=json \
    --output="${VALIDATION_DIR}/new_system_profile.json"

# Compare profiles
python3 << 'EOF'
import json
import sys

baseline_file = f"migrations/{sys.argv[1]}/baseline/old_system_profile.json"
validation_file = f"migrations/{sys.argv[1]}/validation/new_system_profile.json"

with open(baseline_file) as f:
    baseline = json.load(f)
with open(validation_file) as f:
    validation = json.load(f)

print("\n=== Migration Validation Summary ===")
print(f"Old system tables: {len(baseline.get('profiles', []))}")
print(f"New system tables: {len(validation.get('profiles', []))}")

old_rows = baseline.get('metadata', {}).get('total_rows', 0)
new_rows = validation.get('metadata', {}).get('total_rows', 0)

print(f"Old system rows: {old_rows:,}")
print(f"New system rows: {new_rows:,}")
print(f"Row difference: {new_rows - old_rows:,} ({(new_rows - old_rows) / old_rows * 100:.2f}%)")
EOF "$MIGRATION_ID"

echo "Validation complete: $VALIDATION_DIR"
```

## Daily Health Checks

### Comprehensive Health Check Script

```bash
#!/bin/bash
# daily_health_check.sh

DATE=$(date +%Y%m%d)
HEALTH_DIR="health_checks/$DATE"

mkdir -p "$HEALTH_DIR"

echo "Running daily health check for $DATE..."

# 1. Profile critical tables
echo "Checking critical tables..."
batch-profile \
  --file=config/critical_tables.csv \
  --compare \
  --detect-anomalies \
  --parallel=6 \
  --format=html \
  --output="${HEALTH_DIR}/critical_tables.html" \
  --log="${HEALTH_DIR}/critical_tables.log"

# 2. Compare staging vs production
echo "Comparing staging to production..."
batch-compare \
  --file=config/staging_prod_pairs.txt \
  --critical-only \
  --threshold=10 \
  --format=json \
  --output="${HEALTH_DIR}/env_comparison.json" \
  --quiet

# 3. Check for degraded queries
echo "Checking query performance..."
batch-optimize \
  --file=config/monitored_queries.txt \
  --min-cost=5 \
  --format=json \
  --output="${HEALTH_DIR}/query_health.json" \
  --quiet

# 4. Generate summary
python3 << EOF
import json
from datetime import datetime

with open("${HEALTH_DIR}/critical_tables.html") as f:
    tables_ok = True  # Simple check - file exists

with open("${HEALTH_DIR}/env_comparison.json") as f:
    comparison = json.load(f)
    critical_diffs = comparison.get('aggregate_analysis', {}).get('critical_differences', 0)

with open("${HEALTH_DIR}/query_health.json") as f:
    queries = json.load(f)
    critical_recs = queries.get('aggregate_analysis', {}).get('severity_breakdown', {}).get('critical', 0)

print(f"\n=== Daily Health Check Summary - $DATE ===")
print(f"Critical table profiles: OK")
print(f"Critical environment differences: {critical_diffs}")
print(f"Critical query issues: {critical_recs}")

health_ok = critical_diffs == 0 and critical_recs == 0

if health_ok:
    print("\nStatus: HEALTHY ✓")
    exit(0)
else:
    print("\nStatus: NEEDS ATTENTION ⚠")
    print(f"Review reports in: ${HEALTH_DIR}")
    exit(1)
EOF
```

## Schema Change Detection

### Track Schema Changes Over Time

```bash
#!/bin/bash
# schema_change_detection.sh

BASELINE_FILE="schema_baselines.json"
CURRENT_DATE=$(date +%Y%m%d)

# Profile current state
batch-profile \
  --file=config/tracked_tables.csv \
  --format=json \
  --output="current_schema_${CURRENT_DATE}.json" \
  --quiet

# Compare with baseline if it exists
if [ -f "$BASELINE_FILE" ]; then
  echo "Comparing with baseline..."

  # Extract and compare schemas
  python3 << 'EOF'
import json
import sys

with open(sys.argv[1]) as f:
    baseline = json.load(f)
with open(sys.argv[2]) as f:
    current = json.load(f)

changes = []

for curr_table in current.get('profiles', []):
    table_id = curr_table.get('metadata', {}).get('table_id')
    curr_schema = {col['name']: col['type']
                   for col in curr_table.get('columns', [])}

    # Find in baseline
    base_table = next((t for t in baseline.get('profiles', [])
                      if t.get('metadata', {}).get('table_id') == table_id), None)

    if base_table:
        base_schema = {col['name']: col['type']
                      for col in base_table.get('columns', [])}

        # Detect changes
        added = set(curr_schema.keys()) - set(base_schema.keys())
        removed = set(base_schema.keys()) - set(curr_schema.keys())
        changed = {k for k in curr_schema.keys() & base_schema.keys()
                  if curr_schema[k] != base_schema[k]}

        if added or removed or changed:
            changes.append({
                'table': table_id,
                'added_columns': list(added),
                'removed_columns': list(removed),
                'changed_columns': list(changed)
            })

if changes:
    print(f"\n=== Schema Changes Detected ===")
    for change in changes:
        print(f"\nTable: {change['table']}")
        if change['added_columns']:
            print(f"  Added: {', '.join(change['added_columns'])}")
        if change['removed_columns']:
            print(f"  Removed: {', '.join(change['removed_columns'])}")
        if change['changed_columns']:
            print(f"  Changed: {', '.join(change['changed_columns'])}")
else:
    print("No schema changes detected")
EOF "$BASELINE_FILE" "current_schema_${CURRENT_DATE}.json"
else
  echo "Creating new baseline..."
  cp "current_schema_${CURRENT_DATE}.json" "$BASELINE_FILE"
fi
```

## Tips for Production Use

1. **Set up cron jobs** for regular health checks:
   ```cron
   0 6 * * * /path/to/daily_health_check.sh
   0 8 * * 1 /path/to/weekly_cost_analysis.sh
   ```

2. **Use exit codes** for CI/CD integration:
   - Exit 0 = success
   - Exit 1 = validation failed

3. **Archive reports** for historical analysis:
   ```bash
   # Keep last 30 days
   find reports/ -name "*.html" -mtime +30 -delete
   ```

4. **Send notifications** on failures:
   ```bash
   if [ $? -ne 0 ]; then
     echo "Health check failed!" | mail -s "ALERT: Health Check" team@example.com
   fi
   ```

5. **Version control** your configuration files:
   ```bash
   git add config/*.csv config/*.txt
   git commit -m "Update monitored tables"
   ```

For more examples and documentation, see README.md and QUICKSTART.md.
