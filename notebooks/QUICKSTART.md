# Notebooks Quick Start Guide

Get up and running with the BigQuery utility notebooks in 5 minutes.

## 1. Install Dependencies (2 minutes)

```bash
# Navigate to notebooks directory
cd /path/to/decentclaude/mayor/rig/notebooks

# Install required packages
pip install -r requirements-notebooks.txt
```

## 2. Authenticate with Google Cloud (1 minute)

```bash
# Login to Google Cloud
gcloud auth application-default login

# Set your default project (optional)
gcloud config set project YOUR_PROJECT_ID
```

## 3. Start Jupyter (30 seconds)

```bash
# Start Jupyter Notebook
jupyter notebook

# OR start JupyterLab (recommended)
jupyter lab
```

Your browser will open automatically at http://localhost:8888

## 4. Open a Notebook (30 seconds)

Click on any notebook:
- `bigquery-exploration.ipynb` - Start here for data exploration
- `data-quality-workflow.ipynb` - For data quality analysis
- `cost-optimization.ipynb` - For cost analysis and optimization

## 5. Run Your First Analysis (1 minute)

1. Click on the first code cell
2. Press `Shift + Enter` to run it
3. Continue running cells sequentially
4. Modify configuration cells with your table IDs

## Example: Profile a Table

```python
# In any notebook, run this in a code cell:
from pathlib import Path
import subprocess
import json

UTILS_DIR = Path('../bin/data-utils')

def run_util(util_name, args):
    util_path = UTILS_DIR / util_name
    result = subprocess.run([str(util_path)] + args,
                          capture_output=True, text=True)
    return json.loads(result.stdout)

# Profile a public dataset table
profile = run_util('bq-profile', [
    'bigquery-public-data.usa_names.usa_1910_current',
    '--format=json'
])

# Display key metrics
meta = profile['table_overview']
print(f"Rows: {meta['num_rows']:,}")
print(f"Columns: {meta['num_columns']}")
```

## Notebook Overview

### bigquery-exploration.ipynb
**Best for:** Initial data discovery and exploration

**What you'll learn:**
- How to profile tables
- Compare schemas
- Visualize data distributions
- Analyze multiple tables

**Time:** 15-20 minutes

### data-quality-workflow.ipynb
**Best for:** Data quality audits and monitoring

**What you'll learn:**
- NULL value analysis
- Completeness checks
- Duplicate detection
- Quality scorecard generation

**Time:** 20-25 minutes

### cost-optimization.ipynb
**Best for:** Reducing BigQuery costs

**What you'll learn:**
- Cost estimation
- Query optimization
- ROI calculations
- Cost trend analysis

**Time:** 25-30 minutes

## Common Issues

### "Module not found" Error
```bash
# Reinstall requirements
pip install -r requirements-notebooks.txt --upgrade
```

### "Permission denied" Error
```bash
# Re-authenticate
gcloud auth application-default login
```

### "bq-* utility not found" Error
```bash
# Make utilities executable
chmod +x ../bin/data-utils/bq-*
```

### Jupyter Not Starting
```bash
# Install Jupyter if missing
pip install jupyter jupyterlab

# Or restart the kernel if already running
# In Jupyter: Kernel -> Restart
```

## Tips for Success

1. **Start with public datasets** - All notebooks use `bigquery-public-data.*` by default
2. **Run cells in order** - Don't skip cells, especially setup cells
3. **Modify configurations** - Change table IDs and thresholds to match your needs
4. **Save often** - Jupyter auto-saves, but manual saves are safer
5. **Check outputs** - Review visualizations and tables after each cell

## Next Steps

After completing the quick start:

1. Explore the full README.md for advanced usage
2. Customize notebooks for your specific use cases
3. Create your own notebooks using the provided templates
4. Automate workflows by converting notebooks to scripts

## Getting Help

- Check the main README.md for detailed documentation
- Review example code in each notebook
- Consult BigQuery documentation at https://cloud.google.com/bigquery/docs
- Look for inline comments and markdown explanations

## Keyboard Shortcuts

**Essential Jupyter shortcuts:**
- `Shift + Enter` - Run cell and move to next
- `Ctrl + Enter` - Run cell and stay
- `A` - Insert cell above
- `B` - Insert cell below
- `D, D` - Delete cell
- `M` - Change to markdown
- `Y` - Change to code
- `Esc` - Exit edit mode
- `Enter` - Enter edit mode

## Quick Reference

### Profile a table
```python
profile = run_util('bq-profile', ['project.dataset.table', '--format=json'])
```

### Compare schemas
```python
diff = run_util('bq-schema-diff', ['table1', 'table2', '--format=json'])
```

### Estimate query cost
```python
job_config = bigquery.QueryJobConfig(dry_run=True)
query_job = client.query(sql, job_config=job_config)
bytes_processed = query_job.total_bytes_processed
```

### Get table lineage
```python
lineage = run_util('bq-lineage', ['project.dataset.table', '--format=json'])
```

Happy analyzing!
