# BigQuery Utility Notebooks - Overview

Visual guide to the interactive notebooks for BigQuery data utilities.

## Directory Structure

```
notebooks/
├── .gitignore                          # Git ignore rules
├── README.md                           # Comprehensive documentation
├── QUICKSTART.md                       # 5-minute getting started guide
├── OVERVIEW.md                         # This file
├── requirements-notebooks.txt          # Python dependencies
├── bigquery-exploration.ipynb          # Data exploration notebook
├── data-quality-workflow.ipynb         # Quality analysis notebook
└── cost-optimization.ipynb             # Cost optimization notebook
```

## Notebooks at a Glance

### 1. bigquery-exploration.ipynb

**Purpose:** Interactive data exploration and discovery

**Key Features:**
- Table profiling with bq-profile
- Schema comparison with bq-schema-diff
- Lineage analysis with bq-lineage
- Data type distribution visualization
- NULL value analysis
- Uniqueness ratio analysis
- Multi-table comparison

**Visualizations:**
- Bar charts for data type distribution
- Horizontal bars for NULL percentages
- Uniqueness ratio comparisons
- Multi-table metric comparisons

**Best For:**
- New dataset exploration
- Understanding table structure
- Comparing development vs production schemas
- Finding primary key candidates

**Time Investment:** 15-20 minutes

---

### 2. data-quality-workflow.ipynb

**Purpose:** Comprehensive data quality assessment

**Key Features:**
- Complete table profiling
- NULL value detection and thresholds
- Data completeness scoring
- Uniqueness and duplicate analysis
- Quality scorecard with visual gauge
- Automated recommendations
- Custom quality checks

**Visualizations:**
- NULL percentage horizontal bars
- Completeness percentage by column
- Quality scorecard with traffic light colors
- Overall quality gauge (speedometer style)
- Data type pie chart

**Quality Metrics:**
- NULL value percentage
- Data completeness score
- Uniqueness ratios
- Overall quality score (0-100%)

**Thresholds (Configurable):**
```python
THRESHOLDS = {
    'max_null_percentage': 10.0,
    'min_uniqueness': 0.01,
    'max_duplicate_percentage': 5.0,
    'min_completeness': 90.0,
}
```

**Best For:**
- Data quality audits
- Compliance reporting
- Data validation
- Quality monitoring dashboards

**Time Investment:** 20-25 minutes

---

### 3. cost-optimization.ipynb

**Purpose:** BigQuery cost analysis and optimization

**Key Features:**
- Query cost estimation (dry runs)
- Before/after optimization comparisons
- Query analysis and recommendations
- Performance benchmarking
- Cost trend analysis (30-day simulation)
- ROI calculations for optimizations
- Optimization checklist

**Visualizations:**
- Cost comparison bar charts
- Data processed (GB) comparisons
- Query execution time benchmarks
- Cost trend line charts (daily costs)
- ROI analysis horizontal bars
- Optimization priority matrix

**Cost Analysis:**
- Bytes processed estimation
- Cost calculation ($5 per TB)
- Savings percentage
- Payback period in days
- Annual savings projection

**Optimization Strategies:**
```
HIGH IMPACT, LOW EFFORT:
- Avoid SELECT *
- Use partition filters
- Enable query caching

HIGH IMPACT, MEDIUM EFFORT:
- Create materialized views
- Add table clustering

MEDIUM IMPACT, HIGH EFFORT:
- Optimize data types
- Restructure tables
```

**Best For:**
- Cost reduction initiatives
- Query performance tuning
- Budget planning
- Optimization prioritization

