# BI Tools - BigQuery to BI Platform Integration

Command-line utilities for integrating BigQuery data models with Business Intelligence platforms (Looker, Tableau, etc.).

## Overview

This toolkit provides utilities to:
- Export BigQuery tables to Looker LookML views
- Generate Tableau Data Source (TDS) files
- Sync metadata between BigQuery and BI tools
- Track table usage and dashboard dependencies
- Document BI platform integrations

## Tools

### 1. looker-export

Export BigQuery tables to Looker LookML view files.

**Features:**
- Automatic dimension and measure generation
- Type mapping from BigQuery to Looker
- Support for time dimensions with standard timeframes
- Optional auto-generated measures
- Batch export entire datasets

**Basic Usage:**

```bash
# Export a single table
looker-export project.analytics.fct_orders

# Export with auto-generated measures
looker-export project.analytics.fct_orders --include-measures

# Export entire dataset
looker-export --dataset=project.analytics --output-dir=./lookml

# Use sql_table_name instead of derived table
looker-export project.analytics.dim_customers --sql-table-name
```

**Examples:**

```bash
# Export all fact tables to a Looker project
looker-export --dataset=project.marts_finance \
  --output-dir=./looker/views \
  --include-measures

# Export a dimension table with sql_table_name reference
looker-export project.dimensions.dim_products \
  --sql-table-name \
  --output-dir=./looker/views
```

**Output:**

Generates `.view.lkml` files in the specified output directory:

```lkml
view: fct_orders {
  sql_table_name: `project.analytics.fct_orders` ;;

  dimension: order_id {
    primary_key: yes
    type: number
    sql: ${TABLE}.order_id ;;
  }

  dimension: order_date {
    type: date
    sql: ${TABLE}.order_date ;;
    datatype: timestamp
    timeframes: [raw, time, date, week, month, quarter, year]
  }

  measure: count {
    type: count
    drill_fields: [*]
  }
}
```

---

### 2. tableau-export

Generate Tableau Data Source (TDS) XML files for BigQuery tables.

**Features:**
- Full TDS XML generation with BigQuery connector configuration
- Automatic field role assignment (dimension vs. measure)
- Type mapping from BigQuery to Tableau
- Batch export entire datasets
- Metadata preservation (descriptions, custom fields)

**Basic Usage:**

```bash
# Export a single table
tableau-export project.analytics.fct_sales

# Export entire dataset
tableau-export --dataset=project.analytics --output-dir=./datasources

# Specify custom connection name
tableau-export project.analytics.fct_orders \
  --connection-name="Production Analytics"

# Override project ID for connection
tableau-export project.analytics.dim_customers \
  --project-id=my-production-project
```

**Examples:**

```bash
# Export all tables for a Tableau project
tableau-export --dataset=project.marts_marketing \
  --output-dir=./tableau/datasources \
  --connection-name="Marketing Data Warehouse"

# Export with specific project
tableau-export project.staging.stg_events \
  --project-id=analytics-prod-12345 \
  --output-dir=./staging-datasources
```

**Output:**

Generates `.tds` files that can be opened in Tableau Desktop or published to Tableau Server:

```xml
<datasource inline="true" name="fct_orders" version="18.1">
  <connection class="bigquery" dbname="project-id" schema="analytics" tablename="fct_orders" username="oauth">
    ...
  </connection>
  <column name="[order_id]" role="dimension" datatype="integer"/>
  <column name="[revenue]" role="measure" datatype="real"/>
  ...
</datasource>
```

---

### 3. bi-metadata-sync

Extract and sync metadata from BigQuery for BI tool integration.

**Features:**
- Extract table and column descriptions
- Generate metadata manifests
- Track documentation coverage
- Multiple output formats (JSON, YAML, CSV)
- Filter by documentation status

**Basic Usage:**

```bash
# Export metadata as JSON
bi-metadata-sync project.analytics --format=json --output=metadata.json

# Include full schema details
bi-metadata-sync project.analytics --include-schema --include-stats

# Export only documented tables
bi-metadata-sync project.analytics --only-documented

# Export as YAML for version control
bi-metadata-sync project.prod --format=yaml --output=metadata.yaml
```

**Examples:**

```bash
# Full metadata export with statistics
bi-metadata-sync project.marts \
  --include-schema \
  --include-stats \
  --format=json \
  --output=./metadata/marts-metadata.json

# Documentation coverage report
bi-metadata-sync project.analytics \
  --only-documented \
  --format=csv \
  --output=documentation-status.csv

# Lightweight metadata for BI tool import
bi-metadata-sync project.analytics --format=json | \
  jq '.tables[] | {name: .table_name, desc: .description}'
```

**Output:**

