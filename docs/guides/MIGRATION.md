# Migration Guide: Legacy Tools to DecentClaude Utilities

## Table of Contents

1. [Overview](#overview)
2. [Migration Benefits](#migration-benefits)
3. [Migration from bq CLI](#migration-from-bq-cli)
4. [Migration from Custom Python Scripts](#migration-from-custom-python-scripts)
5. [Migration from BigQuery Console](#migration-from-bigquery-console)
6. [Migration from Legacy Data Quality Tools](#migration-from-legacy-data-quality-tools)
7. [Migration Utilities](#migration-utilities)
8. [Migration Strategy](#migration-strategy)
9. [Migration Checklist](#migration-checklist)
10. [Common Pitfalls](#common-pitfalls)
11. [Validation and Testing](#validation-and-testing)
12. [Rollback Plan](#rollback-plan)

---

## Overview

This guide provides a comprehensive roadmap for migrating from legacy BigQuery tools to the DecentClaude utilities ecosystem. The migration is designed to be incremental, allowing teams to adopt utilities at their own pace while maintaining existing workflows.

### What Gets Migrated

- **bq CLI commands** → DecentClaude BigQuery utilities
- **Custom Python scripts** → Standardized utilities with error handling
- **Manual console operations** → Automated, observable workflows
- **Ad-hoc data quality checks** → Comprehensive profiling framework
- **Custom cost tracking** → Unified observability platform

### Timeline Overview

- **Phase 1 (Weeks 1-2)**: Read-only operations and profiling
- **Phase 2 (Weeks 3-4)**: Quality checks and monitoring
- **Phase 3 (Weeks 5-6)**: Full CI/CD integration
- **Phase 4 (Weeks 7-8)**: Decommission legacy tools

---

## Migration Benefits

### Cost Savings

**Before Migration**:
- No query cost estimation → accidental full table scans
- Manual partition detection → inefficient queries
- No caching → repeated metadata API calls
- Example: 10TB/month in unnecessary scans = $50/month wasted

**After Migration**:
- Automatic cost estimation with `bq-query-cost`
- Partition-aware query optimization with `bq-optimize`
- Intelligent metadata caching reduces API costs by 80%
- Estimated savings: $100-500/month for medium-sized teams

### Consistency

**Before Migration**:
- Each team member has different scripts
- Inconsistent error handling across tools
- No standardized output formats
- Knowledge scattered across wikis and Slack

**After Migration**:
- Single source of truth for all operations
- Consistent error messages and logging
- Standardized JSON/Markdown/HTML outputs
- Centralized documentation and knowledge base

### Observability

**Before Migration**:
- No visibility into query patterns
- Manual cost tracking in spreadsheets
- Reactive incident response
- No audit trail for data operations

**After Migration**:
- Automated cost reporting with trends
- Query performance baselines and anomaly detection
- Proactive alerting on cost/performance issues
- Complete audit trail of all operations

### Developer Experience

**Before Migration**:
- Context switching between CLI, console, and scripts
- Slow feedback loops (run query, check console, adjust)
- Manual documentation of schemas and lineage
- Difficult to share knowledge

**After Migration**:
- Everything accessible via CLI with aliases
- Instant feedback with dry-run and explain features
- Auto-generated documentation and diagrams
- Knowledge base integrated into workflow

---

## Migration from bq CLI

### Overview

The `bq` CLI is powerful but lacks features for modern data engineering workflows. DecentClaude utilities extend and enhance `bq` functionality.

### Command Mapping

| Legacy bq Command | DecentClaude Utility | Improvements |
|-------------------|---------------------|--------------|
| `bq query` | `bq-explain` + `bq-optimize` | Cost estimation, execution plan, optimization suggestions |
| `bq show` | `bq-profile` | Comprehensive stats, anomaly detection, quality metrics |
| `bq ls` | `bq-explore` | Interactive TUI, filtering, search |
| `bq mk --schema` | `ai-generate --type schema` | AI-powered schema design |
| Manual schema comparison | `bq-schema-diff` | Side-by-side diff, type compatibility |
| Manual lineage tracking | `bq-lineage` | Automated dependency graph |
| Manual partition checks | `bq-partition-info` | Detailed partition analysis |

### Example Migrations

#### Example 1: Query Analysis

**Before (bq CLI)**:
```bash
# Run query blindly
bq query --use_legacy_sql=false "
SELECT
  user_id,
  COUNT(*) as order_count,
  SUM(amount) as total_amount
FROM \`project.dataset.orders\`
WHERE date >= '2024-01-01'
GROUP BY user_id
"

# Check job in console to see cost (too late!)
# Manually look at execution plan (if you remember)
```

**After (DecentClaude)**:
```bash
# First, estimate cost (no execution)
bq-query-cost --query "SELECT user_id, COUNT(*) as order_count, SUM(amount) as total_amount FROM \`project.dataset.orders\` WHERE date >= '2024-01-01' GROUP BY user_id"

# Output:
# Estimated bytes processed: 2.3 GB
# Estimated cost: $0.012
# Partitions scanned: 13 out of 365
# Recommendation: Query is well-optimized

# Explain execution plan
bq-explain --dry-run --query "SELECT ..."

# Output:
# Stage 1: Read (1.2s, 2.3GB)
#   └─ Table: project.dataset.orders
#      Partitions: 13 (3.6% of table)
# Stage 2: Aggregate (0.3s)
#   └─ Group by: user_id
#
# Performance: ✓ Good
# Cost efficiency: ✓ Excellent

# Get optimization suggestions
bq-optimize --query "SELECT ..."

# Output:
# ✓ Query is using partition filter
# ✓ Appropriate aggregation
# → Consider: Adding clustering on user_id for better performance
```

**Migration Steps**:
1. Identify all scripts using `bq query`
2. Wrap with cost estimation (`bq-query-cost`) in CI/CD
3. Add explain step for complex queries
4. Set up cost alerts for queries over threshold
5. Gradually replace manual optimization with `bq-optimize`

**Validation**:
```bash
# Test that both approaches return same results
bq query --format=csv "SELECT ..." > legacy.csv
bq-explain --dry-run "SELECT ..." && bq query --format=csv "SELECT ..." > new.csv
diff legacy.csv new.csv
```

#### Example 2: Table Profiling

**Before (bq CLI)**:
```bash
# Get basic table info
bq show --format=prettyjson project:dataset.customers

# Manually run queries to understand data
bq query "SELECT COUNT(*) FROM project.dataset.customers"
bq query "SELECT COUNT(DISTINCT user_id) FROM project.dataset.customers"
bq query "SELECT MIN(created_at), MAX(created_at) FROM project.dataset.customers"

# Check for nulls
bq query "SELECT
  COUNTIF(email IS NULL) as null_emails,
  COUNTIF(phone IS NULL) as null_phones
FROM project.dataset.customers"

# Takes 10+ minutes and multiple queries
```

**After (DecentClaude)**:
```bash
# One command, comprehensive profile
bq-profile project.dataset.customers

# Output in 30 seconds:
#
# Table: project.dataset.customers
# Rows: 1,234,567
# Size: 45.2 GB
# Last Modified: 2024-01-13 10:30:00 UTC
#
# Schema (5 columns):
#   user_id (STRING): 1,234,567 distinct (100.0% unique) ✓ Primary key candidate
#   email (STRING): 1,234,320 distinct (99.98% unique), 247 nulls (0.02%)
#   phone (STRING): 892,341 distinct (72.3% unique), 342,226 nulls (27.7%)
#   created_at (TIMESTAMP): Range: 2020-01-01 to 2024-01-13
#   status (STRING): 3 distinct values [active: 98.2%, inactive: 1.5%, pending: 0.3%]
#
# Data Quality:
#   ✓ No duplicate user_ids
#   ⚠ High null rate on phone (27.7%)
#   ✓ No future dates in created_at
#   ✓ All statuses are valid
#
# Cost: $0.003 (single query)

# Export to markdown for documentation
bq-profile project.dataset.customers --format=markdown > docs/tables/customers.md
```

**Migration Steps**:
1. Create inventory of tables requiring regular profiling
2. Replace manual profiling scripts with `bq-profile`
3. Set up scheduled profiling for critical tables
4. Integrate profiles into documentation pipeline
5. Archive legacy profiling queries

**Validation**:
```bash
# Compare metrics from legacy vs new
python bin/migration-utils/validate-profile-migration.py \
  --table project.dataset.customers \
  --legacy-script scripts/profile_customers.sql
```

#### Example 3: Schema Management

**Before (bq CLI)**:
```bash
# Compare dev and prod schemas manually
bq show --schema --format=prettyjson project-dev:dataset.table > dev_schema.json
bq show --schema --format=prettyjson project-prod:dataset.table > prod_schema.json

# Manual diff (hard to read)
diff dev_schema.json prod_schema.json

# Output:
# 5c5
# <   "type": "STRING"
# ---
# >   "type": "INTEGER"
#
# What changed? Which field? Hard to tell!
```

**After (DecentClaude)**:
```bash
# Clear, human-readable schema diff
bq-schema-diff project-dev.dataset.table project-prod.dataset.table

# Output:
#
# Schema Differences: project-dev.dataset.table → project-prod.dataset.table
#
# MODIFIED FIELDS:
#   user_id: STRING → INTEGER ⚠️  Type change may break queries
#
# ADDED FIELDS (in prod):
#   ✓ created_by (STRING, nullable)
#   ✓ updated_at (TIMESTAMP, nullable)
#
# REMOVED FIELDS (from dev):
#   ✗ legacy_id (INTEGER)
#
# COMPATIBILITY ASSESSMENT:
#   ⚠️  BREAKING CHANGES DETECTED
#   Action required: Update queries using user_id
#
# Recommendation: Review and update dependent queries before promotion

# Export for code review
bq-schema-diff dev.table prod.table --format=markdown > schema-changes.md
```

**Migration Steps**:
1. Identify all schema comparison scripts
2. Replace with `bq-schema-diff` in deployment pipeline
3. Add breaking change detection to CI/CD
4. Create alerts for unexpected schema changes
5. Document schema evolution process

**Validation**:
```bash
# Verify diff accuracy
python bin/migration-utils/validate-schema-diff.py \
  --table1 project-dev.dataset.table \
  --table2 project-prod.dataset.table
```

#### Example 4: Partition Management

**Before (bq CLI)**:
```bash
# Check if table is partitioned (manual inspection)
bq show --format=prettyjson project:dataset.events | grep -i partition

# Figure out partition column (parsing JSON)
bq show --format=prettyjson project:dataset.events | jq '.timePartitioning'

# Count partitions (complex query)
bq query "SELECT
  COUNT(DISTINCT DATE(event_timestamp)) as partition_count
FROM project.dataset.events"

# Very manual and error-prone
```

**After (DecentClaude)**:
```bash
# Comprehensive partition analysis
bq-partition-info project.dataset.events

# Output:
#
# Partition Information: project.dataset.events
#
# Partitioning: TIME-BASED
#   Column: event_timestamp
#   Granularity: DAY
#   Partition expiration: 90 days
#
# Statistics:
#   Total partitions: 365
#   Oldest partition: 2023-01-13
#   Newest partition: 2024-01-13
#   Avg partition size: 1.2 GB
#   Total size: 438 GB
#
# Partition Health:
#   ✓ No gaps in partitions
#   ✓ Consistent partition sizes
#   ⚠ 23 partitions exceed 2 GB (consider clustering)
#
# Cost Optimization:
#   ✓ Partition filter recommended for all queries
#   → Using full table scan would cost $2.19/query
#   → Using partition filter costs $0.06/query (97% savings)
```

**Migration Steps**:
1. Audit all partitioned tables
2. Replace manual partition checks with `bq-partition-info`
3. Add partition validation to table creation process
4. Set up monitoring for partition health
5. Document partition strategies per table

---

## Migration from Custom Python Scripts

### Overview

Many teams have custom Python scripts using `google-cloud-bigquery`. DecentClaude utilities provide better error handling, caching, and observability.

### Common Script Patterns

#### Pattern 1: Table Metadata Fetching

**Before (Custom Script)**:
```python
#!/usr/bin/env python3
"""
get_table_info.py - Get basic table information
"""
from google.cloud import bigquery

def get_table_info(table_id):
    client = bigquery.Client()

    # No error handling
    table = client.get_table(table_id)

    print(f"Table: {table.table_id}")
    print(f"Rows: {table.num_rows}")
    print(f"Size: {table.num_bytes}")
    print(f"Schema: {len(table.schema)} columns")

    # No caching, repeated API calls
    # No structured output
    # No error recovery

if __name__ == "__main__":
    import sys
    get_table_info(sys.argv[1])
```

**After (DecentClaude)**:
```python
#!/usr/bin/env python3
"""
Use bq-profile instead - it handles:
- Comprehensive metadata with caching
- Proper error handling and recovery
- Multiple output formats
- Data quality metrics
- Anomaly detection
- Null analysis
- Cardinality estimation
"""

# Just use the utility:
# bq-profile project.dataset.table --format=json > table_info.json

# Or import the library for programmatic use:
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from bq_cache import BQMetadataCache
from common_errors import handle_api_error, error_context
from google.cloud import bigquery

def get_table_info_with_cache(table_id):
    """
    Enhanced table info with caching and error handling
    """
    client = bigquery.Client()
    cache = BQMetadataCache()

    try:
        with error_context("fetching table metadata", table_id=table_id):
            # Uses cache to avoid repeated API calls
            metadata = cache.get_cached_table_metadata(client, table_id)
            schema = cache.get_cached_schema(client, table_id)

            return {
                "table_id": table_id,
                "num_rows": metadata.get("num_rows"),
                "num_bytes": metadata.get("num_bytes"),
                "schema": schema,
                "cached": cache.is_cached(table_id)
            }
    except Exception as e:
        handle_api_error(e, context={"table_id": table_id})
        return None

if __name__ == "__main__":
    result = get_table_info_with_cache(sys.argv[1])
    if result:
        print(json.dumps(result, indent=2))
```

**Migration Steps**:
1. **Audit existing scripts**:
   ```bash
   python bin/migration-utils/analyze-legacy-usage.py \
     --scan-dir scripts/ \
     --output legacy-audit.json
   ```

2. **Test replacement**:
   ```bash
   # Compare outputs
   python scripts/get_table_info.py project.dataset.table > old.txt
   bq-profile project.dataset.table > new.txt

   # Validate metrics match
   python bin/migration-utils/validate-migration.py \
     --legacy old.txt \
     --new new.txt
   ```

3. **Update callers**:
   ```bash
   # Find all usages
   grep -r "get_table_info.py" scripts/ jenkins/ airflow/

   # Replace with bq-profile
   # Update CI/CD pipelines
   ```

4. **Archive legacy script**:
   ```bash
   mv scripts/get_table_info.py scripts/legacy/
   echo "Replaced by bq-profile - see docs/guides/MIGRATION.md" > scripts/get_table_info.DEPRECATED
   ```

#### Pattern 2: Query Cost Estimation

**Before (Custom Script)**:
```python
#!/usr/bin/env python3
"""
estimate_cost.py - Estimate query cost
"""
from google.cloud import bigquery

def estimate_cost(query):
    client = bigquery.Client()

    job_config = bigquery.QueryJobConfig(dry_run=True)

    try:
        query_job = client.query(query, job_config=job_config)

        bytes_processed = query_job.total_bytes_processed
        cost_per_tb = 5.00  # Hard-coded, may drift
        cost = (bytes_processed / (1024**4)) * cost_per_tb

        print(f"Bytes: {bytes_processed}")
        print(f"Cost: ${cost:.4f}")

    except Exception as e:
        print(f"Error: {e}")
        # No detailed error handling
        # No retry logic
        # No logging

if __name__ == "__main__":
    import sys
    with open(sys.argv[1]) as f:
        estimate_cost(f.read())
```

**After (DecentClaude)**:
```bash
# Use bq-query-cost with enhanced features
bq-query-cost --file query.sql

# Output:
# Query Cost Estimation
#
# Bytes to process: 2.3 GB (2,468,241,408 bytes)
# Estimated cost: $0.0123
# Cost tier: FREE (under 1 TB/month free tier)
#
# Breakdown:
#   Table reads: 2.1 GB
#     └─ project.dataset.orders (partitioned): 2.1 GB
#        Partitions: 13/365 (3.6%)
#   Intermediate results: 0.2 GB
#
# Optimization opportunities:
#   ✓ Using partition filters
#   → Consider: Add clustering on user_id (could reduce by 30%)
#
# Historical context:
#   Similar queries average: $0.015
#   This query is: 18% below average ✓
```

**Migration Steps**:
1. Replace all `dry_run=True` scripts with `bq-query-cost`
2. Integrate into CI/CD for PR checks
3. Set up cost budgets and alerts
4. Remove custom cost calculation logic

#### Pattern 3: Schema Comparison

**Before (Custom Script)**:
```python
#!/usr/bin/env python3
"""
compare_schemas.py - Compare two table schemas
"""
from google.cloud import bigquery

def compare_schemas(table1_id, table2_id):
    client = bigquery.Client()

    table1 = client.get_table(table1_id)
    table2 = client.get_table(table2_id)

    schema1 = {f.name: f.field_type for f in table1.schema}
    schema2 = {f.name: f.field_type for f in table2.schema}

    # Simple set operations
    only_in_1 = set(schema1.keys()) - set(schema2.keys())
    only_in_2 = set(schema2.keys()) - set(schema1.keys())
    common = set(schema1.keys()) & set(schema2.keys())

    print(f"Only in {table1_id}: {only_in_1}")
    print(f"Only in {table2_id}: {only_in_2}")

    for field in common:
        if schema1[field] != schema2[field]:
            print(f"Type diff in {field}: {schema1[field]} vs {schema2[field]}")

    # Limitations:
    # - No nested field support
    # - No mode (REQUIRED/NULLABLE) comparison
    # - No description comparison
    # - No compatibility analysis
    # - No output formatting options
```

**After (DecentClaude)**:
```bash
# Comprehensive schema comparison
bq-schema-diff project-dev.dataset.table project-prod.dataset.table

# Features:
# - Nested field support
# - Mode and description comparison
# - Type compatibility analysis
# - Breaking change detection
# - Multiple output formats
# - Actionable recommendations
```

**Migration Steps**:
1. Identify all schema comparison scripts
2. Test `bq-schema-diff` against legacy output
3. Update deployment pipelines
4. Add breaking change gates to CI/CD
5. Remove custom comparison logic

### Migration Utility for Python Scripts

Use the automated converter:

```bash
# Analyze legacy script usage patterns
python bin/migration-utils/analyze-legacy-usage.py \
  --scan-dir scripts/ \
  --output-report legacy-usage-report.html

# Convert compatible scripts
python bin/migration-utils/convert-bq-script.py \
  --input scripts/legacy_profiler.py \
  --output scripts/migrated_profiler.sh \
  --suggest-utility
```

---

## Migration from BigQuery Console

### Overview

The BigQuery console is great for ad-hoc exploration but lacks automation and version control. DecentClaude utilities enable console-like workflows from the CLI.

### Common Console Operations

#### Operation 1: Exploring Datasets

**Before (Console)**:
1. Navigate to BigQuery in Cloud Console
2. Expand project in explorer
3. Click through datasets
4. Click on tables to see schemas
5. Click "Preview" to see sample data
6. Manually copy schema to docs
7. No version control or audit trail

**After (DecentClaude)**:
```bash
# Interactive TUI for exploration
bq-explore

# Features:
# - Fuzzy search datasets/tables
# - Live preview of sample data
# - Export schemas to markdown
# - Bookmark frequent tables
# - Command history
# - Export operations to shell script

# Or use individual commands:
bq-profile project.dataset.table --sample-size=20
bq-lineage project.dataset.table --depth=2
```

**Migration Steps**:
1. Train team on `bq-explore` TUI
2. Set up aliases for frequent operations
3. Create runbooks for common exploration patterns
4. Document in knowledge base
5. Track console usage and gradually reduce

#### Operation 2: Query Development

**Before (Console)**:
1. Write query in console editor
2. Click "Run"
3. Wait for results
4. Realize query scans full table
5. Check bytes processed (too late!)
6. Modify query
7. Run again
8. Repeat 10x until optimized
9. Copy final query to git (if you remember)
10. No cost tracking or optimization history

**After (DecentClaude)**:
```bash
# Cost estimation BEFORE running
bq-query-cost --file query.sql

# Explain execution plan
bq-explain --file query.sql --dry-run

# Get optimization suggestions
bq-optimize --file query.sql

# Iterate until satisfied, then run
bq query < query.sql

# All commands are:
# - Version controlled (query.sql in git)
# - Logged for audit
# - Cached for performance
# - Integrated with knowledge base
```

**Migration Steps**:
1. Create templates for common query patterns
2. Set up pre-commit hooks for cost checks
3. Document query development workflow
4. Integrate with code review process
5. Measure console usage reduction

#### Operation 3: Schema Documentation

**Before (Console)**:
1. Click on table
2. Click "Schema" tab
3. Manually copy to Google Doc
4. Manually format as table
5. Manually add descriptions
6. Gets out of date immediately
7. No automation or version control

**After (DecentClaude)**:
```bash
# Auto-generate markdown documentation
bq-profile project.dataset.customers --format=markdown > docs/tables/customers.md

# Output:
# # Table: project.dataset.customers
#
# **Last Updated**: 2024-01-13 10:30:00 UTC
# **Rows**: 1,234,567
# **Size**: 45.2 GB
#
# ## Schema
#
# | Column | Type | Mode | Description |
# |--------|------|------|-------------|
# | user_id | STRING | REQUIRED | Unique user identifier |
# | email | STRING | NULLABLE | User email address |
# | created_at | TIMESTAMP | REQUIRED | Account creation timestamp |
#
# ## Data Quality
#
# - ✓ No duplicate user_ids
# - ✓ Valid email format (99.8%)
# - ✓ No future dates
#
# *Generated automatically by bq-profile*

# Commit to git for version control
git add docs/tables/customers.md
git commit -m "Update customers table documentation"

# Set up scheduled documentation updates
# Add to cron or Airflow
```

**Migration Steps**:
1. Create documentation structure in git
2. Generate initial docs for all tables
3. Set up automated refresh schedule
4. Link from README and wiki
5. Deprecate manual documentation process

---

## Migration from Legacy Data Quality Tools

### Overview

Legacy data quality tools often lack integration with BigQuery's capabilities and modern observability practices.

### Tool Mapping

| Legacy Tool | DecentClaude Utility | Improvements |
|-------------|---------------------|--------------|
| Great Expectations | `bq-profile` + custom checks | Native BigQuery integration, lower cost |
| Custom NULL checks | `bq-profile --format=json` | Automated, comprehensive |
| Manual uniqueness checks | `bq-profile` (uniqueness ratio) | Efficient, cached |
| Airflow data quality DAGs | `bq-profile` + alerting | Faster, integrated observability |
| Manual row count validation | `bq-table-compare` | Comprehensive comparison |

### Example: Data Quality Workflow

**Before (Great Expectations)**:
```python
# great_expectations/checkpoints/customers_checkpoint.py
import great_expectations as gx

context = gx.get_context()

# Load data from BigQuery (slow, downloads to local)
batch = context.get_batch(
    datasource_name="bigquery",
    data_asset_name="customers",
    batch_spec={"table": "project.dataset.customers"}
)

# Run expectations (slow, not BigQuery-native)
results = context.run_checkpoint(
    checkpoint_name="customers_checkpoint",
    batch_request=batch
)

# Limitations:
# - Downloads data locally (slow, expensive)
# - Not using BigQuery's native capabilities
# - Complex configuration
# - Difficult to integrate with existing tools
```

**After (DecentClaude)**:
```bash
# Single command, BigQuery-native, fast
bq-profile project.dataset.customers --format=json > profile.json

# Extract quality metrics
cat profile.json | jq '.quality_checks'

# Output:
# {
#   "duplicate_primary_keys": 0,
#   "null_rates": {
#     "user_id": 0.0,
#     "email": 0.0002,
#     "phone": 0.277
#   },
#   "uniqueness_ratios": {
#     "user_id": 1.0,
#     "email": 0.9998
#   },
#   "future_dates": 0,
#   "invalid_emails": 247
# }

# Set up alerts
cat > quality-check.sh << 'EOF'
#!/bin/bash
PROFILE=$(bq-profile project.dataset.customers --format=json)
NULL_RATE=$(echo $PROFILE | jq '.quality_checks.null_rates.email')

if (( $(echo "$NULL_RATE > 0.01" | bc -l) )); then
  echo "ALERT: Email null rate ${NULL_RATE} exceeds 1% threshold"
  # Send to alerting system
  curl -X POST https://alerts.example.com/webhook \
    -d "table=customers&metric=email_null_rate&value=${NULL_RATE}"
fi
EOF

# Schedule in Airflow/cron
# No complex configuration, pure BigQuery
```

**Migration Steps**:
1. **Audit existing checks**:
   ```bash
   # List all Great Expectations checkpoints
   find . -name "*checkpoint*.py" -o -name "*.yml"

   # Document what each checkpoint validates
   python bin/migration-utils/analyze-legacy-usage.py \
     --type great-expectations \
     --output ge-audit.json
   ```

2. **Map to bq-profile checks**:
   ```bash
   # For each GE checkpoint, identify equivalent bq-profile metric
   # Example mapping:
   # - expect_column_values_to_not_be_null → null_rates
   # - expect_column_values_to_be_unique → uniqueness_ratios
   # - expect_column_values_to_be_between → min/max from profile
   ```

3. **Create validation scripts**:
   ```bash
   # Generate validation script from GE checkpoint
   python bin/migration-utils/convert-ge-checkpoint.py \
     --input great_expectations/checkpoints/customers_checkpoint.py \
     --output bin/data-quality/validate-customers.sh
   ```

4. **Parallel run**:
   ```bash
   # Run both systems in parallel for validation period
   # Compare results
   python bin/migration-utils/compare-quality-results.py \
     --ge-results ge_results.json \
     --bq-profile-results profile.json
   ```

5. **Cutover**:
   ```bash
   # After validation period, switch to bq-profile
   # Update Airflow DAGs
   # Archive Great Expectations configuration
   ```

---

## Migration Utilities

### Overview

DecentClaude provides utilities to automate and validate migrations.

### Utility 1: convert-bq-script.py

Converts legacy bq CLI scripts to DecentClaude utilities.

**Usage**:
```bash
python bin/migration-utils/convert-bq-script.py \
  --input scripts/legacy_query_analyzer.sh \
  --output scripts/migrated_query_analyzer.sh \
  --suggest-utility
```

**Example Conversion**:

*Input (legacy_query_analyzer.sh)*:
```bash
#!/bin/bash
# Analyze query cost and run it

QUERY="SELECT * FROM project.dataset.table WHERE date = '2024-01-01'"

# Get dry run stats
bq query --dry_run --format=json "$QUERY" > dry_run.json

BYTES=$(cat dry_run.json | jq '.totalBytesProcessed | tonumber')
COST=$(echo "scale=4; $BYTES / 1099511627776 * 5" | bc)

echo "Estimated cost: \$${COST}"

if (( $(echo "$COST < 0.10" | bc -l) )); then
  echo "Cost acceptable, running query..."
  bq query --format=csv "$QUERY" > results.csv
else
  echo "Cost too high, aborting"
  exit 1
fi
```

*Output (migrated_query_analyzer.sh)*:
```bash
#!/bin/bash
# Migrated to use DecentClaude utilities
# Original: scripts/legacy_query_analyzer.sh
# Migration date: 2024-01-13

QUERY="SELECT * FROM project.dataset.table WHERE date = '2024-01-01'"

# Cost estimation with enhanced output
COST_OUTPUT=$(bq-query-cost --query "$QUERY" --format=json)
COST=$(echo "$COST_OUTPUT" | jq -r '.estimated_cost')

echo "Cost analysis:"
echo "$COST_OUTPUT" | jq -r '.summary'

# Compare to threshold
if (( $(echo "$COST < 0.10" | bc -l) )); then
  echo "Cost acceptable (${COST}), running query..."

  # Optional: explain execution plan
  bq-explain --query "$QUERY" --dry-run

  # Run query
  bq query --format=csv "$QUERY" > results.csv
else
  echo "Cost too high (${COST}), aborting"
  exit 1
fi

# Log for observability
echo "$COST_OUTPUT" >> logs/query-costs.jsonl
```

**Features**:
- Automatic detection of `bq` commands
- Suggests appropriate DecentClaude utility
- Preserves logic and error handling
- Adds observability hooks
- Documents migration provenance

### Utility 2: analyze-legacy-usage.py

Analyzes existing BigQuery usage patterns to prioritize migration.

**Usage**:
```bash
python bin/migration-utils/analyze-legacy-usage.py \
  --scan-dir scripts/ \
  --scan-dir airflow/dags/ \
  --output-report migration-analysis.html \
  --output-json migration-analysis.json
```

**Output** (migration-analysis.json):
```json
{
  "scan_date": "2024-01-13T10:30:00Z",
  "scanned_paths": ["scripts/", "airflow/dags/"],
  "summary": {
    "total_files": 143,
    "files_with_bq_usage": 47,
    "total_bq_commands": 218,
    "migration_candidates": 38
  },
  "command_usage": {
    "bq query": 89,
    "bq show": 45,
    "bq ls": 23,
    "bq mk": 12,
    "bq load": 8,
    "other": 41
  },
  "migration_recommendations": [
    {
      "file": "scripts/daily_profiler.sh",
      "priority": "HIGH",
      "current_commands": ["bq query (15x)", "bq show (8x)"],
      "suggested_utility": "bq-profile",
      "estimated_savings": "90% reduction in API calls via caching",
      "complexity": "LOW",
      "migration_steps": [
        "Replace bq show loop with single bq-profile call",
        "Update output format to JSON",
        "Test against current output",
        "Deploy to dev environment"
      ]
    },
    {
      "file": "airflow/dags/quality_checks.py",
      "priority": "HIGH",
      "current_commands": ["bigquery.Client.query (45x)"],
      "suggested_utility": "bq-profile with quality checks",
      "estimated_savings": "$50/month in query costs",
      "complexity": "MEDIUM",
      "migration_steps": [
        "Map Great Expectations checks to bq-profile metrics",
        "Create validation script",
        "Parallel run for 1 week",
        "Compare results",
        "Cutover"
      ]
    }
  ],
  "python_script_analysis": {
    "total_python_files": 67,
    "files_using_bigquery_client": 23,
    "common_patterns": [
      {
        "pattern": "client.get_table() without error handling",
        "occurrences": 18,
        "recommendation": "Use bq_cache.BQMetadataCache with error_context"
      },
      {
        "pattern": "dry_run for cost estimation",
        "occurrences": 12,
        "recommendation": "Replace with bq-query-cost"
      }
    ]
  }
}
```

**Features**:
- Scans multiple directories
- Detects `bq` CLI commands and Python BigQuery usage
- Prioritizes by impact and complexity
- Estimates cost savings
- Generates actionable migration steps
- Exports to HTML report for stakeholder review

### Utility 3: migration-report.py

Generates comprehensive migration assessment and progress tracking.

**Usage**:
```bash
# Initial assessment
python bin/migration-utils/migration-report.py \
  --mode=assessment \
  --output-report=migration-assessment.html

# Progress tracking (run weekly)
python bin/migration-utils/migration-report.py \
  --mode=progress \
  --baseline=migration-assessment.json \
  --output-report=migration-progress-week-2.html
```

**Output** (migration-assessment.html):

```html
<!DOCTYPE html>
<html>
<head><title>BigQuery Migration Assessment</title></head>
<body>
  <h1>Migration to DecentClaude Utilities</h1>

  <h2>Executive Summary</h2>
  <ul>
    <li>Total scripts analyzed: 143</li>
    <li>Migration candidates: 38 (26.6%)</li>
    <li>Estimated effort: 4-6 weeks</li>
    <li>Estimated cost savings: $200-400/month</li>
    <li>Risk level: LOW (incremental migration supported)</li>
  </ul>

  <h2>Migration Phases</h2>
  <table>
    <tr>
      <th>Phase</th>
      <th>Duration</th>
      <th>Scripts</th>
      <th>Effort</th>
      <th>Risk</th>
    </tr>
    <tr>
      <td>Phase 1: Read-only profiling</td>
      <td>Week 1-2</td>
      <td>15</td>
      <td>LOW</td>
      <td>LOW</td>
    </tr>
    <tr>
      <td>Phase 2: Quality checks</td>
      <td>Week 3-4</td>
      <td>12</td>
      <td>MEDIUM</td>
      <td>LOW</td>
    </tr>
    <tr>
      <td>Phase 3: CI/CD integration</td>
      <td>Week 5-6</td>
      <td>11</td>
      <td>MEDIUM</td>
      <td>MEDIUM</td>
    </tr>
  </table>

  <h2>High Priority Migrations</h2>
  <!-- Detailed list from analyze-legacy-usage.py -->

  <h2>Team Training Requirements</h2>
  <ul>
    <li>1-hour workshop: DecentClaude utilities overview</li>
    <li>Hands-on session: Migrating first script</li>
    <li>Office hours: Daily for first 2 weeks</li>
    <li>Documentation: Command aliases, migration guide</li>
  </ul>

  <h2>Success Metrics</h2>
  <ul>
    <li>API calls reduced by 60% (via caching)</li>
    <li>Query costs reduced by 25% (via optimization)</li>
    <li>Data quality check runtime reduced by 70%</li>
    <li>Documentation freshness: < 24 hours lag</li>
  </ul>
</body>
</html>
```

---

## Migration Strategy

### Phase 1: Read-Only Operations (Weeks 1-2)

**Goal**: Introduce utilities without changing existing workflows.

**Activities**:
1. **Install and configure**:
   ```bash
   # Install utilities
   cd /path/to/decentclaude/mayor/rig
   ./bin/setup-wizard.sh

   # Install aliases
   ./bin/install-aliases.sh

   # Verify installation
   bqp --help
   ```

2. **Team training**:
   ```bash
   # 1-hour workshop covering:
   # - bq-profile: Comprehensive table profiling
   # - bq-explain: Query execution plans
   # - bq-explore: Interactive dataset exploration
   # - bq-lineage: Dependency tracking

   # Hands-on exercises:
   bqp your-project.your-dataset.your-table
   bqe --file sample-query.sql --dry-run
   bql your-project.your-dataset.your-table
   ```

3. **Parallel run**:
   ```bash
   # Run legacy and new side-by-side
   # Example: Daily profiling job

   # Legacy (keep running)
   python scripts/daily_profiler.py

   # New (run in parallel)
   bqp project.dataset.table --format=json > profiles/table_$(date +%Y%m%d).json

   # Compare results weekly
   python bin/migration-utils/compare-outputs.py \
     --legacy scripts/output/ \
     --new profiles/ \
     --report weekly-comparison.html
   ```

4. **Success criteria**:
   - [ ] All team members trained on basic utilities
   - [ ] Utilities running in parallel for 1 week
   - [ ] No discrepancies found in output comparison
   - [ ] Positive feedback from team (>80% satisfaction)

### Phase 2: Quality Checks and Monitoring (Weeks 3-4)

**Goal**: Replace legacy quality checks with utilities.

**Activities**:
1. **Map quality checks**:
   ```bash
   # Analyze existing checks
   python bin/migration-utils/analyze-legacy-usage.py \
     --type quality-checks \
     --output quality-check-mapping.json

   # Review mapping
   cat quality-check-mapping.json | jq '.recommendations'
   ```

2. **Create validation scripts**:
   ```bash
   # For each quality check, create validation script
   # Example: Null rate validation

   cat > bin/data-quality/validate-null-rates.sh << 'EOF'
   #!/bin/bash
   set -euo pipefail

   TABLE=$1
   THRESHOLD=${2:-0.05}  # 5% default threshold

   PROFILE=$(bqp "$TABLE" --format=json)

   # Check each column's null rate
   NULL_VIOLATIONS=$(echo "$PROFILE" | jq -r --arg threshold "$THRESHOLD" '
     .quality_checks.null_rates |
     to_entries |
     select(.value > ($threshold | tonumber)) |
     "\(.key): \(.value)"
   ')

   if [[ -n "$NULL_VIOLATIONS" ]]; then
     echo "Null rate violations found:"
     echo "$NULL_VIOLATIONS"
     exit 1
   else
     echo "All columns pass null rate check"
   fi
   EOF

   chmod +x bin/data-quality/validate-null-rates.sh
   ```

3. **Integrate with CI/CD**:
   ```bash
   # Add to pre-commit hooks
   cat >> .git/hooks/pre-push << 'EOF'
   #!/bin/bash
   # Run quality checks before push

   TABLES=(
     "project.dataset.customers"
     "project.dataset.orders"
   )

   for table in "${TABLES[@]}"; do
     echo "Validating $table..."
     if ! bin/data-quality/validate-null-rates.sh "$table"; then
       echo "Quality check failed for $table"
       exit 1
     fi
   done

   echo "All quality checks passed"
   EOF

   chmod +x .git/hooks/pre-push
   ```

4. **Success criteria**:
   - [ ] Quality checks migrated (target: 80%)
   - [ ] CI/CD integration complete
   - [ ] Quality check runtime reduced by >50%
   - [ ] No false positives in validation

### Phase 3: Full CI/CD Integration (Weeks 5-6)

**Goal**: Complete integration with development workflows.

**Activities**:
1. **Cost gates in PR checks**:
   ```yaml
   # .github/workflows/pr-checks.yml
   name: PR Checks
   on: [pull_request]

   jobs:
     query-cost-check:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2

         - name: Install DecentClaude utilities
           run: |
             cd mayor/rig
             ./bin/install-aliases.sh

         - name: Check query costs
           run: |
             for file in $(find . -name "*.sql"); do
               COST=$(bq-query-cost --file "$file" --format=json | jq -r '.estimated_cost')
               if (( $(echo "$COST > 1.00" | bc -l) )); then
                 echo "Query $file exceeds cost threshold: $COST"
                 exit 1
               fi
             done

     schema-diff-check:
       runs-on: ubuntu-latest
       steps:
         - name: Check for breaking schema changes
           run: |
             if git diff --name-only origin/main | grep -q "schema/"; then
               # Detect which tables changed
               for schema_file in $(git diff --name-only origin/main | grep "schema/"); do
                 TABLE=$(basename "$schema_file" .json)
                 bq-schema-diff "project-dev.dataset.$TABLE" "project-prod.dataset.$TABLE" \
                   --format=json > schema-diff.json

                 if jq -e '.breaking_changes | length > 0' schema-diff.json; then
                   echo "Breaking schema change detected in $TABLE"
                   jq '.breaking_changes' schema-diff.json
                   exit 1
                 fi
               done
             fi
   ```

2. **Scheduled profiling**:
   ```python
   # airflow/dags/scheduled_profiling.py
   from airflow import DAG
   from airflow.operators.bash import BashOperator
   from datetime import datetime, timedelta

   default_args = {
       'owner': 'data-eng',
       'depends_on_past': False,
       'start_date': datetime(2024, 1, 1),
       'email_on_failure': True,
       'email_on_retry': False,
       'retries': 1,
       'retry_delay': timedelta(minutes=5),
   }

   dag = DAG(
       'scheduled_table_profiling',
       default_args=default_args,
       description='Profile critical tables daily',
       schedule_interval='0 2 * * *',  # 2 AM daily
       catchup=False
   )

   CRITICAL_TABLES = [
       'project.dataset.customers',
       'project.dataset.orders',
       'project.dataset.events',
   ]

   for table in CRITICAL_TABLES:
       table_name = table.split('.')[-1]

       profile_task = BashOperator(
           task_id=f'profile_{table_name}',
           bash_command=f'''
               bqp {table} --format=json > /data/profiles/{table_name}_$(date +%Y%m%d).json

               # Check for quality issues
               PROFILE=$(cat /data/profiles/{table_name}_$(date +%Y%m%d).json)

               # Alert on high null rates
               NULL_ISSUES=$(echo "$PROFILE" | jq -r '
                 .quality_checks.null_rates |
                 to_entries |
                 select(.value > 0.1) |
                 .key
               ')

               if [[ -n "$NULL_ISSUES" ]]; then
                   echo "High null rates detected in: $NULL_ISSUES"
                   # Send to alerting system
                   curl -X POST https://alerts.example.com/webhook \
                       -d "table={table}&alert=high_null_rate&columns=$NULL_ISSUES"
               fi
           ''',
           dag=dag
       )
   ```

3. **Success criteria**:
   - [ ] All CI/CD pipelines updated
   - [ ] Cost gates preventing expensive queries
   - [ ] Schema change detection active
   - [ ] Scheduled profiling running smoothly
   - [ ] Zero incidents caused by migration

### Phase 4: Decommission Legacy Tools (Weeks 7-8)

**Goal**: Archive legacy tools and complete migration.

**Activities**:
1. **Verify complete migration**:
   ```bash
   # Run final analysis
   python bin/migration-utils/analyze-legacy-usage.py \
     --scan-dir scripts/ \
     --scan-dir airflow/ \
     --output final-audit.json

   # Should show minimal or zero legacy usage
   cat final-audit.json | jq '.summary.files_with_bq_usage'
   ```

2. **Archive legacy scripts**:
   ```bash
   # Move to archive
   mkdir -p archive/legacy-scripts
   mv scripts/legacy_*.py archive/legacy-scripts/

   # Add README
   cat > archive/legacy-scripts/README.md << 'EOF'
   # Legacy Scripts Archive

   These scripts have been migrated to DecentClaude utilities.

   See docs/guides/MIGRATION.md for mapping.

   **Do not use these scripts in production.**

   Archived: 2024-01-13
   EOF

   git add archive/
   git commit -m "Archive legacy scripts after migration"
   ```

3. **Update documentation**:
   ```bash
   # Update README to point to new utilities
   # Update runbooks
   # Update team wiki
   # Update onboarding docs
   ```

4. **Success criteria**:
   - [ ] Legacy script usage at 0%
   - [ ] All documentation updated
   - [ ] Team onboarded to new utilities
   - [ ] Cost savings validated (target: 25%+)
   - [ ] Migration retrospective completed

---

## Migration Checklist

### Pre-Migration

- [ ] **Environment Setup**
  - [ ] DecentClaude utilities installed
  - [ ] Aliases configured for team
  - [ ] Access to BigQuery verified
  - [ ] Test environment available

- [ ] **Analysis**
  - [ ] Legacy usage analyzed
  - [ ] Migration priorities identified
  - [ ] Cost baseline established
  - [ ] Success metrics defined

- [ ] **Team Readiness**
  - [ ] Team trained on utilities
  - [ ] Documentation reviewed
  - [ ] Support channel established (Slack, email)
  - [ ] Office hours scheduled

- [ ] **Planning**
  - [ ] Migration timeline created
  - [ ] Phases defined with milestones
  - [ ] Rollback plan documented
  - [ ] Stakeholders informed

### Phase 1: Read-Only (Weeks 1-2)

- [ ] **Installation**
  - [ ] Utilities installed on all dev machines
  - [ ] Aliases available in all shells
  - [ ] Verified with `dca` (decentclaude-aliases)

- [ ] **Training**
  - [ ] Workshop completed
  - [ ] Hands-on exercises done
  - [ ] Cheat sheet distributed
  - [ ] Knowledge base articles created

- [ ] **Parallel Run**
  - [ ] Legacy scripts still running
  - [ ] New utilities running alongside
  - [ ] Daily comparison of outputs
  - [ ] No discrepancies found

- [ ] **Validation**
  - [ ] Output comparison script created
  - [ ] Automated daily checks
  - [ ] Team feedback collected
  - [ ] Metrics baseline captured

### Phase 2: Quality Checks (Weeks 3-4)

- [ ] **Quality Check Migration**
  - [ ] Quality checks mapped
  - [ ] Validation scripts created
  - [ ] Thresholds configured
  - [ ] Tests passing

- [ ] **CI/CD Integration**
  - [ ] Pre-commit hooks added
  - [ ] PR checks configured
  - [ ] Build pipelines updated
  - [ ] Deployment gates added

- [ ] **Monitoring**
  - [ ] Quality metrics tracked
  - [ ] Alerts configured
  - [ ] Dashboard created
  - [ ] On-call runbook updated

- [ ] **Validation**
  - [ ] No false positives
  - [ ] Quality checks running in <5 min
  - [ ] Team comfortable with workflow
  - [ ] Incidents: 0

### Phase 3: Full Integration (Weeks 5-6)

- [ ] **Automation**
  - [ ] Scheduled profiling running
  - [ ] Cost reporting automated
  - [ ] Schema diff in deployment
  - [ ] Documentation auto-generated

- [ ] **Observability**
  - [ ] Cost tracking dashboard
  - [ ] Query performance monitoring
  - [ ] Data quality trends
  - [ ] Usage analytics

- [ ] **Optimization**
  - [ ] Cache hit rate >60%
  - [ ] API calls reduced by >50%
  - [ ] Query costs down by >20%
  - [ ] Profiling runtime improved

- [ ] **Validation**
  - [ ] All workflows migrated
  - [ ] Legacy usage <5%
  - [ ] Team velocity maintained
  - [ ] Quality maintained

### Phase 4: Decommission (Weeks 7-8)

- [ ] **Cleanup**
  - [ ] Legacy scripts archived
  - [ ] Dependencies removed
  - [ ] Documentation updated
  - [ ] Git history cleaned

- [ ] **Validation**
  - [ ] Legacy usage at 0%
  - [ ] No broken workflows
  - [ ] All tests passing
  - [ ] Cost savings validated

- [ ] **Documentation**
  - [ ] Migration guide complete
  - [ ] Team wiki updated
  - [ ] Runbooks refreshed
  - [ ] Onboarding docs updated

- [ ] **Retrospective**
  - [ ] Lessons learned documented
  - [ ] Metrics reviewed
  - [ ] Improvements identified
  - [ ] Success celebrated!

---

## Common Pitfalls

### Pitfall 1: Trying to Migrate Everything at Once

**Problem**: Team tries to migrate all scripts in week 1, causing disruption and errors.

**Symptom**:
- Broken CI/CD pipelines
- Team members confused
- Increased incident rate
- Rollback pressure

**Solution**:
- Follow phased approach (read-only → quality → full integration)
- Start with low-risk, high-value migrations
- Run parallel for validation period
- Get team buy-in before each phase

**Prevention**:
```bash
# Use migration-report.py to plan phases
python bin/migration-utils/migration-report.py \
  --mode=assessment \
  --output migration-plan.html

# Review with team before starting
# Set realistic milestones
```

### Pitfall 2: Not Validating Output Parity

**Problem**: Assuming new utilities produce identical output without testing.

**Symptom**:
- Data quality checks failing unexpectedly
- Different row counts or metrics
- Confusion about which is correct
- Loss of confidence in new tools

**Solution**:
- Always run parallel validation period
- Automate output comparison
- Document known differences
- Investigate discrepancies before cutover

**Prevention**:
```bash
# Create comparison script for each migration
cat > validate-migration.sh << 'EOF'
#!/bin/bash
set -euo pipefail

LEGACY_OUTPUT=$(python scripts/legacy_profiler.py project.dataset.table)
NEW_OUTPUT=$(bqp project.dataset.table)

# Extract key metrics and compare
LEGACY_ROWS=$(echo "$LEGACY_OUTPUT" | grep "Rows:" | awk '{print $2}')
NEW_ROWS=$(echo "$NEW_OUTPUT" | grep "Rows:" | awk '{print $2}')

if [[ "$LEGACY_ROWS" != "$NEW_ROWS" ]]; then
  echo "Row count mismatch: legacy=$LEGACY_ROWS, new=$NEW_ROWS"
  exit 1
fi

echo "Validation passed"
EOF

# Run daily during parallel period
```

### Pitfall 3: Ignoring Caching Implications

**Problem**: Not understanding how caching affects results.

**Symptom**:
- Stale metadata in profiles
- Confusion when schema changes don't appear
- Cache invalidation issues

**Solution**:
- Understand cache TTL (default: 1 hour)
- Use `--no-cache` for critical operations
- Document cache behavior
- Clear cache after schema changes

**Prevention**:
```bash
# For critical checks, disable cache
bqp project.dataset.table --no-cache

# After schema change, clear cache
rm -rf ~/.cache/bq-metadata/

# In automation, decide on cache strategy:
# - Scheduled jobs: use cache (faster, cheaper)
# - CI/CD checks: no cache (accurate, fresh)
```

### Pitfall 4: Not Training Team Adequately

**Problem**: Team doesn't know how to use new utilities effectively.

**Symptom**:
- Continued use of legacy tools
- Workarounds and scripts
- Frustration and complaints
- Low adoption rate

**Solution**:
- Run hands-on workshop
- Create cheat sheets and quick reference
- Offer office hours
- Build knowledge base articles
- Pair programming for first migrations

**Prevention**:
```bash
# Create team cheat sheet
cat > docs/CHEAT_SHEET.md << 'EOF'
# DecentClaude Quick Reference

## Common Tasks

### Profile a table
```bash
bqp project.dataset.table
```

### Estimate query cost
```bash
bq-query-cost --file query.sql
```

### Compare schemas
```bash
bqd dev.table prod.table
```

### Explore dataset interactively
```bash
bqx
```

## Aliases (after running install-aliases.sh)
- `bqp` = bq-profile
- `bqe` = bq-explain
- `bqd` = bq-schema-diff

## Getting Help
- Run `<command> --help` for any utility
- Slack: #decentclaude-support
- Docs: docs/guides/MIGRATION.md
- Office hours: Daily 2-3 PM
EOF
```

### Pitfall 5: Not Measuring Success

**Problem**: No baseline metrics, can't prove migration value.

**Symptom**:
- Can't quantify cost savings
- Can't show performance improvements
- Difficult to justify effort
- Hard to celebrate wins

**Solution**:
- Capture baselines before migration
- Track metrics throughout
- Create dashboards for visibility
- Report on improvements

**Prevention**:
```bash
# Capture baseline metrics
cat > capture-baseline.sh << 'EOF'
#!/bin/bash

# Capture current state before migration
OUTPUT_FILE="migration-baseline-$(date +%Y%m%d).json"

# Count legacy script usage
LEGACY_SCRIPTS=$(find scripts/ -name "*.py" -o -name "*.sh" | wc -l)

# Estimate current costs (requires BigQuery access)
QUERY_COST=$(bq query --format=csv --use_legacy_sql=false "
SELECT
  SUM(total_bytes_processed) / (1024*1024*1024*1024) as total_tb_processed,
  SUM(total_bytes_processed) / (1024*1024*1024*1024) * 5 as estimated_cost
FROM \`project.region.INFORMATION_SCHEMA.JOBS_BY_PROJECT\`
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
")

# Profile execution times
PROFILE_START=$(date +%s)
python scripts/legacy_profiler.py project.dataset.table > /dev/null 2>&1
PROFILE_END=$(date +%s)
LEGACY_PROFILE_TIME=$((PROFILE_END - PROFILE_START))

# Save baseline
cat > "$OUTPUT_FILE" << JSON
{
  "date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "legacy_scripts": $LEGACY_SCRIPTS,
  "monthly_query_costs": $(echo "$QUERY_COST" | tail -1 | cut -d, -f2),
  "profile_time_seconds": $LEGACY_PROFILE_TIME,
  "api_calls_per_day": 450
}
JSON

echo "Baseline captured: $OUTPUT_FILE"
EOF

# Run before migration starts
./capture-baseline.sh

# Track progress weekly
python bin/migration-utils/migration-report.py \
  --mode=progress \
  --baseline=migration-baseline-*.json \
  --output weekly-progress.html
```

### Pitfall 6: Not Having a Rollback Plan

**Problem**: Migration goes wrong, no plan to revert.

**Symptom**:
- Panic and scrambling
- Extended downtime
- Loss of confidence
- Resistance to future changes

**Solution**:
- Document rollback procedure before migration
- Keep legacy scripts available during parallel run
- Tag git commits for easy revert
- Test rollback in staging

**Prevention**:
```bash
# Document rollback procedure
cat > docs/ROLLBACK.md << 'EOF'
# Migration Rollback Procedure

If migration causes issues, follow these steps:

## 1. Assess Impact
- Identify which phase caused the issue
- Determine affected systems/scripts
- Estimate downtime

## 2. Quick Revert (< 5 minutes)
```bash
# Restore legacy scripts from archive
cp -r archive/legacy-scripts/* scripts/

# Revert CI/CD changes
git revert <migration-commit-sha>

# Restart affected services
systemctl restart airflow
```

## 3. Full Rollback (< 30 minutes)
```bash
# Restore from pre-migration tag
git checkout pre-migration-backup

# Rebuild deployment
./deploy.sh

# Verify legacy tools working
python scripts/test_legacy_tools.py
```

## 4. Post-Rollback
- [ ] Verify all systems operational
- [ ] Notify team of rollback
- [ ] Document what went wrong
- [ ] Schedule retrospective
- [ ] Plan corrective actions before next attempt

## Contact
- On-call: 1-800-DATA-ENG
- Slack: #incident-response
- Email: data-eng@example.com
EOF

# Create pre-migration tag
git tag -a pre-migration-backup -m "Backup before DecentClaude migration"
git push origin pre-migration-backup
```

---

## Validation and Testing

### Pre-Migration Testing

Before migrating any production workflow, test thoroughly in development.

#### Test 1: Output Parity

Verify that new utilities produce equivalent output to legacy tools.

```bash
#!/bin/bash
# test-output-parity.sh

set -euo pipefail

TABLE="project.dataset.test_table"
TEMP_DIR=$(mktemp -d)

echo "Testing output parity for $TABLE"

# Run legacy script
python scripts/legacy_profiler.py "$TABLE" > "$TEMP_DIR/legacy.txt"

# Run new utility
bqp "$TABLE" > "$TEMP_DIR/new.txt"

# Extract and compare key metrics
LEGACY_ROWS=$(grep "Rows:" "$TEMP_DIR/legacy.txt" | awk '{print $2}')
NEW_ROWS=$(grep "Rows:" "$TEMP_DIR/new.txt" | awk '{print $2}')

echo "Legacy rows: $LEGACY_ROWS"
echo "New rows: $NEW_ROWS"

if [[ "$LEGACY_ROWS" != "$NEW_ROWS" ]]; then
  echo "FAIL: Row count mismatch"
  exit 1
fi

# Test JSON output parsing
bqp "$TABLE" --format=json > "$TEMP_DIR/profile.json"
if ! jq -e '.num_rows' "$TEMP_DIR/profile.json" >/dev/null 2>&1; then
  echo "FAIL: JSON output invalid"
  exit 1
fi

echo "PASS: Output parity confirmed"
rm -rf "$TEMP_DIR"
```

#### Test 2: Performance

Verify that new utilities meet performance requirements.

```bash
#!/bin/bash
# test-performance.sh

set -euo pipefail

TABLE="project.dataset.large_table"
RUNS=5

echo "Performance test: $RUNS runs on $TABLE"

# Test legacy script
LEGACY_TOTAL=0
for i in $(seq 1 $RUNS); do
  START=$(date +%s%N)
  python scripts/legacy_profiler.py "$TABLE" > /dev/null 2>&1
  END=$(date +%s%N)
  DURATION=$(( (END - START) / 1000000 ))  # Convert to ms
  LEGACY_TOTAL=$((LEGACY_TOTAL + DURATION))
  echo "  Legacy run $i: ${DURATION}ms"
done
LEGACY_AVG=$((LEGACY_TOTAL / RUNS))

# Test new utility (with cache)
NEW_TOTAL=0
for i in $(seq 1 $RUNS); do
  START=$(date +%s%N)
  bqp "$TABLE" > /dev/null 2>&1
  END=$(date +%s%N)
  DURATION=$(( (END - START) / 1000000 ))
  NEW_TOTAL=$((NEW_TOTAL + DURATION))
  echo "  New run $i: ${DURATION}ms"
done
NEW_AVG=$((NEW_TOTAL / RUNS))

echo ""
echo "Results:"
echo "  Legacy average: ${LEGACY_AVG}ms"
echo "  New average: ${NEW_AVG}ms"

IMPROVEMENT=$(( (LEGACY_AVG - NEW_AVG) * 100 / LEGACY_AVG ))
echo "  Improvement: ${IMPROVEMENT}%"

if [[ $NEW_AVG -lt $LEGACY_AVG ]]; then
  echo "PASS: New utility is faster"
else
  echo "WARN: New utility is slower (but may have more features)"
fi
```

#### Test 3: Error Handling

Verify that utilities handle errors gracefully.

```bash
#!/bin/bash
# test-error-handling.sh

set -euo pipefail

echo "Testing error handling"

# Test 1: Invalid table ID
if bqp "invalid.table.id" 2>/dev/null; then
  echo "FAIL: Should reject invalid table ID"
  exit 1
else
  echo "PASS: Invalid table ID rejected"
fi

# Test 2: Non-existent table
if bqp "project.dataset.nonexistent" 2>/dev/null; then
  echo "FAIL: Should handle non-existent table"
  exit 1
else
  echo "PASS: Non-existent table handled"
fi

# Test 3: Permission denied (if applicable)
# if bqp "restricted.dataset.table" 2>/dev/null; then
#   echo "FAIL: Should handle permission denied"
#   exit 1
# else
#   echo "PASS: Permission denied handled"
# fi

echo "All error handling tests passed"
```

### Post-Migration Validation

After migrating each component, validate that it works correctly.

#### Validation 1: Functional Testing

```bash
#!/bin/bash
# validate-functional.sh

set -euo pipefail

COMPONENT=$1  # e.g., "quality-checks", "ci-cd", "scheduled-jobs"

echo "Functional validation: $COMPONENT"

case "$COMPONENT" in
  quality-checks)
    # Test quality check workflow
    bqp project.dataset.test_table --format=json > profile.json

    # Verify expected fields exist
    jq -e '.quality_checks' profile.json >/dev/null
    jq -e '.quality_checks.null_rates' profile.json >/dev/null
    jq -e '.quality_checks.uniqueness_ratios' profile.json >/dev/null

    echo "PASS: Quality checks functional"
    ;;

  ci-cd)
    # Test CI/CD integration
    # (Run this in CI environment)

    # Test cost gate
    COST=$(bq-query-cost --query "SELECT 1" --format=json | jq -r '.estimated_cost')
    if [[ -z "$COST" ]]; then
      echo "FAIL: Cost estimation not working"
      exit 1
    fi

    echo "PASS: CI/CD integration functional"
    ;;

  scheduled-jobs)
    # Test scheduled job execution
    # (Run this on scheduler)

    # Verify output directory exists
    if [[ ! -d "/data/profiles" ]]; then
      echo "FAIL: Output directory not found"
      exit 1
    fi

    # Verify recent profiles exist
    RECENT_PROFILES=$(find /data/profiles -name "*.json" -mtime -1 | wc -l)
    if [[ $RECENT_PROFILES -lt 1 ]]; then
      echo "FAIL: No recent profiles found"
      exit 1
    fi

    echo "PASS: Scheduled jobs functional"
    ;;

  *)
    echo "Unknown component: $COMPONENT"
    exit 1
    ;;
esac
```

#### Validation 2: Integration Testing

```bash
#!/bin/bash
# validate-integration.sh

set -euo pipefail

echo "Integration testing: End-to-end workflow"

# Simulate typical workflow
TABLE="project.dataset.integration_test"

# 1. Profile table
echo "Step 1: Profile table"
bqp "$TABLE" --format=json > profile.json

# 2. Check quality metrics
echo "Step 2: Check quality"
NULL_RATE=$(cat profile.json | jq -r '.quality_checks.null_rates.email // 0')
if (( $(echo "$NULL_RATE > 0.5" | bc -l) )); then
  echo "Quality issue detected: high null rate"
  # Would trigger alert in production
fi

# 3. Analyze query
echo "Step 3: Analyze query"
QUERY="SELECT * FROM \`$TABLE\` WHERE date >= '2024-01-01'"
bq-query-cost --query "$QUERY" --format=json > cost.json

# 4. Verify cost acceptable
COST=$(cat cost.json | jq -r '.estimated_cost')
if (( $(echo "$COST > 1.0" | bc -l) )); then
  echo "Cost too high: $COST"
  exit 1
fi

# 5. Check lineage
echo "Step 4: Check lineage"
bql "$TABLE" --format=json > lineage.json
DOWNSTREAM=$(cat lineage.json | jq -r '.downstream | length')
echo "Downstream dependencies: $DOWNSTREAM"

echo "PASS: Integration test complete"
```

---

## Rollback Plan

### When to Rollback

Initiate rollback if:
- **Critical production issue** caused by migration
- **Data quality degradation** detected
- **Significant performance regression** (>50% slower)
- **Team velocity severely impacted** (>30% slower)
- **Cost increase >20%** without clear value

### Rollback Procedures

#### Quick Rollback (5 minutes)

For issues in Phase 1 or 2 (before full integration):

```bash
#!/bin/bash
# quick-rollback.sh

set -euo pipefail

echo "Initiating quick rollback"

# 1. Restore legacy scripts
if [[ -d "archive/legacy-scripts" ]]; then
  echo "Restoring legacy scripts..."
  cp -r archive/legacy-scripts/* scripts/
else
  echo "ERROR: Archive not found"
  exit 1
fi

# 2. Disable new utilities temporarily
if [[ -f "$HOME/.bashrc" ]]; then
  echo "Disabling aliases..."
  sed -i.bak '/decentclaude.*aliases/d' "$HOME/.bashrc"
fi

# 3. Restart services
echo "Restarting services..."
# systemctl restart airflow  # If using systemd
# supervisorctl restart all  # If using supervisor

echo "Quick rollback complete"
echo "Legacy scripts restored to scripts/"
echo "Please restart your shell or run: source ~/.bashrc"
```

#### Full Rollback (30 minutes)

For issues in Phase 3 or 4 (full integration):

```bash
#!/bin/bash
# full-rollback.sh

set -euo pipefail

echo "Initiating full rollback"

# 1. Revert to pre-migration git state
echo "Reverting git changes..."
git checkout pre-migration-backup

# 2. Restore configurations
echo "Restoring configurations..."
git checkout pre-migration-backup -- .github/workflows/
git checkout pre-migration-backup -- .git/hooks/
git checkout pre-migration-backup -- airflow/dags/

# 3. Rebuild and redeploy
echo "Rebuilding..."
# ./build.sh  # If applicable

echo "Redeploying..."
# ./deploy.sh  # If applicable

# 4. Verify legacy tools working
echo "Verifying legacy tools..."
python scripts/test_legacy_tools.py

# 5. Notify team
echo "Notifying team..."
# curl -X POST https://slack.com/webhook -d '{"text":"Migration rolled back"}'

echo "Full rollback complete"
echo "Please verify all systems operational"
```

### Post-Rollback Actions

1. **Verify systems operational**:
   ```bash
   # Run smoke tests
   ./scripts/smoke-tests.sh

   # Check monitoring dashboards
   # Verify no alerts firing
   ```

2. **Document incident**:
   ```bash
   # Create incident report
   cat > incidents/migration-rollback-$(date +%Y%m%d).md << 'EOF'
   # Migration Rollback Incident

   **Date**: 2024-01-XX
   **Duration**: X hours
   **Impact**: [Description]

   ## Timeline
   - HH:MM - Migration deployed
   - HH:MM - Issue detected
   - HH:MM - Rollback initiated
   - HH:MM - Systems restored

   ## Root Cause
   [Description]

   ## Resolution
   [Steps taken]

   ## Follow-up Actions
   - [ ] Fix root cause
   - [ ] Add safeguards
   - [ ] Update testing procedures
   - [ ] Schedule retrospective
   EOF
   ```

3. **Schedule retrospective**:
   - Review what went wrong
   - Identify improvements
   - Update migration plan
   - Decide on next steps

---

## Success Metrics and ROI

### Metrics to Track

Track these metrics before, during, and after migration:

#### Cost Metrics

```bash
# Monthly query cost
bq query --format=csv --use_legacy_sql=false "
SELECT
  DATE_TRUNC(DATE(creation_time), MONTH) as month,
  SUM(total_bytes_processed) / POW(1024, 4) as tb_processed,
  SUM(total_bytes_processed) / POW(1024, 4) * 5 as estimated_cost_usd
FROM \`project.region.INFORMATION_SCHEMA.JOBS_BY_PROJECT\`
WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 6 MONTH)
GROUP BY month
ORDER BY month DESC
"

# API call costs (metadata operations)
# Track via Cloud Billing API or export to BigQuery
```

#### Performance Metrics

```bash
# Average profiling time
# Before: Time to run legacy scripts
# After: Time to run bq-profile

# Query development cycle time
# Before: Time from writing query to production
# After: Time with cost estimation + optimization

# Data quality check runtime
# Before: Time to run all quality checks
# After: Time to run bq-profile-based checks
```

#### Adoption Metrics

```bash
# Utility usage
# Track command frequency via shell history or wrapper

# Legacy script usage
grep -r "bq query" scripts/ | wc -l  # Count legacy usage
grep -r "bq-" scripts/ | wc -l      # Count new utility usage

# Team satisfaction
# Survey: "How satisfied are you with DecentClaude utilities?" (1-5)
```

### Expected ROI

Based on typical migrations:

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Monthly query costs** | $500 | $375 | 25% reduction |
| **API calls** | 10,000/month | 4,000/month | 60% reduction |
| **Data quality check runtime** | 45 min | 12 min | 73% reduction |
| **Query development time** | 30 min/query | 15 min/query | 50% reduction |
| **Documentation freshness** | 1 week lag | < 24 hours | 86% improvement |
| **Incident response time** | 2 hours | 45 min | 62% reduction |

**Total Value** (medium-sized team):
- Cost savings: $100-500/month
- Time savings: 20-40 hours/month
- Quality improvements: Fewer data incidents, faster detection
- **ROI**: Positive within 1-2 months

---

## Conclusion

Migrating from legacy BigQuery tools to DecentClaude utilities provides significant benefits in cost, consistency, and observability. By following this guide's phased approach and using the provided migration utilities, teams can complete the transition smoothly with minimal risk.

### Key Takeaways

1. **Go Incremental**: Phase 1 (read-only) → Phase 2 (quality) → Phase 3 (full integration)
2. **Validate Everything**: Run parallel, compare outputs, test thoroughly
3. **Train the Team**: Workshops, cheat sheets, office hours
4. **Measure Success**: Baseline metrics, track progress, celebrate wins
5. **Have a Rollback Plan**: Document procedures, test in staging, be prepared

### Next Steps

1. Run migration assessment:
   ```bash
   python bin/migration-utils/analyze-legacy-usage.py \
     --scan-dir scripts/ \
     --output-report migration-assessment.html
   ```

2. Review with team and stakeholders

3. Begin Phase 1 (read-only operations)

4. Track progress weekly

5. Celebrate success!

### Support

- **Documentation**: `docs/guides/`
- **Issues**: Create GitHub issue with `migration` label
- **Questions**: Slack #decentclaude-support
- **Training**: Schedule workshop with data engineering team

---

*Last updated: 2024-01-13*
*Version: 1.0*
