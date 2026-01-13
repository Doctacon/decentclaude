# Hook Examples Quick Start

Get started with Claude Code hooks in 5 minutes.

## What Are These?

Three production-ready hook scripts that extend Claude Code:

1. **PreToolUse__sql-validation.sh** - Validates SQL before running expensive queries
2. **PostToolUse__auto-formatting.sh** - Auto-formats code files after edits
3. **PostToolUse__cost-tracking.sh** - Tracks BigQuery costs and budgets

## Quick Install

```bash
# Copy hooks to your Claude directory
mkdir -p ~/.claude/hooks
cp *.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.sh

# Done! Hooks will run automatically in Claude Code
```

## Test It

```bash
# Run the test suite
./test-hooks.sh

# Or test individual hooks
echo '{"tool": "mcp__bigquery__run_query", "arguments": {"sql": "SELECT * FROM big_table"}}' | \
  ~/.claude/hooks/PreToolUse__sql-validation.sh
```

## Configuration

Set environment variables to customize behavior:

```bash
# SQL Validation
export SQL_VALIDATION_STRICT=1           # Block on warnings
export SQL_VALIDATION_DISABLED=1         # Disable hook

# Auto-formatting
export AUTO_FORMAT_PYTHON=black          # Use black for Python
export AUTO_FORMAT_SQL=sqlfluff          # Use sqlfluff for SQL
export AUTO_FORMAT_DISABLED=1            # Disable hook

# Cost Tracking
export COST_TRACKING_DAILY_BUDGET=100    # Daily budget ($USD)
export COST_TRACKING_SESSION_BUDGET=10   # Session budget ($USD)
export COST_TRACKING_DISABLED=1          # Disable hook
```

## What Happens?

### SQL Validation (PreToolUse)

Before any BigQuery query runs:
- ✓ Checks SQL syntax
- ✓ Warns about SELECT *
- ✓ Warns about missing WHERE clauses
- ✓ Detects unmatched parentheses
- ✓ Flags potential cartesian products

**Blocks bad queries before they run!**

### Auto-formatting (PostToolUse)

After any file edit:
- ✓ Detects file type (Python, SQL, JS, etc.)
- ✓ Runs appropriate formatter
- ✓ Only if formatter is installed
- ✓ Preserves original if formatting fails

**No configuration needed - just works!**

### Cost Tracking (PostToolUse)

After any BigQuery query:
- ✓ Logs query, bytes scanned, cost
- ✓ Tracks session and daily totals
- ✓ Warns at 80% of budget
- ✓ Provides cost-saving tips

**Prevents budget overruns!**

## Example Output

### SQL Validation
```
[SQL Validation] Validating SQL query...
[SQL Validation Warning] Found 2 warning(s):
  ⚠ Query uses SELECT * without LIMIT
  ⚠ Query appears to scan entire table without WHERE clause
```

### Auto-formatting
```
[Auto-Format] Processing example.py
[Auto-Format] Running black on example.py
[Auto-Format] Formatted example.py with black ✓
```

### Cost Tracking
```
[Cost Tracking] Query completed
[Cost Stats] Bytes scanned: 1.25GB
[Cost Stats] Estimated cost: $0.007813
[Cost Tracking] Session total: $0.045678 / $10.00 (0%)
[Cost Tracking] Daily total: $2.34 / $100.00 (2%)
```

## Disable a Hook

```bash
# Temporarily
export SQL_VALIDATION_DISABLED=1

# Permanently (remove execute permission)
chmod -x ~/.claude/hooks/PreToolUse__sql-validation.sh

# Or delete it
rm ~/.claude/hooks/PreToolUse__sql-validation.sh
```

## Troubleshooting

**Hook not running?**
- Check it's executable: `ls -la ~/.claude/hooks/`
- Check naming: Must be `{HookType}__{name}.sh`
- Check shebang: `#!/usr/bin/env bash`

**Formatter not found?**
```bash
# Install formatters
pip install black sqlfluff
npm install -g prettier
brew install shfmt  # for shell scripts
```

**View logs:**
```bash
# Auto-formatting log
cat ~/.claude/auto-format.log

# Cost tracking log
cat ~/.claude/bigquery-costs.log

# Daily cost summary
grep "$(date +%Y-%m-%d)" ~/.claude/bigquery-costs.log | \
  awk -F'|' '{sum+=$4} END {print "Total: $" sum}'
```

## Learn More

- Full documentation: [README.md](README.md)
- Hook development: Create custom hooks with our templates
- Test suite: `./test-hooks.sh` for examples

## Contributing

Found a bug? Have an idea for a new hook? Contributions welcome!

1. Copy a hook template
2. Follow the naming convention
3. Add error handling
4. Document with comments
5. Test thoroughly

## License

MIT - Use freely, modify as needed
