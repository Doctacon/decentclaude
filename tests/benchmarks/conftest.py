"""
Shared fixtures and configuration for performance benchmarks.

This module provides common test fixtures for benchmarking decentclaude utilities,
including mocked BigQuery clients, data generators, and benchmark configuration.
"""

import pytest
from unittest.mock import Mock, MagicMock
from google.cloud import bigquery
from typing import List, Dict, Any
import random
import string


# Benchmark configuration
pytest_benchmark_disable_gc = True
pytest_benchmark_warmup = True
pytest_benchmark_warmup_iterations = 3


@pytest.fixture
def mock_bq_client():
    """
    Create a mock BigQuery client for benchmarking.

    This fixture mocks all external API calls to measure pure code performance
    without network latency or quota limits.
    """
    client = Mock(spec=bigquery.Client)
    client.project = "test-project"
    return client


@pytest.fixture
def mock_table_metadata():
    """Generate mock table metadata for benchmarking."""
    def _create_metadata(table_id: str, num_rows: int = 1000000, num_bytes: int = 100000000):
        table = Mock(spec=bigquery.Table)
        table.table_id = table_id.split('.')[-1]
        table.dataset_id = table_id.split('.')[-2] if '.' in table_id else "dataset"
        table.project = table_id.split('.')[0] if table_id.count('.') == 2 else "project"
        table.table_type = "TABLE"
        table.num_rows = num_rows
        table.num_bytes = num_bytes
        table.created = None
        table.modified = None
        table.description = f"Mock table {table_id}"
        return table

    return _create_metadata


@pytest.fixture
def mock_table_schema():
    """Generate mock table schema with various column types."""
    def _create_schema(num_columns: int = 10, include_nested: bool = False):
        schema = []
        field_types = ['STRING', 'INT64', 'FLOAT64', 'BOOLEAN', 'TIMESTAMP', 'DATE']

        for i in range(num_columns):
            field = Mock(spec=bigquery.SchemaField)
            field.name = f"column_{i}"
            field.field_type = random.choice(field_types)
            field.mode = "NULLABLE"
            schema.append(field)

        if include_nested:
            # Add a nested RECORD field
            nested_field = Mock(spec=bigquery.SchemaField)
            nested_field.name = "nested_data"
            nested_field.field_type = "RECORD"
            nested_field.mode = "NULLABLE"
            nested_field.fields = [
                Mock(name="nested_col1", field_type="STRING", mode="NULLABLE"),
                Mock(name="nested_col2", field_type="INT64", mode="NULLABLE"),
            ]
            schema.append(nested_field)

        return schema

    return _create_schema


@pytest.fixture
def mock_query_results():
    """Generate mock query results for benchmarking."""
    def _create_results(num_rows: int = 100, num_columns: int = 5):
        rows = []
        for _ in range(num_rows):
            row = {}
            for col in range(num_columns):
                col_name = f"col_{col}"
                row[col_name] = random.choice([
                    random.randint(1, 1000000),
                    random.random() * 1000,
                    ''.join(random.choices(string.ascii_letters, k=20)),
                    None
                ])
            rows.append(row)

        # Mock the query result iterator
        mock_result = MagicMock()
        mock_result.__iter__ = lambda self: iter(rows)
        mock_result.total_rows = num_rows

        return mock_result

    return _create_results


@pytest.fixture
def mock_query_job():
    """Create a mock BigQuery query job."""
    def _create_job(
        job_id: str = "test-job-123",
        total_bytes_processed: int = 1000000,
        total_slot_ms: int = 5000,
        query_plan_stages: int = 3
    ):
        job = Mock(spec=bigquery.QueryJob)
        job.job_id = job_id
        job.state = "DONE"
        job.total_bytes_processed = total_bytes_processed
        job.total_slot_ms = total_slot_ms

        # Mock query plan stages
        stages = []
        for i in range(query_plan_stages):
            stage = Mock()
            stage.name = f"Stage {i}"
            stage.read_ratio_avg = random.random()
            stage.write_ratio_avg = random.random()
            stage.compute_ratio_avg = random.random()
            stage.wait_ratio_avg = random.random()
            stage.records_read = random.randint(1000, 1000000)
            stage.records_written = random.randint(100, 100000)
            stage.shuffle_output_bytes = random.randint(10000, 10000000)
            stages.append(stage)

        job.query_plan = stages
        job.result = lambda: MagicMock()

        return job

    return _create_job


