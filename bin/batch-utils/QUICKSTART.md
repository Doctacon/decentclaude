# Batch Utils Quick Start Guide

Quick reference for common batch processing tasks.

## Quick Examples

### Profile Multiple Tables

```bash
# From file list
batch-profile --file=tables.txt --compare --format=html --output=report.html

# Entire dataset
batch-profile --dataset=project.analytics --compare --progress

# With anomaly detection
batch-profile --file=critical_tables.csv --detect-anomalies --parallel=8
```

### Compare Table Pairs

```bash
# From pairs file
batch-compare --file=pairs.txt --progress --format=markdown --output=diff.md

# Critical differences only
batch-compare --file=staging_prod.txt --critical-only --format=html

# Staging to production validation
echo "staging.users:prod.users" | batch-compare --stdin --skip-samples
```

### Optimize Queries

```bash
# All queries in directory
batch-optimize --dir=sql/ --prioritize --top=10

# High-cost queries only
batch-optimize --dir=sql/ --min-cost=50 --format=html --output=costly.html

# Prioritized optimization report
batch-optimize --file=queries.txt --prioritize --format=json --output=opts.json
```

## Common Command Patterns

### Input Sources

```bash
# Direct arguments
batch-profile table1 table2 table3

# From file
batch-profile --file=tables.txt

# From stdin
cat tables.txt | batch-profile --stdin

# Entire dataset
batch-profile --dataset=project.dataset

# Directory of files
batch-optimize --dir=sql/
```

### Output Formats

```bash
# Terminal output (default)
batch-profile --file=tables.txt

# JSON for automation
batch-profile --file=tables.txt --format=json --output=data.json

# Markdown for docs
batch-profile --file=tables.txt --format=markdown --output=report.md

# HTML for sharing
batch-profile --file=tables.txt --format=html --output=report.html
```

### Performance Tuning

```bash
# More workers = faster
batch-profile --file=tables.txt --parallel=8

# Show progress
batch-profile --file=tables.txt --progress

# Continue on errors
batch-profile --file=tables.txt --continue-on-error --log=errors.log

# Quiet mode (summary only)
batch-profile --file=tables.txt --quiet --compare
```

## File Formats

### Tables List (tables.txt)
```
project.dataset.table1
project.dataset.table2
project.dataset.table3
```

### Table Pairs (pairs.txt)
```
staging.users:prod.users
staging.orders:prod.orders
staging.products:prod.products
```

### CSV with Names (tables.csv)
```csv
table_id,name
project.dataset.users,User Data
project.dataset.orders,Order History
```

### JSON Format
```json
[
  {"table_id": "project.dataset.users", "name": "Users"},
  {"table_id": "project.dataset.orders", "name": "Orders"}
]
```

## One-Liners

```bash
# Profile all tables matching pattern
batch-profile --dataset=project.warehouse --pattern="fact_.*" --compare

# Compare staging to prod for all tables
for table in users orders products; do
  echo "staging.$table:prod.$table"
done | batch-compare --stdin --critical-only

# Find most expensive queries
batch-optimize --dir=sql/ --prioritize --top=5 --quiet

# Daily health check
batch-profile --file=critical_tables.txt \
  --compare --format=html \
  --output="health_$(date +%Y%m%d).html"

# Migration validation
batch-compare --file=migration_pairs.txt \
  --progress --continue-on-error \
  --log=migration.log --format=html

# Cost optimization sprint
batch-optimize --dir=sql/ \
  --prioritize --min-cost=10 --top=20 \
  --format=markdown --output=optimizations.md
```

## Common Workflows

### Pre-Deployment Checklist

```bash
#!/bin/bash
set -e

echo "Comparing staging to production..."
batch-compare --file=deployment/pairs.txt --critical-only

echo "Profiling new tables..."
batch-profile --file=deployment/new_tables.txt --detect-anomalies

echo "Optimizing new queries..."
batch-optimize --file=deployment/new_queries.txt --min-cost=5

echo "All checks passed!"
```

### Weekly Cost Report

```bash
#!/bin/bash
WEEK=$(date +%Y_week_%V)

# Most expensive queries
batch-optimize --dir=sql/production/ \
  --prioritize --top=20 \
  --format=html \
  --output="reports/costs_${WEEK}.html"

# Largest tables
batch-profile --dataset=project.warehouse \
  --compare --top=15 \
  --format=json \
  --output="reports/sizes_${WEEK}.json"
```

### Data Quality Monitoring

```bash
#!/bin/bash
DATE=$(date +%Y%m%d)

batch-profile --file=config/monitored_tables.csv \
  --detect-anomalies \
  --compare \
  --format=html \
  --output="reports/quality_${DATE}.html" \
  --log="logs/quality_${DATE}.log"
```

## Tips

1. **Start Small**: Test with a few items before running on large batches
2. **Use Progress**: Always use `--progress` for long-running operations
3. **Log Everything**: Use `--log` for debugging and audit trails
4. **Parallelize Wisely**: 4-8 workers is usually optimal
5. **Filter Results**: Use `--quiet`, `--critical-only`, `--min-cost` to focus
6. **Output to Files**: Use `--output` to save reports for later analysis

## Getting Help

```bash
batch-profile --help
batch-compare --help
batch-optimize --help
```

For detailed documentation, see README.md in this directory.
