-- Example dbt model: Simple user aggregation
-- This demonstrates basic dbt syntax and best practices

{{
  config(
    materialized='table',
    partition_by={
      "field": "created_date",
      "data_type": "date"
    }
  )
}}

WITH users AS (
  SELECT * FROM {{ ref('stg_users') }}
),

user_stats AS (
  SELECT
    user_id,
    email,
    created_at,
    EXTRACT(DATE FROM created_at) as created_date,
    is_active,
    is_valid_email,

    -- Example calculations
    DATE_DIFF(CURRENT_DATE(), EXTRACT(DATE FROM created_at), DAY) as account_age_days,

    -- Categorization
    CASE
      WHEN DATE_DIFF(CURRENT_DATE(), EXTRACT(DATE FROM created_at), DAY) < 30 THEN 'new'
      WHEN DATE_DIFF(CURRENT_DATE(), EXTRACT(DATE FROM created_at), DAY) < 365 THEN 'established'
      ELSE 'veteran'
    END as user_cohort

  FROM users
  WHERE is_valid_email = true
)

SELECT * FROM user_stats
