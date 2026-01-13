-- Example: Data Quality Check Query (Working Example)
-- This demonstrates data quality checks using real BigQuery tables
-- Compare with data_quality.sql for the template version

WITH quality_checks AS (
  SELECT
    'null_emails' AS check_name,
    COUNT(*) AS failure_count
  FROM `segment-warehouse-236622.salesforce_v4.user`
  WHERE email IS NULL

  UNION ALL

  SELECT
    'duplicate_users' AS check_name,
    COUNT(*) - COUNT(DISTINCT id) AS failure_count
  FROM `segment-warehouse-236622.salesforce_v4.user`

  UNION ALL

  SELECT
    'invalid_dates' AS check_name,
    COUNT(*) AS failure_count
  FROM `segment-warehouse-236622.salesforce_v4.user`
  WHERE created_date > CURRENT_TIMESTAMP()

  UNION ALL

  SELECT
    'stale_records' AS check_name,
    COUNT(*) AS failure_count
  FROM `segment-warehouse-236622.salesforce_v4.user`
  WHERE last_modified_date < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 365 DAY)
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
