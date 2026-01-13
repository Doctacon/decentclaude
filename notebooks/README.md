# BigQuery Utility Notebooks

Interactive Jupyter notebooks demonstrating the BigQuery data utilities.

## Notebooks

### 1. bigquery-exploration.ipynb

Explore BigQuery tables using the bq-* utilities:
- Profile tables with `bq-profile`
- Compare schemas with `bq-schema-diff`
- Analyze table lineage with `bq-lineage`
- Visualize data distributions and quality metrics

**Use Cases:**
- Data discovery and exploration
- Schema analysis and comparison
- Understanding data lineage
- Multi-table profiling

### 2. data-quality-workflow.ipynb

Complete data quality workflow:
- Comprehensive table profiling
- NULL value analysis
- Uniqueness and duplicate detection
- Data completeness checks
- Quality scorecard generation
- Actionable recommendations

**Use Cases:**
- Data quality audits
- Quality monitoring dashboards
- Data validation workflows
- Quality scorecard reporting

### 3. cost-optimization.ipynb

Query cost analysis and optimization:
- Cost estimation with dry runs
- Query optimization analysis
- Performance benchmarking
- Cost trend analysis
- ROI calculations for optimizations
- Optimization checklists

**Use Cases:**
- Cost reduction initiatives
- Query optimization
- Budget planning
- Performance tuning

## Setup

### Prerequisites

1. Python 3.7+
2. Google Cloud SDK with BigQuery access
3. Jupyter or JupyterLab

### Installation

```bash
# Install required packages
pip install -r requirements-notebooks.txt

# Authenticate with Google Cloud
gcloud auth application-default login

# Set your default project
gcloud config set project YOUR_PROJECT_ID
```

### Starting Jupyter

```bash
# From the notebooks directory
jupyter notebook

# Or use JupyterLab
jupyter lab
```

## Using the Notebooks

### Quick Start

1. Open any notebook in Jupyter
2. Run the setup cells to import libraries
3. Modify the configuration cells with your table IDs
4. Execute cells sequentially

### Working with Public Datasets

The notebooks use BigQuery public datasets by default:
- `bigquery-public-data.stackoverflow.*`
- `bigquery-public-data.usa_names.*`
- Other public datasets

You can explore available public datasets:
```sql
SELECT * FROM `bigquery-public-data.INFORMATION_SCHEMA.SCHEMATA`
```

### Adapting for Your Data

To use your own tables:

1. Replace table IDs in configuration cells:
```python
TABLE_ID = 'your-project.your-dataset.your-table'
```

2. Update quality thresholds as needed:
```python
THRESHOLDS = {
    'max_null_percentage': 10.0,
    'min_completeness': 90.0,
    # ...
}
```

3. Modify queries to match your schema

## Common Tasks

### Profile a New Table

```python
from pathlib import Path
import subprocess
import json

UTILS_DIR = Path('../bin/data-utils')

def run_util(util_name, args):
    util_path = UTILS_DIR / util_name
    result = subprocess.run([str(util_path)] + args,
                          capture_output=True, text=True)
    return json.loads(result.stdout)

# Profile table
profile = run_util('bq-profile', [
    'your-project.dataset.table',
    '--format=json'
])
```

### Compare Two Schemas

```python
schema_diff = run_util('bq-schema-diff', [
    'project.dataset.table_v1',
    'project.dataset.table_v2',
    '--format=json'
])

print(f"Identical: {schema_diff['identical']}")
```

### Estimate Query Cost

```python
from google.cloud import bigquery

client = bigquery.Client()

query = """
SELECT * FROM `project.dataset.table`
WHERE date >= '2024-01-01'
"""

job_config = bigquery.QueryJobConfig(dry_run=True)
query_job = client.query(query, job_config=job_config)

bytes_processed = query_job.total_bytes_processed
cost = (bytes_processed / (1024**4)) * 5.00  # $5 per TB

print(f"Estimated cost: ${cost:.4f}")
```

## Customization

### Adding Custom Checks

Edit `data-quality-workflow.ipynb` to add domain-specific checks:

