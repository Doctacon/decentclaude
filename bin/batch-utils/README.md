# Batch Processing Utilities for BigQuery

This directory contains batch processing wrapper utilities for running multiple BigQuery operations efficiently with parallel processing and aggregated reporting.

## Overview

The batch utilities wrap existing data-utils tools (`bq-profile`, `bq-table-compare`, `bq-optimize`) to process multiple targets in parallel and generate comprehensive aggregate reports.

### Available Tools

1. **batch-profile** - Profile multiple tables with comparative analysis
2. **batch-compare** - Compare multiple table pairs with difference aggregation
3. **batch-optimize** - Analyze multiple queries with prioritized recommendations

All tools support:
- Multiple input formats (CSV, JSON, text, stdin)
- Parallel processing with configurable workers
- Multiple output formats (text, JSON, Markdown, HTML)
- Progress tracking
- Error handling with continue-on-error
- Detailed logging

## batch-profile

Profile multiple BigQuery tables and generate comparative analysis across all tables.

### Usage

```bash
# Profile multiple tables directly
batch-profile project.dataset.users project.dataset.orders project.dataset.products

# Profile from CSV file
batch-profile --file=tables.csv --format=markdown --output=report.md

# Profile entire dataset with pattern filter
batch-profile --dataset=project.dataset --pattern="fact_.*" --compare

# Profile from stdin with progress
cat tables.txt | batch-profile --stdin --progress --parallel=8

# Generate HTML report with comparative analysis
batch-profile --file=tables.json --compare --format=html --output=profiles.html
```

### Input Formats

**Text file** (one table per line):
```
project.dataset.table1
project.dataset.table2
project.dataset.table3
```

**CSV file**:
```csv
table_id,name
project.dataset.table1,Users Table
project.dataset.table2,Orders Table
```

**JSON file**:
```json
[
  {"table_id": "project.dataset.table1", "name": "Users"},
  {"table_id": "project.dataset.table2", "name": "Orders"}
]
```

### Options

```
--file=<path>           Read table list from CSV/JSON file
--stdin                 Read table list from stdin
--dataset=<dataset>     Profile all tables in dataset
--pattern=<pattern>     Filter tables by regex pattern
--parallel=<n>          Number of parallel workers (default: 4)
--format=<format>       Output format: text, json, markdown, html
--output=<path>         Write to file instead of stdout
--compare               Generate comparative analysis
--top=<n>               Show top N tables in comparisons (default: 10)
--detect-anomalies      Enable anomaly detection
--sample-size=<n>       Sample size per table (default: 10)
--progress              Show progress bar
--quiet                 Only show summary, not individual profiles
--continue-on-error     Continue if individual tables fail
--log=<path>            Write detailed log file
```

### Example Output (Text Format)

```
Batch Profile Report
================================================================================
Generated: 2025-01-13T10:30:00
Tables profiled: 25
Errors: 0
Execution time: 45.23s

Comparative Analysis
--------------------------------------------------------------------------------
Total rows across all tables: 15,234,567
Total size: 125.45 GB

Partitioning:
  Partitioned tables: 18
  Non-partitioned tables: 7
  Clustered tables: 12

Largest Tables:
  1. fact_sales: 45.23 GB (5,234,567 rows)
  2. fact_orders: 32.11 GB (3,456,789 rows)
  3. dim_customers: 15.67 GB (2,345,678 rows)

Highest Average Null Rates:
  1. staging_temp: 45.2%
  2. dim_products: 23.1%
  3. fact_events: 18.7%

Most Columns:
  1. fact_sales: 156 columns
  2. dim_customers: 89 columns
  3. fact_orders: 67 columns
```

### Comparative Analysis Features

When `--compare` is enabled, the report includes:
- Total rows and size across all tables
- Partitioning and clustering statistics
- Largest tables by size
- Tables with highest null rates
- Tables with most columns
- Oldest and newest tables

### Use Cases

1. **Dataset Health Check**: Profile all tables in a dataset to identify issues
   ```bash
   batch-profile --dataset=project.analytics --compare --format=html --output=health.html
   ```

2. **Migration Validation**: Profile tables before/after migration
   ```bash
   batch-profile --file=critical_tables.txt --detect-anomalies --log=migration.log
   ```

3. **Cost Analysis**: Identify largest tables for cost optimization
   ```bash
   batch-profile --dataset=project.warehouse --compare --top=20 --quiet
   ```

