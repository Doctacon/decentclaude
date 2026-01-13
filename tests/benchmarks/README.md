# Performance Benchmarks for Decentclaude Utilities

This directory contains comprehensive performance benchmarks for decentclaude CLI utilities using pytest-benchmark. Benchmarks measure pure code performance with mocked external API calls (BigQuery, OpenAI) to isolate and measure algorithmic efficiency.

## Overview

The benchmark suite covers the following utilities:

1. **bq-profile** - Table profiling and metadata extraction
2. **bq-lineage** - Dependency discovery and lineage tracking
3. **bq-explain** - Query execution plan analysis
4. **bq-schema-diff** - Schema comparison
5. **ai-generate** - AI-powered code generation
6. **kb search** - Knowledge base search operations

## Installation

Install the required benchmarking dependencies:

```bash
pip install pytest-benchmark
pip install -r requirements-test.txt
```

## Running Benchmarks

### Run All Benchmarks

```bash
# Run all benchmarks
pytest tests/benchmarks/ --benchmark-only

# Run with verbose output
pytest tests/benchmarks/ --benchmark-only -v
```

### Run Specific Benchmark Suites

```bash
# Run only bq-profile benchmarks
pytest tests/benchmarks/test_bq_profile_benchmark.py --benchmark-only

# Run only kb search benchmarks
pytest tests/benchmarks/test_kb_search_benchmark.py --benchmark-only

# Run benchmarks for a specific utility
pytest tests/benchmarks/ -m bq_profile --benchmark-only
```

### Run with Different Dataset Sizes

Benchmarks automatically test with small, medium, and large datasets. Filter by test name:

```bash
# Run only small dataset benchmarks
pytest tests/benchmarks/ -k "small" --benchmark-only

# Run only large dataset benchmarks
pytest tests/benchmarks/ -k "large" --benchmark-only
```

## Generating Reports

### Save Benchmark Results

```bash
# Auto-save results with timestamp
pytest tests/benchmarks/ --benchmark-only --benchmark-autosave

# Save with custom name
pytest tests/benchmarks/ --benchmark-only --benchmark-save=baseline

# Save data for later comparison
pytest tests/benchmarks/ --benchmark-only --benchmark-save-data
```

### Generate HTML Reports

```bash
# Generate HTML report
pytest tests/benchmarks/ --benchmark-only --benchmark-autosave

# View saved benchmarks
pytest-benchmark list

# Compare with previous results
pytest tests/benchmarks/ --benchmark-only --benchmark-compare=0001
pytest tests/benchmarks/ --benchmark-only --benchmark-compare-fail=mean:10%
```

### Export Results

```bash
# Export to JSON
pytest tests/benchmarks/ --benchmark-only --benchmark-json=results.json

# Export with machine info
pytest tests/benchmarks/ --benchmark-only --benchmark-json=results.json --benchmark-save-data
```

## Interpreting Results

### Key Metrics

Benchmark output includes the following metrics:

- **Min**: Minimum execution time across all rounds
- **Max**: Maximum execution time across all rounds
- **Mean**: Average execution time
- **StdDev**: Standard deviation (consistency of performance)
- **Median**: Middle value of all measurements
- **IQR**: Interquartile range (spread of middle 50% of data)
- **Outliers**: Number of outlier measurements
- **Rounds**: Number of times the benchmark was run
- **Iterations**: Number of function calls per round

### Example Output

```
-------------------------------------------------------------------------------------- benchmark: 6 tests --------------------------------------------------------------------------------------
Name (time in us)                                  Min                 Max                Mean            StdDev              Median               IQR            Outliers       OPS            Rounds  Iterations
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
test_get_table_metadata_small                   45.5000 (1.0)      156.3000 (1.0)       52.8421 (1.0)      8.9234 (1.0)       50.2000 (1.0)      4.4250 (1.0)          19;25  18,924.3095 (1.0)         173           1
test_parse_column_statistics_small              87.3000 (1.92)     201.5000 (1.29)      95.6789 (1.81)    11.2345 (1.26)      93.1000 (1.85)     6.7500 (1.53)         12;18  10,451.6234 (0.55)        148           1
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

### Performance Targets

#### bq-profile
- **Small tables (10 columns)**: < 100ms per operation
- **Medium tables (50 columns)**: < 500ms per operation
- **Large tables (200 columns)**: < 2s per operation
- **Batch profiling (10 tables)**: < 5s total

#### bq-lineage
- **Simple view parsing**: < 10ms
- **Complex query parsing**: < 50ms
- **Depth 1 dependencies**: < 100ms
- **Depth 2 dependencies**: < 500ms
- **Dependency graph (50 tables)**: < 1s

#### bq-explain
- **Parse simple plan (3 stages)**: < 20ms
- **Parse complex plan (20 stages)**: < 100ms
- **Performance analysis**: < 50ms
- **Cost calculation**: < 10ms

#### bq-schema-diff
- **Small schema comparison (20 columns)**: < 50ms
- **Medium schema comparison (50 columns)**: < 100ms
- **Large schema comparison (200 columns)**: < 500ms
- **Nested schema comparison**: < 200ms
- **Batch comparison (10 pairs)**: < 2s

#### ai-generate
- **Build system prompt**: < 5ms
- **Build user prompt**: < 10ms
- **Parse requirements**: < 20ms
- **Format code**: < 15ms
- **Mocked API call**: < 5ms

#### kb search
- **Search small KB (10 articles)**: < 10ms
- **Search medium KB (100 articles)**: < 50ms
- **Search large KB (1000 articles)**: < 200ms
- **Full-text search with filters**: < 300ms
- **Article retrieval by ID**: < 5ms
- **Add article**: < 20ms

## Benchmark Markers

Use markers to run specific benchmark categories:

```bash
# Run all BigQuery benchmarks
pytest tests/benchmarks/ -m "bq_profile or bq_lineage or bq_explain or bq_schema_diff" --benchmark-only

