# Test Coverage Summary

Comprehensive test suite for all CLI utilities with 164 total tests achieving 100% utility coverage.

## Quick Start

```bash
# Install test dependencies
make install

# Run all tests
make test

# Run with coverage report
make coverage

# Run bash tests
make test-bats
```

## Test Statistics

### Overall Coverage
- **Total Tests:** 164
  - Python tests (pytest): 112
  - Bash tests (bats): 52
- **Utilities Covered:** 13/13 (100%)
  - Python utilities: 5/5
  - Bash utilities: 8/8
- **Code Coverage Target:** 80%+ (configured in pytest.ini)

### Detailed Test Counts

#### Python Unit Tests (112 tests)
- `test_data_quality.py`: 32 tests
  - DataQualityCheck base class
  - SQLFileExistsCheck
  - SQLSyntaxCheck
  - ConfigFileCheck
  - NoHardcodedSecretsCheck
  - run_all_checks() orchestration
  - main() entry point

- `test_bq_schema_diff.py`: 22 tests
  - get_table_schema() with various field types
  - compare_schemas() with all difference types
  - print_text_report() formatting
  - print_json_report() formatting
  - main() integration
  - Exit code handling

- `test_bq_query_cost.py`: 33 tests
  - format_bytes() all units (B → EB)
  - get_cost_category() all categories
  - estimate_query_cost() various sizes
  - print_text_report() formatting
  - print_json_report() formatting
  - main() with file and inline queries
  - Error handling

- `test_bq_partition_lineage.py`: 15 tests
  - Partition info for all table types
  - Time and range partitioning
  - Clustering fields
  - Upstream dependencies
  - Downstream dependencies
  - Lineage chain analysis

#### Integration Tests (10 tests)
- `test_bq_integration.py`: 10 tests
  - Schema diff workflows
  - Query cost estimation workflows
  - Partition analysis workflows
  - Lineage exploration workflows
  - Multi-utility workflows
  - Error recovery
  - API error handling

#### Bash Tests (52 tests)
- `test_git_hooks.bats`: 16 tests
  - pre-commit hook validation
  - post-checkout hook validation
  - post-merge hook validation
  - install-hooks.sh functionality
  - Shebang validation
  - Error handling
  - Worktree state management

- `test_worktree_utils.bats`: 36 tests
  - wt-switch functionality
  - wt-status with verbose and dirty-only modes
  - wt-clean with dry-run, merged, gone, force options
  - wt-sync with prune-merged option
  - Help options for all utilities
  - Color-coded output
  - Summary reporting
  - Error handling

## Test Infrastructure

### Files Created
```
tests/
├── README.md                           # Test suite documentation
├── conftest.py                         # Shared pytest fixtures
├── verify_test_coverage.sh            # Coverage verification script
├── unit/                               # Unit tests
│   ├── test_data_quality.py
│   ├── test_bq_schema_diff.py
│   ├── test_bq_query_cost.py
│   └── test_bq_partition_lineage.py
├── integration/                        # Integration tests
│   └── test_bq_integration.py
└── bats/                               # Bash tests
    ├── test_git_hooks.bats
    └── test_worktree_utils.bats

requirements-test.txt                   # Test dependencies
pytest.ini                              # Pytest configuration
Makefile                                # Test runner commands
```

### Configuration Files

#### pytest.ini
- Test discovery patterns
- Coverage requirements (80% minimum)
- Test markers (unit, integration, slow, bq, hooks, worktree)
- Output formatting
- 2-minute default timeout

#### conftest.py Fixtures
- File system fixtures (temp_dir, temp_sql_file, temp_config_file)
- BigQuery mocking fixtures (mock_bigquery_client, mock_table, mock_schema)
- Partitioned and clustered table fixtures
- View with dependencies fixture
- SQL content fixtures (valid/invalid/with secrets)
- Git repository fixtures
- Environment fixtures (clean_env, mock_gcp_env)

#### requirements-test.txt
- pytest >= 7.4.0
- pytest-cov >= 4.1.0
- pytest-mock >= 3.11.0
- pytest-timeout >= 2.1.0
- google-cloud-bigquery >= 3.11.0
- sqlparse >= 0.4.4
- coverage[toml] >= 7.3.0
- mock >= 5.1.0
- freezegun >= 1.2.2

## Utilities Tested

### Python Utilities (5)

1. **data_quality.py** (scripts/)
   - 5 check classes + orchestration
   - 32 tests covering all checks
   - Edge cases and error handling

2. **bq-schema-diff** (bin/data-utils/)
   - Schema comparison functionality
   - 22 tests for all schema variations
   - Text and JSON output formats

