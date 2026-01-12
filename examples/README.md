# Example SQL Files

This directory contains example SQL files that demonstrate best practices and can be used to test the Claude Code hooks.

## Files

### valid_query.sql
A basic BigQuery query demonstrating:
- Proper SQL formatting
- Window functions
- Date functions
- Filtering and ordering

Use this to test the SQL validation hooks.

### data_quality.sql
A comprehensive data quality check query that:
- Checks for null values
- Detects duplicate records
- Validates date ranges
- Identifies stale data

This demonstrates how to build data quality checks using SQL.

### dbt_model_example.sql
A dbt model showing:
- Model configuration (materialization, partitioning, clustering)
- CTEs for organization
- Source and ref functions
- Business logic transformations
- User lifecycle calculations

Use this with the dbt-compile hook to test dbt integration.

### sqlmesh_model_example.sql
A SQLMesh model demonstrating:
- Model metadata (name, kind, schedule)
- Incremental processing by time range
- Grain specification
- Event aggregation and pivoting
- Running window calculations
- Engagement scoring logic

Use this with the sqlmesh-plan and sqlmesh-test hooks.

## Testing the Hooks

### Test SQL Validation

1. Try writing an invalid SQL file:
```
Create a file called invalid.sql with: SELECT * FORM table
```

The before-write hook should catch the syntax error.

### Test BigQuery Validation

1. Ask Claude to run a query:
```
Run this query: SELECT * FROM dataset.table
```

The before-tool-call hook will validate syntax before execution.

### Test dbt Integration

1. Set up a dbt project
2. Copy dbt_model_example.sql to your models directory
3. Ask Claude:
```
Run the dbt-compile hook
```

### Test SQLMesh Integration

1. Set up a SQLMesh project
2. Copy sqlmesh_model_example.sql to your models directory
3. Ask Claude:
```
Run the sqlmesh-plan hook
```

### Test Data Quality Checks

1. Customize scripts/data_quality.py for your needs
2. Ask Claude:
```
Run the data-quality-check hook
```

## Best Practices Demonstrated

1. **Consistent Formatting**: All SQL uses consistent indentation and casing
2. **CTEs for Clarity**: Complex queries broken into readable steps
3. **Explicit Column Names**: No SELECT * in production queries
4. **Date Partitioning**: Queries limited by date ranges for performance
5. **Quality Checks**: Built-in validation and error detection
6. **Documentation**: Comments explain query purpose and logic

## Extending the Examples

Add your own example files to demonstrate:
- Complex window functions
- Advanced joins
- Nested CTEs
- Performance optimization patterns
- Your organization's SQL style guide
