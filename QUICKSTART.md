# Quick Start Guide

Get up and running with DecentClaude Data Workflows in 5 minutes.

## What You'll Get

Automated validation and quality checks for your data workflows:
- SQL syntax validation before queries run
- BigQuery cost estimation
- dbt model compilation and testing
- Data quality checks
- Schema comparison tools
- Table lineage tracking

## 1. Run the Setup Wizard (2 minutes)

The fastest way to get started:

```bash
./bin/setup-wizard.sh
```

The wizard will:
1. Check your Python installation
2. Install required dependencies
3. Optionally install dbt, SQLMesh, and sqlfluff
4. Configure dbt if needed
5. Test your BigQuery connection
6. Add CLI utilities to your PATH

## 2. Verify Installation (30 seconds)

Test that everything works:

```bash
# Test SQL parsing
python3 -c "import sqlparse; print('✓ sqlparse works')"

# Test BigQuery client
python3 -c "from google.cloud import bigquery; print('✓ BigQuery client works')"

# Test CLI utility
./bin/data-utils/bq-query-cost --help
```

## 3. Try Your First Workflow (2 minutes)

### Example 1: Validate SQL Before Running

Just ask Claude to run a query:

```
Run this query: SELECT * FROM dataset.table WHERE date > '2024-01-01'
```

The BigQuery validation hook automatically checks syntax before execution.

### Example 2: Compare Table Schemas

```bash
./bin/data-utils/bq-schema-diff project.dataset.table_v1 project.dataset.table_v2
```

See exactly what changed between two tables.

### Example 3: Estimate Query Cost

Before running an expensive query:

```bash
./bin/data-utils/bq-query-cost "SELECT * FROM bigquery-public-data.usa_names.usa_1910_current"
```

Know the cost before you spend.

### Example 4: Check Table Lineage

Understand dependencies before making changes:

```bash
./bin/data-utils/bq-lineage project.dataset.critical_table
```

See what depends on this table (impact analysis).

## 4. Common Use Cases

### Automated SQL Validation

Claude Code hooks automatically validate SQL in two scenarios:

1. **Before running queries**: The `before-tool-call` hook validates BigQuery queries
2. **Before writing SQL files**: The `before-write` hook checks syntax

No configuration needed - just write SQL naturally!

### dbt Workflows

If you installed dbt:

```
Run the dbt-compile hook
```

This compiles all your dbt models and shows any errors.

```
Run the dbt-test hook
```

Runs your dbt tests to verify data quality.

### Pre-commit Validation

Before committing code:

```
Run the pre-commit-data hook
```

This validates all SQL files and compiles dbt models.

### Data Quality Checks

Run custom quality checks:

```
Run the data-quality-check hook
```

Customize checks in `scripts/data_quality.py`.

## 5. Real-World Workflows

### Scenario: Adding a New Table

You're adding a new analytics table. Here's the workflow:

1. **Design the schema**
   ```
   Show me partition and clustering options for a table with 10M daily events
   ```

2. **Check cost before creating**
   ```bash
   ./bin/data-utils/bq-query-cost --file=create_table.sql
   ```

3. **Create dbt model**
   ```
   Create a dbt model for this table with partitioning by date and clustering by user_id
   ```

4. **Compile and test**
   ```
   Run the dbt-compile hook
   ```

5. **Pre-commit validation**
   ```
   Run the pre-commit-data hook
   ```

### Scenario: Investigating a Schema Change

Production table schema changed unexpectedly:

1. **Compare schemas**
   ```bash
   ./bin/data-utils/bq-schema-diff project.dataset.prod_table project.dataset.staging_table
   ```

2. **Check what depends on it**
   ```bash
   ./bin/data-utils/bq-lineage project.dataset.prod_table --direction=downstream
   ```

3. **Find impact**
   - See all downstream tables that might break
   - Identify queries that reference changed columns

### Scenario: Optimizing Query Costs

