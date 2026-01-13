---
name: schema-doc-generator
description: Generate comprehensive schema documentation for BigQuery tables including column descriptions, data types, constraints, and markdown documentation
allowed-tools:
  - Read
  - Grep
  - Write
  - mcp__bigquery__get_table_schema
  - mcp__bigquery__get_table_metadata
  - mcp__bigquery__list_tables
  - mcp__bigquery__list_datasets
  - mcp__bigquery__get_table_sample
  - mcp__bigquery__describe_table_columns
  - mcp__bigquery__get_table_partitioning_details
  - mcp__bigquery__get_table_clustering_details
  - mcp__bigquery__get_column_distinct_values
  - mcp__bigquery__get_table_null_percentages
---

# Schema Documentation Generator Skill

Generate comprehensive, human-readable schema documentation for BigQuery tables and datasets. Creates detailed markdown documentation with column descriptions, data types, constraints, sample data, and data quality metrics.

## Workflow

### 1. Discover Schema Structure

- **Target identification**: Specify table, dataset, or entire project
- **Schema retrieval**: Fetch complete schema definitions
- **Metadata collection**: Gather table-level metadata
- **Type analysis**: Identify column types (scalar, nested, repeated)
- **Constraint detection**: Document keys, nullability, modes

### 2. Analyze Data Characteristics

For each column:
- **Data type**: STRING, INT64, FLOAT64, TIMESTAMP, RECORD, etc.
- **Mode**: NULLABLE, REQUIRED, REPEATED
- **Description**: Extract or infer column purpose
- **Sample values**: Show representative data
- **Distinct counts**: Cardinality analysis
- **Null percentages**: Data completeness metrics
- **Value ranges**: Min/max for numeric columns

### 3. Profile Data Quality

- **Completeness**: Null percentages per column
- **Uniqueness**: Distinct value counts
- **Distribution**: Value frequency analysis
- **Nested structures**: Document RECORD and ARRAY types
- **Data patterns**: Common formats (email, phone, UUID)
- **Outliers**: Identify unusual values

### 4. Document Table-Level Details

- **Table metadata**: Size, row count, creation date, last modified
- **Partitioning**: Field, type, and granularity
- **Clustering**: Clustered columns for optimization
- **Schema evolution**: Track schema change history
- **Access patterns**: Common query patterns
- **Performance**: Optimization recommendations

### 5. Generate Documentation

Create structured markdown documentation:

```markdown
# Schema Documentation: [Table Name]

## Table Overview
- **Fully Qualified Name**: project.dataset.table
- **Type**: Table | View | Materialized View
- **Description**: [Business purpose]
- **Rows**: 1.2M
- **Size**: 45 GB
- **Created**: 2025-01-01
- **Last Modified**: 2026-01-12

## Partitioning & Clustering
- **Partitioned By**: event_date (DAY)
- **Clustered By**: user_id, event_type
- **Partition Expiration**: 365 days

## Schema

| Column | Type | Mode | Description | Null % | Distinct | Sample Values |
|--------|------|------|-------------|--------|----------|---------------|
| id | STRING | REQUIRED | Unique identifier | 0% | 1.2M | uuid-v4 |
| user_id | INT64 | NULLABLE | User reference | 2% | 45K | 1001, 1002 |
| event_type | STRING | REQUIRED | Event category | 0% | 12 | click, view |

## Nested Structures
[Document RECORD and ARRAY types with sub-fields]

## Data Quality Summary
- Overall completeness: 95%
- Primary key candidate: id
- Foreign keys: user_id -> users.id

## Usage Patterns
- Common queries: [Examples]
- Performance notes: [Optimization tips]
```

### 6. Create Multi-Level Documentation

- **Single table**: Detailed documentation for one table
- **Dataset catalog**: All tables in a dataset
- **Schema comparison**: Compare schemas across environments
- **Change log**: Track schema evolution over time
- **Data dictionary**: Business glossary with technical mappings

### 7. Add Context and Examples

- **Business context**: What the table represents
- **Source systems**: Where data originates
- **Update frequency**: Refresh schedule
- **Data owners**: Team or person responsible
- **Related tables**: Joins and relationships
- **Example queries**: Common usage patterns
- **Known issues**: Data quality caveats

