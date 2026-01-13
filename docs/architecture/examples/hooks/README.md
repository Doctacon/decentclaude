# Claude Code Hook Examples

This directory contains example hook scripts that demonstrate how to extend Claude Code with custom automation at key lifecycle points.

## What Are Hooks?

Hooks are executable bash scripts that run automatically at specific points during Claude Code execution:

- **PreToolUse** - Runs before a tool is executed (can validate/block)
- **PostToolUse** - Runs after a tool completes (can process results)
- **PreResponse** - Runs before Claude generates a response
- **PostResponse** - Runs after response is delivered

## Hook Naming Convention

Hooks follow a strict naming pattern:

```
{HookType}__{hook-name}.sh
```

Examples:
- `PreToolUse__sql-validation.sh` - Validates SQL before execution
- `PostToolUse__auto-formatting.sh` - Formats code after edits
- `PostToolUse__cost-tracking.sh` - Tracks BigQuery costs

## Available Example Hooks

### 1. PreToolUse__sql-validation.sh

Validates SQL queries before execution to prevent costly mistakes.

**Features:**
- Validates SQL syntax using BigQuery MCP
- Checks for anti-patterns (SELECT *, missing WHERE, etc.)
- Warns about high-cost queries
- Can block execution if issues found

**Configuration:**
```bash
export SQL_VALIDATION_STRICT=1           # Block on warnings
export SQL_VALIDATION_MAX_BYTES=10737418240  # Max bytes (10GB)
export SQL_VALIDATION_DISABLED=1         # Disable hook
```

**Usage:**
```bash
# Install
chmod +x PreToolUse__sql-validation.sh
cp PreToolUse__sql-validation.sh ~/.claude/hooks/

# Test
echo '{"tool": "mcp__bigquery__run_query", "arguments": {"sql": "SELECT * FROM table"}}' | ./PreToolUse__sql-validation.sh
```

### 2. PostToolUse__auto-formatting.sh

Automatically formats code files after Write/Edit operations.

**Supported Languages:**
- Python (black, autopep8, yapf)
- SQL (sqlfluff, pg_format)
- JavaScript/TypeScript (prettier)
- Go (gofmt)
- Rust (rustfmt)
- Shell (shfmt)

**Configuration:**
```bash
export AUTO_FORMAT_DISABLED=1       # Disable hook
export AUTO_FORMAT_PYTHON=black     # Python formatter
export AUTO_FORMAT_SQL=sqlfluff     # SQL formatter
export AUTO_FORMAT_JS=prettier      # JS/TS formatter
export AUTO_FORMAT_BACKUP=1         # Create .bak files
```

**Installation:**
```bash
# Install formatters
pip install black sqlfluff
npm install -g prettier

# Install hook
chmod +x PostToolUse__auto-formatting.sh
cp PostToolUse__auto-formatting.sh ~/.claude/hooks/
```

### 3. PostToolUse__cost-tracking.sh

Tracks BigQuery query costs and warns about budget limits.

**Features:**
- Logs every query with cost estimate
- Maintains session and daily totals
- Warns at configurable budget thresholds
- Provides cost-saving recommendations

**Configuration:**
```bash
export COST_TRACKING_DISABLED=1          # Disable hook
export COST_TRACKING_DAILY_BUDGET=100    # Daily budget ($USD)
export COST_TRACKING_SESSION_BUDGET=10   # Session budget ($USD)
export COST_TRACKING_WARN_THRESHOLD=0.8  # Warn at 80%
export COST_TRACKING_PRICE_PER_TB=6.25   # BigQuery price/TB
```

**View Logs:**
```bash
# View cost log
cat ~/.claude/bigquery-costs.log

# Daily summary
grep "$(date +%Y-%m-%d)" ~/.claude/bigquery-costs.log | \
  awk -F'|' '{sum+=$4} END {print "Total: $" sum}'
```

## Hook Input/Output Format

### PreToolUse Hooks