```python
def custom_quality_check(df):
    """Your custom quality check logic."""
    # Example: Check for future dates
    future_dates = df[df['date'] > pd.Timestamp.now()]

    if len(future_dates) > 0:
        return {
            'passed': False,
            'message': f'Found {len(future_dates)} future dates'
        }
    return {'passed': True, 'message': 'No future dates'}
```

### Creating New Visualizations

Use the provided helper functions and extend with your own:

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_metric_over_time(df, metric_col, date_col):
    """Plot a metric over time."""
    plt.figure(figsize=(12, 6))
    plt.plot(df[date_col], df[metric_col], marker='o')
    plt.xlabel('Date')
    plt.ylabel(metric_col)
    plt.title(f'{metric_col} Over Time')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
```

## Best Practices

### Performance

- Use `--format=json` for programmatic parsing
- Enable caching for repeated metadata queries
- Use `LIMIT` in exploratory queries
- Profile smaller tables first to understand patterns

### Cost Management

- Always use dry runs to estimate costs
- Start with public datasets for testing
- Set query timeouts to avoid runaway costs
- Monitor actual vs. estimated costs

### Notebook Organization

- Keep configuration in top cells
- Document assumptions and thresholds
- Save outputs before closing notebooks
- Version control your modified notebooks

## Troubleshooting

### Authentication Issues

```bash
# Re-authenticate
gcloud auth application-default login

# Check current auth
gcloud auth list
```

### Permission Errors

Ensure your account has:
- `bigquery.jobs.create` - Run queries
- `bigquery.tables.get` - Read table metadata
- `bigquery.tables.getData` - Read table data

### Utility Not Found

```bash
# Check utilities exist
ls -la ../bin/data-utils/

# Make utilities executable
chmod +x ../bin/data-utils/bq-*
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements-notebooks.txt --upgrade

# Check installations
pip list | grep -E "google-cloud-bigquery|pandas|matplotlib"
```

## Examples Gallery

### Example 1: Daily Data Quality Report

```python
# Profile all tables in a dataset
tables = ['table1', 'table2', 'table3']
dataset = 'your-project.your-dataset'

daily_report = []
for table in tables:
    profile = run_util('bq-profile', [
        f'{dataset}.{table}',
        '--format=json'
    ])
    daily_report.append(profile)

# Generate summary
df_summary = pd.DataFrame([
    {
        'Table': p['table_id'],
        'Rows': p['table_overview']['num_rows'],
        'Quality Score': calculate_quality_score(p)
    }
    for p in daily_report
])
```

### Example 2: Cost Optimization Pipeline

```python
# Identify expensive queries
expensive_queries = identify_expensive_queries()

# Analyze each query
for query in expensive_queries:
    suggestions = analyze_query(query)
    cost_before = estimate_cost(query)

    # Apply optimizations
    optimized_query = apply_optimizations(query, suggestions)
    cost_after = estimate_cost(optimized_query)

    print(f"Savings: ${cost_before - cost_after:.2f}")
```

### Example 3: Schema Evolution Tracking

```python
# Track schema changes over time
versions = ['v1', 'v2', 'v3']
changes = []

for i in range(len(versions) - 1):
    diff = run_util('bq-schema-diff', [
        f'project.dataset.table_{versions[i]}',
        f'project.dataset.table_{versions[i+1]}',
        '--format=json'
    ])
    changes.append({
        'from': versions[i],
        'to': versions[i+1],
        'changes': len(diff['type_changes'])
    })
```

## Resources

### Documentation

- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [BigQuery Pricing](https://cloud.google.com/bigquery/pricing)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)

### Tools

- [BigQuery Console](https://console.cloud.google.com/bigquery)
- [bq Command-Line Tool](https://cloud.google.com/bigquery/docs/bq-command-line-tool)
- [BigQuery Python Client](https://googleapis.dev/python/bigquery/latest/)

### Learning Resources

- [BigQuery Public Datasets](https://cloud.google.com/bigquery/public-data)
- [Query Optimization Guide](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)
- [Cost Optimization Guide](https://cloud.google.com/bigquery/docs/best-practices-costs)

## Contributing

To add new notebooks or improve existing ones:

1. Follow the existing notebook structure
2. Include setup, examples, and visualizations
3. Document all configuration options
4. Test with public datasets
5. Update this README with new examples

## License

See the main project LICENSE file.