## Use Cases

### New Team Member Onboarding
```
User: "Generate documentation for all tables in the analytics dataset"

1. List all tables in analytics dataset
2. For each table, retrieve schema and metadata
3. Profile data quality metrics
4. Generate comprehensive markdown docs
5. Create index file linking all table docs
6. Add dataset-level overview
```

### Schema Review
```
User: "Document the schema for events.user_interactions"

1. Fetch complete schema with nested structures
2. Analyze data types and modes
3. Sample data for each column
4. Calculate null percentages and distinct counts
5. Document partitioning and clustering
6. Generate detailed table documentation
```

### API Documentation
```
User: "Create API documentation for our data export tables"

1. List tables in export dataset
2. Generate schema docs with examples
3. Add data type mappings for common languages
4. Document required vs optional fields
5. Provide sample queries
6. Create API reference guide
```

### Schema Migration Planning
```
User: "Compare dev and prod schemas for all tables"

1. Fetch schemas from both environments
2. Identify differences (added/removed/modified columns)
3. Document breaking changes
4. Generate migration checklist
5. Create rollout plan
```

## Integration Points

- **BigQuery API**: Schema and metadata retrieval
- **INFORMATION_SCHEMA**: System metadata queries
- **Git repository**: Version control for documentation
- **Data catalog tools**: Export to Datahub, Amundsen, etc.
- **Documentation sites**: Generate for Docusaurus, MkDocs, etc.
- **CI/CD pipelines**: Auto-generate on schema changes

## Output Formats

### Markdown Documentation
- `TABLE_NAME.md`: Single table documentation
- `DATASET_README.md`: Dataset overview
- `DATA_DICTIONARY.md`: Business glossary
- `SCHEMA_CHANGELOG.md`: Schema evolution history

### Structured Data
- `schema.json`: Machine-readable schema
- `metadata.json`: Table metadata
- `data_quality.json`: Quality metrics

### Visual Diagrams
- Entity-relationship diagrams
- Schema visualization
- Type hierarchy diagrams

## Documentation Templates

### Table Documentation Template
```markdown
# [Table Name]

## Purpose
[Business description of what this table contains]

## Table Information
- **Dataset**: [dataset_name]
- **Type**: [Table/View/Materialized View]
- **Rows**: [count]
- **Size**: [bytes]
- **Updated**: [timestamp]

## Optimization
- **Partitioned**: [Yes/No - details]
- **Clustered**: [Yes/No - details]
- **Expiration**: [days or none]

## Schema Definition

### Columns

| Name | Type | Mode | Description | Null % | Example |
|------|------|------|-------------|--------|---------|
| ... | ... | ... | ... | ... | ... |

### Nested Fields
[For RECORD types, document sub-structure]

## Data Quality

| Metric | Value |
|--------|-------|
| Completeness | 98% |
| Primary Key | id |
| Unique Columns | email, user_id |
| Nullable Columns | 5 of 20 |

## Sample Data
```json
{
  "id": "uuid-123",
  "user_id": 1001,
  "event_type": "click"
}
```

## Related Tables
- **users**: Joined on user_id
- **products**: Joined on product_id

## Common Queries
```sql
-- Example: Get daily event counts
SELECT
  DATE(event_timestamp) as date,
  COUNT(*) as events
FROM `project.dataset.table`
WHERE event_date >= CURRENT_DATE() - 7
GROUP BY 1
ORDER BY 1 DESC
```

## Notes
- [Important caveats, known issues, or special considerations]
```

### Dataset Index Template
```markdown
# Dataset: [dataset_name]

## Overview
[Dataset description and purpose]

## Tables

| Table | Type | Rows | Description |
|-------|------|------|-------------|
| table1 | Table | 1.2M | ... |
| table2 | View | - | ... |

## Conventions
- Partitioning strategy: [description]
- Naming conventions: [pattern]
- Clustering guidelines: [rules]

## Maintenance
- Refresh schedule: [timing]
- Data retention: [policy]
- Owner: [team/person]
```

