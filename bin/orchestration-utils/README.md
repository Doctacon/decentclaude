# Orchestration Utilities

Utilities for generating orchestration code, monitoring pipeline health, and tracking SLA compliance for data pipelines.

## Tools

### airflow-dag-gen

Generate Airflow DAGs from dbt or SQLMesh project metadata.

**Features:**
- Auto-generate DAGs from dbt manifest.json or SQLMesh models
- Preserve model dependencies and lineage
- Include health checks and SLA monitoring
- Group models by schema (staging, intermediate, marts)
- Configure scheduling from model metadata

**Usage:**

```bash
# Generate from dbt project
airflow-dag-gen \
  --project-type dbt \
  --manifest-path /path/to/dbt/target/manifest.json \
  --output-dir ./dags \
  --schedule daily

# Generate from SQLMesh project
airflow-dag-gen \
  --project-type sqlmesh \
  --project-path /path/to/sqlmesh \
  --output-dir ./dags \
  --schedule hourly
```

**dbt Model Configuration:**

Add metadata to your dbt models to control scheduling and SLA:

```yaml
# schema.yml
models:
  - name: my_model
    meta:
      schedule: daily
      sla_hours: 2
    config:
      materialized: incremental
      partition_by:
        field: event_timestamp
        data_type: timestamp
        granularity: day
```

**Output:**

Generated DAGs include:
- Task definitions for each model
- Dependency relationships
- Health check tasks
- SLA compliance monitoring
- BigQuery operators optimized for your warehouse

### dagster-asset-gen

Generate Dagster assets from dbt or SQLMesh project metadata.

**Features:**
- Auto-generate assets with proper dependencies
- Partitioning and freshness policies from model config
- Asset checks for data quality
- Auto-materialization policies
- Sensors for SLA monitoring and alerting

**Usage:**

```bash
# Generate from dbt project
dagster-asset-gen \
  --project-type dbt \
  --manifest-path /path/to/dbt/target/manifest.json \
  --output-dir ./dagster_assets

# Generate from SQLMesh project
dagster-asset-gen \
  --project-type sqlmesh \
  --project-path /path/to/sqlmesh \
  --output-dir ./dagster_assets
```

**dbt Model Configuration:**

```yaml
models:
  - name: my_model
    meta:
      freshness_hours: 1
      sla_hours: 2
    tags:
      - critical
    config:
      materialized: incremental
      partition_by:
        field: event_timestamp
        granularity: day
```

**Output:**

Generated assets include:
- Asset definitions with dependencies
- Partitioning definitions (daily, hourly, monthly)
- Freshness policies
- Asset checks (row count, freshness)
- Sensors (SLA monitoring, freshness, health checks)
- Repository configuration

### pipeline-health-monitor

Monitor pipeline health and track data quality metrics.

**Features:**
- Data freshness monitoring
- Row count validation
- Query failure detection
- Cost monitoring and alerts
- Partition health checks
- Schema drift detection

**Usage:**

```bash
# Run configured health checks
pipeline-health-monitor --config health-config.json --output results.json

# Check individual table freshness
pipeline-health-monitor --table project.dataset.table --check-freshness

# Check for failed jobs
pipeline-health-monitor --check-failures --hours 24

# Generate cost report
pipeline-health-monitor --cost-report --hours 24
```

**Configuration Example:**

```json
{
  "tables": [
    {
      "table_id": "project.dataset.events",
      "freshness": {
        "timestamp_column": "event_timestamp",
        "max_age_hours": 2
      },
      "row_count": {
        "min_rows": 1000,
        "max_rows": 10000000,
        "partition_column": "event_date",
        "lookback_days": 7
      },
      "check_partitions": true,
      "expected_schema": [
        {"name": "event_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "event_timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
        {"name": "user_id", "type": "STRING", "mode": "NULLABLE"}
      ]
    }
  ],
  "check_failures": true,
  "failure_lookback_hours": 24,
  "check_costs": true,
  "cost_lookback_hours": 24,
  "cost_threshold_usd": 100.0
}
```

**Output:**

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "checks": [
    {
      "table": "project.dataset.events",
      "check": "freshness",
      "status": "PASS",
      "latest_update": "2024-01-15T09:00:00Z",
      "hours_stale": 1.5,
      "max_age_hours": 2
    }
  ],
  "summary": {
    "total_checks": 5,
    "passed": 4,
    "failed": 1,
    "health_score": 80.0
  }
}
```

### sla-tracker

Track and monitor SLA compliance for data pipelines.

**Features:**
- Pipeline completion time SLAs
- Data freshness SLAs
- Data quality SLAs
- Availability SLAs
- Continuous monitoring mode
- Alert on violations (integrates with Slack, PagerDuty)
- Markdown and JSON reports

**Usage:**

```bash
# Check all SLAs
sla-tracker --config sla-config.json

# Generate compliance report
sla-tracker --config sla-config.json --report --format markdown --output report.md

