# DecentClaude Data Workflows

Claude Code hooks for world-class data engineering workflows with automated validation, quality checks, and testing.

## Overview

This repository provides a comprehensive set of Claude Code hooks designed specifically for data engineering workflows. These hooks automate validation and quality checks for SQL, dbt, SQLMesh, and other data tools.

## Features

### CLI Data Utilities

Powerful command-line utilities for common BigQuery operations:

- **bq-schema-diff**: Compare schemas of two tables to identify differences
- **bq-query-cost**: Estimate query costs before execution
- **bq-partition-info**: Analyze partitioning configuration and partition sizes
- **bq-lineage**: Explore table dependencies (upstream and downstream)
- **bq-explain**: Visualize query execution plans with detailed stage analysis
- **bq-optimize**: Analyze queries and suggest performance optimizations
- **bq-benchmark**: Benchmark query performance with multiple runs and comparisons
- **bq-cost-report**: Analyze historical costs and usage patterns

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

### bq-explain

Analyze and visualize BigQuery query execution plans with detailed stage-by-stage breakdowns.

**Usage:**
```bash
bin/data-utils/bq-explain <query> [options]
bin/data-utils/bq-explain --file=<sql_file> [options]
bin/data-utils/bq-explain --job-id=<job_id> [options]
```

**Options:**
- `--file=<path>` - Read query from SQL file
- `--job-id=<id>` - Analyze existing job by ID
- `--format=<format>` - Output format: text, json (default: text)
- `--dry-run` - Analyze without executing query

**Examples:**
```bash
# Analyze query execution plan
bin/data-utils/bq-explain "SELECT * FROM project.dataset.table WHERE date = '2024-01-01'"

# Analyze from file
bin/data-utils/bq-explain --file=query.sql

# Analyze existing job
bin/data-utils/bq-explain --job-id=abc123-def456-ghi789

# Dry run analysis (estimate only)
bin/data-utils/bq-explain --file=query.sql --dry-run

# JSON output
bin/data-utils/bq-explain --file=query.sql --format=json
```

**Output includes:**
- Job ID and execution state
- Data processed and billed
- Cache hit status
- Slot usage statistics
- Stage-by-stage execution breakdown
  - Records read/written per stage
  - Compute, read, write, and wait times
  - Shuffle operations and spilling
  - Parallel inputs and execution steps
- Execution timeline
- Visual performance indicators

### bq-optimize

Analyze queries and suggest BigQuery optimization opportunities to improve performance and reduce costs.

**Usage:**
```bash
bin/data-utils/bq-optimize <query> [options]
bin/data-utils/bq-optimize --file=<sql_file> [options]
bin/data-utils/bq-optimize --job-id=<job_id> [options]
```

**Options:**
- `--file=<path>` - Read query from SQL file
- `--job-id=<id>` - Analyze existing job for execution-based recommendations
- `--format=<format>` - Output format: text, json (default: text)

**Examples:**
```bash
# Analyze query for optimizations
bin/data-utils/bq-optimize "SELECT * FROM project.dataset.table WHERE date = '2024-01-01'"

# Analyze from file
bin/data-utils/bq-optimize --file=query.sql

# Analyze with job execution data
bin/data-utils/bq-optimize --file=query.sql --job-id=abc123-def456-ghi789

# JSON output
bin/data-utils/bq-optimize --file=query.sql --format=json
```

**Recommendations include:**
- **High Priority**
  - Missing partition filters (major cost impact)
  - No WHERE clause detected
  - Correlated subqueries
  - CROSS JOIN usage
  - Shuffle spilling to disk
- **Medium Priority**
  - SELECT * usage
  - Large data scans
  - ORDER BY without LIMIT
  - Complex nested queries
  - High shuffle operations
  - Many JOIN operations
- **Low Priority**
  - Missing LIMIT clause
  - Multiple DISTINCT operations
  - Low parallelism

**Categories:**
- Cost optimization
- Performance improvements
- Best practices

### bq-benchmark

Benchmark BigQuery query performance with multiple runs, statistical analysis, and baseline comparisons.

**Usage:**
```bash
bin/data-utils/bq-benchmark <query> [options]
bin/data-utils/bq-benchmark --file=<sql_file> [options]
```