**Time Investment:** 25-30 minutes

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Start Here                                │
│                                                              │
│  New to BigQuery utilities? → bigquery-exploration.ipynb    │
│  Quality concerns?          → data-quality-workflow.ipynb   │
│  High costs?                → cost-optimization.ipynb       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              1. bigquery-exploration.ipynb                   │
│                                                              │
│  • Profile your tables                                      │
│  • Understand data structure                                │
│  • Compare schemas                                          │
│  • Identify data types                                      │
│                                                              │
│  Output: Table profiles, schema comparisons                 │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│           2. data-quality-workflow.ipynb                     │
│                                                              │
│  • Analyze NULL values                                      │
│  • Check data completeness                                  │
│  • Detect duplicates                                        │
│  • Generate quality scorecard                               │
│                                                              │
│  Output: Quality score (0-100%), recommendations            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│            3. cost-optimization.ipynb                        │
│                                                              │
│  • Estimate query costs                                     │
│  • Benchmark performance                                    │
│  • Calculate optimization ROI                               │
│  • Prioritize improvements                                  │
│                                                              │
│  Output: Cost savings, optimization priorities              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Iterate & Improve                            │
│                                                              │
│  • Implement optimizations                                  │
│  • Monitor quality metrics                                  │
│  • Track cost trends                                        │
│  • Repeat as needed                                         │
└─────────────────────────────────────────────────────────────┘
```

## Feature Matrix

| Feature | Exploration | Quality | Cost |
|---------|-------------|---------|------|
| **Table Profiling** | ✓ | ✓ | - |
| **Schema Comparison** | ✓ | - | - |
| **Lineage Analysis** | ✓ | - | - |
| **NULL Analysis** | ✓ | ✓ | - |
| **Quality Scoring** | - | ✓ | - |
| **Cost Estimation** | - | - | ✓ |
| **Query Optimization** | - | - | ✓ |
| **ROI Calculation** | - | - | ✓ |
| **Benchmarking** | - | - | ✓ |
| **Visualizations** | ✓ | ✓ | ✓ |
| **Recommendations** | - | ✓ | ✓ |

## Utility Usage

| Utility | Exploration | Quality | Cost |
|---------|-------------|---------|------|
| bq-profile | ✓✓✓ | ✓✓✓ | ✓ |
| bq-schema-diff | ✓✓✓ | ✓ | - |
| bq-lineage | ✓✓ | - | - |
| bq-query-cost | - | - | ✓✓✓ |
| bq-optimize | - | - | ✓✓ |
| bq-benchmark | - | - | ✓✓✓ |

Legend: ✓ = Used, ✓✓ = Frequently used, ✓✓✓ = Primary use

## Common Use Cases

### Use Case 1: New Dataset Onboarding
**Path:** Exploration → Quality → Documentation
1. Run bigquery-exploration.ipynb to understand structure
2. Run data-quality-workflow.ipynb to assess quality
3. Document findings and create data catalog

### Use Case 2: Production Table Validation
**Path:** Quality → Monitoring
1. Run data-quality-workflow.ipynb on production table
2. Set up alerts for quality score drops
3. Schedule weekly quality reports

### Use Case 3: Cost Reduction Initiative
**Path:** Cost → Optimization → Measurement
1. Run cost-optimization.ipynb to identify expensive queries
2. Implement high-ROI optimizations
3. Re-run to measure savings

### Use Case 4: Schema Migration
**Path:** Exploration (Schema Diff) → Validation
1. Compare old vs new schema with bigquery-exploration.ipynb
2. Validate data quality with data-quality-workflow.ipynb
3. Verify no cost regression with cost-optimization.ipynb

### Use Case 5: Regular Health Check
**Path:** All Three → Dashboard
1. Monthly profiling with bigquery-exploration.ipynb
2. Quality assessment with data-quality-workflow.ipynb
3. Cost review with cost-optimization.ipynb
4. Aggregate into executive dashboard

## Output Examples

### From bigquery-exploration.ipynb
```
Table: bigquery-public-data.stackoverflow.posts_questions
Rows: 24,358,221
Columns: 19
Size: 14.2 GB

Data Type Distribution:
  STRING   12 columns (63.2%)
  INT64     5 columns (26.3%)
  TIMESTAMP 2 columns (10.5%)

Potential Primary Keys:
  id (uniqueness: 1.0000)
```

### From data-quality-workflow.ipynb
```
QUALITY SCORECARD
Overall Score: 87.5%

NULL Values:      92.0% ✓ Pass
Completeness:     88.0% ✓ Pass
Uniqueness:       82.0% ⚠ Warning

Recommendations:
  HIGH: 2 columns exceed NULL threshold
  MEDIUM: No unique identifier found
```

### From cost-optimization.ipynb
```
COST ANALYSIS
Unoptimized Query: $0.0450
Optimized Query:   $0.0089
Savings:           $0.0361 (80.2%)

Annual Projected Savings: $6,572.65
ROI: 2,450%
Payback Period: 2 days
```

## Integration Patterns

### Pattern 1: Automated Quality Reports
```python
# Schedule with cron or Airflow
def daily_quality_report():
    profile = run_util('bq-profile', [table, '--format=json'])
    quality_score = calculate_score(profile)

    if quality_score < 80:
        send_alert(f"Quality dropped to {quality_score}%")

    save_to_dashboard(quality_score)
```

### Pattern 2: Pre-deployment Checks
```python
# In CI/CD pipeline
def validate_schema_change():
    diff = run_util('bq-schema-diff', [old_table, new_table])

    if not diff['identical']:
        print(f"Schema changes: {diff['summary']}")
        require_approval()
```

### Pattern 3: Cost Monitoring
```python
# Weekly cost review
def weekly_cost_review():
    queries = get_expensive_queries()

    for query in queries:
        suggestions = analyze_query(query)
        print(f"Optimization potential: ${calculate_savings(suggestions)}")
```

## Performance Tips

1. **Start small** - Profile sample tables before production
2. **Use caching** - Enable metadata caching for repeated queries
3. **Limit scope** - Use WHERE clauses and LIMIT in exploratory queries
4. **Batch operations** - Profile multiple tables in parallel
5. **Save outputs** - Export results for later comparison

## Best Practices

1. **Version control** - Commit customized notebooks
2. **Document assumptions** - Add markdown cells explaining thresholds
3. **Test with public data** - Validate on free datasets first
4. **Schedule reviews** - Regular quality and cost audits
5. **Share insights** - Export visualizations for stakeholders

## Quick Start

```bash
# 1. Install
pip install -r requirements-notebooks.txt

# 2. Authenticate
gcloud auth application-default login

# 3. Launch
jupyter lab

# 4. Open any notebook and run!
```

See QUICKSTART.md for detailed instructions.

## Support

- Full documentation: README.md
- Quick start: QUICKSTART.md
- Example code: In each notebook
- BigQuery docs: https://cloud.google.com/bigquery/docs
