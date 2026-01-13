# [Component/System Name] Troubleshooting Guide

**Component**: [Component/System Name]
**Owner**: [Team/Individual]
**Last Updated**: [YYYY-MM-DD]
**Related Runbooks**: [Links to related runbooks]

## Quick Diagnostics

### Health Check Commands

```bash
# System status
[status_check_command]

# Recent errors
[error_check_command]

# Current metrics
[metrics_command]

# Connectivity test
[connectivity_command]
```

### Common Symptoms Quick Reference

| Symptom | Likely Cause | Quick Fix | Details |
|---------|--------------|-----------|---------|
| [Symptom 1] | [Cause] | `[command]` | [Section link] |
| [Symptom 2] | [Cause] | `[command]` | [Section link] |
| [Symptom 3] | [Cause] | `[command]` | [Section link] |

## Diagnostic Framework

### Step 1: Identify the Problem

**Questions to ask:**
1. What is the exact error message?
2. When did it start failing?
3. What changed recently?
4. Is it affecting all users/data or specific cases?
5. Can you reproduce it?

**Gather information:**
```bash
# Check logs
[log_command]

# Check recent deployments
[deployment_history_command]

# Check dependencies
[dependency_check_command]
```

### Step 2: Isolate the Cause

**Narrow down the scope:**
```bash
# Test connectivity
[connectivity_test]

# Verify credentials
[auth_test]

# Check data availability
[data_check]

# Review recent changes
git log --since="[timeframe]" --oneline
```

### Step 3: Implement Fix

**Apply fix safely:**
1. Test in dev environment first
2. Document what you're changing
3. Have rollback plan ready
4. Monitor after applying fix

### Step 4: Verify Resolution

**Confirm fix:**
```bash
# Run validation
[validation_command]

# Check metrics
[metrics_command]

# Test end-to-end
[e2e_test_command]
```

### Step 5: Prevent Recurrence

**Update safeguards:**
- Add monitoring/alerts
- Update documentation
- Add tests to prevent regression
- Share learnings with team

## Common Issues

### Category: Data Quality

#### Issue: Duplicate Records

**Symptoms:**
- Primary key violations
- Unexpected row count increases
- Data quality tests fail

**Diagnosis:**
```sql
-- Find duplicates
SELECT
  [grain_columns],
  COUNT(*) as duplicate_count
FROM `[project.dataset.table]`
WHERE DATE([partition_column]) = CURRENT_DATE()
GROUP BY [grain_columns]
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- Identify source of duplicates
SELECT
  [source_column],
  COUNT(*) as record_count
FROM `[project.dataset.table]`
WHERE [grain_columns] IN (
  SELECT [grain_columns]
  FROM `[project.dataset.table]`
  WHERE DATE([partition_column]) = CURRENT_DATE()
  GROUP BY [grain_columns]
  HAVING COUNT(*) > 1
)
GROUP BY [source_column];
```

**Root Causes:**
- [ ] Upstream source sending duplicates
- [ ] Missing deduplication logic
- [ ] Incorrect grain definition
- [ ] Multiple pipeline runs without idempotency
- [ ] Incorrect incremental logic

**Resolution:**
```sql
-- Add deduplication (example)
SELECT DISTINCT
  [columns]
FROM [source]
WHERE [conditions]
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY [grain_columns]
  ORDER BY [timestamp_column] DESC
) = 1;
```

**Prevention:**
```yaml
# Add test
models:
  - name: [model_name]
    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns: [grain_columns]
```

#### Issue: Null Values in Critical Columns

**Symptoms:**
- Downstream joins fail
- Analytics reports missing data
- Data quality tests fail

**Diagnosis:**
```sql
-- Check null rates
SELECT
  COUNTIF([column_1] IS NULL) / COUNT(*) * 100 as column_1_null_pct,
  COUNTIF([column_2] IS NULL) / COUNT(*) * 100 as column_2_null_pct,
  COUNTIF([column_3] IS NULL) / COUNT(*) * 100 as column_3_null_pct
FROM `[project.dataset.table]`
WHERE DATE([partition_column]) = CURRENT_DATE();

-- Find patterns in null values
SELECT
  DATE([partition_column]) as date,
  COUNTIF([critical_column] IS NULL) as null_count,
  COUNT(*) as total_count
FROM `[project.dataset.table]`
WHERE DATE([partition_column]) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY 1
ORDER BY 1 DESC;
```

