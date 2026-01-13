# CLI Utilities Test Suite

Comprehensive test coverage for all CLI utilities including Python scripts, BigQuery utilities, git hooks, and worktree utilities.

## Test Structure

```
tests/
├── conftest.py              # Shared pytest fixtures
├── unit/                    # Unit tests for individual components
│   ├── test_data_quality.py
│   ├── test_bq_schema_diff.py
│   ├── test_bq_query_cost.py
│   ├── test_bq_partition_info.py
│   └── test_bq_lineage.py
├── integration/             # Integration tests with mocked services
│   └── test_bq_integration.py
└── bats/                    # Bash tests for shell utilities
    ├── test_git_hooks.bats
    └── test_worktree_utils.bats
```

## Setup

### Install Python Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Install Bats (for shell script testing)

**macOS:**
```bash
brew install bats-core
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install bats

# Or install from source
git clone https://github.com/bats-core/bats-core.git
cd bats-core
sudo ./install.sh /usr/local
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Types

**Unit tests only:**
```bash
pytest -m unit
```

**Integration tests only:**
```bash
pytest -m integration
```

**BigQuery tests only:**
```bash
pytest -m bq
```

**Run tests for a specific file:**
```bash
pytest tests/unit/test_data_quality.py
```

### Run with Coverage Report
```bash
pytest --cov=scripts --cov=bin --cov-report=html
# View coverage report: open htmlcov/index.html
```

### Run Bash Tests (Bats)
```bash
bats tests/bats/test_git_hooks.bats
bats tests/bats/test_worktree_utils.bats
```

## Test Markers

Tests are organized with markers for easy filtering:

- `@pytest.mark.unit` - Unit tests for individual functions
- `@pytest.mark.integration` - Integration tests with external dependencies
- `@pytest.mark.slow` - Tests that take longer to run
- `@pytest.mark.bq` - Tests requiring BigQuery client
- `@pytest.mark.hooks` - Tests for git hooks
- `@pytest.mark.worktree` - Tests for worktree utilities

## Coverage Requirements

- **Target:** 80%+ code coverage
- **Measured on:** All Python utilities in `scripts/` and `bin/`
- **Coverage report:** Generated in `htmlcov/` directory

## Writing New Tests

### Python Tests

1. Create test file in `tests/unit/` or `tests/integration/`
2. Name test file `test_<module>.py`
3. Use fixtures from `conftest.py`
4. Add appropriate markers

Example:
```python
import pytest
from scripts.data_quality import DataQualityCheck

@pytest.mark.unit
def test_data_quality_check(temp_dir):
    check = DataQualityCheck()
    result = check.run()
    assert result.passed is True
```

### Bash Tests

1. Create test file in `tests/bats/`
2. Name test file `test_<feature>.bats`
3. Use bats syntax

Example:
```bash
#!/usr/bin/env bats

@test "wt-switch lists worktrees" {
    run bin/worktree-utils/wt-switch --list
    [ "$status" -eq 0 ]
}
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. The pytest configuration enforces:
- 80% minimum coverage
- All tests must pass
- No warnings allowed with `--strict-markers`