# Continuous monitoring
sla-tracker --config sla-config.json --monitor --interval 300
```

**Configuration Example:**

```json
{
  "pipelines": [
    {
      "name": "daily_aggregation",
      "critical": true,
      "completion_time_sla": {
        "target_duration_minutes": 60,
        "lookback_hours": 24
      }
    }
  ],
  "tables": [
    {
      "table_id": "project.dataset.events",
      "critical": true,
      "freshness_sla": {
        "timestamp_column": "event_timestamp",
        "max_age_hours": 2
      },
      "quality_sla": {
        "query": "SELECT COUNT(*) as total_rows, COUNTIF(user_id IS NULL) as failed_rows FROM `project.dataset.events`",
        "max_failure_rate": 0.01
      },
      "availability_sla": {
        "target_availability": 99.9,
        "lookback_hours": 24
      }
    }
  ]
}
```

**Output:**

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "summary": {
    "total_checks": 10,
    "passed": 8,
    "failed": 2,
    "violations": 2,
    "critical_violations": 1,
    "compliance_rate": 80.0
  },
  "violations": [
    {
      "table": "project.dataset.events",
      "sla_type": "freshness",
      "status": "FAIL",
      "critical": true,
      "hours_stale": 3,
      "max_age_hours": 2,
      "violation_hours": 1
    }
  ]
}
```

## Installation

### Prerequisites

```bash
# Install dependencies
pip install google-cloud-bigquery dagster dagster-gcp apache-airflow
```

### Setup

1. Add utilities to PATH:
```bash
export PATH="$PATH:/path/to/decentclaude/bin/orchestration-utils"
```

2. Configure GCP credentials:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

## Integration Patterns

### Airflow Integration

1. Generate DAGs from your dbt project:
```bash
cd /path/to/dbt/project
dbt compile  # Generate manifest.json
airflow-dag-gen --project-type dbt --manifest-path target/manifest.json --output-dir $AIRFLOW_HOME/dags
```

2. Deploy to Airflow:
```bash
# DAGs are automatically loaded from $AIRFLOW_HOME/dags
airflow dags list
```

### Dagster Integration

1. Generate assets:
```bash
dagster-asset-gen --project-type dbt --manifest-path target/manifest.json --output-dir dagster_assets
```

2. Run Dagster:
```bash
cd dagster_assets
dagster dev
```

### CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/data-quality.yml
name: Data Quality Checks

on: [push, pull_request]

jobs:
  health-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Check pipeline health
        run: |
          pipeline-health-monitor --config health-config.json --output health-results.json

      - name: Check SLA compliance
        run: |
          sla-tracker --config sla-config.json --report --format markdown --output sla-report.md

      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: health-reports
          path: |
            health-results.json
            sla-report.md
```

### Monitoring Integration

Set up continuous monitoring with cron:

```bash
# Add to crontab
# Check pipeline health every 15 minutes
*/15 * * * * /path/to/pipeline-health-monitor --config /path/to/health-config.json >> /var/log/health-monitor.log 2>&1

# Monitor SLAs every 5 minutes
*/5 * * * * /path/to/sla-tracker --config /path/to/sla-config.json >> /var/log/sla-tracker.log 2>&1
```

## Best Practices

### Model Organization

Organize your dbt/SQLMesh models to maximize DAG generation:

```
models/
├── staging/       # stg_ prefix - raw data ingestion
├── intermediate/  # int_ prefix - business logic transformations
└── marts/         # fct_/dim_ prefix - final analytics tables
```

### Metadata Configuration

Add comprehensive metadata to models:

```yaml
models:
  - name: fct_orders
    description: "Order facts table"
    meta:
      # Scheduling
      schedule: daily

      # SLAs
      sla_hours: 2
      freshness_hours: 1

      # Criticality
      critical: true

      # Ownership
      owner: data-team@company.com

    tags:
      - critical
      - daily
```

### Health Check Strategy

1. **Tier your checks:**
   - Critical tables: Check every 5-15 minutes
   - Important tables: Check hourly
   - Other tables: Check daily

2. **Set realistic SLAs:**
   - Base on historical performance
   - Add buffer for variability
   - Review and adjust quarterly

3. **Alert fatigue prevention:**
   - Only page for critical violations
   - Use warnings for non-critical
   - Aggregate multiple failures

### Cost Management

Monitor costs to avoid surprises:

```bash
# Daily cost report
pipeline-health-monitor --cost-report --hours 24 > daily-cost-report.txt

# Alert on high costs
if [ $(jq '.total_cost_usd' daily-cost-report.txt) -gt 100 ]; then
  echo "High cost detected!" | mail -s "BigQuery Cost Alert" team@company.com
fi
```

## Troubleshooting

### DAG Generation Issues

**Problem:** Models not appearing in generated DAG

- Verify manifest.json is up to date: `dbt compile`
- Check model resource_type is "model"
- Ensure models have proper dependencies

**Problem:** Dependencies missing in DAG

- Check `depends_on` in manifest.json
- Verify ref() usage in dbt models
- Use `dbt list --resource-type model` to verify model graph

### Health Check Issues

**Problem:** "Table not found" errors

- Verify table_id format: `project.dataset.table`
- Check GCP credentials and permissions
- Ensure table exists: `bq show project:dataset.table`

**Problem:** Schema drift false positives

- Update expected schema in config
- Use `bq show --schema --format=prettyjson project:dataset.table` to get current schema

### SLA Violations

**Problem:** Constant freshness violations

- Review upstream dependencies
- Check for pipeline failures
- Verify timestamp_column exists and is populated

**Problem:** Completion time SLA failures

- Profile query performance
- Check for data volume changes
- Consider partitioning/clustering optimization

## Support

For issues or questions:
- Check existing patterns in `/docs/templates/`
- Review playbooks in `/playbooks.md`
- File issue in project repository
