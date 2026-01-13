# DecentClaude Data Workflows

Claude Code hooks for world-class data engineering workflows with automated validation, quality checks, and testing.

## Overview

This repository provides a comprehensive set of Claude Code hooks designed specifically for data engineering workflows. These hooks automate validation and quality checks for SQL, dbt, SQLMesh, and other data tools.

## Features

### Knowledge Base System

Searchable knowledge base for capturing tribal knowledge, issues, solutions, and decisions:

- **Capture Team Knowledge**: Document expertise, best practices, and decisions
- **Track Issues**: Record common problems and their context
- **Store Solutions**: Save workarounds and fixes for future reference
- **Full-Text Search**: Search across all content using SQLite FTS5
- **CLI + Web Interface**: Command-line tools and web UI for browsing
- **Link to Code/Docs**: Connect knowledge to relevant resources

See [Knowledge Base Documentation](docs/knowledge-base.md) for detailed usage.

### CLI Data Utilities

Powerful command-line utilities for common data engineering operations:

**BigQuery Utilities:**
- **bq-profile**: Generate comprehensive data profiles with statistics, quality metrics, and anomaly detection
- **bq-schema-diff**: Compare schemas of two tables to identify differences
- **bq-query-cost**: Estimate query costs before execution
- **bq-partition-info**: Analyze partitioning configuration and partition sizes
- **bq-lineage**: Explore table dependencies (upstream and downstream)
- **bq-table-compare**: Comprehensive table comparison with row counts, schema drift, statistics, and sample data

**dbt Utilities:**
- **dbt-deps**: Visualize dbt model dependencies as graphs
- **dbt-test-gen**: Auto-generate dbt tests from model schemas
- **dbt-docs-serve**: Enhanced local docs server with auto-reload
- **dbt-model-search**: Search models by name, description, or column

**AI Generation:**
- **ai-generate**: AI-powered code generation for dbt models, SQLMesh models, tests, transformations, and migrations
- **ai-query**: Natural language to SQL query builder powered by Claude

