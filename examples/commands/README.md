# Custom Commands for BigQuery Analysis

This directory contains production-ready custom command scripts for BigQuery analysis and data quality operations. These scripts are designed to be used as slash commands in Claude Code and integrate with the BigQuery MCP (Model Context Protocol) tools.

## Overview

Custom commands in Claude Code are executable bash scripts that can be invoked with slash notation (e.g., `/query-explain`). They provide a convenient way to perform common BigQuery operations with rich formatting and comprehensive analysis.

## Available Commands

### 1. query-explain

Explains BigQuery query execution plans and provides cost estimates.

**Purpose:**
- Validate SQL syntax before execution
- Estimate query costs and resource usage
- Identify performance optimization opportunities
- Understand query complexity

**Usage:**
```bash
# Analyze inline query
query-explain "SELECT * FROM \`project.dataset.table\` LIMIT 10"

# Analyze query from file
query-explain --file queries/complex_join.sql

# Pipe query to command
cat query.sql | query-explain -f -
```

**Features:**
- Query syntax validation
- Cost estimation (bytes processed + dollar cost)
- Performance optimization suggestions
- Complexity analysis

**BigQuery MCP Tools Used:**
- `validate_sql` - Validates query syntax
- `estimate_query_cost` - Estimates bytes processed

---

### 2. schema-compare

Compares schemas of two BigQuery tables and highlights differences.

**Purpose:**
- Validate schema consistency across environments (dev/staging/prod)
- Identify breaking changes in schema evolution
- Plan schema migrations
- Ensure backward compatibility

**Usage:**
```bash
# Compare dev and prod tables
schema-compare my-project.dev_dataset.users my-project.prod_dataset.users

# Compare tables across projects
schema-compare project-a.dataset.table project-b.dataset.table

# Verbose comparison with full schema output
schema-compare -v project.dataset.table_v1 project.dataset.table_v2
```

**Features:**
- Identifies columns only in first table (dropped columns)
- Identifies columns only in second table (new columns)
- Detects type mismatches (breaking changes)
- Compatibility assessment
- Migration recommendations

**BigQuery MCP Tools Used:**
- `check_table_exists` - Verifies tables exist
- `get_table_schema` - Retrieves table schemas
- `compare_schemas` - Compares two schemas

---

### 3. data-profile

Generates comprehensive data quality profile for a BigQuery table.

**Purpose:**
- Understand data characteristics and distributions
- Identify data quality issues
- Detect potential key columns
- Monitor data freshness
- Plan data cleaning and optimization

**Usage:**
```bash
# Basic profile
data-profile my-project.dataset.users

# Detailed profile with all column statistics
data-profile --detailed my-project.dataset.transactions

# Time series analysis
data-profile --time-series my-project.dataset.events

# Profile specific columns
data-profile --columns user_id,email,created_at my-project.dataset.users
```

**Features:**
- Table metadata (size, row count, timestamps)
- Column-level statistics (min, max, mean, stddev)
- Null percentage analysis
- Uniqueness and cardinality metrics
- Time series freshness analysis
- Data quality warnings and recommendations

**BigQuery MCP Tools Used:**
- `check_table_exists` - Verifies table exists
- `get_table_metadata` - Retrieves table metadata
- `profile_table` - Comprehensive table profiling
- `describe_column` - Column-level statistics
- `describe_table_columns` - All column statistics
- `get_table_null_percentages` - Null analysis
- `get_uniqueness_details` - Uniqueness analysis
- `get_data_freshness` - Time-based freshness
- `get_time_series_distribution` - Time distribution
- `get_table_sample` - Sample data preview

---

## Installation

### 1. Make Scripts Executable

```bash
cd /Users/crlough/gt/decentclaude/mayor/rig/examples/commands
chmod +x query-explain schema-compare data-profile
```

### 2. Add to PATH (Option A: Symlinks)

Create symlinks in a directory that's in your PATH:

