# Shell Completion for BigQuery Utilities

Comprehensive bash and zsh completion scripts for all BigQuery and data utility commands. These completions significantly improve CLI UX by reducing typing, preventing errors, and providing contextual help.

## Features

### Bash Completion
- **Command completion**: All utility names (bq-profile, bq-explain, etc.)
- **Option completion**: All flags and options with `--option=value` syntax
- **Format completion**: Suggests valid output formats (json, markdown, html, text)
- **Table ID completion**: Auto-completes BigQuery table IDs from cache
- **File completion**: Smart file path completion for --file options
- **Project completion**: GCP project ID completion
- **Cached results**: Caches BigQuery table list for fast completion (1 hour TTL)

### Zsh Completion
- **All bash features** plus:
- **Descriptions**: Detailed descriptions for each option and value
- **Better caching**: More efficient background cache refresh
- **Rich format options**: Descriptive format choices with explanations
- **Model suggestions**: AI model completion with descriptions
- **Smart context**: Context-aware completion based on command

## Quick Installation

### Automatic Installation (Recommended)

```bash
# Install for current user (auto-detects shell)
cd /Users/crlough/gt/decentclaude/mayor/rig/completions
./install-completions.sh

# Install system-wide (requires sudo)
./install-completions.sh --system

# Install for specific shell
./install-completions.sh --bash   # Bash only
./install-completions.sh --zsh    # Zsh only
```

### Manual Installation

#### Bash

1. **Copy the completion file:**
   ```bash
   mkdir -p ~/.bash_completion.d
   cp bash_completion ~/.bash_completion.d/bq-utils
   ```

2. **Source it in your ~/.bashrc:**
   ```bash
   echo '
   # BigQuery utilities completion
   if [ -f "$HOME/.bash_completion.d/bq-utils" ]; then
       . "$HOME/.bash_completion.d/bq-utils"
   fi' >> ~/.bashrc
   ```

3. **Reload your shell:**
   ```bash
   source ~/.bashrc
   ```

#### Zsh

1. **Create completion directory and copy file:**
   ```bash
   mkdir -p ~/.zsh/completion
   cp zsh_completion ~/.zsh/completion/_bq-utils
   ```

2. **Add to fpath in ~/.zshrc:**
   ```bash
   echo '
   # BigQuery utilities completion
   fpath=(~/.zsh/completion $fpath)
   autoload -Uz compinit
   compinit' >> ~/.zshrc
   ```

3. **Reload your shell:**
   ```bash
   source ~/.zshrc
   ```

### System-wide Installation

#### Bash (Linux)
```bash
sudo cp bash_completion /etc/bash_completion.d/bq-utils
```

#### Bash (macOS with Homebrew)
```bash
# Install bash-completion if not already installed
brew install bash-completion

# Copy completion file
sudo cp bash_completion /usr/local/etc/bash_completion.d/bq-utils
```

#### Zsh (Any platform)
```bash
sudo cp zsh_completion /usr/local/share/zsh/site-functions/_bq-utils
```

## Usage Examples

### Command Completion
```bash
# Type 'bq-' and press TAB to see all utilities
$ bq-<TAB>
bq-benchmark    bq-explain      bq-lineage      bq-partition-info  bq-schema-diff
bq-cost-report  bq-explore      bq-optimize     bq-profile         bq-table-compare
bq-query-cost

# Complete command name
$ bq-pro<TAB>
$ bq-profile
```

### Option Completion
```bash
# Press TAB after -- to see all options
$ bq-profile --<TAB>
--detect-anomalies  --format=  --help  --no-cache  --parallel=  --progress  --sample-size=

# Complete option name
$ bq-profile --for<TAB>
$ bq-profile --format=
```

### Format Value Completion
```bash
# After --format=, press TAB to see valid formats
$ bq-profile table_id --format=<TAB>
text  json  markdown  html

# Zsh shows descriptions:
$ bq-profile table_id --format=<TAB>
text      -- Plain text output
json      -- JSON format
markdown  -- Markdown format
html      -- HTML report
```

### Table ID Completion
```bash
# Complete BigQuery table IDs (from cache)
$ bq-profile my-project.my-dataset.<TAB>
my-project.my-dataset.customers
my-project.my-dataset.orders
my-project.my-dataset.products

# Works with multiple tables
$ bq-table-compare my-project.prod.users my-project.<TAB>
my-project.staging.users
my-project.dev.users
```

### File Completion
```bash
# Smart file completion for SQL files
$ bq-explain --file=<TAB>
queries/  analytics.sql  report.sql

# Only shows .sql files
$ bq-explain --file=queries/<TAB>
queries/daily_report.sql  queries/user_stats.sql
```

### Project Completion
```bash
# Complete GCP project IDs
$ bq-cost-report --project=<TAB>
my-project-prod
my-project-staging
my-project-dev
```

## Supported Commands

All utilities in `/bin/data-utils/` are supported:

### BigQuery Utilities
- `bq-profile` - Table profiling with format, sample-size, anomaly detection
- `bq-explain` - Query execution plan analysis
- `bq-explore` - Interactive TUI data discovery
- `bq-lineage` - Data lineage tracking
- `bq-query-cost` - Query cost estimation
- `bq-benchmark` - Performance benchmarking
- `bq-cost-report` - Cost reporting and analysis
- `bq-table-compare` - Table comparison
- `bq-optimize` - Table optimization suggestions
- `bq-partition-info` - Partition information
- `bq-schema-diff` - Schema difference analysis

