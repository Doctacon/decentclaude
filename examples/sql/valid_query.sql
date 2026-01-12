-- Example: Valid BigQuery SQL
-- This file demonstrates a properly formatted SQL query

SELECT
  user_id,
  email,
  created_at,
  DATE(created_at) AS signup_date,
  COUNT(*) OVER (PARTITION BY DATE(created_at)) AS daily_signups
FROM
  `project.dataset.users`
WHERE
  created_at >= '2024-01-01'
  AND email IS NOT NULL
  AND status = 'active'
ORDER BY
  created_at DESC
LIMIT 1000;