```bash
# Create a bin directory in your home folder if it doesn't exist
mkdir -p ~/bin

# Create symlinks
ln -s /Users/crlough/gt/decentclaude/mayor/rig/examples/commands/query-explain ~/bin/query-explain
ln -s /Users/crlough/gt/decentclaude/mayor/rig/examples/commands/schema-compare ~/bin/schema-compare
ln -s /Users/crlough/gt/decentclaude/mayor/rig/examples/commands/data-profile ~/bin/data-profile

# Make sure ~/bin is in your PATH (add to ~/.zshrc or ~/.bashrc if needed)
export PATH="$HOME/bin:$PATH"
```

### 3. Add to PATH (Option B: Direct PATH Addition)

Add the commands directory directly to your PATH:

```bash
# Add to ~/.zshrc or ~/.bashrc
echo 'export PATH="/Users/crlough/gt/decentclaude/mayor/rig/examples/commands:$PATH"' >> ~/.zshrc

# Reload shell configuration
source ~/.zshrc
```

### 4. Verify Installation

```bash
# Test that commands are accessible
which query-explain
which schema-compare
which data-profile

# View help for each command
query-explain --help
schema-compare --help
data-profile --help
```

---

## Using as Slash Commands in Claude Code

Once installed and in your PATH, these commands can be invoked in Claude Code using slash notation:

```
/query-explain "SELECT * FROM my-project.dataset.table LIMIT 10"

/schema-compare project.dev.users project.prod.users

/data-profile --detailed project.dataset.events
```

When invoked as slash commands, Claude Code will:
1. Execute the bash script
2. Parse the prompts and MCP tool requests
3. Automatically invoke the appropriate BigQuery MCP tools
4. Format and display the results

---

## Requirements

### BigQuery MCP Configuration

These commands require the BigQuery MCP server to be configured in Claude Code. Ensure your MCP configuration includes:

```json
{
  "mcpServers": {
    "bigquery": {
      "command": "uvx",
      "args": ["mcp-bigquery"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/your/credentials.json"
      }
    }
  }
}
```

### Google Cloud Authentication

You need valid Google Cloud credentials with BigQuery access:

1. Create a service account in Google Cloud Console
2. Grant necessary BigQuery permissions (BigQuery User, BigQuery Data Viewer)
3. Download the service account key JSON file
4. Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

### Required Permissions

The service account needs these BigQuery permissions:
- `bigquery.jobs.create` - For running queries and dry runs
- `bigquery.tables.get` - For reading table metadata
- `bigquery.tables.getData` - For profiling and sampling
- `bigquery.datasets.get` - For listing datasets

---

## Architecture

### How Custom Commands Work

1. **Bash Script Layer**: Each command is a bash script that:
   - Validates arguments
   - Formats output with colors and structure
   - Generates prompts for Claude to execute MCP tools
   - Handles error cases gracefully

2. **Claude Code Integration**: When invoked via slash command:
   - Claude Code executes the bash script
   - Parses the output for MCP tool invocation requests
   - Automatically calls the appropriate BigQuery MCP tools
   - Presents formatted results to the user

3. **BigQuery MCP Tools**: The backend that:
   - Connects to Google BigQuery API
   - Executes queries and metadata operations
   - Returns structured data to Claude
   - Handles authentication and rate limiting

### Script Structure

Each script follows this pattern:

```bash
#!/bin/bash
# Header with description and usage

# Color definitions for formatting
# Help function
# Argument parsing
# Input validation
# Step-by-step execution with prompts
# Error handling
# Formatted output
```

---

## Customization

### Modifying Scripts

You can customize these scripts for your specific needs:

1. **Add custom validation**: Modify the validation functions to enforce your naming conventions
2. **Change output format**: Adjust color codes and formatting
3. **Add new features**: Integrate additional BigQuery MCP tools
4. **Create new commands**: Use these as templates for new custom commands

### Example: Adding Custom Validation

```bash
# Add custom table naming validation
validate_table_id() {
    local table_id="$1"

    # Enforce naming convention: project must be "my-company"
    if [[ ! "$table_id" =~ ^my-company\. ]]; then
        echo "Error: Table must be in 'my-company' project" >&2
        exit 1
    fi
}
```

