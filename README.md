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

See [Data Utilities](#data-utilities) for detailed usage.

### Incident Response Utilities

Comprehensive tools for incident management and response automation:

- **incident-report**: Generate and manage structured incident reports
- **incident-timeline**: Build and track incident timelines automatically
- **incident-postmortem**: Generate post-mortem reports with lessons learned
- **runbook-tracker**: Track runbook execution steps during incidents

See [Incident Response Tools](#incident-response-tools) for detailed usage.

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
```

### Requirements

All utilities require:
- Python 3.7+
- google-cloud-bigquery library: `pip install google-cloud-bigquery`
- Google Cloud credentials configured (via GOOGLE_APPLICATION_CREDENTIALS or gcloud auth)

## Incident Response Tools

Comprehensive incident management automation tools to reduce response time and improve post-incident learning.

### incident-report

Generate and manage structured incident reports with automatic tracking.

**Usage:**
```bash
bin/incident-response/incident-report create [options]
bin/incident-response/incident-report update <incident_id> [options]
bin/incident-response/incident-report show <incident_id> [options]
bin/incident-response/incident-report list [options]
```

**Options:**
- `--severity=<level>` - Incident severity: P0, P1, P2, P3 (default: P2)
- `--title=<title>` - Incident title
- `--symptoms=<text>` - Description of symptoms
- `--impact=<text>` - Business impact description
- `--status=<status>` - Incident status: investigating, mitigating, resolved (default: investigating)
- `--format=<format>` - Output format: text, markdown, json (default: markdown)

**Examples:**
```bash
# Create new incident
bin/incident-response/incident-report create --severity=P1 --title="Dashboard data missing" \
  --symptoms="Users report missing data in sales dashboard" \
  --impact="Sales team cannot access Q4 metrics"

# Update incident status
bin/incident-response/incident-report update INC-001 --status=resolved

# Show incident report
bin/incident-response/incident-report show INC-001

# List all incidents
bin/incident-response/incident-report list
```

**Features:**
- Automatic incident ID generation
- Structured severity levels (P0-P3)
- Timeline tracking
- Action item management
- Multiple output formats

### incident-timeline

Build and reconstruct incident timelines automatically from git commits and manual events.

**Usage:**
```bash
bin/incident-response/incident-timeline add <incident_id> <event> [options]
bin/incident-response/incident-timeline rebuild <incident_id> [options]
bin/incident-response/incident-timeline show <incident_id> [options]
bin/incident-response/incident-timeline auto-detect [options]
```

**Options:**
- `--timestamp=<time>` - Event timestamp (ISO format, default: now)
- `--source=<source>` - Source of event: manual, git, log, alert
- `--since=<time>` - Start time for auto-detection
- `--format=<format>` - Output format: text, markdown, mermaid (default: text)

**Examples:**
```bash
# Add event to timeline
bin/incident-response/incident-timeline add INC-001 "Started investigation"

# Rebuild timeline from git commits
bin/incident-response/incident-timeline rebuild INC-001 --since="2024-01-15 10:00"

# Show timeline as Mermaid diagram
bin/incident-response/incident-timeline show INC-001 --format=mermaid

# Auto-detect events from git
bin/incident-response/incident-timeline auto-detect --since="1 hour ago"
```

**Features:**
- Automatic timeline reconstruction from git
- Manual event tracking
- Multiple visualization formats
- Event source attribution (git, manual, log, alert)

### incident-postmortem

Generate comprehensive post-mortem reports with lessons learned.

**Usage:**
```bash
bin/incident-response/incident-postmortem generate <incident_id> [options]
bin/incident-response/incident-postmortem template [options]
```

**Options:**
- `--format=<format>` - Output format: markdown, html (default: markdown)
- `--output=<file>` - Output file (default: stdout)
- `--include-timeline` - Include full timeline in post-mortem

**Examples:**
```bash
# Generate post-mortem
bin/incident-response/incident-postmortem generate INC-001

# Generate with full timeline
bin/incident-response/incident-postmortem generate INC-001 --include-timeline

# Save to file
bin/incident-response/incident-postmortem generate INC-001 --output=postmortem-001.md

# Get blank template
bin/incident-response/incident-postmortem template
```

**Features:**
- Structured post-mortem template
- Automatic duration calculation
- Timeline integration
- Action item tracking
- Lessons learned sections
- HTML and Markdown output

### runbook-tracker

Track runbook execution steps during incident response.

**Usage:**
```bash
bin/incident-response/runbook-tracker start <runbook_name> [options]
bin/incident-response/runbook-tracker step <session_id> <step_number> [options]
bin/incident-response/runbook-tracker status <session_id> [options]
bin/incident-response/runbook-tracker complete <session_id> [options]
```

**Options:**
- `--incident-id=<id>` - Associated incident ID
- `--status=<status>` - Step status: pending, in-progress, completed, skipped
- `--notes=<text>` - Notes for this step

**Examples:**
```bash
# Start tracking a runbook
bin/incident-response/runbook-tracker start "Data Pipeline Failure" --incident-id=INC-001

# Mark step as completed
bin/incident-response/runbook-tracker step RBOOK-001 1 --status=completed --notes="Checked logs"

# Show progress with visual progress bar
bin/incident-response/runbook-tracker status RBOOK-001

# Complete runbook
bin/incident-response/runbook-tracker complete RBOOK-001
```

**Features:**
- Visual progress tracking
- Step-by-step notes
- Progress percentage calculation
- Session management
- Incident association

### Incident Response Workflow

**Complete workflow example:**

```bash
# 1. Create incident
incident-report create --severity=P1 --title="Pipeline failure" \
  --symptoms="Daily sales pipeline failed" \
  --impact="Sales dashboard not updating"

# 2. Start runbook tracking
runbook-tracker start "Pipeline Failure Response" --incident-id=INC-20260112123456

# 3. Track runbook steps
runbook-tracker step RBOOK-20260112123457 1 --status=completed --notes="Checked pipeline logs"
runbook-tracker step RBOOK-20260112123457 2 --status=completed --notes="Identified schema change"

# 4. Add timeline events
incident-timeline add INC-20260112123456 "Pipeline failure detected"
incident-timeline add INC-20260112123456 "Root cause: upstream schema change identified"
incident-timeline add INC-20260112123456 "Fix deployed, pipeline restarted"

# 5. Update incident
incident-report update INC-20260112123456 --status=resolved \
  --resolution="Updated schema mapping, reran pipeline"

# 6. Generate post-mortem
incident-postmortem generate INC-20260112123456 --include-timeline \
  --output=postmortems/pipeline-failure-2026-01-12.md
```

### Installation

Add to your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$PATH:/path/to/decentclaude/bin/incident-response"
```

Or create symlinks:

```bash
sudo ln -s /path/to/decentclaude/bin/incident-response/incident-report /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/incident-response/incident-timeline /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/incident-response/incident-postmortem /usr/local/bin/
sudo ln -s /path/to/decentclaude/bin/incident-response/runbook-tracker /usr/local/bin/
```

### Requirements

All incident response tools require:
- Python 3.7+
- No external dependencies (uses standard library only)

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
│   ├── incident-response/     # Incident management automation
│   │   ├── incident-report    # Generate incident reports
│   │   ├── incident-timeline  # Build incident timelines
│   │   ├── incident-postmortem # Generate post-mortems
│   │   └── runbook-tracker    # Track runbook execution
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