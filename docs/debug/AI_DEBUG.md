# ai-debug - AI-Assisted Debugging Reference

Comprehensive reference for the ai-debug intelligent troubleshooting tool.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Commands](#commands)
  - [analyze](#analyze)
  - [suggest](#suggest)
  - [fix](#fix)
  - [search](#search)
  - [query](#query)
  - [report](#report)
- [Use Cases](#use-cases)
- [Advanced Usage](#advanced-usage)
- [Exit Codes](#exit-codes)
- [Troubleshooting](#troubleshooting)

## Overview

`ai-debug` is an AI-assisted debugging tool that analyzes errors, suggests root causes, provides fix recommendations, searches knowledge bases, generates debug queries, and creates incident reports.

**Key Features:**
- Intelligent error analysis with pattern recognition
- Root cause suggestion with confidence scoring
- Actionable fix recommendations with code patches
- Knowledge base search across docs, beads, and commits
- Platform-specific debug query generation
- Comprehensive incident reporting

**Supported Error Types:**
- Python tracebacks and exceptions
- BigQuery errors
- SQL errors
- Git errors
- Node.js/npm errors
- Compilation errors
- Generic error messages

## Installation

Add to your PATH:

```bash
# In your shell profile (.bashrc, .zshrc, etc.)
export PATH="$PATH:/path/to/decentclaude/bin/debug-utils"

# Or create a symlink
ln -s /path/to/decentclaude/bin/debug-utils/ai-debug /usr/local/bin/ai-debug
```

Verify installation:

```bash
ai-debug --help
```

## Commands

### analyze

Analyze error messages and extract structured information.

#### Synopsis

```bash
ai-debug analyze [<error_source>] [--format=<format>] [--context=<path>]
```

#### Description

Analyzes error messages to extract:
- Error type (Python, BigQuery, SQL, Git, etc.)
- Severity level (critical, high, medium, low)
- Error summary
- File location and line numbers
- Stack traces
- Relevant keywords
- Additional context from files

#### Arguments

- `error_source` - Path to error file or `-` for stdin (optional, defaults to stdin)

#### Options

- `--format=<format>` - Output format: `text` (default), `json`
- `--context=<path>` - Additional context file path (code file, config, etc.)

#### Examples

```bash
# Analyze error from file
ai-debug analyze error.log

# Analyze from command output
pytest tests/ 2>&1 | ai-debug analyze -

# Include code context
ai-debug analyze traceback.txt --context=src/main.py

# Get JSON output for automation
ai-debug analyze error.log --format=json

# Analyze BigQuery error
bq query "SELECT ..." 2>&1 | ai-debug analyze -
```

#### Output Example (Text)

```
Error Analysis

Type: python
Severity: HIGH

Summary:
  TypeError: unsupported operand type(s) for +: 'int' and 'str'

Location:
  File: src/calculator.py
  Line: 42

Keywords: TypeError, operand, type, unsupported
```

#### Output Example (JSON)

```json
{
  "error_type": "python",
  "summary": "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
  "location": {
    "file": "src/calculator.py",
    "line": 42,
    "type": "python"
  },
  "stack_trace": [
    "File \"src/calculator.py\", line 42, in add_values",
    "return a + b",
    "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
  ],
  "keywords": ["TypeError", "operand", "type"],
  "severity": "high",
  "timestamp": "2026-01-12T17:30:00.000000"
}
```

#### Use Cases

- Quick error triage and classification
- Automated error monitoring
- CI/CD failure analysis
- Log file parsing
- Error aggregation and reporting

---

### suggest

Suggest potential root causes for errors with confidence scoring.

#### Synopsis

```bash
ai-debug suggest [<error_source>] [--format=<format>] [--depth=<level>]
```

#### Description

Analyzes errors and suggests potential root causes with:
- Ranked suggestions by confidence
- Category classification
- Confidence scores (0-100%)
- Code context analysis (when available)

Depth levels control the number and detail of suggestions:
- `shallow`: Quick analysis, top 3 suggestions
- `normal`: Standard analysis, top 5 suggestions (default)
- `deep`: Comprehensive analysis with code inspection, top 10 suggestions

#### Arguments

- `error_source` - Path to error file or `-` for stdin (optional, defaults to stdin)

#### Options

- `--format=<format>` - Output format: `text` (default), `json`
- `--depth=<level>` - Analysis depth: `shallow`, `normal` (default), `deep`

#### Examples

```bash
# Get root cause suggestions
ai-debug suggest traceback.txt

# Deep analysis with code inspection
ai-debug suggest error.log --depth=deep

# Quick shallow analysis
ai-debug suggest error.log --depth=shallow

# JSON output for processing
ai-debug suggest error.log --format=json

# From stdin
python script.py 2>&1 | ai-debug suggest -
```

#### Output Example (Text)

```
Root Cause Suggestions

1. Incorrect type passed to function
   Category: type_error
   Confidence: 90%

2. Type annotation mismatch
   Category: type_error
   Confidence: 70%

3. Dictionary key missing
   Category: type_error
   Confidence: 50%
```

#### Output Example (JSON)

```json
[
  {
    "rank": 1,
    "cause": "Incorrect type passed to function",
    "confidence": 0.9,
    "category": "type_error"
  },
  {
    "rank": 2,
    "cause": "Type annotation mismatch",
    "confidence": 0.7,
    "category": "type_error"
  }
]
```

#### Categories

- `permissions` - Access control and permission issues
- `syntax` - Syntax and formatting errors
- `resource_limit` - Quota and resource exhaustion
- `dependency` - Import and module issues
- `type_error` - Type mismatches and null handling
- `other` - Other categories

#### Use Cases

- Rapid problem diagnosis
- Training junior developers
- Automated triage in CI/CD
- Issue prioritization
- Knowledge capture

---

### fix

Provide actionable fix recommendations with step-by-step instructions.

#### Synopsis

```bash
ai-debug fix [<error_source>] [--format=<format>] [--auto-apply]
```

#### Description

Generates fix recommendations based on root cause analysis, including:
- Fix type and category
- Detailed description
- Step-by-step instructions
- Code patches (when applicable)
- Verification steps

Each fix is tied to a root cause with confidence scoring.

#### Arguments

- `error_source` - Path to error file or `-` for stdin (optional, defaults to stdin)

#### Options

- `--format=<format>` - Output format: `text` (default), `json`
- `--auto-apply` - Automatically apply fixes (planned feature, not yet implemented)

#### Examples

```bash
# Get fix recommendations
ai-debug fix error.log

# Get detailed fixes in JSON
ai-debug fix traceback.txt --format=json

# From command output
npm test 2>&1 | ai-debug fix -

# Save fixes for review
ai-debug fix error.log > fixes-to-apply.txt
```

#### Output Example (Text)

```
Fix Recommendations

Fix 1: type_handling
Fix type error or null handling

Steps:
  1. Add type checking or validation
  2. Handle None/null values explicitly
  3. Add type hints (Python) or type guards (TypeScript)
  4. Use defensive programming patterns

Code Patch:
# Add null checking:
if value is not None:
    # your code here
    pass

Verification: Run type checker and unit tests

Fix 2: syntax
Fix syntax error

Steps:
  1. Review the error line indicated in the traceback
  2. Check for common syntax issues (missing quotes, brackets, commas)
  3. Validate against language/SQL specification
  4. Run linter or syntax checker

Verification: Parse/compile the code successfully
```

#### Output Example (JSON)

```json
[
  {
    "root_cause": "Incorrect type passed to function",
    "confidence": 0.9,
    "fix_type": "type_handling",
    "description": "Fix type error or null handling",
    "steps": [
      "Add type checking or validation",
      "Handle None/null values explicitly",
      "Add type hints (Python) or type guards (TypeScript)",
      "Use defensive programming patterns"
    ],
    "code_patch": "if value is not None:\n    # your code here\n    pass",
    "verification": "Run type checker and unit tests"
  }
]
```

#### Fix Types

- `permission` - Grant required permissions
- `syntax` - Fix syntax errors
- `dependency` - Install or fix dependencies
- `type_handling` - Fix type errors and null handling
- `optimization` - Optimize resource usage
- `investigation` - Requires manual investigation

#### Use Cases

- Guided problem resolution
- Developer onboarding
- Automated remediation (future)
- Documentation generation
- Knowledge sharing

---

### search

Search knowledge base for similar issues across documentation, beads, and commits.

#### Synopsis

```bash
ai-debug search <query> [--format=<format>] [--scope=<scope>]
```

#### Description

Searches your codebase for similar issues, solutions, and patterns across:
- Documentation files (`.md` files in `docs/`)
- Beads (issue tracker)
- Git commit history

Results are ranked by relevance and include previews and context.

#### Arguments

- `query` - Search query (required)

#### Options

- `--format=<format>` - Output format: `text` (default), `json`
- `--scope=<scope>` - Search scope: `docs`, `beads`, `commits`, `all` (default)

#### Examples

```bash
# Search everything
ai-debug search "division by zero"

# Search only documentation
ai-debug search "partition pruning" --scope=docs

# Search only beads
ai-debug search "timeout error" --scope=beads

# Search commit history
ai-debug search "fix null pointer" --scope=commits

# Get JSON results
ai-debug search "performance issue" --format=json
```

#### Output Example (Text)

```
Knowledge Base Search Results
Found 3 results

1. [docs] documentation
   File: docs/data-engineering/BIGQUERY.md
   BigQuery partition pruning is a performance optimization...
   Relevance: 80%

2. [beads] issue
   ? de-abc: Fix division by zero in aggregation query
   Relevance: 75%

3. [git] commit
   abc123f Fix null division in partition calculation
   Relevance: 60%
```

#### Output Example (JSON)

```json
[
  {
    "source": "docs",
    "type": "documentation",
    "file": "docs/data-engineering/BIGQUERY.md",
    "relevance": 0.8,
    "preview": "BigQuery partition pruning is a performance..."
  },
  {
    "source": "beads",
    "type": "issue",
    "content": "? de-abc: Fix division by zero in aggregation query",
    "relevance": 0.75
  },
  {
    "source": "git",
    "type": "commit",
    "hash": "abc123f",
    "message": "Fix null division in partition calculation",
    "relevance": 0.6
  }
]
```

#### Search Scopes

- `docs` - Search markdown files in `docs/` directory
- `beads` - Search beads issue tracker using `bd search`
- `commits` - Search git commit messages using `git log --grep`
- `all` - Search all sources (default)

#### Use Cases

- Finding previous solutions to similar errors
- Learning from past incidents
- Discovering documentation
- Identifying patterns
- Building institutional knowledge

---

### query

Generate platform-specific debug queries for investigation.

#### Synopsis

```bash
ai-debug query <context> [--format=<format>] [--platform=<platform>]
```

#### Description

Generates ready-to-use debug queries tailored to specific platforms:
- BigQuery: Job errors, partition info, cost estimation
- PostgreSQL: Active queries, table stats, locks
- Python: Package inspection, imports, diagnostics

Queries are designed to help investigate and diagnose issues quickly.

#### Arguments

- `context` - Context for query generation (error, logs, keywords)

#### Options

- `--format=<format>` - Output format: `text` (default), `json`
- `--platform=<platform>` - Target platform: `bigquery`, `postgres`, `python`, `auto` (default)

#### Examples

```bash
# Generate BigQuery queries
ai-debug query "partition errors" --platform=bigquery

# Auto-detect platform
ai-debug query "SQL timeout issues"

# Python debugging commands
ai-debug query "import error" --platform=python

# Save queries to file
ai-debug query "performance" --platform=postgres > debug-queries.sql

# JSON output
ai-debug query "error analysis" --format=json
```

#### Output Example (Text)

```
Debug Queries

1. Check recent job errors

SELECT
  job_id,
  creation_time,
  error_result.message as error_message,
  query
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE error_result IS NOT NULL
  AND creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
ORDER BY creation_time DESC
LIMIT 10

2. Check partition information

SELECT
  table_name,
  partition_id,
  total_rows,
  total_logical_bytes
FROM `project.dataset.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'YOUR_TABLE'
ORDER BY partition_id DESC
LIMIT 10
```

#### Output Example (JSON)

```json
[
  {
    "purpose": "Check recent job errors",
    "query": "SELECT job_id, creation_time..."
  },
  {
    "purpose": "Check partition information",
    "query": "SELECT table_name, partition_id..."
  }
]
```

#### Platforms

**BigQuery:**
- Recent job errors
- Partition information
- Query cost estimation
- Schema inspection

**PostgreSQL:**
- Active queries
- Table sizes
- Lock information
- Query plans

**Python:**
- Package listing
- Module inspection
- Verbose logging
- Python path

#### Use Cases

- Quick diagnostics
- Performance investigation
- Resource monitoring
- Debugging sessions
- Training and documentation

---

### report

Create comprehensive incident reports in multiple formats.

#### Synopsis

```bash
ai-debug report [<error_source>] [--format=<format>] [--output=<file>]
```

#### Description

Generates a complete incident report combining:
- Error analysis
- Root cause suggestions
- Fix recommendations
- Metadata and timestamps

Reports can be saved to files for documentation, tracking, or sharing.

#### Arguments

- `error_source` - Path to error file or `-` for stdin (optional, defaults to stdin)

#### Options

- `--format=<format>` - Output format: `markdown` (default), `json`, `text`
- `--output=<file>` - Output file path (defaults to stdout)

#### Examples

```bash
# Create markdown report
ai-debug report error.log

# Save to file
ai-debug report error.log --output=incident.md

# Plain text report
ai-debug report error.log --format=text

# JSON for tracking systems
ai-debug report error.log --format=json --output=incident.json

# From stdin
pytest tests/ 2>&1 | ai-debug report - --output=test-failure.md

# Dated incident reports
ai-debug report error.log --output="incidents/$(date +%Y%m%d-%H%M%S)-error.md"
```

#### Output Example (Markdown)

```markdown
# Incident Report

**Generated:** 2026-01-12 17:30:00

## Summary

**Error Type:** python
**Severity:** high

TypeError: unsupported operand type(s) for +: 'int' and 'str'

## Error Details

**Location:**
- File: `src/calculator.py`
- Line: 42

**Stack Trace:**
```
File "src/calculator.py", line 42, in add_values
return a + b
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

## Root Cause Analysis

1. **Incorrect type passed to function** (90% confidence)
   - Category: type_error

2. **Type annotation mismatch** (70% confidence)
   - Category: type_error

## Recommended Fixes

### Fix 1: type_handling

Fix type error or null handling

**Steps:**
1. Add type checking or validation
2. Handle None/null values explicitly
3. Add type hints (Python) or type guards (TypeScript)
4. Use defensive programming patterns

**Verification:** Run type checker and unit tests

## Keywords

TypeError, operand, type, unsupported

---
*Generated by ai-debug*
```

#### Output Example (JSON)

```json
{
  "timestamp": "2026-01-12T17:30:00.000000",
  "analysis": {
    "error_type": "python",
    "summary": "TypeError: unsupported operand type(s)",
    "severity": "high",
    "location": {...}
  },
  "root_causes": [...],
  "fixes": [...],
  "metadata": {
    "generator": "ai-debug",
    "version": "1.0.0"
  }
}
```

#### Report Formats

**Markdown:**
- Documentation-ready
- Wiki integration
- GitHub/GitLab issues
- Knowledge bases

**JSON:**
- Machine-readable
- Tracking systems
- Automation
- Data analysis

**Text:**
- Plain terminal output
- Email-friendly
- Log files
- Simple archiving

#### Use Cases

- Incident documentation
- Post-mortems
- Knowledge base building
- Team communication
- Compliance and auditing

---

## Use Cases

### CI/CD Integration

Automatically analyze test failures and create reports:

```bash
#!/bin/bash
# In CI pipeline

pytest tests/ 2>&1 | tee test_output.log

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo "Tests failed, generating incident report..."
    ai-debug report test_output.log \
        --format=markdown \
        --output=artifacts/test-failure-$(date +%Y%m%d-%H%M%S).md

    # Also create JSON for tracking
    ai-debug report test_output.log \
        --format=json \
        --output=artifacts/test-failure.json
fi
```

### Pre-commit Hook

Analyze errors before committing:

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run tests
if ! pytest tests/; then
    echo "Tests failed. Analyzing errors..."
    pytest tests/ 2>&1 | ai-debug analyze -
    pytest tests/ 2>&1 | ai-debug suggest - --depth=deep
    exit 1
fi
```

### Interactive Debugging Session

Complete debugging workflow:

```bash
# 1. Reproduce error and capture
python script.py 2>&1 | tee error.log

# 2. Analyze error
ai-debug analyze error.log

# 3. Get root cause suggestions
ai-debug suggest error.log --depth=deep

# 4. Search for similar issues
ERROR_MSG=$(ai-debug analyze error.log --format=json | jq -r '.summary')
ai-debug search "$ERROR_MSG"

# 5. Get fix recommendations
ai-debug fix error.log

# 6. Generate debug queries
ai-debug query "error context" --platform=python

# 7. Create incident report for documentation
ai-debug report error.log --output=incidents/$(date +%Y%m%d)-issue.md
```

### BigQuery Debugging

Debug BigQuery queries and jobs:

```bash
# Run query and capture errors
bq query --use_legacy_sql=false "
SELECT * FROM \`project.dataset.table\`
WHERE partition_date = '2026-01-12'
" 2>&1 | tee bq_error.log

# Analyze error
ai-debug analyze bq_error.log

# Get BigQuery-specific debug queries
ai-debug query "partition error" --platform=bigquery > debug.sql

# Execute debug queries
bq query < debug.sql
```

### Automated Monitoring

Monitor logs and alert on errors:

```bash
#!/bin/bash
# cron job: */5 * * * *

LOG_FILE="/var/log/application.log"
ALERT_FILE="/tmp/error_alert.txt"

# Check for new errors
tail -n 100 "$LOG_FILE" | grep -i error > "$ALERT_FILE"

if [ -s "$ALERT_FILE" ]; then
    # Analyze and send alert
    ANALYSIS=$(ai-debug analyze "$ALERT_FILE" --format=json)
    SEVERITY=$(echo "$ANALYSIS" | jq -r '.severity')

    if [ "$SEVERITY" = "high" ] || [ "$SEVERITY" = "critical" ]; then
        # Send alert with analysis
        ai-debug report "$ALERT_FILE" --format=markdown | \
            mail -s "Critical Error Detected" team@example.com
    fi
fi
```

## Advanced Usage

### Custom Error Sources

Feed errors from various sources:

```bash
# From application logs
tail -f /var/log/app.log | grep ERROR | ai-debug analyze -

# From systemd journal
journalctl -u myservice -n 100 | ai-debug analyze -

# From Docker logs
docker logs container_name 2>&1 | ai-debug analyze -

# From kubectl
kubectl logs pod_name | ai-debug analyze -
```

### Chaining Commands

Combine multiple commands for comprehensive analysis:

```bash
# Full analysis pipeline
ERROR_FILE="error.log"

# Analyze
ai-debug analyze "$ERROR_FILE" > analysis.txt

# Suggest with deep analysis
ai-debug suggest "$ERROR_FILE" --depth=deep > suggestions.txt

# Get fixes
ai-debug fix "$ERROR_FILE" > fixes.txt

# Search for similar issues
SUMMARY=$(ai-debug analyze "$ERROR_FILE" --format=json | jq -r '.summary')
ai-debug search "$SUMMARY" > similar-issues.txt

# Create comprehensive report
ai-debug report "$ERROR_FILE" --output=full-report.md
```

### JSON Processing

Process JSON output with jq:

```bash
# Get only high-confidence suggestions
ai-debug suggest error.log --format=json | \
    jq '[.[] | select(.confidence >= 0.7)]'

# Extract error location
ai-debug analyze error.log --format=json | \
    jq '.location | "\(.file):\(.line)"'

# Count errors by type
for log in *.log; do
    ai-debug analyze "$log" --format=json | jq -r '.error_type'
done | sort | uniq -c
```

### Integration with Beads

Link errors to issues:

```bash
# Analyze error and create bead
ERROR_SUMMARY=$(ai-debug analyze error.log --format=json | jq -r '.summary')

# Create bead with error info
bd create -t bug -p P1 \
    -d "$(ai-debug report error.log --format=markdown)" \
    -l "error,auto-detected" \
    "$ERROR_SUMMARY"

# Search existing beads for similar issues
ai-debug search "$ERROR_SUMMARY" --scope=beads
```

## Exit Codes

- `0` - Success
- `1` - General error (file not found, invalid input, etc.)
- `130` - Interrupted (Ctrl+C)

## Troubleshooting

### Common Issues

**Command not found:**
```bash
# Check if ai-debug is in PATH
which ai-debug

# Add to PATH if needed
export PATH="$PATH:/path/to/decentclaude/bin/debug-utils"
```

**Permission denied:**
```bash
# Make executable
chmod +x /path/to/decentclaude/bin/debug-utils/ai-debug
```

**Empty analysis:**
```bash
# Check input file exists and has content
cat error.log

# Verify input is being piped correctly
echo "Test error" | ai-debug analyze -
```

**bd search fails:**
```bash
# Verify beads is installed and working
bd --version

# Check if you're in a beads-enabled repository
bd status
```

**Git search fails:**
```bash
# Verify you're in a git repository
git status

# Check git log works
git log --oneline
```

### Debug Mode

For troubleshooting ai-debug itself:

```bash
# Run with Python in verbose mode
python3 -v /path/to/ai-debug analyze error.log

# Check for syntax errors
python3 -m py_compile /path/to/ai-debug
```

### Getting Help

```bash
# Show help
ai-debug --help

# Command-specific help
ai-debug analyze --help
ai-debug suggest --help
ai-debug fix --help
ai-debug search --help
ai-debug query --help
ai-debug report --help
```

## See Also

- [Debug Tools README](README.md) - Quick start guide
- [Data Utilities](../data-engineering/README.md) - BigQuery debugging tools
- [Beads Documentation](../beads/README.md) - Issue tracking
- [Git Workflow](../worktrees/README.md) - Version control tools
