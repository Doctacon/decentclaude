# DecentClaude Data Workflows

Claude Code hooks for world-class data engineering workflows with automated validation, quality checks, and testing.

## Overview

This repository provides a comprehensive set of Claude Code hooks designed specifically for data engineering workflows. These hooks automate validation and quality checks for SQL, dbt, SQLMesh, and other data tools.

## Features

### CLI Data Utilities

Powerful command-line utilities for common data platform operations:

**BigQuery:**
- **bq-schema-diff**: Compare schemas of two tables to identify differences
- **bq-query-cost**: Estimate query costs before execution
- **bq-partition-info**: Analyze partitioning configuration and partition sizes
- **bq-lineage**: Explore table dependencies (upstream and downstream)

**Databricks/Spark:**
- **db-optimize**: Optimize Delta tables with optional Z-ORDER clustering
- **db-vacuum**: Clean up old files and reclaim storage
- **db-stats**: Display comprehensive table statistics and metadata
- **db-lineage**: Explore Unity Catalog table lineage

See [Data Utilities](#data-utilities) for detailed usage.

### Automated Validation Hooks

- **SQL Syntax Validation**: Automatically validate SQL before execution or file writes
- **BigQuery Query Validation**: Check SQL syntax before running BigQuery queries
- **SQL File Linting**: Enforce SQL style guidelines with sqlfluff
- **Secret Detection**: Prevent hardcoded credentials in SQL files

### Data Tool Integration

- **dbt**: Compile models and run tests automatically
- **SQLMesh**: Plan and test SQLMesh transformations
- **Custom Data Quality**: Extensible Python-based quality checks

### Pre-commit Workflow

- Comprehensive pre-commit validation
- SQL syntax checking
- dbt model compilation
- Data quality checks

## Quick Start

### 1. Install Dependencies

```bash
# Core dependencies
pip install sqlparse

# Optional tools
pip install sqlfluff dbt-core dbt-bigquery sqlmesh
```

### 2. Configure dbt (if using)

Set up your dbt profile at `~/.dbt/profiles.yml`:

```yaml
default:
  target: dev
  outputs:
    dev:
      type: bigquery
      project: your-project
      dataset: your_dataset
      threads: 4
      method: service-account
      keyfile: /path/to/keyfile.json
```

### 3. Start Using Hooks

The hooks are already configured in `.claude/settings.json` and will automatically:
- Validate SQL queries before execution
- Check SQL files before writing
- Detect dbt commands and log workflow actions

## Available Hooks

### Automatic Hooks

These run automatically during Claude Code operations:

1. **user-prompt-submit**: Detect SQL queries in prompts
2. **before-tool-call**: Validate BigQuery queries before execution
3. **before-write**: Validate SQL files before writing

### Custom Hooks

Trigger these manually by asking Claude:

```
Run the [hook-name] hook
```

- `dbt-compile`: Compile dbt models
- `dbt-test`: Run dbt tests
- `sqlfluff-lint`: Lint SQL files
- `data-quality-check`: Run custom quality checks
- `pre-commit-data`: Comprehensive pre-commit validation
- `sqlmesh-plan`: Run SQLMesh plan
- `sqlmesh-test`: Run SQLMesh tests

## Documentation

- [Hooks Documentation](.claude/HOOKS.md) - Detailed hook descriptions and usage
- [Data Quality Script](scripts/data_quality.py) - Extensible quality check framework

## Example Usage

### Validate SQL Before Running

```
Run this query: SELECT * FROM dataset.table WHERE date > '2024-01-01'
```

The BigQuery validation hook will automatically check syntax before execution.

### Run Pre-commit Checks

```
Run the pre-commit-data hook
```

This validates all SQL files and compiles dbt models.

### Custom Data Quality Checks

```
Run the data-quality-check hook
```

Executes the Python script at `scripts/data_quality.py` with customizable checks.

## Data Utilities

### bq-schema-diff

Compare schemas of two BigQuery tables to identify differences.

**Usage:**
```bash
bin/data-utils/bq-schema-diff <table_a> <table_b> [options]
```

**Options:**
- `--format=<format>` - Output format: text, json (default: text)

**Examples:**
```bash
# Compare two tables
bin/data-utils/bq-schema-diff project.dataset.table_v1 project.dataset.table_v2

# Output as JSON
bin/data-utils/bq-schema-diff project.dataset.staging.users project.dataset.prod.users --format=json
```

**Output includes:**
- Fields only in table A
- Fields only in table B
- Fields with type changes
- Summary of differences

### bq-query-cost

Estimate BigQuery query costs before execution using dry run.

**Usage:**
```bash
bin/data-utils/bq-query-cost <query> [options]
bin/data-utils/bq-query-cost --file=<sql_file> [options]
```

**Options:**
- `--file=<path>` - Read query from SQL file
- `--format=<format>` - Output format: text, json (default: text)

**Examples:**
```bash
# Estimate from query string
bin/data-utils/bq-query-cost "SELECT * FROM project.dataset.table WHERE date = '2024-01-01'"

# Estimate from file
bin/data-utils/bq-query-cost --file=query.sql

# JSON output
bin/data-utils/bq-query-cost --file=query.sql --format=json
```

**Output includes:**
- Bytes processed (formatted)
- GB and TB processed
- Estimated cost in USD
- Cost category (Very Low, Low, Moderate, High, Very High)
- Pricing model information

### bq-partition-info

Analyze BigQuery table partitioning configuration and partition details.

**Usage:**
```bash
bin/data-utils/bq-partition-info <table_id> [options]
```

**Options:**
- `--top=<n>` - Show top N partitions by size (default: 10)
- `--format=<format>` - Output format: text, json (default: text)

**Examples:**
```bash
# Analyze partitioning
bin/data-utils/bq-partition-info project.dataset.events

# Show top 20 partitions
bin/data-utils/bq-partition-info project.dataset.events --top=20

# JSON output
bin/data-utils/bq-partition-info project.dataset.events --format=json
```

**Output includes:**
- Partitioning type (TIME or RANGE)
- Partition field
- Expiration settings
- Partition filter requirement
- Clustering fields
- Top N partitions by size with row counts and bytes

### bq-lineage

Explore BigQuery table lineage to understand dependencies.

**Usage:**
```bash
bin/data-utils/bq-lineage <table_id> [options]
```

**Options:**
- `--direction=<dir>` - Lineage direction: upstream, downstream, both (default: both)
- `--depth=<n>` - Maximum depth to traverse (default: 1)
- `--format=<format>` - Output format: text, json, mermaid (default: text)

**Examples:**
```bash
# Show all dependencies
bin/data-utils/bq-lineage project.dataset.orders

# Show only downstream dependencies
bin/data-utils/bq-lineage project.dataset.orders --direction=downstream

# Generate Mermaid diagram
bin/data-utils/bq-lineage project.dataset.orders --format=mermaid
```

**Output includes:**
- Upstream dependencies (tables this table depends on)
- Downstream dependencies (tables that depend on this table)
- Dependency counts
- Impact analysis information

**Note:** Lineage detection works best with views and materialized views. For tables, it searches for references in view definitions across the project.

### db-optimize

Optimize Delta tables in Databricks using OPTIMIZE command with optional Z-ORDER clustering.

**Usage:**
```bash
bin/data-utils/db-optimize <table_name> [options]
```

**Options:**
- `--zorder=<cols>` - Comma-separated columns for Z-ORDER BY
- `--format=<format>` - Output format: text, json (default: text)
- `--workspace=<url>` - Databricks workspace URL (default: env DATABRICKS_HOST)
- `--token=<token>` - Access token (default: env DATABRICKS_TOKEN)
- `--dry-run` - Show what would be optimized without executing

**Examples:**
```bash
# Optimize a table
bin/data-utils/db-optimize main.analytics.sales

# Optimize with Z-ORDER clustering
bin/data-utils/db-optimize main.analytics.sales --zorder=date,region

# Dry run to preview
bin/data-utils/db-optimize main.analytics.sales --dry-run

# JSON output
bin/data-utils/db-optimize main.analytics.sales --format=json
```

**Output includes:**
- Optimization command executed
- Execution time
- Files added and removed
- Success/failure status

### db-vacuum

Clean up old files in Delta tables to reclaim storage space.

**Usage:**
```bash
bin/data-utils/db-vacuum <table_name> [options]
```

**Options:**
- `--retention=<hours>` - Retention period in hours (default: 168 = 7 days)
- `--format=<format>` - Output format: text, json (default: text)
- `--workspace=<url>` - Databricks workspace URL (default: env DATABRICKS_HOST)
- `--token=<token>` - Access token (default: env DATABRICKS_TOKEN)
- `--dry-run` - Show what would be deleted without executing

**Examples:**
```bash
# Vacuum with default retention (7 days)
bin/data-utils/db-vacuum main.analytics.sales

# Custom retention period (72 hours)
bin/data-utils/db-vacuum main.analytics.sales --retention=72

# Dry run to preview
bin/data-utils/db-vacuum main.analytics.sales --dry-run

# JSON output
bin/data-utils/db-vacuum main.analytics.sales --format=json
```

**Output includes:**
- Number of files deleted
- Sample of deleted file paths (in dry run)
- Execution time
- Success/failure status

**Warning:** After vacuuming, you cannot time travel to versions older than the retention period.

### db-stats

Display comprehensive statistics and metadata for Delta tables.

**Usage:**
```bash
bin/data-utils/db-stats <table_name> [options]
```

**Options:**
- `--history=<n>` - Number of recent operations to show (default: 5)
- `--format=<format>` - Output format: text, json (default: text)
- `--workspace=<url>` - Databricks workspace URL (default: env DATABRICKS_HOST)
- `--token=<token>` - Access token (default: env DATABRICKS_TOKEN)

**Examples:**
```bash
# Show table statistics
bin/data-utils/db-stats main.analytics.sales

# Show more history
bin/data-utils/db-stats main.analytics.sales --history=10

# JSON output
bin/data-utils/db-stats main.analytics.sales --format=json
```

**Output includes:**
- Table location and format
- Number of files and total size
- Partitioning information
- Table properties and configuration
- Recent operations from transaction log

### db-lineage

Explore Unity Catalog table lineage to understand dependencies.

**Usage:**
```bash
bin/data-utils/db-lineage <table_name> [options]
```

**Options:**
- `--direction=<dir>` - Lineage direction: upstream, downstream, both (default: both)
- `--depth=<n>` - Maximum depth to traverse (default: 1)
- `--format=<format>` - Output format: text, json, mermaid (default: text)
- `--workspace=<url>` - Databricks workspace URL (default: env DATABRICKS_HOST)
- `--token=<token>` - Access token (default: env DATABRICKS_TOKEN)

**Examples:**
```bash
# Show all dependencies
bin/data-utils/db-lineage main.analytics.sales

# Show only upstream dependencies
bin/data-utils/db-lineage main.analytics.sales --direction=upstream

# Generate Mermaid diagram
bin/data-utils/db-lineage main.analytics.sales --format=mermaid

# Deeper traversal
bin/data-utils/db-lineage main.analytics.sales --depth=2
```

**Output includes:**
- Upstream dependencies (sources this table reads from)
- Downstream dependencies (consumers that read from this table)
- Table types and creation timestamps
- Dependency visualization (Mermaid format)

**Note:** Requires access to system.access.table_lineage in Unity Catalog. Falls back to view definition parsing if system tables are not accessible.

### Installation

To make utilities accessible from anywhere, add to your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/decentclaude/bin/data-utils"
```

Or create symlinks:

```bash
# BigQuery utilities
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-schema-diff /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-query-cost /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-partition-info /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-lineage /usr/local/bin/

# Databricks utilities
sudo ln -s /path/to/decentclaude/bin/data-utils/db-optimize /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/db-vacuum /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/db-stats /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/db-lineage /usr/local/bin/
```

### Requirements

**BigQuery utilities** require:
- Python 3.7+
- google-cloud-bigquery library: `pip install google-cloud-bigquery`
- Google Cloud credentials configured (via GOOGLE_APPLICATION_CREDENTIALS or gcloud auth)

**Databricks utilities** require:
- Python 3.7+
- databricks-sql-connector library: `pip install databricks-sql-connector`
- Environment variables:
  - `DATABRICKS_HOST`: Workspace URL (e.g., https://your-workspace.cloud.databricks.com)
  - `DATABRICKS_TOKEN`: Personal access token or service principal token

## Customization

### Adding Custom Checks

Edit `scripts/data_quality.py` to add project-specific quality checks:

```python
class CustomCheck(DataQualityCheck):
    def __init__(self):
        super().__init__("My Custom Check")

    def run(self) -> bool:
        # Your validation logic
        self.passed = True
        self.message = "Check passed"
        return self.passed
```

### Adding New Hooks

Edit `.claude/settings.json`:

```json
{
  "hooks": {
    "custom": {
      "my-hook": {
        "command": "echo 'Running my hook'",
        "description": "My custom hook"
      }
    }
  }
}
```

## Git Pre-commit Integration

To run validation on every git commit:

```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
python3 scripts/data_quality.py
EOF
chmod +x .git/hooks/pre-commit
```

## Project Structure

```
.
├── .claude/
│   ├── settings.json           # Hook configurations
│   └── HOOKS.md               # Hook documentation
├── bin/
│   ├── data-utils/            # CLI utilities for data platforms
│   │   ├── bq-schema-diff     # BigQuery: Compare table schemas
│   │   ├── bq-query-cost      # BigQuery: Estimate query costs
│   │   ├── bq-partition-info  # BigQuery: Analyze partitions
│   │   ├── bq-lineage         # BigQuery: Explore table lineage
│   │   ├── db-optimize        # Databricks: Optimize Delta tables
│   │   ├── db-vacuum          # Databricks: Clean up old files
│   │   ├── db-stats           # Databricks: Table statistics
│   │   └── db-lineage         # Databricks: Unity Catalog lineage
│   └── worktree-utils/        # Git worktree utilities
├── scripts/
│   └── data_quality.py        # Data quality check framework
├── docs/                      # Documentation
├── examples/                  # Example SQL and configs
├── data-engineering-patterns.md  # Best practices guide
└── README.md                  # This file
```

## Requirements

- Python 3.7+
- sqlparse (required for hooks)
- google-cloud-bigquery (required for BigQuery CLI utilities)
- databricks-sql-connector (required for Databricks CLI utilities)
- sqlfluff (optional, for linting)
- dbt-core (optional, for dbt hooks)
- sqlmesh (optional, for SQLMesh hooks)

## Contributing

1. Add new hooks to `.claude/settings.json`
2. Document hooks in `.claude/HOOKS.md`
3. Add quality checks to `scripts/data_quality.py`
4. Test hooks before committing

## License

MIT

## Support

For issues or questions about Claude Code hooks, see:
- [Claude Code Documentation](https://github.com/anthropics/claude-code)
- [Hooks Documentation](.claude/HOOKS.md)