# Run all AI benchmarks
pytest tests/benchmarks/ -m ai_generate --benchmark-only

# Run all KB benchmarks
pytest tests/benchmarks/ -m kb_search --benchmark-only
```

Available markers:
- `benchmark` - All benchmark tests
- `bq_profile` - bq-profile utility benchmarks
- `bq_lineage` - bq-lineage utility benchmarks
- `bq_explain` - bq-explain utility benchmarks
- `bq_schema_diff` - bq-schema-diff utility benchmarks
- `ai_generate` - ai-generate utility benchmarks
- `kb_search` - kb search benchmarks

## Comparing Benchmarks

### Compare Against Baseline

```bash
# Save baseline
pytest tests/benchmarks/ --benchmark-only --benchmark-save=baseline

# Run optimized code and compare
pytest tests/benchmarks/ --benchmark-only --benchmark-compare=baseline

# Fail if performance degrades by more than 10%
pytest tests/benchmarks/ --benchmark-only --benchmark-compare=baseline --benchmark-compare-fail=mean:10%
```

### Compare Multiple Runs

```bash
# List all saved benchmarks
pytest-benchmark list

# Compare two specific runs
pytest-benchmark compare 0001 0002

# Generate comparison histogram
pytest-benchmark compare 0001 0002 --histogram
```

## Configuration

Benchmark configuration is defined in:
- `tests/benchmarks/conftest.py` - Shared fixtures and test data generators
- `pytest.ini` - pytest-benchmark settings

### Custom Configuration

You can override benchmark settings:

```bash
# Adjust warmup iterations
pytest tests/benchmarks/ --benchmark-only --benchmark-warmup-iterations=5

# Adjust number of rounds
pytest tests/benchmarks/ --benchmark-only --benchmark-min-rounds=10

# Disable garbage collection during benchmarks (default: enabled)
pytest tests/benchmarks/ --benchmark-only --benchmark-disable-gc

# Set maximum time per benchmark
pytest tests/benchmarks/ --benchmark-only --benchmark-max-time=5.0
```

## Best Practices

1. **Consistency**: Run benchmarks on a quiet system with minimal background processes
2. **Multiple Runs**: Compare results across multiple runs to account for variance
3. **Baseline**: Establish baseline performance before making optimizations
4. **Isolation**: Benchmarks mock external dependencies to measure pure code performance
5. **Real Data**: Use realistic data sizes that reflect production scenarios
6. **Documentation**: Document any performance regressions or improvements

## Continuous Integration

To integrate benchmarks into CI/CD:

```yaml
# Example GitHub Actions workflow
- name: Run Performance Benchmarks
  run: |
    pytest tests/benchmarks/ --benchmark-only --benchmark-json=benchmark.json

- name: Compare with Baseline
  run: |
    pytest tests/benchmarks/ --benchmark-only --benchmark-compare=baseline --benchmark-compare-fail=mean:15%
```

## Troubleshooting

### Benchmarks Running Slowly

If benchmarks take too long:
- Reduce the number of rounds: `--benchmark-min-rounds=5`
- Skip warmup: `--benchmark-warmup=off`
- Run specific tests instead of the full suite

### High Variance in Results

If results have high standard deviation:
- Close other applications
- Run on a dedicated benchmark machine
- Increase warmup iterations: `--benchmark-warmup-iterations=10`
- Check for background processes affecting performance

### Mocked APIs Not Working

If mocks aren't being used:
- Check that fixtures are properly imported in conftest.py
- Verify mock patches are applied correctly
- Use `-v` flag to see which fixtures are active

## Contributing

When adding new benchmarks:

1. Create benchmark tests in appropriate file (e.g., `test_new_utility_benchmark.py`)
2. Use consistent naming: `test_<operation>_<size>_<variant>`
3. Add appropriate markers
4. Document performance targets
5. Use shared fixtures from `conftest.py`
6. Test with small, medium, and large datasets

## Resources

- [pytest-benchmark documentation](https://pytest-benchmark.readthedocs.io/)
- [Writing effective benchmarks](https://pytest-benchmark.readthedocs.io/en/latest/usage.html)
- [Comparing benchmarks](https://pytest-benchmark.readthedocs.io/en/latest/comparing.html)
