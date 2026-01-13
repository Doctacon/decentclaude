# Common Workflows Tutorial

Hands-on tutorials for everyday data engineering tasks with DecentClaude.

## Table of Contents

1. [Daily Development Workflow](#daily-development-workflow)
2. [Query Development and Testing](#query-development-and-testing)
3. [Schema Change Management](#schema-change-management)
4. [Cost Optimization](#cost-optimization)
5. [Data Quality Validation](#data-quality-validation)
6. [dbt Development Workflow](#dbt-development-workflow)
7. [Production Deployment](#production-deployment)

---

## Daily Development Workflow

Your typical day working with data. All validation happens automatically.

### Morning: Review and Plan

**1. Check what changed overnight**

```bash
# See recent commits
git log --oneline --since="yesterday" -- "*.sql"

# Check schema changes
./bin/data-utils/bq-schema-diff project.dataset.prod_table project.dataset.staging_table
```

**2. Review data freshness**

Ask Claude:
```
Check the latest partition in project.dataset.events
```

Claude will query:
```sql
SELECT MAX(_PARTITIONTIME) as latest_partition
FROM project.dataset.events
```

### During the Day: Active Development

**3. Write a new query**

Just write SQL naturally in Claude Code:
```
Create a query to find the top 10 users by revenue in the last 7 days
```

The hook automatically validates syntax before running.

**4. Test the query**

Before running on production data:
```bash
# Estimate cost first
./bin/data-utils/bq-query-cost --file=new_query.sql

# If cost looks good, run it
```

Ask Claude to run the query, and validation happens automatically.

**5. Save the query**

```
Save this query to queries/revenue_analysis.sql
```

The `before-write` hook validates before saving.

### End of Day: Cleanup and Commit

**6. Run quality checks**

```
Run the data-quality-check hook
```

**7. Pre-commit validation**

```
Run the pre-commit-data hook
```

This validates:
- All SQL files
- dbt models (if any)
- No hardcoded secrets

**8. Commit and push**

```bash
git add .
git commit -m "Add revenue analysis query"
git push
```

---

## Query Development and Testing

Build complex queries with confidence.

### Step 1: Start Small

Begin with a simple version:

```
Create a query to get user counts by month from project.dataset.users
```

### Step 2: Check the Cost

Before running on full data:

```bash
./bin/data-utils/bq-query-cost --file=user_counts.sql
```

Output:
```
Estimated bytes processed: 1.2 GB
Estimated cost: $0.006 USD (Very Low)
✓ Safe to run
```

### Step 3: Test on Sample

Modify to test on small sample:

```sql
-- Add LIMIT for testing
SELECT
  DATE_TRUNC(created_at, MONTH) as month,
  COUNT(*) as user_count
FROM project.dataset.users
WHERE created_at >= '2024-01-01'
GROUP BY 1
ORDER BY 1 DESC
LIMIT 100  -- Remove in production
```

### Step 4: Validate Results

Add validation checks:

```sql
WITH monthly_counts AS (
  SELECT
    DATE_TRUNC(created_at, MONTH) as month,
    COUNT(*) as user_count
  FROM project.dataset.users
  WHERE created_at >= '2024-01-01'
  GROUP BY 1
)
SELECT
  *,
  -- Validation: Check for unexpected gaps
  CASE
    WHEN user_count = 0 THEN 'WARN: Zero users'
    WHEN user_count < LAG(user_count) OVER (ORDER BY month) * 0.5
      THEN 'WARN: Significant drop'
    ELSE 'OK'
  END as quality_check
FROM monthly_counts
ORDER BY month DESC
```

### Step 5: Optimize and Finalize

Remove LIMIT, optimize:

```sql
-- Final optimized version
SELECT
  DATE_TRUNC(created_at, MONTH) as month,
  COUNT(*) as user_count,
  COUNT(DISTINCT user_id) as unique_users
FROM project.dataset.users
WHERE
  created_at >= '2024-01-01'
  AND _PARTITIONTIME >= '2024-01-01'  -- Partition filter
GROUP BY 1
ORDER BY 1 DESC
```

Verify cost improved:
```bash
./bin/data-utils/bq-query-cost --file=user_counts_optimized.sql
```

---

## Schema Change Management

Handle schema changes safely.

### Scenario: Adding a New Column

**1. Check current schema**

```bash
./bin/data-utils/bq-schema-diff project.dataset.table_current project.dataset.table_current
```

**2. Plan the change**

Ask Claude:
```
Help me add a new column 'user_segment' to project.dataset.users
```

**3. Check impact**

```bash
# Find what depends on this table
./bin/data-utils/bq-lineage project.dataset.users --direction=downstream
```

Output shows:
```
Downstream dependencies (3):
  - project.dataset.user_analytics
  - project.dataset.revenue_report
  - project.dataset.user_summary
```

**4. Test in staging**

```sql
-- Add column in staging
ALTER TABLE project.dataset_staging.users
ADD COLUMN user_segment STRING
```

**5. Verify schema diff**

```bash
./bin/data-utils/bq-schema-diff project.dataset.users project.dataset_staging.users
```

Output:
```
Fields only in table B:
  - user_segment (STRING)

Summary: 1 field(s) added, 0 removed, 0 changed
```

**6. Update downstream dependencies**

For each dependent table, check if changes needed:

```
Review project.dataset.user_analytics to see if it needs the new user_segment column
```

**7. Deploy to production**

After testing:
```sql
ALTER TABLE project.dataset.users
ADD COLUMN user_segment STRING
```

### Scenario: Changing Column Type

**DANGER ZONE** - This breaks existing queries!

**1. Check dependencies first**

```bash
./bin/data-utils/bq-lineage project.dataset.table --direction=downstream
```

**2. Search for column usage**

Ask Claude:
```
Search all SQL files for references to user_id column
```

**3. Plan migration**

Instead of changing type in-place:
1. Add new column with new type
2. Backfill data
3. Update queries to use new column
4. Deprecate old column
5. Eventually drop old column

**4. Create migration plan**

```sql
-- Step 1: Add new column
ALTER TABLE project.dataset.users
ADD COLUMN user_id_new INT64;

-- Step 2: Backfill
UPDATE project.dataset.users
SET user_id_new = CAST(user_id_old AS INT64)
WHERE user_id_new IS NULL;

-- Step 3: Validate
SELECT
  COUNT(*) as total,
  COUNT(user_id_old) as old_count,
  COUNT(user_id_new) as new_count,
  COUNT(*) - COUNT(user_id_new) as missing_new
FROM project.dataset.users;
```

---

## Cost Optimization

Reduce your BigQuery spending.

### Workflow: Find and Fix Expensive Queries

**1. Identify expensive patterns**

```bash
# Check a suspicious query
./bin/data-utils/bq-query-cost --file=daily_report.sql
```

Output:
```
Estimated bytes processed: 450 GB
Estimated cost: $2.25 USD (High)
⚠ Warning: High cost query
```

**2. Analyze partition usage**

```bash
./bin/data-utils/bq-partition-info project.dataset.events
```

Output shows which partitions are largest.

**3. Add partition filter**

Before:
```sql
SELECT user_id, COUNT(*) as event_count
FROM project.dataset.events
GROUP BY 1
```

After:
```sql
SELECT user_id, COUNT(*) as event_count
FROM project.dataset.events
WHERE
  -- Add partition filter
  _PARTITIONTIME >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY 1
```

**4. Verify improvement**

```bash
./bin/data-utils/bq-query-cost --file=daily_report_optimized.sql
```

Output:
```
Estimated bytes processed: 15 GB
Estimated cost: $0.075 USD (Low)
✓ Cost reduced by 96.7%
```

### Workflow: Optimize Table Design

**1. Check current partitioning**

```bash
./bin/data-utils/bq-partition-info project.dataset.large_table
```

**2. Analyze query patterns**

Ask Claude:
```
Analyze queries in queries/ directory to find common filters
```

**3. Add clustering**

If queries commonly filter by user_id and event_type:

```sql
-- Recreate table with clustering
CREATE OR REPLACE TABLE project.dataset.large_table
PARTITION BY DATE(timestamp)
CLUSTER BY user_id, event_type
AS SELECT * FROM project.dataset.large_table_backup
```

**4. Compare costs**

```bash
# Before clustering
./bin/data-utils/bq-query-cost "SELECT * FROM project.dataset.large_table_backup WHERE user_id = '12345'"

# After clustering
./bin/data-utils/bq-query-cost "SELECT * FROM project.dataset.large_table WHERE user_id = '12345'"
```

---

## Data Quality Validation

Ensure data quality throughout development.

### Daily Quality Checks

**1. Run automated checks**

```
Run the data-quality-check hook
```

**2. Check for common issues**

Ask Claude to create quality check queries:
```
Create a data quality check query for project.dataset.orders that validates:
- No null order_ids
- Order amounts are positive
- Dates are not in the future
- No duplicate orders
```

Output:
```sql
WITH quality_checks AS (
  SELECT
    'Null order_ids' as check_name,
    COUNT(*) as failures
  FROM project.dataset.orders
  WHERE order_id IS NULL

  UNION ALL

  SELECT
    'Negative amounts' as check_name,
    COUNT(*) as failures
  FROM project.dataset.orders
  WHERE amount < 0

  UNION ALL

  SELECT
    'Future dates' as check_name,
    COUNT(*) as failures
  FROM project.dataset.orders
  WHERE order_date > CURRENT_DATE()

  UNION ALL

  SELECT
    'Duplicate orders' as check_name,
    COUNT(*) - COUNT(DISTINCT order_id) as failures
  FROM project.dataset.orders
)
SELECT
  *,
  CASE WHEN failures > 0 THEN '❌ FAIL' ELSE '✅ PASS' END as status
FROM quality_checks
ORDER BY failures DESC
```

### Custom Quality Checks

**1. Edit the quality check script**

```bash
# Open in editor
nano scripts/data_quality.py
```

**2. Add custom check**

```python
class RevenueConsistencyCheck(DataQualityCheck):
    def __init__(self):
        super().__init__("Revenue Consistency")

    def run(self) -> bool:
        # Your validation logic
        # Example: Check if daily revenue is within expected range
        query = """
        SELECT
          DATE(order_date) as date,
          SUM(amount) as daily_revenue
        FROM project.dataset.orders
        WHERE order_date >= CURRENT_DATE() - 7
        GROUP BY 1
        HAVING daily_revenue < 1000 OR daily_revenue > 1000000
        """

        # Run query and check results
        # (Implementation depends on your setup)

        self.passed = True  # or False if check fails
        self.message = "Daily revenue within expected range"
        return self.passed

# Add to check list
checks = [
    NullCheck(),
    DuplicateCheck(),
    RevenueConsistencyCheck(),  # Your new check
]
```

**3. Test the check**

```
Run the data-quality-check hook
```

---

## dbt Development Workflow

Streamlined dbt development with automatic validation.

### Setup

**1. Initialize dbt project** (one-time)

```bash
dbt init my_project
cd my_project
```

**2. Configure profile**

The setup wizard already created `~/.dbt/profiles.yml`.

### Daily Development

**1. Create a new model**

```
Create a dbt model that aggregates user events by day
```

Claude creates:
```sql
-- models/marts/daily_user_events.sql
{{
  config(
    materialized='incremental',
    partition_by={
      "field": "event_date",
      "data_type": "date",
      "granularity": "day"
    }
  )
}}

WITH events AS (
  SELECT * FROM {{ ref('stg_events') }}
  {% if is_incremental() %}
  WHERE event_date > (SELECT MAX(event_date) FROM {{ this }})
  {% endif %}
)

SELECT
  event_date,
  user_id,
  COUNT(*) as event_count,
  COUNT(DISTINCT session_id) as session_count
FROM events
GROUP BY 1, 2
```

**2. Compile to check syntax**

```
Run the dbt-compile hook
```

This automatically:
- Compiles all models
- Shows any Jinja errors
- Validates SQL syntax

**3. Add tests**

Create `models/marts/daily_user_events.yml`:
```yaml
version: 2

models:
  - name: daily_user_events
    description: Daily aggregation of user events
    columns:
      - name: event_date
        description: Date of events
        tests:
          - not_null
      - name: user_id
        description: User identifier
        tests:
          - not_null
      - name: event_count
        description: Number of events
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"
```

**4. Run tests**

```
Run the dbt-test hook
```

**5. Build incrementally**

```
Run dbt run --select daily_user_events
```

### Before Committing

**1. Full validation**

```
Run the pre-commit-data hook
```

This runs:
- dbt compile (all models)
- SQL validation
- Secret detection

**2. Run full test suite**

```
Run the dbt-test hook
```

**3. Commit**

```bash
git add models/marts/daily_user_events.sql
git add models/marts/daily_user_events.yml
git commit -m "Add daily user events mart"
```

---

## Production Deployment

Safe deployment to production.

### Pre-deployment Checklist

**1. Validate all changes**

```
Run the pre-commit-data hook
```

**2. Check dependencies**

For each changed table:
```bash
./bin/data-utils/bq-lineage project.dataset.changed_table
```

**3. Estimate costs**

For new queries:
```bash
./bin/data-utils/bq-query-cost --file=new_query.sql
```

**4. Schema compatibility**

If schema changed:
```bash
./bin/data-utils/bq-schema-diff project.dataset.table_prod project.dataset.table_staging
```

### Deployment Steps

**1. Deploy to staging**

```bash
# dbt
dbt run --target staging

# Or run specific models
dbt run --select +new_model+ --target staging
```

**2. Validate staging**

```sql
-- Compare row counts
SELECT 'staging' as env, COUNT(*) as row_count
FROM project.dataset_staging.table
UNION ALL
SELECT 'prod' as env, COUNT(*) as row_count
FROM project.dataset_prod.table
```

**3. Run full test suite**

```
Run the dbt-test hook on staging
```

**4. Deploy to production**

```bash
dbt run --target prod --select +new_model+
```

**5. Validate production**

```
Check that project.dataset_prod.new_model has data
```

**6. Monitor**

Set up monitoring queries:
```sql
-- Check freshness
SELECT MAX(updated_at) as last_update
FROM project.dataset_prod.new_model

-- Check volume
SELECT COUNT(*) as row_count
FROM project.dataset_prod.new_model
WHERE DATE(updated_at) = CURRENT_DATE()
```

### Rollback Procedure

If something goes wrong:

**1. Check what changed**

```bash
./bin/data-utils/bq-schema-diff project.dataset.table_prod project.dataset.table_backup
```

**2. Restore from backup**

```sql
CREATE OR REPLACE TABLE project.dataset.table_prod
AS SELECT * FROM project.dataset.table_backup
```

**3. Verify restoration**

```bash
./bin/data-utils/bq-schema-diff project.dataset.table_prod project.dataset.table_backup
```

Should show no differences.

---

## Tips and Best Practices

### General Tips

1. **Always estimate cost first** - Use `bq-query-cost` before running expensive queries
2. **Check dependencies** - Use `bq-lineage` before modifying tables
3. **Test in staging** - Never deploy directly to production
4. **Use the hooks** - Let automatic validation catch errors early
5. **Document as you go** - Add comments to complex queries

### Performance Tips

1. **Use partition filters** - Always include `_PARTITIONTIME` filters
2. **Limit scanned data** - Use `WHERE` clauses to reduce data scanned
3. **Cluster frequently filtered columns** - Use `CLUSTER BY` for common filters
4. **Avoid SELECT *** - Specify only needed columns
5. **Use appropriate materializations** - Views for simple transforms, tables for complex ones

### Quality Tips

1. **Add tests** - dbt tests catch regressions
2. **Validate assumptions** - Add quality check queries
3. **Monitor freshness** - Check latest partition regularly
4. **Check for nulls** - Validate critical fields aren't null
5. **Compare environments** - Use schema diff between staging/prod

### Collaboration Tips

1. **Use descriptive names** - Table and column names should be self-documenting
2. **Add YAML documentation** - Document models and columns
3. **Share playbooks** - Document common patterns
4. **Code review** - Review SQL changes like code
5. **Version control everything** - Git commit all SQL and config

---

## Next Steps

Master these workflows, then explore:

1. **Advanced Patterns** - See `data-engineering-patterns.md`
2. **Comprehensive Playbooks** - See `playbooks.md`
3. **Custom Hooks** - Create your own validation rules
4. **Team Processes** - Adapt workflows for your team

Happy data engineering! 🚀
