# BigQuery MCP Server Setup Guide

## Overview

The BigQuery MCP server enables Claude Code to directly query, analyze, and explore BigQuery datasets through a comprehensive set of tools. This integration provides powerful data analytics capabilities without leaving your development environment.

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Cloud Project with BigQuery API enabled
- Appropriate IAM permissions for BigQuery access

### Install the MCP Server

```bash
# Install via pip
pip install mcp-server-bigquery

# Or install from source
git clone https://github.com/anaisbetts/mcp-servers
cd mcp-servers/src/bigquery
pip install -e .
```

## Authentication Setup

### Option 1: Application Default Credentials (Recommended for Development)

```bash
# Install Google Cloud SDK
brew install google-cloud-sdk  # macOS
# or download from https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth application-default login

# Set default project
gcloud config set project YOUR_PROJECT_ID
```

### Option 2: Service Account (Recommended for Production)

1. **Create a Service Account**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Navigate to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Name it (e.g., `claude-bigquery-access`)
   - Grant required roles:
     - `BigQuery Data Viewer` (read access)
     - `BigQuery Job User` (run queries)
     - `BigQuery Metadata Viewer` (view metadata)

2. **Generate Key**:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Choose JSON format
   - Save the file securely (e.g., `~/.config/gcloud/bigquery-sa-key.json`)

3. **Set Environment Variable**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/bigquery-sa-key.json"
   ```

   Add to your shell profile (`~/.zshrc` or `~/.bashrc`):
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/gcloud/bigquery-sa-key.json"
   ```

## Configuration

### Claude Code Settings

Add to your `settings.json`:

```json
{
  "mcpServers": {
    "bigquery": {
      "command": "python",
      "args": ["-m", "mcp_server_bigquery"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/Users/yourname/.config/gcloud/bigquery-sa-key.json",
        "GOOGLE_CLOUD_PROJECT": "your-project-id"
      }
    }
  }
}
```

For ADC (no service account file):

```json
{
  "mcpServers": {
    "bigquery": {
      "command": "python",
      "args": ["-m", "mcp_server_bigquery"],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "your-project-id"
      }
    }
  }
}
```

### Verify Installation

Restart Claude Code and verify the server is connected:

```bash
# In Claude Code, ask:
"List all BigQuery datasets available"
```

## Available Tools

### Discovery and Schema Exploration

#### `list_datasets`
List all datasets in the current project.

```python
# No parameters required
# Returns: Comma-separated list of dataset IDs
```

**Example**:
```
Show me all available BigQuery datasets
```

#### `list_tables`
List all tables in a specified dataset.

```python
# Parameters:
# - dataset_id: Fully-qualified dataset ID (project.dataset)

# Returns: Comma-separated list of table names
```

**Example**:
```
List all tables in my-project.analytics_prod dataset
```

#### `get_table_schema`
Get the schema definition of a table.

```python
# Parameters:
# - table_id: Fully-qualified table ID (project.dataset.table)

# Returns: Schema with field names and types
```

**Example**:
```
Show me the schema for my-project.analytics_prod.user_events
```

#### `get_table_metadata`
Get comprehensive metadata about a table.

```python
# Parameters:
# - table_id: Fully-qualified table ID

# Returns: Creation time, last modified, row count, partitioning, clustering, storage details
```

**Example**:
```
Get full metadata for my-project.analytics_prod.user_events
```

### Data Exploration and Profiling

#### `get_table_sample`
Retrieve sample rows from a table.

```python
# Parameters:
# - table_id: Fully-qualified table ID
# - limit: Max rows to return (default: 10, max: 1000)

# Returns: Sample rows
```

**Example**:
```
Show me 20 sample rows from my-project.analytics_prod.user_events
```

#### `profile_table`
Run comprehensive profiling on a table.

```python
# Parameters:
# - table_id: Fully-qualified table ID

# Returns: Metadata, column statistics, null checks in single report
```

**Example**:
```
Profile the my-project.analytics_prod.user_events table
```

#### `describe_table_columns`
Get descriptive statistics for all columns (similar to pandas.describe()).

```python
# Parameters:
# - table_id: Fully-qualified table ID

# Returns: Summary statistics for each column
```

**Example**:
```
Describe all columns in my-project.analytics_prod.purchases
```

#### `describe_column`
Get detailed statistics for a single column.

```python
# Parameters:
# - table_id: Fully-qualified table ID
# - column: Column name

# Returns: Min, max, mean, stddev (numeric) or distinct count, most frequent (string)
```

**Example**:
```
Describe the revenue column in my-project.analytics_prod.purchases
```

#### `get_column_distinct_values`
Get distinct values from a column.

