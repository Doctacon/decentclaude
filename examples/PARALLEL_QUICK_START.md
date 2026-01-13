# Parallel Execution Quick Start

Quick reference for using parallel execution in BigQuery utilities.

## Installation

```bash
pip install rich
```

## Quick Examples

### Profile Multiple Tables

```bash
# Basic parallel profiling
bq-profile --parallel 4 table1 table2 table3 table4

# With progress bar
bq-profile --parallel 4 --progress table1 table2 table3

# With JSON output
bq-profile --parallel 4 --format=json table1 table2 > profiles.json
```

### Compare Schemas

```bash
# Multiple pairs from stdin
echo -e "dev.t1:prod.t1\ndev.t2:prod.t2" | bq-schema-diff --parallel 2 --progress

# From file
cat pairs.txt | bq-schema-diff --parallel 4

# Create pairs file
cat > pairs.txt << EOF
project.dev.users:project.prod.users
project.dev.orders:project.prod.orders
EOF

bq-schema-diff --pairs-file=pairs.txt --parallel 2
```

### Compare Tables

```bash
# Fast comparison (skip stats/samples)
echo -e "staging.t1:prod.t1\nstaging.t2:prod.t2" | \
  bq-table-compare --parallel 2 --skip-stats --skip-samples --progress

# Full comparison from file
bq-table-compare --pairs-file=pairs.txt --parallel 2
```

## Common Patterns

### Generate Table List

```bash
# List all tables in dataset
bq ls --format=json project:dataset | \
  jq -r '.[] | "project.dataset.\(.tableId)"' > tables.txt

# Profile them all
cat tables.txt | xargs bq-profile --parallel 4 --progress
```

### Compare Dev to Prod

```bash
# Generate comparison pairs
bq ls --format=json project:dev_dataset | \
  jq -r '.[] | "project.dev_dataset.\(.tableId):project.prod_dataset.\(.tableId)"' | \
  bq-schema-diff --parallel 4 --progress
```

### Batch Processing

```bash
# Process 100 tables with 8 workers
seq 1 100 | xargs -I {} echo "project.dataset.table_{}" | \
  xargs bq-profile --parallel 8 --progress
```

## Performance Tips

| Operation Type | Recommended Workers |
|---------------|---------------------|
| Schema comparison | 8-16 |
| Profile (no anomalies) | 4-8 |
| Profile (with anomalies) | 2-4 |
| Full table comparison | 2-4 |

## Error Handling

Partial failures don't stop the batch:

```bash
# Even if table2 fails, others complete
bq-profile --parallel 4 table1 table2 table3 table4

# Check results
✓ table1
✗ table2: Table not found
✓ table3
✓ table4
```

## Output Formats

```bash
# Human-readable
bq-profile --parallel 4 table1 table2

# JSON for scripts
bq-profile --parallel 4 --format=json table1 table2 > output.json

# Extract failed tables
jq -r '.errors[].table_id' output.json
```

## Full Documentation

See [PARALLEL_EXECUTION.md](./PARALLEL_EXECUTION.md) for complete documentation.

## Demo

```bash
python examples/parallel_execution_demo.py
```