Your BigQuery bill is too high:

1. **Find expensive queries**
   ```bash
   # Check each query's cost
   ./bin/data-utils/bq-query-cost --file=expensive_query.sql
   ```

2. **Check partitioning**
   ```bash
   ./bin/data-utils/bq-partition-info project.dataset.large_table
   ```

3. **Optimize and verify**
   ```bash
   # Compare before/after costs
   ./bin/data-utils/bq-query-cost --file=original.sql
   ./bin/data-utils/bq-query-cost --file=optimized.sql
   ```

## Troubleshooting

### "Module 'sqlparse' not found"

```bash
pip3 install sqlparse
```

### "No module named 'google.cloud'"

```bash
pip3 install google-cloud-bigquery
```

### "Permission denied" when running CLI utilities

```bash
chmod +x ./bin/data-utils/*
```

### dbt profile not found

Create `~/.dbt/profiles.yml`:

```yaml
default:
  target: dev
  outputs:
    dev:
      type: bigquery
      project: your-project-id
      dataset: your_dataset
      threads: 4
      method: oauth
```

### BigQuery authentication errors

```bash
gcloud auth login
gcloud auth application-default login
```

## Next Steps

### Learn More About Hooks

Read the comprehensive hooks documentation:

```bash
cat docs/worktrees/HOOKS.md
```

Available hooks:
- `dbt-compile`: Compile dbt models
- `dbt-test`: Run dbt tests
- `sqlfluff-lint`: Lint SQL files
- `data-quality-check`: Run custom quality checks
- `pre-commit-data`: Comprehensive pre-commit validation
- `sqlmesh-plan`: Run SQLMesh plan
- `sqlmesh-test`: Run SQLMesh tests

### Explore Playbooks

Learn common data engineering workflows:

```bash
cat playbooks.md
```

Covers:
- New table migration
- Schema evolution
- Backfill patterns
- Incident response

### Read Best Practices

Data engineering patterns and anti-patterns:

```bash
cat data-engineering-patterns.md
```

Topics:
- Table design patterns
- Partitioning strategies
- Incremental processing
- Testing approaches

### View Examples

See example SQL files:

```bash
ls examples/sql/
cat examples/README.md
```

## Getting Help

### CLI Utilities Help

Each utility has built-in help:

```bash
./bin/data-utils/bq-schema-diff --help
./bin/data-utils/bq-query-cost --help
./bin/data-utils/bq-partition-info --help
./bin/data-utils/bq-lineage --help
```

### Common Questions

**Q: Do the hooks slow down my workflow?**
A: No. Hooks run asynchronously and typically complete in under 1 second.

**Q: Can I disable specific hooks?**
A: Yes. Edit `.claude/settings.json` to remove or comment out hooks.

**Q: How do I add custom validation?**
A: Edit `scripts/data_quality.py` to add your own checks.

**Q: What if I don't use BigQuery?**
A: Most hooks work with any SQL. BigQuery-specific features (like cost estimation) require the BigQuery client.

**Q: Can I use this with Snowflake/Redshift?**
A: SQL validation works with any database. Database-specific features require the appropriate client library.

## Success Checklist

After completing this guide, you should be able to:

- [ ] Run the setup wizard successfully
- [ ] Validate SQL queries automatically
- [ ] Use CLI utilities for BigQuery operations
- [ ] Estimate query costs before running
- [ ] Compare table schemas
- [ ] Check table dependencies
- [ ] Run dbt hooks (if using dbt)
- [ ] Execute pre-commit validation

## What's Next?

You're ready to use DecentClaude Data Workflows! Here are some ways to level up:

1. **Customize validation rules**: Edit `scripts/data_quality.py`
2. **Add custom hooks**: Modify `.claude/settings.json`
3. **Create your own playbooks**: Add to `playbooks.md`
4. **Share patterns with your team**: Document in `data-engineering-patterns.md`

Happy data engineering! 🚀
