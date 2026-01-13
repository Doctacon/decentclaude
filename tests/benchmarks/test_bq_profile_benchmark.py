"""
Performance benchmarks for bq-profile utility.

This module benchmarks the table profiling functionality with different data sizes
and configurations, measuring pure code performance with mocked BigQuery API.

Run with:
    pytest tests/benchmarks/test_bq_profile_benchmark.py --benchmark-only
    pytest tests/benchmarks/test_bq_profile_benchmark.py --benchmark-autosave
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib"))


@pytest.fixture
def mock_profile_dependencies():
    """Mock all external dependencies for bq-profile."""
    with patch('google.cloud.bigquery.Client') as mock_client:
        # Mock table metadata
        mock_table = Mock()
        mock_table.project = "test-project"
        mock_table.dataset_id = "test_dataset"
        mock_table.table_id = "test_table"
        mock_table.table_type = "TABLE"
        mock_table.num_rows = 1000000
        mock_table.num_bytes = 100000000
        mock_table.created = None
        mock_table.modified = None
        mock_table.description = "Test table"

        # Mock schema
        mock_field1 = Mock()
        mock_field1.name = "user_id"
        mock_field1.field_type = "INT64"
        mock_field1.mode = "REQUIRED"

        mock_field2 = Mock()
        mock_field2.name = "event_name"
        mock_field2.field_type = "STRING"
        mock_field2.mode = "NULLABLE"

        mock_field3 = Mock()
        mock_field3.name = "revenue"
        mock_field3.field_type = "FLOAT64"
        mock_field3.mode = "NULLABLE"

        mock_table.schema = [mock_field1, mock_field2, mock_field3]

        mock_client_instance = Mock()
        mock_client_instance.get_table.return_value = mock_table
        mock_client.return_value = mock_client_instance

        yield mock_client_instance


@pytest.mark.benchmark
@pytest.mark.bq_profile
class TestBQProfileBenchmarks:
    """Benchmarks for bq-profile utility."""

    def test_get_table_metadata_small(self, benchmark, mock_bq_client, mock_table_metadata, mock_table_schema):
        """Benchmark getting metadata for a small table (10 columns)."""
        table_id = "project.dataset.small_table"
        mock_table = mock_table_metadata(table_id, num_rows=1000, num_bytes=100000)
        mock_table.schema = mock_table_schema(num_columns=10)
        mock_bq_client.get_table.return_value = mock_table

        def get_metadata():
            table = mock_bq_client.get_table(table_id)
            return {
                "table_id": table_id,
                "project": table.project,
                "dataset": table.dataset_id,
                "table_name": table.table_id,
                "num_rows": table.num_rows,
                "num_bytes": table.num_bytes,
                "schema": [{"name": f.name, "type": f.field_type} for f in table.schema]
            }

        result = benchmark(get_metadata)
        assert result['table_id'] == table_id
        assert len(result['schema']) == 10

    def test_get_table_metadata_medium(self, benchmark, mock_bq_client, mock_table_metadata, mock_table_schema):
        """Benchmark getting metadata for a medium table (50 columns)."""
        table_id = "project.dataset.medium_table"
        mock_table = mock_table_metadata(table_id, num_rows=1000000, num_bytes=10000000)
        mock_table.schema = mock_table_schema(num_columns=50)
        mock_bq_client.get_table.return_value = mock_table

        def get_metadata():
            table = mock_bq_client.get_table(table_id)
            return {
                "table_id": table_id,
                "project": table.project,
                "dataset": table.dataset_id,
                "table_name": table.table_id,
                "num_rows": table.num_rows,
                "num_bytes": table.num_bytes,
                "schema": [{"name": f.name, "type": f.field_type} for f in table.schema]
            }

        result = benchmark(get_metadata)
        assert len(result['schema']) == 50

    def test_get_table_metadata_large(self, benchmark, mock_bq_client, mock_table_metadata, mock_table_schema):
        """Benchmark getting metadata for a large table (200 columns with nested fields)."""
        table_id = "project.dataset.large_table"
        mock_table = mock_table_metadata(table_id, num_rows=100000000, num_bytes=1000000000)
        mock_table.schema = mock_table_schema(num_columns=200, include_nested=True)
        mock_bq_client.get_table.return_value = mock_table

        def get_metadata():
            table = mock_bq_client.get_table(table_id)
            return {
                "table_id": table_id,
                "project": table.project,
                "dataset": table.dataset_id,
                "table_name": table.table_id,
                "num_rows": table.num_rows,
                "num_bytes": table.num_bytes,
                "schema": [{"name": f.name, "type": f.field_type} for f in table.schema]
            }

        result = benchmark(get_metadata)
        assert len(result['schema']) == 201  # 200 + 1 nested field

    def test_build_column_stats_query_small(self, benchmark, mock_table_schema):
        """Benchmark building statistics query for small schema."""
        schema = mock_table_schema(num_columns=10)

        def build_query():
            stats_parts = []
            for field in schema:
                col_name = field.name
                col_type = field.field_type

                if col_type in ['INT64', 'FLOAT64', 'NUMERIC']:
                    stats_parts.append(f"""
                        MIN({col_name}) as {col_name}_min,
                        MAX({col_name}) as {col_name}_max,
                        AVG({col_name}) as {col_name}_avg,
                        STDDEV({col_name}) as {col_name}_stddev
                    """)
                elif col_type == 'STRING':
                    stats_parts.append(f"""
                        COUNT(DISTINCT {col_name}) as {col_name}_distinct,
                        APPROX_TOP_COUNT({col_name}, 5) as {col_name}_top_values
                    """)

            query = f"SELECT {', '.join(stats_parts)} FROM `table_id`"
            return query

        result = benchmark(build_query)
        assert 'SELECT' in result
        assert 'FROM' in result

    def test_build_column_stats_query_large(self, benchmark, mock_table_schema):
        """Benchmark building statistics query for large schema."""
        schema = mock_table_schema(num_columns=200)

        def build_query():
            stats_parts = []
            for field in schema:
                col_name = field.name
                col_type = field.field_type

                if col_type in ['INT64', 'FLOAT64', 'NUMERIC']:
                    stats_parts.append(f"""
                        MIN({col_name}) as {col_name}_min,
                        MAX({col_name}) as {col_name}_max,
                        AVG({col_name}) as {col_name}_avg,
                        STDDEV({col_name}) as {col_name}_stddev
                    """)
                elif col_type == 'STRING':
                    stats_parts.append(f"""
                        COUNT(DISTINCT {col_name}) as {col_name}_distinct,
                        APPROX_TOP_COUNT({col_name}, 5) as {col_name}_top_values
                    """)

            query = f"SELECT {', '.join(stats_parts)} FROM `table_id`"
            return query

        result = benchmark(build_query)
        assert 'SELECT' in result

    def test_parse_column_statistics_small(self, benchmark, mock_query_results, sample_data_small):
        """Benchmark parsing column statistics from small result set."""
        query_result = mock_query_results(
            num_rows=sample_data_small['rows'],
            num_columns=sample_data_small['columns']
        )

        def parse_stats():
            stats = []
            for row in query_result:
                col_stats = {
                    'column_name': row.get('col_0', 'unknown'),
                    'null_count': row.get('col_1', 0),
                    'distinct_count': row.get('col_2', 0),
                    'min_value': row.get('col_3', None),
                    'max_value': row.get('col_4', None),
                }
                stats.append(col_stats)
            return stats

        result = benchmark(parse_stats)
        assert len(result) == sample_data_small['rows']

    def test_parse_column_statistics_medium(self, benchmark, mock_query_results, sample_data_medium):
        """Benchmark parsing column statistics from medium result set."""
        query_result = mock_query_results(
            num_rows=sample_data_medium['rows'],
            num_columns=sample_data_medium['columns']
        )

        def parse_stats():
            stats = []
            for row in query_result:
                col_stats = {}
                for i in range(sample_data_medium['columns']):
                    col_name = f'col_{i}'
                    col_stats[col_name] = row.get(col_name)
                stats.append(col_stats)
            return stats

        result = benchmark(parse_stats)
        assert len(result) == sample_data_medium['rows']

    def test_format_profile_output_text(self, benchmark, mock_table_metadata, mock_table_schema):
        """Benchmark formatting profile output as text."""
        table_id = "project.dataset.table"
        metadata = {
            'table_id': table_id,
            'num_rows': 1000000,
            'num_bytes': 100000000,
            'schema': [{'name': f'col_{i}', 'type': 'STRING'} for i in range(20)]
        }

        column_stats = [
            {
                'column_name': f'col_{i}',
                'null_count': 100,
                'distinct_count': 5000,
                'min_value': 0,
                'max_value': 10000,
            }
            for i in range(20)
        ]

        def format_output():
            lines = []
            lines.append(f"Table Profile: {metadata['table_id']}")
            lines.append(f"Rows: {metadata['num_rows']:,}")
            lines.append(f"Size: {metadata['num_bytes']:,} bytes")
            lines.append("\nColumn Statistics:")

            for stat in column_stats:
                lines.append(f"  {stat['column_name']}:")
                lines.append(f"    Nulls: {stat['null_count']:,}")
                lines.append(f"    Distinct: {stat['distinct_count']:,}")
                if stat.get('min_value') is not None:
                    lines.append(f"    Range: {stat['min_value']} - {stat['max_value']}")

            return '\n'.join(lines)

        result = benchmark(format_output)
        assert 'Table Profile' in result
        assert '1,000,000' in result

    def test_format_profile_output_json(self, benchmark, mock_table_metadata):
        """Benchmark formatting profile output as JSON."""
        import json

        profile_data = {
            'table_id': 'project.dataset.table',
            'metadata': {
                'num_rows': 1000000,
                'num_bytes': 100000000,
                'schema': [{'name': f'col_{i}', 'type': 'STRING'} for i in range(50)]
            },
            'column_stats': [
                {
                    'column_name': f'col_{i}',
                    'null_count': 100,
                    'distinct_count': 5000,
                }
                for i in range(50)
            ]
        }

        def format_json():
            return json.dumps(profile_data, indent=2)

        result = benchmark(format_json)
        assert 'project.dataset.table' in result
        parsed = json.loads(result)
        assert len(parsed['column_stats']) == 50

    def test_batch_profile_processing(self, benchmark, mock_bq_client, mock_table_metadata, mock_table_schema):
        """Benchmark batch profiling of multiple tables."""
        table_ids = [f"project.dataset.table_{i}" for i in range(10)]

        # Setup mocks for all tables
        for table_id in table_ids:
            mock_table = mock_table_metadata(table_id, num_rows=10000, num_bytes=1000000)
            mock_table.schema = mock_table_schema(num_columns=10)
            mock_bq_client.get_table.return_value = mock_table

        def batch_profile():
            results = []
            for table_id in table_ids:
                table = mock_bq_client.get_table(table_id)
                profile = {
                    'table_id': table_id,
                    'num_rows': table.num_rows,
                    'num_bytes': table.num_bytes,
                    'schema': [{'name': f.name, 'type': f.field_type} for f in table.schema]
                }
                results.append(profile)
            return results

        result = benchmark(batch_profile)
        assert len(result) == 10