## Best Practices

### Schema Documentation
- Document business purpose, not just technical details
- Include example values for enum-like columns
- Explain nested structures clearly
- Note relationships to other tables
- Highlight performance considerations

### Data Type Documentation
- Map BigQuery types to common language types
- Explain RECORD and ARRAY structures
- Document precision for numeric types
- Note timezone handling for timestamps
- Clarify JSON and geographic types

### Quality Metrics
- Always include null percentages
- Show distinct counts for low-cardinality fields
- Identify potential primary keys
- Flag data quality issues
- Document validation rules

### Maintenance
- Regenerate docs when schemas change
- Version control documentation
- Use consistent formatting
- Link related documentation
- Keep examples up to date

## Advanced Features

### Schema Evolution Tracking
- Compare schema versions
- Document breaking changes
- Track column additions/removals
- Monitor type changes
- Alert on incompatible changes

### Smart Description Inference
- Infer purpose from column names
- Suggest descriptions based on data patterns
- Detect common field types (email, phone, etc.)
- Map to business glossary terms
- Use AI to generate descriptions

### Data Profiling Integration
- Embed data quality metrics
- Show value distributions
- Highlight outliers
- Detect anomalies
- Recommend constraints

### Multi-Environment Support
- Compare dev/staging/prod schemas
- Document environment-specific differences
- Track migration status
- Validate consistency

## Collaboration

Works well with:
- **data-lineage-doc skill**: For dependency documentation
- **sql-reviewer agent**: For query pattern analysis
- **data-quality-tester agent**: For data profiling
- **document skill**: For general documentation tasks

## Example Output

```markdown
# events.user_interactions

## Purpose
Tracks all user interaction events on the website and mobile app. Used for analytics,
personalization, and ML feature generation.

## Table Information
- **Fully Qualified Name**: production.events.user_interactions
- **Type**: Table (Partitioned)
- **Description**: User interaction events including clicks, views, and custom events
- **Rows**: 45,234,891
- **Size**: 12.3 GB
- **Created**: 2025-06-15 10:30:00 UTC
- **Last Modified**: 2026-01-12 08:15:00 UTC

## Optimization Details
- **Partitioned By**: event_date (DAY) - 90 day retention
- **Clustered By**: user_id, event_type
- **Partition Count**: 90 active partitions
- **Benefits**: 10x faster queries when filtering by date and user_id

## Schema Definition

### Top-Level Columns

| Column | Type | Mode | Description | Null % | Distinct | Example Values |
|--------|------|------|-------------|--------|----------|----------------|
| event_id | STRING | REQUIRED | Unique event identifier (UUIDv4) | 0% | 45.2M | "a1b2c3d4-..." |
| user_id | INT64 | NULLABLE | Reference to users table | 2.1% | 1.2M | 1001, 1002 |
| session_id | STRING | NULLABLE | User session identifier | 0.5% | 8.5M | "sess_abc123" |
| event_type | STRING | REQUIRED | Type of event | 0% | 12 | click, view, purchase |
| event_timestamp | TIMESTAMP | REQUIRED | Event occurrence time (UTC) | 0% | 45M | 2026-01-12 08:00:00 |
| event_date | DATE | REQUIRED | Partition key (derived from timestamp) | 0% | 90 | 2026-01-12 |
| page_url | STRING | NULLABLE | URL where event occurred | 3.2% | 5.6K | "/products/123" |
| referrer | STRING | NULLABLE | Referring URL | 45% | 2.3K | "google.com" |
| device_type | STRING | NULLABLE | Device category | 0.8% | 4 | mobile, desktop |
| properties | RECORD | NULLABLE | Event-specific properties | 0% | - | (nested) |

### Nested Structure: properties

| Field Path | Type | Mode | Description | Null % | Example |
|------------|------|------|-------------|--------|---------|
| properties.product_id | STRING | NULLABLE | For product events | 78% | "prod_123" |
| properties.value | FLOAT64 | NULLABLE | Event value (USD) | 85% | 29.99 |
| properties.category | STRING | NULLABLE | Event category | 60% | "electronics" |
| properties.metadata | JSON | NULLABLE | Additional JSON data | 90% | {"key":"value"} |

## Data Quality Summary

| Metric | Value | Status |
|--------|-------|--------|
| Overall Completeness | 94.3% | ✓ Good |
| Primary Key Candidate | event_id (100% unique) | ✓ Confirmed |
| Foreign Key | user_id -> users.id | ✓ Valid |
| Partition Coverage | Last 90 days | ✓ Good |
| Null Check | 6 nullable columns with <50% nulls | ✓ Good |
| Outliers | 0.01% events with future timestamps | ⚠ Review |

## Sample Data

```json
{
  "event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": 1001,
  "session_id": "sess_abc123xyz",
  "event_type": "purchase",
  "event_timestamp": "2026-01-12T08:15:30Z",
  "event_date": "2026-01-12",
  "page_url": "/checkout/complete",
  "referrer": "https://google.com/search",
  "device_type": "mobile",
  "properties": {
    "product_id": "prod_789",
    "value": 49.99,
    "category": "books",
    "metadata": {"payment_method": "credit_card"}
  }
}
```

## Related Tables

- **users** (`production.core.users`)
  - Join: `user_id` = `users.id`
  - Relationship: Many interactions per user

- **products** (`production.core.products`)
  - Join: `properties.product_id` = `products.id`
  - Relationship: Many events per product

- **sessions** (`production.analytics.sessions`)
  - Join: `session_id` = `sessions.id`
  - Relationship: Many events per session

## Common Queries

### Daily Event Counts by Type
```sql
SELECT
  event_date,
  event_type,
  COUNT(*) as event_count,
  COUNT(DISTINCT user_id) as unique_users