**Root Causes:**
- [ ] Upstream source missing data
- [ ] Schema mismatch
- [ ] Failed joins
- [ ] Incorrect filter logic
- [ ] Data not available yet (freshness issue)

**Resolution:**
1. Identify when nulls appeared
2. Check upstream sources
3. Add null handling or default values
4. Add validation at ingestion

**Prevention:**
```yaml
# Add not_null tests
columns:
  - name: [critical_column]
    tests:
      - not_null
```

#### Issue: Data Freshness Problems

**Symptoms:**
- Dashboards show stale data
- Freshness alerts trigger
- Downstream pipelines waiting

**Diagnosis:**
```sql
-- Check data freshness
SELECT
  MAX([timestamp_column]) as latest_data,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX([timestamp_column]), HOUR) as hours_stale
FROM `[project.dataset.table]`;

-- Check partition freshness
SELECT
  MAX(DATE([partition_column])) as latest_partition,
  DATE_DIFF(CURRENT_DATE(), MAX(DATE([partition_column])), DAY) as days_stale
FROM `[project.dataset.table]`;
```

**Root Causes:**
- [ ] Upstream pipeline delayed/failed
- [ ] Schedule misconfiguration
- [ ] Source system delay
- [ ] Pipeline running but failing silently
- [ ] Timezone issues

**Resolution:**
```bash
# Check pipeline status
[check_pipeline_command]

# Check upstream dependencies
[check_upstream_command]

# Manual trigger if needed
[trigger_command]
```

**Prevention:**
```yaml
# Add freshness test
models:
  - name: [model_name]
    tests:
      - dbt_utils.recency:
          datepart: hour
          field: [timestamp_column]
          interval: [expected_interval]
```

### Category: Performance

#### Issue: Query Timeout

**Symptoms:**
- Queries fail with timeout error
- Pipeline duration exceeds SLA
- High slot utilization

**Diagnosis:**
```bash
# Check query performance
# BigQuery
bq show -j [job_id]

# Review query plan
bq show --format=prettyjson -j [job_id] | jq '.statistics.query.queryPlan'

# Check bytes processed
bq show --format=prettyjson -j [job_id] | jq '.statistics.query.totalBytesProcessed'
```

**Root Causes:**
- [ ] Missing partitioning/clustering
- [ ] Full table scan instead of partition pruning
- [ ] Inefficient joins
- [ ] Missing filters on partition columns
- [ ] Data skew
- [ ] Suboptimal query structure

**Resolution:**
```sql
-- Add partition filter
WHERE DATE([partition_column]) = CURRENT_DATE()

-- Add clustering to improve join performance
CLUSTER BY ([join_columns])

-- Use approximate functions for large aggregations
APPROX_COUNT_DISTINCT([column]) instead of COUNT(DISTINCT [column])

-- Materialize intermediate results
CREATE OR REPLACE TABLE `[project.dataset.temp_table]` AS
SELECT [expensive_transformation]
FROM [source];
```

**Prevention:**
- Always filter on partition columns
- Use clustering for frequently joined/filtered columns
- Monitor query performance trends
- Set up cost/performance alerts

#### Issue: High Query Cost

**Symptoms:**
- Cost alerts trigger
- Budget exceeded
- Bytes processed higher than expected

**Diagnosis:**
```sql
-- Estimate query cost
-- Run as dry run to check bytes
-- BigQuery charges $5 per TB processed

-- Check table sizes
SELECT
  table_name,
  ROUND(size_bytes / POW(10, 12), 2) as size_tb,
  ROUND(size_bytes / POW(10, 12) * 5, 2) as full_scan_cost_usd
FROM `[project.dataset].__TABLES__`
ORDER BY size_bytes DESC;

-- Check if partitioning is effective
SELECT
  _PARTITIONTIME as partition_date,
  COUNT(*) as row_count,
  SUM(LENGTH(TO_JSON_STRING([table_name]))) as partition_size_bytes
FROM `[project.dataset.table]`
GROUP BY 1
ORDER BY 1 DESC
LIMIT 10;
```

