-- Solution: Customer Daily Summary Model
-- This is a reference implementation for Exercise 1

{{
  config(
    materialized='table',
    partition_by={
      "field": "activity_date",
      "data_type": "date"
    },
    cluster_by=["customer_cohort", "customer_id"]
  )
}}

WITH users AS (
  SELECT * FROM {{ ref('stg_users') }}
),

-- Assume we have an orders staging table
orders AS (
  SELECT
    customer_id,
    order_id,
    EXTRACT(DATE FROM order_timestamp) as order_date,
    order_total
  FROM {{ ref('stg_orders') }}
),

daily_aggregates AS (
  SELECT
    o.customer_id,
    o.order_date as activity_date,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(o.order_total) as total_revenue,
    ROUND(AVG(o.order_total), 2) as average_order_value
  FROM orders o
  GROUP BY 1, 2
),

enriched AS (
  SELECT
    agg.*,

    -- Add customer attributes
    u.email,

    -- Calculate customer cohort
    CASE
      WHEN DATE_DIFF(agg.activity_date, EXTRACT(DATE FROM u.created_at), DAY) < 30 THEN 'new'
      WHEN DATE_DIFF(agg.activity_date, EXTRACT(DATE FROM u.created_at), DAY) < 365 THEN 'established'
      ELSE 'veteran'
    END as customer_cohort,

    -- Quality flags
    agg.total_orders > 100 as is_suspicious_activity,
    agg.total_revenue > 10000 as is_high_value

  FROM daily_aggregates agg
  LEFT JOIN users u ON agg.customer_id = u.user_id
)

SELECT
  customer_id,
  activity_date,
  customer_cohort,
  total_orders,
  total_revenue,
  average_order_value,
  is_suspicious_activity,
  is_high_value
FROM enriched
