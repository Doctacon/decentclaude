# Data Testing Templates

Ready-to-use templates for implementing comprehensive data testing in your project.

## Quick Start

1. Copy the template you need to your project
2. Customize placeholders marked with `{{ }}` or `your_`
3. Update configuration values for your environment
4. Run and iterate

## Available Templates

### dbt_schema_yml_template.yml

Comprehensive dbt schema.yml with testing patterns for common scenarios.

**Use when:** Setting up tests for a new dbt model

**Includes:**
- Primary key tests (unique, not_null)
- Foreign key relationships
- Accepted values for enums
- Range checks for numeric columns
- Date/timestamp validation
- Email format validation
- Custom test examples

**Quick start:**
```bash
cp templates/testing/dbt_schema_yml_template.yml models/your_model/schema.yml
# Edit schema.yml and replace placeholder values
dbt test --select your_model
```

---

### custom_data_test_template.sql

Template for custom dbt data tests (SQL queries that fail if they return rows).

**Use when:** Need to test business logic or cross-model validations

**Includes:**
- Revenue reconciliation pattern
- Orphaned records detection
- Business rule validation
- Statistical anomaly detection

**Quick start:**
```bash
cp templates/testing/custom_data_test_template.sql tests/assert_your_business_rule.sql
# Edit the SQL to match your business logic
dbt test
```

**Test patterns included:**
1. **Value Reconciliation:** Compare aggregates between models
2. **Orphaned Records:** Find foreign key violations
3. **Business Rules:** Validate domain-specific logic
4. **Anomaly Detection:** Statistical outlier detection

---

### integration_test_template.sh

Bash script for end-to-end pipeline integration testing.

**Use when:** Need to test complete data pipeline from raw to marts

**Includes:**
- Test dataset creation/cleanup
- dbt seed, run, test execution
- Custom validation queries
- Data quality checks
- Idempotency testing
- Automated cleanup

**Quick start:**
```bash
cp templates/testing/integration_test_template.sh scripts/test_pipeline.sh
chmod +x scripts/test_pipeline.sh

# Configure environment
export GCP_PROJECT_ID="your-project"
export DBT_TARGET="integration_test"

# Run tests
./scripts/test_pipeline.sh
```

**Features:**
- ✅ Automatic test dataset management
- ✅ Row count validation
- ✅ Revenue reconciliation
- ✅ Null checks
- ✅ Idempotency verification
- ✅ Cleanup on exit

---

### python_data_quality_template.py

Python script for BigQuery-specific data quality checks.

**Use when:** Need programmatic data quality validation

**Includes custom check classes:**
- `BigQueryRowCountCheck` - Validate row counts
- `BigQuerySchemaCheck` - Verify schema structure
- `BigQueryDataFreshnessCheck` - Check data recency
- `BigQueryNullCheck` - Find nulls in critical columns
- `BigQueryReconciliationCheck` - Compare source vs target aggregates

**Quick start:**
```bash
cp templates/testing/python_data_quality_template.py scripts/quality_checks.py
# Edit the check configurations
python scripts/quality_checks.py
```

**Integration with CI/CD:**
```yaml
# .github/workflows/ci.yml
- name: Run data quality checks
  run: |
    python scripts/quality_checks.py
```

---

## Usage Patterns

### Pattern 1: New Model Testing

When adding a new dbt model:

1. Copy `dbt_schema_yml_template.yml` to your model directory
2. Define tests for each column
3. Add model-level tests (row counts, uniqueness)
4. Run `dbt test --select your_model`

```bash
# Example
cp templates/testing/dbt_schema_yml_template.yml models/marts/fct_new_model/schema.yml
# Edit schema.yml
dbt test --select fct_new_model
```

### Pattern 2: Custom Business Logic Testing

When you need to validate complex business rules:

1. Copy `custom_data_test_template.sql`
2. Implement your validation logic
3. Place in `tests/` directory
4. Run with dbt test

```bash
# Example: Validate customer lifetime value calculation
cp templates/testing/custom_data_test_template.sql tests/assert_ltv_calculation.sql
# Edit SQL to validate LTV = SUM(orders)
dbt test
```

### Pattern 3: Pipeline Integration Testing

For complete pipeline validation:

1. Copy `integration_test_template.sh`
2. Customize for your project structure
3. Add to CI/CD pipeline

```bash
# Example
cp templates/testing/integration_test_template.sh .github/scripts/test_pipeline.sh
chmod +x .github/scripts/test_pipeline.sh

# Add to GitHub Actions
./.github/scripts/test_pipeline.sh
```

### Pattern 4: Programmatic Data Quality

For BigQuery-specific checks:

1. Copy `python_data_quality_template.py`
2. Configure checks for your tables
3. Run as part of pipeline or standalone

```bash
# Example
cp templates/testing/python_data_quality_template.py scripts/daily_quality_checks.py
# Configure checks
python scripts/daily_quality_checks.py

# Or in Airflow:
# PythonOperator(
#     task_id='quality_checks',
#     python_callable=run_custom_checks
# )
```

---

## Integration with Existing Infrastructure

### With dbt

Templates work seamlessly with dbt:

