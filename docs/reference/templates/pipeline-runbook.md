# [Pipeline Name] Runbook

**Pipeline ID**: `[pipeline_identifier]`
**Owner**: [Team/Individual]
**Last Updated**: [YYYY-MM-DD]
**Status**: [Development / Production / Deprecated]
**On-Call**: [Contact/Rotation]

## Quick Reference

### Pipeline Health
- **Status Dashboard**: [Link to dashboard]
- **Recent Runs**: `[command to check recent runs]`
- **Current Status**: `[command to check current status]`

### Emergency Contacts
- **Primary Owner**: [Name] - [Contact]
- **Secondary**: [Name] - [Contact]
- **Slack Channel**: [#channel]
- **PagerDuty**: [Link if applicable]

### Critical Commands

```bash
# Check pipeline status
[status_check_command]

# Trigger manual run
[trigger_command]

# Cancel running job
[cancel_command]

# View logs
[logs_command]
```

## Overview

### Purpose

[Describe what this pipeline does and why it exists]

### Business Impact

[Explain the business criticality and what breaks if this pipeline fails]

### Data Flow

```
[Source 1] ──┐
             ├──> [Transformation Stage] ──> [Intermediate Storage] ──> [Final Models] ──> [Downstream Systems]
[Source 2] ──┘
```

## Pipeline Architecture

### Components

| Component | Type | Purpose | Location |
|-----------|------|---------|----------|
| [Component 1] | [Extract/Transform/Load] | [Purpose] | `[path/location]` |
| [Component 2] | [Extract/Transform/Load] | [Purpose] | `[path/location]` |

### Technology Stack

- **Orchestration**: [Airflow / Dagster / Prefect / Cloud Composer]
- **Transformation**: [dbt / SQLMesh / Dataflow]
- **Storage**: [BigQuery / Snowflake / Redshift]
- **Monitoring**: [Datadog / Cloud Monitoring / Custom]

## Schedule

### Run Frequency

**Schedule**: `[cron expression]` ([human readable, e.g., "Daily at 3am UTC"])
**Timezone**: [UTC / Other]
**Expected Duration**: [Duration range]

### Dependencies

**Upstream Dependencies** (must complete first):
```
[dependency_1]  # [Expected completion time]
[dependency_2]  # [Expected completion time]
```

**Downstream Dependencies** (waiting on this pipeline):
```
[dependent_1]   # [When it needs data]
[dependent_2]   # [When it needs data]
```

### SLA

- **Target Completion**: [Time by which pipeline should complete]
- **Max Duration**: [Maximum acceptable runtime]
- **Alert Threshold**: [When to alert if not complete]

## Configuration

### Environment Variables

```bash
# Required environment variables
export PROJECT_ID=[gcp_project_id]
export DATASET=[dataset_name]
export SERVICE_ACCOUNT=[service_account_email]

# Optional configuration
export PARALLELISM=[number]
export RETRY_COUNT=[number]
```

### dbt/SQLMesh Configuration

**dbt Project:**
```bash
# profiles.yml location
~/.dbt/profiles.yml

# Target for this pipeline
dbt run --select tag:[pipeline_tag] --target prod
```

**SQLMesh Project:**
```bash
# SQLMesh environment
sqlmesh run --environment prod --select [models]

# Plan changes
sqlmesh plan --environment prod
```

### Airflow DAG Configuration

```python
# Location: dags/[pipeline_name].py

default_args = {
    'owner': '[owner]',
    'depends_on_past': [True/False],
    'retries': [number],
    'retry_delay': timedelta(minutes=[minutes]),
    'sla': timedelta(hours=[hours]),
}

dag = DAG(
    '[pipeline_name]',
    default_args=default_args,
    schedule_interval='[cron]',
    catchup=[True/False],
)
```

## Execution

### Normal Run

```bash
# 1. Verify upstream dependencies complete
[check_dependencies_command]

# 2. Trigger pipeline
[trigger_command]

# 3. Monitor execution
[monitor_command]

# 4. Validate results
[validation_command]
```

### Manual Backfill

```bash
# Backfill specific date range
dbt run --select tag:[pipeline_tag] --vars '{"start_date": "2024-01-01", "end_date": "2024-01-31"}'

# SQLMesh backfill
sqlmesh run --start-date 2024-01-01 --end-date 2024-01-31 --environment prod
```

### Development/Testing

```bash
# Run against dev environment
dbt run --select tag:[pipeline_tag] --target dev

# Test with sample data
dbt run --select tag:[pipeline_tag] --target dev --vars '{"limit": 1000}'

# Dry run
dbt compile --select tag:[pipeline_tag]
```

## Monitoring

### Key Metrics

| Metric | Normal Range | Alert Threshold | Query/Dashboard |
|--------|--------------|-----------------|-----------------|
| Duration | [range] | > [threshold] | [link] |
| Row Count | [range] | Outside [range] | [link] |
| Data Freshness | [range] | > [threshold] | [link] |
| Error Rate | [range] | > [threshold] | [link] |
| Cost | [range] | > [threshold] | [link] |

### Health Checks

```sql
-- Check data freshness
SELECT
  MAX([timestamp_column]) as latest_data,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX([timestamp_column]), HOUR) as hours_stale
FROM `[project.dataset.table]`;

-- Check row counts
SELECT
  DATE([partition_column]) as date,
  COUNT(*) as row_count
FROM `[project.dataset.table]`
WHERE DATE([partition_column]) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
GROUP BY 1
ORDER BY 1 DESC;

-- Check for data quality issues
SELECT
  [quality_dimension],
  COUNT(*) as issue_count
FROM `[project.dataset.table]`
WHERE [quality_condition]
GROUP BY 1;
```

### Alerts

**Alert Conditions:**
- Pipeline duration > [threshold]
- Row count outside expected range
- Data freshness > [threshold]
- Failure rate > [threshold]
- Cost > [threshold]

**Alert Destinations:**
- Slack: [#channel]
- PagerDuty: [Policy]
- Email: [Distribution list]

## Troubleshooting

### Common Issues

#### Issue: Pipeline Timeout

**Symptoms**: Pipeline runs longer than [duration]

**Diagnosis**:
```bash
# Check for long-running queries
[check_queries_command]

# Review query plans
[query_plan_command]
```

**Resolution**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Prevention**: [How to prevent this issue]

#### Issue: Data Quality Failure

**Symptoms**: Data quality tests fail

**Diagnosis**:
```sql
-- Identify failing records
SELECT * FROM [table]
WHERE [quality_condition]
LIMIT 100;
```

**Resolution**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Prevention**: [How to prevent this issue]

#### Issue: Upstream Dependency Delay

**Symptoms**: Upstream data not available

**Diagnosis**:
```bash
# Check upstream pipeline status
[check_upstream_command]

# Verify data availability
[verify_data_command]
```

**Resolution**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Prevention**: [How to prevent this issue]

### Rollback Procedure

```bash
# 1. Identify last known good version
[identify_version_command]

# 2. Rollback to previous version
[rollback_command]

# 3. Verify rollback success
[verify_command]

# 4. Notify stakeholders
[notification_command]
```

## Data Quality

### Quality Checks

**dbt Tests:**
```yaml
# models/schema.yml
models:
  - name: [model_name]
    tests:
      - dbt_utils.recency:
          datepart: hour
          field: created_at
          interval: 24
      - dbt_utils.expression_is_true:
          expression: "[quality_expression]"
```

**Custom Validations:**
```sql
-- Expected volume check
SELECT
  DATE([partition_column]) as date,
  COUNT(*) as row_count,
  CASE
    WHEN COUNT(*) < [min_threshold] THEN 'TOO_LOW'
    WHEN COUNT(*) > [max_threshold] THEN 'TOO_HIGH'
    ELSE 'OK'
  END as status
FROM `[project.dataset.table]`
WHERE DATE([partition_column]) = CURRENT_DATE()
GROUP BY 1;
```

### Validation Queries

```sql
-- Check for duplicates
SELECT
  [grain_columns],
  COUNT(*) as duplicate_count
FROM `[project.dataset.table]`
WHERE DATE([partition_column]) = CURRENT_DATE()
GROUP BY [grain_columns]
HAVING COUNT(*) > 1;

-- Check for nulls in critical columns
SELECT
  COUNTIF([column_1] IS NULL) as column_1_nulls,
  COUNTIF([column_2] IS NULL) as column_2_nulls
FROM `[project.dataset.table]`
WHERE DATE([partition_column]) = CURRENT_DATE();
```

## Performance

### Optimization

**Current Performance**:
- Average Duration: [duration]
- Data Processed: [volume]
- Cost Per Run: [cost]

**Optimization Strategies**:
1. [Strategy 1]
2. [Strategy 2]
3. [Strategy 3]

### Cost Management

```sql
-- Query cost analysis
-- Check bytes processed by pipeline models
SELECT
  table_name,
  ROUND(size_bytes / POW(10, 9), 2) as size_gb,
  ROUND(size_bytes / POW(10, 9) * 0.02, 2) as full_scan_cost_usd
FROM `[project.dataset].__TABLES__`
WHERE table_name IN ([model_list])
ORDER BY size_bytes DESC;
```

**Cost Optimization Tips**:
- [Tip 1]
- [Tip 2]
- [Tip 3]

## Disaster Recovery

### Backup Strategy

**What's Backed Up**:
- [Component 1]: [Backup method]
- [Component 2]: [Backup method]

**Backup Schedule**: [Frequency]
**Retention**: [Duration]

### Recovery Procedure

```bash
# 1. Assess impact
[assessment_command]

# 2. Restore from backup
[restore_command]

# 3. Verify data integrity
[verify_command]

# 4. Resume pipeline
[resume_command]
```

**Recovery Time Objective (RTO)**: [Duration]
**Recovery Point Objective (RPO)**: [Duration]

## Change Management

### Deployment Process

```bash
# 1. Test in dev
dbt run --select tag:[pipeline_tag] --target dev
dbt test --select tag:[pipeline_tag] --target dev

# 2. Deploy to staging
dbt run --select tag:[pipeline_tag] --target staging
dbt test --select tag:[pipeline_tag] --target staging

# 3. Deploy to prod
dbt run --select tag:[pipeline_tag] --target prod
dbt test --select tag:[pipeline_tag] --target prod

# 4. Monitor for issues
[monitoring_command]
```

### Rollout Strategy

- **Canary Deployment**: [If applicable]
- **Blue/Green**: [If applicable]
- **Feature Flags**: [If applicable]

### Testing Requirements

**Pre-Deployment Checklist**:
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Data quality tests pass
- [ ] Performance tests pass
- [ ] Security scan passes
- [ ] Code review approved
- [ ] Documentation updated

## Claude Code Integration

### Common Claude Workflows

**"Debug [pipeline_name] failure"**
```bash
# Claude will:
# 1. Check recent run logs
# 2. Identify error patterns
# 3. Suggest fixes
# 4. Run validation tests
```

**"Optimize [pipeline_name] for cost"**
```bash
# Claude will:
# 1. Analyze query patterns
# 2. Review partitioning/clustering
# 3. Suggest incremental strategies
# 4. Estimate cost savings
```

**"Backfill [pipeline_name] for [date_range]"**
```bash
# Claude will:
# 1. Validate date range
# 2. Check for existing data
# 3. Run backfill
# 4. Verify results
```

### Pipeline Development with Claude

```bash
# 1. Ask Claude to review pipeline design
# "Review the architecture of [pipeline_name] for best practices"

# 2. Ask Claude to add monitoring
# "Add monitoring and alerting for [pipeline_name]"

# 3. Ask Claude to optimize performance
# "Optimize [pipeline_name] to reduce runtime by 50%"

# 4. Ask Claude to add tests
# "Add comprehensive data quality tests for [pipeline_name]"
```

## References

### Documentation Links
- [Source system documentation]
- [Downstream system documentation]
- [Architecture diagrams]
- [Data dictionary]

### Related Runbooks
- [Related pipeline 1]
- [Related pipeline 2]

### Audit Trail
| Date | Change | Author | Ticket |
|------|--------|--------|--------|
| [YYYY-MM-DD] | [Description] | [Name] | [Link] |

## Notes

[Any additional context, edge cases, or tribal knowledge]
