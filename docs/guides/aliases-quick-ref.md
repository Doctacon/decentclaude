# Command Aliases Quick Reference

One-page cheat sheet for DecentClaude command aliases.

## Installation

```bash
# Automated installation
./bin/install-aliases.sh

# Manual installation
source /path/to/rig/bin/aliases.sh
```

## BigQuery Commands

```bash
bqp <table>              # Profile table (statistics, quality, anomalies)
bqe <query>              # Explain query execution plan
bqo <query>              # Optimize query and get suggestions
bql <table>              # Show table lineage (upstream/downstream)
bqd <table1> <table2>    # Diff schemas between two tables
bqc <table1> <table2>    # Compare tables (rows, schema, data)
bqx                      # Explore datasets interactively (TUI)
bqb <query>              # Benchmark query performance
bqcost <query>           # Estimate query cost
bqpart <table>           # Show partition information
bqrep                    # Generate cost usage report
```

## dbt Commands

```bash
dbtt <model>             # Generate tests for model
dbtd <model>             # Show model dependencies graph
dbtserve                 # Serve dbt docs with auto-reload
dbts <search>            # Search models by name/column
```

## SQLMesh Commands

```bash
smdiff                   # Show model diffs
smmig                    # Migrate SQLMesh project
smval                    # Validate SQLMesh models
smviz                    # Visualize SQLMesh lineage
```

## AI Commands

```bash
aig --type <type>        # Generate code (model/test/migration)
aiq "<nl query>"         # Natural language to SQL
air <file>               # AI code review
aid <path>               # Generate documentation
```

## Debug & Incident

```bash
aidbg --error "<msg>"    # Analyze error with AI
inc create               # Create incident report
inct add                 # Add timeline entry
incpm --incident <id>    # Generate post-mortem
runbook                  # Track runbook execution
```

## Knowledge Base

```bash
kb add <title>           # Add knowledge entry
kb search <query>        # Search knowledge base
kb list                  # List all entries
kbw                      # Start web interface
```

## Common Workflows

### Profile and Optimize Table

```bash
# 1. Profile the table
bqp my-project.dataset.users

# 2. Check lineage
bql my-project.dataset.users

# 3. Analyze partition info
bqpart my-project.dataset.users
```

### Optimize Slow Query

```bash
# 1. Explain current query
bqe "SELECT * FROM dataset.large_table WHERE date > '2024-01-01'"

# 2. Get optimization suggestions
bqo "SELECT * FROM dataset.large_table WHERE date > '2024-01-01'"

# 3. Benchmark improved query
bqb "SELECT * FROM dataset.large_table WHERE date > '2024-01-01' AND _PARTITIONTIME > '2024-01-01'"

# 4. Estimate cost
bqcost "SELECT ..."
```

### Compare Tables (e.g., dev vs prod)

```bash
# Quick comparison
bqc dev-project.dataset.users prod-project.dataset.users

# Detailed schema diff
bqd dev-project.dataset.users prod-project.dataset.users
```

### Generate dbt Model with AI

```bash
# 1. Generate model
aig --type model --name fct_revenue

# 2. Review generated code
air models/marts/fct_revenue.sql

# 3. Generate tests
dbtt models/marts/fct_revenue.sql

# 4. Check dependencies
dbtd models/marts/fct_revenue.sql
```

### Debug Data Quality Issue

```bash
# 1. Analyze error
aidbg --error "NULL values in revenue column"

# 2. Search knowledge base for similar issues
kb search "null revenue"

# 3. Profile table to find issues
bqp my-project.dataset.orders

# 4. Create incident if needed
inc create --severity medium --title "Null revenue values"
```

## Tips

### List All Aliases

```bash
decentclaude-aliases     # Full list with descriptions
dca                      # Short alias for above
```

### Get Help

```bash
bqp --help               # Get help for specific command
kb search "<topic>"      # Search knowledge base
```

### Shell Completion

Use `Tab` to autocomplete:

```bash
bq<Tab>                  # Lists all bq* aliases
dbt<Tab>                 # Lists all dbt* aliases
```

### Combine with Other Tools

```bash
# Profile all tables in a dataset
bq ls my-project:dataset | tail -n +3 | awk '{print $1}' | xargs -I {} bqp my-project.dataset.{}

# Generate tests for all models
find models/ -name "*.sql" | xargs -I {} dbtt {}
```

## Reference

For detailed documentation:

- [Command Aliases Guide](command-aliases.md) - Full installation and usage guide
- [QUICKSTART](QUICKSTART.md) - Getting started guide
- Main README - Complete feature overview

## Troubleshooting

### Alias not found

```bash
# Reload shell config
source ~/.bashrc  # or ~/.zshrc

# Check if aliases.sh is sourced
grep aliases.sh ~/.bashrc
```

### Permission denied

```bash
# Make utilities executable
chmod +x /path/to/rig/bin/data-utils/*
```

### Conflicting alias

```bash
# Check what the alias points to
type bqp

# Unset conflicting alias
unalias bqp

# Use full command instead
/path/to/rig/bin/data-utils/bq-profile
```
