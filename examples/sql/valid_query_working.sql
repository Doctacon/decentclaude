-- Example: Valid BigQuery SQL (Working Example)
-- This query demonstrates proper SQL formatting using real BigQuery tables
-- Compare with valid_query.sql for the template version

SELECT
  id AS user_id,
  email,
  created_date,
  DATE(created_date) AS signup_date,
  COUNT(*) OVER (PARTITION BY DATE(created_date)) AS daily_signups
FROM
  `segment-warehouse-236622.salesforce_v4.user`
WHERE
  created_date >= '2024-01-01'
  AND email IS NOT NULL
  AND is_active = TRUE
ORDER BY
  created_date DESC
LIMIT 10;
