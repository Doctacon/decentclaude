# Benchmark Quick Start Guide

Get started with performance benchmarking in 5 minutes.

## 1. Install Dependencies

```bash
cd /Users/crlough/gt/decentclaude/mayor/rig
pip install -r requirements-test.txt
```

This installs pytest-benchmark and all testing dependencies.

## 2. Run Your First Benchmark

```bash
# Run a single benchmark suite
pytest tests/benchmarks/test_bq_profile_benchmark.py --benchmark-only -v
```

You should see output like:

```
======================== benchmark: 10 tests ========================
Name (time in us)                          Min      Max     Mean
------------------------------------------------------------------
test_get_table_metadata_small           45.50   156.30    52.84
test_get_table_metadata_medium          89.20   234.10   102.35
...
```

## 3. Run All Benchmarks

```bash
# Run all benchmark suites
pytest tests/benchmarks/ --benchmark-only

# With verbose output
pytest tests/benchmarks/ --benchmark-only -v
```

## 4. Generate a Report

```bash
# Save results with auto-generated name
pytest tests/benchmarks/ --benchmark-only --benchmark-autosave

# Results are saved to .benchmarks/ directory
ls -la .benchmarks/
```

## 5. Compare Performance

```bash
# Save a baseline
pytest tests/benchmarks/ --benchmark-only --benchmark-save=baseline

# Make some code changes...

# Compare against baseline
pytest tests/benchmarks/ --benchmark-only --benchmark-compare=baseline

# Fail if performance degrades > 10%
pytest tests/benchmarks/ --benchmark-only --benchmark-compare=baseline --benchmark-compare-fail=mean:10%
```

## 6. View Results

```bash
# List all saved benchmarks
pytest-benchmark list

# Compare two benchmark runs
pytest-benchmark compare 0001 0002

# Generate histogram
pytest-benchmark compare 0001 0002 --histogram
```

## Common Commands

### Run Specific Benchmarks

```bash
# By utility
pytest tests/benchmarks/test_bq_profile_benchmark.py --benchmark-only

# By marker
pytest tests/benchmarks/ -m bq_profile --benchmark-only

# By test name pattern
pytest tests/benchmarks/ -k "small" --benchmark-only
```

### Export Results

```bash
# Export to JSON
pytest tests/benchmarks/ --benchmark-only --benchmark-json=results.json

# Export to CSV (requires py-cpuinfo)
pytest tests/benchmarks/ --benchmark-only --benchmark-json=results.json
python -c "import json; import csv; ..."
```

### Adjust Settings

```bash
# More rounds for accuracy
pytest tests/benchmarks/ --benchmark-only --benchmark-min-rounds=10

# Longer warmup
pytest tests/benchmarks/ --benchmark-only --benchmark-warmup-iterations=5

# Skip warmup (faster)
pytest tests/benchmarks/ --benchmark-only --benchmark-warmup=off
```

## Understanding Output

### Metrics Explained

- **Min/Max**: Fastest and slowest execution times
- **Mean**: Average execution time (most important)
- **StdDev**: Consistency (lower is better)
- **Median**: Middle value (less affected by outliers)
- **IQR**: Spread of middle 50% of data
- **Outliers**: Unusual measurements (system noise)
- **OPS**: Operations per second (higher is better)
- **Rounds**: How many times the test ran
- **Iterations**: Function calls per round

### Example Output

```
Name                                Min      Max     Mean   StdDev
-------------------------------------------------------------------
test_search_small_kb             8.30    42.10    10.25     2.15
test_search_medium_kb           45.20   123.40    52.80     8.90
test_search_large_kb           187.50   345.20   215.30    25.40
```

Interpretation:
- Small KB search: ~10ms average (excellent)
- Medium KB search: ~53ms average (good)
- Large KB search: ~215ms average (acceptable, meets target)
- StdDev < 15% of mean indicates consistent performance

## Performance Targets

Quick reference for expected performance:

| Utility | Operation | Target | Status |
|---------|-----------|--------|--------|
| bq-profile | Small table | < 100ms | Pass if mean < 100000us |
| bq-lineage | Simple parse | < 10ms | Pass if mean < 10000us |
| bq-explain | Parse plan | < 20ms | Pass if mean < 20000us |
| bq-schema-diff | Compare small | < 50ms | Pass if mean < 50000us |
| ai-generate | Build prompt | < 10ms | Pass if mean < 10000us |
| kb search | Search small KB | < 10ms | Pass if mean < 10000us |

## Troubleshooting

### Benchmarks are slow
- Close other applications
- Run: `pytest tests/benchmarks/ -k "small" --benchmark-only` for faster subset

### High variance (StdDev)
- System is busy, close apps
- Increase warmup: `--benchmark-warmup-iterations=10`

### Import errors
- Install dependencies: `pip install -r requirements-test.txt`
- Check Python path: `echo $PYTHONPATH`

### No benchmarks found
- Verify you're in project root: `cd /Users/crlough/gt/decentclaude/mayor/rig`
- Check test discovery: `pytest tests/benchmarks/ --collect-only`

## Next Steps

1. Review detailed README: `tests/benchmarks/README.md`
2. Examine individual benchmark files for examples
3. Create benchmarks for your own utilities
4. Set up CI/CD integration for automated tracking

## Tips

1. **Baseline early**: Save a baseline before making changes
2. **Run multiple times**: Compare 3+ runs to account for variance
3. **Watch for regressions**: Use `--benchmark-compare-fail` in CI
4. **Profile outliers**: Investigate tests with high StdDev
5. **Mock externals**: All external APIs should be mocked for consistency
