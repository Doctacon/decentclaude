# Claude Code Hooks Documentation

This document describes the Claude Code hooks configured for data engineering workflows.

## Overview

This project uses Claude Code hooks to automatically validate SQL, enforce quality standards, and integrate with data tools like dbt and SQLMesh. Hooks run at specific points in the workflow to catch issues early.

## Automatic Hooks

These hooks run automatically during Claude Code operations.

### bigquery-validation (PreToolUse)

**Trigger**: Before any BigQuery MCP tool is executed

**Purpose**: Validates SQL syntax before running BigQuery queries

**What it does**:
- Parses SQL queries using sqlparse
- Checks for basic syntax errors
- Blocks execution if SQL is invalid (exit code 2)

**Example**:
```
User: Run this query: SELECT * FROM dataset.table
Claude: [bigquery-validation hook runs automatically]
        [Hook validates the SQL syntax]
        [If valid, query proceeds; if invalid, execution is blocked]
```

**Requirements**:
- Python 3.7+
- sqlparse: `pip install sqlparse`

**Script location**: `.claude/hooks/bigquery-validation.sh`

### sql-validation (PostToolUse)

**Trigger**: After Edit or Write operations

**Purpose**: Validates SQL files after they are written to disk

**What it does**:
- Checks if the written file is a SQL file (.sql extension)
- Validates SQL syntax using sqlparse
- Checks for hardcoded secrets (passwords, API keys, etc.)
- Blocks if SQL is invalid or warns if secrets are detected

**Example**:
```
User: Create a SQL file with this query: SELECT * FROM users
Claude: [Writes the file]
        [sql-validation hook runs automatically]
        [Hook validates the file content]
```

**Requirements**:
- Python 3.7+
- sqlparse: `pip install sqlparse`

**Script location**: `.claude/hooks/sql-validation.sh`

## Custom Hooks

These hooks can be triggered manually by asking Claude to run them.

### dbt-compile

**Usage**:
```
Run the dbt-compile hook
```

**Purpose**: Compiles dbt models to validate SQL and Jinja templating

**What it does**:
- Checks if dbt is installed
- Verifies dbt_project.yml exists
- Runs `dbt compile` to validate all models
- Reports compilation errors if any

**Requirements**:
- dbt-core: `pip install dbt-core`
- dbt adapter (e.g., dbt-bigquery): `pip install dbt-bigquery`
- Configured dbt profile in `~/.dbt/profiles.yml`

**Exit codes**:
- 0: Compilation succeeded
- 1: Compilation failed (fix errors before proceeding)

**Script location**: `.claude/hooks/dbt-compile.sh`

### dbt-test

**Usage**:
```
Run the dbt-test hook
```

**Purpose**: Runs dbt tests to validate data quality and model integrity

**What it does**:
- Checks if dbt is installed
- Verifies dbt_project.yml exists
- Runs `dbt test` to execute all configured tests
- Reports test failures if any

**Requirements**:
- dbt-core: `pip install dbt-core`
- dbt adapter (e.g., dbt-bigquery): `pip install dbt-bigquery`
- Configured dbt profile in `~/.dbt/profiles.yml`
- Access to data warehouse for running tests

**Exit codes**:
- 0: All tests passed
- 1: One or more tests failed

**Script location**: `.claude/hooks/dbt-test.sh`

### sqlfluff-lint

**Usage**:
```
Run the sqlfluff-lint hook
```

**Purpose**: Lints SQL files to enforce style guidelines and best practices

**What it does**:
- Finds all .sql files in the project (excluding target/, .git/, venv/)
- Runs sqlfluff lint with BigQuery dialect
- Reports style violations and formatting issues

**Requirements**:
- sqlfluff: `pip install sqlfluff`

**Exit codes**:
- 0: All files passed linting
- 1: Linting issues found (run `sqlfluff fix` to auto-fix)

**Tip**: Run `sqlfluff fix --dialect bigquery` to automatically fix many issues

**Script location**: `.claude/hooks/sqlfluff-lint.sh`

### data-quality-check

**Usage**:
```
Run the data-quality-check hook
```

**Purpose**: Runs custom data quality checks using the Python framework

**What it does**:
- Executes `scripts/data_quality.py`
- Runs configured quality checks:
  - SQL file existence checks
  - SQL syntax validation
  - Configuration file checks
  - Hardcoded secrets detection

**Requirements**:
- Python 3.7+
- sqlparse: `pip install sqlparse`

**Customization**: Edit `scripts/data_quality.py` to add project-specific checks

**Exit codes**:
- 0: All quality checks passed
- 1: One or more checks failed

**Script location**: `.claude/hooks/data-quality-check.sh`

## Hook Configuration