```json
{
  "dataset_id": "project.analytics",
  "description": "Core analytics tables",
  "extracted_at": "2024-01-15T10:30:00",
  "summary": {
    "total_tables": 25,
    "documented_tables": 20,
    "documentation_coverage": 80.0
  },
  "tables": [
    {
      "table_name": "fct_orders",
      "description": "Order fact table with daily grain",
      "columns": [
        {
          "name": "order_id",
          "type": "INTEGER",
          "description": "Unique order identifier"
        }
      ],
      "documentation_status": {
        "table_documented": true,
        "documented_columns": 15,
        "total_columns": 20,
        "documentation_coverage": 75.0
      }
    }
  ]
}
```

---

### 4. bi-usage-tracker

Track BigQuery table usage to understand BI dashboard dependencies.

**Features:**
- Query frequency analysis
- User activity tracking
- Data volume and cost analysis
- Performance metrics (query duration, bytes scanned)
- Identify most-used tables for BI optimization

**Basic Usage:**

```bash
# Analyze usage for the last 7 days
bi-usage-tracker project.analytics

# Extended analysis period
bi-usage-tracker project.analytics --days=30

# Export as JSON
bi-usage-tracker project.analytics \
  --format=json \
  --output=usage-report.json

# Show only top 10 most queried tables
bi-usage-tracker project.analytics --top=10

# Include user-level details
bi-usage-tracker project.analytics --include-users

# Filter by minimum query count
bi-usage-tracker project.analytics --min-queries=10 --days=7
```

**Examples:**

```bash
# Monthly usage report for capacity planning
bi-usage-tracker project.marts \
  --days=30 \
  --format=json \
  --output=monthly-usage.json

# Identify heavily-used tables (dashboard dependencies)
bi-usage-tracker project.analytics \
  --min-queries=100 \
  --days=7 \
  --top=20

# User activity analysis
bi-usage-tracker project.analytics \
  --include-users \
  --days=14 \
  --format=csv \
  --output=user-activity.csv

# Find unused tables (candidates for deprecation)
bi-usage-tracker project.staging --days=30 | \
  grep "query_count: 0"
```

**Output:**

```
BI Table Usage Report
Dataset: project.analytics
Period: Last 7 days
Analysis Time: 2024-01-15T10:30:00
================================================================================

Summary
  Tables Queried: 18
  Total Queries: 1,247
  Total Data Processed: 45.8 GB
  Most Queried: fct_orders

Table Usage Details
================================================================================

1. fct_orders
   Queries: 423 | Users: 12 | Data Processed: 18.5 GB
   Avg Query Duration: 1,250 ms | Avg Bytes/Query: 44.7 MB
   First Query: 2024-01-08T09:15:23 | Last Query: 2024-01-15T10:28:45
   Top Users: analyst@company.com, bi-service@company.com, dashboard@company.com

2. dim_customers
   Queries: 287 | Users: 8 | Data Processed: 3.2 GB
   Avg Query Duration: 450 ms | Avg Bytes/Query: 11.4 MB
   First Query: 2024-01-08T08:30:12 | Last Query: 2024-01-15T10:25:33
```

---

## Installation

### Prerequisites

```bash
# Python 3.7+
python3 --version

# Google Cloud SDK (authenticated)
gcloud auth application-default login

# Required Python packages
pip install google-cloud-bigquery
```

### Setup

1. Add tools to your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/decentclaude/bin/bi-tools"
```

2. Verify installation:

```bash
looker-export --help
tableau-export --help
bi-metadata-sync --help
bi-usage-tracker --help
```

### Optional: Install BI Platform SDKs

For advanced integrations:

```bash
# Looker SDK (for API operations)
pip install looker-sdk

# Tableau SDK (for Server operations)
pip install tableauserverclient

# YAML support (for metadata sync)
pip install pyyaml
```

---

## Common Workflows

### 1. Initial BI Setup: Export All Tables

```bash
# Export Looker views
looker-export --dataset=project.analytics \
  --output-dir=./looker-project/views \
  --include-measures

# Export Tableau datasources
tableau-export --dataset=project.analytics \
  --output-dir=./tableau-datasources \
  --connection-name="Analytics Warehouse"

# Export metadata for documentation
bi-metadata-sync project.analytics \
  --include-schema \
  --include-stats \
  --format=json \
  --output=./docs/analytics-metadata.json
```

### 2. Regular Metadata Sync

```bash
#!/bin/bash
# sync-bi-metadata.sh - Run daily to keep metadata in sync

DATASET="project.analytics"
DATE=$(date +%Y%m%d)

# Export current metadata
bi-metadata-sync $DATASET \
  --include-schema \
  --format=json \
  --output="./metadata/metadata-${DATE}.json"

