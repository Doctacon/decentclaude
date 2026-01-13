# Orchestration Integration Guide

This guide covers how to integrate your dbt or SQLMesh projects with orchestration platforms (Airflow, Dagster) using the DecentClaude orchestration utilities.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Airflow Integration](#airflow-integration)
- [Dagster Integration](#dagster-integration)
- [Monitoring and SLA Tracking](#monitoring-and-sla-tracking)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)

## Overview

The orchestration utilities provide auto-generation of:
- **Airflow DAGs** from dbt/SQLMesh metadata
- **Dagster assets** with dependencies and checks
- **Pipeline health monitoring** for BigQuery
- **SLA compliance tracking** and alerting

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│              dbt/SQLMesh Models                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  Staging    │  │Intermediate │  │    Marts    │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└────────────┬────────────────────────────────────────────┘
             │
             │ Parse metadata
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│         Orchestration Generators                        │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │ airflow-dag-gen  │    │dagster-asset-gen │          │
│  └──────────────────┘    └──────────────────┘          │
└────────────┬────────────────────┬─────────────────────┘
             │                    │
             ▼                    ▼
┌─────────────────────┐  ┌─────────────────────┐
│   Airflow DAGs      │  │  Dagster Assets     │
│  - Task deps        │  │  - Asset deps       │
│  - Scheduling       │  │  - Partitioning     │
│  - Health checks    │  │  - Asset checks     │
└─────────────────────┘  └─────────────────────┘
             │                    │
             └────────┬───────────┘
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Monitoring & SLA Tracking                  │
│  ┌────────────────────┐  ┌────────────────────┐        │
│  │pipeline-health-    │  │   sla-tracker      │        │
│  │     monitor        │  │                    │        │
│  └────────────────────┘  └────────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Prepare Your dbt Project

Add orchestration metadata to your models:

```yaml
# models/schema.yml
models:
  - name: fct_orders
    meta:
      schedule: daily
      sla_hours: 2
      freshness_hours: 1
      critical: true
    tags:
      - daily
      - critical
    config:
      materialized: incremental
      partition_by:
        field: order_date
        data_type: date
        granularity: day
```

### 2. Compile Your Project

```bash
cd /path/to/dbt/project
dbt compile
```

### 3. Generate Orchestration Code

```bash
# For Airflow
airflow-dag-gen \
  --project-type dbt \
  --manifest-path target/manifest.json \
  --output-dir ./dags

# For Dagster
dagster-asset-gen \
  --project-type dbt \
  --manifest-path target/manifest.json \
  --output-dir ./dagster_assets
```

### 4. Set Up Monitoring

```bash
# Create health check config
cp examples/orchestration/health-config.json ./health-config.json

# Create SLA config
cp examples/orchestration/sla-config.json ./sla-config.json

# Run health checks
pipeline-health-monitor --config health-config.json

# Check SLA compliance
sla-tracker --config sla-config.json --report
```

## Airflow Integration

### Project Structure

```
your_dbt_project/
├── dbt_project.yml
├── models/
│   ├── staging/
│   ├── intermediate/
│   └── marts/
└── target/
    └── manifest.json

airflow_project/
├── dags/
│   ├── dbt_staging.py        # Generated
│   ├── dbt_intermediate.py   # Generated
│   └── dbt_marts.py          # Generated
└── config/
    └── health-config.json
```

### Generation Process

1. **Parse dbt manifest:**
   - Extract models and dependencies
   - Read configuration and metadata
   - Identify scheduling requirements

2. **Generate DAG files:**
   - Group models by schema/layer
   - Create task definitions
   - Set up dependencies
   - Add health checks

3. **Deploy to Airflow:**
   - Copy DAGs to `$AIRFLOW_HOME/dags`
   - Airflow automatically loads them

### Generated DAG Structure

```python
# dbt_marts.py (example)
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator

dag = DAG(
    'dbt_marts',
    schedule_interval='@daily',
    default_args={...},
)

# Model tasks
fct_orders = BigQueryInsertJobOperator(
    task_id='fct_orders',
    configuration={...},
    sla=timedelta(hours=2),
    dag=dag,
)

dim_customers = BigQueryInsertJobOperator(
    task_id='dim_customers',
    configuration={...},
    dag=dag,
)

# Dependencies from dbt lineage
dim_customers >> fct_orders

# Health check
health_check = PythonOperator(
    task_id='check_pipeline_health',
    python_callable=check_pipeline_health,
    dag=dag,
)

fct_orders >> health_check
```

### Customization

Edit generated DAGs to add:
- Custom operators
- Additional tasks (quality checks, notifications)
- Alert configurations
- Cost controls

### Deployment

```bash
# Option 1: Copy to Airflow DAGs folder
cp ./dags/* $AIRFLOW_HOME/dags/

# Option 2: Use Git sync (Cloud Composer)
git add dags/
git commit -m "Update generated DAGs"
git push

# Verify
airflow dags list | grep dbt
```

## Dagster Integration

### Project Structure

```
dagster_project/
├── dagster_assets/
│   ├── __init__.py          # Generated repository
│   ├── staging_assets.py    # Generated staging assets
│   ├── intermediate_assets.py
│   ├── marts_assets.py
│   ├── sensors.py           # Generated sensors
│   └── pyproject.toml
└── dagster.yaml
```

### Generation Process

1. **Parse dbt manifest:**
   - Extract models and dependencies
   - Read partitioning configuration
   - Identify freshness requirements

2. **Generate asset files:**
   - Create asset definitions per layer
   - Set up dependencies
   - Configure partitioning
   - Add asset checks

3. **Generate sensors:**
   - SLA monitoring
   - Freshness checks
   - Health monitoring

4. **Create repository:**
   - Load all assets
   - Register sensors
   - Configure resources

### Generated Asset Structure

```python
# marts_assets.py (example)
from dagster import asset, DailyPartitionsDefinition, FreshnessPolicy

@asset(
    name="fct_orders",
    ins={"dim_customers": AssetIn("dim_customers")},
    partitions_def=DailyPartitionsDefinition(start_date="2024-01-01"),
    freshness_policy=FreshnessPolicy(maximum_lag_minutes=60),
    auto_materialize_policy=AutoMaterializePolicy.eager(),
)
def fct_orders(context, dim_customers):
    """Orders fact table"""
    # Materialization logic
    ...

@asset_check(asset=fct_orders)
def check_fct_orders_row_count(context):
    """Verify row count is within expected range"""
    # Check logic
    ...
```

### Running Dagster

```bash
cd dagster_assets

# Development
dagster dev

# Production
dagster-daemon run
```

### Asset Materialization

```bash
# Materialize all assets
dagster asset materialize --select '*'

# Materialize specific asset
dagster asset materialize --select fct_orders

# Materialize asset partition
dagster asset materialize --select fct_orders --partition 2024-01-15
```

## Monitoring and SLA Tracking

### Health Monitoring Setup

1. **Create configuration:**

```json
{
  "tables": [
    {
      "table_id": "project.dataset.fct_orders",
      "freshness": {
        "timestamp_column": "created_at",
        "max_age_hours": 2
      },
      "row_count": {
        "min_rows": 1000,
        "partition_column": "order_date",
        "lookback_days": 7
      }
    }
  ],
  "check_failures": true,
  "check_costs": true,
  "cost_threshold_usd": 100
}
```

2. **Run checks:**

```bash
# One-time check
pipeline-health-monitor --config health-config.json --output results.json

# Continuous monitoring (every 5 minutes)
while true; do
  pipeline-health-monitor --config health-config.json --output results.json
  sleep 300
done
```

### SLA Tracking Setup

1. **Create SLA configuration:**

```json
{
  "pipelines": [
    {
      "name": "daily_aggregation",
      "critical": true,
      "completion_time_sla": {
        "target_duration_minutes": 60
      }
    }
  ],
  "tables": [
    {
      "table_id": "project.dataset.fct_orders",
      "critical": true,
      "freshness_sla": {
        "timestamp_column": "created_at",
        "max_age_hours": 2
      }
    }
  ]
}
```

2. **Monitor SLAs:**

```bash
# Check compliance
sla-tracker --config sla-config.json

# Generate report
sla-tracker --config sla-config.json --report --format markdown --output sla-report.md

# Continuous monitoring
sla-tracker --config sla-config.json --monitor --interval 300
```

### Alerting Integration

Extend monitoring utilities to send alerts:

```python
# Add to health monitor or SLA tracker
def send_alert(violation):
    if violation['critical']:
        # Slack
        slack_client.post_message(
            channel='#data-alerts',
            text=f"🚨 Critical SLA violation: {violation['table']}"
        )

        # PagerDuty
        pagerduty_client.trigger_incident(
            title=f"Data SLA Violation",
            details=violation
        )

    # Email for non-critical
    send_email(
        to='data-team@company.com',
        subject='SLA Violation',
        body=json.dumps(violation, indent=2)
    )
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/data-pipeline.yml
name: Data Pipeline CI/CD

on:
  push:
    branches: [main]
    paths:
      - 'models/**'
      - 'dbt_project.yml'

jobs:
  generate-orchestration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install dbt-bigquery dagster google-cloud-bigquery

      - name: Compile dbt
        run: |
          cd dbt_project
          dbt compile

      - name: Generate Airflow DAGs
        run: |
          airflow-dag-gen \
            --project-type dbt \
            --manifest-path dbt_project/target/manifest.json \
            --output-dir airflow_dags

      - name: Generate Dagster assets
        run: |
          dagster-asset-gen \
            --project-type dbt \
            --manifest-path dbt_project/target/manifest.json \
            --output-dir dagster_assets

      - name: Health checks
        run: |
          pipeline-health-monitor \
            --config health-config.json \
            --output health-results.json

      - name: SLA compliance
        run: |
          sla-tracker \
            --config sla-config.json \
            --report \
            --format markdown \
            --output sla-report.md

      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: orchestration-artifacts
          path: |
            airflow_dags/
            dagster_assets/
            health-results.json
            sla-report.md

      - name: Deploy to Airflow
        if: github.ref == 'refs/heads/main'
        run: |
          # Deploy DAGs to Cloud Composer
          gcloud composer environments storage dags import \
            --environment $COMPOSER_ENV \
            --location $COMPOSER_LOCATION \
            --source airflow_dags/
```

### GitLab CI Example

```yaml
# .gitlab-ci.yml
stages:
  - compile
  - generate
  - test
  - deploy

compile_dbt:
  stage: compile
  script:
    - cd dbt_project
    - dbt compile
  artifacts:
    paths:
      - dbt_project/target/

generate_airflow:
  stage: generate
  dependencies:
    - compile_dbt
  script:
    - airflow-dag-gen \
        --project-type dbt \
        --manifest-path dbt_project/target/manifest.json \
        --output-dir airflow_dags
  artifacts:
    paths:
      - airflow_dags/

health_checks:
  stage: test
  script:
    - pipeline-health-monitor --config health-config.json --output results.json
    - sla-tracker --config sla-config.json --report --output sla-report.json
  artifacts:
    reports:
      junit: results.json

deploy_production:
  stage: deploy
  only:
    - main
  script:
    - cp airflow_dags/* $AIRFLOW_DAGS_FOLDER/
```

## Best Practices

### Model Organization

1. **Follow naming conventions:**
   - `stg_*` for staging models
   - `int_*` for intermediate models
   - `fct_*` for fact tables
   - `dim_*` for dimension tables

2. **Use consistent metadata:**
```yaml
meta:
  schedule: daily|hourly|weekly
  sla_hours: <number>
  freshness_hours: <number>
  critical: true|false
  owner: <email>
```

3. **Tag strategically:**
```yaml
tags:
  - <schedule>  # daily, hourly, weekly
  - <layer>     # staging, intermediate, marts
  - critical    # for critical tables
```

### Scheduling Strategy

1. **Align with data availability:**
   - Schedule after upstream data arrives
   - Add buffer for processing time
   - Consider timezone differences

2. **Optimize for cost:**
   - Batch similar models together
   - Use incremental materialization
   - Leverage partitioning and clustering

3. **Balance freshness vs resources:**
   - Not everything needs hourly updates
   - Critical dashboards: more frequent
   - Historical reports: less frequent

### SLA Management

1. **Set realistic SLAs:**
   - Base on historical performance
   - Add 20-30% buffer
   - Review quarterly

2. **Tier your SLAs:**
   - Critical (revenue, compliance): tight SLAs
   - Important (core analytics): moderate SLAs
   - Nice-to-have (experimental): loose SLAs

3. **Monitor trends:**
   - Track SLA compliance over time
   - Identify degradation early
   - Adjust SLAs as needed

### Cost Optimization

1. **Monitor query costs:**
```bash
# Daily cost check
pipeline-health-monitor --cost-report --hours 24 | \
  jq '.total_cost_usd' | \
  awk '{if ($1 > 100) print "High cost alert!"}'
```

2. **Optimize expensive queries:**
   - Use partitioning
   - Add clustering
   - Limit full table scans
   - Use incremental models

3. **Set cost alerts:**
```json
{
  "check_costs": true,
  "cost_threshold_usd": 100.0
}
```

### Troubleshooting

**DAG not generating:**
- Check manifest.json exists and is valid
- Verify models have resource_type='model'
- Check for circular dependencies

**Asset checks failing:**
- Verify table permissions
- Check query syntax
- Review expected value ranges

**SLA violations:**
- Profile query performance
- Check upstream dependencies
- Review partition strategy
- Consider scaling resources

**High costs:**
- Identify expensive queries
- Review partition pruning
- Check for full table scans
- Optimize transformations

## Advanced Topics

### Custom Health Checks

Extend the health monitor:

```python
def custom_business_logic_check(table_id):
    """Custom check for business logic"""
    query = f"""
    SELECT
        COUNT(*) as total,
        COUNTIF(revenue > refunds) as valid
    FROM `{table_id}`
    WHERE DATE(order_date) = CURRENT_DATE()
    """
    # Run check and return result
```

### Multi-Environment Setup

```bash
# Development
airflow-dag-gen \
  --project-type dbt \
  --manifest-path target/manifest.json \
  --output-dir dev_dags

# Production
airflow-dag-gen \
  --project-type dbt \
  --manifest-path target/manifest.json \
  --output-dir prod_dags
```

### Cross-Platform Migration

Migrate from Airflow to Dagster:

1. Generate both orchestrations from same manifest
2. Run in parallel during transition
3. Compare outputs
4. Gradually migrate workflows
5. Decommission old platform

## Resources

- [Airflow Documentation](https://airflow.apache.org/docs/)
- [Dagster Documentation](https://docs.dagster.io/)
- [dbt Documentation](https://docs.getdbt.com/)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [DecentClaude Data Engineering Patterns](./data-engineering-patterns.md)
- [DecentClaude Playbooks](./playbooks.md)
