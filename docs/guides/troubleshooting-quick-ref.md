# BigQuery Troubleshooting Quick Reference

A one-page cheat sheet for the most common BigQuery issues and their solutions.

---

## SQL Errors

| Error | Likely Cause | Quick Fix |
|-------|-------------|-----------|
| Syntax error | Invalid SQL | `sqlfluff lint file.sql` |
| Permission denied | Wrong account or missing IAM | `gcloud auth login` |
| Table not found | Typo or wrong project | `bq ls PROJECT:DATASET` |
| Query timeout | Too much data | Add WHERE filters, LIMIT |
| Resources exceeded | Complex query | Break into smaller queries |

---

## Performance Issues

| Symptom | Diagnosis | Solution |
|---------|-----------|----------|
| Slow query | Full table scan | Add WHERE, use partitions |
| High bytes scanned | SELECT * or no filters | Select specific columns, add filters |
| Long queue time | Slot contention | Schedule off-peak, use reservations |

**Optimization Checklist**:
- [ ] Use WHERE to filter data
- [ ] Select only needed columns
- [ ] Use partitioned/clustered tables
- [ ] Add LIMIT for testing
- [ ] Check execution plan with dry run

---

## Cost Problems

| Issue | Check | Action |
|-------|-------|--------|
| Unexpected charges | Query history | Review INFORMATION_SCHEMA.JOBS |
| Quota exceeded | Current usage | Request increase or optimize |
| Need cost estimate | Before running | `bq query --dry_run` |

**Cost Reduction**:
1. Avoid SELECT *
2. Use partition filters
3. Cache results when possible
4. Use table samples for dev/test

---

## Data Quality

| Problem | Detection | Resolution |
|---------|-----------|------------|
| Unexpected NULLs | `get_table_null_percentages` | Add COALESCE, check source |
| Duplicate records | `get_uniqueness_details` | Use DISTINCT, QUALIFY ROW_NUMBER() |
| Schema mismatch | `compare_schemas` | Check migration history |
| Stale data | `get_data_freshness` | Review pipeline logs |

---

## Emergency Commands

```bash
# Cancel a running query
bq cancel JOB_ID

# Find expensive queries today
bq query "SELECT * FROM \`region-us\`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE DATE(creation_time) = CURRENT_DATE()
ORDER BY total_bytes_processed DESC LIMIT 10"

# Check recent failures
python -c "from mayor.rig.mcp import get_failed_jobs; print(get_failed_jobs())"

# Verify table exists
bq show PROJECT:DATASET.TABLE

# Check your quota
gcloud compute project-info describe --project=PROJECT_ID
```

---

## Interactive Troubleshooting

Need more help? Use the interactive troubleshooting tool:

```bash
# Start interactive assistant
python /Users/crlough/gt/decentclaude/mayor/rig/kb/troubleshooting_tree.py

# Jump to specific category
python troubleshooting_tree.py --category sql
python troubleshooting_tree.py --category performance
python troubleshooting_tree.py --category cost
python troubleshooting_tree.py --category quality
python troubleshooting_tree.py --category tool
```

---

## Key MCP Tools

| Task | MCP Tool |
|------|----------|
| Find table by column | `find_tables_with_column('column_name')` |
| Check NULL percentages | `get_table_null_percentages('table_id')` |
| Find duplicates | `get_uniqueness_details('table_id', 'column')` |
| Compare schemas | `compare_schemas('table_a', 'table_b')` |
| Check data freshness | `get_data_freshness('table_id', 'time_col')` |
| Estimate query cost | `estimate_query_cost('SELECT ...')` |
| Profile table | `profile_table('table_id')` |
| Get table metadata | `get_table_metadata('table_id')` |

---

## Common Query Patterns

### Check for NULLs
```sql
SELECT
  COUNT(*) as total,
  COUNT(column_name) as non_null,
  100.0 * COUNT(column_name) / COUNT(*) as pct_non_null
FROM `project.dataset.table`;
```

### Find Duplicates
```sql
SELECT id, COUNT(*) as count
FROM `project.dataset.table`
GROUP BY id
HAVING COUNT(*) > 1
ORDER BY count DESC;
```

### Deduplicate
```sql
CREATE OR REPLACE TABLE project.dataset.table AS
SELECT * EXCEPT(rn)
FROM (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) as rn
  FROM project.dataset.table
)
WHERE rn = 1;
```

### Check Data Freshness
```sql
SELECT
  MAX(timestamp_col) as latest,
  TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(timestamp_col), HOUR) as hours_old
FROM `project.dataset.table`;
```

### Estimate Cost
```bash
bq query --dry_run < query.sql
```

---

## Documentation Links

- [Full Troubleshooting Tree](./troubleshooting-tree.md) - Interactive decision tree
- [SQL Style Guide](./sql-style-guide.md) - Best practices
- [Performance Optimization](./performance-optimization.md) - Speed up queries
- [Cost Management](./cost-management.md) - Reduce expenses
- [MCP Tools Reference](../reference/mcp-tools.md) - All available tools

---

## When to Escalate

Contact your data engineering team if:
- Issue persists after following troubleshooting steps
- Need quota increase
- Require schema changes
- Experiencing production outages
- Need access to restricted datasets

---

**Pro Tip**: Always test queries with LIMIT 10 first, then increase gradually!
