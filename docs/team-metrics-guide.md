# Team Metrics and Reporting Guide

A comprehensive analytics and reporting system for data engineering teams, providing insights into query performance, costs, pipeline health, test coverage, documentation quality, and team contributions.

## Overview

The team metrics system consists of:

1. **Core Metrics Module** (`scripts/team_metrics.py`) - Python library for collecting BigQuery metrics
2. **CLI Tool** (`bin/data-utils/bq-metrics`) - Command-line interface for exporting metrics
3. **Web Dashboard** (`scripts/metrics_dashboard.py`) - Interactive visualization dashboard

## Features

### Metrics Collected

#### 1. Query Performance Trends
- Query count over time
- Average and P95 slot seconds
- Average GB processed
- Error rates
- Cache hit rates

#### 2. Cost Tracking
- Daily costs by user
- TB billed per user/team
- Cost breakdowns by project
- Historical cost trends

#### 3. Pipeline Success Rates
- Job success rates by type
- Error counts
- Average job durations
- State tracking (DONE, FAILED, etc.)

#### 4. Test Coverage
- Test table counts vs production tables
- Coverage percentage by dataset
- Test completeness indicators

#### 5. Documentation Completeness
- Table description coverage
- Column description coverage
- Documentation quality scores by dataset

#### 6. Contribution Analytics
- Active days per user
- Total queries per user
- Data processed per user
- Job type distribution

## Installation

### Prerequisites

```bash
pip install google-cloud-bigquery flask
```

### Setup

1. Ensure you have BigQuery access configured:
```bash
gcloud auth application-default login
```

2. Make the CLI tool executable:
```bash
chmod +x bin/data-utils/bq-metrics
```

3. Add the bin directory to your PATH (optional):
```bash
export PATH="$PATH:$(pwd)/bin/data-utils"
```

## Usage

### CLI Tool

#### Basic Usage

```bash
# Export all metrics for last 7 days in text format
bq-metrics --days 7

# Export as JSON for dashboard integration
bq-metrics --days 30 --format json

# Export specific metric categories
bq-metrics --metrics costs,performance --days 7

# Filter by team or project
bq-metrics --team data-platform --days 30

# Export to file
bq-metrics --days 30 --format json > metrics.json
```

#### Available Options

- `--days N` - Number of days to look back (default: 30)
- `--format text|json` - Output format (default: text)
- `--metrics CATEGORIES` - Comma-separated list of metrics:
  - `performance` - Query performance trends
  - `costs` - Cost tracking
  - `pipeline` - Pipeline success rates
  - `tests` - Test coverage
  - `documentation` - Documentation completeness
  - `contributions` - User contributions
- `--team NAME` - Filter by team name
- `--project NAME` - Filter by project name
- `--project-id ID` - GCP project ID (uses default if not specified)

#### Example Outputs

**Text Format:**
```
Team Metrics Report
Generated: 2026-01-12 17:30:00
================================================================================

QUERY PERFORMANCE
--------------------------------------------------------------------------------
Date         Queries    Avg GB       P95 Slots    Errors     Cache %
2026-01-12   1,234      45.67        12.34        5          23.4
2026-01-11   1,189      43.21        11.89        3          25.1
...

COSTS
--------------------------------------------------------------------------------
Date         User                            TB Billed    Cost (USD)
2026-01-12   user1@example.com               2.3456       $11.73
2026-01-12   user2@example.com               1.2345       $6.17
...
```

**JSON Format:**
```json
{
  "query_performance": [
    {
      "metric_name": "query_performance_daily",
      "value": {
        "date": "2026-01-12",
        "query_count": 1234,
        "avg_slot_seconds": 45.67,
        "avg_gb_processed": 12.34,
        "p95_slot_seconds": 56.78,
        "error_count": 5,
        "cache_hit_count": 289,
        "cache_hit_rate": 23.4
      },
      "unit": "daily_stats",
      "timestamp": "2026-01-12T00:00:00"
    }
  ],
  "costs": [...],
  ...
}
```

### Web Dashboard

#### Starting the Dashboard

```bash
# Start with default settings (port 5000, 30 days)
python scripts/metrics_dashboard.py

# Custom port and time range
python scripts/metrics_dashboard.py --port 8080 --days 60

# Specify GCP project
python scripts/metrics_dashboard.py --project-id my-project-id

# Run in debug mode
python scripts/metrics_dashboard.py --debug
```