**Root Causes:**
- [ ] Querying entire table instead of partitions
- [ ] Not using clustering
- [ ] Scanning columns not needed
- [ ] Multiple full table scans
- [ ] Not using cached results

**Resolution:**
```sql
-- Scan only needed columns
SELECT [specific_columns]  -- NOT SELECT *
FROM `[project.dataset.table]`
WHERE DATE([partition_column]) = CURRENT_DATE();  -- Filter partition

-- Use materialized views for expensive queries
CREATE MATERIALIZED VIEW `[project.dataset.mv_name]`
PARTITION BY DATE([partition_column])
CLUSTER BY ([cluster_columns])
AS
SELECT [optimized_query];
```

**Prevention:**
- Use partition pruning filters
- Select only needed columns
- Use incremental models
- Monitor query costs
- Set up budget alerts

### Category: Pipeline Failures

#### Issue: dbt Model Failure

**Symptoms:**
- `dbt run` fails
- Error in dbt logs
- Model shows as errored in docs

**Diagnosis:**
```bash
# Run specific model with debug logging
dbt run --select [model_name] --debug

# Check compiled SQL
dbt compile --select [model_name]
cat target/compiled/[project]/models/[path]/[model_name].sql

# Test dependencies
dbt run --select +[model_name]  # Run upstream dependencies
```

**Root Causes:**
- [ ] Syntax error in SQL
- [ ] Upstream dependency failed
- [ ] Schema change in source
- [ ] Insufficient permissions
- [ ] Resource constraints (memory/timeout)
- [ ] Invalid ref() or source()

**Resolution:**
```bash
# Fix syntax errors
dbt compile --select [model_name]  # Check compilation

# Check dependencies
dbt list --select +[model_name]  # List all dependencies
dbt run --select +[model_name]    # Run dependencies first

# Grant permissions
# Run GRANT statements if permission error

# Increase resources
# Update dbt_project.yml or model config
```

**Prevention:**
```yaml
# Add pre-commit hooks
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: dbt-compile
        name: dbt compile
        entry: dbt compile
        language: system
        pass_filenames: false
```

#### Issue: SQLMesh Plan Fails

**Symptoms:**
- `sqlmesh plan` fails
- Breaking changes detected
- Models not updating

**Diagnosis:**
```bash
# Check plan details
sqlmesh plan --environment [env]

# Review breaking changes
sqlmesh diff --environment [env]

# Check model definition
sqlmesh validate [model_name]

# View rendered SQL
sqlmesh render [model_name]
```

**Root Causes:**
- [ ] Schema change requires migration
- [ ] Invalid model definition
- [ ] Macro/function error
- [ ] Environment configuration issue
- [ ] Version conflict

**Resolution:**
```bash
# For breaking changes, create migration
sqlmesh plan --environment [env] --create-migration

# Or recreate virtual environment
sqlmesh plan --environment [env] --recreate

# Fix model definition
# Edit model SQL and re-validate
sqlmesh validate [model_name]
```

**Prevention:**
- Use forward-only changes when possible
- Test in dev environment first
- Use environment-specific configurations
- Document breaking changes

#### Issue: Airflow DAG Failure

**Symptoms:**
- DAG shows failed in UI
- Task stuck in running state
- Scheduler not picking up DAG

**Diagnosis:**
```bash
# Check DAG status
airflow dags list-runs --dag-id [dag_id]

# Check task logs
airflow tasks logs [dag_id] [task_id] [execution_date]

# Test task locally
airflow tasks test [dag_id] [task_id] [execution_date]

# Check for import errors
airflow dags list-import-errors
```

**Root Causes:**
- [ ] Task logic error
- [ ] Resource constraints
- [ ] Dependency not met
- [ ] Syntax error in DAG file
- [ ] Missing connection/variable
- [ ] External system unavailable

**Resolution:**
```bash
# Clear failed task and retry
airflow tasks clear [dag_id] --task-regex [task_id]

# Set up missing connection
airflow connections add [conn_id] --conn-type [type] --conn-host [host]

# Update DAG and refresh
# Edit DAG file
airflow dags trigger [dag_id]
```

