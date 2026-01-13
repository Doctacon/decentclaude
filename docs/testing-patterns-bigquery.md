# BigQuery-Specific Testing Patterns

Advanced testing patterns and utilities specifically for BigQuery data transformations and pipelines.

## Table of Contents

1. [BigQuery Testing Utilities](#bigquery-testing-utilities)
2. [Schema Evolution Testing](#schema-evolution-testing)
3. [Cost-Aware Testing](#cost-aware-testing)
4. [Partition Testing Patterns](#partition-testing-patterns)
5. [Testing Complex SQL Patterns](#testing-complex-sql-patterns)

---

## BigQuery Testing Utilities

### Using bq-schema-diff for Testing

Compare schemas between environments to catch breaking changes:

```bash
# Test schema consistency between staging and production
bq-schema-diff \
  project-staging.dataset.table \
  project-prod.dataset.table \
  --format=json > schema_diff.json

# Assert no differences in CI/CD
if [ -s schema_diff.json ]; then
  echo "Schema mismatch detected!"
  cat schema_diff.json
  exit 1
fi
```

**In dbt pre-hook:**

```sql
-- models/hooks/pre-deploy-schema-check.sql
{% if target.name == 'prod' %}
  {{ log("Validating schema compatibility...", info=True) }}

  {%- set staging_table = target.database ~ '.staging.' ~ this.name -%}
  {%- set prod_table = target.database ~ '.prod.' ~ this.name -%}

  -- Use bq-schema-diff to validate
  -- (Implement as macro or external script)
{% endif %}
```

### Using bq-query-cost for Test Optimization

Prevent expensive test queries from running in CI:

```python
# tests/conftest.py
import subprocess
import json

def pytest_collection_modifyitems(config, items):
    """Skip expensive tests in CI"""
    for item in items:
        if "expensive" in item.keywords:
            # Estimate query cost
            query = item.get_closest_marker("query").args[0]
            result = subprocess.run(
                ['bq-query-cost', query, '--format=json'],
                capture_output=True,
                text=True
            )
            cost_data = json.loads(result.stdout)

            # Skip if cost > $1
            if cost_data['estimated_cost_usd'] > 1.0:
                item.add_marker(pytest.mark.skip(
                    reason=f"Query too expensive: ${cost_data['estimated_cost_usd']:.2f}"
                ))
```

**Usage:**

```python
@pytest.mark.expensive
@pytest.mark.query("SELECT * FROM `project.dataset.huge_table`")
def test_full_table_scan():
    # This will be skipped if too expensive
    pass
```

### Using bq-partition-info for Partition Testing

Validate partitioning strategy:

```bash
#!/bin/bash
# tests/validate_partitioning.sh

# Check that table is properly partitioned
bq-partition-info project.dataset.events --format=json | \
  jq -e '.is_partitioned == true and .partitioning_type == "TIME (DAY)"'

if [ $? -ne 0 ]; then
  echo "Table is not properly partitioned!"
  exit 1
fi

# Check partition sizes are balanced
bq-partition-info project.dataset.events --top=30 --format=json | \
  jq '.partitions[] | select(.total_logical_bytes > 10737418240)' | \
  jq -s 'if length > 5 then error("Too many large partitions") else empty end'
```

### Using bq-lineage for Impact Analysis

Test data lineage before schema changes:

```bash
# tests/test_schema_change_impact.sh

TABLE_TO_CHANGE="project.dataset.source_table"

# Get downstream dependencies
DOWNSTREAM=$(bq-lineage $TABLE_TO_CHANGE --direction=downstream --format=json)

# Parse and validate
echo "$DOWNSTREAM" | jq -e '.downstream | length <= 10' || {
  echo "ERROR: Schema change would impact too many downstream tables!"
  echo "$DOWNSTREAM" | jq '.downstream[]'
  exit 1
}

# For each downstream table, validate schema compatibility
echo "$DOWNSTREAM" | jq -r '.downstream[]' | while read -r table; do
  echo "Checking impact on $table..."
  # Run tests specific to that table
  dbt test --select "$table"
done
```

---

## Schema Evolution Testing

### Testing Schema Changes

**Pattern: Add Column with Default**

```sql
-- tests/test_add_column_backwards_compatible.sql
-- Verify new column doesn't break existing queries

-- 1. Simulate existing query (without new column)
WITH legacy_query AS (
  SELECT
    order_id,
    customer_id,
    order_total
    -- new_column NOT referenced
  FROM {{ ref('fct_orders') }}
),

-- 2. Verify new column exists with defaults
new_column_check AS (
  SELECT
    COUNT(*) as total_rows,
    COUNT(new_status_flag) as non_null_count,
    COUNTIF(new_status_flag = 'pending') as default_count
  FROM {{ ref('fct_orders') }}
)

-- 3. Assert backward compatibility
SELECT
  'Legacy query still works' as test_case,
  (SELECT COUNT(*) FROM legacy_query) as legacy_count,
  (SELECT total_rows FROM new_column_check) as current_count,
  (SELECT COUNT(*) FROM legacy_query) = (SELECT total_rows FROM new_column_check) as passed

UNION ALL

SELECT
  'New column has defaults' as test_case,
  NULL,
  (SELECT default_count FROM new_column_check),
  (SELECT default_count FROM new_column_check) > 0 as passed
```

**Pattern: Rename Column**

```sql
-- tests/test_column_rename_compatibility.sql
-- Ensure both old and new column names work during transition

SELECT
  'Both column names exist during transition' as test,
  COUNT(*) as row_count
FROM {{ ref('fct_orders') }}
WHERE old_column_name IS NOT NULL
  AND new_column_name IS NOT NULL
  AND old_column_name = new_column_name  -- Values should match
HAVING COUNT(*) != (SELECT COUNT(*) FROM {{ ref('fct_orders') }})
```

**Pattern: Change Column Type**

```sql
-- tests/test_column_type_change.sql
-- Validate type conversion doesn't lose data

WITH type_conversion_test AS (
  SELECT
    order_id,
    CAST(old_string_id AS INT64) as converted_id,
    new_int_id,
    -- Check for conversion failures
    SAFE_CAST(old_string_id AS INT64) as safe_converted_id
  FROM {{ ref('stg_orders') }}
)

SELECT
  'Type conversion succeeded' as test_case,
  COUNT(*) as total_rows,
  COUNTIF(safe_converted_id IS NULL) as conversion_failures
FROM type_conversion_test
WHERE safe_converted_id IS NULL  -- Should be empty

UNION ALL

SELECT
  'New and old values match' as test_case,
  COUNT(*),
  COUNTIF(converted_id != new_int_id) as mismatches
FROM type_conversion_test
WHERE converted_id != new_int_id  -- Should be empty
```

### Testing Schema Versions

```sql
-- models/schema.yml
models:
  - name: fct_orders
    meta:
      schema_version: "2.0"
      breaking_changes:
        - version: "2.0"
          date: "2024-01-15"
          description: "Renamed order_status_code to order_status"
          migration_path: "Use new order_status column"

    tests:
      - dbt_utils.expression_is_true:
          name: schema_version_tracked
          expression: "schema_version = '2.0'"
          config:
            enabled: true
```

---

## Cost-Aware Testing

### Optimizing Test Query Costs

**Use Table Samples for Large Tables:**

```sql
-- tests/test_with_sample_data.sql
-- Test logic without scanning entire table

{% if target.name == 'ci' %}
  -- Use sample in CI
  {% set sample_clause = "TABLESAMPLE SYSTEM (1 PERCENT)" %}
{% else %}
  {% set sample_clause = "" %}
{% endif %}

WITH sampled_data AS (
  SELECT *
  FROM {{ ref('huge_fact_table') }} {{ sample_clause }}
),

test_results AS (
  SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT user_id) as unique_users,
    SUM(revenue) as total_revenue
  FROM sampled_data
)

SELECT *
FROM test_results
WHERE total_rows = 0  -- Should have data
```

**Use WHERE Clauses to Limit Scan:**

```sql
-- tests/test_recent_data_only.sql
-- Only test recent partitions in CI

{% if target.name == 'ci' %}
  {% set date_filter = "DATE(order_date) >= CURRENT_DATE() - 7" %}
{% else %}
  {% set date_filter = "TRUE" %}
{% endif %}

SELECT
  order_id,
  order_total
FROM {{ ref('fct_orders') }}
WHERE {{ date_filter }}
  AND order_total < 0  -- Should be empty
```

**Estimate Before Running:**

```python
# tests/test_runner.py
"""Run tests with cost estimation"""
import subprocess
import json

def should_run_test(query, max_cost_usd=0.10):
    """Check if test query is within cost budget"""
    result = subprocess.run(
        ['bq-query-cost', query, '--format=json'],
        capture_output=True,
        text=True
    )
    cost_data = json.loads(result.stdout)
    return cost_data['estimated_cost_usd'] <= max_cost_usd

# Example usage
test_query = """
SELECT COUNT(*)
FROM `project.dataset.huge_table`
WHERE complex_condition
"""

if should_run_test(test_query):
    # Run the test
    pass
else:
    print("Skipping expensive test")
```

### Cost Budgets for Test Suites

```yaml
# .github/workflows/ci.yml
env:
  MAX_TEST_COST_USD: "5.00"  # $5 budget for all tests

steps:
  - name: Estimate test costs
    run: |
      TOTAL_COST=0
      for query_file in tests/queries/*.sql; do
        COST=$(bq-query-cost --file=$query_file --format=json | jq -r '.estimated_cost_usd')
        TOTAL_COST=$(echo "$TOTAL_COST + $COST" | bc)
      done

      if (( $(echo "$TOTAL_COST > $MAX_TEST_COST_USD" | bc -l) )); then
        echo "Test suite too expensive: \$$TOTAL_COST"
        exit 1
      fi
```

---

## Partition Testing Patterns

### Testing Partition Pruning

```sql
-- tests/test_partition_pruning.sql
-- Verify queries use partition pruning

-- This test uses _PARTITIONTIME to ensure partition filter is applied
WITH partition_filter_test AS (
  SELECT
    COUNT(*) as row_count,
    COUNT(DISTINCT _PARTITIONTIME) as partition_count
  FROM {{ ref('partitioned_events') }}
  WHERE DATE(_PARTITIONTIME) = '2024-01-01'
)

SELECT
  'Partition pruning works' as test,
  partition_count,
  1 as expected_partitions
FROM partition_filter_test
WHERE partition_count != 1  -- Should only scan one partition
```

### Testing Partition Expiration

```sql
-- tests/test_partition_expiration.sql
-- Verify old partitions are expired

WITH partition_ages AS (
  SELECT
    partition_id,
    TIMESTAMP(partition_id) as partition_time,
    DATE_DIFF(CURRENT_DATE(), DATE(partition_id), DAY) as age_days
  FROM `project.dataset.INFORMATION_SCHEMA.PARTITIONS`
  WHERE table_name = 'events'
    AND partition_id != '__NULL__'
)

SELECT
  partition_id,
  age_days
FROM partition_ages
WHERE age_days > 90  -- Should be empty if retention is 90 days
```

### Testing Partition Balance

```sql
-- tests/test_partition_balance.sql
-- Detect skewed partitions

WITH partition_sizes AS (
  SELECT
    partition_id,
    total_rows,
    total_logical_bytes,
    AVG(total_rows) OVER () as avg_rows,
    STDDEV(total_rows) OVER () as stddev_rows
  FROM `project.dataset.INFORMATION_SCHEMA.PARTITIONS`
  WHERE table_name = 'events'
    AND partition_id != '__NULL__'
    AND DATE(partition_id) >= CURRENT_DATE() - 30
),

skewed_partitions AS (
  SELECT
    partition_id,
    total_rows,
    avg_rows,
    -- Flag partitions > 3 std deviations from mean
    ABS(total_rows - avg_rows) / NULLIF(stddev_rows, 0) as z_score
  FROM partition_sizes
  WHERE ABS(total_rows - avg_rows) / NULLIF(stddev_rows, 0) > 3
)

SELECT *
FROM skewed_partitions  -- Should be empty or minimal
```

### Testing Clustering Effectiveness

```sql
-- tests/test_clustering_effectiveness.sql
-- Validate clustering is effective

WITH cluster_stats AS (
  SELECT
    SUM(total_logical_bytes) / COUNT(DISTINCT partition_id) as avg_partition_size,
    COUNT(DISTINCT partition_id) as partition_count
  FROM `project.dataset.INFORMATION_SCHEMA.PARTITIONS`
  WHERE table_name = 'clustered_events'
),

-- Query a clustered column
clustered_query_bytes AS (
  SELECT
    -- Get bytes processed for clustered query
    (SELECT total_bytes_processed
     FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
     WHERE job_id = 'test_clustered_query'
    ) as bytes_processed
)

SELECT
  'Clustering reduces scan' as test,
  bytes_processed,
  avg_partition_size * partition_count as full_scan_bytes,
  bytes_processed < (avg_partition_size * partition_count * 0.5) as passed
FROM clustered_query_bytes, cluster_stats
```

---

## Testing Complex SQL Patterns

### Testing Deduplication Logic

```sql
-- tests/test_deduplication.sql
-- Validate ROW_NUMBER deduplication

WITH raw_data_with_dupes AS (
  SELECT
    1 as id, '2024-01-01' as date, 'A' as value
  UNION ALL SELECT 1, '2024-01-01', 'B'  -- Duplicate
  UNION ALL SELECT 2, '2024-01-01', 'C'
),

deduped AS (
  SELECT * EXCEPT(row_num)
  FROM (
    SELECT
      *,
      ROW_NUMBER() OVER (PARTITION BY id, date ORDER BY value DESC) as row_num
    FROM raw_data_with_dupes
  )
  WHERE row_num = 1
),

test_results AS (
  SELECT
    COUNT(*) as total_rows,
    COUNT(DISTINCT id) as unique_ids,
    COUNT(*) = COUNT(DISTINCT id) as no_duplicates
  FROM deduped
)

SELECT *
FROM test_results
WHERE NOT no_duplicates  -- Should be empty
```

### Testing Window Functions

```sql
-- tests/test_window_functions.sql
-- Validate cumulative calculations

WITH test_data AS (
  SELECT 1 as user_id, DATE('2024-01-01') as date, 100 as amount
  UNION ALL SELECT 1, DATE('2024-01-02'), 150
  UNION ALL SELECT 1, DATE('2024-01-03'), 200
  UNION ALL SELECT 2, DATE('2024-01-01'), 50
  UNION ALL SELECT 2, DATE('2024-01-02'), 75
),

with_cumulative AS (
  SELECT
    user_id,
    date,
    amount,
    SUM(amount) OVER (
      PARTITION BY user_id
      ORDER BY date
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total
  FROM test_data
),

validation AS (
  SELECT
    user_id,
    date,
    running_total,
    -- Manual calculation for validation
    (SELECT SUM(amount)
     FROM test_data t2
     WHERE t2.user_id = t1.user_id
       AND t2.date <= t1.date
    ) as expected_total,
    running_total = (
      SELECT SUM(amount)
      FROM test_data t2
      WHERE t2.user_id = t1.user_id
        AND t2.date <= t1.date
    ) as match
  FROM with_cumulative t1
)

SELECT *
FROM validation
WHERE NOT match  -- Should be empty
```

### Testing Pivots

```sql
-- tests/test_pivot_logic.sql
-- Validate pivot transformation

WITH raw_data AS (
  SELECT 'user1' as user_id, 'metric_a' as metric, 100 as value
  UNION ALL SELECT 'user1', 'metric_b', 200
  UNION ALL SELECT 'user2', 'metric_a', 150
  UNION ALL SELECT 'user2', 'metric_b', 250
),

pivoted AS (
  SELECT
    user_id,
    MAX(IF(metric = 'metric_a', value, NULL)) as metric_a,
    MAX(IF(metric = 'metric_b', value, NULL)) as metric_b
  FROM raw_data
  GROUP BY user_id
),

validation AS (
  SELECT
    p.user_id,
    p.metric_a,
    p.metric_b,
    -- Validate against source
    (SELECT value FROM raw_data WHERE user_id = p.user_id AND metric = 'metric_a') as expected_a,
    (SELECT value FROM raw_data WHERE user_id = p.user_id AND metric = 'metric_b') as expected_b,
    p.metric_a = (SELECT value FROM raw_data WHERE user_id = p.user_id AND metric = 'metric_a') as metric_a_match,
    p.metric_b = (SELECT value FROM raw_data WHERE user_id = p.user_id AND metric = 'metric_b') as metric_b_match
  FROM pivoted p
)

SELECT *
FROM validation
WHERE NOT (metric_a_match AND metric_b_match)
```

### Testing Join Logic

```sql
-- tests/test_join_completeness.sql
-- Validate joins don't lose data unexpectedly

WITH left_table AS (
  SELECT * FROM {{ ref('dim_customers') }}
  WHERE customer_id <= 100  -- Sample
),

right_table AS (
  SELECT * FROM {{ ref('fct_orders') }}
  WHERE customer_id <= 100
),

joined_data AS (
  SELECT
    c.customer_id,
    o.order_id
  FROM left_table c
  LEFT JOIN right_table o ON c.customer_id = o.customer_id
),

validation AS (
  SELECT
    'All left table rows preserved' as test,
    COUNT(DISTINCT customer_id) as joined_count,
    (SELECT COUNT(*) FROM left_table) as expected_count,
    COUNT(DISTINCT customer_id) = (SELECT COUNT(*) FROM left_table) as passed
  FROM joined_data
)

SELECT *
FROM validation
WHERE NOT passed
```

### Testing ARRAY/STRUCT Handling

```sql
-- tests/test_array_unnesting.sql
-- Validate ARRAY unnesting logic

WITH test_data AS (
  SELECT
    'order1' as order_id,
    [STRUCT('item1' as item_id, 10.0 as price), STRUCT('item2', 20.0)] as items
  UNION ALL
  SELECT
    'order2',
    [STRUCT('item3', 30.0)]
),

unnested AS (
  SELECT
    order_id,
    item.item_id,
    item.price
  FROM test_data,
  UNNEST(items) as item
),

validation AS (
  SELECT
    COUNT(*) as total_items,
    COUNT(DISTINCT order_id) as unique_orders,
    SUM(price) as total_price,
    -- Should have 3 items total
    COUNT(*) = 3 as item_count_correct,
    -- Should sum to 60.0
    ABS(SUM(price) - 60.0) < 0.01 as sum_correct
  FROM unnested
)

SELECT *
FROM validation
WHERE NOT (item_count_correct AND sum_correct)
```

---

## Additional Resources

- [BigQuery Best Practices: Optimizing Query Performance](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)
- [BigQuery Testing with dbt](https://docs.getdbt.com/reference/warehouse-setups/bigquery-setup)
- [Cost Optimization for BigQuery](https://cloud.google.com/bigquery/docs/best-practices-costs)
- [Partitioning and Clustering Guide](https://cloud.google.com/bigquery/docs/partitioned-tables)

---

**Related Documentation:**
- [Main Testing Patterns](../data-testing-patterns.md)
- [CLI Utilities](../tests/README.md)
- [BigQuery Utilities Guide](../README.md)

**Last Updated:** 2026-01-13
