# Migration Utilities

Utilities to help migrate from legacy BigQuery tools to DecentClaude utilities.

## Overview

These utilities automate the analysis, conversion, and tracking of migrations from legacy tools (bq CLI, custom Python scripts, Great Expectations, etc.) to DecentClaude utilities.

## Utilities

### 1. analyze-legacy-usage.py

Analyzes existing BigQuery usage patterns to prioritize migration.

**Features**:
- Scans codebase for bq CLI commands
- Detects Python BigQuery client usage
- Identifies Great Expectations patterns
- Prioritizes migration candidates
- Generates HTML reports and JSON data

**Usage**:
```bash
# Scan a directory
./analyze-legacy-usage.py --scan-dir scripts/ --output-report legacy-analysis.html

# Scan multiple directories
./analyze-legacy-usage.py \
  --scan-dir scripts/ \
  --scan-dir airflow/dags/ \
  --output-json analysis.json \
  --output-report analysis.html

# Focus on specific file types
./analyze-legacy-usage.py \
  --scan-dir . \
  --extensions .py .sh \
  --output-report python-shell-analysis.html
```

**Output**:
- HTML report with prioritized migration candidates
- JSON file with detailed analysis data
- Console summary with top recommendations

### 2. convert-bq-script.py

Converts legacy bq CLI scripts to use DecentClaude utilities.

**Features**:
- Detects common bq CLI patterns
- Suggests appropriate DecentClaude utilities
- Can auto-convert simple scripts
- Generates migration comments
- Creates HTML conversion reports

**Usage**:
```bash
# Analyze a single script
./convert-bq-script.py --input legacy_profiler.sh --suggest-utility

# Convert a script
./convert-bq-script.py \
  --input scripts/legacy_profiler.sh \
  --output scripts/migrated_profiler.sh

# Scan entire directory
./convert-bq-script.py \
  --input scripts/ \
  --scan-all \
  --report conversion-report.html
```

**Conversions**:
- `bq query --dry_run` → `bq-query-cost`
- `bq show` → `bq-profile`
- `bq ls` → `bq-explore`
- Schema diffs → `bq-schema-diff`
- Manual cost calculations → `bq-query-cost`

### 3. migration-report.py

Generates comprehensive migration assessment and progress tracking reports.

**Features**:
- Initial migration assessment with effort estimates
- Cost savings projections
- Risk analysis
- Progress tracking against baseline
- Phase completion tracking
- Recommendations

**Usage**:
```bash
# Generate initial assessment
./migration-report.py \
  --mode=assessment \
  --output-report migration-assessment.html

# Include analysis data in assessment
./migration-report.py \
  --mode=assessment \
  --analysis legacy-analysis.json \
  --output-report assessment-with-data.html

# Track progress (run weekly)
./migration-report.py \
  --mode=progress \
  --baseline migration-baseline.json \
  --output-report week-2-progress.html

# Output JSON for automation
./migration-report.py \
  --mode=progress \
  --baseline baseline.json \
  --output-json progress.json \
  --output-report progress.html
```

## Typical Workflow

### Step 1: Baseline and Analysis

```bash
# Capture baseline metrics (before migration)
cat > capture-baseline.sh << 'EOF'
#!/bin/bash
OUTPUT="baseline-$(date +%Y%m%d).json"
cat > "$OUTPUT" << JSON
{
  "date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "legacy_scripts": $(find scripts/ -name "*.py" -o -name "*.sh" | wc -l),
  "monthly_query_costs": 500,
  "api_calls_per_day": 450,
  "profile_time_seconds": 30
}
JSON
echo "Baseline saved: $OUTPUT"
EOF

chmod +x capture-baseline.sh
./capture-baseline.sh

# Analyze legacy usage
./analyze-legacy-usage.py \
  --scan-dir scripts/ \
  --scan-dir airflow/dags/ \
  --output-json legacy-analysis.json \
  --output-report legacy-analysis.html
```

### Step 2: Generate Migration Plan

```bash
# Create comprehensive assessment
./migration-report.py \
  --mode=assessment \
  --analysis legacy-analysis.json \
  --output-json migration-plan.json \
  --output-report migration-plan.html

# Review migration-plan.html with team
# Adjust timeline and priorities as needed
```

### Step 3: Begin Migration

```bash
# Convert high-priority scripts
./convert-bq-script.py \
  --input scripts/daily_profiler.sh \
  --output scripts/daily_profiler_migrated.sh

# Scan all for conversion opportunities
./convert-bq-script.py \
  --input scripts/ \
  --scan-all \
  --report conversion-opportunities.html
```

