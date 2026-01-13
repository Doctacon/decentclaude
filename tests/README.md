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
│   ├── test_bq_integration.py
│   └── test_skills.py       # Skills integration tests
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

**Skills tests only:**
```bash
pytest -m skills
```

**Run tests for a specific file:**
```bash
pytest tests/unit/test_data_quality.py
pytest tests/integration/test_skills.py
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
- `@pytest.mark.skills` - Tests for Skills utility invocation

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

## Skills Integration Tests

The `tests/integration/test_skills.py` file contains comprehensive tests for Skills that invoke CLI utilities. These tests validate that Skills correctly:

1. **Invoke utilities with correct parameters** - Verify command-line arguments are properly formatted
2. **Parse utility output** - Test JSON and text output parsing
3. **Handle errors gracefully** - Ensure failures are caught and handled
4. **Support multiple workflows** - Test cross-skill integration patterns

### Skills Covered

- **data-lineage-doc**: Tests for `bq-lineage` utility invocation with JSON and Mermaid output
- **schema-doc-generator**: Tests for `bq-schema-diff` utility for schema comparison
- **sql-optimizer**: Tests for `bq-optimize` and `bq-explain` utilities
- **doc-generator**: Tests for `ai-generate` utility (when available)

### Test Approach

Skills tests use mocked subprocess calls to:
- Avoid external dependencies (BigQuery, APIs)
- Ensure fast, deterministic test execution
- Validate utility invocations without running actual commands
- Test error handling with simulated failures

### Example

```python
@pytest.mark.integration
@pytest.mark.skills
def test_invokes_bq_lineage_with_correct_params(mock_subprocess, successful_subprocess_result):
    """Test that data-lineage-doc skill invokes bq-lineage correctly"""
    successful_subprocess_result.stdout = json_output
    mock_subprocess.return_value = successful_subprocess_result

    result = subprocess.run(
        ["bin/data-utils/bq-lineage", "project.dataset.table", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    mock_subprocess.assert_called_once_with(
        ["bin/data-utils/bq-lineage", "project.dataset.table", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )
```

### Running Skills Tests

```bash
# Run all skills tests
pytest -m skills

# Run specific skill test file
pytest tests/integration/test_skills.py

# Run tests for specific skill
pytest tests/integration/test_skills.py -k "lineage"
pytest tests/integration/test_skills.py -k "schema"
pytest tests/integration/test_skills.py -k "optimizer"

# Run with verbose output
pytest tests/integration/test_skills.py -v
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. The pytest configuration enforces:
- 80% minimum coverage
- All tests must pass
- No warnings allowed with `--strict-markers`
