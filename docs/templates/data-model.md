# [Model Name] Data Model Documentation

**Type**: [Staging / Intermediate / Mart / Dimension / Fact]
**Owner**: [Team/Individual]
**Last Updated**: [YYYY-MM-DD]
**Status**: [Development / Production / Deprecated]

## Overview

[Brief description of what this model represents and its purpose in the data warehouse]

### Business Context

[Explain the business need this model addresses and who the primary stakeholders are]

## Model Details

### Location

**Framework**: [dbt / SQLMesh]
**Path**: `[path/to/model.sql]`
**Database**: `[project.dataset.table]`
**Materialization**: [table / view / incremental / ephemeral]

### Dependencies

#### Upstream Models
```
[parent_model_1]  # Description
[parent_model_2]  # Description
```

#### Downstream Models
```
[child_model_1]   # Description
[child_model_2]   # Description
```

## Schema

### Primary Key
- **Column(s)**: `[column_name(s)]`
- **Uniqueness**: [Enforced / Tested / None]
- **Test Coverage**: [Yes / No]

### Columns

| Column Name | Data Type | Nullable | Description | Business Rules |
|-------------|-----------|----------|-------------|----------------|
| `[column_1]` | STRING | NO | [Description] | [Rules/Constraints] |
| `[column_2]` | TIMESTAMP | YES | [Description] | [Rules/Constraints] |
| `[column_3]` | INTEGER | NO | [Description] | [Rules/Constraints] |

### Grain

[Describe the grain/granularity: "One row per...", e.g., "One row per user per day"]

## Configuration

### dbt Configuration

```yaml
# models/schema.yml
version: 2

models:
  - name: [model_name]
    description: |
      [Description]

    config:
      materialized: [table/view/incremental]
      partition_by:
        field: [date_column]
        data_type: date
        granularity: day
      cluster_by: [column1, column2]
      tags: [tag1, tag2]

    columns:
      - name: [column_name]
        description: [Description]
        tests:
          - not_null
          - unique
```

### SQLMesh Configuration

```sql
-- models/[model_name].sql

MODEL (
  name [schema].[model_name],
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column [date_column]
  ),
  grain ([grain_columns]),
  partitioned_by ([date_column], day),
  clustered_by ([cluster_columns]),
  tags [tag1, tag2]
);

SELECT
  [columns]
FROM [source]
WHERE [date_column] BETWEEN @start_date AND @end_date;
```

## Data Quality

### Tests

**dbt Tests:**
```yaml
# models/schema.yml
tests:
  - dbt_utils.unique_combination_of_columns:
      combination_of_columns: [col1, col2]
  - dbt_utils.recency:
      datepart: day
      field: created_at
      interval: 1
```

**Custom Data Quality Checks:**
```sql
-- tests/[model_name]_quality.sql
-- [Description of quality check]
SELECT
  COUNT(*) as failures
FROM {{ ref('[model_name]') }}
WHERE [quality_condition]
HAVING COUNT(*) > 0;
```

### Monitoring

- **Freshness**: [Expected update cadence, e.g., "Updated daily at 3am UTC"]
- **Volume**: [Expected row count range, e.g., "~10M rows"]
- **Alerts**: [Alerting setup if applicable]

## Transformations

### Business Logic

[Describe key transformations and business logic applied in this model]

### Example Transformations

```sql
-- Example transformation pattern
CASE
  WHEN [condition] THEN [value]
  ELSE [default]
END AS [derived_column]
```

## Usage Examples

### Query Patterns

```sql
-- Common query pattern 1
SELECT
  [columns]
FROM `[project.dataset.model_name]`
WHERE [conditions]
GROUP BY [grouping]
ORDER BY [ordering];
```

### Claude Code Integration

**Ask Claude to validate this model:**
```bash
# Validate model compiles
dbt compile --select [model_name]

# Run model with test data
dbt run --select [model_name] --target dev

# Run data quality tests
dbt test --select [model_name]
```

## Performance

### Optimization Strategy

- **Partitioning**: [Strategy and rationale]
- **Clustering**: [Strategy and rationale]
- **Incremental Logic**: [If applicable]

### Query Cost

**Estimated bytes processed**: [Size estimate]
**Typical query cost**: [Cost estimate]

### Performance Notes

[Any specific performance considerations or optimization tips]

## Maintenance

### Refresh Schedule

- **Frequency**: [hourly / daily / weekly]
- **Trigger**: [cron / event / manual]
- **Dependencies**: [What must complete before this runs]

### Breaking Changes History

| Date | Change | Migration Path |
|------|--------|----------------|
| [YYYY-MM-DD] | [Description] | [How to migrate] |

### Known Issues

[Document any known limitations or issues with this model]

## References

### Related Documentation
- [Link to business documentation]
- [Link to source system docs]
- [Link to related models]

### Contact
- **Primary Owner**: [Name/Team]
- **Slack Channel**: [#channel]
- **On-Call**: [Rotation/Contact]

## Claude Code Patterns

### Model Development Workflow

```bash
# 1. Create new model from template
cp docs/templates/data-model.md docs/models/[model_name].md

# 2. Ask Claude to generate initial SQL
# "Create a dbt model for [description] based on [sources]"

# 3. Validate and test
dbt compile --select [model_name]
dbt run --select [model_name] --target dev
dbt test --select [model_name]

# 4. Document schema
dbt docs generate
dbt docs serve
```

### Common Claude Prompts

**"Review this model for best practices"**
- Checks naming conventions
- Validates materialization strategy
- Reviews test coverage
- Suggests optimizations

**"Add data quality tests for [model_name]"**
- Generates appropriate tests based on schema
- Adds recency/volume checks
- Creates custom quality validations

**"Optimize [model_name] for cost"**
- Analyzes partition/cluster strategy
- Suggests incremental patterns
- Reviews query efficiency

## Notes

[Any additional notes, context, or considerations]
