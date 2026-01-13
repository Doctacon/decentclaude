# Command Aliases Guide

This guide covers the installation and usage of short command aliases for DecentClaude data utilities.

## Overview

DecentClaude provides a comprehensive set of command-line utilities for data engineering tasks. While the full command names are descriptive, they can be verbose for frequent use. The alias system provides short, memorable alternatives that speed up your workflow.

## Quick Start

### Automated Installation

The fastest way to install aliases is using the automated installer:

```bash
cd /path/to/decentclaude/mayor/rig
./bin/install-aliases.sh
```

This will:
1. Detect your shell (bash, zsh, or fish)
2. Add the alias configuration to your shell profile
3. Provide instructions for activating the aliases

### Manual Installation

If you prefer manual installation or need more control:

#### Option 1: Source the Aliases (Recommended)

Add this line to your shell configuration:

```bash
# For bash: ~/.bashrc or ~/.bash_profile
# For zsh: ~/.zshrc
source /path/to/decentclaude/mayor/rig/bin/aliases.sh
```

Then reload your shell:

```bash
source ~/.bashrc  # or ~/.zshrc for zsh
```

#### Option 2: Add to PATH

Add the bin directory to your PATH:

```bash
# For bash: ~/.bashrc or ~/.bash_profile
# For zsh: ~/.zshrc
export PATH="$PATH:/path/to/decentclaude/mayor/rig/bin"
```

This allows you to use the full command names directly without aliases.

#### Option 3: Create Symlinks

Create symbolic links in a directory already in your PATH:

```bash
./bin/install-aliases.sh --method symlink
```