@pytest.fixture
def sample_data_small():
    """Generate small dataset for benchmarking (10 rows)."""
    return {
        'rows': 10,
        'columns': 5,
        'description': 'Small dataset (10 rows, 5 columns)'
    }


@pytest.fixture
def sample_data_medium():
    """Generate medium dataset for benchmarking (1000 rows)."""
    return {
        'rows': 1000,
        'columns': 20,
        'description': 'Medium dataset (1000 rows, 20 columns)'
    }


@pytest.fixture
def sample_data_large():
    """Generate large dataset for benchmarking (100000 rows)."""
    return {
        'rows': 100000,
        'columns': 50,
        'description': 'Large dataset (100000 rows, 50 columns)'
    }


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic API client for AI utilities."""
    client = Mock()

    # Mock the messages.create method
    mock_message = Mock()
    mock_message.content = [
        Mock(text="Generated SQL code here")
    ]
    mock_message.usage = Mock(
        input_tokens=100,
        output_tokens=200
    )

    client.messages.create = Mock(return_value=mock_message)

    return client


@pytest.fixture
def mock_kb_database(tmp_path):
    """Create a temporary knowledge base database for benchmarking."""
    db_path = tmp_path / "test_kb.db"
    return str(db_path)


def generate_table_rows(num_rows: int, schema: List[Dict[str, str]]) -> List[Dict]:
    """
    Generate random table rows based on schema.

    Args:
        num_rows: Number of rows to generate
        schema: List of column definitions with 'name' and 'type'

    Returns:
        List of row dictionaries
    """
    rows = []
    for _ in range(num_rows):
        row = {}
        for col in schema:
            col_name = col['name']
            col_type = col['type']

            if col_type in ['STRING', 'BYTES']:
                row[col_name] = ''.join(random.choices(string.ascii_letters, k=20))
            elif col_type in ['INT64', 'INTEGER']:
                row[col_name] = random.randint(1, 1000000)
            elif col_type in ['FLOAT64', 'FLOAT', 'NUMERIC']:
                row[col_name] = random.random() * 1000
            elif col_type == 'BOOLEAN':
                row[col_name] = random.choice([True, False])
            elif col_type == 'TIMESTAMP':
                row[col_name] = "2024-01-01T00:00:00Z"
            elif col_type == 'DATE':
                row[col_name] = "2024-01-01"
            else:
                row[col_name] = None

        rows.append(row)

    return rows


@pytest.fixture
def data_generator():
    """Fixture that returns the data generation function."""
    return generate_table_rows


# Benchmark grouping configuration
def pytest_configure(config):
    """Configure pytest with custom benchmark settings."""
    config.addinivalue_line(
        "markers", "benchmark: mark test as a benchmark test"
    )
    config.addinivalue_line(
        "markers", "bq_profile: mark test as bq-profile benchmark"
    )
    config.addinivalue_line(
        "markers", "bq_lineage: mark test as bq-lineage benchmark"
    )
    config.addinivalue_line(
        "markers", "bq_explain: mark test as bq-explain benchmark"
    )
    config.addinivalue_line(
        "markers", "bq_schema_diff: mark test as bq-schema-diff benchmark"
    )
    config.addinivalue_line(
        "markers", "ai_generate: mark test as ai-generate benchmark"
    )
    config.addinivalue_line(
        "markers", "kb_search: mark test as kb search benchmark"
    )