3. **bq-query-cost** (bin/data-utils/)
   - Cost estimation with dry run
   - 33 tests for all byte ranges
   - Cost categorization

4. **bq-partition-info** (bin/data-utils/)
   - Partition analysis
   - 15 tests for partitioned/clustered tables
   - TIME and RANGE partitioning

5. **bq-lineage** (bin/data-utils/)
   - Lineage exploration
   - 15 tests for upstream/downstream
   - View dependency parsing

### Bash Utilities (8)

6. **install-hooks.sh** (.git-hooks/)
   - Hook installation
   - Local and global modes

7. **pre-commit** (.git-hooks/)
   - Shared branch detection
   - Timestamp management

8. **post-checkout** (.git-hooks/)
   - Branch checkout handling
   - Duplicate detection

9. **post-merge** (.git-hooks/)
   - Merge event handling
   - Worktree notification

10. **wt-switch** (bin/worktree-utils/)
    - Worktree switching
    - List functionality

11. **wt-status** (bin/worktree-utils/)
    - Status display
    - Verbose and dirty-only modes

12. **wt-clean** (bin/worktree-utils/)
    - Worktree cleanup
    - Merged/gone branch removal

13. **wt-sync** (bin/worktree-utils/)
    - Worktree synchronization
    - Fetch and prune

## Test Types

### Unit Tests
- Test individual functions and classes
- Mock external dependencies (BigQuery, file system)
- Fast execution (< 1 second per test)
- Marker: `@pytest.mark.unit`

### Integration Tests
- Test interactions between components
- Use mocked BigQuery client
- Test complete workflows
- Marker: `@pytest.mark.integration`

### Bash Tests
- Test shell script functionality
- Validate script structure
- Check for required patterns
- Use bats-core framework

## Running Tests

### All Tests
```bash
make test              # Python tests only
make test-bats         # Bash tests only
./tests/verify_test_coverage.sh  # Verify coverage without running
```

### Specific Test Types
```bash
pytest -m unit         # Unit tests only
pytest -m integration  # Integration tests only
pytest -m bq           # BigQuery-related tests only
pytest -m hooks        # Git hooks tests only
```

### With Coverage
```bash
make coverage          # Generate HTML coverage report
# View report: open htmlcov/index.html
```

### Specific Files
```bash
pytest tests/unit/test_data_quality.py -v
pytest tests/unit/test_bq_schema_diff.py::test_compare_schemas_identical
bats tests/bats/test_git_hooks.bats
```

## Coverage Goals

### Target: 80%+ Code Coverage
- All Python utilities in `scripts/` and `bin/`
- Measured using pytest-cov with branch coverage
- Enforced in pytest.ini with `--cov-fail-under=80`

### Coverage Reports
- **Terminal:** Displays missing lines
- **HTML:** Detailed report in `htmlcov/`
- **XML:** Machine-readable format for CI/CD

## CI/CD Integration

Tests are designed for CI/CD pipelines:
- Exit codes indicate pass/fail
- JSON output available for parsing
- Coverage threshold enforcement
- No interactive prompts
- Fast execution (< 5 minutes for full suite)

## Test Markers

Use markers to organize and run specific test subsets:
- `unit` - Unit tests for individual components
- `integration` - Integration tests with dependencies
- `slow` - Tests that take longer to run
- `bq` - Tests requiring BigQuery client
- `hooks` - Git hooks tests
- `worktree` - Worktree utilities tests

## Maintenance

### Adding New Tests
1. Create test file in appropriate directory
2. Name file `test_<module>.py` or `test_<feature>.bats`
3. Use fixtures from `conftest.py`
4. Add appropriate markers
5. Update this summary

### Running Before Commit
```bash
make test && make test-bats
```

### Troubleshooting
- **Import errors:** Check Python path in test files
- **Fixture not found:** Check `conftest.py`
- **Coverage too low:** Add tests for uncovered code paths
- **Bats not found:** Install with `brew install bats-core`

## Dependencies

### Python
- pytest ecosystem (pytest, pytest-cov, pytest-mock, pytest-timeout)
- google-cloud-bigquery for BigQuery mocking
- sqlparse for SQL validation testing
- mock and freezegun for advanced mocking

### Bash
- bats-core for bash testing
- Standard Unix tools (git, bash 4+)

## Success Metrics

✓ 164 total tests
✓ 100% utility coverage (13/13)
✓ 80%+ code coverage target
✓ All major code paths tested
✓ Error handling validated
✓ Integration workflows tested
✓ CI/CD ready