#### Accessing the Dashboard

Open your browser to `http://localhost:5000` (or your specified port)

#### Dashboard Features

- **Summary Cards** - Key metrics at a glance
- **Interactive Charts** - Visualizations using Chart.js
- **Time Range Selection** - View data for 7, 14, 30, 60, or 90 days
- **Auto-Refresh** - Updates every 5 minutes
- **Responsive Design** - Works on desktop and mobile

#### Dashboard Sections

1. **Summary Cards**
   - Total Queries
   - Total Cost
   - Average Success Rate
   - Test Coverage
   - Documentation Coverage
   - Active Users

2. **Charts**
   - Query Performance Trends (line chart)
   - Daily Costs (bar chart)
   - Pipeline Success Rates (bar chart)
   - Test Coverage by Dataset (horizontal bar chart)
   - Documentation Coverage (grouped horizontal bar chart)
   - Top Contributors (horizontal bar chart)

### Python API

#### Using the Metrics Collector Directly

```python
from scripts.team_metrics import TeamMetricsCollector

# Initialize collector
collector = TeamMetricsCollector(project_id='my-project-id')

# Collect specific metrics
performance = collector.get_query_performance_trends(days=30)
costs = collector.get_cost_tracking(days=30)
pipeline = collector.get_pipeline_success_rates(days=30)
tests = collector.get_test_coverage_metrics()
docs = collector.get_documentation_completeness()
contributions = collector.get_contribution_analytics(days=30)

# Collect all metrics at once
all_metrics = collector.collect_all_metrics(
    days=30,
    team_filter='data-platform',
    project_filter='analytics'
)

# Export to JSON
json_output = collector.export_to_json(all_metrics)
```

#### Metric Result Structure

```python
@dataclass
class MetricResult:
    metric_name: str      # Name of the metric
    value: Any           # Metric data (dict or scalar)
    unit: str            # Unit of measurement
    timestamp: datetime  # When the metric was collected
    metadata: Dict       # Additional metadata
```

## Integration Examples

### Daily Report Email

```bash
#!/bin/bash
# daily-metrics-report.sh

# Generate metrics report
REPORT=$(bq-metrics --days 1 --format text)

# Email the report
echo "$REPORT" | mail -s "Daily Team Metrics Report" team@example.com
```

### CI/CD Pipeline Integration

```yaml
# .github/workflows/metrics.yml
name: Collect Metrics

on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight

jobs:
  metrics:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Collect metrics
        run: |
          bin/data-utils/bq-metrics --days 1 --format json > metrics.json
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: metrics
          path: metrics.json
```

### Alerting on High Costs

```python
from scripts.team_metrics import TeamMetricsCollector

collector = TeamMetricsCollector()
costs = collector.get_cost_tracking(days=1)

# Calculate today's total cost
total_cost = sum(r.value['cost_usd'] for r in costs)

# Alert if cost exceeds threshold
if total_cost > 100:
    print(f"ALERT: Daily cost ${total_cost:.2f} exceeds threshold!")
    # Send alert via Slack, PagerDuty, etc.
```

## Best Practices

### Data Collection

1. **Regular Monitoring** - Set up daily or hourly collection for trending
2. **Historical Archive** - Store metrics in a separate BigQuery table for long-term analysis
3. **Baseline Establishment** - Collect at least 30 days of data to establish normal patterns
4. **Team Labels** - Use consistent team/project labels for filtering

### Cost Optimization

1. **Monitor P95 Slot Times** - High slot times indicate inefficient queries
2. **Track Cache Hit Rates** - Low rates suggest opportunities for query optimization
3. **Identify High-Cost Users** - Focus optimization efforts on top spenders
4. **Set Cost Budgets** - Alert when daily/weekly costs exceed thresholds

### Quality Metrics

1. **Test Coverage Goals** - Aim for >80% test coverage on production datasets
2. **Documentation Standards** - Require descriptions on all tables and key columns
3. **Pipeline SLAs** - Monitor success rates and set alerts for <95% success
4. **Review Cycles** - Weekly review of metrics with team

### Dashboard Usage

1. **Team Standups** - Display dashboard during daily standups
2. **Sprint Planning** - Use trends to inform capacity planning
3. **Incident Review** - Correlate metrics with incidents for root cause analysis
4. **Executive Reporting** - Export JSON for executive dashboards