4. **Data Quality Report**: Generate regular quality reports
   ```bash
   batch-profile --file=monitored_tables.csv --format=markdown --output=quality_$(date +%Y%m%d).md
   ```

## batch-compare

Compare multiple BigQuery table pairs and aggregate differences with critical alerts.

### Usage

```bash
# Compare multiple pairs directly
batch-compare staging.users:prod.users staging.orders:prod.orders

# Compare from file
batch-compare --file=pairs.txt --format=json --output=differences.json

# Compare with progress and critical-only reporting
batch-compare --file=pairs.csv --critical-only --progress --parallel=8

# Compare from stdin
cat pairs.txt | batch-compare --stdin --format=html --output=comparison.html
```

### Input Formats

**Text file** (one pair per line, use `:` or `|` as separator):
```
project.staging.table1:project.prod.table1
project.staging.table2|project.prod.table2
```

**CSV file**:
```csv
table_a,table_b,name
project.staging.users,project.prod.users,Users Comparison
project.staging.orders,project.prod.orders,Orders Comparison
```

**JSON file**:
```json
[
  {
    "table_a": "project.staging.users",
    "table_b": "project.prod.users",
    "name": "Users Staging vs Prod"
  }
]
```

### Options

```
--file=<path>           Read table pairs from file
--stdin                 Read pairs from stdin
--parallel=<n>          Number of parallel workers (default: 4)
--format=<format>       Output format: text, json, markdown, html
--output=<path>         Write to file
--sample-size=<n>       Sample rows for comparison (default: 100)
--skip-stats            Skip statistical comparisons (faster)
--skip-samples          Skip sample data comparison
--progress              Show progress bar
--quiet                 Only show summary
--continue-on-error     Continue on errors
--log=<path>            Write log file
--critical-only         Only report critical differences
--threshold=<pct>       Row count diff threshold % (default: 10)
```

### Example Output (Text Format)

```
Batch Comparison Report
================================================================================
Generated: 2025-01-13T10:45:00
Comparisons completed: 15
Errors: 0
Execution time: 32.15s

Aggregate Analysis
--------------------------------------------------------------------------------
Total comparisons: 15
Critical differences: 3
Schema differences: 2
Row count differences: 5
Identical tables: 10

Critical Differences:
  Users Staging vs Prod
    project.staging.users
    project.prod.users
    Status: schema_mismatch

  Orders Staging vs Prod
    project.staging.orders
    project.prod.orders
    Status: large_row_count_difference
```

### Critical Difference Detection

A comparison is flagged as critical if:
- Schema differences exist (missing columns, type changes)
- Row count difference exceeds threshold (default 10%)

### Use Cases

1. **Staging to Production Validation**: Compare before promoting
   ```bash
   batch-compare --file=staging_prod_pairs.txt --critical-only --format=html
   ```

2. **Migration Verification**: Compare old vs new tables
   ```bash
   batch-compare --file=migration_pairs.csv --progress --log=migration.log
   ```

3. **Environment Sync Check**: Verify environments are in sync
   ```bash
   batch-compare --file=dev_prod_pairs.txt --skip-samples --threshold=5
   ```

4. **Data Replication Audit**: Check replicated tables
   ```bash
   batch-compare --file=replication_pairs.json --format=json --output=audit.json
   ```

## batch-optimize

Analyze multiple BigQuery queries and prioritize optimization recommendations by potential cost savings.

### Usage

```bash
# Optimize multiple query files
batch-optimize queries/fact_*.sql

# Optimize all queries in directory
batch-optimize --dir=sql/ --pattern=".*_daily\\.sql"

# Optimize from file list with prioritization
batch-optimize --file=queries.txt --prioritize --format=html --output=optimizations.html

# Optimize from stdin with cost filtering
find sql/ -name "*.sql" | batch-optimize --stdin --min-cost=10 --progress

# Generate prioritized report
batch-optimize --dir=sql/ --prioritize --top=20 --format=json --output=top_optimizations.json
```

### Input Formats

**Text file** (one query file path per line):
```
/path/to/query1.sql
/path/to/query2.sql
/path/to/query3.sql
```

**JSON file**:
```json
[
  {"path": "/path/to/query1.sql", "name": "Daily Sales Report"},
  {"path": "/path/to/query2.sql", "name": "User Analytics"}
]
```