### Step 4: Track Progress

```bash
# Weekly progress tracking
./migration-report.py \
  --mode=progress \
  --baseline baseline-20240113.json \
  --output-report progress-week-1.html

# Review progress report
# Adjust strategy based on recommendations
```

### Step 5: Validate and Iterate

```bash
# Re-analyze to track remaining work
./analyze-legacy-usage.py \
  --scan-dir scripts/ \
  --output-json current-analysis.json

# Compare with initial analysis
diff <(jq -S . legacy-analysis.json) <(jq -S . current-analysis.json)
```

## Integration with CI/CD

### Pre-commit Hook

Prevent new legacy patterns from being introduced:

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check for new bq CLI commands
if git diff --cached --diff-filter=A | grep -E "bq (query|show|ls)"; then
  echo "ERROR: New bq CLI commands detected"
  echo "Please use DecentClaude utilities instead:"
  echo "  bq query → bq-explain + bq-query-cost"
  echo "  bq show  → bq-profile"
  echo "  bq ls    → bq-explore"
  echo ""
  echo "See docs/guides/MIGRATION.md for details"
  exit 1
fi
```

### Pull Request Checks

```yaml
# .github/workflows/migration-check.yml
name: Migration Check
on: [pull_request]

jobs:
  check-legacy-usage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Check for legacy patterns
        run: |
          cd mayor/rig/bin/migration-utils
          ./analyze-legacy-usage.py \
            --scan-dir ../../.. \
            --output-json pr-analysis.json

          # Fail if new legacy patterns added
          LEGACY_COUNT=$(jq '.summary.files_with_bq_usage' pr-analysis.json)
          if [[ $LEGACY_COUNT -gt 0 ]]; then
            echo "Legacy BigQuery patterns found in PR"
            exit 1
          fi
```

## Output Examples

### Analysis Report

The HTML report includes:
- Executive summary with statistics
- Usage by category (bq CLI, Python, data quality, etc.)
- Top migration candidates with priorities
- Pattern statistics
- Recommended next steps

### Conversion Report

Shows for each script:
- Original bq commands
- Suggested DecentClaude utilities
- Converted code snippets
- Migration complexity estimate

### Assessment Report

Includes:
- Timeline and effort estimates
- Cost savings projections
- Migration phases with activities
- Risk assessment with mitigation
- Success metrics

### Progress Report

Tracks:
- Metrics comparison (baseline vs. current)
- Phase completion percentages
- Recommendations based on progress
- Areas needing attention

## Tips

### For Large Codebases

```bash
# Scan in batches to avoid memory issues
for dir in $(find . -type d -name "scripts" -o -name "dags"); do
  ./analyze-legacy-usage.py \
    --scan-dir "$dir" \
    --output-json "analysis-$(basename $dir).json"
done

# Combine results
jq -s 'reduce .[] as $item ({}; . * $item)' analysis-*.json > combined-analysis.json
```

### For Incremental Migration

```bash
# Focus on high-priority files only
./analyze-legacy-usage.py \
  --scan-dir scripts/critical/ \
  --output-report critical-migration.html

# Migrate in small batches
# Track progress weekly
# Adjust priorities based on feedback
```

### For Team Adoption

```bash
# Create simple cheat sheet from analysis
./analyze-legacy-usage.py --scan-dir scripts/ --output-json analysis.json

# Extract top 5 patterns
jq -r '.pattern_stats | to_entries | sort_by(.value) | reverse | .[0:5] | .[] | "\(.key): \(.value)"' analysis.json

# Share with team in daily standup
```

## Troubleshooting

### "No matches found"

- Check file extensions with `--extensions`
- Verify directory path is correct
- Ensure files contain actual bq usage

### "Conversion produces incorrect code"

- Use `--suggest-utility` mode first
- Manually verify complex conversions
- File issues for pattern improvements

### "Progress report shows no improvement"

- Verify baseline metrics are accurate
- Ensure utilities are actually being used
- Check that metrics collection is working

## Contributing

To add new conversion patterns:

1. Edit `convert-bq-script.py`
2. Add pattern to `_initialize_patterns()`
3. Implement converter method
4. Test with sample scripts
5. Update documentation

## See Also

- [Migration Guide](../../docs/guides/MIGRATION.md) - Comprehensive migration guide
- [Command Aliases](../aliases.sh) - Shortcut aliases for utilities
- [Setup Wizard](../setup-wizard.sh) - Initial setup script

## Support

- Issues: Create GitHub issue with `migration` label
- Questions: Slack #decentclaude-support
- Documentation: docs/guides/MIGRATION.md
