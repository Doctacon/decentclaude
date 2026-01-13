# Exercise 1: Create a Customer Summary Model

## Objective

Practice creating a dbt model by building a customer summary table that aggregates data from multiple sources.

## Scenario

Your company wants a daily summary of customer activity. You need to create a model that:

1. Aggregates customer data by day
2. Calculates key metrics
3. Includes data quality flags
4. Is properly tested

## Requirements

Create a model called `fct_customer_daily_summary` that includes:

**Dimensions**:
- customer_id
- activity_date
- customer_cohort (new/established/veteran)

**Metrics**:
- total_orders
- total_revenue
- average_order_value

**Quality Flags**:
- is_suspicious_activity (orders > 100 in a day)
- is_high_value (revenue > $10,000)

## Steps

1. Create the model file: `models/marts/fct_customer_daily_summary.sql`
2. Configure it as a table with date partitioning
3. Add appropriate CTEs for organization
4. Create a schema.yml with tests
5. Run and test your model

## Hints

- Use `{{ ref('stg_users') }}` to reference the staging table
- Partition by activity_date for better performance
- Add uniqueness test on `customer_id, activity_date`
- Test for null values on key fields

## Validation

Your model should pass:
```bash
dbt run --select fct_customer_daily_summary
dbt test --select fct_customer_daily_summary
```

## Time Estimate

30 minutes

## Solution

Check `solutions/exercise-1-solution.sql` after attempting the exercise yourself.