**Prevention:**
- Add retries to tasks
- Implement proper error handling
- Use sensors for external dependencies
- Test DAGs before deploying
- Monitor resource usage

### Category: Authentication/Permissions

#### Issue: Permission Denied

**Symptoms:**
- `403 Forbidden` error
- `Permission denied` in logs
- Cannot access table/dataset

**Diagnosis:**
```bash
# Check current user
gcloud auth list

# Check project permissions
gcloud projects get-iam-policy [project_id]

# Check dataset permissions (BigQuery)
bq show --format=prettyjson [dataset_id]

# Check table permissions
bq show --format=prettyjson [project:dataset.table]
```

**Root Causes:**
- [ ] Service account lacks permissions
- [ ] User not authenticated
- [ ] Wrong project selected
- [ ] Table/dataset permissions not granted
- [ ] IAM role not assigned

**Resolution:**
```bash
# Grant BigQuery permissions
bq update --dataset \
  --add_access_entry role=READER,user=[email] \
  [project:dataset]

# Grant IAM role
gcloud projects add-iam-policy-binding [project_id] \
  --member="serviceAccount:[sa_email]" \
  --role="roles/bigquery.dataEditor"

# Authenticate
gcloud auth login
gcloud config set project [project_id]
```

**Prevention:**
- Use service accounts for automation
- Follow principle of least privilege
- Document required permissions
- Use IAM conditions for fine-grained control

## Escalation Process

### When to Escalate

Escalate immediately if:
- [ ] Production data loss or corruption
- [ ] Security incident
- [ ] SLA breach with business impact
- [ ] Issue persists after 2 hours of troubleshooting
- [ ] Need for emergency rollback

### Escalation Contacts

**Level 1**: [Team/Channel]
**Level 2**: [Senior Engineer/Lead]
**Level 3**: [Manager/On-Call]
**Level 4**: [Director/VP]

### Escalation Template

```
SUBJECT: [URGENT/HIGH/MEDIUM] - [Component] - [Brief Description]

IMPACT:
- Affected users/systems: [details]
- Business impact: [details]
- Data at risk: [details]

SYMPTOMS:
[What's happening]

WHAT WE'VE TRIED:
[Troubleshooting steps taken]

TIMELINE:
[When it started, key events]

NEXT STEPS:
[What we need]
```

## Claude Code Assistance

### Diagnostic Workflows

**"Debug [component] showing [symptom]"**
```bash
# Claude will:
# 1. Check recent changes
# 2. Review logs for errors
# 3. Run diagnostic queries
# 4. Suggest fixes based on patterns
```

**"Why is [query/model] slow?"**
```bash
# Claude will:
# 1. Analyze query structure
# 2. Check partitioning/clustering
# 3. Review bytes processed
# 4. Suggest optimizations
```

**"Fix permission error for [resource]"**
```bash
# Claude will:
# 1. Check current permissions
# 2. Identify missing grants
# 3. Generate GRANT commands
# 4. Verify after applying
```

### Common Claude Prompts

- "Check if [pipeline] is running normally"
- "Find why [model] is failing"
- "Optimize [query] for cost and performance"
- "Add monitoring for [metric]"
- "Create runbook for [issue]"

## Additional Resources

### Documentation
- [Internal wiki link]
- [Vendor documentation]
- [Architecture docs]

### Tools
- **Logging**: [Link to logging system]
- **Monitoring**: [Link to dashboards]
- **Alerting**: [Link to alert manager]

### Useful Queries

[Link to query library or paste frequently used diagnostic queries]

## Post-Incident Review

### Incident Template

```markdown
## Incident: [Title]
**Date**: [YYYY-MM-DD]
**Duration**: [Duration]
**Severity**: [S1/S2/S3/S4]

### Timeline
- [Time]: [Event]
- [Time]: [Event]

### Root Cause
[Technical root cause]

### Impact
- [Impact detail]
- [Impact detail]

### Resolution
[What fixed it]

### Action Items
- [ ] [Preventive measure 1]
- [ ] [Preventive measure 2]
- [ ] [Documentation update]
```

## Change Log

| Date | Change | Author |
|------|--------|--------|
| [YYYY-MM-DD] | [Description] | [Name] |