### Example: Creating a New Command

Use the existing scripts as templates:

```bash
#!/bin/bash
# my-custom-command - Brief description

# Copy the header, color definitions, and help function
# Add your custom logic
# Integrate appropriate BigQuery MCP tools
```

---

## Troubleshooting

### Command Not Found

If you get "command not found" errors:

1. Verify scripts are executable: `ls -l /path/to/commands`
2. Check PATH includes the commands directory: `echo $PATH`
3. Reload shell configuration: `source ~/.zshrc`

### Authentication Errors

If you get authentication errors:

1. Verify credentials file exists: `ls -l $GOOGLE_APPLICATION_CREDENTIALS`
2. Check service account has necessary permissions
3. Ensure BigQuery API is enabled in your GCP project

### MCP Tool Errors

If BigQuery MCP tools fail:

1. Verify MCP server is configured in Claude Code settings
2. Check MCP server logs for errors
3. Test MCP connection directly in Claude Code
4. Ensure you have the latest version of mcp-bigquery

### Permission Denied

If you get permission errors:

1. Make scripts executable: `chmod +x script-name`
2. Verify you have read access to the script directory
3. Check BigQuery table permissions

---

## Best Practices

### Query Optimization

When using `query-explain`:
- Always validate queries before running on production data
- Check cost estimates for large tables
- Use the recommendations to optimize expensive queries
- Consider partitioning and clustering suggestions

### Schema Management

When using `schema-compare`:
- Compare schemas before deploying changes
- Document breaking changes in migration plans
- Use verbose mode for detailed schema review
- Version your schemas in source control

### Data Quality

When using `data-profile`:
- Run profiles regularly to monitor data quality
- Set up alerts for data freshness issues
- Track null percentages over time
- Document data quality thresholds

### Security

- Never hardcode credentials in scripts
- Use environment variables for sensitive configuration
- Limit service account permissions to minimum required
- Audit command usage in production environments

---

## Examples

### Complete Workflow: Schema Migration

```bash
# 1. Compare dev and prod schemas
schema-compare my-project.dev.users my-project.prod.users

# 2. Profile dev table to understand data
data-profile --detailed my-project.dev.users

# 3. Validate migration query
query-explain --file migration.sql

# 4. After migration, verify schemas match
schema-compare my-project.prod.users_backup my-project.prod.users
```

### Complete Workflow: Data Quality Audit

```bash
# 1. Get comprehensive profile
data-profile --detailed my-project.analytics.events

# 2. Check data freshness
data-profile --time-series my-project.analytics.events

# 3. Analyze specific problem columns
data-profile --columns user_id,session_id,timestamp my-project.analytics.events

# 4. Sample problematic data
data-profile --sample 100 my-project.analytics.events
```

### Complete Workflow: Query Optimization

```bash
# 1. Explain current query
query-explain "$(cat current_query.sql)"

# 2. Profile source tables
data-profile my-project.raw.events
data-profile my-project.raw.users

# 3. Compare table structures
schema-compare my-project.raw.events my-project.processed.events

# 4. Validate optimized query
query-explain --file optimized_query.sql
```

---

## Contributing

To contribute new commands or improvements:

1. Create new scripts in this directory
2. Follow the existing naming convention and structure
3. Include comprehensive help text
4. Add examples and documentation
5. Test thoroughly with various table types
6. Update this README with your command

---

## Resources

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [BigQuery MCP Documentation](https://github.com/ergut/mcp-bigquery)
- [BigQuery SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql)
- [Google Cloud Authentication](https://cloud.google.com/docs/authentication)

---

## License

These scripts are provided as examples and can be freely modified and distributed.

## Support

For issues or questions:
- Check the troubleshooting section above
- Review BigQuery MCP documentation
- File issues in the decentclaude repository
- Consult Claude Code documentation

---

**Last Updated**: 2026-01-12
**Version**: 1.0.0
