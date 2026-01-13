# AI-Generate Usage Examples

This document provides comprehensive examples of using the `ai-generate` CLI tool for various data engineering code generation tasks.

## Prerequisites

1. Install the anthropic library:
   ```bash
   pip install anthropic
   ```

2. Set your API key:
   ```bash
   export ANTHROPIC_API_KEY='your-api-key-here'
   ```

## Basic Usage

### Generate dbt Model

Generate a staging model for user events:

```bash
bin/data-utils/ai-generate dbt-model \
  "Create a staging model for user events that extracts user_id, event_type, event_timestamp, and session_id from raw events. Filter to events from the last 90 days." \
  --output=models/staging/stg_analytics__user_events.sql
```

### Generate SQLMesh Model

Generate an incremental SQLMesh model for daily aggregations:

```bash
bin/data-utils/ai-generate sqlmesh-model \
  "Create a daily user engagement model that aggregates events by user and date, calculating total events, unique sessions, and total time spent. Use incremental processing by date." \
  --output=models/analytics/user_engagement_daily.sql
```

### Generate Data Quality Test

Generate a test to validate data quality:

```bash
bin/data-utils/ai-generate test \
  "Test that ensures each user_id appears only once per day in the user_engagement_daily table" \
  --output=tests/assert_unique_user_per_day.sql
```

### Generate Transformation Logic

Generate a reusable macro for common transformations:

```bash
bin/data-utils/ai-generate transform \
  "Create a dbt macro that calculates a 7-day rolling average for any numeric column, handling nulls appropriately" \
  --output=macros/rolling_average.sql
```

### Generate Migration Script

Generate a migration script for schema changes:

```bash
bin/data-utils/ai-generate migration \
  "Add date-based partitioning to the events table by event_date column, and cluster by user_id and event_type" \
  --output=migrations/001_partition_events_table.sql
```

## Advanced Usage

### Using Context Files

Provide additional context like table schemas:

```bash
# Create a context file with schema information
cat > schema_context.txt << 'EOF'
Source table: raw.events
Columns:
- event_id: STRING
- user_id: STRING
- event_type: STRING (values: page_view, click, purchase, signup)
- event_timestamp: TIMESTAMP
- session_id: STRING
- properties: JSON
EOF

# Use the context file
bin/data-utils/ai-generate dbt-model \
  "Create a staging model that parses the properties JSON field and extracts page_url, referrer, and device_type" \
  --context=schema_context.txt \
  --output=models/staging/stg_events_parsed.sql
```

### JSON Output Format

Get structured JSON output for programmatic use:

```bash
bin/data-utils/ai-generate dbt-model \
  "Simple daily aggregation of user events" \
  --format=json | jq .
```

Output structure:
```json
{
  "success": true,
  "type": "dbt-model",
  "code": "{{ config(...) }}\n...",
  "model": "claude-sonnet-4-5-20250929",
  "tokens": {
    "input": 1234,
    "output": 567
  }
}
```

### Using Different Claude Models

Use a specific Claude model:

```bash
bin/data-utils/ai-generate dbt-model \
  "Complex fact table with multiple dimensions" \
  --model=claude-opus-4-5-20251101 \
  --output=models/marts/fct_orders.sql
```

### Requirements from File

Create a requirements file and reference it:

```bash
cat > requirements/user_metrics.txt << 'EOF'
Create a dbt model that:
1. Aggregates user events by day
2. Calculates:
   - Total events per user per day
   - Unique event types
   - First and last event timestamps
   - Session count
3. Partitions by date
4. Clusters by user_id
5. Includes appropriate WHERE clause for incremental processing
6. Uses proper naming convention (fct_user_daily_metrics)
EOF

bin/data-utils/ai-generate dbt-model requirements/user_metrics.txt \
  --output=models/marts/fct_user_daily_metrics.sql
```

## Real-World Scenarios

### Scenario 1: Building a Complete Data Model Layer

```bash
# Generate staging model
bin/data-utils/ai-generate dbt-model \
  "Staging model for orders table: clean and standardize order_id, user_id, order_date, total_amount, status" \
  --output=models/staging/stg_orders.sql

# Generate intermediate transformation
bin/data-utils/ai-generate dbt-model \
  "Intermediate model that enriches orders with user lifetime metrics: total_orders, total_spent, avg_order_value, first_order_date, last_order_date" \
  --output=models/intermediate/int_orders_with_user_metrics.sql

# Generate fact table
bin/data-utils/ai-generate dbt-model \
  "Fact table that combines enriched orders with product and category dimensions for analytics" \
  --output=models/marts/fct_orders.sql

# Generate tests
bin/data-utils/ai-generate test \
  "Test that order totals in fct_orders match the sum in staging" \
  --output=tests/assert_order_totals_match.sql
```