```python
# Parameters:
# - table_id: Fully-qualified table ID
# - column: Column name
# - limit: Max distinct values (default: 100)

# Returns: List of distinct values
```

**Example**:
```
Get distinct product categories from my-project.analytics_prod.purchases
```

#### `get_column_histogram`
Generate histogram for numeric column.

```python
# Parameters:
# - table_id: Fully-qualified table ID
# - column: Numeric column name
# - buckets: Number of buckets (default: 10)

# Returns: Bucket ranges and counts
```

**Example**:
```
Create a histogram of purchase amounts with 20 buckets
```

#### `get_frequent_items`
Find most frequent values in a column.

```python
# Parameters:
# - table_id: Fully-qualified table ID
# - column: Column name
# - num_items: Number of top items (default: 10)

# Returns: Most frequent values and their counts
```

**Example**:
```
Show me the top 20 most frequent users
```

### Data Quality and Validation

#### `get_table_null_percentages`
Get null percentage for each column.

```python
# Parameters:
# - table_id: Fully-qualified table ID

# Returns: Column-to-null-percentage mapping
```

**Example**:
```
Check null percentages in my-project.analytics_prod.user_events
```

#### `get_uniqueness_details`
Analyze column uniqueness.

```python
# Parameters:
# - table_id: Fully-qualified table ID
# - column: Column name

# Returns: Total rows, distinct count, uniqueness ratio
```

**Example**:
```
Check if user_id is a unique key in the events table
```

#### `get_correlation_matrix`
Compute pairwise Pearson correlation for numeric columns.

```python
# Parameters:
# - table_id: Fully-qualified table ID
# - columns: List of numeric column names

# Returns: Correlation matrix
```

**Example**:
```
Calculate correlation between revenue, quantity, and discount columns
```

### Time Series Analysis

#### `get_time_series_distribution`
Count records per time period.

```python
# Parameters:
# - table_id: Fully-qualified table ID
# - time_column: Timestamp/date/datetime column
# - freq: Aggregation frequency ('DAY', 'WEEK', 'MONTH', 'YEAR')

# Returns: Period-to-count mapping
```

**Example**:
```
Show daily distribution of events for the last month
```

#### `detect_time_series_anomalies_with_bqml`
Detect anomalies using BigQuery ML.

```python
# Parameters:
# - table_id: Fully-qualified table ID
# - time_column: Timestamp column
# - value_column: Numeric column to analyze
# - confidence: Confidence level (0-1, default: 0.95)

# Returns: Rows with detected anomalies
```

**Example**:
```
Detect anomalies in daily revenue with 99% confidence
```

#### `get_data_freshness`
Check data recency.

```python
# Parameters:
# - table_id: Fully-qualified table ID
# - time_column: Timestamp column

# Returns: Latest timestamp and freshness lag
```

**Example**:
```
Check how fresh the user_events data is
```

### Query Execution

#### `run_query`
Execute SQL query and return results.

```python
# Parameters:
# - sql: SQL query to execute
# - limit: Max rows to return (default: 100, max: 1000)

# Returns: Query results as list of dictionaries
```

**Example**:
```
Run query: SELECT user_id, COUNT(*) as event_count
FROM `my-project.analytics_prod.user_events`
WHERE DATE(timestamp) = CURRENT_DATE()
GROUP BY user_id
ORDER BY event_count DESC
```

#### `validate_sql`
Validate SQL without executing.

```python
# Parameters:
# - sql: SQL query to validate

# Returns: Success message or error details
```

**Example**:
```
Validate this SQL: SELECT * FROM `my-project.analytics_prod.user_events` LIMIT 10
```

#### `estimate_query_cost`
Estimate bytes processed by a query.

```python
# Parameters:
# - sql: SQL query to analyze

# Returns: Estimated bytes that would be processed
```

**Example**:
```
Estimate cost of: SELECT * FROM `my-project.analytics_prod.user_events` WHERE DATE(timestamp) >= '2024-01-01'
```

### Table Management

#### `check_table_exists`
Check if a table exists.

```python
# Parameters:
# - table_id: Fully-qualified table ID

# Returns: Existence status message
```

**Example**:
```
Does my-project.analytics_prod.user_events_staging exist?
```

#### `get_table_row_count`
Get total row count.

```python
# Parameters:
# - table_id: Fully-qualified table ID

# Returns: Row count
```

**Example**:
```
How many rows in my-project.analytics_prod.user_events?
```

#### `get_table_size_bytes`
Get table storage size.

```python
# Parameters:
# - table_id: Fully-qualified table ID

# Returns: Size in bytes
```

**Example**:
```
What's the storage size of my-project.analytics_prod.user_events?
```

### Partitioning and Clustering

#### `get_table_partitioning_details`
Get partitioning configuration.