```bash
# Use schema template
cp templates/testing/dbt_schema_yml_template.yml models/staging/schema.yml

# Use custom test template
cp templates/testing/custom_data_test_template.sql tests/custom_validation.sql

# Run all tests
dbt test

# Run specific tests
dbt test --select schema.yml
dbt test --select test_name:custom_validation
```

### With CI/CD

Integration test template is CI/CD ready:

```yaml
# GitHub Actions example
name: Data Pipeline Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2

      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt

      - name: Run integration tests
        env:
          GCP_PROJECT_ID: ${{ secrets.GCP_PROJECT }}
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GCP_SA_KEY }}
        run: |
          ./scripts/test_pipeline.sh
```

### With Airflow

Python template integrates with Airflow:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator

# Import from template
from scripts.quality_checks import run_custom_checks

with DAG('daily_pipeline', ...) as dag:
    quality_check = PythonOperator(
        task_id='data_quality_checks',
        python_callable=run_custom_checks
    )
```

---

## Customization Guide

### dbt Schema Template

Replace these placeholders:

- `your_model_name` → Your actual model name
- `owner: "data-team@company.com"` → Your team email
- Column names and types → Match your schema
- Test parameters (min_value, max_value) → Your business rules

### Custom Data Test Template

Replace these sections:

- `{{ ref('your_model') }}` → Your model references
- `{{ filter_condition }}` → Your WHERE clauses
- Validation logic → Your business rules
- Uncomment and adapt pattern examples

### Integration Test Template

Update these variables:

- `PROJECT_ID` → Your GCP project
- `DBT_TARGET` → Your dbt target name
- Table references → Your actual table names
- Validation thresholds → Your requirements

### Python Quality Template

Customize these classes:

- Table IDs → Your BigQuery tables
- Column names → Your schema
- Thresholds → Your requirements (min/max rows, freshness, tolerance)
- Add/remove checks based on needs

---

## Best Practices

### 1. Start Simple

Begin with basic tests:
- unique
- not_null
- relationships

Then add:
- Custom data tests
- Integration tests
- Quality checks

### 2. Test Incrementally

Don't try to test everything at once:
1. Test new models as you build them
2. Add tests when fixing bugs
3. Gradually increase coverage

### 3. Use Templates as Starting Points

Templates are guidelines, not rigid rules:
- Adapt to your needs
- Remove unnecessary checks
- Add domain-specific tests

### 4. Document Your Tests

Add descriptions to tests:
```yaml
tests:
  - unique:
      name: unique_order_id
      config:
        error_if: ">100"  # Allow some duplicates
        warn_if: ">10"
```

### 5. Monitor Test Performance

Some tests can be expensive:
- Use samples for large tables in CI
- Limit date ranges where appropriate
- Use `bq-query-cost` to estimate costs

---

## Examples

### Example 1: Testing New Orders Model

```bash
# 1. Create schema with tests
cp templates/testing/dbt_schema_yml_template.yml models/marts/fct_orders/schema.yml

# 2. Add custom revenue reconciliation test
cp templates/testing/custom_data_test_template.sql tests/assert_orders_revenue.sql

# 3. Run tests
dbt test --select fct_orders
```

### Example 2: End-to-End Pipeline Test

```bash
# 1. Set up integration test
cp templates/testing/integration_test_template.sh scripts/test_daily_pipeline.sh

# 2. Customize for your pipeline
vim scripts/test_daily_pipeline.sh  # Edit table names, validations

# 3. Run
./scripts/test_daily_pipeline.sh
```

### Example 3: Data Quality Monitoring

```bash
# 1. Set up quality checks
cp templates/testing/python_data_quality_template.py scripts/hourly_quality_checks.py

# 2. Configure for critical tables
vim scripts/hourly_quality_checks.py  # Add your tables

# 3. Schedule in cron or Airflow
# crontab: 0 * * * * python scripts/hourly_quality_checks.py
```

---

## Troubleshooting

### Issue: Test Runs Too Slow

**Solution:** Use samples or date filters
```sql
-- Add WHERE clause to limit data
WHERE DATE(order_date) >= CURRENT_DATE() - 7
```

### Issue: Test is Too Expensive

**Solution:** Check cost first
```bash
bq-query-cost --file=tests/expensive_test.sql
# If > $1, optimize or skip in CI
```

### Issue: Test Fails Intermittently

**Solution:** Add tolerance
```yaml
tests:
  - dbt_utils.accepted_range:
      min_value: 900  # Instead of exact 1000
      max_value: 1100
```

### Issue: Schema Test Doesn't Catch Issue

**Solution:** Add custom data test
```sql
-- tests/custom_validation.sql
SELECT * FROM {{ ref('model') }}
WHERE your_specific_condition
```

---

## Additional Resources

- [Main Testing Patterns Documentation](../../data-testing-patterns.md)
- [BigQuery-Specific Patterns](../../docs/testing-patterns-bigquery.md)
- [Test Infrastructure](../../tests/README.md)
- [CLI Utilities Guide](../../README.md)

---

**Last Updated:** 2026-01-13
**Maintained By:** decentclaude data engineering team
