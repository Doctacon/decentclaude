---
name: sql-optimizer
description: SQL query analysis and optimization workflow including execution plan analysis, performance improvement suggestions, anti-pattern identification, index recommendations, and cost impact estimation
allowed-tools:
  - Read
  - Grep
  - Bash
  - Write
  - mcp__bigquery__validate_sql
  - mcp__bigquery__estimate_query_cost
  - mcp__bigquery__get_table_schema
  - mcp__bigquery__get_table_metadata
  - mcp__bigquery__get_table_partitioning_details
  - mcp__bigquery__get_table_clustering_details
  - mcp__bigquery__run_query
  - mcp__bigquery__describe_column
  - mcp__bigquery__get_table_sample
  - mcp__bigquery__compare_schemas
  - mcp__bigquery__get_correlation_matrix
  - mcp__bigquery__profile_table
---

# SQL Optimizer Skill

Comprehensive SQL query optimization workflow that analyzes query execution plans, suggests performance improvements, identifies anti-patterns, recommends indexes/partitioning/clustering, and estimates cost impact of optimizations.

## Workflow

### 1. Analyze Query Structure

**Parse and validate SQL**:

```bash
# Validate syntax
# Use mcp__bigquery__validate_sql to check SQL is valid

# Identify all referenced tables
grep -E "FROM|JOIN" query.sql

# Extract WHERE conditions
grep -E "WHERE|AND|OR" query.sql

# Check for subqueries
grep -E "SELECT.*FROM.*SELECT" query.sql
```

**Categorize query type**:
- SELECT query (read-only)
- Aggregation query (GROUP BY)
- Join query (multiple tables)
- Window function query
- Subquery/CTE query

### 2. Gather Table Metadata

**For each table in the query**:

```bash
# Get table schema
# Use mcp__bigquery__get_table_schema

# Get table metadata (size, row count, creation date)
# Use mcp__bigquery__get_table_metadata

# Check partitioning configuration
# Use mcp__bigquery__get_table_partitioning_details

# Check clustering configuration
# Use mcp__bigquery__get_table_clustering_details

# Get sample data to understand data patterns
# Use mcp__bigquery__get_table_sample
```

**Analyze table characteristics**:
- Table size (bytes)
- Row count
- Partition scheme (daily, monthly, ingestion time)
- Clustering columns
- Column data types and distributions

### 3. Estimate Query Cost

**Calculate baseline cost**:

```bash
# Estimate bytes processed
# Use mcp__bigquery__estimate_query_cost

# Document baseline
echo "Baseline: 10.5 GB processed = ~$0.05 per query"
```

**Identify cost drivers**:
- Full table scans
- Wide SELECT * projections
- Missing partition filters
- Cartesian products (CROSS JOINs)
- Expensive UDFs or functions

### 4. Identify Anti-Patterns

**Common SQL anti-patterns to detect**:

#### A. SELECT * Abuse

```sql
-- BAD: Reads all columns (expensive)
SELECT * FROM large_table
WHERE user_id = 123

-- GOOD: Select only needed columns
SELECT user_id, email, created_at FROM large_table
WHERE user_id = 123
```

#### B. Missing Partition Filters

```sql
-- BAD: Scans all partitions (years of data)
SELECT * FROM events.user_activity
WHERE user_id = 123

-- GOOD: Filter to recent partitions
SELECT * FROM events.user_activity
WHERE event_date >= CURRENT_DATE() - 30
  AND user_id = 123
```

#### C. Correlated Subqueries

```sql
-- BAD: Runs subquery for every row (slow)
SELECT
  user_id,
  (SELECT COUNT(*) FROM orders WHERE orders.user_id = users.id) as order_count
FROM users

-- GOOD: Use JOIN with aggregation
SELECT
  u.user_id,
  COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.user_id
```

#### D. N+1 Query Problem

```sql
-- BAD: Multiple queries in application code
SELECT * FROM users WHERE id = 1;  -- Query 1
SELECT * FROM orders WHERE user_id = 1;  -- Query 2
SELECT * FROM orders WHERE user_id = 2;  -- Query 3
-- ... repeated N times

-- GOOD: Single query with JOIN
SELECT u.*, o.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.id IN (1, 2, 3, ...)
```

#### E. Cartesian Products

```sql
-- BAD: Accidental CROSS JOIN (huge result set)
SELECT *
FROM table1, table2
WHERE table1.status = 'active'

-- GOOD: Explicit join condition
SELECT *
FROM table1 t1
INNER JOIN table2 t2 ON t1.id = t2.table1_id
WHERE t1.status = 'active'
```

#### F. Inefficient Joins

```sql
-- BAD: Large table first (expensive)
SELECT *
FROM large_table_1b_rows l
JOIN small_table_1k_rows s ON l.id = s.id

-- GOOD: Small table first (broadcast join optimization)
SELECT *
FROM small_table_1k_rows s
JOIN large_table_1b_rows l ON s.id = l.id
```

