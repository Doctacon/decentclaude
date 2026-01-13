# Shell Completion Quick Start

## Installation (30 seconds)

```bash
cd /Users/crlough/gt/decentclaude/mayor/rig/completions
./install-completions.sh
exec $SHELL
```

That's it! Now test it:

```bash
bq-profile --<TAB>
```

## Essential Completions Cheat Sheet

### Command Discovery
```bash
bq-<TAB>              # List all bq utilities
ai-<TAB>              # List all ai utilities
dbt-<TAB>             # List all dbt utilities
sqlmesh-<TAB>         # List all sqlmesh utilities
```

### Option Completion
```bash
bq-profile --<TAB>    # Show all options for bq-profile
--format=<TAB>        # Show valid format values
--parallel=<TAB>      # Show suggested parallel values
```

### Table ID Completion
```bash
bq-profile my-proj<TAB>              # Complete project name
bq-profile my-project.my-dat<TAB>    # Complete dataset name
bq-profile my-project.dataset.tab<TAB>  # Complete table name
```

### File Completion
```bash
bq-explain --file=<TAB>              # Show .sql files
ai-review <TAB>                      # Complete file paths
```

### Common Workflows

#### Profile a table
```bash
bq-profile <TAB>                     # Select table
bq-profile table --format=<TAB>      # Choose format
bq-profile table --format=json --sample-size=<TAB>
```

#### Compare tables
```bash
bq-table-compare <TAB>               # First table
bq-table-compare table1 <TAB>        # Second table
bq-table-compare table1 table2 --check-<TAB>
```

#### Explain query
```bash
bq-explain --file=<TAB>              # Select SQL file
bq-explain --file=query.sql --format=<TAB>
```

## Common Issues

### Completion not working
```bash
# Reload shell
exec $SHELL

# Or source config manually
source ~/.bashrc   # bash
source ~/.zshrc    # zsh
```

### Table IDs not completing
```bash
# Check if cache exists
ls -la ~/.cache/bq-completion-cache

# Verify bq and jq installed
which bq jq

# Check GCP project set
gcloud config get-value project
```

### Slow completion
```bash
# Cache is refreshing in background
# Wait a moment and try again
# Or increase cache TTL in completion scripts
```

## Advanced Tips

### Refresh table cache manually
```bash
rm ~/.cache/bq-completion-cache
bq-profile <TAB>  # Triggers refresh
```

### Use with aliases
```bash
alias bqp='bq-profile'
alias bqe='bq-explain'
# Completion works automatically!
```

### Multiple projects
```bash
export GOOGLE_CLOUD_PROJECT=my-other-project
rm ~/.cache/bq-completion-cache
bq-profile <TAB>  # New project tables
```

## Help

```bash
# Show help for any command
bq-profile --help
bq-explain -h

# Show completion documentation
cat /path/to/completions/README.md
```

## Uninstall

```bash
cd /path/to/completions
./install-completions.sh --uninstall
```
