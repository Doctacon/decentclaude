# [Dashboard/Report Name] BI Dependencies Documentation

**BI Tool**: [Looker / Tableau / Power BI / Other]
**Owner**: [Team/Individual]
**Last Updated**: [YYYY-MM-DD]
**Status**: [Development / Production / Deprecated]
**Refresh Schedule**: [Real-time / Hourly / Daily / Weekly / On-demand]

## Overview

[Brief description of the dashboard/report purpose and key metrics displayed]

### Business Context

[Explain the business need this dashboard addresses, who uses it, and how it drives decisions]

### Key Stakeholders

- **Primary Users**: [Team/Role]
- **Report Owner**: [Name/Team]
- **Data Owner**: [Name/Team]
- **Update Frequency**: [How often users check this dashboard]

## Dashboard Details

### Location

**Dashboard URL**: [Full URL to the dashboard]
**Workspace/Folder**: [Looker folder path / Tableau project path]
**Dashboard ID**: [Internal ID if applicable]

### Access Control

**Visibility**: [Public / Private / Role-based]
**User Groups**: [List of groups with access]
**Row-level Security**: [Yes / No - describe if yes]

## Data Dependencies

### BigQuery Tables

List all BigQuery tables used by this dashboard:

| Table Name | Type | Refresh Pattern | Critical | Purpose |
|------------|------|-----------------|----------|---------|
| `project.dataset.fct_orders` | Fact | Incremental daily | Yes | Order metrics |
| `project.dataset.dim_customers` | Dimension | Full refresh weekly | No | Customer attributes |
| `project.dataset.dim_products` | Dimension | Full refresh daily | No | Product catalog |

### Data Freshness Requirements

| Table | Max Acceptable Lag | Current SLA | Alert Threshold |
|-------|-------------------|-------------|-----------------|
| `fct_orders` | 1 hour | 15 minutes | 2 hours |
| `dim_customers` | 24 hours | 8 hours | 48 hours |

### Upstream Data Sources

```
[source_system_1]
  └─ [staging_table_1]
     └─ [intermediate_model_1]
        └─ [mart_table_1] → Dashboard

[source_system_2]
  └─ [staging_table_2]
     └─ [mart_table_2] → Dashboard
```

## Dashboard Queries

### Main Metrics

Document the key metrics and their calculation logic:

#### 1. [Metric Name]

**Description**: [What this metric measures]
**Calculation**:
```sql
SELECT
    SUM(revenue) as total_revenue,
    COUNT(DISTINCT order_id) as order_count
FROM `project.dataset.fct_orders`
WHERE order_date >= CURRENT_DATE() - 30
```

**Tables Used**:
- `project.dataset.fct_orders`

**Filters Applied**:
- Date range: Last 30 days
- Status: Completed orders only

**Expected Performance**: [Query runtime, data volume]

#### 2. [Metric Name]

[Repeat for each major metric]

### Custom Fields/Calculations

List any custom fields created in the BI tool:

| Field Name | Formula | Description |
|------------|---------|-------------|
| `customer_ltv` | `SUM(revenue) / COUNT(DISTINCT customer_id)` | Average lifetime value |
| `conversion_rate` | `COUNT(orders) / COUNT(sessions) * 100` | Order conversion rate |

## Performance Considerations

### Query Performance

**Typical Query Runtime**: [X seconds/minutes]
**Data Volume**: [X GB scanned per refresh]
**Optimization Applied**:
- [Partitioning strategy]
- [Clustering fields]
- [Materialized views used]

### Optimization History

| Date | Issue | Solution | Impact |
|------|-------|----------|--------|
| 2024-01-15 | Slow page load (30s) | Added clustering on date | Reduced to 3s |
| 2024-02-01 | High cost queries | Implemented aggregate table | 80% cost reduction |

## Change Management

### Recent Changes