#### G. ORDER BY Without LIMIT

```sql
-- BAD: Sorts entire result set
SELECT * FROM events
ORDER BY created_at DESC

-- GOOD: Limit results
SELECT * FROM events
ORDER BY created_at DESC
LIMIT 100
```

#### H. Lack of Safe Operations

```sql
-- BAD: Division by zero error
SELECT revenue / order_count FROM stats

-- GOOD: Safe division
SELECT SAFE_DIVIDE(revenue, order_count) FROM stats
```

### 5. Analyze Execution Plan

**Partition scanning**:
- Are partition filters present?
- How many partitions are scanned?
- Can we reduce partition scan with tighter date ranges?

**Clustering effectiveness**:
- Are clustered columns used in WHERE clauses?
- Are clustered columns used in JOINs?
- Is data skew present on clustered columns?

**Join strategy**:
- Join order (smaller table first?)
- Join types (INNER, LEFT, CROSS)
- Join conditions (equality vs inequality)
- Broadcast vs shuffle joins

**Aggregation strategy**:
- GROUP BY cardinality
- Use of approximate functions (APPROX_COUNT_DISTINCT)
- Pre-aggregation opportunities

### 6. Recommend Optimizations

**Priority framework**:

1. **Critical (99% cost reduction)**: Add missing partition filters
2. **High (50-90% reduction)**: Replace SELECT *, optimize joins
3. **Medium (10-50% reduction)**: Convert subqueries, add clustering hints
4. **Low (<10% reduction)**: Use APPROX_ functions, minor tweaks

**Optimization examples**:

#### Partition Filter Addition

```sql
-- Before: 100 GB scanned
SELECT user_id, COUNT(*) as events
FROM `project.events.user_activity`
WHERE user_type = 'premium'
GROUP BY user_id

-- After: 1 GB scanned (99% reduction)
SELECT user_id, COUNT(*) as events
FROM `project.events.user_activity`
WHERE event_date >= CURRENT_DATE() - 7  -- Add partition filter
  AND user_type = 'premium'
GROUP BY user_id
```

#### Column Projection Optimization

```sql
-- Before: 50 columns, 10 GB scanned
SELECT * FROM wide_table
WHERE category = 'electronics'

-- After: 5 columns, 1 GB scanned (90% reduction)
SELECT product_id, name, price, stock, category
FROM wide_table
WHERE category = 'electronics'
```

#### Subquery to Join Conversion

```sql
-- Before: Correlated subquery (30 seconds)
SELECT
  p.product_id,
  p.name,
  (SELECT AVG(rating) FROM reviews r WHERE r.product_id = p.id) as avg_rating
FROM products p

-- After: LEFT JOIN with aggregation (3 seconds, 10x faster)
SELECT
  p.product_id,
  p.name,
  AVG(r.rating) as avg_rating
FROM products p
LEFT JOIN reviews r ON p.id = r.product_id
GROUP BY p.product_id, p.name
```

#### Use Approximate Functions

```sql
-- Before: Exact count (expensive on large datasets)
SELECT COUNT(DISTINCT user_id) FROM large_events_table

-- After: Approximate count (95% accuracy, 10x faster)
SELECT APPROX_COUNT_DISTINCT(user_id) FROM large_events_table
```

#### Materialized View Recommendation

```sql
-- If query runs frequently (>10x per day) and results don't need real-time freshness

-- Original expensive query
SELECT
  date,
  product_category,
  SUM(revenue) as total_revenue,
  COUNT(*) as order_count
FROM fact_sales
GROUP BY date, product_category

-- Recommendation: Create materialized view
CREATE MATERIALIZED VIEW sales_summary AS
SELECT
  date,
  product_category,
  SUM(revenue) as total_revenue,
  COUNT(*) as order_count
FROM fact_sales
GROUP BY date, product_category

-- Then query the materialized view (instant results)
SELECT * FROM sales_summary
WHERE date >= CURRENT_DATE() - 30
```

### 7. Estimate Impact

**For each optimization**:

```markdown
## Optimization Impact Summary

### Before Optimization
- **Bytes Processed**: 10.5 GB
- **Estimated Cost**: $0.0525 per query
- **Estimated Runtime**: ~30 seconds
- **Partitions Scanned**: 365 (full year)

### After Optimization
- **Bytes Processed**: 0.5 GB
- **Estimated Cost**: $0.0025 per query
- **Estimated Runtime**: ~3 seconds
- **Partitions Scanned**: 7 (last week only)

### Savings
- **Cost Reduction**: 95% ($0.05 saved per query)
- **Performance Improvement**: 10x faster
- **Annual Savings** (1000 queries/day): $18,250
```

### 8. Validate Optimizations

**Test optimized query**:

```bash
# Validate syntax
# Use mcp__bigquery__validate_sql

# Estimate new cost
# Use mcp__bigquery__estimate_query_cost

# Run on sample data to verify correctness
# Use mcp__bigquery__run_query with LIMIT 100

# Compare results with original query
# Ensure same row count and values
```

