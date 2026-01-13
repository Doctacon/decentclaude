# Data Engineering Patterns Library

A comprehensive guide to best practices for dbt, SQLMesh, BigQuery optimization, partitioning, clustering, and cost management for Claude-assisted development.

## Table of Contents

1. [dbt Models Best Practices](#dbt-models-best-practices)
2. [SQLMesh Migrations](#sqlmesh-migrations)
3. [BigQuery Optimization](#bigquery-optimization)
4. [Partitioning Strategies](#partitioning-strategies)
5. [Clustering Strategies](#clustering-strategies)
6. [Cost Management](#cost-management)

---

## dbt Models Best Practices

### Model Organization

**Layered Architecture**
```
models/
├── staging/          # Raw data cleaning and renaming
│   └── stg_*.sql
├── intermediate/     # Business logic transformations
│   └── int_*.sql
└── marts/           # Final analytical models
    ├── core/
    └── finance/
```

**Naming Conventions**
- `stg_[source]__[entity].sql` - Staging models (e.g., `stg_salesforce__accounts.sql`)
- `int_[entity]__[verb].sql` - Intermediate models (e.g., `int_orders__pivoted.sql`)
- `fct_[entity].sql` - Fact tables (e.g., `fct_orders.sql`)
- `dim_[entity].sql` - Dimension tables (e.g., `dim_customers.sql`)

### Model Configuration

**Materialization Strategy**
```sql
-- staging: views (cheap, always fresh)
{{ config(materialized='view') }}

-- intermediate: ephemeral or views (reduce storage)
{{ config(materialized='ephemeral') }}

-- marts: tables or incremental (performance)
{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='fail'
) }}
```

**Incremental Models**
```sql
{{
  config(
    materialized='incremental',
    unique_key='id',
    incremental_strategy='merge',
    on_schema_change='fail'
  )
}}

select
  id,
  created_at,
  updated_at,
  -- columns
from source

{% if is_incremental() %}
  where updated_at > (select max(updated_at) from {{ this }})
{% endif %}
```

**Key Principles:**
- Use `on_schema_change='fail'` to catch breaking changes early
- Always include audit columns (created_at, updated_at, _loaded_at)
- Test unique_key constraints with dbt tests
- Use `{{ this }}` to reference the current model in incremental logic

### Testing Strategy

**Required Tests**
```yaml
# schema.yml
version: 2

models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
      - name: order_total
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
```

**Custom Data Tests**
```sql
-- tests/assert_order_total_matches_line_items.sql
select
  order_id,
  sum(line_item_total) as calculated_total,
  order_total
from {{ ref('fct_orders') }}
group by order_id, order_total
having abs(calculated_total - order_total) > 0.01
```

### Documentation

**Model Documentation**
```yaml
# models/schema.yml
models:
  - name: fct_orders
    description: >
      Order fact table containing one row per order with all order-level metrics.
      Grain: One row per order_id.
    columns:
      - name: order_id
        description: Unique identifier for each order
      - name: order_total
        description: Total order amount in USD, including tax and shipping
```

**Use doc blocks for complex logic**
```sql
{% docs payment_method_logic %}
Payment methods are normalized from various sources:
- Stripe: card types mapped directly
- PayPal: all mapped to 'paypal'
- Manual: classified as 'other'
{% enddocs %}
```

### Performance Optimization

**Avoid SELECT ***
```sql
-- BAD
select * from {{ ref('stg_orders') }}

-- GOOD
select
  order_id,
  customer_id,
  order_date,
  order_total
from {{ ref('stg_orders') }}
```

**Use CTEs for readability**
```sql
with orders as (
  select * from {{ ref('stg_orders') }}
),

customers as (
  select * from {{ ref('stg_customers') }}
),

final as (
  select
    orders.order_id,
    customers.customer_name,
    orders.order_total
  from orders
  inner join customers using (customer_id)
)

select * from final
```

**Limit joins in staging models**
- Staging: Clean and rename only
- Intermediate: Join and transform
- Marts: Final business logic

---

## SQLMesh Migrations

### Project Structure

```
sqlmesh/
├── config.yaml              # Environment configuration
├── models/                  # SQL models
│   ├── staging/
│   ├── intermediate/
│   └── marts/
├── audits/                  # Data quality checks
├── macros/                  # Reusable SQL snippets
└── tests/                   # Unit tests
```

### Model Definitions

**Basic Model**
```sql
-- models/staging/stg_orders.sql
MODEL (
  name staging.stg_orders,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column order_date
  ),
  start '2020-01-01',
  cron '@daily',
  grain [order_id]
);

SELECT
  order_id,
  customer_id,
  order_date,
  order_total,
  @loaded_at AS _loaded_at
FROM raw.orders
WHERE
  order_date BETWEEN @start_date AND @end_date
```

**Model Kinds**

```sql
-- VIEW: Always recomputed
MODEL (
  name staging.stg_customers,
  kind VIEW
);

-- INCREMENTAL_BY_TIME_RANGE: Partitioned by time
MODEL (
  name marts.fct_orders,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column order_date
  ),
  partitioned_by order_date,
  clustered_by [customer_id]
);

-- INCREMENTAL_BY_UNIQUE_KEY: Upsert by key
MODEL (
  name staging.stg_users,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key user_id
  )
);

-- FULL: Always rebuild
MODEL (
  name marts.dim_customers,
  kind FULL
);
```

### Migration Workflow

**1. Development Cycle**
```bash
# Create new model or modify existing
vim models/staging/stg_new_table.sql

# Plan changes (dry run)
sqlmesh plan dev

# Review plan output:
# - Models to be created/modified
# - Backfill requirements
# - Breaking changes

# Apply plan
sqlmesh plan dev --auto-apply

# Run tests
sqlmesh test
```

**2. Production Deployment**
```bash
# Create production plan
sqlmesh plan prod

# Review:
# - Forward-only changes (no breaking changes)
# - Backfill strategy
# - Data quality impact

# Apply to production
sqlmesh plan prod --auto-apply

# Monitor execution
sqlmesh info prod
```

### Breaking Changes

**Non-breaking changes:**
- Adding new columns
- Adding new models
- Changing model logic (forward-only)

**Breaking changes (require backfill):**
- Removing columns
- Changing column types
- Changing grain
- Changing partitioning

**Handling breaking changes:**
```sql
-- Option 1: Create new model version
MODEL (
  name marts.fct_orders_v2,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column order_date
  )
);

-- Option 2: Use forward-only flag (production)
MODEL (
  name marts.fct_orders,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column order_date
  ),
  forward_only true  -- Prevents backfill, only affects new data
);
```

### Audits and Tests

**Audit Definition**
```sql
-- audits/check_order_totals.sql
AUDIT (
  name check_order_totals
);

SELECT
  order_id,
  order_total,
  calculated_total
FROM (
  SELECT
    order_id,
    order_total,
    SUM(line_item_total) AS calculated_total
  FROM @this_model
  GROUP BY order_id, order_total
)
WHERE ABS(order_total - calculated_total) > 0.01
```

**Attach audit to model**
```sql
MODEL (
  name marts.fct_orders,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column order_date
  ),
  audits [check_order_totals]
);
```

### Macros

**Reusable SQL**
```sql
-- macros/surrogate_key.sql
@DEF(surrogate_key, columns)
  MD5(CONCAT(@each(@columns, c -> CAST(c AS STRING), ', ')))
@END

-- Usage in model
SELECT
  @surrogate_key([customer_id, order_date]) AS order_key,
  customer_id,
  order_date
FROM orders
```

---

## BigQuery Optimization

### Query Performance

**1. Reduce Data Scanned**

```sql
-- BAD: Scans entire table
SELECT *
FROM `project.dataset.large_table`
WHERE date = '2024-01-01'

-- GOOD: Uses partition pruning
SELECT
  user_id,
  event_name,
  event_timestamp
FROM `project.dataset.large_table`
WHERE DATE(event_timestamp) = '2024-01-01'  -- Partition column
```

**2. Use Approximate Aggregations**

```sql
-- Exact count (expensive)
SELECT COUNT(DISTINCT user_id) FROM large_table

-- Approximate count (99% accurate, much faster)
SELECT APPROX_COUNT_DISTINCT(user_id) FROM large_table

-- Other approximate functions
SELECT
  APPROX_TOP_COUNT(country, 10) AS top_countries,
  APPROX_QUANTILES(revenue, 100)[OFFSET(50)] AS median_revenue
FROM sales
```

**3. Optimize Joins**

```sql
-- BAD: Large table first
SELECT *
FROM large_fact_table f
JOIN small_dimension_table d USING (dimension_id)

-- GOOD: Small table first
SELECT *
FROM small_dimension_table d
JOIN large_fact_table f USING (dimension_id)

-- BEST: Use appropriate join type
SELECT *
FROM large_fact_table f
LEFT JOIN small_dimension_table d USING (dimension_id)
WHERE d.active = true  -- Filter after join
```

**4. Use Nested and Repeated Fields**

```sql
-- BAD: Multiple joins for one-to-many
SELECT
  o.order_id,
  li.line_item_id,
  li.product_name
FROM orders o
JOIN line_items li USING (order_id)

-- GOOD: Use ARRAY of STRUCT
SELECT
  order_id,
  line_items  -- ARRAY<STRUCT<line_item_id INT64, product_name STRING>>
FROM orders
```

**5. Avoid Self-Joins with Window Functions**

```sql
-- BAD: Self-join for ranking
SELECT a.*
FROM orders a
JOIN (
  SELECT order_id, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) as rn
  FROM orders
) b ON a.order_id = b.order_id
WHERE b.rn = 1

-- GOOD: Window function directly
SELECT * FROM (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) as rn
  FROM orders
)
WHERE rn = 1
```

### Materialized Views

**When to use:**
- Frequently queried aggregations
- Complex joins that don't change often
- Pre-computed metrics for dashboards

**Example:**
```sql
CREATE MATERIALIZED VIEW `project.dataset.daily_revenue`
PARTITION BY DATE(order_date)
CLUSTER BY customer_segment
AS
SELECT
  DATE(order_date) as order_date,
  customer_segment,
  COUNT(DISTINCT order_id) as order_count,
  SUM(order_total) as total_revenue
FROM `project.dataset.orders`
GROUP BY 1, 2
```

**Benefits:**
- Automatic refresh
- Query optimizer can use it automatically
- Only changed partitions are updated

---

## Partitioning Strategies

### Time-Based Partitioning

**Daily Partitioning**
```sql
CREATE TABLE `project.dataset.events`
PARTITION BY DATE(event_timestamp)
OPTIONS(
  partition_expiration_days=90,
  require_partition_filter=true
)
AS
SELECT
  event_id,
  event_timestamp,
  user_id,
  event_type
FROM source_data
```

**Hourly Partitioning (for high-volume data)**
```sql
CREATE TABLE `project.dataset.streaming_events`
PARTITION BY TIMESTAMP_TRUNC(event_timestamp, HOUR)
OPTIONS(
  partition_expiration_days=7,
  require_partition_filter=true
)
```

**Monthly Partitioning (for historical data)**
```sql
CREATE TABLE `project.dataset.historical_orders`
PARTITION BY DATE_TRUNC(order_date, MONTH)
```

### Integer Range Partitioning

**For non-temporal data**
```sql
CREATE TABLE `project.dataset.customer_scores`
PARTITION BY RANGE_BUCKET(customer_score, GENERATE_ARRAY(0, 100, 10))
AS
SELECT
  customer_id,
  customer_score,  -- 0-100
  score_date
FROM customer_metrics
```

### Partitioning Best Practices

**1. Always use partition filters**
```sql
-- BAD: Full table scan
SELECT * FROM events
WHERE event_type = 'purchase'

-- GOOD: Partition pruning
SELECT * FROM events
WHERE DATE(event_timestamp) BETWEEN '2024-01-01' AND '2024-01-31'
  AND event_type = 'purchase'
```

**2. Set partition expiration**
```sql
-- Automatically delete old partitions
ALTER TABLE `project.dataset.events`
SET OPTIONS (
  partition_expiration_days=90
)
```

**3. Require partition filters (for large tables)**
```sql
ALTER TABLE `project.dataset.events`
SET OPTIONS (
  require_partition_filter=true
)
-- Now queries without partition filters will fail
```

**4. Monitor partition metadata**
```sql
-- Check partition sizes
SELECT
  partition_id,
  total_rows,
  ROUND(total_logical_bytes / POW(10, 9), 2) as gb
FROM `project.dataset.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'events'
ORDER BY partition_id DESC
LIMIT 10
```

---

## Clustering Strategies

### When to Use Clustering

**Use clustering when:**
- Queries filter on specific columns frequently
- Data within partitions is large (>1GB)
- Queries filter on multiple columns
- Order of data matters for your queries

**Don't use clustering when:**
- Partitions are small (<1GB)
- Queries scan entire tables
- Filter columns are high cardinality (>100k distinct values)

### Clustering Syntax

**Basic Clustering**
```sql
CREATE TABLE `project.dataset.orders`
PARTITION BY DATE(order_date)
CLUSTER BY customer_id, order_status
AS
SELECT
  order_id,
  order_date,
  customer_id,
  order_status,
  order_total
FROM source_orders
```

**Column Order Matters**
```sql
-- Good for: WHERE customer_id = X
-- Good for: WHERE customer_id = X AND order_status = 'completed'
CLUSTER BY customer_id, order_status

-- Good for: WHERE order_status = 'completed'
-- Less optimal for: WHERE customer_id = X
CLUSTER BY order_status, customer_id
```

### Clustering Best Practices

**1. Choose up to 4 clustering columns**
```sql
-- Optimal
CLUSTER BY customer_segment, product_category, order_status

-- Too many (diminishing returns)
CLUSTER BY c1, c2, c3, c4, c5, c6  -- Avoid
```

**2. Order by query frequency and cardinality**
```sql
-- customer_segment: 10 values, filtered often
-- product_category: 50 values, filtered sometimes
-- order_date: high cardinality, less often
CLUSTER BY customer_segment, product_category, order_date
```

**3. Combine with partitioning**
```sql
CREATE TABLE `project.dataset.user_events`
PARTITION BY DATE(event_timestamp)
CLUSTER BY user_id, event_type
OPTIONS(
  partition_expiration_days=90,
  require_partition_filter=true
)
```

**4. Monitor clustering effectiveness**
```sql
-- Check if table needs reclustering
SELECT
  table_name,
  total_logical_bytes / POW(10, 9) as gb,
  active_logical_bytes / total_logical_bytes as clustering_ratio
FROM `project.dataset.INFORMATION_SCHEMA.TABLES`
WHERE table_name = 'events'

-- clustering_ratio < 0.8 means table would benefit from reclustering
```

**5. Let BigQuery handle reclustering**
```sql
-- BigQuery automatically reclusters in the background
-- No manual intervention needed
-- But be aware of costs for frequently updated tables
```

### Clustering vs Partitioning

| Feature | Partitioning | Clustering |
|---------|-------------|------------|
| Number of columns | 1 | Up to 4 |
| Cost optimization | Partition pruning (major) | Block pruning (moderate) |
| Metadata overhead | Higher | Lower |
| Best for | Time-based queries | Multi-column filters |
| DML operations | Can be expensive | More efficient |

**Combined Example**
```sql
-- Best of both worlds
CREATE TABLE `project.dataset.sales`
PARTITION BY DATE(sale_date)  -- Prune by date
CLUSTER BY region, product_category, customer_segment  -- Prune within partitions
AS SELECT
  sale_id,
  sale_date,
  region,
  product_category,
  customer_segment,
  sale_amount
FROM raw_sales
```

---

## Cost Management

### Understanding BigQuery Costs

**Two pricing models:**

1. **On-Demand**: $6.25 per TB scanned (first 1 TB free per month)
2. **Flat-Rate**: Fixed monthly/annual pricing for reserved slots

**Storage costs:**
- Active storage: $0.02 per GB per month
- Long-term storage: $0.01 per GB per month (after 90 days)

### Cost Optimization Strategies

**1. Use Query Cost Estimation**
```sql
-- Dry run to estimate cost before running
# bq query --dry_run --use_legacy_sql=false \
  'SELECT * FROM `project.dataset.large_table` WHERE date = "2024-01-01"'

-- Returns: "Query will process X GB"
-- Cost = (X / 1024) * $6.25
```

**2. Leverage Partitioning and Clustering**
```sql
-- Without partition: Scans 100 GB
SELECT * FROM events
WHERE DATE(event_timestamp) = '2024-01-01'

-- With partition: Scans 1 GB
-- Cost savings: 99%
```

**3. Use Column Selection**
```sql
-- Bad: $6.25 per TB
SELECT * FROM large_table

-- Good: 90% cost reduction if you only need 10% of columns
SELECT user_id, event_name FROM large_table
```

**4. Materialized Views for Repeated Queries**
```sql
-- Running this daily costs N
SELECT
  DATE(order_date) as date,
  SUM(order_total) as revenue
FROM orders
GROUP BY 1

-- Create materialized view once, query costs ~0
CREATE MATERIALIZED VIEW daily_revenue
PARTITION BY date
AS
SELECT
  DATE(order_date) as date,
  SUM(order_total) as revenue
FROM orders
GROUP BY 1

-- Query the MV instead (automatic refresh)
SELECT * FROM daily_revenue
WHERE date BETWEEN '2024-01-01' AND '2024-01-31'
```

**5. Set Query Cost Limits**
```sql
-- Project-level: Prevent expensive accidents
bq mk --transfer_config \
  --project_id=my-project \
  --data_source=scheduled_query \
  --target_dataset=my_dataset \
  --maximum_bytes_billed=1099511627776  -- 1 TB limit
```

**6. Use BI Engine for Dashboards**
```sql
-- Enable BI Engine (in-memory analysis)
-- Flat fee, unlimited queries on cached data
-- Perfect for dashboards with repeated queries
```

**7. Monitor Costs with INFORMATION_SCHEMA**
```sql
-- Top 10 most expensive queries (last 30 days)
SELECT
  user_email,
  query,
  total_bytes_processed / POW(10, 12) as TB_processed,
  (total_bytes_processed / POW(10, 12)) * 6.25 as estimated_cost_usd,
  creation_time
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE
  DATE(creation_time) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  AND job_type = 'QUERY'
  AND statement_type != 'SCRIPT'
ORDER BY total_bytes_processed DESC
LIMIT 10
```

**8. Archive Old Data**
```sql
-- Move to cheaper long-term storage
-- Data not modified for 90 days automatically moves to long-term storage
-- 50% cost reduction ($0.02 -> $0.01 per GB)

-- For data you rarely query, export to Cloud Storage
bq extract \
  --destination_format PARQUET \
  --compression SNAPPY \
  project:dataset.old_table \
  gs://bucket/path/old_table-*.parquet

-- Query from Cloud Storage when needed (external table)
CREATE EXTERNAL TABLE `project.dataset.archived_data`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://bucket/path/old_table-*.parquet']
)
```

### Cost Monitoring Best Practices

**1. Set up billing alerts**
```bash
# In Google Cloud Console
# Billing > Budgets & Alerts
# Set threshold alerts at 50%, 90%, 100% of budget
```

**2. Create cost dashboards**
```sql
-- Create a scheduled query to track daily costs
CREATE OR REPLACE TABLE `project.monitoring.daily_query_costs`
PARTITION BY DATE(job_date)
AS
SELECT
  DATE(creation_time) as job_date,
  user_email,
  COUNT(*) as query_count,
  SUM(total_bytes_processed) / POW(10, 12) as total_tb,
  SUM(total_bytes_processed) / POW(10, 12) * 6.25 as estimated_cost_usd
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE DATE(creation_time) = CURRENT_DATE()
  AND job_type = 'QUERY'
GROUP BY 1, 2
```

**3. Implement cost attribution**
```sql
-- Use labels to track costs by team/project
CREATE TABLE `project.dataset.analytics`
OPTIONS(
  labels=[("team", "data_science"), ("cost_center", "research")]
)
AS SELECT * FROM source_data
```

**4. Regular cost reviews**
- Weekly: Review top queries and users
- Monthly: Analyze trends and set next month's budget
- Quarterly: Evaluate on-demand vs flat-rate pricing

### Quick Cost Wins

**Checklist for immediate savings:**
- [ ] Add partition filters to all queries on partitioned tables
- [ ] Replace SELECT * with specific columns
- [ ] Enable require_partition_filter on large tables
- [ ] Create materialized views for frequently run aggregations
- [ ] Set partition_expiration_days on event tables
- [ ] Use APPROX_COUNT_DISTINCT instead of COUNT(DISTINCT)
- [ ] Cluster tables that have large partitions (>1GB)
- [ ] Review INFORMATION_SCHEMA.JOBS for expensive queries
- [ ] Set up billing alerts and cost dashboards
- [ ] Archive data older than 1 year to Cloud Storage

---

## Additional Resources

### Documentation
- [dbt Documentation](https://docs.getdbt.com/)
- [SQLMesh Documentation](https://sqlmesh.readthedocs.io/)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)

### Tools
- `dbt debug` - Validate dbt configuration
- `dbt compile` - See compiled SQL before running
- `sqlmesh plan --dry-run` - Preview migration changes
- `bq query --dry_run` - Estimate query cost

### Monitoring Queries

**dbt run statistics**
```sql
-- Check model run times
SELECT
  name,
  schema,
  status,
  execution_time,
  rows_affected
FROM analytics.dbt_run_results
ORDER BY execution_time DESC
LIMIT 10
```

**BigQuery slot usage**
```sql
-- Monitor slot utilization (for flat-rate)
SELECT
  TIMESTAMP_TRUNC(period_start, HOUR) as hour,
  AVG(total_slot_ms) / (1000 * 60) as avg_slots_used
FROM `region-us`.INFORMATION_SCHEMA.JOBS_TIMELINE_BY_PROJECT
WHERE DATE(period_start) = CURRENT_DATE()
GROUP BY 1
ORDER BY 1
```

---

## Quick Reference

### dbt Commands
```bash
dbt run                          # Run all models
dbt run --select model_name      # Run specific model
dbt run --select tag:daily       # Run tagged models
dbt test                         # Run all tests
dbt docs generate                # Generate documentation
dbt deps                         # Install packages
```

### SQLMesh Commands
```bash
sqlmesh plan dev                 # Plan dev environment
sqlmesh run dev                  # Run dev environment
sqlmesh test                     # Run all tests
sqlmesh audit                    # Run all audits
sqlmesh ui                       # Launch web UI
```

### BigQuery CLI
```bash
bq query --use_legacy_sql=false 'SELECT ...'
bq show project:dataset.table
bq ls -j -a -n 1000              # List recent jobs
bq mk --table project:dataset.table schema.json
```

---

**Last Updated:** 2026-01-12
**Maintained By:** decentclaude data engineering team
