# Data Engineering Playbooks

Step-by-step workflows for common data engineering tasks. These playbooks provide concrete actions, commands, and decision trees for handling routine and exceptional scenarios.

## Table of Contents

1. [New Table Migration](#new-table-migration)
2. [Schema Evolution](#schema-evolution)
3. [Backfill Patterns](#backfill-patterns)
4. [Incident Response](#incident-response)

---

## New Table Migration

### Overview
Workflow for adding a new table to your data warehouse, including modeling, testing, and deployment.

### Prerequisites
- Access to BigQuery project
- dbt or SQLMesh environment configured
- Source data schema defined

### Workflow Steps

#### 1. Design Phase (30-60 minutes)

**a. Define Requirements**
```bash
# Document in your issue tracker or design doc:
# - Business purpose and use case
# - Expected query patterns
# - Data freshness requirements (real-time, hourly, daily, weekly)
# - Estimated row volume and growth rate
# - Data retention policy
```

**b. Choose Partitioning Strategy**
```sql
-- Decision tree:
-- Daily volume > 1M rows? → Consider partitioning
-- Queries filter by date 90%+ of time? → Partition by date
-- Queries filter by category/region? → Consider clustering
-- Need to enforce retention? → Use partition expiration

-- Example: Time-based partitioning
PARTITION BY DATE(_PARTITIONTIME)
OPTIONS(
  partition_expiration_days = 365,
  require_partition_filter = true
)
```

**c. Choose Clustering Strategy**
```sql
-- Use clustering when:
-- - High cardinality columns frequently in WHERE/JOIN
-- - Queries commonly filter on 2-4 specific columns
-- - Want better cost/performance without partition overhead

-- Example:
CLUSTER BY user_id, event_type
```

#### 2. Implementation Phase (dbt)

**a. Create Model File**
```bash
# Naming convention: <source>__<entity>.sql
touch models/staging/stg_analytics__user_events.sql
```

**b. Write Model**
```sql
-- models/staging/stg_analytics__user_events.sql
{{
  config(
    materialized='incremental',
    partition_by={
      "field": "event_timestamp",
      "data_type": "timestamp",
      "granularity": "day"
    },
    cluster_by=["user_id", "event_type"],
    incremental_strategy='insert_overwrite',
    on_schema_change='fail'
  )
}}

with source as (
  select * from {{ source('analytics', 'raw_events') }}
  {% if is_incremental() %}
  where event_timestamp >= _dbt_max_partition
  {% endif %}
),

cleaned as (
  select
    event_id,
    user_id,
    event_type,
    event_timestamp,
    event_properties,
    -- Data quality transformations
    case
      when event_type is null then 'unknown'
      else lower(trim(event_type))
    end as event_type_clean
  from source
)

select * from cleaned
```

**c. Add Tests**
```yaml
# models/staging/schema.yml
version: 2

models:
  - name: stg_analytics__user_events
    description: Cleaned and standardized user events
    columns:
      - name: event_id
        description: Unique event identifier
        tests:
          - unique
          - not_null
      - name: user_id
        description: User who triggered event
        tests:
          - not_null
          - relationships:
              to: ref('stg_users')
              field: user_id
      - name: event_timestamp
        description: When event occurred
        tests:
          - not_null
          - dbt_utils.recency:
              datepart: day
              field: event_timestamp
              interval: 7
```

**d. Run and Test Locally**
```bash
# Test on subset
dbt run --select stg_analytics__user_events --vars '{"limit": 1000}'

# Run full model
dbt run --select stg_analytics__user_events

# Run tests
dbt test --select stg_analytics__user_events

# Check row counts
dbt run-operation query --args '{sql: "select count(*) from {{ ref(\"stg_analytics__user_events\") }}"}'
```

#### 3. Implementation Phase (SQLMesh)

**a. Create Model File**
```bash
touch models/staging/stg_analytics__user_events.sql
```

**b. Write Model**
```sql
-- models/staging/stg_analytics__user_events.sql
MODEL (
  name staging.stg_analytics__user_events,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column event_timestamp,
    batch_size 1
  ),
  owner data_eng,
  cron '@daily',
  grain (event_id, event_timestamp),
  audits (
    not_null(columns := (event_id, user_id, event_timestamp)),
    unique_values(columns := (event_id))
  ),
  partitioned_by (DATE(event_timestamp)),
  clustered_by (user_id, event_type)
);

SELECT
  event_id,
  user_id,
  event_type,
  event_timestamp,
  event_properties,
  CASE
    WHEN event_type IS NULL THEN 'unknown'
    ELSE LOWER(TRIM(event_type))
  END AS event_type_clean
FROM analytics.raw_events
WHERE event_timestamp BETWEEN @start_date AND @end_date
```

**c. Test Model**
```bash
# Plan changes
sqlmesh plan

# Run for specific date range
sqlmesh run --start-date 2024-01-01 --end-date 2024-01-31

# Validate audits
sqlmesh audit
```

#### 4. Validation Phase

**a. Data Quality Checks**
```sql
-- Check row counts match source
SELECT
  'source' as source,
  COUNT(*) as row_count,
  MIN(event_timestamp) as min_date,
  MAX(event_timestamp) as max_date
FROM analytics.raw_events
UNION ALL
SELECT
  'target' as source,
  COUNT(*) as row_count,
  MIN(event_timestamp) as min_date,
  MAX(event_timestamp) as max_date
FROM staging.stg_analytics__user_events;

-- Check for duplicates
SELECT
  event_id,
  COUNT(*) as duplicate_count
FROM staging.stg_analytics__user_events
GROUP BY event_id
HAVING COUNT(*) > 1;

-- Check null rates
SELECT
  COUNTIF(event_id IS NULL) / COUNT(*) as event_id_null_rate,
  COUNTIF(user_id IS NULL) / COUNT(*) as user_id_null_rate,
  COUNTIF(event_timestamp IS NULL) / COUNT(*) as timestamp_null_rate
FROM staging.stg_analytics__user_events;
```

**b. Performance Validation**
```sql
-- Check partition pruning works
-- Should scan only 1 day of data
SELECT COUNT(*)
FROM staging.stg_analytics__user_events
WHERE DATE(event_timestamp) = '2024-01-15'
-- Check bytes processed in query results

-- Check clustering effectiveness
SELECT user_id, event_type, COUNT(*) as event_count
FROM staging.stg_analytics__user_events
WHERE DATE(event_timestamp) = '2024-01-15'
  AND user_id = 'test-user-123'
GROUP BY user_id, event_type
-- Should scan minimal bytes due to clustering
```

#### 5. Deployment Phase

**a. Deploy to Production**
```bash
# dbt
dbt run --select stg_analytics__user_events --target prod
dbt test --select stg_analytics__user_events --target prod

# SQLMesh
sqlmesh plan --environment prod
sqlmesh run --environment prod
```

**b. Set up Monitoring**
```sql
-- Create monitoring view
CREATE OR REPLACE VIEW monitoring.user_events_health AS
SELECT
  DATE(event_timestamp) as event_date,
  COUNT(*) as row_count,
  COUNT(DISTINCT user_id) as unique_users,
  COUNTIF(event_id IS NULL) as null_event_ids,
  COUNTIF(user_id IS NULL) as null_user_ids,
  MIN(event_timestamp) as min_timestamp,
  MAX(event_timestamp) as max_timestamp
FROM staging.stg_analytics__user_events
WHERE DATE(event_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY event_date
ORDER BY event_date DESC;
```

**c. Document**
```markdown
# Update data catalog or wiki with:
- Table purpose and business use case
- Refresh schedule
- Primary consumers/stakeholders
- Known limitations or edge cases
- Example queries
- Contact for questions
```

### Rollback Plan

If issues are found post-deployment:

```bash
# dbt - revert to previous model version
git revert <commit-hash>
dbt run --select stg_analytics__user_events --target prod

# SQLMesh - use virtual environments
sqlmesh plan --environment prod --rollback
```

---

## Schema Evolution

### Overview
Workflow for safely modifying existing table schemas without breaking downstream dependencies.

### Common Change Types

1. **Adding a column** (low risk)
2. **Removing a column** (medium risk)
3. **Renaming a column** (high risk)
4. **Changing data type** (high risk)
5. **Changing partitioning** (requires recreation)

### Workflow Steps

#### 1. Impact Analysis

**a. Find Downstream Dependencies**
```sql
-- BigQuery: Find views that reference your table
SELECT
  table_name,
  view_definition
FROM `project.dataset.INFORMATION_SCHEMA.VIEWS`
WHERE view_definition LIKE '%your_table_name%';

-- Find downstream models in dbt
dbt list --select +your_model --output json
```

**b. Search for Direct References**
```bash
# Search codebase for table references
grep -r "your_table_name" models/
grep -r "your_table_name" analyses/
grep -r "your_table_name" macros/

# Check for column references
grep -r "column_to_change" models/
```

**c. Identify Stakeholders**
```bash
# Check git history for recent contributors
git log --pretty=format:"%an" -- models/your_model.sql | sort | uniq

# Review documentation for listed owners
cat models/schema.yml | grep -A 5 "name: your_model"
```

#### 2. Change Implementation by Type

### Adding a Column (Low Risk)

**Step 1: Update Model**
```sql
-- Add new column with default/null handling
select
  existing_column_1,
  existing_column_2,
  -- New column
  coalesce(new_column, 'default_value') as new_column_clean
from source_table
```

**Step 2: Update Tests**
```yaml
# schema.yml
- name: new_column_clean
  description: Description of new column
  tests:
    - not_null
    - accepted_values:
        values: ['value1', 'value2']
```

**Step 3: Deploy**
```bash
# Run incrementally if possible
dbt run --select your_model

# Or full refresh if adding to partition key
dbt run --select your_model --full-refresh
```

### Removing a Column (Medium Risk)

**Step 1: Verify No Dependencies**
```bash
# Confirm no downstream models reference it
grep -r "column_to_remove" models/

# Check if in any tests
grep -r "column_to_remove" tests/
```

**Step 2: Two-Phase Rollout**

*Phase 1: Stop Populating*
```sql
-- Comment out or mark as deprecated
select
  existing_column_1,
  existing_column_2,
  -- DEPRECATED: column_to_remove will be removed 2024-02-01
  -- null as column_to_remove
from source_table
```

**Deploy and monitor for 1-2 weeks**

*Phase 2: Remove Column*
```sql
-- Remove from query entirely
select
  existing_column_1,
  existing_column_2
from source_table
```

### Renaming a Column (High Risk)

**Step 1: Three-Phase Rollout**

*Phase 1: Duplicate Column*
```sql
select
  existing_column,
  existing_column as new_column_name  -- Add new name
from source_table
```

*Phase 2: Migrate Downstream (1-2 weeks)*
- Update all downstream models to use new_column_name
- Update tests and documentation
- Notify stakeholders

*Phase 3: Remove Old Column*
```sql
select
  new_column_name  -- Remove old name
from source_table
```

### Changing Data Type (High Risk)

**Example: String to Integer**

**Step 1: Add New Typed Column**
```sql
select
  user_id,  -- Original string column
  safe_cast(user_id as int64) as user_id_int,  -- New typed column
  case
    when safe_cast(user_id as int64) is null and user_id is not null
    then user_id
  end as user_id_cast_failures  -- Track bad data
from source_table
```

**Step 2: Monitor Cast Failures**
```sql
select
  count(*) as total_rows,
  countif(user_id_cast_failures is not null) as failed_casts,
  countif(user_id_cast_failures is not null) / count(*) as failure_rate
from your_table
```

**Step 3: If failure rate acceptable (<0.1%), proceed with migration**
- Follow rename column workflow above
- Or use dual-column approach permanently

### Changing Partitioning (Requires Recreation)

**Step 1: Create New Table with New Partitioning**
```sql
-- SQLMesh
MODEL (
  name staging.stg_user_events_v2,  -- New version
  kind FULL,
  partitioned_by (DATE(event_timestamp), user_region)  -- New partition scheme
);

-- dbt
{{
  config(
    materialized='table',
    partition_by={
      "field": "event_timestamp",
      "data_type": "timestamp",
      "granularity": "day"
    },
    cluster_by=["user_region", "event_type"]  -- Updated clustering
  )
}}
```

**Step 2: Backfill Historical Data**
```bash
# Use backfill workflow (see Backfill Patterns section)
dbt run --select stg_user_events_v2 --full-refresh
```

**Step 3: Cutover**
```sql
-- Swap tables atomically
-- 1. Rename old table to backup
ALTER TABLE staging.stg_user_events RENAME TO stg_user_events_backup;

-- 2. Rename new table to production name
ALTER TABLE staging.stg_user_events_v2 RENAME TO stg_user_events;

-- 3. Monitor for 24-48 hours, then drop backup
-- DROP TABLE staging.stg_user_events_backup;
```

#### 3. Testing Schema Changes

**a. Unit Tests**
```bash
# Run on dev environment first
dbt run --select your_model --target dev
dbt test --select your_model --target dev
```

**b. Integration Tests**
```bash
# Run downstream models
dbt run --select your_model+ --target dev

# Compare row counts before/after
dbt run-operation compare_row_counts --args '{
  "old_table": "staging.your_model_backup",
  "new_table": "staging.your_model"
}'
```

**c. Validation Queries**
```sql
-- Compare aggregates between old and new versions
WITH old_data AS (
  SELECT
    DATE(timestamp_col) as date,
    COUNT(*) as row_count,
    SUM(metric) as total_metric
  FROM staging.your_model_backup
  GROUP BY date
),
new_data AS (
  SELECT
    DATE(timestamp_col) as date,
    COUNT(*) as row_count,
    SUM(metric) as total_metric
  FROM staging.your_model
  GROUP BY date
)
SELECT
  COALESCE(o.date, n.date) as date,
  o.row_count as old_row_count,
  n.row_count as new_row_count,
  o.total_metric as old_metric,
  n.total_metric as new_metric,
  ABS(o.row_count - n.row_count) as row_count_diff,
  ABS(o.total_metric - n.total_metric) as metric_diff
FROM old_data o
FULL OUTER JOIN new_data n USING (date)
WHERE ABS(o.row_count - n.row_count) > 0
   OR ABS(o.total_metric - n.total_metric) > 0.01
ORDER BY date DESC;
```

#### 4. Communication Plan

**For Medium/High Risk Changes**

```markdown
# Schema Change Notification Template

**Table**: staging.user_events
**Change Type**: Renaming column `user_type` to `user_segment`
**Planned Date**: 2024-02-01
**Risk Level**: High

## What's Changing
The column `user_type` is being renamed to `user_segment` for consistency with other tables.

## Timeline
- 2024-01-25: Phase 1 - Both columns available
- 2024-01-25 - 2024-02-01: Migration period - update your queries
- 2024-02-01: Phase 2 - Old column removed

## Action Required
If you query this table directly:
1. Update references from `user_type` to `user_segment`
2. Test in dev environment
3. Notify #data-eng when complete

## Downstream Impact
The following dbt models are affected and will be updated by data eng:
- models/marts/user_segments.sql
- models/reports/weekly_cohorts.sql

## Questions?
Contact: @data-eng-team or #data-eng-support
```

#### 5. Rollback Procedures

**Quick Rollback (Within 24 Hours)**
```bash
# Revert code changes
git revert <schema-change-commit>

# Redeploy old version
dbt run --select your_model --full-refresh --target prod
```

**Extended Rollback (After 24 Hours)**
```sql
-- Restore from backup table
CREATE OR REPLACE TABLE staging.your_model AS
SELECT * FROM staging.your_model_backup;

-- Or restore from time travel (within 7 days)
CREATE OR REPLACE TABLE staging.your_model AS
SELECT * FROM staging.your_model
FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 DAY);
```

---

## Backfill Patterns

### Overview
Workflows for backfilling historical data, whether for new models, bug fixes, or schema changes.

### Common Backfill Scenarios

1. **Initial backfill** - New table needs historical data
2. **Bug fix backfill** - Correct data quality issue
3. **Schema change backfill** - Rebuild with new structure
4. **Incremental catch-up** - Fill gaps in incremental model

### Pattern 1: Full Historical Backfill (dbt)

**Scenario**: New incremental model needs last 2 years of data

**Step 1: Estimate Cost**
```bash
# Dry run to estimate bytes processed
dbt compile --select your_model
# Copy compiled SQL and run in BigQuery UI with dry run

# Calculate cost: bytes_processed * $5/TB
```

**Step 2: Backfill Strategy**

*Option A: Single Full Refresh (< 1TB data)*
```bash
dbt run --select your_model --full-refresh --vars '{limit: null}'
```

*Option B: Chunked Backfill (> 1TB data)*
```bash
# Backfill in monthly chunks to control cost and avoid timeouts
for year in 2022 2023 2024; do
  for month in {1..12}; do
    dbt run --select your_model \
      --vars "{
        start_date: '${year}-${month}-01',
        end_date: '${year}-${month}-28'
      }"
  done
done
```

**Step 3: Model Configuration for Chunked Backfill**
```sql
-- models/your_model.sql
{{
  config(
    materialized='incremental',
    partition_by={'field': 'date', 'data_type': 'date'},
    incremental_strategy='insert_overwrite'
  )
}}

{% set start_date = var('start_date', None) %}
{% set end_date = var('end_date', None) %}

select *
from source_table
{% if is_incremental() %}
  {% if start_date and end_date %}
    -- Manual backfill mode
    where date >= '{{ start_date }}' and date <= '{{ end_date }}'
  {% else %}
    -- Standard incremental mode
    where date > (select max(date) from {{ this }})
  {% endif %}
{% endif %}
```

**Step 4: Validation**
```sql
-- Check all partitions populated
SELECT
  DATE_TRUNC(date, MONTH) as month,
  COUNT(*) as row_count,
  MIN(date) as min_date,
  MAX(date) as max_date
FROM your_table
GROUP BY month
ORDER BY month;

-- Identify missing dates
WITH date_spine AS (
  SELECT date
  FROM UNNEST(GENERATE_DATE_ARRAY('2022-01-01', CURRENT_DATE())) AS date
),
actual_dates AS (
  SELECT DISTINCT date
  FROM your_table
)
SELECT ds.date as missing_date
FROM date_spine ds
LEFT JOIN actual_dates ad USING (date)
WHERE ad.date IS NULL;
```

### Pattern 2: Incremental Backfill (SQLMesh)

**Scenario**: Backfill specific date range in SQLMesh incremental model

**Step 1: Plan Backfill**
```bash
# Show what will be backfilled
sqlmesh plan --start-date 2023-01-01 --end-date 2023-12-31 --dry-run
```

**Step 2: Execute Backfill**
```bash
# Backfill with automatic chunking
sqlmesh run --start-date 2023-01-01 --end-date 2023-12-31

# Monitor progress
sqlmesh info
```

**Step 3: Validate**
```bash
# Run audits on backfilled data
sqlmesh audit --start-date 2023-01-01 --end-date 2023-12-31
```

### Pattern 3: Partition-Level Backfill

**Scenario**: Fix bug in specific partitions without full refresh

**Step 1: Identify Affected Partitions**
```sql
-- Find partitions with data quality issue
SELECT
  DATE(_PARTITIONTIME) as partition_date,
  COUNTIF(bad_condition) as bad_rows,
  COUNT(*) as total_rows
FROM your_table
WHERE _PARTITIONTIME >= '2024-01-01'
GROUP BY partition_date
HAVING COUNTIF(bad_condition) > 0;
```

**Step 2: Delete Affected Partitions**
```sql
-- Delete specific partitions
DELETE FROM your_table
WHERE DATE(_PARTITIONTIME) IN ('2024-01-15', '2024-01-16', '2024-01-17');
```

**Step 3: Rerun for Those Dates**
```bash
# dbt with insert_overwrite strategy
dbt run --select your_model \
  --vars "{
    start_date: '2024-01-15',
    end_date: '2024-01-17'
  }"

# SQLMesh
sqlmesh run --start-date 2024-01-15 --end-date 2024-01-17
```

### Pattern 4: Parallel Backfill

**Scenario**: Backfill large date range quickly using parallel execution

**Approach 1: dbt Multi-Threading**
```bash
# Increase threads for parallel partition processing
dbt run --select your_model --full-refresh --threads 8
```

**Approach 2: Manual Parallel Jobs**
```bash
# Split date range and run in parallel terminal sessions
# Terminal 1
dbt run --vars "{start_date: '2023-01-01', end_date: '2023-03-31'}"

# Terminal 2
dbt run --vars "{start_date: '2023-04-01', end_date: '2023-06-30'}"

# Terminal 3
dbt run --vars "{start_date: '2023-07-01', end_date: '2023-09-30'}"

# Terminal 4
dbt run --vars "{start_date: '2023-10-01', end_date: '2023-12-31'}"
```

**Approach 3: BigQuery Scripting**
```sql
-- Run multiple INSERT jobs in parallel using BigQuery scripts
DECLARE partitions ARRAY<DATE> DEFAULT GENERATE_DATE_ARRAY('2023-01-01', '2023-12-31');
DECLARE partition_date DATE;

FOR i IN (SELECT * FROM UNNEST(partitions) AS p) DO
  SET partition_date = i.p;

  -- Each partition gets processed independently
  INSERT INTO target_table
  SELECT * FROM source_table
  WHERE DATE(timestamp_col) = partition_date;
END FOR;
```

### Pattern 5: Upsert/Merge Backfill

**Scenario**: Update existing records rather than full replacement

```sql
-- Backfill using MERGE for updates + inserts
MERGE target_table T
USING (
  SELECT *
  FROM source_table
  WHERE date BETWEEN '2024-01-01' AND '2024-01-31'
) S
ON T.id = S.id AND DATE(T.timestamp) = DATE(S.timestamp)
WHEN MATCHED THEN
  UPDATE SET
    T.column1 = S.column1,
    T.column2 = S.column2,
    T.updated_at = CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN
  INSERT (id, column1, column2, timestamp, updated_at)
  VALUES (S.id, S.column1, S.column2, S.timestamp, CURRENT_TIMESTAMP());
```

### Pattern 6: Resumable Backfill

**Scenario**: Long-running backfill that might fail partway through

**Step 1: Create Checkpoint Table**
```sql
CREATE TABLE IF NOT EXISTS backfill_checkpoints (
  backfill_id STRING,
  date_processed DATE,
  rows_processed INT64,
  status STRING,
  error_message STRING,
  processed_at TIMESTAMP
);
```

**Step 2: Backfill with Checkpointing**
```python
# backfill_script.py
from google.cloud import bigquery
from datetime import datetime, timedelta

client = bigquery.Client()
backfill_id = "user_events_backfill_2024"
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)

current_date = start_date
while current_date <= end_date:
    # Check if already processed
    check_query = f"""
    SELECT COUNT(*) as count
    FROM backfill_checkpoints
    WHERE backfill_id = '{backfill_id}'
      AND date_processed = '{current_date.date()}'
      AND status = 'completed'
    """
    result = client.query(check_query).result()
    if next(result).count > 0:
        print(f"Skipping {current_date.date()} - already completed")
        current_date += timedelta(days=1)
        continue

    try:
        # Run backfill for this date
        backfill_query = f"""
        INSERT INTO target_table
        SELECT * FROM source_table
        WHERE DATE(timestamp) = '{current_date.date()}'
        """
        job = client.query(backfill_query)
        result = job.result()

        # Record success
        checkpoint_query = f"""
        INSERT INTO backfill_checkpoints VALUES (
          '{backfill_id}',
          '{current_date.date()}',
          {job.num_dml_affected_rows},
          'completed',
          NULL,
          CURRENT_TIMESTAMP()
        )
        """
        client.query(checkpoint_query).result()

        print(f"Completed {current_date.date()}: {job.num_dml_affected_rows} rows")

    except Exception as e:
        # Record failure
        checkpoint_query = f"""
        INSERT INTO backfill_checkpoints VALUES (
          '{backfill_id}',
          '{current_date.date()}',
          0,
          'failed',
          '{str(e)}',
          CURRENT_TIMESTAMP()
        )
        """
        client.query(checkpoint_query).result()
        print(f"Failed {current_date.date()}: {e}")

    current_date += timedelta(days=1)
```

**Step 3: Monitor Progress**
```sql
SELECT
  status,
  COUNT(*) as partition_count,
  SUM(rows_processed) as total_rows
FROM backfill_checkpoints
WHERE backfill_id = 'user_events_backfill_2024'
GROUP BY status;

-- Find failed partitions
SELECT date_processed, error_message
FROM backfill_checkpoints
WHERE backfill_id = 'user_events_backfill_2024'
  AND status = 'failed'
ORDER BY date_processed;
```

### Backfill Best Practices

1. **Always estimate cost first** - Use dry run before executing
2. **Chunk large backfills** - Avoid timeouts and control costs
3. **Use insert_overwrite** - Atomic partition replacement
4. **Monitor progress** - Log completion status
5. **Validate thoroughly** - Check row counts, date coverage, data quality
6. **Keep backups** - Don't drop old table immediately
7. **Communicate** - Notify stakeholders of large backfills that might affect query performance

---

## Incident Response

### Overview
Structured workflow for responding to data incidents including data quality issues, pipeline failures, and incorrect data.

### Incident Severity Levels

- **P0 Critical**: Revenue-impacting, customer-facing data incorrect, SLA breach
- **P1 High**: Important dashboards broken, delayed reporting, degraded accuracy
- **P2 Medium**: Non-critical data quality issues, delayed non-essential pipelines
- **P3 Low**: Minor issues, cosmetic problems, optimization opportunities

### Incident Response Workflow

#### Phase 1: Detection & Triage (0-15 minutes)

**Step 1: Receive Alert**
```bash
# Common alert sources:
# - dbt test failures
# - SQLMesh audit failures
# - Data monitoring alerts
# - Stakeholder reports
# - Scheduled job failures
```

**Step 2: Initial Assessment**
```sql
-- Quick health check queries
-- Check recent data freshness
SELECT
  MAX(updated_at) as last_update,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(updated_at), MINUTE) as minutes_stale
FROM production.critical_table;

-- Check row count trends
SELECT
  DATE(timestamp) as date,
  COUNT(*) as row_count
FROM production.critical_table
WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY date
ORDER BY date DESC;

-- Check null rates
SELECT
  COUNTIF(critical_column IS NULL) / COUNT(*) as null_rate
FROM production.critical_table
WHERE DATE(timestamp) = CURRENT_DATE();
```

**Step 3: Determine Severity**
```markdown
Ask:
- Is this affecting customer-facing data? → P0
- Is this affecting executive reporting? → P0 or P1
- Is this affecting automated decisions? → P0 or P1
- Is this blocking other teams? → P1
- Can this wait until tomorrow? → P2 or P3
```

**Step 4: Create Incident Ticket**
```markdown
# Incident Template

**Severity**: P1
**Status**: Investigating
**Detected**: 2024-01-15 10:23 AM
**Reporter**: @username
**Assignee**: @data-eng-oncall

## Symptoms
- Describe what was observed
- Include specific error messages
- Link to failed job/test

## Impact
- Which tables/dashboards affected
- Number of users impacted
- Business processes affected

## Timeline
- 10:23 - Alert received
- 10:25 - Investigation started
- (Update as incident progresses)
```

#### Phase 2: Investigation (15-60 minutes)

**Step 1: Identify Scope**
```sql
-- Find first occurrence of bad data
WITH data_quality AS (
  SELECT
    DATE(timestamp) as date,
    COUNT(*) as total_rows,
    COUNTIF(quality_check_fails) as bad_rows
  FROM production.table
  WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  GROUP BY date
)
SELECT
  date,
  total_rows,
  bad_rows,
  bad_rows / total_rows as bad_rate
FROM data_quality
WHERE bad_rows > 0
ORDER BY date;
```

**Step 2: Trace Lineage**
```bash
# Find upstream dependencies
dbt list --select +production.affected_table

# Check source data
# Compare affected table to its source
```

```sql
-- Compare aggregates between source and transformed
WITH source_metrics AS (
  SELECT
    DATE(timestamp) as date,
    COUNT(*) as row_count,
    SUM(amount) as total_amount
  FROM source.raw_table
  WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
  GROUP BY date
),
transformed_metrics AS (
  SELECT
    DATE(timestamp) as date,
    COUNT(*) as row_count,
    SUM(amount) as total_amount
  FROM production.affected_table
  WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 DAY)
  GROUP BY date
)
SELECT
  COALESCE(s.date, t.date) as date,
  s.row_count as source_rows,
  t.row_count as transformed_rows,
  s.total_amount as source_amount,
  t.total_amount as transformed_amount,
  s.row_count - t.row_count as row_diff,
  s.total_amount - t.total_amount as amount_diff
FROM source_metrics s
FULL OUTER JOIN transformed_metrics t USING (date)
ORDER BY date DESC;
```

**Step 3: Check Recent Changes**
```bash
# Check recent commits
git log --since="3 days ago" --oneline -- models/production/affected_table.sql

# Check recent deployments
dbt list --select production.affected_table --output json | jq '.[-1].compiled_at'

# Review recent config changes
git diff HEAD~5 -- dbt_project.yml
```

**Step 4: Examine Logs**
```bash
# dbt run logs
cat logs/dbt.log | grep "affected_table" | tail -50

# Check BigQuery job history
bq ls -j --max_results=50 | grep affected_table

# Get specific job details
bq show -j <job_id>
```

**Step 5: Identify Root Cause**

Common root causes:
1. **Source data issue** - Upstream system sent bad data
2. **Logic bug** - Code change introduced error
3. **Schema change** - Upstream schema changed unexpectedly
4. **Resource issue** - Job timed out or failed
5. **Configuration change** - dbt/SQLMesh config modified incorrectly

#### Phase 3: Mitigation (Immediate Fix - 30-120 minutes)

**Strategy 1: Rollback to Last Good Version**
```bash
# Find last successful run
git log --all --oneline -- models/production/affected_table.sql

# Revert to that version
git checkout <good-commit-hash> -- models/production/affected_table.sql

# Redeploy
dbt run --select production.affected_table --full-refresh
```

**Strategy 2: Use Time Travel for Data Recovery**
```sql
-- Restore table from before incident (within 7 days)
CREATE OR REPLACE TABLE production.affected_table AS
SELECT * FROM production.affected_table
FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 DAY);

-- Or restore specific partitions
DELETE FROM production.affected_table
WHERE DATE(timestamp) IN ('2024-01-14', '2024-01-15');

INSERT INTO production.affected_table
SELECT * FROM production.affected_table
FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 2 DAY)
WHERE DATE(timestamp) IN ('2024-01-14', '2024-01-15');
```

**Strategy 3: Quick Hotfix**
```sql
-- Apply temporary fix directly in SQL
UPDATE production.affected_table
SET column_name = CASE
  WHEN bad_condition THEN corrected_value
  ELSE column_name
END
WHERE DATE(timestamp) >= '2024-01-14';
```

**Strategy 4: Downstream Damage Control**
```bash
# Identify and pause downstream jobs
dbt run --select +production.affected_table+ --dry-run

# Manually pause critical downstream jobs
# Prevent propagation of bad data
```

#### Phase 4: Communication

**For P0/P1 Incidents - Immediate Notification**
```markdown
# Slack Post Template

🚨 DATA INCIDENT - P1

**Affected**: production.user_metrics table
**Impact**: Executive dashboard showing incorrect user counts
**Status**: Identified root cause, deploying fix
**ETA**: Fix deployed in 15 minutes, data corrected in 30 minutes

**Action Required**:
- Do not use user_metrics for reporting until 11:30 AM
- Refresh dashboards after 11:30 AM

Updates: Thread below
Next update: 11:00 AM or when fixed
Incident ticket: INCIDENT-1234
```

**For P2/P3 Incidents - Standard Notification**
```markdown
# Slack Post Template

⚠️ Data Issue - P2

**Affected**: staging.daily_summary table
**Impact**: Internal reporting delayed by 2 hours
**Status**: Fixing upstream data issue
**ETA**: Resolved by end of day

Updates in #data-incidents
```

#### Phase 5: Resolution (Permanent Fix)

**Step 1: Implement Permanent Fix**
```sql
-- Add defensive logic to prevent recurrence
select
  user_id,
  -- Add validation
  case
    when metric < 0 then 0  -- Prevent negative values
    when metric > 1000000 then 1000000  -- Cap unrealistic values
    else metric
  end as metric_clean,
  -- Add data quality flag
  case
    when metric < 0 or metric > 1000000 then true
    else false
  end as is_anomalous
from source_table
```

**Step 2: Add Tests to Prevent Regression**
```yaml
# schema.yml
models:
  - name: production.affected_table
    columns:
      - name: metric_clean
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"
          - dbt_utils.expression_is_true:
              expression: "<= 1000000"

      # Row-level validation
    tests:
      - dbt_utils.fewer_rows_than:
          compare_model: source('raw', 'source_table')
          group_by_columns: ['date']
```

**Step 3: Add Monitoring**
```sql
-- Create monitoring query
CREATE OR REPLACE VIEW monitoring.affected_table_health AS
SELECT
  DATE(timestamp) as date,
  COUNT(*) as total_rows,
  COUNTIF(is_anomalous) as anomalous_rows,
  COUNTIF(is_anomalous) / COUNT(*) as anomaly_rate,
  MIN(metric_clean) as min_metric,
  MAX(metric_clean) as max_metric,
  AVG(metric_clean) as avg_metric
FROM production.affected_table
WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY date;

-- Set up alert
-- If anomaly_rate > 0.05 for any day, send alert
```

**Step 4: Backfill Corrected Data**
```bash
# Use backfill workflow to fix historical data
dbt run --select production.affected_table --vars '{
  start_date: "2024-01-14",
  end_date: "2024-01-15"
}'
```

#### Phase 6: Post-Incident Review (Within 48 Hours)

**Post-Mortem Template**
```markdown
# Incident Post-Mortem: [Brief Description]

**Date**: 2024-01-15
**Severity**: P1
**Duration**: 2 hours (10:23 AM - 12:23 PM)
**Responders**: @eng1, @eng2

## Summary
One-paragraph summary of what happened and impact.

## Timeline
- 10:23 - Alert received from monitoring
- 10:25 - Investigation started
- 10:45 - Root cause identified (upstream schema change)
- 11:00 - Hotfix deployed
- 11:30 - Data corrected via backfill
- 12:00 - Monitoring confirmed resolution
- 12:23 - Incident closed

## Root Cause
Upstream system changed column name from `user_id` to `userId` without notice.
Our model failed silently and populated nulls.

## Impact
- Executive dashboard showed 0 users for 2 hours
- 3 stakeholders affected
- No customer-facing impact
- ~$50 in wasted query costs from failed runs

## Resolution
1. Updated model to handle both column names
2. Added test for not_null on user_id
3. Added monitoring alert for null rate > 5%
4. Contacted upstream team about change notification process

## Action Items
- [ ] Implement schema change detection (@eng1 - Due: 2024-01-20)
- [ ] Add integration tests for upstream sources (@eng2 - Due: 2024-01-22)
- [ ] Document upstream change notification process (@eng1 - Due: 2024-01-18)
- [ ] Review all upstream source dependencies (@team - Due: 2024-01-25)

## What Went Well
- Alert fired within 2 minutes of failure
- Root cause identified quickly
- Rollback process was smooth

## What Could Be Improved
- No tests caught this before production
- Upstream changes weren't communicated
- Recovery took longer than ideal due to large backfill

## Lessons Learned
- Always validate critical joins return expected row counts
- Add contract testing for upstream dependencies
- Implement schema versioning with upstream teams
```

### Incident Prevention Checklist

**Before Deploying to Production**
- [ ] All tests pass in dev
- [ ] Reviewed compiled SQL for logic errors
- [ ] Validated row counts match expectations
- [ ] Checked for breaking schema changes
- [ ] Added tests for critical business logic
- [ ] Considered edge cases and null handling
- [ ] Reviewed impact on downstream models
- [ ] Communicated changes to stakeholders
- [ ] Have rollback plan ready

**Monitoring in Production**
- [ ] Freshness monitoring on critical tables
- [ ] Row count anomaly detection
- [ ] Null rate monitoring on key columns
- [ ] Data quality tests running daily
- [ ] Downstream dependency monitoring
- [ ] Cost monitoring for query efficiency
- [ ] On-call rotation defined
- [ ] Runbooks documented

---

## Additional Resources

- [Data Engineering Patterns](./data-engineering-patterns.md) - Best practices for dbt, SQLMesh, and BigQuery
- [Example SQL](./examples/sql/) - Template models and queries
- [Git Worktree Workflows](./docs/worktrees/WORKTREES.md) - Managing parallel development
- [Hook Configuration](./README.md) - Automated validation and testing

## Contributing

To add new playbooks or improve existing ones:
1. Create a new section following the existing format
2. Include concrete code examples
3. Add decision trees for complex scenarios
4. Test workflows in dev environment first
5. Submit PR with description of new/updated playbook

---

**Last Updated**: 2026-01-12
**Maintainer**: Data Engineering Team