```python
# Parameters:
# - table_id: Fully-qualified table ID

# Returns: Partitioning field, type, granularity
```

**Example**:
```
Show partitioning details for my-project.analytics_prod.user_events
```

#### `get_latest_partition`
Get the most recent partition value.

```python
# Parameters:
# - table_id: Fully-qualified table ID (must be partitioned)

# Returns: Latest partition value
```

**Example**:
```
What's the latest partition in my-project.analytics_prod.user_events?
```

#### `get_table_clustering_details`
Get clustering configuration.

```python
# Parameters:
# - table_id: Fully-qualified table ID

# Returns: Clustering fields
```

**Example**:
```
Show clustering details for my-project.analytics_prod.user_events
```

### Lineage and Dependencies

#### `get_table_dependencies`
List upstream dependencies (referenced tables for views).

```python
# Parameters:
# - dataset_id: Dataset ID (project.dataset)
# - table_name: View or table name

# Returns: List of referenced tables
```

**Example**:
```
What tables does the user_summary view depend on?
```

#### `get_downstream_dependencies`
Find downstream dependencies (tables/views that reference this table).

```python
# Parameters:
# - table_id: Fully-qualified table ID

# Returns: List of dependent tables/views
```

**Example**:
```
What views or tables depend on my-project.analytics_prod.user_events?
```

#### `get_view_sql`
Get SQL definition of a view.

```python
# Parameters:
# - table_id: Fully-qualified view ID

# Returns: SQL definition
```

**Example**:
```
Show the SQL for my-project.analytics_prod.user_summary view
```

### Schema Discovery

#### `find_tables_with_column`
Search for tables containing a specific column.

```python
# Parameters:
# - column_name: Column name to search for
# - dataset_filter: Optional dataset to search within

# Returns: List of tables containing the column
```

**Example**:
```
Find all tables with a user_id column
```

#### `compare_schemas`
Compare schemas of two tables.

```python
# Parameters:
# - table_id_a: First table ID
# - table_id_b: Second table ID

# Returns: Columns only in A, only in B, and type differences
```

**Example**:
```
Compare schemas between staging and production user_events tables
```

### Operations and Monitoring

#### `get_failed_jobs`
List recent failed BigQuery jobs.

```python
# Parameters:
# - limit: Max jobs to check (default: 10, max: 100)

# Returns: Failed jobs with error messages
```

**Example**:
```
Show me the last 20 failed BigQuery jobs
```

## Best Practices

### Query Optimization

1. **Use Partitioned Tables**: Always filter on partition columns
   ```sql
   -- Good
   SELECT * FROM `project.dataset.events`
   WHERE DATE(timestamp) >= '2024-01-01'

   -- Bad (full table scan)
   SELECT * FROM `project.dataset.events`
   WHERE user_id = 'abc123'
   ```

2. **Leverage Clustering**: Filter on clustered columns for better performance
   ```sql
   -- If table is clustered by user_id
   SELECT * FROM `project.dataset.events`
   WHERE DATE(timestamp) >= '2024-01-01'
     AND user_id IN ('abc123', 'def456')
   ```

3. **Select Only Required Columns**: Avoid `SELECT *`
   ```sql
   -- Good
   SELECT user_id, event_name, timestamp
   FROM `project.dataset.events`

   -- Bad (scans all columns)
   SELECT * FROM `project.dataset.events`
   ```

4. **Use `LIMIT` for Exploration**: When sampling data
   ```sql
   SELECT * FROM `project.dataset.events`
   LIMIT 1000
   ```

5. **Validate Before Running**: Use `validate_sql` and `estimate_query_cost`
   ```
   First validate and estimate cost for this query before running it
   ```

### Cost Management

1. **Check Query Costs First**:
   ```
   Estimate the cost of scanning the entire user_events table
   ```

2. **Use Table Sampling**: For data exploration
   ```
   Get 100 sample rows from user_events instead of running full query
   ```

3. **Monitor Failed Jobs**: Regular checks prevent repeated errors
   ```
   Check for failed jobs in the last hour
   ```

4. **Set Query Limits**: Always use reasonable limits
   ```python
   # In Claude Code requests
   "Run this query with a limit of 100 rows"
   ```

### Security

1. **Use Service Accounts**: Production environments should use service accounts
2. **Principle of Least Privilege**: Grant only necessary BigQuery roles
3. **Rotate Credentials**: Regularly rotate service account keys
4. **Secure Key Storage**: Never commit keys to repositories
   ```bash
   # Add to .gitignore
   *.json
   *-key.json
   .config/gcloud/
   ```

### Data Quality Workflows

1. **Profile New Tables**:
   ```
   Profile the newly created user_events table
   ```