Hooks are configured in `.claude/settings.json`. The configuration specifies:

- **When hooks run**: PreToolUse (before) or PostToolUse (after)
- **What triggers them**: Tool name patterns (matchers)
- **What they execute**: Bash scripts
- **Timeouts**: How long hooks can run before being canceled

Example configuration:
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__bigquery__.*",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/bigquery-validation.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

## Workflow Examples

### Validating SQL Before Running

```
User: Run this query: SELECT * FORM dataset.table
Claude: [bigquery-validation hook runs]
        Error: Invalid SQL syntax detected
        [Query execution blocked]

User: Run this query: SELECT * FROM dataset.table
Claude: [bigquery-validation hook runs]
        SQL syntax is valid
        [Query executes successfully]
```

### Creating and Validating SQL Files

```
User: Create a file models/users.sql with this query: SELECT * FROM raw.users
Claude: [Writes the file]
        [sql-validation hook runs]
        SQL file syntax is valid
        [File created successfully]
```

### Running Pre-commit Checks

```
User: Before I commit, run dbt-compile, dbt-test, and data-quality-check
Claude: [Runs dbt-compile.sh]
        ✓ dbt compile succeeded
        [Runs dbt-test.sh]
        ✓ dbt tests passed
        [Runs data-quality-check.sh]
        ✓ Data quality checks passed
        All checks passed - safe to commit!
```

## Troubleshooting

### Hook Not Running

**Check hook registration**:
```
/hooks
```

This shows all registered hooks and their configuration.

**Check hook is executable**:
```bash
ls -la .claude/hooks/
```

All .sh files should have execute permissions (x flag).

### Hook Failing

**Check dependencies**:
- bigquery-validation and sql-validation require sqlparse
- dbt-compile and dbt-test require dbt-core and adapter
- sqlfluff-lint requires sqlfluff

**Check logs**: Hook output is displayed in Claude's response. Read error messages carefully.

**Test hook manually**:
```bash
# Test bigquery-validation
echo '{"tool_input":{"sql":"SELECT * FROM table"}}' | .claude/hooks/bigquery-validation.sh

# Test sql-validation
echo 'SELECT * FROM table' > test.sql
echo '{"tool_input":{"file_path":"test.sql"}}' | .claude/hooks/sql-validation.sh

# Test custom hooks
.claude/hooks/dbt-compile.sh
.claude/hooks/sqlfluff-lint.sh
```

### Bypassing Hooks (Not Recommended)

If you need to temporarily disable hooks:

1. Rename `.claude/settings.json` to `.claude/settings.json.disabled`
2. Perform your operation
3. Rename back to `.claude/settings.json`

Or ask Claude to use Bash directly instead of MCP tools (though this bypasses validation).

## Best Practices

1. **Run hooks before commits**: Always run dbt-compile, dbt-test, and data-quality-check before committing code

2. **Fix issues immediately**: Don't bypass hooks - they catch real problems early

3. **Customize quality checks**: Edit `scripts/data_quality.py` for project-specific validations

4. **Use sqlfluff fix**: Auto-fix style issues with `sqlfluff fix --dialect bigquery`

5. **Keep hooks fast**: Hooks have timeouts (30-120 seconds). Keep them focused and efficient.

6. **Document custom checks**: If you add custom validation logic, document it in this file

## Adding New Hooks

To add a new hook:

1. Create a bash script in `.claude/hooks/`:
   ```bash
   #!/bin/bash
   set -e
   echo "Running my hook..."
   # Your logic here
   exit 0
   ```

2. Make it executable:
   ```bash
   chmod +x .claude/hooks/my-hook.sh
   ```

3. For automatic hooks, add to `.claude/settings.json`:
   ```json
   {
     "hooks": {
       "PreToolUse": [
         {
           "matcher": "MyTool",
           "hooks": [
             {
               "type": "command",
               "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/my-hook.sh",
               "timeout": 30
             }
           ]
         }
       ]
     }
   }
   ```

4. For manual hooks, just create the script and ask Claude to run it

## Environment Variables

Available in hook scripts:

- `$CLAUDE_PROJECT_DIR`: Absolute path to project root
- `CLAUDE_CODE_REMOTE`: Whether running in web ("true") or CLI
- `PYTHONPATH`: Set to "./" for sqlmesh/dbt compatibility

## Exit Codes

Hooks use exit codes to control Claude's behavior:

- **0**: Success, allow operation to proceed
- **1**: General failure (for custom hooks, treated as informational)
- **2**: Blocking failure (prevents tool execution for PreToolUse hooks)

## See Also

- [Claude Code Hooks Documentation](https://code.claude.com/docs/en/hooks.md)
- [Data Quality Script](../scripts/data_quality.py)
- [README](../README.md)
