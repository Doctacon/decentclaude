#!/usr/bin/env python3
"""
legacy-quality-check.py - Example legacy data quality check script

This demonstrates common patterns in legacy Python scripts that should
be migrated to DecentClaude utilities.

Problems with this approach:
- No error handling or retry logic
- Repeated API calls with no caching
- Manual quality check logic (reinventing the wheel)
- No structured output for alerting
- Difficult to maintain and extend
"""

import sys
from google.cloud import bigquery

def check_table_quality(table_id):
    """Run quality checks on a table"""
    client = bigquery.Client()

    print(f"Checking quality for: {table_id}")

    # Get table metadata (API call 1)
    table = client.get_table(table_id)
    print(f"Rows: {table.num_rows}")

    # Check for null values (API call 2)
    null_check_query = f"""
    SELECT
      COUNTIF(user_id IS NULL) as null_user_ids,
      COUNTIF(email IS NULL) as null_emails,
      COUNTIF(created_at IS NULL) as null_created_at
    FROM `{table_id}`
    """
    null_results = list(client.query(null_check_query).result())[0]

    # Manual threshold checking
    null_threshold = 0.01  # 1%
    total_rows = table.num_rows

    if null_results.null_user_ids / total_rows > null_threshold:
        print(f"WARNING: High null rate for user_id: {null_results.null_user_ids}")

    if null_results.null_emails / total_rows > null_threshold:
        print(f"WARNING: High null rate for email: {null_results.null_emails}")

    # Check for duplicates (API call 3)
    dup_check_query = f"""
    SELECT COUNT(*) as duplicate_count
    FROM (
      SELECT user_id, COUNT(*) as cnt
      FROM `{table_id}`
      GROUP BY user_id
      HAVING cnt > 1
    )
    """
    dup_results = list(client.query(dup_check_query).result())[0]

    if dup_results.duplicate_count > 0:
        print(f"ERROR: Found {dup_results.duplicate_count} duplicate user_ids")
        sys.exit(1)

    # Check for future dates (API call 4)
    future_date_query = f"""
    SELECT COUNT(*) as future_date_count
    FROM `{table_id}`
    WHERE created_at > CURRENT_TIMESTAMP()
    """
    future_results = list(client.query(future_date_query).result())[0]

    if future_results.future_date_count > 0:
        print(f"ERROR: Found {future_results.future_date_count} future dates")
        sys.exit(1)

    # Check email format (API call 5)
    email_check_query = f"""
    SELECT COUNT(*) as invalid_emails
    FROM `{table_id}`
    WHERE email IS NOT NULL
      AND NOT REGEXP_CONTAINS(email, r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{{2,}}$')
    """
    email_results = list(client.query(email_check_query).result())[0]

    if email_results.invalid_emails > total_rows * 0.001:  # 0.1% threshold
        print(f"WARNING: Found {email_results.invalid_emails} invalid emails")

    print("Quality checks complete!")

    # No structured output for automation
    # No caching of results
    # No historical comparison
    # No automatic alerting


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: legacy-quality-check.py <table_id>")
        sys.exit(1)

    check_table_quality(sys.argv[1])