See [Data Utilities](#data-utilities) for detailed usage.

### CLI Debug Utilities

AI-assisted debugging and troubleshooting tools:

- **ai-debug**: Intelligent error analysis, root cause suggestions, fix recommendations, knowledge base search, debug query generation, and incident reporting

See [Debug Utilities](#debug-utilities) for detailed usage.

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

**New users: Run the setup wizard for guided installation!**

```bash
./bin/setup-wizard.sh
```

The wizard will install dependencies, configure tools, and test your setup in 2-3 minutes.

**See [QUICKSTART.md](QUICKSTART.md) for a complete 5-minute getting started guide.**

### Manual Installation

```bash
# Install all required dependencies
pip install -r requirements.txt

# Or install individually
pip install sqlparse google-cloud-bigquery anthropic

# Knowledge base web interface
pip install fastapi uvicorn

# AI-powered query builder
pip install anthropic

# Optional tools
pip install sqlfluff dbt-core dbt-bigquery sqlmesh
```

### 1a. Knowledge Base Quick Start

```bash
# Add knowledge
kb add "How to deploy" --content "Deployment guide..." --tags "deployment"

# Search knowledge base
kb search "deployment"

# Start web interface (http://localhost:8000)
kb-web
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

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup and first workflows
- **[Setup Wizard](bin/setup-wizard.sh)** - Interactive installation script
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Tutorials and Guides
- **[Common Workflows Tutorial](docs/WORKFLOWS_TUTORIAL.md)** - Step-by-step daily workflows
- **[Video Walkthrough Script](docs/VIDEO_WALKTHROUGH.md)** - Script for creating video tutorials
- **[Playbooks](playbooks.md)** - Comprehensive workflow patterns
- **[Best Practices](data-engineering-patterns.md)** - Data engineering patterns and anti-patterns

### Technical Reference
- [Hooks Documentation](docs/worktrees/HOOKS.md) - Detailed hook descriptions and usage
- [Data Quality Script](scripts/data_quality.py) - Extensible quality check framework
- [Data Testing Patterns](data-testing-patterns.md) - Testing framework patterns

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

### bq-profile

Generate comprehensive data profiles for BigQuery tables with detailed statistics, quality metrics, and anomaly detection.

**Usage:**
```bash
bin/data-utils/bq-profile <table_id> [options]
```

**Options:**
- `--format=<format>` - Output format: text, json, markdown, html (default: text)
- `--sample-size=<n>` - Number of sample rows to include (default: 10)
- `--detect-anomalies` - Enable anomaly detection for numeric columns

**Examples:**
```bash
# Generate text profile
bin/data-utils/bq-profile project.dataset.customers

# Generate JSON profile
bin/data-utils/bq-profile project.dataset.orders --format=json

# Generate HTML report with anomaly detection
bin/data-utils/bq-profile project.dataset.sales --format=html --detect-anomalies

# Generate Markdown profile with more samples
bin/data-utils/bq-profile project.dataset.events --format=markdown --sample-size=20
```

**Output includes:**

*Table Metadata:*
- Table type, row count, size
- Creation and modification timestamps
- Column count and schema

*Data Type Distribution:*
- Count and percentage of each data type
- Quick overview of column composition

*Column Statistics:*
- **All columns**: null count/percentage, distinct values, uniqueness ratio
- **Numeric columns**: min, max, mean, median, standard deviation, quartiles (Q25, Q75)
- **String columns**: min/max/average length

*Sample Values:*
- Representative sample rows from the table
- Configurable sample size

*Anomaly Detection (optional):*
- Outlier detection using IQR (Interquartile Range) method
- Outlier count and percentage per numeric column
- Lower and upper bounds for expected values

**Use Cases:**
- Initial data exploration and profiling
- Data quality assessment
- Documentation generation
- Anomaly and outlier detection
- Schema understanding and validation

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

### bq-table-compare

Perform comprehensive comparison of two BigQuery tables to validate migrations, compare prod/staging environments, or detect data drift.

**Usage:**
```bash
bin/data-utils/bq-table-compare <table_a> <table_b> [options]
```

**Options:**
- `--format=<format>` - Output format: text, json (default: text)
- `--sample-size=<n>` - Number of rows to sample for comparison (default: 100)
- `--skip-stats` - Skip statistical comparisons (faster)
- `--skip-samples` - Skip sample data comparison

**Examples:**
```bash
# Compare staging and production tables
bin/data-utils/bq-table-compare project.staging.users project.prod.users

# Compare with larger sample size
bin/data-utils/bq-table-compare project.dataset.table_v1 project.dataset.table_v2 --sample-size=1000

# JSON output for programmatic use
bin/data-utils/bq-table-compare project.staging.data project.prod.data --format=json

# Quick comparison without statistics
bin/data-utils/bq-table-compare project.dev.orders project.prod.orders --skip-stats
```

**Output includes:**
- Row count differences with percentage change
- Schema drift detection (missing fields, added fields, type changes)
- Statistical comparison of numeric columns (mean, min, max, stddev, median)
- Data distribution analysis
- Sample data comparison
- Overall summary of differences

**Use cases:**
- Validate data migrations before cutover
- Compare staging and production environments
- Detect schema drift between versions
- Verify data consistency across replicas
- Monitor data quality over time

### dbt-deps

Visualize dbt model dependencies as interactive graphs in multiple formats.

**Usage:**
```bash
bin/data-utils/dbt-deps [options]
bin/data-utils/dbt-deps <model_name> [options]
```

**Options:**
- `--manifest=<path>` - Path to manifest.json (default: target/manifest.json)
- `--format=<format>` - Output format: tree, mermaid, dot, json (default: tree)
- `--upstream` - Show upstream dependencies only (models this depends on)
- `--downstream` - Show downstream dependencies only (models that depend on this)
- `--depth=<n>` - Maximum depth to traverse (default: unlimited)

**Examples:**
```bash
# Show all model dependencies
bin/data-utils/dbt-deps

# Show dependencies for specific model
bin/data-utils/dbt-deps stg_users

# Show only upstream dependencies
bin/data-utils/dbt-deps stg_users --upstream

# Export as Mermaid diagram
bin/data-utils/dbt-deps --format=mermaid > deps.mmd

# Export as PNG via Graphviz
bin/data-utils/dbt-deps --format=dot | dot -Tpng > deps.png
```

**Output includes:**
- Model name and type (view, table, incremental)
- Upstream dependencies (models this depends on)
- Downstream dependencies (models that depend on this)
- Visual representation in chosen format

### dbt-test-gen

Auto-generate dbt tests from model schemas with smart inference.

**Usage:**
```bash
bin/data-utils/dbt-test-gen [options]
bin/data-utils/dbt-test-gen <model_name> [options]
```

**Options:**
- `--manifest=<path>` - Path to manifest.json (default: target/manifest.json)
- `--catalog=<path>` - Path to catalog.json (default: target/catalog.json)
- `--output=<path>` - Output YAML file (default: stdout)
- `--test-suite=<level>` - Test suite: minimal, standard, comprehensive (default: standard)
- `--format=<format>` - Output format: yaml, sql (default: yaml)

**Examples:**
```bash
# Generate standard tests for all models
bin/data-utils/dbt-test-gen

# Generate tests for specific model
bin/data-utils/dbt-test-gen stg_users

# Save to schema file
bin/data-utils/dbt-test-gen stg_users --output=models/staging/schema.yml

# Generate comprehensive test suite
bin/data-utils/dbt-test-gen stg_users --test-suite=comprehensive
```

**Test Suite Levels:**
- **minimal**: not_null tests for primary key columns only
- **standard**: not_null + unique for primary keys, not_null for required columns
- **comprehensive**: All standard tests plus accepted_values, relationships, custom tests

**Smart Inference:**
- Detects primary keys (id, pk, uuid patterns)
- Detects foreign keys (_id, _key, _fk suffixes)
- Detects timestamps (created_at, updated_at)
- Detects booleans (is_, has_, can_ prefixes)
- Detects emails and generates appropriate tests

### dbt-docs-serve

Enhanced local dbt docs server with auto-reload and better UX.

**Usage:**
```bash
bin/data-utils/dbt-docs-serve [options]
```

**Options:**
- `--port=<port>` - Port to serve on (default: 8080)
- `--host=<host>` - Host to bind to (default: 0.0.0.0)
- `--docs-dir=<path>` - Path to docs directory (default: target)
- `--no-browser` - Don't automatically open browser
- `--watch` - Watch for file changes and notify
- `--watch-interval=<s>` - Watch interval in seconds (default: 2)

**Examples:**
```bash
# Serve docs with default settings
bin/data-utils/dbt-docs-serve

# Custom port
bin/data-utils/dbt-docs-serve --port=3000

# Enable file watching for auto-reload
bin/data-utils/dbt-docs-serve --watch

# Don't open browser
bin/data-utils/dbt-docs-serve --no-browser
```

**Features:**
- Automatically opens browser on startup
- File watching with change notifications
- Better error messages for missing files
- Colored terminal output
- CORS headers for local development

### dbt-model-search

Search dbt models by name, description, columns, or tags with smart ranking.

**Usage:**
```bash
bin/data-utils/dbt-model-search <query> [options]
```

**Options:**
- `--manifest=<path>` - Path to manifest.json (default: target/manifest.json)
- `--catalog=<path>` - Path to catalog.json (default: target/catalog.json)
- `--search-in=<fields>` - Fields to search: name,description,columns,tags (default: all)
- `--case-sensitive` - Enable case-sensitive search
- `--format=<format>` - Output format: text, json, csv (default: text)
- `--limit=<n>` - Maximum number of results to show

**Examples:**
```bash
# Find models containing "user"
bin/data-utils/dbt-model-search user

# Search only in column names
bin/data-utils/dbt-model-search email --search-in=columns

# Search in names and tags
bin/data-utils/dbt-model-search "staging" --search-in=name,tags

# Export results as JSON
bin/data-utils/dbt-model-search customer --format=json

# Limit results
bin/data-utils/dbt-model-search order --limit=5
```

**Output includes:**
- Model name and path
- Model type (view, table, incremental)
- Description preview
- Match locations (name, description, columns, tags)
- Relevance score

## Debug Utilities

### ai-debug

AI-assisted debugging and troubleshooting tool for intelligent error analysis.

**Usage:**
```bash
bin/debug-utils/ai-debug <command> [options]
```

**Commands:**
- `analyze` - Analyze error messages and extract key information
- `suggest` - Suggest potential root causes for errors
- `fix` - Provide fix recommendations and patches
- `search` - Search knowledge base for similar issues
- `query` - Generate debug queries for investigation
- `report` - Create comprehensive incident reports

**Examples:**
```bash
# Analyze error from file
bin/debug-utils/ai-debug analyze error.log

# Get root cause suggestions
bin/debug-utils/ai-debug suggest traceback.txt --depth=deep

# Search for similar issues
bin/debug-utils/ai-debug search "division by zero"

# Generate BigQuery debug queries
bin/debug-utils/ai-debug query "partition errors" --platform=bigquery

# Create incident report
bin/debug-utils/ai-debug report error.log --format=markdown --output=incident.md

# Analyze from command output
pytest tests/ 2>&1 | bin/debug-utils/ai-debug analyze -
```

**Features:**
- Intelligent error type detection (Python, BigQuery, SQL, Git, etc.)
- Root cause suggestions with confidence scoring
- Actionable fix recommendations with step-by-step instructions
- Knowledge base search across docs, beads, and git commits
- Platform-specific debug query generation
- Multiple output formats (text, json, markdown)

**Documentation:**
- [Quick Start Guide](docs/debug/README.md)
- [Comprehensive Reference](docs/debug/AI_DEBUG.md)

### ai-generate

AI-powered code generation for data engineering tasks using Claude.

**Usage:**
```bash
bin/data-utils/ai-generate <type> <requirements> [options]
```

**Arguments:**
- `type` - Generation type: dbt-model, sqlmesh-model, test, transform, migration
- `requirements` - Requirements description or path to requirements file

**Options:**
- `--output=<path>` - Output file path (default: stdout)
- `--format=<format>` - Output format: text, json (default: text)
- `--context=<file>` - Additional context file (schema, existing models, etc.)
- `--model=<model>` - Claude model to use (default: claude-sonnet-4-5-20250929)

**Examples:**
```bash
# Generate dbt model from natural language
bin/data-utils/ai-generate dbt-model "daily user engagement metrics" --output=models/staging/stg_analytics__user_engagement.sql

# Generate SQLMesh model from spec file
bin/data-utils/ai-generate sqlmesh-model requirements.txt --output=models/user_engagement_daily.sql

# Generate data quality tests
bin/data-utils/ai-generate test "validate user_id is unique per day in user_engagement" --output=tests/assert_unique_users.sql

# Generate transformation logic
bin/data-utils/ai-generate transform "calculate 7-day rolling average of user activity" --output=macros/rolling_avg.sql

# Generate migration script
bin/data-utils/ai-generate migration "add partitioning to events table by event_date" --output=migrations/001_partition_events.sql

# Use additional context from schema file
bin/data-utils/ai-generate dbt-model "staging layer for orders" --context=schema.json --output=models/staging/stg_orders.sql
```

**Output includes:**
- Generated code ready to save to file
- Model and token usage information
- Success/failure status

**Requirements:**
- Python 3.7+
- anthropic library: `pip install anthropic`
- ANTHROPIC_API_KEY environment variable set

### ai-query

Convert natural language descriptions into SQL queries using Claude AI.

**Usage:**
```bash
bin/data-utils/ai-query <description> [options]
bin/data-utils/ai-query --interactive [options]
bin/data-utils/ai-query --explain <sql> [options]
```

**Options:**
- `--interactive, -i` - Interactive mode for query refinement
- `--explain` - Explain an existing SQL query in natural language
- `--validate` - Validate generated SQL against BigQuery (default: true)
- `--no-validate` - Skip SQL validation
- `--format=<format>` - Output format: text, json, sql (default: text)
- `--context=<tables>` - Comma-separated list of table IDs for context

**Examples:**
```bash
# Generate SQL from natural language
bin/data-utils/ai-query "show me top 10 customers by revenue this year"

# Use table context for better accuracy
bin/data-utils/ai-query "count orders by status for each month" --context=project.dataset.orders

# Interactive mode with refinement
bin/data-utils/ai-query --interactive

# Explain existing SQL
bin/data-utils/ai-query --explain "SELECT COUNT(*) FROM users WHERE active = true"

# Get only the SQL output (useful for piping)
bin/data-utils/ai-query "total sales by region" --format=sql
```

**Features:**
- Converts natural language to BigQuery Standard SQL
- Supports complex queries (joins, aggregations, window functions)
- Automatic SQL validation using BigQuery dry run
- Interactive refinement mode
- Query explanation in natural language
- Table schema context for improved accuracy

**Requirements:**
- Set `ANTHROPIC_API_KEY` environment variable
- Install anthropic package: `pip install anthropic`
- BigQuery authentication configured (for validation)

**Interactive Mode:**
In interactive mode, you can:
- Enter query descriptions naturally
- Use `refine: <changes>` to modify the last query
- Use `explain` to get a natural language explanation
- Use `context: <tables>` to set table context
- Type `quit` to exit

### Installation

To make utilities accessible from anywhere, add to your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/decentclaude/bin/data-utils"
export PATH="$PATH:/path/to/decentclaude/bin/debug-utils"
```

Or create symlinks:

```bash
# BigQuery utilities
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-profile /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-schema-diff /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-query-cost /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-partition-info /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-lineage /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/bq-table-compare /usr/local/bin/

# dbt utilities
sudo ln -s /path/to/decentclaude/bin/data-utils/dbt-deps /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/dbt-test-gen /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/dbt-docs-serve /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/data-utils/dbt-model-search /usr/local/bin/

# AI utilities
sudo ln -s /path/to/decentclaude/bin/data-utils/ai-generate /usr/local/bin/

# Debug utilities
sudo ln -s /path/to/decentclaude/bin/debug-utils/ai-debug /usr/local/bin/
```

### Requirements

**BigQuery utilities (bq-*):**
- Python 3.7+
- google-cloud-bigquery library: `pip install google-cloud-bigquery`
- Google Cloud credentials configured (via GOOGLE_APPLICATION_CREDENTIALS or gcloud auth)

**dbt utilities:**
- Python 3.7+
- dbt project with compiled manifest.json (run `dbt compile` or `dbt run`)
- No additional dependencies (pure Python)

**AI utilities (ai-generate):**
- Python 3.7+
- anthropic library: `pip install anthropic`
- ANTHROPIC_API_KEY environment variable set

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
│   ├── kb                     # Knowledge base CLI
│   ├── kb-web                 # Knowledge base web server
│   ├── data-utils/            # CLI utilities for data engineering
│   │   ├── bq-profile         # Generate data profiles
│   │   ├── bq-schema-diff     # Compare table schemas
│   │   ├── bq-query-cost      # Estimate query costs
│   │   ├── bq-partition-info  # Analyze partitions
│   │   ├── bq-lineage         # Explore table lineage
│   │   ├── bq-table-compare   # Comprehensive table comparison
│   │   ├── dbt-deps           # Visualize dbt model dependencies
│   │   ├── dbt-test-gen       # Auto-generate dbt tests
│   │   ├── dbt-docs-serve     # Enhanced dbt docs server
│   │   ├── dbt-model-search   # Search dbt models
│   │   └── ai-generate        # AI-powered code generation
│   ├── debug-utils/           # AI-assisted debugging utilities
│   │   └── ai-debug           # Intelligent troubleshooting tool
│   └── worktree-utils/        # Git worktree utilities
├── kb/
│   ├── storage.py             # Knowledge base storage backend
│   ├── web.py                 # Knowledge base web interface
│   └── README.md              # Knowledge base docs
├── scripts/
│   └── data_quality.py        # Data quality check framework
├── docs/
│   ├── debug/                 # Debug utilities documentation
│   ├── knowledge-base.md      # Knowledge base documentation
│   ├── templates/             # Project templates
│   └── worktrees/             # Worktree utilities documentation
├── tests/
│   └── test_kb_storage.py     # Knowledge base tests
├── examples/                  # Example SQL and configs
├── data-engineering-patterns.md  # Best practices guide
└── README.md                  # This file
```

## Requirements

- Python 3.7+
- sqlparse (required for hooks)
- google-cloud-bigquery (required for BigQuery CLI utilities)
- anthropic (required for ai-generate utility)
- fastapi + uvicorn (required for knowledge base web interface)
- sqlfluff (optional, for linting)
- dbt-core (optional, for dbt hooks)
- sqlmesh (optional, for SQLMesh hooks)
- pytest (optional, for running tests)

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