### Options

```
--dir=<path>            Analyze all .sql files in directory (recursive)
--file=<path>           Read query file list
--stdin                 Read paths from stdin
--pattern=<pattern>     Filter SQL files by regex
--parallel=<n>          Number of parallel workers (default: 4)
--format=<format>       Output format: text, json, markdown, html
--output=<path>         Write to file
--progress              Show progress bar
--quiet                 Only show summary
--continue-on-error     Continue on errors
--log=<path>            Write log file
--prioritize            Prioritize by cost savings
--top=<n>               Show top N queries (default: 10)
--min-cost=<gb>         Only include queries processing >= N GB
```

### Example Output (Text Format)

```
Batch Optimization Report
================================================================================
Generated: 2025-01-13T11:00:00
Queries analyzed: 42
Errors: 0
Execution time: 28.45s

Aggregate Analysis
--------------------------------------------------------------------------------
Total queries analyzed: 42
Total data processed: 1,245.67 GB
Total recommendations: 156

Severity breakdown:
  Critical: 12
  High: 28
  Medium: 67
  Low: 49

Most Common Recommendations:
  partition_filter: 18
  select_star: 15
  join_optimization: 12
  subquery_optimization: 10

Top Queries by Cost:
  1. daily_sales_report: 234.56 GB
  2. customer_analytics: 189.23 GB
  3. inventory_summary: 156.78 GB

Top Queries by Optimization Potential:
  1. daily_sales_report: score 485.6 (12 recommendations)
  2. user_behavior_analysis: score 367.2 (8 recommendations)
  3. product_recommendations: score 289.4 (10 recommendations)
```

### Optimization Scoring

When `--prioritize` is enabled, queries are scored based on:
- GB processed (higher = more cost)
- Number of recommendations
- Severity of recommendations (critical = 50 points, high = 25, medium = 10)

This helps identify the queries that would benefit most from optimization.

### Use Cases

1. **Cost Optimization Initiative**: Find highest-impact optimizations
   ```bash
   batch-optimize --dir=sql/ --prioritize --min-cost=50 --top=10
   ```

2. **Query Performance Audit**: Analyze all production queries
   ```bash
   batch-optimize --dir=production/sql/ --format=html --output=audit.html
   ```

3. **Pre-Deployment Review**: Check queries before deployment
   ```bash
   batch-optimize --file=new_queries.txt --continue-on-error --log=review.log
   ```

4. **Regular Optimization Reports**: Generate weekly reports
   ```bash
   batch-optimize --dir=sql/ --prioritize --format=markdown --output=weekly_$(date +%Y%m%d).md
   ```

## Common Patterns

### Parallel Processing

All tools support parallel processing with `--parallel`:
```bash
# Use 8 workers for faster processing
batch-profile --file=tables.txt --parallel=8

# Auto-detect CPU count
batch-profile --file=tables.txt --parallel=$(nproc)
```

### Progress Tracking

Enable progress bars with `--progress`:
```bash
batch-profile --file=large_dataset.txt --progress
```

### Error Handling

Continue processing even if individual items fail:
```bash
batch-profile --file=tables.txt --continue-on-error --log=errors.log
```

### Output Formats

Generate reports in different formats:
```bash
# Text for terminal
batch-profile --file=tables.txt --format=text

# JSON for programmatic processing
batch-profile --file=tables.txt --format=json --output=data.json

# Markdown for documentation
batch-profile --file=tables.txt --format=markdown --output=report.md

# HTML for sharing
batch-profile --file=tables.txt --format=html --output=report.html
```

### Filtering Results

Show only important results:
```bash
# Only critical differences
batch-compare --file=pairs.txt --critical-only

# Only queries over 10 GB
batch-optimize --dir=sql/ --min-cost=10

# Only top 5 results
batch-profile --file=tables.txt --compare --top=5 --quiet
```

## Integration Examples

### CI/CD Pipeline

```bash
#!/bin/bash
# Pre-deployment validation

# Compare staging to production
batch-compare \
  --file=deployment/table_pairs.txt \
  --critical-only \
  --format=json \
  --output=comparison_results.json

# Check for critical differences
if grep -q '"critical_differences": [^0]' comparison_results.json; then
  echo "Critical differences found! Review required."
  exit 1
fi

# Optimize new queries
batch-optimize \
  --file=deployment/new_queries.txt \
  --min-cost=5 \
  --format=markdown \
  --output=optimization_report.md
```

