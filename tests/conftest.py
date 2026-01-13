"""
Shared pytest fixtures for CLI utilities testing.
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock
import pytest


# --- File System Fixtures ---

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_sql_file(temp_dir):
    """Create a temporary SQL file."""
    sql_file = temp_dir / "test.sql"
    sql_file.write_text("SELECT * FROM table")
    return sql_file


@pytest.fixture
def temp_config_file(temp_dir):
    """Create a temporary config file."""
    config_file = temp_dir / "config.yaml"
    config_file.write_text("key: value")
    return config_file


# --- BigQuery Mocking Fixtures ---

@pytest.fixture
def mock_bigquery_client():
    """Create a mock BigQuery client."""
    client = MagicMock()
    return client


@pytest.fixture
def mock_table():
    """Create a mock BigQuery table object."""
    table = MagicMock()
    table.table_id = "test_table"
    table.dataset_id = "test_dataset"
    table.project = "test_project"
    table.num_rows = 1000
    table.num_bytes = 1024 * 1024  # 1 MB
    table.created = "2024-01-01 00:00:00"
    table.modified = "2024-01-02 00:00:00"
    table.time_partitioning = None
    table.range_partitioning = None
    table.clustering_fields = None
    return table


@pytest.fixture
def mock_partitioned_table(mock_table):
    """Create a mock partitioned BigQuery table."""
    partition = MagicMock()
    partition.type_ = "DAY"
    partition.field = "date"
    partition.expiration_ms = 7776000000  # 90 days
    mock_table.time_partitioning = partition
    return mock_table


@pytest.fixture
def mock_clustered_table(mock_table):
    """Create a mock clustered BigQuery table."""
    mock_table.clustering_fields = ["user_id", "event_type"]
    return mock_table


@pytest.fixture
def mock_schema():
    """Create a mock BigQuery schema."""
    field1 = MagicMock()
    field1.name = "id"
    field1.field_type = "INTEGER"
    field1.mode = "REQUIRED"

    field2 = MagicMock()
    field2.name = "name"
    field2.field_type = "STRING"
    field2.mode = "NULLABLE"

    field3 = MagicMock()
    field3.name = "tags"
    field3.field_type = "STRING"
    field3.mode = "REPEATED"

    return [field1, field2, field3]


@pytest.fixture
def mock_query_job():
    """Create a mock BigQuery query job."""
    job = MagicMock()
    job.total_bytes_processed = 1024 * 1024 * 100  # 100 MB
    job.total_bytes_billed = 1024 * 1024 * 100
    job.state = "DONE"
    job.error_result = None
    return job


@pytest.fixture
def mock_table_reference():
    """Create a mock BigQuery table reference."""
    ref = MagicMock()
    ref.project = "test_project"
    ref.dataset_id = "test_dataset"
    ref.table_id = "test_table"
    return ref


# --- SQL Content Fixtures ---

@pytest.fixture
def valid_sql():
    """Return valid SQL content."""
    return "SELECT id, name, email FROM users WHERE created_at > '2024-01-01'"


@pytest.fixture
def invalid_sql():
    """Return invalid SQL content."""
    return "SELECT FROM WHERE"


@pytest.fixture
def sql_with_secrets():
    """Return SQL with hardcoded secrets."""
    return """
    SELECT * FROM users
    WHERE api_key = 'sk_test_abc123'
    AND password = 'secret123'
    """


@pytest.fixture
def sql_without_secrets():
    """Return SQL without secrets."""
    return """
    SELECT * FROM users
    WHERE user_id = @user_id
    AND status = 'active'
    """


# --- View Definition Fixtures ---

@pytest.fixture
def mock_view_with_dependencies():
    """Create a mock view with upstream dependencies."""
    view = MagicMock()
    view.table_type = "VIEW"
    view.view_query = """
    SELECT
        u.id,
        u.name,
        o.order_id
    FROM `project.dataset.users` u
    LEFT JOIN `project.dataset.orders` o
        ON u.id = o.user_id
    """
    return view


# --- Git Repository Fixtures ---

@pytest.fixture
def mock_git_repo(temp_dir):
    """Create a mock git repository structure."""
    git_dir = temp_dir / ".git"
    git_dir.mkdir()
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir()
    return temp_dir


@pytest.fixture
def mock_worktree_list():
    """Return mock output from git worktree list."""
    return """
/Users/test/repo              abc1234 [main]
/Users/test/repo-feature1     def5678 [feature/test-1]
/Users/test/repo-feature2     ghi9012 [feature/test-2]
    """.strip()


# --- Environment Fixtures ---

@pytest.fixture
def clean_env(monkeypatch):
    """Provide a clean environment without Google Cloud credentials."""
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.delenv("GCLOUD_PROJECT", raising=False)
    return monkeypatch


@pytest.fixture
def mock_gcp_env(monkeypatch, temp_dir):
    """Set up mock GCP environment variables."""
    creds_file = temp_dir / "credentials.json"
    creds_file.write_text('{"type": "service_account"}')
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", str(creds_file))
    monkeypatch.setenv("GCLOUD_PROJECT", "test-project")
    return monkeypatch


# --- Marker Configuration ---

def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "bq: BigQuery related tests")
    config.addinivalue_line("markers", "hooks: Git hooks tests")
    config.addinivalue_line("markers", "worktree: Worktree utilities tests")
    config.addinivalue_line("markers", "skills: Skills integration tests")
