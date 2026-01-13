# Step 3: Your First dbt Model

## Overview

Now that your environment is set up, let's create your first dbt model. You'll learn how to write transformations, test them, and document them.

## What is a dbt Model?

A dbt model is a SQL SELECT statement that transforms raw data into analytics-ready tables. dbt handles:
- Running the SQL
- Creating/updating tables
- Managing dependencies
- Testing data quality

## 1. Create Your First Model

### Create a new model file:

```bash
# Create models directory (if it doesn't exist)
mkdir -p models/staging

# Create your first model
cat > models/staging/stg_users.sql <<EOF
{{
  config(
    materialized='view'
  )
}}

WITH source AS (
  SELECT *
  FROM \`{{ var('project_id') }}.raw_data.users\`
),

renamed AS (
  SELECT
    user_id,
    email,
    LOWER(email) as email_normalized,
    created_at,
    updated_at,
    is_active,
    -- Data quality: Flag invalid emails
    REGEXP_CONTAINS(email, r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$') as is_valid_email
  FROM source
)

SELECT * FROM renamed
EOF
```

### Key concepts in this model:

- **CTEs (Common Table Expressions)**: `WITH source AS ...` organizes your SQL
- **Config block**: `{{ config(...) }}` sets how dbt materializes the model
- **Jinja templating**: `{{ var('project_id') }}` for dynamic values
- **Data quality**: Added `is_valid_email` flag

## 2. Configure Model Properties

Create a schema YAML file to define tests and documentation:

```bash
cat > models/staging/schema.yml <<EOF
version: 2

models:
  - name: stg_users
    description: "Staging table for user data with basic cleaning and validation"
    columns:
      - name: user_id
        description: "Unique identifier for users"
        tests:
          - unique
          - not_null

      - name: email
        description: "User email address (original case)"
        tests:
          - not_null

      - name: email_normalized
        description: "Lowercase email for consistent matching"

      - name: is_valid_email
        description: "Boolean flag indicating if email matches standard format"
        tests:
          - accepted_values:
              values: [true, false]

      - name: created_at
        description: "Timestamp when user was created"
        tests:
          - not_null

      - name: is_active
        description: "Boolean indicating if user account is active"
EOF
```

## 3. Run Your Model

### Compile the model (check for syntax errors):

```bash
dbt compile --select stg_users
```

### Run the model:

```bash
dbt run --select stg_users
```

Expected output:
```
Running with dbt=1.7.0
Found 1 model, 5 tests, 0 snapshots, 0 analyses, 0 macros, 0 operations, 0 seed files, 0 sources

Concurrency: 4 threads (target='dev')

1 of 1 START sql view model dbt_dev.stg_users ..................... [RUN]
1 of 1 OK created sql view model dbt_dev.stg_users ................ [CREATE VIEW in 1.2s]

Finished running 1 view model in 2.5s.

Completed successfully
```

## 4. Test Your Model

Run the tests defined in schema.yml:

```bash
dbt test --select stg_users
```

Expected output:
```
Running with dbt=1.7.0
Found 1 model, 5 tests, 0 snapshots, 0 analyses, 0 macros, 0 operations, 0 seed files, 0 sources

Concurrency: 4 threads (target='dev')

1 of 5 START test not_null_stg_users_user_id ...................... [RUN]
1 of 5 PASS not_null_stg_users_user_id ............................ [PASS in 0.8s]
2 of 5 START test unique_stg_users_user_id ........................ [RUN]
2 of 5 PASS unique_stg_users_user_id .............................. [PASS in 0.7s]
... (more tests)

Finished running 5 tests in 3.2s.

Completed successfully
Done. PASS=5 WARN=0 ERROR=0 SKIP=0 TOTAL=5
```

## 5. Understanding the Workflow

The dbt development cycle:

```
1. Write SQL → 2. Compile → 3. Run → 4. Test → 5. Document
                    ↓                              ↓
                 Fix errors ←────────── Iterate ←──┘
```

## Best Practices (from data-engineering-patterns.md)

### Model Organization

```
models/
├── staging/        # 1:1 with source tables, light transformations
├── intermediate/   # Business logic, reusable building blocks
└── marts/          # Final analytics tables
```

### Naming Conventions

- `stg_` prefix for staging models
- `int_` prefix for intermediate models
- `fct_` prefix for fact tables
- `dim_` prefix for dimension tables

### Materialization Strategy

- **Views**: Staging models (fast builds, query-time computation)
- **Tables**: Marts (slower builds, fast queries)
- **Incremental**: Large fact tables (efficient updates)

## Interactive Exercise

Modify your model to add a new transformation:

```sql
-- Add this to the renamed CTE in stg_users.sql
EXTRACT(DATE FROM created_at) as signup_date,
DATE_DIFF(CURRENT_DATE(), EXTRACT(DATE FROM created_at), DAY) as days_since_signup
```

Then:

```bash
# 1. Compile to check syntax
dbt compile --select stg_users

# 2. Run the updated model
dbt run --select stg_users

# 3. View the results
bq query --use_legacy_sql=false "SELECT * FROM \`your-project.dbt_dev.stg_users\` LIMIT 5"
```

## Common Issues

### Issue: "Relation not found"

**Solution**: Check that the source table exists:
```bash
bq ls --project_id=your-project raw_data
```

### Issue: "Compilation Error: var 'project_id' is undefined"

**Solution**: Define the variable in dbt_project.yml:
```yaml
vars:
  project_id: "your-project-id"
```

### Issue: Tests failing

**Solution**: Investigate the failures:
```bash
# Run tests with verbose output
dbt test --select stg_users --store-failures

# Query the failed test results
bq query --use_legacy_sql=false "SELECT * FROM \`your-project.dbt_dev.test_failures\`"
```

## Checkpoint Questions

1. What's the difference between `dbt compile` and `dbt run`?
2. Where do you define tests for your models?
3. What materialization should you use for staging models?

<details>
<summary>View Answers</summary>

1. `dbt compile` checks SQL syntax without creating tables; `dbt run` executes SQL and creates/updates tables
2. In a `schema.yml` file in the same directory as your models
3. Views (they're lightweight and rebuild quickly)

</details>

## What You Learned

- Creating dbt models with SQL
- Configuring model materialization
- Writing tests in schema.yml
- Running and testing models
- Best practices for model organization

## Next Step

Continue to [Step 4: Running Data Quality Checks](04-data-quality-checks.md) to learn advanced validation techniques.
