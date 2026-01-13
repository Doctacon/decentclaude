# AI-Assisted Debugging Tools

Intelligent troubleshooting and debugging utilities powered by AI analysis.

## Quick Start

```bash
# Add to PATH
export PATH="$PATH:/path/to/decentclaude/bin/debug-utils"

# Analyze an error
ai-debug analyze error.log

# Get fix recommendations
ai-debug fix traceback.txt

# Search for similar issues
ai-debug search "division by zero"

# Generate debug queries
ai-debug query "partition errors" --platform=bigquery

# Create incident report
ai-debug report error.log --format=markdown --output=incident.md
```

## Features

### Error Analysis
Automatically analyzes error messages to extract:
- Error type and severity
- File location and line numbers
- Stack traces
- Relevant keywords
- Contextual information

### Root Cause Suggestions
Provides ranked suggestions for potential root causes with:
- Confidence scores
- Category classification
- Code context analysis
- Pattern matching

### Fix Recommendations
Generates actionable fix recommendations including:
- Step-by-step instructions
- Code patches when applicable
- Verification steps
- Best practices

### Knowledge Base Search
Searches your codebase for similar issues across:
- Documentation files
- Beads (issues)
- Git commit history
- Error patterns

### Debug Query Generation
Creates platform-specific debug queries for:
- BigQuery (job errors, partitions, cost estimation)
- PostgreSQL (active queries, table stats)
- Python (package inspection, logging)

### Incident Reports
Generates comprehensive reports in multiple formats:
- Markdown (documentation-ready)
- JSON (machine-readable)
- Plain text (readable logs)

## Commands

### analyze
Analyze error messages and extract key information

```bash
ai-debug analyze <error_source> [--format=<format>] [--context=<path>]
```

**Examples:**
```bash
# Analyze error from file
ai-debug analyze error.log

# Analyze from stdin
pytest tests/ 2>&1 | ai-debug analyze -

# Include code context
ai-debug analyze error.log --context=src/app.py

# Get JSON output
ai-debug analyze error.log --format=json
```

### suggest
Suggest potential root causes for errors

```bash
ai-debug suggest <error_source> [--format=<format>] [--depth=<level>]
```

**Depth levels:**
- `shallow`: Top 3 suggestions
- `normal`: Top 5 suggestions (default)
- `deep`: Top 10 suggestions with code analysis

**Examples:**
```bash
# Get root cause suggestions
ai-debug suggest traceback.txt

# Deep analysis with code inspection
ai-debug suggest error.log --depth=deep

# JSON output for automation
ai-debug suggest error.log --format=json
```

### fix
Provide fix recommendations and patches

```bash
ai-debug fix <error_source> [--format=<format>] [--auto-apply]
```

**Examples:**
```bash
# Get fix recommendations
ai-debug fix error.log

# View fixes as JSON
ai-debug fix error.log --format=json

# Note: --auto-apply is planned for future release
```

### search
Search knowledge base for similar issues

```bash
ai-debug search <query> [--format=<format>] [--scope=<scope>]
```

**Scopes:**
- `docs`: Search documentation only
- `beads`: Search beads (issues) only
- `commits`: Search git commit history only
- `all`: Search everything (default)

**Examples:**
```bash
# Search for SQL errors
ai-debug search "division by zero in aggregation"

# Search only in docs
ai-debug search "partition pruning" --scope=docs

# Search beads for similar bugs
ai-debug search "timeout error" --scope=beads
```

### query
Generate debug queries for investigation

```bash
ai-debug query <context> [--format=<format>] [--platform=<platform>]
```

**Platforms:**
- `bigquery`: BigQuery debug queries
- `postgres`: PostgreSQL queries
- `python`: Python debug commands
- `auto`: Auto-detect from context (default)

**Examples:**
```bash
# Generate BigQuery debug queries
ai-debug query "partition errors" --platform=bigquery

# Auto-detect platform
ai-debug query "SQL timeout issues"

# Get queries as JSON
ai-debug query "performance problems" --format=json
```

### report
Create comprehensive incident reports

```bash
ai-debug report <error_source> [--format=<format>] [--output=<file>]
```

**Formats:**
- `markdown`: Markdown format (default)
- `json`: Machine-readable JSON
- `text`: Plain text

**Examples:**
```bash
# Create markdown report
ai-debug report error.log --format=markdown

# Save to file
ai-debug report error.log --output=incident.md

# Generate JSON report for tracking system
ai-debug report error.log --format=json --output=incident.json
```

## Integration Examples

### With pytest
```bash
# Analyze test failures
pytest tests/ 2>&1 | ai-debug analyze -

# Create report from test output
pytest tests/ 2>&1 | ai-debug report - --output=test-failure.md
```

### With git hooks
```bash
# Add to pre-commit hook
if ! pytest tests/; then
    pytest tests/ 2>&1 | ai-debug analyze -
fi
```

### With CI/CD
```bash
# In CI pipeline
run_tests() {
    pytest tests/ 2>&1 | tee test_output.log
    if [ $? -ne 0 ]; then
        ai-debug report test_output.log --format=json --output=artifacts/failure-report.json
    fi
}
```

### With BigQuery
```bash
# Analyze BigQuery errors
bq query --use_legacy_sql=false "SELECT ..." 2>&1 | ai-debug analyze -

# Get partition debug queries
ai-debug query "partition performance" --platform=bigquery > debug-queries.sql
```

## Output Formats

### Text (Default)
Human-readable colored output for terminal display.

### JSON
Machine-readable format for automation and integration:
```json
{
  "error_type": "python",
  "severity": "high",
  "summary": "TypeError: unsupported operand type(s)",
  "location": {
    "file": "src/app.py",
    "line": 42
  },
  "keywords": ["TypeError", "operand", "type"]
}
```

### Markdown
Documentation-ready format for reports and wikis.

## Tips

1. **Use stdin for live errors**: Pipe command output directly to ai-debug
   ```bash
   your-command 2>&1 | ai-debug analyze -
   ```

2. **Combine commands**: Use multiple commands for comprehensive analysis
   ```bash
   ai-debug analyze error.log
   ai-debug suggest error.log --depth=deep
   ai-debug fix error.log
   ```

3. **Save reports**: Keep incident reports for future reference
   ```bash
   ai-debug report error.log --output=incidents/$(date +%Y%m%d)-error.md
   ```

4. **Search before debugging**: Check if the issue was solved before
   ```bash
   ai-debug search "your error message"
   ```

5. **Generate queries early**: Get debug queries to investigate faster
   ```bash
   ai-debug query "error context" --platform=bigquery
   ```

## See Also

- [AI-Debug Reference](AI_DEBUG.md) - Comprehensive command reference
- [Data Utilities](../data-engineering/README.md) - BigQuery debugging tools
- [Worktree Utilities](../worktrees/README.md) - Git workflow tools