**Regression testing**:
- Verify query returns same results
- Check edge cases (null values, empty results)
- Test with different date ranges
- Validate aggregation accuracy

### 9. Document Optimizations

**Create optimization report**:

```markdown
# SQL Optimization Report: [Query Name]

Date: 2026-01-12
Analyst: SQL Optimizer Skill

## Original Query
```sql
[Original SQL]
```

**Issues Identified:**
1. Missing partition filter on event_date (Critical)
2. SELECT * on 50-column table (High)
3. Correlated subquery for user counts (High)
4. No use of approximate functions (Medium)

## Optimized Query
```sql
[Optimized SQL with inline comments explaining changes]
```

## Performance Comparison

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Bytes Processed | 10.5 GB | 0.5 GB | 95% reduction |
| Estimated Cost | $0.0525 | $0.0025 | 95% savings |
| Runtime (est.) | 30 sec | 3 sec | 10x faster |
| Partitions Scanned | 365 | 7 | 98% reduction |

## Optimizations Applied

### 1. Added Partition Filter (Critical)
**Impact**: 90% cost reduction
```sql
-- Added this filter
WHERE event_date >= CURRENT_DATE() - 7
```

### 2. Column Projection (High)
**Impact**: 50% cost reduction on remaining data
```sql
-- Changed from SELECT * to specific columns
SELECT user_id, event_type, created_at
```

### 3. Converted Correlated Subquery (High)
**Impact**: 10x performance improvement
```sql
-- Changed from correlated subquery to JOIN
LEFT JOIN user_stats s ON u.id = s.user_id
```

### 4. Used Approximate Functions (Medium)
**Impact**: 5x faster aggregation
```sql
-- Changed from COUNT(DISTINCT ...) to APPROX_COUNT_DISTINCT(...)
SELECT APPROX_COUNT_DISTINCT(user_id) as unique_users
```

## Index/Schema Recommendations

1. **Partition event_date column**: Already exists ✓
2. **Cluster by user_id**: Recommended for user-based queries
3. **Consider materialized view**: If query runs >10x daily

## Next Steps

- [ ] Review optimized query with data team
- [ ] Run A/B test with sample traffic
- [ ] Update query in production
- [ ] Monitor performance metrics
- [ ] Schedule quarterly query review
```

## Best Practices

### Optimization Principles

- **Measure first**: Always profile before optimizing
- **Focus on biggest wins**: Partition filters and column selection first
- **One change at a time**: Isolate impact of each optimization
- **Validate correctness**: Ensure results match original query
- **Document everything**: Explain why changes improve performance

### When to Optimize

**Optimize when**:
- Query runs frequently (>10x per day)
- Query processes >1 GB of data
- Query takes >5 seconds
- Query costs >$0.01 per run
- Users complain about slow dashboards

**Don't optimize when**:
- Query runs rarely (<1x per week)
- Query already fast (<1 second)
- Optimization adds significant complexity
- Approximate results not acceptable

### BigQuery-Specific Best Practices

**Partitioning**:
- Always filter partitioned tables by partition column
- Use partition decorators for specific partitions
- Prune partitions to minimum needed range

**Clustering**:
- Use clustered columns in WHERE, JOIN, GROUP BY
- Order matters: most selective columns first
- Max 4 clustering columns

**Functions**:
- Use native functions over UDFs
- Prefer APPROX_* for large aggregations
- Avoid expensive REGEXP on large text columns

**Joins**:
- Put smaller table first (broadcast join)
- Use exact data type matches in join keys
- Avoid inequality joins when possible

**Cost Control**:
- Use LIMIT for exploratory queries
- Sample large tables with TABLESAMPLE
- Set maximum bytes billed with query config
- Use BI Engine for repeated queries

## Common Pitfalls

- Optimizing prematurely (measure first!)
- Sacrificing correctness for performance
- Over-using approximate functions where precision matters
- Not considering data growth patterns
- Ignoring seasonal query patterns
- Missing monitoring after optimization

## Tools

### Analysis Tools
- **BigQuery Console**: Built-in query execution plan
- **Query validator**: Syntax checking
- **Cost estimator**: Bytes processed calculation
- **Table explorer**: Schema and metadata viewer

### Optimization Tools
- **Query optimizer**: Automatic recommendations
- **Execution statistics**: Runtime metrics
- **Slot usage analyzer**: Resource consumption
- **BI Engine**: Caching layer

### Monitoring Tools
- **Query history**: Past execution stats
- **Audit logs**: Usage patterns
- **Cloud Monitoring**: Alerting on slow queries
- **Cost reports**: BigQuery spend tracking

## Collaboration

Works well with:
- **sql-reviewer agent**: For comprehensive code review
- **schema-analyzer agent**: For schema design optimization
- **data-quality-tester agent**: For result validation
- **data-lineage-doc skill**: For understanding query dependencies
- **performance-expert agent**: For deep performance analysis
