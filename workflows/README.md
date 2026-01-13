# Workflow Orchestration Templates

Pre-built executable workflows that combine DecentClaude utilities and Skills to automate complex multi-step processes.

## Available Workflows

### 1. data-quality-audit

Comprehensive data quality assessment for BigQuery tables.

**Usage:**
```bash
./workflows/data-quality-audit <table_id> [quality_threshold]
```

**What it does:**
1. Profiles the table with `bq-profile --detect-anomalies`
2. Analyzes data quality metrics (null %, distinctness, anomalies)
3. Calculates quality score (0-100)
4. Generates recommendations for improvements
5. Returns PASS/FAIL based on threshold

**Example:**
```bash
./workflows/data-quality-audit myproject.analytics.users 85
```

**Output:**
- JSON profile report with quality metrics
- Quality score and PASS/FAIL status
- Recommendations for data quality improvements

---

### 2. incident-response

Automated incident triage, debugging, and post-mortem generation.

**Usage:**
```bash
./workflows/incident-response "<incident_description>" [severity]
```

**What it does:**
1. Initial triage (severity assessment, SLA determination)
2. Context gathering (logs, deployments, monitoring)
3. Hypothesis formation (root cause analysis framework)
4. Mitigation guidance (immediate actions to restore service)
5. Root cause analysis documentation
6. Action item generation (immediate, short-term, long-term)

**Example:**
```bash
./workflows/incident-response "Dashboard query timeout" P1
```

**Output:**
- `incident-report.md` - Complete incident documentation
- `timeline.jsonl` - Event timeline for debugging
- `action-items.md` - Follow-up tasks organized by priority

---

### 3. schema-migration

Safe BigQuery schema change workflow with validation and rollback.

**Usage:**
```bash
# Dry run (compare only)
./workflows/schema-migration <source_table> <target_table>

# Execute migration
./workflows/schema-migration <source_table> <target_table> --execute
```

**What it does:**
1. Compares schemas using `bq-schema-diff`
2. Checks compatibility (SAFE, BREAKING, REVIEW_REQUIRED)
3. Generates migration SQL (ALTER TABLE statements)
4. Generates rollback SQL for safety
5. Optionally executes migration (only if safe)

**Example:**
```bash
# Compare dev and prod schemas
./workflows/schema-migration myproject.dev.users myproject.prod.users

# Execute safe migration
./workflows/schema-migration myproject.dev.users myproject.prod.users --execute
```

**Output:**
- `migration-report.md` - Complete migration plan
- `migration.sql` - SQL to apply changes
- `rollback.sql` - SQL to undo changes
- Exit code 0 (safe) or 1 (breaking changes detected)

---

### 4. query-optimization

Systematic BigQuery query performance and cost optimization.

**Usage:**
```bash
./workflows/query-optimization <query_file> [cost_threshold_usd]
```

**What it does:**
1. Analyzes original query with `bq-explain`
2. Identifies optimization opportunities
3. Generates optimized query with `bq-optimize`
4. Analyzes optimized query for cost comparison
5. Calculates cost savings and validates against threshold

**Example:**
```bash
./workflows/query-optimization queries/dashboard.sql 0.50
```

**Output:**
- `optimization-report.md` - Before/after comparison
- `original.sql` - Original query for reference
- `optimized.sql` - Optimized query ready to deploy
- Cost savings percentage and recommendations

---

## Integration with CI/CD

All workflows are designed for CI/CD integration. They:
- Return exit code 0 for success, 1 for failure
- Support JSON/structured output for parsing
- Generate reports in markdown for documentation
- Can be run in automated pipelines

### GitHub Actions Example

```yaml
name: Data Quality Check
on: [pull_request]
jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Data Quality Audit
        run: |
          ./workflows/data-quality-audit myproject.dataset.table 80
        env:
          GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GCP_KEY }}
```

### GitLab CI Example

```yaml
data-quality:
  script:
    - ./workflows/data-quality-audit $TABLE_ID 85
  only:
    - merge_requests
```

---

## Customization

All workflows are bash scripts that can be easily customized:

1. **Add custom checks:** Edit the workflow script to add validation logic
2. **Change thresholds:** Modify default values at top of script
3. **Integrate tools:** Add calls to your own utilities
4. **Customize output:** Modify report templates

Example customization:
```bash
# Edit workflows/data-quality-audit
# Change default threshold from 80 to 90
THRESHOLD="${2:-90}"  # Changed from 80

# Add custom check
if (( $(echo "$DISTINCT_RATIO < 0.5" | bc -l) )); then
    RECOMMENDATIONS+=("Custom check: Consider indexing frequently queried columns")
fi
```

---

## Observability Integration

All workflows integrate with the DecentClaude observability framework:

- **Metrics:** Workflow execution time, success/failure rates
- **Logging:** Structured logs for debugging
- **Tracing:** Correlation IDs for tracking across tools
- **Errors:** Automatic error capture to Sentry

Enable observability:
```bash
export METRICS_ENABLED=true
export LOG_FORMAT=json
export SENTRY_ENABLED=true
```

---

## Combining Workflows

Workflows can be chained for complex automation:

```bash
#!/bin/bash
# Deploy pipeline with validation

# 1. Schema migration
if ./workflows/schema-migration dev.table prod.table --execute; then
    echo "Schema migration successful"
else
    echo "Schema migration failed - aborting"
    exit 1
fi

# 2. Data quality check
if ./workflows/data-quality-audit prod.table 85; then
    echo "Data quality check passed"
else
    echo "Data quality issues detected - rolling back"
    # Rollback logic here
    exit 1
fi

# 3. Query optimization
./workflows/query-optimization queries/dashboard.sql 1.00
```

---

## Troubleshooting

### Workflow fails with "command not found"

Ensure utilities are in PATH or use absolute paths:
```bash
BIN_DIR="$(pwd)/bin/data-utils"
"$BIN_DIR/bq-profile" ...
```

### Workflow fails with "Permission denied"

Make scripts executable:
```bash
chmod +x workflows/*
```

### Workflow produces no output

Check that required environment variables are set:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
export GOOGLE_CLOUD_PROJECT=your-project
```

---

## Best Practices

1. **Test in non-production first:** Always test workflows against dev/staging before production
2. **Version control workflow configs:** Store workflow scripts and configs in git
3. **Monitor execution:** Track workflow success rates and execution times
4. **Document customizations:** Comment any changes you make to workflows
5. **Use idempotent operations:** Design workflows to be safely re-runnable

---

## Adding New Workflows

Create a new workflow following this template:

```bash
#!/usr/bin/env bash
#
# my-workflow - Brief description
#
# Usage and documentation here
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/../bin/data-utils"

# Your workflow logic here

# Exit with appropriate code
exit 0
```

Then:
1. Make it executable: `chmod +x workflows/my-workflow`
2. Test it thoroughly
3. Document it in this README
4. Add CI/CD examples if applicable

---

## Support

For issues or questions:
- Check the troubleshooting section above
- Review individual workflow documentation (comment blocks in scripts)
- See `docs/guides/WORKFLOWS_TUTORIAL.md` for detailed examples
- File an issue in the repository

---

*Part of DecentClaude - World-class data engineering with Claude Code*
