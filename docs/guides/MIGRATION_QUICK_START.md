# Migration Quick Start Guide

Fast-track guide for migrating from legacy BigQuery tools to DecentClaude utilities.

## 5-Minute Quick Start

### 1. Analyze Your Current Usage

```bash
cd mayor/rig/bin/migration-utils

# Scan your scripts directory
./analyze-legacy-usage.py \
  --scan-dir ../../../scripts/ \
  --output-report legacy-usage.html

# Open the report
open legacy-usage.html  # macOS
# or: xdg-open legacy-usage.html  # Linux
```

Review the report to see:
- How many scripts use legacy patterns
- Which scripts are highest priority to migrate
- Estimated effort and savings

### 2. Try Converting a Script

```bash
# Pick a high-priority script from the report
./convert-bq-script.py \
  --input ../../../scripts/your_script.sh \
  --suggest-utility

# Review suggestions, then convert
./convert-bq-script.py \
  --input ../../../scripts/your_script.sh \
  --output ../../../scripts/your_script_migrated.sh
```

### 3. Test the Migrated Script

```bash
# Run both and compare output
../../../scripts/your_script.sh arg1 > legacy_output.txt
../../../scripts/your_script_migrated.sh arg1 > migrated_output.txt

# Compare
diff legacy_output.txt migrated_output.txt
```

### 4. See Examples

```bash
# Check the example scripts
cd examples/

# Compare legacy vs migrated
cat legacy-profiler.sh
cat migrated-profiler.sh

# Try them (if you have a test table)
# ./legacy-profiler.sh project.dataset.test_table
# ./migrated-profiler.sh project.dataset.test_table
```

### 5. Generate Migration Plan

```bash
cd ..

# Create comprehensive assessment
./migration-report.py \
  --mode=assessment \
  --analysis legacy-usage.json \
  --output-report migration-plan.html

open migration-plan.html
```

## Common Migration Patterns

### Pattern 1: Table Profiling

**Before** (10+ bq commands, 2-5 minutes):
```bash
bq show project.dataset.table
bq query "SELECT COUNT(*) FROM project.dataset.table"
bq query "SELECT COUNT(DISTINCT user_id) FROM project.dataset.table"
# ... many more queries
```

**After** (1 command, 10-30 seconds):
```bash
bq-profile project.dataset.table
```

### Pattern 2: Cost Estimation

**Before**:
```bash
bq query --dry_run --format=json "SELECT ..." > dry_run.json
BYTES=$(cat dry_run.json | jq '.totalBytesProcessed')
COST=$(echo "$BYTES / 1099511627776 * 5" | bc)
```

**After**:
```bash
bq-query-cost --query "SELECT ..."
# or
bq-query-cost --file query.sql
```

### Pattern 3: Schema Comparison

**Before**:
```bash
bq show --schema dev.table > dev_schema.json
bq show --schema prod.table > prod_schema.json
diff dev_schema.json prod_schema.json
```

**After**:
```bash
bq-schema-diff dev.table prod.table
```

### Pattern 4: Query Optimization

**Before**:
```bash
# Run query, check console for stats
bq query "SELECT ..."
# Manually analyze execution plan
# Manually tweak query
# Repeat
```

**After**:
```bash
# Get cost estimate first
bq-query-cost --file query.sql

# See execution plan
bq-explain --file query.sql --dry-run

# Get optimization suggestions
bq-optimize --file query.sql

# Then run query
bq query < query.sql
```

## Migration Checklist

Use this for each script you migrate:

- [ ] Run analyze-legacy-usage.py to identify patterns
- [ ] Use convert-bq-script.py to generate migrated version
- [ ] Test both versions with same inputs
- [ ] Compare outputs (should be equivalent)
- [ ] Measure performance improvement
- [ ] Update any scripts that call the migrated script
- [ ] Update documentation
- [ ] Archive legacy script
- [ ] Mark migration as complete

## Quick Commands

```bash
# Analyze entire codebase
./analyze-legacy-usage.py --scan-dir . --output-report analysis.html

# Convert single script
./convert-bq-script.py --input script.sh --output script_new.sh

# Scan directory for conversion opportunities
./convert-bq-script.py --input scripts/ --scan-all --report report.html

# Generate migration plan
./migration-report.py --mode=assessment --output-report plan.html

# Track weekly progress
./migration-report.py --mode=progress --baseline baseline.json --output-report week1.html
```

## Get Help

- Full guide: [MIGRATION.md](./MIGRATION.md)
- Utilities README: [bin/migration-utils/README.md](../../bin/migration-utils/README.md)
- Examples: [bin/migration-utils/examples/](../../bin/migration-utils/examples/)
- Support: Slack #decentclaude-support

## Next Steps

1. Review the [full migration guide](./MIGRATION.md)
2. Schedule team workshop
3. Begin Phase 1 (read-only operations)
4. Track progress weekly
5. Celebrate wins!
