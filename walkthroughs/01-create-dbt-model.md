# Walkthrough: Creating a New dbt Model

## Overview

This walkthrough guides you through creating a new dbt model from scratch, including proper configuration, testing, and documentation.

## Prerequisites

- dbt installed and configured
- Access to BigQuery
- Familiarity with SQL
- Completed the Getting Started tutorial

## Time Estimate

15-20 minutes

## Steps

### 1. Identify the Model Type

First, determine what type of model you're creating:

- **Staging (`stg_`)**: 1:1 with source tables, light cleaning
- **Intermediate (`int_`)**: Business logic, reusable components
- **Mart (`fct_` or `dim_`)**: Final analytics tables

**For this walkthrough**, we'll create an intermediate model called `int_user_metrics`.

### 2. Create the Model File

```bash
# Create the appropriate directory
mkdir -p models/intermediate

# Create the model file
touch models/intermediate/int_user_metrics.sql
```

### 3. Write the SQL

Open `models/intermediate/int_user_metrics.sql` and add:

```sql
{{
  config(
    materialized='view',
    tags=['intermediate', 'users']
  )
}}

WITH users AS (
  SELECT * FROM {{ ref('stg_users') }}
),

user_activity AS (
  SELECT * FROM {{ ref('stg_user_activity') }}
),

user_metrics AS (
  SELECT
    u.user_id,
    u.email,
    u.created_at,

    -- Engagement metrics
    COUNT(DISTINCT ua.activity_date) as days_active,
    COUNT(ua.activity_id) as total_activities,
    MAX(ua.activity_date) as last_activity_date,
    MIN(ua.activity_date) as first_activity_date,

    -- Recency
    DATE_DIFF(CURRENT_DATE(), MAX(ua.activity_date), DAY) as days_since_last_activity,

    -- Activity rate
    ROUND(
      COUNT(ua.activity_id) /
      GREATEST(DATE_DIFF(CURRENT_DATE(), MIN(ua.activity_date), DAY), 1),
      2
    ) as avg_activities_per_day

  FROM users u
  LEFT JOIN user_activity ua ON u.user_id = ua.user_id
  GROUP BY 1, 2, 3
)

SELECT * FROM user_metrics
```

### 4. Create Schema Documentation

Create or update `models/intermediate/schema.yml`:

```yaml
version: 2

models:
  - name: int_user_metrics
    description: >
      User engagement metrics aggregated from activity data.
      Includes recency, frequency, and activity patterns.

    columns:
      - name: user_id
        description: Unique identifier for the user
        tests:
          - unique
          - not_null
          - relationships:
              to: ref('stg_users')
              field: user_id

      - name: email
        description: User email address

      - name: days_active
        description: Total number of distinct days with activity
        tests:
          - not_null

      - name: total_activities
        description: Total count of all activities
        tests:
          - not_null

      - name: last_activity_date
        description: Date of most recent activity

      - name: days_since_last_activity
        description: Days between today and last activity
        tests:
          - dbt_utils.accepted_range:
              min_value: 0
              inclusive: true

      - name: avg_activities_per_day
        description: Average activities per day since first activity
        tests:
          - not_null
```

### 5. Compile the Model

Check for syntax errors:

```bash
dbt compile --select int_user_metrics
```

Expected output:
```
Compiled 1 model
```

### 6. Run the Model

Execute the model:

```bash
dbt run --select int_user_metrics
```

Expected output:
```
1 of 1 START sql view model analytics.int_user_metrics .... [RUN]
1 of 1 OK created sql view model analytics.int_user_metrics  [CREATE VIEW in 1.5s]
```

### 7. Test the Model

Run the tests defined in schema.yml:

```bash
dbt test --select int_user_metrics
```

All tests should pass:
```
Completed with 0 errors and 0 warnings
```

### 8. Generate Documentation

Update the dbt documentation:

```bash
dbt docs generate
dbt docs serve
```

Navigate to your model in the documentation to verify it appears correctly.

### 9. Add to Version Control

```bash
git add models/intermediate/int_user_metrics.sql
git add models/intermediate/schema.yml
git commit -m "Add int_user_metrics model for user engagement tracking"
```

## Validation

Verify your model is working correctly:

### 1. Check row count
```bash
bq query --use_legacy_sql=false \
  "SELECT COUNT(*) as row_count FROM \`your-project.analytics.int_user_metrics\`"
```

### 2. Spot check the data
```bash
bq query --use_legacy_sql=false \
  "SELECT * FROM \`your-project.analytics.int_user_metrics\` LIMIT 10"
```

### 3. Verify metrics make sense
```bash
bq query --use_legacy_sql=false \
  "SELECT
    AVG(days_active) as avg_days_active,
    AVG(total_activities) as avg_total_activities
   FROM \`your-project.analytics.int_user_metrics\`"
```

## Troubleshooting

### Issue: "Relation not found"

**Cause**: Referenced model doesn't exist or hasn't been run

**Solution**:
```bash
# Check dependencies
dbt ls --select +int_user_metrics

# Run upstream models first
dbt run --select +int_user_metrics
```

### Issue: Tests failing

**Cause**: Data quality issues or incorrect test configuration

**Solution**:
```bash
# Run tests with store-failures
dbt test --select int_user_metrics --store-failures

# Examine failures
bq query --use_legacy_sql=false \
  "SELECT * FROM \`your-project.dbt_test__audit.test_failures\` LIMIT 10"
```

### Issue: Performance is slow

**Cause**: Large data volume, inefficient SQL

**Solution**:
1. Change materialization to table:
   ```sql
   {{ config(materialized='table') }}
   ```

2. Add partitioning/clustering if applicable

3. Check query plan:
   ```bash
   dbt run --select int_user_metrics --debug
   ```

## Best Practices Checklist

- [ ] Model name follows naming convention
- [ ] Proper materialization strategy
- [ ] CTEs for organization
- [ ] Clear column names
- [ ] Comprehensive tests
- [ ] Documentation in schema.yml
- [ ] Tags for organization
- [ ] Validated with spot checks

## Related Resources

- [Data Engineering Patterns - dbt Best Practices](../data-engineering-patterns.md#dbt-best-practices)
- [Data Testing Patterns](../data-testing-patterns.md)
- [Creating Incremental Models](04-create-incremental-model.md)

## Next Steps

- Add this model to a mart
- Create data quality checks
- Set up monitoring
- Document in project README