# Generate updated Looker views for new tables
looker-export --dataset=$DATASET \
  --output-dir=./looker/views \
  --sql-table-name

# Commit to version control
git add metadata/ looker/
git commit -m "Update BI metadata - ${DATE}"
```

### 3. Dashboard Health Check

```bash
#!/bin/bash
# dashboard-health-check.sh

DATASET="project.analytics"

echo "Checking table usage..."
bi-usage-tracker $DATASET --days=7 --top=20

echo -e "\nChecking documentation coverage..."
bi-metadata-sync $DATASET --format=csv | \
  awk -F',' '{print $1, $3, $4, $5}' | column -t

echo -e "\nChecking for unused tables..."
bi-usage-tracker $DATASET --days=30 --min-queries=0 | \
  grep "query_count: 0"
```

### 4. BI Migration: Compare Before/After

```bash
# Before migration
bi-metadata-sync project.old_analytics \
  --format=json \
  --output=metadata-before.json

# After migration
bi-metadata-sync project.new_analytics \
  --format=json \
  --output=metadata-after.json

# Compare schemas
diff <(jq -S '.tables[].columns' metadata-before.json) \
     <(jq -S '.tables[].columns' metadata-after.json)
```

### 5. Cost Optimization

```bash
# Find expensive tables
bi-usage-tracker project.analytics \
  --days=30 \
  --format=json \
  --output=usage.json

# Analyze cost per table
jq -r '.tables[] |
  "\(.table_name): \(.total_bytes_processed_gb) GB, \(.query_count) queries, Cost: $\((.total_bytes_processed_gb * 0.005) | round * 100 / 100)"' \
  usage.json | \
  sort -t':' -k2 -rn | \
  head -20
```

---

## Integration with dbt/SQLMesh

### dbt Post-Hook

Add to `dbt_project.yml`:

```yaml
on-run-end:
  - "{{ export_to_looker() }}"

models:
  my_project:
    marts:
      +post-hook:
        - "{{ log('Exporting to BI tools...', info=True) }}"
```

### SQLMesh Hook

Add to your SQLMesh workflow:

```bash
# After successful SQLMesh run
sqlmesh run && \
  looker-export --dataset=project.marts --output-dir=./looker/views
```

---

## Troubleshooting

### Permission Errors

```bash
# Verify BigQuery permissions
bq ls project:dataset

# Re-authenticate
gcloud auth application-default login
```

### Missing Dependencies

```bash
# Install all required packages
pip install google-cloud-bigquery pyyaml

# Check Python version
python3 --version  # Should be 3.7+
```

### Empty Results

```bash
# Check if tables exist
bq ls project:dataset

# Verify query permissions
bq query "SELECT COUNT(*) FROM \`project.dataset.table\`"
```

### INFORMATION_SCHEMA Access

For `bi-usage-tracker`:

```bash
# Ensure you have JOBS_BY_PROJECT access
bq ls --jobs project:region-us
```

---

## Documentation Templates

A comprehensive BI dependencies documentation template is available at:

```
docs/templates/bi-dependencies.md
```

Use this template to document:
- Dashboard dependencies
- Data freshness requirements
- Performance metrics
- Incident response procedures
- Cost analysis

---

## Best Practices

### 1. Version Control

Always commit generated LookML and metadata to version control:

```bash
git add looker/views/*.view.lkml
git add metadata/*.json
git commit -m "Update BI exports - $(date +%Y-%m-%d)"
```

### 2. Automation

Set up scheduled jobs to sync metadata:

```bash
# crontab entry
0 2 * * * /path/to/sync-bi-metadata.sh
```

### 3. Documentation

Document all dashboards using the provided template:

```bash
cp docs/templates/bi-dependencies.md \
   docs/dashboards/my-dashboard.md
```

### 4. Monitoring

Track usage regularly to identify:
- Most critical tables (high query count)
- Cost hotspots (high data volume)
- Unused tables (candidates for deprecation)
- Performance issues (slow queries)

---

## Related Tools

These BI tools complement the existing data utilities:

- `bq-schema-diff` - Compare table schemas
- `bq-lineage` - Explore table dependencies
- `bq-partition-info` - Analyze partitioning
- `bq-query-cost` - Estimate query costs

---

## Support

For issues or feature requests, see the main project README.

**Useful Resources:**
- [Looker LookML Documentation](https://cloud.google.com/looker/docs/lookml)
- [Tableau TDS Reference](https://help.tableau.com/current/pro/desktop/en-us/connect_basic_connector_example.htm)
- [BigQuery INFORMATION_SCHEMA](https://cloud.google.com/bigquery/docs/information-schema-intro)