## Troubleshooting

### Common Issues

#### "Permission denied" errors

Ensure you have BigQuery access:
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

#### "Module not found" errors

Add the scripts directory to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/scripts"
```

#### Empty or missing metrics

Check that:
1. Your GCP project has BigQuery job history (run some queries first)
2. You have access to `INFORMATION_SCHEMA.JOBS_BY_PROJECT`
3. The time range includes data (try a longer `--days` value)

#### Dashboard not loading

1. Check Flask is installed: `pip install flask`
2. Ensure port is not in use: `lsof -i :5000`
3. Check browser console for JavaScript errors

### Performance Considerations

- **Large Projects** - For projects with millions of jobs, consider:
  - Reducing the `--days` parameter
  - Using table partitioning for archived metrics
  - Implementing result caching

- **API Quotas** - BigQuery INFORMATION_SCHEMA queries count against quotas:
  - Monitor quota usage in GCP Console
  - Implement rate limiting if needed
  - Cache results when possible

## Advanced Usage

### Custom Metrics

Extend the `TeamMetricsCollector` class:

```python
class CustomMetricsCollector(TeamMetricsCollector):
    def get_custom_metric(self):
        query = """
        SELECT
            custom_field,
            COUNT(*) as count
        FROM
            `project.dataset.table`
        GROUP BY
            custom_field
        """
        # Implementation...
```

### Exporting to Data Warehouse

```python
from google.cloud import bigquery

collector = TeamMetricsCollector()
metrics = collector.collect_all_metrics(days=1)

# Insert into BigQuery table
client = bigquery.Client()
table_id = "project.dataset.team_metrics"

rows_to_insert = []
for category, results in metrics.items():
    for result in results:
        row = {
            "category": category,
            "metric_name": result.metric_name,
            "value": json.dumps(result.value),
            "timestamp": result.timestamp.isoformat()
        }
        rows_to_insert.append(row)

errors = client.insert_rows_json(table_id, rows_to_insert)
```

## Metrics Schema Reference

### query_performance_daily

```json
{
  "date": "YYYY-MM-DD",
  "query_count": int,
  "avg_slot_seconds": float,
  "avg_gb_processed": float,
  "median_slot_seconds": float,
  "p95_slot_seconds": float,
  "error_count": int,
  "cache_hit_count": int,
  "cache_hit_rate": float
}
```

### cost_by_user_daily

```json
{
  "date": "YYYY-MM-DD",
  "user": "email@example.com",
  "tb_billed": float,
  "cost_usd": float,
  "query_count": int
}
```

### pipeline_success_rate

```json
{
  "date": "YYYY-MM-DD",
  "job_type": "QUERY|LOAD|COPY|EXTRACT",
  "state": "DONE|FAILED|...",
  "job_count": int,
  "error_count": int,
  "success_rate": float,
  "avg_duration_seconds": float
}
```

### test_coverage_by_dataset

```json
{
  "dataset": "project.dataset",
  "prod_table_count": int,
  "test_table_count": int,
  "coverage_percentage": float
}
```

### documentation_completeness

```json
{
  "dataset": "project.dataset",
  "total_tables": int,
  "documented_tables": int,
  "table_doc_percentage": float,
  "total_columns": int,
  "documented_columns": int,
  "column_doc_percentage": float
}
```

### user_contributions

```json
{
  "user": "email@example.com",
  "active_days": int,
  "total_queries": int,
  "tb_processed": float,
  "load_jobs": int,
  "query_jobs": int,
  "copy_jobs": int,
  "extract_jobs": int,
  "avg_job_duration_seconds": float
}
```

## Future Enhancements

Potential additions to the metrics system:

- [ ] Alert system with configurable thresholds
- [ ] Historical comparison (this week vs last week)
- [ ] Anomaly detection using statistical methods
- [ ] Cost forecasting based on trends
- [ ] Team leaderboards and gamification
- [ ] Integration with dbt metrics
- [ ] Slack/Teams bot for on-demand metrics
- [ ] Export to Prometheus/Grafana
- [ ] Machine learning for query optimization recommendations
- [ ] Carbon footprint tracking

## Support

For questions or issues:
- Check the troubleshooting section above
- Review example outputs and usage patterns
- Examine the source code for implementation details
- Open an issue in the project repository
