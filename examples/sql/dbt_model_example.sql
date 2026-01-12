-- Example: dbt Model
-- This demonstrates a typical dbt model with CTEs and transformations

{{
  config(
    materialized='table',
    partition_by={
      "field": "event_date",
      "data_type": "date"
    },
    cluster_by=["user_id", "event_type"]
  )
}}

WITH raw_events AS (
  SELECT
    event_id,
    user_id,
    event_type,
    event_timestamp,
    DATE(event_timestamp) AS event_date,
    properties
  FROM {{ source('analytics', 'events') }}
  WHERE DATE(event_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
),

user_metadata AS (
  SELECT
    user_id,
    email,
    signup_date,
    user_tier
  FROM {{ ref('users') }}
),

enriched_events AS (
  SELECT
    e.event_id,
    e.user_id,
    u.email,
    u.user_tier,
    e.event_type,
    e.event_timestamp,
    e.event_date,
    e.properties,
    -- Calculate days since signup
    DATE_DIFF(e.event_date, u.signup_date, DAY) AS days_since_signup,
    -- User lifecycle stage
    CASE
      WHEN DATE_DIFF(e.event_date, u.signup_date, DAY) <= 7 THEN 'new'
      WHEN DATE_DIFF(e.event_date, u.signup_date, DAY) <= 30 THEN 'active'
      ELSE 'mature'
    END AS user_lifecycle_stage
  FROM raw_events e
  LEFT JOIN user_metadata u
    ON e.user_id = u.user_id
)

SELECT * FROM enriched_events