2. **Check Data Freshness**:
   ```
   Check freshness of all event tables
   ```

3. **Validate Data Quality**:
   ```
   Check null percentages and uniqueness for user_id in user_events
   ```

4. **Monitor Anomalies**:
   ```
   Detect anomalies in daily user signup counts
   ```

## Common Workflows

### Exploring a New Dataset

```
1. List all datasets
2. List tables in analytics_prod
3. Get schema for user_events
4. Get 50 sample rows from user_events
5. Profile the user_events table
6. Check null percentages
```

### Investigating Data Quality Issues

```
1. Get table metadata for user_events
2. Check data freshness for the timestamp column
3. Get null percentages for all columns
4. Check uniqueness of user_id column
5. Get frequent items for event_name column
6. Detect anomalies in daily event counts
```

### Analyzing Table Relationships

```
1. Find all tables with user_id column
2. Get downstream dependencies for user_events
3. Get upstream dependencies for user_summary view
4. Get the SQL definition of user_summary view
```

### Query Development

```
1. Validate SQL: SELECT user_id, COUNT(*) FROM `project.dataset.events` GROUP BY user_id
2. Estimate query cost
3. Run query with limit 100
4. Refine query based on results
5. Run final query
```

### Performance Analysis

```
1. Get partitioning details for user_events
2. Get clustering details for user_events
3. Get table size in bytes
4. Estimate cost for full table scan vs partitioned query
```

## Troubleshooting

### Authentication Errors

**Error**: `Could not automatically determine credentials`

**Solution**:
```bash
# Re-authenticate with gcloud
gcloud auth application-default login

# Or verify service account key path
echo $GOOGLE_APPLICATION_CREDENTIALS
ls -l $GOOGLE_APPLICATION_CREDENTIALS
```

**Error**: `Access Denied: Project XXX: User does not have permission`

**Solution**:
- Verify IAM roles are assigned correctly
- Check that the service account has BigQuery Job User role
- Ensure the project ID is correct

### Query Errors

**Error**: `Table not found`

**Solution**:
- Verify table ID format: `project.dataset.table`
- Check table exists: `Does my-project.analytics_prod.user_events exist?`
- List tables in dataset to verify name

**Error**: `Query exceeded resource limits`

**Solution**:
- Use partitioning filters
- Select specific columns instead of `*`
- Add LIMIT clause
- Check query cost before running

### Performance Issues

**Issue**: Queries are slow

**Solution**:
- Check if table is partitioned and use partition filters
- Verify clustering is being utilized
- Use `estimate_query_cost` to check bytes scanned
- Consider materialized views for complex queries

### Connection Issues

**Error**: `MCP server not responding`

**Solution**:
```bash
# Check if Python and package are installed
python -m mcp_server_bigquery --version

# Verify settings.json configuration
# Restart Claude Code

# Check environment variables
env | grep GOOGLE
```

## Advanced Usage

### Custom Queries for Business Intelligence

```sql
-- User engagement metrics
SELECT
  DATE(timestamp) as date,
  COUNT(DISTINCT user_id) as active_users,
  COUNT(*) as total_events,
  COUNT(*) / COUNT(DISTINCT user_id) as avg_events_per_user
FROM `project.analytics_prod.user_events`
WHERE DATE(timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY date
ORDER BY date DESC
```

### Combining Multiple Tools

```
1. First, list all tables in analytics_prod
2. For each table, get row count and size
3. Check data freshness for tables with timestamp columns
4. Profile tables with more than 1M rows
5. Generate a summary report
```

### Automated Data Quality Checks

```
Create a data quality report for user_events:
1. Check null percentages for all columns
2. Verify user_id uniqueness
3. Check data freshness
4. Detect anomalies in daily event counts
5. Validate that all required columns exist
```

## Integration with Development Workflows

### Pre-deployment Validation

Before deploying new BigQuery tables or views:

```
1. Validate SQL for the new view definition
2. Estimate query cost for downstream consumers
3. Compare schema with existing tables
4. Run sample queries to verify results
```

### Debugging Production Issues

When investigating data issues:

```
1. Check failed jobs for errors
2. Get data freshness to verify ETL runs
3. Profile affected tables
4. Compare schemas between environments
5. Run diagnostic queries
```

### Documentation Generation

```
For each table in analytics_prod:
1. Get table metadata
2. Get schema with descriptions
3. Get sample rows
4. Get partitioning and clustering details
5. Generate markdown documentation
```

## Resources

- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax)
- [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices)
- [BigQuery Pricing](https://cloud.google.com/bigquery/pricing)
- [MCP Server BigQuery GitHub](https://github.com/anaisbetts/mcp-servers/tree/main/src/bigquery)