This creates short symlinks in `~/.local/bin` (ensure it's in your PATH).

## Available Aliases

### BigQuery Utilities

| Alias | Full Command | Description |
|-------|-------------|-------------|
| `bqp` | `bq-profile` | Generate comprehensive data profiles |
| `bqe` | `bq-explain` | Visualize query execution plans |
| `bqo` | `bq-optimize` | Analyze queries and suggest optimizations |
| `bql` | `bq-lineage` | Explore table dependencies |
| `bqd` | `bq-schema-diff` | Compare schemas of two tables |
| `bqc` | `bq-table-compare` | Comprehensive table comparison |
| `bqx` | `bq-explore` | Interactive TUI for exploring datasets |
| `bqb` | `bq-benchmark` | Benchmark query performance |
| `bqcost` | `bq-query-cost` | Estimate query costs |
| `bqpart` | `bq-partition-info` | Analyze partitioning configuration |
| `bqrep` | `bq-cost-report` | Analyze historical costs and usage |

### dbt Utilities

| Alias | Full Command | Description |
|-------|-------------|-------------|
| `dbtt` | `dbt-test-gen` | Auto-generate dbt tests from schemas |
| `dbtd` | `dbt-deps` | Visualize dbt model dependencies |
| `dbtserve` | `dbt-docs-serve` | Enhanced local docs server with auto-reload |
| `dbts` | `dbt-model-search` | Search models by name, description, or column |

### SQLMesh Utilities

| Alias | Full Command | Description |
|-------|-------------|-------------|
| `smdiff` | `sqlmesh-diff` | Show model diffs |
| `smmig` | `sqlmesh-migrate` | Migrate SQLMesh project |
| `smval` | `sqlmesh-validate` | Validate SQLMesh models |
| `smviz` | `sqlmesh-visualize` | Visualize SQLMesh lineage |

### AI Generation Utilities

| Alias | Full Command | Description |
|-------|-------------|-------------|
| `aig` | `ai-generate` | AI-powered code generation |
| `aiq` | `ai-query` | Natural language to SQL query builder |
| `air` | `ai-review` | AI-powered code reviewer |
| `aid` | `ai-docs` | AI-powered documentation generator |

### Debug & Incident Response

| Alias | Full Command | Description |
|-------|-------------|-------------|
| `aidbg` | `ai-debug` | Intelligent error analysis |
| `inc` | `incident-report` | Generate incident reports |
| `inct` | `incident-timeline` | Track incident timelines |
| `incpm` | `incident-postmortem` | Generate post-mortem reports |
| `runbook` | `runbook-tracker` | Track runbook execution |

### Knowledge Base

| Alias | Full Command | Description |
|-------|-------------|-------------|
| `kb` | `kb` | Knowledge base CLI |
| `kbw` | `kb-web` | Knowledge base web interface |

## Usage Examples

### BigQuery Operations

```bash
# Profile a table
bqp my-project.dataset.users

# Compare two tables
bqc my-project.dataset.users_v1 my-project.dataset.users_v2

# Explain a query
bqe "SELECT * FROM dataset.table WHERE created_at > '2024-01-01'"

# Check table lineage
bql my-project.dataset.users --downstream

# Analyze query performance
bqo --query "SELECT COUNT(*) FROM large_table GROUP BY user_id"
```

### dbt Workflows

```bash
# Generate tests for a model
dbtt models/staging/stg_users.sql

# Visualize model dependencies
dbtd models/marts/fct_orders.sql

# Search for models
dbts "revenue"

# Serve documentation
dbtserve --port 8080
```

### AI-Powered Tasks

```bash
# Generate a new dbt model
aig --type model --name fct_user_revenue

# Convert natural language to SQL
aiq "show me top 10 users by revenue in the last month"

# Review SQL code
air models/staging/stg_orders.sql

# Generate documentation
aid models/marts/
```

### Debugging

```bash
# Analyze an error
aidbg --error "Division by zero in revenue calculation"

# Search knowledge base for solutions
kb search "division by zero"
```

### Incident Response

```bash
# Create incident report
inc create --severity high --title "Data pipeline failure"

# Track timeline
inct add --incident INC-001 --event "Started investigation"

# Generate postmortem
incpm --incident INC-001 --output postmortem.md
```

## Helper Commands

### List All Aliases

To see all available aliases and their descriptions:

```bash
decentclaude-aliases
# or
dca
```

This displays a formatted table of all aliases with descriptions.

## Installation Options

The installer supports multiple options for different use cases:

### Preview Installation (Dry Run)

See what would be installed without making changes:

```bash
./bin/install-aliases.sh --dry-run
```

### Install for Specific Shell

Install for a specific shell type:

```bash
./bin/install-aliases.sh --shell bash
./bin/install-aliases.sh --shell zsh
```

### Choose Installation Method

Select a specific installation method:

```bash
# Source method (recommended)
./bin/install-aliases.sh --method source

# PATH method
./bin/install-aliases.sh --method path

# Symlink method
./bin/install-aliases.sh --method symlink
```

## Uninstallation

To remove the aliases:

```bash
./bin/install-aliases.sh --uninstall
```

This will:
1. Create a backup of your shell configuration
2. Remove the alias configuration
3. Preserve your other shell settings

To remove symlinks:

```bash
./bin/install-aliases.sh --method symlink --uninstall
```

## Updating Aliases

If new utilities are added or aliases are updated:

### For Source/PATH Method

Simply reload your shell configuration:

```bash
source ~/.bashrc  # or ~/.zshrc
```

### For Symlink Method

Re-run the installer:

```bash
./bin/install-aliases.sh --method symlink
```

This will add any new symlinks without affecting existing ones.

## Troubleshooting

### Aliases Not Found

**Problem**: Running an alias gives "command not found"

**Solutions**:
1. Ensure you've reloaded your shell: `source ~/.bashrc`
2. Check that aliases.sh is sourced in your profile: `grep aliases.sh ~/.bashrc`
3. Verify the alias file exists: `ls -la /path/to/bin/aliases.sh`

### Conflicting Aliases

**Problem**: Alias conflicts with existing commands or aliases

**Solutions**:
1. Check for conflicts: `type bqp` (shows what bqp resolves to)
2. Unset conflicting alias: `unalias bqp`
3. Edit aliases.sh to customize alias names
4. Use full command names instead

### Permission Denied

**Problem**: Can't execute the utilities

**Solutions**:
1. Make utilities executable: `chmod +x /path/to/bin/data-utils/*`
2. Check file permissions: `ls -la /path/to/bin/data-utils/`

### PATH Not Updated

**Problem**: PATH changes don't persist

**Solutions**:
1. Ensure you edited the correct shell config (.bashrc vs .bash_profile)
2. Check for syntax errors in config file
3. Verify the config file is being loaded: `echo $PATH`

## Best Practices

### Naming Conventions

The aliases follow a consistent naming pattern:

- **BigQuery**: `bq` prefix (e.g., `bqp`, `bqe`)
- **dbt**: `dbt` prefix (e.g., `dbtt`, `dbtd`)
- **SQLMesh**: `sm` prefix (e.g., `smdiff`, `smval`)
- **AI tools**: `ai` prefix (e.g., `aig`, `aiq`)
- **Incident**: `inc` prefix (e.g., `inc`, `inct`)

This makes it easy to:
- Remember aliases by tool category
- Use shell tab completion effectively
- Avoid naming conflicts

### Shell Completion

For better tab completion, consider using the source method rather than PATH or symlinks. The function-based aliases in aliases.sh provide better completion support.

### Customization

You can customize aliases by editing `bin/aliases.sh`:

```bash
# Add your own custom aliases
alias myalias="${DATA_UTILS_DIR}/my-favorite-util"
myalias() {
    "${DATA_UTILS_DIR}/my-favorite-util" "$@"
}
```

Just be aware that custom changes may be overwritten when updating the repository.

### Integration with Scripts

When writing scripts that use these utilities, prefer full command names for clarity:

```bash
# Good: Clear what's being run
/path/to/bin/data-utils/bq-profile my-project.dataset.table

# Less clear: What is bqp?
bqp my-project.dataset.table
```

Reserve aliases for interactive use.

## Advanced Usage

### Conditional Loading

Load aliases only in interactive shells:

```bash
# In ~/.bashrc or ~/.zshrc
if [[ $- == *i* ]]; then
    source /path/to/aliases.sh
fi
```

### Shell-Specific Aliases

Create shell-specific customizations:

```bash
# In ~/.zshrc (zsh only)
if [[ -n "$ZSH_VERSION" ]]; then
    # Add zsh-specific aliases or functions
fi
```

### Environment-Specific Aliases

Load different aliases based on environment:

```bash
# In ~/.bashrc
if [[ "$ENV" == "production" ]]; then
    source /path/to/aliases-prod.sh
else
    source /path/to/aliases.sh
fi
```

## See Also

- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
- [data-engineering-patterns.md](data-engineering-patterns.md) - Data engineering best practices
- [../reference/cli-reference.md](../reference/cli-reference.md) - Complete CLI reference
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Troubleshooting guide

## Getting Help

If you encounter issues with aliases:

1. Check this guide's troubleshooting section
2. Run `./bin/install-aliases.sh --help` for installer options
3. Check shell configuration: `cat ~/.bashrc` or `cat ~/.zshrc`
4. Open an issue on GitHub with your shell type and error message