**Options:**
- `--file=<path>` - Read query from SQL file
- `--runs=<n>` - Number of benchmark runs (default: 3)
- `--warmup` - Include a warmup run (not counted in results)
- `--no-cache` - Disable query cache for benchmarking
- `--baseline=<file>` - Compare against baseline results from JSON file
- `--save=<file>` - Save benchmark results to JSON file
- `--format=<format>` - Output format: text, json (default: text)

**Examples:**
```bash
# Run basic benchmark
bin/data-utils/bq-benchmark --file=query.sql

# Run 5 times with warmup
bin/data-utils/bq-benchmark --file=query.sql --runs=5 --warmup

# Disable cache for true performance test
bin/data-utils/bq-benchmark --file=query.sql --no-cache

# Save baseline for future comparison
bin/data-utils/bq-benchmark --file=query.sql --save=baseline.json

# Compare against baseline
bin/data-utils/bq-benchmark --file=query.sql --baseline=baseline.json

# JSON output
bin/data-utils/bq-benchmark --file=query.sql --format=json
```

**Output includes:**
- Configuration (runs, warmup, cache settings)
- Execution time statistics
  - Min, max, mean, median
  - Standard deviation and coefficient of variation
- Data processed statistics
- Slot usage metrics
- Cache hit rate
- Individual run details
- Baseline comparison (when provided)
  - Percent change in execution time
  - Percent change in bytes processed
  - Performance improvement/regression indicators

**Use cases:**
- Compare query performance before/after optimization
- Track performance regression over time
- Validate optimization improvements
- Understand query performance variability

### bq-cost-report

Analyze historical BigQuery costs and usage patterns from job history.

**Usage:**
```bash
bin/data-utils/bq-cost-report [options]
```

**Options:**
- `--project=<id>` - Project ID to analyze (default: current project)
- `--days=<n>` - Number of days to analyze (default: 7)
- `--group-by=<field>` - Group results by: user, dataset, table, query_type (default: user)
- `--top=<n>` - Show top N results (default: 10)
- `--format=<format>` - Output format: text, json, csv (default: text)

**Examples:**
```bash
# Analyze last 7 days by user
bin/data-utils/bq-cost-report

# Analyze last 30 days
bin/data-utils/bq-cost-report --days=30

# Group by dataset
bin/data-utils/bq-cost-report --group-by=dataset --top=20

# Group by table
bin/data-utils/bq-cost-report --group-by=table

# Group by query type
bin/data-utils/bq-cost-report --group-by=query_type

# Analyze different project
bin/data-utils/bq-cost-report --project=my-project --days=90

# JSON output
bin/data-utils/bq-cost-report --format=json

# CSV output for further analysis
bin/data-utils/bq-cost-report --days=30 --format=csv > costs.csv
```

**Output includes:**
- Summary
  - Total jobs executed
  - Total data processed
  - Total cost (USD)
  - Average cost per day
  - Cache hit rate
- Top N results by grouping
  - Number of jobs
  - Cost (total and per job)
  - Cache hit rate
  - Color-coded by cost impact
- Daily breakdown
  - Jobs per day
  - Data processed per day
  - Cost per day
- Cost trends and patterns

**Use cases:**
- Identify cost hot spots
- Track usage by user or team
- Find expensive queries or tables
- Monitor daily cost trends
- Export data for budget reporting

**Note:** Requires access to `INFORMATION_SCHEMA.JOBS_BY_PROJECT`. Costs calculated using on-demand pricing ($6.25/TB).

### Installation

To make utilities accessible from anywhere, add to your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/decentclaude/bin/data-utils"
```

Or create symlinks:

```bash
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-schema-diff /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-query-cost /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-partition-info /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-lineage /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-explain /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-optimize /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-benchmark /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-cost-report /usr/local/bin/
```

### Requirements

All utilities require:
- Python 3.7+
- google-cloud-bigquery library: `pip install google-cloud-bigquery`
- Google Cloud credentials configured (via GOOGLE_APPLICATION_CREDENTIALS or gcloud auth)

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
│   ├── data-utils/            # CLI utilities for BigQuery
│   │   ├── bq-schema-diff     # Compare table schemas
│   │   ├── bq-query-cost      # Estimate query costs
│   │   ├── bq-partition-info  # Analyze partitions
│   │   └── bq-lineage         # Explore table lineage
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
- google-cloud-bigquery (required for CLI utilities)
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