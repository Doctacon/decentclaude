# Data Testing Framework Patterns

A comprehensive guide to testing patterns for data transformations, pipelines, and quality assertions for Claude-assisted development.

## Table of Contents

1. [Unit Testing Transformations](#unit-testing-transformations)
2. [Integration Testing Pipelines](#integration-testing-pipelines)
3. [Data Quality Assertions](#data-quality-assertions)
4. [Testing Best Practices](#testing-best-practices)
5. [Tools and Frameworks](#tools-and-frameworks)

---

## Unit Testing Transformations

### dbt Testing

#### Schema Tests (Basic)

```yaml
# models/schema.yml
version: 2

models:
  - name: fct_orders
    description: Order fact table
    columns:
      - name: order_id
        description: Primary key
        tests:
          - unique
          - not_null

      - name: customer_id
        description: Foreign key to customers
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id

      - name: order_total
        description: Total order amount
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1000000

      - name: order_status
        description: Current order status
        tests:
          - accepted_values:
              values: ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']

      - name: order_date
        description: Order creation date
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= '2020-01-01'"
```

#### Data Tests (Custom SQL)

```sql
-- tests/assert_order_total_matches_line_items.sql
-- Tests that order totals equal sum of line items

select
  order_id,
  order_total,
  sum(line_item_total) as calculated_total
from {{ ref('fct_orders') }} o
join {{ ref('fct_order_line_items') }} li using (order_id)
group by order_id, order_total
having abs(order_total - calculated_total) > 0.01
```

```sql
-- tests/assert_no_future_orders.sql
-- Tests that no orders exist in the future

select
  order_id,
  order_date
from {{ ref('fct_orders') }}
where order_date > current_date()
```

```sql
-- tests/assert_revenue_reconciliation.sql
-- Tests that revenue metrics match across models

with revenue_from_orders as (
  select
    date_trunc('day', order_date) as date,
    sum(order_total) as revenue
  from {{ ref('fct_orders') }}
  where order_status != 'cancelled'
  group by 1
),

revenue_from_summary as (
  select
    date,
    total_revenue as revenue
  from {{ ref('daily_revenue_summary') }}
)

select
  coalesce(o.date, s.date) as date,
  o.revenue as orders_revenue,
  s.revenue as summary_revenue,
  abs(coalesce(o.revenue, 0) - coalesce(s.revenue, 0)) as difference
from revenue_from_orders o
full outer join revenue_from_summary s using (date)
where abs(coalesce(o.revenue, 0) - coalesce(s.revenue, 0)) > 0.01
```

#### Generic Tests (Reusable)

```sql
-- macros/test_row_count_in_range.sql
{% test row_count_in_range(model, min_value, max_value) %}

select count(*) as row_count
from {{ model }}
having count(*) < {{ min_value }}
   or count(*) > {{ max_value }}

{% endtest %}
```

```yaml
# Usage in schema.yml
models:
  - name: fct_orders
    tests:
      - row_count_in_range:
          min_value: 1000
          max_value: 1000000
```

```sql
-- macros/test_recent_data.sql
{% test recent_data(model, column_name, datepart, interval) %}

select
  max({{ column_name }}) as latest_date,
  {{ dbt.dateadd(datepart, interval, dbt.current_timestamp()) }} as expected_minimum
from {{ model }}
having max({{ column_name }}) < {{ dbt.dateadd(datepart, interval, dbt.current_timestamp()) }}

{% endtest %}
```

```yaml
# Usage
models:
  - name: fct_events
    tests:
      - recent_data:
          column_name: event_timestamp
          datepart: day
          interval: -1  # Data should be from within last 24 hours
```

#### Unit Tests (dbt 1.8+)

```yaml
# models/staging/stg_orders.yml
unit_tests:
  - name: test_order_total_calculation
    description: Verify that order total is calculated correctly
    model: stg_orders
    given:
      - input: ref('raw_orders')
        rows:
          - order_id: 1
            subtotal: 100.00
            tax: 10.00
            shipping: 5.00
          - order_id: 2
            subtotal: 50.00
            tax: 5.00
            shipping: 0.00
    expect:
      rows:
        - order_id: 1
          order_total: 115.00
        - order_id: 2
          order_total: 55.00

  - name: test_status_mapping
    description: Verify status codes are mapped correctly
    model: stg_orders
    given:
      - input: ref('raw_orders')
        rows:
          - order_id: 1
            status_code: 'P'
          - order_id: 2
            status_code: 'C'
          - order_id: 3
            status_code: 'S'
    expect:
      rows:
        - order_id: 1
          order_status: 'pending'
        - order_id: 2
          order_status: 'confirmed'
        - order_id: 3
          order_status: 'shipped'
```

### SQLMesh Testing

#### Unit Tests

```sql
-- tests/test_stg_orders.yaml
test_stg_orders:
  model: staging.stg_orders
  inputs:
    raw.orders:
      rows:
        - order_id: 1
          order_date: 2024-01-01
          customer_id: 100
          order_total: 150.00
          status: P
        - order_id: 2
          order_date: 2024-01-02
          customer_id: 101
          order_total: 75.00
          status: C
  outputs:
    query:
      rows:
        - order_id: 1
          order_date: 2024-01-01
          customer_id: 100
          order_total: 150.00
          order_status: pending
        - order_id: 2
          order_date: 2024-01-02
          customer_id: 101
          order_total: 75.00
          order_status: confirmed
```

#### Audits (Data Quality)

```sql
-- audits/check_primary_key_uniqueness.sql
AUDIT (
  name check_primary_key_uniqueness,
  dialect bigquery
);

SELECT
  order_id,
  COUNT(*) as duplicate_count
FROM @this_model
GROUP BY order_id
HAVING COUNT(*) > 1
```

```sql
-- audits/check_referential_integrity.sql
AUDIT (
  name check_referential_integrity
);

-- Check for orphaned orders (customer doesn't exist)
SELECT
  o.order_id,
  o.customer_id
FROM @this_model o
LEFT JOIN {{ ref('dim_customers') }} c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
```

```sql
-- audits/check_data_freshness.sql
AUDIT (
  name check_data_freshness
);

SELECT
  MAX(order_date) as latest_order,
  CURRENT_DATE() - MAX(order_date) as days_stale
FROM @this_model
WHERE CURRENT_DATE() - MAX(order_date) > 1
```

### Testing SQL Transformations in Isolation

#### Using Common Table Expressions (CTEs) for Testability

```sql
-- models/marts/fct_customer_metrics.sql
-- BAD: Hard to test
SELECT
  c.customer_id,
  c.customer_name,
  COUNT(DISTINCT o.order_id) as order_count,
  SUM(o.order_total) as lifetime_value,
  MAX(o.order_date) as last_order_date
FROM {{ ref('dim_customers') }} c
LEFT JOIN {{ ref('fct_orders') }} o ON c.customer_id = o.customer_id
WHERE o.order_status != 'cancelled'
GROUP BY c.customer_id, c.customer_name

-- GOOD: Each CTE can be tested separately
WITH customers AS (
  SELECT * FROM {{ ref('dim_customers') }}
),

orders AS (
  SELECT * FROM {{ ref('fct_orders') }}
  WHERE order_status != 'cancelled'
),

customer_orders AS (
  SELECT
    c.customer_id,
    c.customer_name,
    o.order_id,
    o.order_total,
    o.order_date
  FROM customers c
  LEFT JOIN orders o ON c.customer_id = o.customer_id
),

customer_metrics AS (
  SELECT
    customer_id,
    customer_name,
    COUNT(DISTINCT order_id) as order_count,
    SUM(order_total) as lifetime_value,
    MAX(order_date) as last_order_date
  FROM customer_orders
  GROUP BY customer_id, customer_name
)

SELECT * FROM customer_metrics
```

#### Mock Data for Testing

```sql
-- tests/fixtures/mock_customers.sql
-- Create test fixture for testing
SELECT
  1 as customer_id,
  'Test Customer 1' as customer_name,
  'test1@example.com' as email
UNION ALL
SELECT
  2 as customer_id,
  'Test Customer 2' as customer_name,
  'test2@example.com' as email
```

### Testing Edge Cases

**Create comprehensive test cases:**

```yaml
# models/schema.yml
models:
  - name: calculate_discount
    description: Calculate discount based on order total
    tests:
      - dbt_utils.expression_is_true:
          name: discount_zero_for_small_orders
          expression: "discount = 0"
          config:
            where: "order_total < 100"

      - dbt_utils.expression_is_true:
          name: discount_10_percent_for_medium_orders
          expression: "discount = order_total * 0.10"
          config:
            where: "order_total >= 100 AND order_total < 500"

      - dbt_utils.expression_is_true:
          name: discount_capped_at_100
          expression: "discount <= 100"
```

**Test boundary conditions:**

```sql
-- tests/test_date_boundaries.sql
-- Test edge cases for date logic

WITH test_cases AS (
  SELECT DATE('2024-01-01') as test_date, 'year_start' as scenario
  UNION ALL SELECT DATE('2024-12-31'), 'year_end'
  UNION ALL SELECT DATE('2024-02-29'), 'leap_day'
  UNION ALL SELECT NULL, 'null_date'
),

results AS (
  SELECT
    scenario,
    test_date,
    {{ your_date_function('test_date') }} as result
  FROM test_cases
)

SELECT *
FROM results
WHERE result IS NULL OR result < '1900-01-01' OR result > '2100-12-31'
```

---

## Integration Testing Pipelines

### End-to-End Pipeline Testing

#### dbt Project Integration Tests

```bash
#!/bin/bash
# scripts/integration_test.sh

set -e

echo "Running integration tests for dbt project..."

# 1. Set up test database
export DBT_TARGET=integration_test
export DBT_SCHEMA=integration_test_$(date +%s)

# 2. Run seeds (test data)
dbt seed --target integration_test

# 3. Run models
dbt run --target integration_test

# 4. Run tests
dbt test --target integration_test

# 5. Run custom validation queries
bq query --use_legacy_sql=false < tests/integration/validate_pipeline.sql

# 6. Cleanup
bq rm -r -f -d "project:${DBT_SCHEMA}"

echo "Integration tests passed!"
```

#### Testing Data Flows

```sql
-- tests/integration/validate_pipeline.sql
-- Validate complete data flow from raw to marts

WITH raw_counts AS (
  SELECT COUNT(*) as count FROM `project.raw.orders`
),

staging_counts AS (
  SELECT COUNT(*) as count FROM `project.staging.stg_orders`
),

marts_counts AS (
  SELECT COUNT(*) as count FROM `project.marts.fct_orders`
),

validation AS (
  SELECT
    r.count as raw_count,
    s.count as staging_count,
    m.count as marts_count,
    -- Staging should have >= 95% of raw (some filtering expected)
    s.count >= r.count * 0.95 as staging_valid,
    -- Marts should have same as staging
    m.count = s.count as marts_valid
  FROM raw_counts r
  CROSS JOIN staging_counts s
  CROSS JOIN marts_counts m
)

SELECT *
FROM validation
WHERE NOT staging_valid OR NOT marts_valid
```

### Testing Orchestration

#### Airflow DAG Testing

```python
# tests/dags/test_daily_etl_dag.py
import pytest
from datetime import datetime
from airflow.models import DagBag

def test_dag_loaded():
    """Test that DAG is loaded without errors"""
    dagbag = DagBag(include_examples=False)
    assert 'daily_etl' in dagbag.dags
    assert len(dagbag.import_errors) == 0

def test_dag_structure():
    """Test DAG structure and dependencies"""
    dagbag = DagBag(include_examples=False)
    dag = dagbag.get_dag('daily_etl')

    # Check all expected tasks exist
    expected_tasks = [
        'extract_raw_data',
        'run_dbt_staging',
        'run_dbt_marts',
        'data_quality_checks',
        'send_success_notification'
    ]
    for task_id in expected_tasks:
        assert task_id in dag.task_ids

    # Check dependencies
    extract_task = dag.get_task('extract_raw_data')
    dbt_staging_task = dag.get_task('run_dbt_staging')

    assert dbt_staging_task in extract_task.downstream_list

def test_dag_default_args():
    """Test DAG default arguments"""
    dagbag = DagBag(include_examples=False)
    dag = dagbag.get_dag('daily_etl')

    assert dag.default_args['retries'] >= 2
    assert dag.default_args['retry_delay'].total_seconds() >= 300
    assert 'email' in dag.default_args
    assert dag.default_args['email_on_failure'] is True

def test_task_execution_timeout():
    """Test that tasks have reasonable timeouts"""
    dagbag = DagBag(include_examples=False)
    dag = dagbag.get_dag('daily_etl')

    for task in dag.tasks:
        assert task.execution_timeout is not None
        assert task.execution_timeout.total_seconds() <= 7200  # 2 hours max
```

#### Testing Task Execution

```python
# tests/operators/test_dbt_operator.py
import pytest
from airflow.utils.state import State
from datetime import datetime

def test_dbt_run_task(dag, mock_dbt):
    """Test dbt run task execution"""
    task = dag.get_task('run_dbt_staging')

    # Mock execution
    execution_date = datetime(2024, 1, 1)
    task_instance = task.run(
        start_date=execution_date,
        end_date=execution_date,
        ignore_ti_state=True
    )

    assert task_instance.state == State.SUCCESS
    mock_dbt.assert_called_with(['run', '--select', 'staging.*'])

def test_dbt_test_task_failures(dag, mock_dbt_with_failures):
    """Test that dbt test failures are handled correctly"""
    task = dag.get_task('run_dbt_tests')

    with pytest.raises(Exception) as exc_info:
        task.execute(context={})

    assert 'dbt test failed' in str(exc_info.value)
```

### Testing Incremental Loads

#### Incremental Load Test Pattern

```sql
-- tests/test_incremental_load.sql
-- Test that incremental model processes only new data

-- Step 1: Initial load
CREATE OR REPLACE TABLE test_dataset.test_orders AS
SELECT * FROM (
  SELECT 1 as order_id, DATE('2024-01-01') as order_date, 100.0 as total
  UNION ALL
  SELECT 2, DATE('2024-01-02'), 200.0
);

-- Run dbt model (incremental)
-- dbt run --select fct_orders --target test

-- Step 2: Add new data
INSERT INTO test_dataset.test_orders VALUES
  (3, DATE('2024-01-03'), 300.0);

-- Run dbt model again
-- dbt run --select fct_orders --target test

-- Step 3: Validate
SELECT
  'All rows processed' as test_case,
  COUNT(*) as actual_count,
  3 as expected_count,
  COUNT(*) = 3 as passed
FROM test_dataset.fct_orders

UNION ALL

SELECT
  'New row added in second run' as test_case,
  COUNT(*) as actual_count,
  1 as expected_count,
  COUNT(*) = 1 as passed
FROM test_dataset.fct_orders
WHERE order_id = 3

UNION ALL

SELECT
  'Existing rows not duplicated' as test_case,
  COUNT(*) as actual_count,
  1 as expected_count,
  COUNT(*) = 1 as passed
FROM test_dataset.fct_orders
WHERE order_id = 1;
```

#### Testing Idempotency

```python
# tests/test_idempotency.py
"""Test that pipeline is idempotent (can be run multiple times safely)"""

import subprocess
from datetime import datetime

def test_idempotent_dbt_run():
    """Test that running dbt multiple times produces same results"""

    # Run 1
    subprocess.run(['dbt', 'run', '--target', 'test'], check=True)
    result1 = get_table_checksum('test.fct_orders')

    # Run 2 (without new data)
    subprocess.run(['dbt', 'run', '--target', 'test'], check=True)
    result2 = get_table_checksum('test.fct_orders')

    # Results should be identical
    assert result1 == result2, "dbt run is not idempotent"

def get_table_checksum(table_id):
    """Calculate checksum of table for comparison"""
    query = f"""
    SELECT
      COUNT(*) as row_count,
      SUM(FARM_FINGERPRINT(TO_JSON_STRING(t))) as checksum
    FROM `{table_id}` t
    """
    # Execute query and return results
    # Implementation depends on your BigQuery client
    pass
```

### Testing Data Quality in Pipelines

```python
# airflow/dags/daily_etl.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def validate_data_quality(**context):
    """Run data quality checks after pipeline"""
    from google.cloud import bigquery

    client = bigquery.Client()

    # Check 1: Row count is within expected range
    query = """
    SELECT COUNT(*) as count
    FROM `project.marts.fct_orders`
    WHERE DATE(order_date) = CURRENT_DATE() - 1
    """
    result = client.query(query).to_dataframe()
    row_count = result['count'].iloc[0]

    assert 1000 <= row_count <= 100000, f"Row count {row_count} outside expected range"

    # Check 2: No nulls in critical columns
    query = """
    SELECT COUNT(*) as null_count
    FROM `project.marts.fct_orders`
    WHERE order_id IS NULL OR customer_id IS NULL OR order_total IS NULL
    """
    result = client.query(query).to_dataframe()
    null_count = result['null_count'].iloc[0]

    assert null_count == 0, f"Found {null_count} rows with null critical values"

    # Check 3: Revenue reconciliation
    query = """
    WITH source_revenue AS (
      SELECT SUM(amount) as revenue
      FROM `project.raw.transactions`
      WHERE DATE(transaction_date) = CURRENT_DATE() - 1
    ),
    transformed_revenue AS (
      SELECT SUM(order_total) as revenue
      FROM `project.marts.fct_orders`
      WHERE DATE(order_date) = CURRENT_DATE() - 1
    )
    SELECT
      ABS(s.revenue - t.revenue) / s.revenue as pct_diff
    FROM source_revenue s, transformed_revenue t
    """
    result = client.query(query).to_dataframe()
    pct_diff = result['pct_diff'].iloc[0]

    assert pct_diff < 0.01, f"Revenue mismatch: {pct_diff*100:.2f}%"

with DAG(
    'daily_etl',
    default_args={'retries': 2},
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
) as dag:

    run_dbt = BashOperator(
        task_id='run_dbt',
        bash_command='dbt run --target prod'
    )

    quality_checks = PythonOperator(
        task_id='data_quality_checks',
        python_callable=validate_data_quality
    )

    run_dbt >> quality_checks
```

---

## Data Quality Assertions

### Great Expectations

#### Setup and Configuration

```yaml
# great_expectations/great_expectations.yml
datasources:
  bigquery_datasource:
    class_name: Datasource
    execution_engine:
      class_name: SqlAlchemyExecutionEngine
      connection_string: bigquery://my-project
    data_connectors:
      default_inferred_data_connector:
        class_name: InferredAssetSqlDataConnector
        include_schema_name: true
```

#### Expectation Suites

```python
# great_expectations/expectations/orders_suite.py
import great_expectations as gx

context = gx.get_context()

# Create expectation suite
suite = context.add_expectation_suite("orders_quality_suite")

# Add expectations
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(
        column="order_id"
    )
)

suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeUnique(
        column="order_id"
    )
)

suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeInSet(
        column="order_status",
        value_set=["pending", "confirmed", "shipped", "delivered", "cancelled"]
    )
)

suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="order_total",
        min_value=0,
        max_value=1000000
    )
)

suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="order_date",
        min_value="2020-01-01",
        max_value="2030-12-31",
        parse_strings_as_datetimes=True
    )
)

# Custom expectation
suite.add_expectation(
    gx.expectations.ExpectColumnPairValuesToBeEqual(
        column_A="order_total",
        column_B="subtotal_plus_tax_plus_shipping"
    )
)
```

#### Running Validations

```python
# scripts/run_data_quality_checks.py
import great_expectations as gx
from datetime import datetime

context = gx.get_context()

# Create checkpoint
checkpoint = context.add_checkpoint(
    name="daily_orders_checkpoint",
    validations=[
        {
            "batch_request": {
                "datasource_name": "bigquery_datasource",
                "data_connector_name": "default_inferred_data_connector",
                "data_asset_name": "project.marts.fct_orders",
                "batch_spec_passthrough": {
                    "query": """
                        SELECT * FROM `project.marts.fct_orders`
                        WHERE DATE(order_date) = CURRENT_DATE() - 1
                    """
                }
            },
            "expectation_suite_name": "orders_quality_suite"
        }
    ]
)

# Run checkpoint
result = checkpoint.run()

# Check results
if not result.success:
    print("Data quality validation failed!")
    for validation_result in result.run_results.values():
        for check in validation_result["validation_result"]["results"]:
            if not check["success"]:
                print(f"  Failed: {check['expectation_config']['expectation_type']}")
    raise Exception("Data quality checks failed")
else:
    print("All data quality checks passed!")
```

### dbt Expectations

```yaml
# models/schema.yml
version: 2

models:
  - name: fct_orders
    tests:
      # Row-level expectations
      - dbt_expectations.expect_table_row_count_to_be_between:
          min_value: 1000
          max_value: 1000000

      - dbt_expectations.expect_table_row_count_to_equal_other_table:
          compare_model: ref('stg_orders')

      # Column-level expectations
      - dbt_expectations.expect_column_values_to_be_of_type:
          column_name: order_id
          column_type: INT64

      - dbt_expectations.expect_column_values_to_match_regex:
          column_name: email
          regex: "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"

      - dbt_expectations.expect_column_mean_to_be_between:
          column_name: order_total
          min_value: 50
          max_value: 500

      - dbt_expectations.expect_column_quantile_values_to_be_between:
          column_name: order_total
          quantile: 0.95
          min_value: 200
          max_value: 1000
```

### Custom Quality Checks

#### Schema Validation

```sql
-- tests/validate_schema.sql
-- Ensure schema matches expected structure

WITH expected_schema AS (
  SELECT 'order_id' as column_name, 'INT64' as data_type
  UNION ALL SELECT 'customer_id', 'INT64'
  UNION ALL SELECT 'order_date', 'DATE'
  UNION ALL SELECT 'order_total', 'FLOAT64'
  UNION ALL SELECT 'order_status', 'STRING'
),

actual_schema AS (
  SELECT
    column_name,
    data_type
  FROM `project.marts.INFORMATION_SCHEMA.COLUMNS`
  WHERE table_name = 'fct_orders'
),

schema_diff AS (
  SELECT
    COALESCE(e.column_name, a.column_name) as column_name,
    e.data_type as expected_type,
    a.data_type as actual_type,
    CASE
      WHEN e.column_name IS NULL THEN 'Unexpected column'
      WHEN a.column_name IS NULL THEN 'Missing column'
      WHEN e.data_type != a.data_type THEN 'Type mismatch'
      ELSE 'OK'
    END as status
  FROM expected_schema e
  FULL OUTER JOIN actual_schema a USING (column_name)
)

SELECT *
FROM schema_diff
WHERE status != 'OK'
```

#### Business Rule Validation

```sql
-- tests/business_rules.sql
-- Validate business logic rules

-- Rule 1: Orders must have at least one line item
WITH orders_without_items AS (
  SELECT o.order_id
  FROM {{ ref('fct_orders') }} o
  LEFT JOIN {{ ref('fct_order_line_items') }} li ON o.order_id = li.order_id
  WHERE li.order_id IS NULL
)

SELECT 'Orders without line items' as rule, COUNT(*) as violations
FROM orders_without_items

UNION ALL

-- Rule 2: Cancelled orders should have $0 revenue
SELECT
  'Cancelled orders with revenue' as rule,
  COUNT(*) as violations
FROM {{ ref('fct_orders') }}
WHERE order_status = 'cancelled' AND order_total != 0

UNION ALL

-- Rule 3: Customer lifetime value should equal sum of order totals
WITH customer_order_sums AS (
  SELECT
    customer_id,
    SUM(order_total) as calculated_ltv
  FROM {{ ref('fct_orders') }}
  WHERE order_status != 'cancelled'
  GROUP BY customer_id
),

ltv_mismatches AS (
  SELECT
    c.customer_id,
    c.lifetime_value,
    co.calculated_ltv
  FROM {{ ref('dim_customers') }} c
  JOIN customer_order_sums co USING (customer_id)
  WHERE ABS(c.lifetime_value - co.calculated_ltv) > 0.01
)

SELECT 'LTV calculation mismatches' as rule, COUNT(*) as violations
FROM ltv_mismatches
```

#### Anomaly Detection

```sql
-- tests/detect_anomalies.sql
-- Detect statistical anomalies in daily metrics

WITH daily_metrics AS (
  SELECT
    DATE(order_date) as date,
    COUNT(*) as order_count,
    AVG(order_total) as avg_order_value,
    SUM(order_total) as total_revenue
  FROM {{ ref('fct_orders') }}
  WHERE DATE(order_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  GROUP BY 1
),

stats AS (
  SELECT
    AVG(order_count) as mean_orders,
    STDDEV(order_count) as stddev_orders,
    AVG(avg_order_value) as mean_aov,
    STDDEV(avg_order_value) as stddev_aov,
    AVG(total_revenue) as mean_revenue,
    STDDEV(total_revenue) as stddev_revenue
  FROM daily_metrics
  WHERE date < DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)  -- Exclude recent data
),

anomalies AS (
  SELECT
    dm.date,
    dm.order_count,
    dm.avg_order_value,
    dm.total_revenue,
    -- Flag if more than 3 standard deviations from mean
    ABS(dm.order_count - s.mean_orders) > 3 * s.stddev_orders as order_count_anomaly,
    ABS(dm.avg_order_value - s.mean_aov) > 3 * s.stddev_aov as aov_anomaly,
    ABS(dm.total_revenue - s.mean_revenue) > 3 * s.stddev_revenue as revenue_anomaly
  FROM daily_metrics dm
  CROSS JOIN stats s
  WHERE dm.date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
)

SELECT *
FROM anomalies
WHERE order_count_anomaly OR aov_anomaly OR revenue_anomaly
```

### SLA Monitoring

```sql
-- tests/sla_monitoring.sql
-- Monitor data SLAs (freshness, completeness, accuracy)

WITH sla_checks AS (
  -- Freshness: Data should be available by 9 AM
  SELECT
    'data_freshness' as sla_name,
    MAX(DATE(order_date)) as latest_date,
    CURRENT_DATE() - 1 as expected_date,
    MAX(DATE(order_date)) >= CURRENT_DATE() - 1 as sla_met,
    'Data should be loaded by 9 AM daily' as description
  FROM {{ ref('fct_orders') }}

  UNION ALL

  -- Completeness: All orders from source should be in target
  SELECT
    'data_completeness' as sla_name,
    NULL as latest_date,
    NULL as expected_date,
    (SELECT COUNT(*) FROM {{ ref('fct_orders') }} WHERE DATE(order_date) = CURRENT_DATE() - 1) >=
    (SELECT COUNT(*) FROM {{ source('raw', 'orders') }} WHERE DATE(order_date) = CURRENT_DATE() - 1) * 0.99 as sla_met,
    'At least 99% of source records should be processed' as description

  UNION ALL

  -- Accuracy: Revenue should reconcile within 0.1%
  SELECT
    'revenue_accuracy' as sla_name,
    NULL as latest_date,
    NULL as expected_date,
    ABS(
      (SELECT SUM(order_total) FROM {{ ref('fct_orders') }} WHERE DATE(order_date) = CURRENT_DATE() - 1) -
      (SELECT SUM(amount) FROM {{ source('raw', 'orders') }} WHERE DATE(order_date) = CURRENT_DATE() - 1)
    ) / (SELECT SUM(amount) FROM {{ source('raw', 'orders') }} WHERE DATE(order_date) = CURRENT_DATE() - 1) < 0.001 as sla_met,
    'Revenue should reconcile within 0.1%' as description
)

SELECT *
FROM sla_checks
WHERE NOT sla_met
```

---

## Testing Best Practices

### Test Pyramid for Data Pipelines

```
         ┌─────────────────┐
         │  Integration    │  ← Few, expensive, end-to-end
         │     Tests       │
         └─────────────────┘
              ▲
              │
      ┌──────────────────┐
      │  Data Quality    │     ← Moderate, validate outputs
      │    Assertions    │
      └──────────────────┘
            ▲
            │
    ┌──────────────────────┐
    │   Unit Tests         │   ← Many, fast, test transformations
    │  (Schema, Data)      │
    └──────────────────────┘
```

### Testing Checklist

**For every data model, ensure:**

- [ ] Primary key is unique and not null
- [ ] Foreign keys have referential integrity
- [ ] Required columns are not null
- [ ] Enum columns have accepted values
- [ ] Numeric columns are within expected ranges
- [ ] Date columns are within reasonable bounds
- [ ] Row counts are within expected ranges
- [ ] Data is fresh (recent load timestamp)
- [ ] Aggregations reconcile with source data
- [ ] Business rules are validated

### Test Organization

```
project/
├── models/
│   ├── staging/
│   │   ├── stg_orders.sql
│   │   └── schema.yml          # Schema tests
│   └── marts/
│       ├── fct_orders.sql
│       └── schema.yml
├── tests/
│   ├── generic/                # Reusable test macros
│   │   ├── test_recent_data.sql
│   │   └── test_row_count_in_range.sql
│   ├── unit/                   # Unit tests (dbt 1.8+)
│   │   └── test_stg_orders.yml
│   ├── data/                   # Custom data tests
│   │   ├── assert_revenue_reconciliation.sql
│   │   └── business_rules.sql
│   └── integration/            # Integration tests
│       ├── test_pipeline.sh
│       └── validate_pipeline.sql
├── great_expectations/
│   ├── expectations/
│   │   └── orders_suite.py
│   └── checkpoints/
│       └── daily_checkpoint.yml
└── scripts/
    └── run_all_tests.sh
```

### Continuous Testing

```yaml
# .github/workflows/ci.yml
name: Data Pipeline CI

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install dbt-bigquery great-expectations sqlmesh

      - name: Run dbt tests
        env:
          DBT_TARGET: ci
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GCP_SA_KEY }}
        run: |
          dbt deps
          dbt seed --target ci
          dbt run --target ci
          dbt test --target ci

      - name: Run Great Expectations
        run: |
          python scripts/run_data_quality_checks.py

      - name: Run integration tests
        run: |
          bash tests/integration/test_pipeline.sh
```

---

## Tools and Frameworks

### Testing Tools Comparison

| Tool | Best For | Pros | Cons |
|------|----------|------|------|
| **dbt tests** | SQL transformations | Native to dbt, easy to write | Limited to SQL, basic assertions |
| **Great Expectations** | Comprehensive data quality | Rich expectation library, good UI | Steeper learning curve, overhead |
| **SQLMesh audits** | Inline data quality | Integrated with models, version aware | SQLMesh-specific |
| **pytest** | Python transformations | Full programming language, flexible | Requires Python knowledge |
| **dbt-expectations** | Enhanced dbt testing | Extends dbt with GE-like tests | Dependency on external package |

### Recommended Stack

**Minimum viable testing:**
1. dbt schema tests (unique, not_null, relationships)
2. Custom data tests for business rules
3. Basic integration test script

**Production-grade testing:**
1. dbt + dbt-expectations for comprehensive SQL testing
2. Great Expectations for complex data quality
3. pytest for Python-based transformations
4. CI/CD pipeline with automated test runs
5. Monitoring and alerting on test failures

### Quick Start Commands

```bash
# dbt testing
dbt test                                    # Run all tests
dbt test --select model_name                # Test specific model
dbt test --select tag:critical              # Test tagged models
dbt test --store-failures                   # Store failed rows for debugging

# Great Expectations
great_expectations init                     # Initialize project
great_expectations suite new                # Create expectation suite
great_expectations checkpoint new           # Create checkpoint
great_expectations checkpoint run <name>    # Run checkpoint

# SQLMesh testing
sqlmesh test                                # Run all tests
sqlmesh audit                               # Run all audits
sqlmesh plan --test                         # Test before deployment

# Integration testing
pytest tests/                               # Run pytest tests
bash scripts/integration_test.sh            # Run custom integration tests
```

---

## Additional Resources

### Documentation
- [dbt Testing Documentation](https://docs.getdbt.com/docs/build/tests)
- [Great Expectations](https://greatexpectations.io/)
- [dbt-expectations Package](https://github.com/calogica/dbt-expectations)
- [SQLMesh Testing](https://sqlmesh.readthedocs.io/en/stable/concepts/tests/)

### Example Test Suites
- [dbt-utils Tests](https://github.com/dbt-labs/dbt-utils#tests)
- [Great Expectations Expectation Gallery](https://greatexpectations.io/expectations)

---

**Last Updated:** 2026-01-12
**Maintained By:** decentclaude data engineering team
