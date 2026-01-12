# Claude Code Hooks for Data Workflows

This document describes the Claude Code hooks configured for data engineering workflows.

## Overview

The hooks in this repository provide automated validation and quality checks for data workflows, including SQL validation, dbt compilation, and test execution.

## Hook Types

### 1. User Prompt Submit Hooks

**SQL Query Detection**
- Automatically detects SQL queries in user prompts
- Provides a reminder to validate SQL before execution
- Helps prevent accidental execution of invalid or dangerous queries

### 2. Before Tool Call Hooks

**BigQuery Query Validation**
- Hook: `before-tool-call.mcp__bigquery__run_query`
- Validates SQL syntax using sqlparse before executing BigQuery queries
- Prevents syntax errors from reaching BigQuery
- Requirement: Python package `sqlparse` (`pip install sqlparse`)

**dbt Command Detection**
- Hook: `before-tool-call.Bash`
- Detects dbt commands (run, test, compile)
- Logs dbt workflow actions for visibility

### 3. Before Write Hooks

**SQL File Validation**
- Validates SQL files before writing them to disk
- Uses sqlparse to check syntax
- Ensures only valid SQL is committed to the repository
- Requirement: Python package `sqlparse`

### 4. Custom Hooks

These hooks can be triggered manually or integrated into workflows.

#### dbt-compile
```bash
# Trigger with: Run the dbt-compile hook
```
- Compiles dbt models to check for errors
- Requires: dbt project with `dbt_project.yml`
- Uses profiles from `~/.dbt`

#### dbt-test
```bash
# Trigger with: Run the dbt-test hook
```
- Runs dbt tests
- Validates data quality and model assertions

#### sqlfluff-lint
```bash
# Trigger with: Run the sqlfluff-lint hook
```
- Lints SQL files using sqlfluff
- Enforces SQL style guidelines
- Requirement: `pip install sqlfluff`

#### data-quality-check
```bash
# Trigger with: Run the data-quality-check hook
```
- Runs custom data quality checks
- Expects script at `scripts/data_quality.py`
- Can be customized for project-specific checks

#### pre-commit-data
```bash
# Trigger with: Run the pre-commit-data hook
```
Comprehensive pre-commit validation including:
- SQL file syntax validation
- dbt model compilation
- Can be integrated with git pre-commit hooks

#### sqlmesh-plan
```bash
# Trigger with: Run the sqlmesh-plan hook
```
- Runs SQLMesh plan with auto-apply
- Validates and previews SQLMesh changes
- Requires: SQLMesh installed and `config.yaml` present
- Sets PYTHONPATH=. for proper module resolution

#### sqlmesh-test
```bash
# Trigger with: Run the sqlmesh-test hook
```
- Runs SQLMesh tests
- Validates SQLMesh model logic and transformations

## Setup Requirements

### Python Packages

```bash
pip install sqlparse  # For SQL validation
pip install sqlfluff  # For SQL linting (optional)
pip install dbt-core  # For dbt hooks
pip install sqlmesh   # For SQLMesh hooks
```

### dbt Configuration

Ensure dbt profiles are configured at `~/.dbt/profiles.yml`

### SQLMesh Configuration

For SQLMesh hooks, ensure:
- `config.yaml` exists in the project root
- SQLMesh is installed
- PYTHONPATH is set to `.` when running commands

## Usage Examples

### Manual Hook Execution

Ask Claude to run hooks:
- "Run the dbt-compile hook"
- "Run the pre-commit-data hook"
- "Run the sqlfluff-lint hook"

### Automatic Execution

Hooks run automatically on:
- User prompts containing SQL
- BigQuery query tool calls
- Writing .sql files

### Git Pre-commit Integration

To integrate the pre-commit-data hook with git:

```bash
# Create .git/hooks/pre-commit
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
set -e
echo '=== Pre-commit Data Workflow Checks ==='
echo 'Checking for SQL files...'
if git diff --cached --name-only | grep -q '\.sql$'; then
  echo 'Validating SQL files...'
  for file in $(git diff --cached --name-only | grep '\.sql$'); do
    echo "Checking $file"
    python3 -c "import sqlparse; content = open('$file').read(); parsed = sqlparse.parse(content); exit(0 if parsed else 1)"
  done
  echo '✓ SQL validation passed'
fi
if [ -f dbt_project.yml ]; then
  echo 'Compiling dbt models...'
  dbt compile --profiles-dir ~/.dbt
  echo '✓ dbt compilation passed'
fi
echo '=== All pre-commit checks passed ==='
EOF
chmod +x .git/hooks/pre-commit
```

## Customization

### Adding New Hooks

Edit `.claude/settings.json` to add new hooks:

```json
{
  "hooks": {
    "custom": {
      "your-hook-name": {
        "command": "your-command-here",
        "description": "Description of what this hook does"
      }
    }
  }
}
```

### Modifying Existing Hooks

Edit the `command` field in `.claude/settings.json` for any hook.

### Hook Variables

Available variables in hooks:
- `$CLAUDE_USER_PROMPT`: User's prompt text (user-prompt-submit)
- `$TOOL_ARGS_*`: Tool arguments (before-tool-call)
- `$FILE_PATH`: File being written (before-write)
- `$FILE_CONTENT`: Content being written (before-write)

## Best Practices

1. **Always validate SQL before execution**: Use the BigQuery validation hook
2. **Run pre-commit checks**: Use the pre-commit-data hook before committing
3. **Compile dbt models regularly**: Catch errors early
4. **Lint SQL files**: Maintain consistent style with sqlfluff
5. **Write custom data quality checks**: Add project-specific validations

## Troubleshooting

### Hook Fails with "Command not found"
Install the required tool (dbt, sqlfluff, sqlmesh, etc.)

### SQL Validation Fails
Ensure `sqlparse` is installed: `pip install sqlparse`

### dbt Hooks Fail
- Check that `dbt_project.yml` exists
- Verify dbt profiles at `~/.dbt/profiles.yml`
- Ensure database credentials are configured

### SQLMesh Hooks Fail
- Verify `config.yaml` exists
- Check PYTHONPATH is set correctly
- Ensure SQLMesh is installed: `pip install sqlmesh`

## Contributing

To add new data workflow hooks:
1. Identify the validation or check needed
2. Add the hook to `.claude/settings.json`
3. Document it in this file
4. Test the hook before committing
