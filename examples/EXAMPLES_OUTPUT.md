# Example SQL Query Outputs

This document shows actual outputs from running the example SQL queries against real BigQuery data.

## Files Overview

### Template Files (Use as starting points)
- `valid_query.sql` - Template with placeholder table names
- `data_quality.sql` - Template for data quality checks
- `dbt_model_example.sql` - dbt model template
- `sqlmesh_model_example.sql` - SQLMesh model template

### Working Examples (Run directly against BigQuery)
- `valid_query_working.sql` - Uses actual Salesforce user table
- `data_quality_working.sql` - Data quality checks on real data

## Example Outputs

### valid_query_working.sql

**Query**: Basic user signup query with window functions

**Output** (First 10 rows):
```
user_id              email                           created_date              signup_date  daily_signups
-------------------  ----------------------------  ----------------------  -------------  ---------------
005Uw00000PlnGcIAJ   ricardo.drumond@harness.io    2026-01-12T03:56:28Z    2026-01-12                 2
005Uw00000PlnRtIAJ   dominick.biocchi@harness.io   2026-01-12T03:56:28Z    2026-01-12                 2
005Uw00000PhL7dIAF   c_dan.kearney@harness.io      2026-01-09T20:57:56Z    2026-01-09                 7
005Uw00000PhL4PIAV   c_deserae.smith@harness.io    2026-01-09T20:57:56Z    2026-01-09                 7
005Uw00000PhL61IAF   c_christopher.boland@...      2026-01-09T20:57:56Z    2026-01-09                 7
```

**What it demonstrates**:
- Proper SQL formatting
- Window functions (COUNT OVER PARTITION)
- Date functions (DATE())
- Filtering and ordering
- Column aliasing

**How to use**:
```bash
# Run via BigQuery MCP
claude validate_sql --file examples/sql/valid_query_working.sql

# Or copy/paste into BigQuery console
```

### data_quality_working.sql

**Query**: Comprehensive data quality checks

**Output**:
```
check_name         failure_count  status
-----------------  -------------  ------
stale_records                540  FAIL
invalid_dates                  0  PASS
duplicate_users                0  PASS
null_emails                    0  PASS
```

**What it demonstrates**:
- Multiple quality checks in one query
- UNION ALL for combining check results
- Conditional logic (CASE statements)
- Null checking
- Duplicate detection
- Date range validation
- Staleness detection

**How to use**:
```bash
# Run and save results
claude run_query --file examples/sql/data_quality_working.sql > results.txt
```

## Template Files Usage

### valid_query.sql

Replace the placeholder values:
```sql
-- BEFORE (template):
FROM `project.dataset.users`

-- AFTER (your table):
FROM `your-project.your-dataset.your-users-table`
```

### data_quality.sql

Customize for your schema:
```sql
-- BEFORE:
FROM `project.dataset.users`
WHERE email IS NULL

-- AFTER:
FROM `your-project.your-dataset.customers`
WHERE email IS NULL OR email = ''
```

## dbt Model Example

The `dbt_model_example.sql` file shows a production-ready dbt model with:

**Features**:
- Model configuration (materialization, partitioning, clustering)
- Source and ref functions for dependencies
- CTEs for readable transformations
- Business logic (user lifecycle stages)
- Window functions for calculations

**How to use**:
1. Copy to your dbt project's models directory
2. Update source/ref names to match your project
3. Run `dbt compile` to validate
4. Run `dbt run` to execute

**Testing**:
```bash
# Compile without running
dbt compile --select dbt_model_example

# Run the model
dbt run --select dbt_model_example

# Run with full refresh
dbt run --select dbt_model_example --full-refresh
```

## SQLMesh Model Example

The `sqlmesh_model_example.sql` file demonstrates SQLMesh-specific features:

**Features**:
- MODEL() configuration block
- Incremental processing by time range
- Grain specification for deduplication
- Event aggregation and pivoting
- Running window calculations
- Engagement scoring logic

**How to use**:
1. Copy to your SQLMesh project's models directory
2. Update model name and dependencies
3. Run `sqlmesh plan` to validate
4. Run `sqlmesh run` to execute

**Testing**:
```bash
# Validate the model
sqlmesh plan

# Run with specific date range
sqlmesh run --start-date 2024-01-01 --end-date 2024-01-31

# Test the model
sqlmesh test
```

## Best Practices Demonstrated

### 1. Consistent Formatting
All SQL uses:
- Uppercase keywords (SELECT, FROM, WHERE)
- Indented subqueries and CTEs
- Aligned column names
- Clear line breaks

### 2. Performance Optimization
- Date range filters to limit data scanned
- Partitioning configuration
- Clustering on frequently filtered columns
- Window functions over self-joins

### 3. Maintainability
- Descriptive column names
- Comments explaining business logic
- CTEs to break down complex queries
- Explicit column selection (no SELECT *)

### 4. Data Quality
- NULL handling
- Duplicate detection
- Date validation
- Staleness checks

## Running the Examples

### Using BigQuery MCP

```bash
# Validate syntax without executing
claude validate_sql "$(cat examples/sql/valid_query_working.sql)"

# Run query and get results
claude run_query "$(cat examples/sql/data_quality_working.sql)"

# Estimate query cost
claude estimate_query_cost "$(cat examples/sql/valid_query_working.sql)"
```

### Using BigQuery Console

1. Open [BigQuery Console](https://console.cloud.google.com/bigquery)
2. Click "Compose New Query"
3. Copy/paste SQL from example files
4. Click "Run" or use Ctrl+Enter

### Using bq Command Line

```bash
# Run query and save to table
bq query --use_legacy_sql=false < examples/sql/valid_query_working.sql

# Dry run to validate
bq query --dry_run --use_legacy_sql=false < examples/sql/data_quality_working.sql
```

## Extending the Examples

### Add Custom Quality Checks

```sql
-- Add to data_quality_working.sql:
UNION ALL

SELECT
  'future_dates' AS check_name,
  COUNT(*) AS failure_count
FROM `segment-warehouse-236622.salesforce_v4.user`
WHERE created_date > CURRENT_TIMESTAMP()
```

### Create Your Own Examples

1. Start with a template file
2. Replace table names with your schema
3. Add business-specific logic
4. Test with sample data
5. Document the output
6. Add to version control

## Troubleshooting

### Common Issues

**Error: Table not found**
- Check project, dataset, and table names
- Verify access permissions
- Use backticks around table references

**Error: Syntax error**
- Validate SQL using `validate_sql` tool
- Check for missing commas or parentheses
- Ensure proper quoting

**Error: Exceeded quota**
- Add LIMIT clause for testing
- Use date range filters
- Check query cost before running

## Additional Resources

- [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql)
- [dbt Documentation](https://docs.getdbt.com/)
- [SQLMesh Documentation](https://sqlmesh.readthedocs.io/)
- [SQL Style Guide](https://www.sqlstyle.guide/)
