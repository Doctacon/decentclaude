## Data Model Changes

<!-- What data model(s) are being added or modified? -->

## Business Context

<!-- What business need does this model serve? -->

## Model Details

### Model Type
- [ ] Source/staging model
- [ ] Intermediate model
- [ ] Mart/final model
- [ ] Seed data
- [ ] Snapshot

### Models Modified/Added
<!-- List the models with their purpose -->
- `model_name`: Purpose

### Schema Changes
<!-- Describe any schema changes -->
- **New columns**:
- **Modified columns**:
- **Removed columns**:
- **New tables/views**:

## SQL/dbt/SQLMesh Details

### Tool
- [ ] dbt
- [ ] SQLMesh
- [ ] Raw SQL/BigQuery

### Configuration
<!-- Describe materialization, partitioning, clustering -->
- **Materialization**: table/view/incremental/snapshot
- **Partitioning**: Field and strategy
- **Clustering**: Fields
- **Incremental strategy**: (if applicable)

## Data Quality

- [ ] Data quality tests added
- [ ] Schema validation tests added
- [ ] Freshness checks configured
- [ ] Null checks on critical fields
- [ ] Unique key constraints validated
- [ ] Referential integrity tested

### Test Coverage
<!-- List the tests added -->
-
-

## Validation

- [ ] SQL syntax validated
- [ ] BigQuery dry run passed
- [ ] dbt/SQLMesh compilation successful
- [ ] Sample queries tested
- [ ] Cost estimate reviewed (for BigQuery)

### Query Performance
<!-- Estimated query cost and performance -->
- **Estimated bytes processed**:
- **Execution time** (if tested):
- **Optimization applied**:

## Impact Assessment

- [ ] Downstream dependencies identified and notified
- [ ] Breaking changes: Yes/No
  - If yes, migration plan:
- [ ] Historical data handling: Describe approach
- [ ] Backfill required: Yes/No
  - If yes, backfill plan:

### Downstream Impact
<!-- List downstream models, dashboards, or pipelines affected -->
-
-

## Documentation

- [ ] Data model documentation created/updated (use `data-model.md` template)
- [ ] Column definitions documented
- [ ] Business logic documented
- [ ] Example queries provided
- [ ] Lineage diagram updated (if applicable)
- [ ] CLAUDE.md updated with new patterns

## Deployment Plan

### Rollout Strategy
<!-- How will this be deployed? -->
- [ ] Can be deployed incrementally
- [ ] Requires full refresh
- [ ] Requires coordinated deployment

### Rollback Plan
<!-- How can this be rolled back? -->
-

## Checklist

- [ ] Follows data engineering best practices (see `data-engineering-patterns.md`)
- [ ] SQL follows project conventions (see `playbooks.md`)
- [ ] All validation hooks pass
- [ ] No secrets or sensitive data committed
- [ ] Reviewed own code before requesting review
- [ ] Cost optimization applied
- [ ] Proper use of partitioning/clustering

## Related Work

<!-- Link to related beads, models, or discussions -->
- Related bead:
- Related models:
- Design doc:

## Additional Context

<!-- Schema diagrams, example outputs, or other context -->