| Date | Change | Implemented By | Impact |
|------|--------|----------------|--------|
| [YYYY-MM-DD] | Added customer segment filter | [Name] | New feature |
| [YYYY-MM-DD] | Migrated to new fact table | [Name] | Breaking change |

### Upcoming Changes

| Planned Date | Change | Owner | Status |
|--------------|--------|-------|--------|
| [YYYY-MM-DD] | Add real-time refresh | [Name] | In progress |

## Incident Response

### Known Issues

| Issue | Workaround | Permanent Fix | Priority |
|-------|------------|---------------|----------|
| [Description] | [Temporary solution] | [Planned fix] | [P1/P2/P3] |

### Monitoring & Alerts

**Monitoring Dashboard**: [Link to monitoring]
**Alert Channels**: [Slack channel / Email list]
**On-call Contact**: [Name/Team]

**Key Metrics Monitored**:
- Data freshness (alert if > 2 hours old)
- Query failure rate (alert if > 1%)
- Dashboard load time (alert if > 10s)

### Incident Playbook

When this dashboard breaks:

1. **Check data freshness**: Run `bi-usage-tracker project.dataset --days=1`
2. **Verify upstream tables**: Check dbt/SQLMesh run logs
3. **Test queries manually**: Run queries in BigQuery console
4. **Check for schema changes**: Run `bq-schema-diff` on source tables
5. **Contact**: [Escalation path]

## Testing & Validation

### Data Quality Checks

| Check | Frequency | Threshold | Action on Failure |
|-------|-----------|-----------|-------------------|
| Row count validation | Daily | ±5% variance | Alert data team |
| Null check on key fields | Daily | 0 nulls | Block refresh |
| Metric comparison vs. source | Weekly | ±2% variance | Investigate |

### Validation Queries

```sql
-- Validate total order count matches source
SELECT
    COUNT(*) as dashboard_count,
    (SELECT COUNT(*) FROM source_system.orders) as source_count,
    ABS(COUNT(*) - (SELECT COUNT(*) FROM source_system.orders)) as difference
FROM `project.dataset.fct_orders`
HAVING difference > 100;
```

## Documentation & Training

### User Documentation

**User Guide**: [Link to user documentation]
**Training Materials**: [Link to training videos/slides]
**FAQ**: [Link to FAQ document]

### Technical Documentation

**Data Model**: [Link to data model documentation]
**Looker/Tableau Config**: [Link to LookML files or Tableau workbook]
**API Documentation**: [If dashboard has API access]

## Costs & Usage

### Usage Statistics

**Active Users (30 days)**: [Number]
**Total Views (30 days)**: [Number]
**Peak Usage Times**: [Time windows]
**Most Viewed Page**: [Page/chart name]

### Cost Analysis

**Monthly Query Cost**: [$X (X GB scanned)]
**Storage Cost**: [$X (X GB stored)]
**BI Tool License Cost**: [$X/month]

**Cost Optimization Opportunities**:
- [List potential optimizations]

## Maintenance Schedule

| Task | Frequency | Owner | Last Completed |
|------|-----------|-------|----------------|
| Review metrics accuracy | Monthly | [Name] | [Date] |
| Update documentation | Quarterly | [Name] | [Date] |
| Performance audit | Quarterly | [Name] | [Date] |
| User access review | Quarterly | [Name] | [Date] |

## Migration & Deprecation

**Original Creation Date**: [YYYY-MM-DD]
**Expected Lifespan**: [X months/years / Until replacement]
**Deprecation Plan**: [Description if applicable]
**Replacement Dashboard**: [Link if applicable]

## Related Resources

- **Data Lineage**: [Link to lineage documentation]
- **Related Dashboards**: [Links to related dashboards]
- **Source Code**: [Link to LookML/Tableau repository]
- **Runbooks**: [Links to operational runbooks]

## Notes

[Any additional context, quirks, or important information that doesn't fit elsewhere]

---

**Generated with**: `bi-metadata-sync project.dataset --format=json`
**Last Validated**: [YYYY-MM-DD]