### Scenario 2: Creating SQLMesh Incremental Models

```bash
# Daily aggregation
bin/data-utils/ai-generate sqlmesh-model \
  "Daily revenue by product category with incremental processing by order_date" \
  --output=models/revenue_by_category_daily.sql

# Weekly rollup
bin/data-utils/ai-generate sqlmesh-model \
  "Weekly active users model with 7-day rolling calculation, incremental by week" \
  --output=models/weekly_active_users.sql
```

### Scenario 3: Data Quality Test Suite

```bash
# Uniqueness test
bin/data-utils/ai-generate test \
  "Validate that order_id is unique in fct_orders" \
  --output=tests/assert_unique_order_id.sql

# Referential integrity test
bin/data-utils/ai-generate test \
  "Ensure all user_ids in fct_orders exist in dim_users" \
  --output=tests/assert_valid_user_references.sql

# Business logic test
bin/data-utils/ai-generate test \
  "Verify that order total equals sum of line item amounts" \
  --output=tests/assert_order_totals_accurate.sql

# Freshness test
bin/data-utils/ai-generate test \
  "Check that the most recent order_date is within the last 2 days" \
  --output=tests/assert_data_freshness.sql
```

### Scenario 4: Migration Scripts

```bash
# Add partitioning
bin/data-utils/ai-generate migration \
  "Add date partitioning to orders table by order_date with 90-day expiration" \
  --output=migrations/001_partition_orders.sql

# Add clustering
bin/data-utils/ai-generate migration \
  "Add clustering to events table by user_id, event_type, and session_id" \
  --output=migrations/002_cluster_events.sql

# Schema change
bin/data-utils/ai-generate migration \
  "Add new columns to users table: signup_method (STRING), referral_source (STRING), is_verified (BOOLEAN)" \
  --output=migrations/003_add_user_columns.sql
```

## Tips and Best Practices

### 1. Be Specific in Requirements

**Poor:**
```bash
ai-generate dbt-model "user model"
```

**Better:**
```bash
ai-generate dbt-model \
  "Dimension table for users with user_id, email, signup_date, country, subscription_tier. Use SCD Type 1. Cluster by country."
```

### 2. Use Context Files for Complex Schemas

When working with complex schemas or multiple source tables, create a context file:

```bash
cat > context.txt << 'EOF'
Source tables:
- users: user_id, email, created_at
- subscriptions: subscription_id, user_id, plan, start_date, end_date
- payments: payment_id, user_id, amount, payment_date

Goal: Create a user metrics model showing lifetime value
EOF

ai-generate dbt-model "Calculate user lifetime value" --context=context.txt
```

### 3. Review and Refine Generated Code

Always review the generated code and make adjustments as needed:

```bash
# Generate initial version
ai-generate dbt-model "user metrics" --output=temp.sql

# Review and make manual adjustments
# Then move to final location
mv temp.sql models/marts/fct_user_metrics.sql
```

### 4. Combine with Other Tools

Use ai-generate as part of a larger workflow:

```bash
# Generate model
bin/data-utils/ai-generate dbt-model "daily revenue" --output=models/revenue_daily.sql

# Estimate query cost
bin/data-utils/bq-query-cost --file=models/revenue_daily.sql

# Validate schema
dbt compile -s revenue_daily
```

## Environment Variables

Set these environment variables for optimal usage:

```bash
# Required
export ANTHROPIC_API_KEY='your-api-key'

# Optional: Use a different default model
export AI_GENERATE_MODEL='claude-sonnet-4-5-20250929'

# Optional: Default output directory
export AI_GENERATE_OUTPUT_DIR='generated_models'
```

## Troubleshooting

### API Key Not Set

```
Error: ANTHROPIC_API_KEY environment variable not set
```

Solution:
```bash
export ANTHROPIC_API_KEY='your-key-here'
```

### Module Not Found

```
ModuleNotFoundError: No module named 'anthropic'
```

Solution:
```bash
pip install anthropic
```

### Output Directory Doesn't Exist

The tool automatically creates parent directories, but ensure you have write permissions:

```bash
mkdir -p models/staging
bin/data-utils/ai-generate dbt-model "..." --output=models/staging/model.sql
```

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Set your API key: `export ANTHROPIC_API_KEY='...'`
3. Try the basic examples above
4. Integrate into your dbt or SQLMesh workflow
5. Create custom context files for your data warehouse schema
6. Build a library of generated models and tests

## Support

For issues or questions:
- Check the main README.md
- Review the data-engineering-patterns.md guide
- See the Claude Code documentation