### AI Utilities
- `ai-docs` - AI-powered documentation
- `ai-generate` - AI code generation
- `ai-query` - AI query assistance
- `ai-review` - AI code review

### DBT Utilities
- `dbt-deps` - DBT dependency management
- `dbt-docs-serve` - DBT documentation server
- `dbt-model-search` - DBT model search
- `dbt-test-gen` - DBT test generation

### SQLMesh Utilities
- `sqlmesh-diff` - SQLMesh diff
- `sqlmesh-migrate` - SQLMesh migration
- `sqlmesh-validate` - SQLMesh validation
- `sqlmesh-visualize` - SQLMesh visualization

## Cache Management

### BigQuery Table Cache

The completion scripts cache BigQuery table IDs for faster completion:

- **Cache file**: `~/.cache/bq-completion-cache`
- **TTL**: 1 hour (3600 seconds)
- **Refresh**: Automatic background refresh when cache expires

#### Manual Cache Refresh

If you want to force a cache refresh:

```bash
# Delete the cache file
rm ~/.cache/bq-completion-cache

# Next completion will trigger a refresh
bq-profile <TAB>
```

#### Cache Requirements

To populate the cache, you need:
1. `bq` command-line tool installed and configured
2. `jq` command for JSON processing
3. Valid GCP credentials
4. Default project set in gcloud config or GOOGLE_CLOUD_PROJECT env var

### Disable Caching

If you don't want table ID completion from cache:

1. **Bash**: Comment out the `_complete_bq_table_id` calls in `bash_completion`
2. **Zsh**: Comment out the `_bq_tables` function in `zsh_completion`

## Troubleshooting

### Completion Not Working

1. **Verify installation:**
   ```bash
   # Bash
   ls -la ~/.bash_completion.d/bq-utils
   grep -q "bq-utils" ~/.bashrc && echo "Sourced in bashrc"

   # Zsh
   ls -la ~/.zsh/completion/_bq-utils
   echo $fpath | grep -q ".zsh/completion" && echo "In fpath"
   ```

2. **Reload shell:**
   ```bash
   exec $SHELL
   ```

3. **Test completion function:**
   ```bash
   # Bash
   type _bq_complete

   # Zsh
   which _bq_utils
   ```

### Table IDs Not Completing

1. **Check cache file:**
   ```bash
   ls -la ~/.cache/bq-completion-cache
   cat ~/.cache/bq-completion-cache | head
   ```

2. **Verify prerequisites:**
   ```bash
   which bq
   which jq
   gcloud config get-value project
   ```

3. **Test manual cache population:**
   ```bash
   # Run the cache refresh manually
   project=$(gcloud config get-value project)
   bq ls --project_id="$project" --format=json | jq -r '.[].id'
   ```

### Completion Too Slow

If completion feels slow:

1. **Check cache freshness:** Old cache = background refresh = slight delay
2. **Increase cache TTL:** Edit `_BQ_CACHE_TTL` in the completion scripts
3. **Pre-populate cache:** Run cache refresh manually before starting work

### Permission Errors

If you see permission errors:

1. **For user installation:** No special permissions needed
2. **For system installation:** Use `sudo` with the install script
3. **For cache directory:** Ensure `~/.cache` is writable

### Zsh Completion Not Loading

1. **Check compinit:**
   ```bash
   # Add to ~/.zshrc if missing
   autoload -Uz compinit
   compinit
   ```

2. **Rebuild completion cache:**
   ```bash
   rm -f ~/.zcompdump
   compinit
   ```

3. **Verify fpath:**
   ```bash
   echo $fpath
   # Should include ~/.zsh/completion
   ```

## Uninstallation

### Using Install Script
```bash
./install-completions.sh --uninstall
```

### Manual Removal

#### Bash
```bash
rm ~/.bash_completion.d/bq-utils
# Remove sourcing lines from ~/.bashrc manually
```

#### Zsh
```bash
rm ~/.zsh/completion/_bq-utils
rm ~/.zcompdump
# Remove fpath configuration from ~/.zshrc manually
```

## Advanced Configuration

### Custom Cache Location

Edit the completion scripts to change cache location:

```bash
# In bash_completion or zsh_completion
_BQ_CACHE_FILE="${HOME}/.local/share/bq-cache"
```

### Custom Cache TTL

Change the cache time-to-live:

```bash
# In bash_completion or zsh_completion
_BQ_CACHE_TTL=7200  # 2 hours instead of 1
```

### Add Custom Options

To add completion for new options:

1. **Bash**: Update `_UTIL_OPTIONS` array in `bash_completion`
2. **Zsh**: Add to the appropriate `_arguments` section in `zsh_completion`

### Multiple Projects

If you work with multiple GCP projects, you can:

1. Set `GOOGLE_CLOUD_PROJECT` environment variable
2. Switch projects: `gcloud config set project PROJECT_ID`
3. Delete cache: `rm ~/.cache/bq-completion-cache`
4. Completion will rebuild cache for new project

## Contributing

To add support for new utilities:

1. **Identify options**: Run `utility --help` to see all options
2. **Update bash_completion**: Add to `_UTIL_OPTIONS` and `_UTIL_FORMAT_OPTIONS`
3. **Update zsh_completion**: Add new case in `_bq_utils` function
4. **Update README**: Add to supported commands list
5. **Test**: Verify completion works in both shells

## License

Same as parent project.

## Support

For issues or questions:
1. Check this README's troubleshooting section
2. Verify your shell and completion setup
3. Test with a simple command first: `bq-profile --<TAB>`
4. Check cache and permissions
