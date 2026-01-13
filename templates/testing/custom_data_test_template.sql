-- Template for custom dbt data test
-- Place in tests/ directory
-- Test fails if query returns any rows

/*
  Test Name: {{ test_name }}
  Description: {{ test_description }}
  Author: {{ your_name }}
  Created: {{ date }}
*/

-- Define test logic that returns rows ONLY when test fails
-- Empty result set = test passes

WITH test_data AS (
  SELECT
    column1,
    column2,
    column3
  FROM {{ ref('your_model') }}
  WHERE {{ filter_condition }}
),

validation_logic AS (
  SELECT
    column1,
    column2,
    -- Add your validation logic here
    -- Example: checking for data quality issues
    CASE
      WHEN column2 IS NULL THEN 'Missing required value'
      WHEN column3 < 0 THEN 'Negative value not allowed'
      WHEN column3 > 1000000 THEN 'Value exceeds maximum'
      ELSE NULL
    END as validation_error
  FROM test_data
),

failed_validations AS (
  SELECT
    column1,
    column2,
    validation_error
  FROM validation_logic
  WHERE validation_error IS NOT NULL
)

-- Return failed rows
SELECT *
FROM failed_validations

-- Examples of common test patterns:

-- Pattern 1: Value Reconciliation
/*
WITH source_total AS (
  SELECT SUM(amount) as total
  FROM {{ source('raw', 'orders') }}
  WHERE DATE(order_date) = CURRENT_DATE() - 1
),

model_total AS (
  SELECT SUM(amount) as total
  FROM {{ ref('fct_orders') }}
  WHERE DATE(order_date) = CURRENT_DATE() - 1
)

SELECT
  s.total as source_total,
  m.total as model_total,
  ABS(s.total - m.total) as difference,
  ABS(s.total - m.total) / s.total as pct_difference
FROM source_total s, model_total m
WHERE ABS(s.total - m.total) / s.total > 0.001  -- More than 0.1% difference
*/

-- Pattern 2: Orphaned Records
/*
SELECT
  o.order_id,
  o.customer_id,
  'Orphaned order - customer not found' as error
FROM {{ ref('fct_orders') }} o
LEFT JOIN {{ ref('dim_customers') }} c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
*/

-- Pattern 3: Business Rule Validation
/*
WITH rule_violations AS (
  SELECT
    order_id,
    order_status,
    shipped_date,
    delivered_date,
    CASE
      WHEN order_status = 'delivered' AND delivered_date IS NULL
        THEN 'Delivered orders must have delivered_date'
      WHEN order_status = 'shipped' AND shipped_date IS NULL
        THEN 'Shipped orders must have shipped_date'
      WHEN delivered_date < shipped_date
        THEN 'Delivered date cannot be before shipped date'
      WHEN shipped_date < order_date
        THEN 'Shipped date cannot be before order date'
    END as violation
  FROM {{ ref('fct_orders') }}
)

SELECT *
FROM rule_violations
WHERE violation IS NOT NULL
*/

-- Pattern 4: Statistical Anomaly Detection
/*
WITH daily_metrics AS (
  SELECT
    DATE(order_date) as date,
    COUNT(*) as order_count,
    AVG(order_total) as avg_order_value
  FROM {{ ref('fct_orders') }}
  WHERE DATE(order_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
  GROUP BY 1
),

stats AS (
  SELECT
    AVG(order_count) as mean_orders,
    STDDEV(order_count) as stddev_orders,
    AVG(avg_order_value) as mean_aov,
    STDDEV(avg_order_value) as stddev_aov
  FROM daily_metrics
  WHERE date < DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
)

SELECT
  dm.date,
  dm.order_count,
  dm.avg_order_value,
  'Order count anomaly' as anomaly_type
FROM daily_metrics dm
CROSS JOIN stats s
WHERE dm.date >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  AND ABS(dm.order_count - s.mean_orders) > 3 * s.stddev_orders
*/
