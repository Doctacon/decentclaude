# BigQuery Data Utilities - Quick Reference

This directory previously contained example command scripts that have been **moved to their canonical location** in `bin/data-utils/`. All BigQuery analysis and data quality utilities are now maintained in a single location.

## Canonical Utilities Location

All BigQuery utilities are located in:

```
/Users/crlough/gt/decentclaude/mayor/rig/bin/data-utils/
```

## Command Redirects

The following commands have been consolidated:

| Old Command (examples/commands/) | New Canonical Utility (bin/data-utils/) |
|----------------------------------|------------------------------------------|
| `query-explain` | `bq-explain` |
| `schema-compare` | `bq-schema-diff` |
| `data-profile` | `bq-profile` |

## Available Utilities

The `bin/data-utils/` directory contains comprehensive BigQuery utilities written in Python:

### Query Analysis
- **bq-explain** - Analyze and visualize BigQuery query execution plans
- **bq-optimize** - Suggest query optimizations
- **bq-query-cost** - Estimate query costs
- **bq-explore** - Interactive table exploration

### Schema & Structure
- **bq-schema-diff** - Compare schemas of two BigQuery tables
- **bq-lineage** - Track data lineage and dependencies
- **bq-partition-info** - Analyze table partitioning

### Data Quality & Profiling
- **bq-profile** - Generate comprehensive data quality profiles
- **bq-table-compare** - Compare data between tables
- **bq-benchmark** - Performance benchmarking

### Cost Management
- **bq-cost-report** - Generate cost analysis reports

### AI-Powered Tools
- **ai-query** - Generate SQL queries from natural language
- **ai-docs** - Generate documentation from schemas
- **ai-review** - Review queries for best practices
- **ai-generate** - Generate test data and schemas

### dbt Integration
- **dbt-deps** - Manage dbt dependencies
- **dbt-docs-serve** - Serve dbt documentation
- **dbt-model-search** - Search dbt models
- **dbt-test-gen** - Generate dbt tests

### SQLMesh Integration
- **sqlmesh-diff** - Compare SQLMesh environments
- **sqlmesh-migrate** - Migration utilities
- **sqlmesh-validate** - Validate SQLMesh models
- **sqlmesh-visualize** - Visualize SQLMesh lineage

## Usage Examples

### Query Explanation (previously query-explain)

```bash
# Old way
query-explain "SELECT * FROM project.dataset.table"

# New way
bq-explain "SELECT * FROM project.dataset.table"

# Additional capabilities
bq-explain --file=query.sql
bq-explain --job-id=abc123-def456-ghi789
bq-explain --format=json
```

### Schema Comparison (previously schema-compare)

```bash
# Old way
schema-compare project.dev.users project.prod.users

# New way
bq-schema-diff project.dev.users project.prod.users

# Additional capabilities
bq-schema-diff table_a table_b --format=json
```

### Data Profiling (previously data-profile)

```bash
# Old way
data-profile project.dataset.users

# New way
bq-profile project.dataset.users

# Additional capabilities
bq-profile project.dataset.users --format=json
bq-profile project.dataset.users --format=markdown
bq-profile project.dataset.users --detect-anomalies
bq-profile project.dataset.users --sample-size=20
```

## Installation

### 1. Add to PATH

Add the bin/data-utils directory to your PATH:

```bash
# Add to ~/.zshrc or ~/.bashrc
echo 'export PATH="/Users/crlough/gt/decentclaude/mayor/rig/bin/data-utils:$PATH"' >> ~/.zshrc

# Reload shell configuration
source ~/.zshrc
```

### 2. Verify Installation

```bash
# Test that commands are accessible
which bq-explain
which bq-schema-diff
which bq-profile

# View help for each command
bq-explain --help
bq-schema-diff --help
bq-profile --help
```

## Requirements

### Python Dependencies

The utilities require Python 3.7+ and these packages:

```bash
pip install google-cloud-bigquery
```

### Google Cloud Authentication

Set up Google Cloud credentials:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

### Required Permissions

Your service account needs these BigQuery permissions:
- `bigquery.jobs.create` - For running queries and dry runs
- `bigquery.tables.get` - For reading table metadata
- `bigquery.tables.getData` - For profiling and sampling
- `bigquery.datasets.get` - For listing datasets

## Why the Consolidation?

The utilities in `bin/data-utils/` offer several advantages over the previous bash scripts:

1. **Better Implementation** - Written in Python with proper error handling
2. **More Features** - Additional output formats (JSON, Markdown, HTML)
3. **Consistent Interface** - All utilities follow the same CLI patterns
4. **Active Maintenance** - Single location for updates and improvements
5. **Better Integration** - Direct Google Cloud API integration vs MCP abstraction layer
6. **Enhanced Capabilities** - AI-powered tools, dbt/SQLMesh integration

## Migration Guide

If you have scripts or workflows using the old commands:

1. **Find usages**: Search your codebase for `query-explain`, `schema-compare`, `data-profile`
2. **Update references**: Replace with `bq-explain`, `bq-schema-diff`, `bq-profile`
3. **Update PATH**: Point to `bin/data-utils/` instead of `examples/commands/`
4. **Review options**: Check help text as new utilities may have additional features
5. **Test**: Verify functionality with test queries/tables

## Complete Utility Reference

For detailed documentation on all available utilities, see:

```
/Users/crlough/gt/decentclaude/mayor/rig/bin/data-utils/
```

Each utility includes built-in help accessible via `--help` flag.

## Support

For issues or questions:
- Check utility help: `<utility-name> --help`
- Review BigQuery documentation: https://cloud.google.com/bigquery/docs
- File issues in the decentclaude repository

---

**Last Updated**: 2026-01-13
**Migration Status**: Complete - All duplicate commands removed