### Daily Health Check

```bash
#!/bin/bash
# Daily table health monitoring

REPORT_DATE=$(date +%Y%m%d)

# Profile all critical tables
batch-profile \
  --file=config/critical_tables.csv \
  --compare \
  --detect-anomalies \
  --format=html \
  --output="reports/health_${REPORT_DATE}.html" \
  --log="logs/health_${REPORT_DATE}.log"

# Send report via email
mail -s "Daily BigQuery Health Report" \
  -a "reports/health_${REPORT_DATE}.html" \
  team@example.com < /dev/null
```

### Cost Optimization Sprint

```bash
#!/bin/bash
# Weekly cost optimization analysis

WEEK=$(date +%Y_week_%V)

# Find highest-cost queries
batch-optimize \
  --dir=sql/production/ \
  --prioritize \
  --top=20 \
  --min-cost=10 \
  --format=markdown \
  --output="reports/optimization_${WEEK}.md"

# Profile largest tables
batch-profile \
  --dataset=project.warehouse \
  --compare \
  --top=15 \
  --format=json \
  --output="reports/table_sizes_${WEEK}.json"
```

### Migration Validation

```bash
#!/bin/bash
# Validate data migration

# Compare all migrated tables
batch-compare \
  --file=migration/table_pairs.csv \
  --sample-size=1000 \
  --progress \
  --continue-on-error \
  --format=html \
  --output=migration_validation.html \
  --log=migration_validation.log

# Profile new tables
batch-profile \
  --file=migration/new_tables.txt \
  --detect-anomalies \
  --format=json \
  --output=new_tables_profile.json
```

## Performance Tips

1. **Adjust Parallelism**: Start with 4 workers, increase based on your machine's CPU
   ```bash
   batch-profile --file=tables.txt --parallel=8
   ```

2. **Use Filtering**: Process only what you need
   ```bash
   batch-optimize --dir=sql/ --min-cost=10  # Skip cheap queries
   batch-compare --file=pairs.txt --skip-samples  # Faster comparison
   ```

3. **Enable Progress**: Track long-running operations
   ```bash
   batch-profile --file=large_dataset.txt --progress
   ```

4. **Use Quiet Mode**: Speed up by skipping detailed output
   ```bash
   batch-profile --file=tables.txt --quiet --compare
   ```

5. **Batch by Size**: Process large items separately
   ```bash
   # Small tables first (fast)
   batch-profile --file=small_tables.txt --parallel=16

   # Large tables separately (slower, fewer workers)
   batch-profile --file=large_tables.txt --parallel=2
   ```

## Logging and Debugging

All tools support detailed logging:
```bash
batch-profile \
  --file=tables.txt \
  --log=debug.log \
  --continue-on-error
```

Log format:
```
[2025-01-13T10:30:00] [INFO] Loading tables from file: tables.txt
[2025-01-13T10:30:01] [INFO] Loaded 25 tables
[2025-01-13T10:30:02] [INFO] Profiling table: project.dataset.users
[2025-01-13T10:30:15] [INFO] Successfully profiled: project.dataset.users
[2025-01-13T10:30:16] [ERROR] Failed to profile project.dataset.temp: Table not found
```

## Dependencies

These utilities require:
- Python 3.7+
- `google-cloud-bigquery` (for dataset operations)
- `rich` (optional, for progress bars)
- Underlying tools: `bq-profile`, `bq-table-compare`, `bq-optimize`

## Troubleshooting

### "Command not found: bq-profile"

Ensure the data-utils tools are in the correct location:
```bash
ls ../data-utils/bq-profile
```

### Timeout Errors

Increase timeout for large operations by modifying the timeout in the code, or process in smaller batches.

### Memory Issues

Reduce parallelism:
```bash
batch-profile --file=tables.txt --parallel=2
```

### Permission Errors

Ensure BigQuery permissions are set:
```bash
gcloud auth application-default login
```

## Contributing

When adding new batch utilities:
1. Follow the existing pattern (parallel processing, multiple formats, etc.)
2. Support stdin, file, and direct arguments
3. Include progress tracking and error handling
4. Generate aggregate analysis
5. Document with examples

## License

Part of the Mayor rig data utilities suite.
