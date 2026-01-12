-- Example: SQLMesh Model
-- This demonstrates a SQLMesh model with metadata and transformations

MODEL (
  name analytics.user_engagement_daily,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column event_date
  ),
  start '2024-01-01',
  cron '@daily',
  grain (user_id, event_date)
);

WITH daily_events AS (
  SELECT
    user_id,
    DATE(event_timestamp) AS event_date,
    event_type,
    COUNT(*) AS event_count
  FROM analytics.events
  WHERE
    event_date BETWEEN @start_date AND @end_date
  GROUP BY 1, 2, 3
),

event_pivot AS (
  SELECT
    user_id,
    event_date,
    SUM(CASE WHEN event_type = 'page_view' THEN event_count ELSE 0 END) AS page_views,
    SUM(CASE WHEN event_type = 'click' THEN event_count ELSE 0 END) AS clicks,
    SUM(CASE WHEN event_type = 'purchase' THEN event_count ELSE 0 END) AS purchases,
    SUM(event_count) AS total_events
  FROM daily_events
  GROUP BY 1, 2
),

engagement_metrics AS (
  SELECT
    user_id,
    event_date,
    page_views,
    clicks,
    purchases,
    total_events,
    -- Engagement score
    (page_views * 1.0) + (clicks * 2.0) + (purchases * 10.0) AS engagement_score,
    -- Running totals
    SUM(total_events) OVER (
      PARTITION BY user_id
      ORDER BY event_date
      ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS events_last_7_days
  FROM event_pivot
)

SELECT
  user_id,
  event_date,
  page_views,
  clicks,
  purchases,
  total_events,
  engagement_score,
  events_last_7_days,
  -- Engagement tier
  CASE
    WHEN engagement_score >= 100 THEN 'high'
    WHEN engagement_score >= 50 THEN 'medium'
    ELSE 'low'
  END AS engagement_tier
FROM engagement_metrics;
