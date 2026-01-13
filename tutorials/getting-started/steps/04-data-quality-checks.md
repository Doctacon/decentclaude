# Step 4: Running Data Quality Checks

## Overview

Data quality is critical for reliable analytics. In this step, you'll learn how to use DecentClaude's data quality framework to validate your transformations beyond basic dbt tests.

## The Data Quality Framework

DecentClaude includes a Python-based data quality framework (`scripts/data_quality.py`) that provides:

- Custom validation rules
- Statistical anomaly detection
- Cross-table consistency checks
- Automated reporting

## 1. Understanding the Framework

### View the framework structure:

```bash
# Read the data quality framework
cat scripts/data_quality.py
```

Key components:

- **DataQualityCheck** base class - Framework for custom checks
- **run_check()** method - Executes validation logic
- **report()** method - Formats results

## 2. Create Your First Quality Check

Create a custom check for your `stg_users` model:

```bash
cat > scripts/checks/validate_users.py <<EOF
#!/usr/bin/env python3
"""Data quality checks for stg_users model."""

import sys
sys.path.append('scripts')

from data_quality import DataQualityCheck
from google.cloud import bigquery

class ValidateUserEmails(DataQualityCheck):
    """Validate that user emails are properly formatted."""

    def __init__(self, project_id: str, dataset: str):
        super().__init__()
        self.project_id = project_id
        self.dataset = dataset
        self.client = bigquery.Client(project=project_id)

    def run_check(self):
        """Check email validity distribution."""
        query = f"""
        SELECT
          COUNT(*) as total_users,
          COUNTIF(is_valid_email) as valid_emails,
          COUNTIF(NOT is_valid_email) as invalid_emails,
          ROUND(COUNTIF(is_valid_email) / COUNT(*) * 100, 2) as valid_pct
        FROM \`{self.project_id}.{self.dataset}.stg_users\`
        """

        result = self.client.query(query).to_dataframe()

        total = result['total_users'][0]
        valid_pct = result['valid_pct'][0]

        # Check passes if >95% emails are valid
        self.passed = valid_pct >= 95.0
        self.message = f"Email validity: {valid_pct}% ({result['valid_emails'][0]}/{total})"

        if not self.passed:
            self.message += f" - FAILED: Expected >=95% valid emails"

        return self.passed

class ValidateUserActivity(DataQualityCheck):
    """Validate user activity distribution."""

    def __init__(self, project_id: str, dataset: str):
        super().__init__()
        self.project_id = project_id
        self.dataset = dataset
        self.client = bigquery.Client(project=project_id)

    def run_check(self):
        """Check active user percentage."""
        query = f"""
        SELECT
          COUNT(*) as total_users,
          COUNTIF(is_active) as active_users,
          ROUND(COUNTIF(is_active) / COUNT(*) * 100, 2) as active_pct
        FROM \`{self.project_id}.{self.dataset}.stg_users\`
        """

        result = self.client.query(query).to_dataframe()

        active_pct = result['active_pct'][0]

        # Check passes if active rate is reasonable (>10%)
        self.passed = active_pct >= 10.0
        self.message = f"Active users: {active_pct}% ({result['active_users'][0]}/{result['total_users'][0]})"

        if not self.passed:
            self.message += f" - FAILED: Suspiciously low active user rate"

        return self.passed

if __name__ == "__main__":
    import os

    project_id = os.environ.get('GCP_PROJECT_ID')
    dataset = os.environ.get('BQ_DATASET', 'dbt_dev')

    print("Running data quality checks on stg_users...")
    print("=" * 60)

    checks = [
        ValidateUserEmails(project_id, dataset),
        ValidateUserActivity(project_id, dataset),
    ]

    all_passed = True
    for check in checks:
        check.run_check()
        check.report()
        all_passed = all_passed and check.passed

    print("=" * 60)
    if all_passed:
        print("✓ All checks passed!")
        sys.exit(0)
    else:
        print("✗ Some checks failed!")
        sys.exit(1)
EOF

chmod +x scripts/checks/validate_users.py
```

## 3. Run Quality Checks

### Execute your custom checks:

```bash
# Set environment variables
export GCP_PROJECT_ID="your-project-id"
export BQ_DATASET="dbt_dev"

# Run the checks
python scripts/checks/validate_users.py
```

Expected output:
```
Running data quality checks on stg_users...
============================================================
✓ PASSED: Email validity: 98.5% (985/1000)
✓ PASSED: Active users: 67.3% (673/1000)
============================================================
✓ All checks passed!
```

## 4. Advanced Quality Checks

### Statistical Anomaly Detection

Create a check that detects unusual patterns:

