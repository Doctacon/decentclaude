-- Example: Data Quality Check Query
-- This demonstrates a query that checks for data quality issues

WITH quality_checks AS (
  SELECT
    'null_emails' AS check_name,
    COUNT(*) AS failure_count
  FROM `project.dataset.users`
  WHERE email IS NULL

  UNION ALL

  SELECT
    'duplicate_users' AS check_name,
    COUNT(*) - COUNT(DISTINCT user_id) AS failure_count
  FROM `project.dataset.users`

  UNION ALL

  SELECT
    'invalid_dates' AS check_name,
    COUNT(*) AS failure_count
  FROM `project.dataset.users`
  WHERE created_at > CURRENT_TIMESTAMP()

  UNION ALL

  SELECT
    'old_records' AS check_name,
    COUNT(*) AS failure_count
  FROM `project.dataset.users`
  WHERE updated_at < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
)

SELECT
  check_name,
  failure_count,
  CASE
    WHEN failure_count = 0 THEN 'PASS'
    ELSE 'FAIL'
  END AS status
FROM quality_checks
ORDER BY failure_count DESC;