FROM `production.events.user_interactions`
WHERE event_date >= CURRENT_DATE() - 7
GROUP BY 1, 2
ORDER BY 1 DESC, 3 DESC
```

### User Journey Analysis
```sql
SELECT
  user_id,
  session_id,
  ARRAY_AGG(
    STRUCT(event_type, event_timestamp, page_url)
    ORDER BY event_timestamp
  ) as journey
FROM `production.events.user_interactions`
WHERE event_date = CURRENT_DATE()
  AND user_id IS NOT NULL
GROUP BY 1, 2
```

### Purchase Conversion Funnel
```sql
SELECT
  event_date,
  COUNTIF(event_type = 'view') as views,
  COUNTIF(event_type = 'add_to_cart') as cart_adds,
  COUNTIF(event_type = 'purchase') as purchases,
  SAFE_DIVIDE(
    COUNTIF(event_type = 'purchase'),
    COUNTIF(event_type = 'view')
  ) * 100 as conversion_rate
FROM `production.events.user_interactions`
WHERE event_date >= CURRENT_DATE() - 30
GROUP BY 1
ORDER BY 1 DESC
```

## Performance Notes

- **Partition Pruning**: Always filter by `event_date` for best performance
- **Clustering Benefit**: Filter by `user_id` or `event_type` after date for 10x speedup
- **Cost Optimization**: Use `SELECT *` sparingly; select only needed columns
- **Nested Fields**: Accessing `properties.*` fields is slightly more expensive

## Known Issues & Caveats

- **Null user_id**: ~2% of events are from anonymous users (before authentication)
- **Future timestamps**: Small number (<0.01%) of events have client clock skew
- **Referrer accuracy**: 45% null referrers (direct traffic, privacy settings)
- **Properties variance**: Structure of `properties` varies by `event_type`

## Maintenance

- **Owner**: Data Engineering Team (@data-team)
- **Refresh**: Streaming inserts (real-time)
- **Retention**: 90 days in BigQuery, 2 years in cold storage
- **Monitoring**: Alert on >5% null user_id or >1 hour data delay
- **Updates**: Schema changes require migration plan and 2-week notice

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-01-12 | Added properties.metadata JSON field | @eng-team |
| 2025-11-20 | Changed clustering from (event_type, user_id) to (user_id, event_type) | @data-team |
| 2025-09-10 | Extended retention from 30 to 90 days | @data-team |
| 2025-06-15 | Initial table creation | @data-team |
```