```python
class ValidateSignupRate(DataQualityCheck):
    """Validate signup rate is within expected range."""

    def run_check(self):
        query = f"""
        WITH daily_signups AS (
          SELECT
            EXTRACT(DATE FROM created_at) as signup_date,
            COUNT(*) as signups
          FROM \`{self.project_id}.{self.dataset}.stg_users\`
          WHERE created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
          GROUP BY 1
        ),
        stats AS (
          SELECT
            AVG(signups) as mean,
            STDDEV(signups) as stddev
          FROM daily_signups
        )
        SELECT
          d.signup_date,
          d.signups,
          s.mean,
          s.stddev,
          -- Flag if more than 3 standard deviations from mean
          ABS(d.signups - s.mean) > 3 * s.stddev as is_anomaly
        FROM daily_signups d
        CROSS JOIN stats s
        ORDER BY d.signup_date DESC
        LIMIT 7
        """

        result = self.client.query(query).to_dataframe()
        anomalies = result[result['is_anomaly'] == True]

        self.passed = len(anomalies) == 0
        self.message = f"Signup rate: {len(anomalies)} anomalies detected in last 7 days"

        return self.passed
```

## 5. Integration with dbt Tests

You can also create custom dbt tests for data quality:

```bash
# Create a custom dbt test
mkdir -p tests/data_quality

cat > tests/data_quality/test_email_domains.sql <<EOF
-- Test that all emails use approved domains
SELECT
  email,
  REGEXP_EXTRACT(email, r'@(.+)$') as domain
FROM {{ ref('stg_users') }}
WHERE REGEXP_EXTRACT(email, r'@(.+)$') NOT IN (
  'gmail.com',
  'yahoo.com',
  'company.com'
)
AND is_valid_email = true
EOF
```

Run the custom test:

```bash
dbt test --select test_email_domains
```

## 6. Automated Quality Reports

Create a script to run all quality checks and generate a report:

```bash
cat > scripts/run_all_quality_checks.sh <<EOF
#!/bin/bash
# Run all data quality checks and generate report

set -e

REPORT_FILE="quality_report_\$(date +%Y%m%d_%H%M%S).txt"

echo "DecentClaude Data Quality Report" > \$REPORT_FILE
echo "Generated: \$(date)" >> \$REPORT_FILE
echo "======================================" >> \$REPORT_FILE
echo "" >> \$REPORT_FILE

# Run dbt tests
echo "Running dbt tests..." >> \$REPORT_FILE
dbt test --select stg_users 2>&1 | tee -a \$REPORT_FILE
echo "" >> \$REPORT_FILE

# Run custom Python checks
echo "Running custom quality checks..." >> \$REPORT_FILE
python scripts/checks/validate_users.py 2>&1 | tee -a \$REPORT_FILE
echo "" >> \$REPORT_FILE

echo "Report saved to \$REPORT_FILE"
EOF

chmod +x scripts/run_all_quality_checks.sh
```

## Best Practices

### 1. Layer Your Quality Checks

```
Level 1: dbt schema tests (fast, basic validation)
  ↓
Level 2: Custom dbt tests (SQL-based business rules)
  ↓
Level 3: Python framework (complex statistical checks)
  ↓
Level 4: Monitoring & alerting (production checks)
```

### 2. Quality Check Principles

- **Fast feedback**: Run basic checks in CI/CD
- **Progressive validation**: More thorough checks in production
- **Clear failure messages**: Help debugging
- **Automated remediation**: Auto-fix when possible

### 3. When to Use Each Tool

**dbt schema tests**:
- Column-level constraints (not null, unique)
- Referential integrity
- Accepted values

**Custom dbt tests**:
- Business logic validation
- Cross-table consistency
- Complex SQL conditions

**Python framework**:
- Statistical analysis
- Machine learning-based anomaly detection
- External API validation
- Complex multi-step checks

## Interactive Exercise

Create your own quality check:

1. **Identify a quality dimension** (completeness, accuracy, consistency, timeliness)
2. **Write the check** using the DataQualityCheck base class
3. **Run it** on your stg_users model
4. **Document the check** in your project README

Example starter:

```python
class ValidateCompleteness(DataQualityCheck):
    """Check that critical fields have minimal nulls."""

    def run_check(self):
        # Your validation logic here
        pass
```

## Checkpoint Questions

1. What are the three levels of data quality checks in DecentClaude?
2. When should you use a custom dbt test vs. the Python framework?
3. What makes a good data quality check?

<details>
<summary>View Answers</summary>

1. dbt schema tests, custom dbt tests, and Python framework checks
2. Use dbt tests for SQL-based validation; use Python for statistical analysis or external integrations
3. Fast, clear failure messages, automated when possible, appropriate for the quality dimension

</details>

## What You Learned

- Using the DecentClaude data quality framework
- Creating custom validation checks
- Integrating quality checks with dbt
- Best practices for multi-layered validation
- Automated quality reporting

## Congratulations!

You've completed the Getting Started tutorial. You now know:

- The DecentClaude project structure
- How to set up your environment
- Creating and testing dbt models
- Building comprehensive data quality checks

## Next Steps

Continue your learning journey:

1. **dbt Basics Tutorial** - Advanced transformation patterns
2. **BigQuery Optimization Tutorial** - Performance tuning
3. **Incident Response Tutorial** - Handling production issues

Or explore the knowledge base:

- [Data Engineering Patterns](../../../data-engineering-patterns.md)
- [Data Testing Patterns](../../../data-testing-patterns.md)
- [Operational Playbooks](../../../playbooks.md)
