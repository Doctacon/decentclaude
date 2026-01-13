# Parallel Execution for BigQuery Utilities

This document describes the parallel execution capabilities added to BigQuery data utilities for improved performance on batch operations.

## Overview

Three BigQuery utilities now support parallel execution for batch operations:

1. **bq-profile** - Batch table profiling
2. **bq-schema-diff** - Batch schema comparison
3. **bq-table-compare** - Batch table comparison

## Features

- **Multiprocessing Pool**: Uses Python's `multiprocessing.Pool` for true parallelism
- **Progress Bars**: Optional rich library integration for visual progress tracking
- **Error Handling**: Graceful handling of partial failures (failed operations don't stop the batch)
- **Flexible Input**: Support for command-line arguments, files, and stdin
- **Aggregate Reports**: Consolidated reports with summary statistics

## Installation

Install the rich library for progress bar support:

```bash
pip install rich
```

The utilities will work without rich, but progress bars will be disabled.

## Usage Examples

### bq-profile

Profile multiple tables in parallel:

```bash
# Profile 4 tables with 4 workers
bq-profile --parallel 4 --progress \
  project.dataset.table1 \
  project.dataset.table2 \
  project.dataset.table3 \
  project.dataset.table4

# With JSON output
bq-profile --parallel 4 --format=json \
  table1 table2 table3 table4

# With anomaly detection
bq-profile --parallel 2 --detect-anomalies --progress \
  table1 table2
```

### bq-schema-diff

Compare multiple table pairs in parallel:

```bash
# Using command-line pairs (single pair)
bq-schema-diff project.dev.table project.prod.table

# Using stdin for multiple pairs
echo -e "dev.t1:prod.t1\ndev.t2:prod.t2\ndev.t3:prod.t3" | \
  bq-schema-diff --parallel 2 --progress

# Using a pairs file
cat > table_pairs.txt << EOF
project.dev.users:project.prod.users
project.dev.orders:project.prod.orders
project.dev.products:project.prod.products
EOF

bq-schema-diff --parallel 4 --pairs-file=table_pairs.txt --progress

# With JSON output
bq-schema-diff --parallel 4 --pairs-file=table_pairs.txt --format=json
```

### bq-table-compare

Compare multiple table pairs with detailed analysis:

```bash
# Using stdin for multiple pairs
echo -e "staging.t1:prod.t1\nstaging.t2:prod.t2" | \
  bq-table-compare --parallel 2 --progress --skip-stats

# Using a pairs file with full comparison
bq-table-compare --parallel 2 --pairs-file=table_pairs.txt

# Fast comparison (skip stats and samples)
bq-table-compare --parallel 4 --pairs-file=pairs.txt \
  --skip-stats --skip-samples --progress
```

## Input Methods

All three utilities support multiple input methods:

### 1. Command-Line Arguments

```bash
# Single operation
bq-schema-diff table_a table_b

# Multiple tables (bq-profile only)
bq-profile table1 table2 table3
```

### 2. Pairs File

Create a file with table pairs (one per line, format: `table_a:table_b`):

```bash
# table_pairs.txt
project.dev.users:project.prod.users
project.dev.orders:project.prod.orders
project.dev.products:project.prod.products
```

Use with:

```bash
bq-schema-diff --parallel 4 --pairs-file=table_pairs.txt
bq-table-compare --parallel 2 --pairs-file=table_pairs.txt
```

### 3. Standard Input (Pipe)

```bash
# From echo
echo -e "dev.t1:prod.t1\ndev.t2:prod.t2" | \
  bq-schema-diff --parallel 2

# From file
cat table_pairs.txt | bq-schema-diff --parallel 4 --progress

# From command substitution
bq list --format=json project:dataset | \
  jq -r '.[] | "\(.tableId):\(.tableId)"' | \
  bq-schema-diff --parallel 4
```

## Command-Line Options

### Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `--parallel N` | Number of parallel workers | 4 |
| `--progress` | Show progress bar (requires rich) | False |
| `--format` | Output format (text, json) | text |
| `--no-cache` | Disable metadata caching | False |

### bq-profile Specific

| Option | Description | Default |
|--------|-------------|---------|
| `--sample-size N` | Number of sample rows | 10 |
| `--detect-anomalies` | Enable anomaly detection | False |

### bq-table-compare Specific

| Option | Description | Default |
|--------|-------------|---------|
| `--sample-size N` | Number of sample rows | 100 |
| `--skip-stats` | Skip statistical comparisons | False |
| `--skip-samples` | Skip sample data comparison | False |

## Performance Tuning

### Optimal Worker Count

The optimal number of workers depends on several factors:

1. **CPU Cores**: Start with 2-4x your CPU core count
2. **Operation Complexity**:
   - Metadata-only operations: 8-16 workers
   - With statistics: 4-8 workers
   - With samples: 2-4 workers
3. **Network Bandwidth**: More workers = more concurrent API calls
4. **BigQuery Quota**: Monitor quota consumption

### Examples

```bash
# Light operations (schema comparison)
bq-schema-diff --parallel 8 --pairs-file=pairs.txt

# Medium operations (profiling without anomalies)
bq-profile --parallel 4 table1 table2 table3 table4

# Heavy operations (full table comparison)
bq-table-compare --parallel 2 --pairs-file=pairs.txt
```

### System Limits

The utilities automatically limit workers to `cpu_count() * 2`:

```bash
# On 4-core system, max workers = 8
bq-profile --parallel 16 table1 table2  # Limited to 8
```

## Output Formats

### Text Format (Default)

Provides a human-readable summary:

```
================================================================================
Batch Profile Summary
================================================================================

Results:
  Total tables: 4
  Successful: 4
  Failed: 0

================================================================================
```

### JSON Format

Provides structured data for programmatic processing:

```json
{
  "batch_summary": {
    "total_tables": 4,
    "successful": 4,
    "failed": 0,
    "timestamp": "2026-01-13T12:00:00Z"
  },
  "profiles": [
    {
      "table_id": "project.dataset.table1",
      "profile": { ... }
    }
  ],
  "errors": []
}
```

## Error Handling

Partial failures don't stop the batch:

```bash
# If table2 fails, table1, table3, and table4 are still processed
bq-profile --parallel 4 table1 table2 table3 table4

# Output shows which tables failed
Results:
  Total tables: 4
  Successful: 3
  Failed: 1

Failed tables:
  ✗ table2: Table not found
```

## Progress Tracking

With the `--progress` flag and rich library installed:

```bash
bq-profile --parallel 4 --progress table1 table2 table3 table4
```

Shows:

```
⠋ Profiling 4 tables ━━━━━━━━━━━━━━━━━━━━ 50% 0:00:10
✓ project.dataset.table1
✓ project.dataset.table2
```

## Performance Comparison

Expected speedup with parallel execution:

| Workers | Tables/Pairs | Speedup |
|---------|--------------|---------|
| 1 (sequential) | 4 | 1.0x (baseline) |
| 2 | 4 | 1.7-1.9x |
| 4 | 4 | 2.5-3.2x |
| 4 | 8 | 3.0-3.5x |

Actual speedup depends on:
- Network latency
- BigQuery backend load
- Operation complexity
- System resources

## Demo Script

Run the performance demo to see real-world improvements:

```bash
cd /Users/crlough/gt/decentclaude/mayor/rig/examples
python parallel_execution_demo.py
```

The demo compares sequential vs. parallel execution for all three utilities.

## Best Practices

1. **Start Small**: Test with 2-4 workers first
2. **Monitor Quota**: Watch BigQuery API quota consumption
3. **Use Progress Bars**: Enable `--progress` for long-running operations
4. **Handle Errors**: Review failed operations in the summary
5. **Choose Format**: Use JSON for programmatic processing, text for human review
6. **Cache Wisely**: Use `--no-cache` for fresh data, omit for faster execution

## Troubleshooting

### Progress Bar Not Showing

Install rich library:

```bash
pip install rich
```

### Worker Count Warning

If you see "Limiting workers to N (system max)", reduce `--parallel`:

```bash
# System has 4 cores (max 8 workers)
bq-profile --parallel 4 table1 table2  # OK
bq-profile --parallel 16 table1 table2  # Limited to 8
```

### API Quota Exceeded

Reduce parallel workers:

```bash
# Reduce from 8 to 2 workers
bq-profile --parallel 2 table1 table2 table3 table4
```

### Memory Issues

Reduce workers or disable caching:

```bash
bq-profile --parallel 2 --no-cache table1 table2
```

## Integration Examples

### CI/CD Pipeline

```bash
#!/bin/bash
# Compare dev and prod schemas in CI

# Generate pairs from all tables
bq ls --format=json project:dev_dataset | \
  jq -r '.[] | "project.dev_dataset.\(.tableId):project.prod_dataset.\(.tableId)"' | \
  bq-schema-diff --parallel 4 --format=json > schema_diff.json

# Check for differences
if [ $(jq '.batch_summary.different' schema_diff.json) -gt 0 ]; then
  echo "Schema differences detected!"
  exit 1
fi
```

### Data Quality Monitoring

```bash
#!/bin/bash
# Profile all tables in a dataset

DATASET="project.analytics"

# Get all tables
TABLES=$(bq ls --format=json $DATASET | jq -r '.[].tableId' | \
  sed "s|^|$DATASET.|")

# Profile in parallel
echo "$TABLES" | tr ' ' '\n' | \
  xargs -n 1 echo | \
  bq-profile --parallel 8 --progress --format=json > profiles.json
```

### Schema Migration Validation

```bash
#!/bin/bash
# Validate schema migration

# Read migration pairs from file
cat migration_pairs.txt | \
  bq-schema-diff --parallel 4 --progress --format=json > migration_report.json

# Email report
jq '.comparisons[] | select(.identical == false)' migration_report.json | \
  mail -s "Schema Migration Report" team@example.com
```

## See Also

- [bq-profile documentation](../bin/data-utils/bq-profile)
- [bq-schema-diff documentation](../bin/data-utils/bq-schema-diff)
- [bq-table-compare documentation](../bin/data-utils/bq-table-compare)
- [Performance demo script](./parallel_execution_demo.py)