**Input (stdin):** JSON object with tool information
```json
{
  "tool": "mcp__bigquery__run_query",
  "name": "run_query",
  "arguments": {
    "sql": "SELECT * FROM dataset.table LIMIT 10",
    "limit": 100
  }
}
```

**Output:** Exit code and stderr messages
- Exit 0: Allow tool execution
- Exit 1: Block tool execution (with error message)

### PostToolUse Hooks

**Input (stdin):** JSON object with tool result
```json
{
  "tool": "Write",
  "name": "Write",
  "arguments": {
    "file_path": "/path/to/file.py",
    "content": "print('hello')"
  },
  "result": {
    "success": true,
    "file_path": "/path/to/file.py"
  }
}
```

**Output:** Exit code and stderr messages
- Exit 0: Success
- Exit 1: Error (warning only, doesn't block)

## Installation

### 1. System-wide Installation

Install hooks for all Claude Code sessions:

```bash
# Create hooks directory
mkdir -p ~/.claude/hooks

# Copy hooks
cp examples/hooks/*.sh ~/.claude/hooks/

# Make executable
chmod +x ~/.claude/hooks/*.sh
```

### 2. Project-specific Installation

Install hooks for a specific project:

```bash
# Create project hooks directory
mkdir -p .claude/hooks

# Copy hooks
cp examples/hooks/*.sh .claude/hooks/

# Make executable
chmod +x .claude/hooks/*.sh
```

### 3. Selective Installation

Install only specific hooks:

```bash
mkdir -p ~/.claude/hooks

# Install just SQL validation
cp examples/hooks/PreToolUse__sql-validation.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/PreToolUse__sql-validation.sh

# Install just auto-formatting
cp examples/hooks/PostToolUse__auto-formatting.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/PostToolUse__auto-formatting.sh
```

## Enabling/Disabling Hooks

### Temporary Disable (Environment Variable)

```bash
# Disable specific hook
export SQL_VALIDATION_DISABLED=1
export AUTO_FORMAT_DISABLED=1
export COST_TRACKING_DISABLED=1

# Run Claude Code
claude
```

### Permanent Disable (Remove Execute Permission)

```bash
# Disable hook
chmod -x ~/.claude/hooks/PreToolUse__sql-validation.sh

# Re-enable hook
chmod +x ~/.claude/hooks/PreToolUse__sql-validation.sh
```

### Remove Hook

```bash
# Delete hook file
rm ~/.claude/hooks/PreToolUse__sql-validation.sh
```

## Creating Custom Hooks

### Basic Template

```bash
#!/usr/bin/env bash
set -euo pipefail

# Read JSON input
INPUT=$(cat)

# Extract tool information
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool // .name // "unknown"')

# Your hook logic here
echo "Processing tool: $TOOL_NAME" >&2

# Exit 0 for success
exit 0
```

### Best Practices

1. **Always use strict mode:** `set -euo pipefail`
2. **Provide disable mechanism:** Use environment variables
3. **Use stderr for logging:** stdout is reserved for data
4. **Handle errors gracefully:** Don't crash on missing dependencies
5. **Include helpful error messages:** Guide users to fix issues
6. **Add configuration options:** Use environment variables
7. **Log important actions:** Maintain audit trail
8. **Be fast:** Hooks run on every tool call
9. **Test thoroughly:** Use sample JSON inputs
10. **Document well:** Include usage examples

### Testing Hooks

```bash
# Test PreToolUse hook
echo '{
  "tool": "mcp__bigquery__run_query",
  "arguments": {"sql": "SELECT * FROM table"}
}' | ./PreToolUse__sql-validation.sh

# Test PostToolUse hook
echo '{
  "tool": "Write",
  "arguments": {"file_path": "test.py"},
  "result": {"success": true}
}' | ./PostToolUse__auto-formatting.sh
```

## Hook Execution Order

When multiple hooks exist for the same trigger:

1. Hooks run in **alphabetical order** by filename
2. Use numeric prefixes to control order: `01-first.sh`, `02-second.sh`
3. PreToolUse hooks can block execution (first failure stops chain)
4. PostToolUse hooks always run (failures logged but don't stop chain)

## Debugging Hooks

### Enable Verbose Logging

```bash
# Add to top of hook script
set -x  # Print each command before execution

# Or run with bash -x
bash -x ~/.claude/hooks/PreToolUse__sql-validation.sh < input.json
```

### Check Hook Output

```bash
# Stderr goes to terminal
# You can redirect to file for debugging
./hook.sh < input.json 2> hook-debug.log
```

### Common Issues

**Hook not running:**
- Check file is executable: `ls -la ~/.claude/hooks/`
- Check naming convention matches: `{HookType}__{name}.sh`
- Check shebang is correct: `#!/usr/bin/env bash`

**JSON parsing errors:**
- Ensure `jq` is installed: `which jq`
- Test JSON structure: `echo "$INPUT" | jq .`
- Validate input format matches expectation

**Permission denied:**
- Make hook executable: `chmod +x hook.sh`
- Check directory permissions: `ls -ld ~/.claude/hooks`

## Advanced Examples

### Hook with External API Call

```bash
#!/usr/bin/env bash
INPUT=$(cat)
SQL=$(echo "$INPUT" | jq -r '.arguments.sql')

# Call external validation service
RESPONSE=$(curl -s -X POST https://api.example.com/validate \
  -H "Content-Type: application/json" \
  -d "{\"sql\": $(echo "$SQL" | jq -Rs .)}")

if echo "$RESPONSE" | jq -e '.valid == false' >/dev/null; then
  echo "External validation failed" >&2
  exit 1
fi
```

### Hook with Slack Notifications

```bash
#!/usr/bin/env bash
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK"

INPUT=$(cat)
COST=$(echo "$INPUT" | jq -r '.cost // 0')

if (( $(echo "$COST > 10" | bc -l) )); then
  curl -X POST "$SLACK_WEBHOOK" \
    -H 'Content-Type: application/json' \
    -d "{\"text\": \"High-cost query: \$$COST\"}"
fi
```

### Hook with Database Logging

```bash
#!/usr/bin/env bash
INPUT=$(cat)

# Log to SQLite database
sqlite3 ~/.claude/hooks.db <<EOF
CREATE TABLE IF NOT EXISTS hook_logs (
  timestamp TEXT,
  tool TEXT,
  status TEXT
);
INSERT INTO hook_logs VALUES (
  datetime('now'),
  '$(echo "$INPUT" | jq -r '.tool')',
  'success'
);
EOF
```

## Security Considerations

1. **Never log sensitive data** - SQL queries may contain credentials
2. **Validate all inputs** - Don't trust JSON structure
3. **Limit file permissions** - `chmod 700 ~/.claude/hooks/`
4. **Use secure API endpoints** - Always use HTTPS
5. **Don't execute untrusted code** - Avoid `eval` on user input
6. **Sanitize file paths** - Prevent directory traversal attacks

## Performance Tips

1. **Exit early** - Check tool name first, skip irrelevant calls
2. **Cache expensive operations** - Use temp files for lookups
3. **Run async when possible** - Background processes for logging
4. **Limit external calls** - Minimize network requests
5. **Use built-in tools** - Prefer bash over external commands

## Resources

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [Bash Best Practices](https://google.github.io/styleguide/shellguide.html)
- [jq Manual](https://stedolan.github.io/jq/manual/)
- [BigQuery Pricing](https://cloud.google.com/bigquery/pricing)

## Contributing

To contribute new hook examples:

1. Follow naming convention
2. Include comprehensive documentation
3. Add configuration via environment variables
4. Test with sample inputs
5. Include error handling
6. Add to this README

## License

These examples are provided as-is for educational purposes. Modify and adapt as needed for your use case.
