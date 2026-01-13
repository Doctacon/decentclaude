"""
Performance benchmarks for bq-schema-diff utility.

This module benchmarks the schema comparison functionality with different
schema sizes and complexity levels.

Run with:
    pytest tests/benchmarks/test_bq_schema_diff_benchmark.py --benchmark-only
    pytest tests/benchmarks/test_bq_schema_diff_benchmark.py --benchmark-autosave
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib"))


@pytest.mark.benchmark
@pytest.mark.bq_schema_diff
class TestBQSchemaDiffBenchmarks:
    """Benchmarks for bq-schema-diff utility."""

    def test_get_schema_small_tables(self, benchmark, mock_bq_client, mock_table_schema):
        """Benchmark getting schema for small tables (10 columns)."""
        table_id = "project.dataset.table"
        mock_table = Mock()
        mock_table.schema = mock_table_schema(num_columns=10)
        mock_bq_client.get_table.return_value = mock_table

        def get_schema():
            table = mock_bq_client.get_table(table_id)
            schema = {}
            for field in table.schema:
                schema[field.name] = {
                    'type': field.field_type,
                    'mode': field.mode
                }
            return schema

        result = benchmark(get_schema)
        assert len(result) == 10

    def test_get_schema_medium_tables(self, benchmark, mock_bq_client, mock_table_schema):
        """Benchmark getting schema for medium tables (50 columns)."""
        table_id = "project.dataset.table"
        mock_table = Mock()
        mock_table.schema = mock_table_schema(num_columns=50)
        mock_bq_client.get_table.return_value = mock_table

        def get_schema():
            table = mock_bq_client.get_table(table_id)
            schema = {}
            for field in table.schema:
                schema[field.name] = {
                    'type': field.field_type,
                    'mode': field.mode
                }
            return schema

        result = benchmark(get_schema)
        assert len(result) == 50

    def test_get_schema_large_tables(self, benchmark, mock_bq_client, mock_table_schema):
        """Benchmark getting schema for large tables (200 columns with nested fields)."""
        table_id = "project.dataset.table"
        mock_table = Mock()
        mock_table.schema = mock_table_schema(num_columns=200, include_nested=True)
        mock_bq_client.get_table.return_value = mock_table

        def get_schema():
            table = mock_bq_client.get_table(table_id)
            schema = {}
            for field in table.schema:
                if field.field_type == 'RECORD' and hasattr(field, 'fields'):
                    nested = {}
                    for nested_field in field.fields:
                        nested[nested_field.name] = nested_field.field_type
                    schema[field.name] = {'type': 'RECORD', 'fields': nested}
                else:
                    schema[field.name] = {
                        'type': field.field_type,
                        'mode': field.mode
                    }
            return schema

        result = benchmark(get_schema)
        assert len(result) == 201

    def test_compare_identical_schemas_small(self, benchmark, mock_table_schema):
        """Benchmark comparing two identical small schemas."""
        schema = mock_table_schema(num_columns=20)

        schema_a = {field.name: {'type': field.field_type, 'mode': field.mode} for field in schema}
        schema_b = {field.name: {'type': field.field_type, 'mode': field.mode} for field in schema}

        def compare_schemas():
            only_in_a = set(schema_a.keys()) - set(schema_b.keys())
            only_in_b = set(schema_b.keys()) - set(schema_a.keys())
            common_fields = set(schema_a.keys()) & set(schema_b.keys())

            type_changes = []
            for field in common_fields:
                if schema_a[field]['type'] != schema_b[field]['type']:
                    type_changes.append({
                        'field': field,
                        'type_a': schema_a[field]['type'],
                        'type_b': schema_b[field]['type']
                    })

            return {
                'only_in_a': list(only_in_a),
                'only_in_b': list(only_in_b),
                'type_changes': type_changes
            }

        result = benchmark(compare_schemas)
        assert len(result['only_in_a']) == 0
        assert len(result['only_in_b']) == 0
        assert len(result['type_changes']) == 0

    def test_compare_different_schemas_small(self, benchmark, mock_table_schema):
        """Benchmark comparing two different small schemas."""
        schema_a_fields = mock_table_schema(num_columns=20)
        schema_b_fields = mock_table_schema(num_columns=20)

        # Modify schema_b to have differences
        schema_a = {field.name: {'type': field.field_type, 'mode': field.mode} for field in schema_a_fields}
        schema_b = {field.name: {'type': field.field_type, 'mode': field.mode} for field in schema_b_fields}

        # Add some differences
        schema_b['column_0'] = {'type': 'INT64', 'mode': 'REQUIRED'}  # Type change
        schema_b['new_column'] = {'type': 'STRING', 'mode': 'NULLABLE'}  # New column
        del schema_b['column_1']  # Removed column

        def compare_schemas():
            only_in_a = set(schema_a.keys()) - set(schema_b.keys())
            only_in_b = set(schema_b.keys()) - set(schema_a.keys())
            common_fields = set(schema_a.keys()) & set(schema_b.keys())

            type_changes = []
            for field in common_fields:
                if schema_a[field]['type'] != schema_b[field]['type']:
                    type_changes.append({
                        'field': field,
                        'type_a': schema_a[field]['type'],
                        'type_b': schema_b[field]['type']
                    })

            return {
                'only_in_a': list(only_in_a),
                'only_in_b': list(only_in_b),
                'type_changes': type_changes
            }

        result = benchmark(compare_schemas)
        assert len(result['only_in_a']) >= 1
        assert len(result['only_in_b']) >= 1

    def test_compare_schemas_large(self, benchmark, mock_table_schema):
        """Benchmark comparing two large schemas (100 columns each)."""
        schema_a_fields = mock_table_schema(num_columns=100)
        schema_b_fields = mock_table_schema(num_columns=100)

        schema_a = {field.name: {'type': field.field_type, 'mode': field.mode} for field in schema_a_fields}
        schema_b = {field.name: {'type': field.field_type, 'mode': field.mode} for field in schema_b_fields}

        # Create some differences
        for i in range(0, 10, 2):
            col_name = f'column_{i}'
            if col_name in schema_b:
                schema_b[col_name] = {'type': 'INT64', 'mode': 'REQUIRED'}

        def compare_schemas():
            only_in_a = set(schema_a.keys()) - set(schema_b.keys())
            only_in_b = set(schema_b.keys()) - set(schema_a.keys())
            common_fields = set(schema_a.keys()) & set(schema_b.keys())

            type_changes = []
            mode_changes = []
            for field in common_fields:
                if schema_a[field]['type'] != schema_b[field]['type']:
                    type_changes.append({
                        'field': field,
                        'type_a': schema_a[field]['type'],
                        'type_b': schema_b[field]['type']
                    })
                if schema_a[field]['mode'] != schema_b[field]['mode']:
                    mode_changes.append({
                        'field': field,
                        'mode_a': schema_a[field]['mode'],
                        'mode_b': schema_b[field]['mode']
                    })

            return {
                'only_in_a': list(only_in_a),
                'only_in_b': list(only_in_b),
                'type_changes': type_changes,
                'mode_changes': mode_changes
            }

        result = benchmark(compare_schemas)
        assert isinstance(result, dict)

    def test_compare_nested_schemas(self, benchmark):
        """Benchmark comparing schemas with nested RECORD fields."""
        schema_a = {
            'user_id': {'type': 'INT64', 'mode': 'REQUIRED'},
            'user_data': {
                'type': 'RECORD',
                'fields': {
                    'name': 'STRING',
                    'email': 'STRING',
                    'age': 'INT64',
                    'address': {
                        'type': 'RECORD',
                        'fields': {
                            'street': 'STRING',
                            'city': 'STRING',
                            'zip': 'STRING'
                        }
                    }
                }
            }
        }

        schema_b = {
            'user_id': {'type': 'INT64', 'mode': 'REQUIRED'},
            'user_data': {
                'type': 'RECORD',
                'fields': {
                    'name': 'STRING',
                    'email': 'STRING',
                    'age': 'STRING',  # Type changed
                    'phone': 'STRING',  # New field
                    'address': {
                        'type': 'RECORD',
                        'fields': {
                            'street': 'STRING',
                            'city': 'STRING',
                            'country': 'STRING'  # New nested field, zip removed
                        }
                    }
                }
            }
        }

        def compare_nested_schemas():
            differences = []

            def compare_fields(path, fields_a, fields_b):
                for field_name in set(list(fields_a.keys()) + list(fields_b.keys())):
                    full_path = f"{path}.{field_name}" if path else field_name

                    if field_name not in fields_a:
                        differences.append({'type': 'added', 'field': full_path})
                    elif field_name not in fields_b:
                        differences.append({'type': 'removed', 'field': full_path})
                    else:
                        field_a = fields_a[field_name]
                        field_b = fields_b[field_name]

                        if isinstance(field_a, dict) and 'type' in field_a:
                            if field_a['type'] != field_b.get('type'):
                                differences.append({
                                    'type': 'type_change',
                                    'field': full_path,
                                    'from': field_a['type'],
                                    'to': field_b.get('type')
                                })

                            if field_a['type'] == 'RECORD' and 'fields' in field_a:
                                compare_fields(full_path, field_a['fields'], field_b.get('fields', {}))
                        elif field_a != field_b:
                            differences.append({
                                'type': 'type_change',
                                'field': full_path,
                                'from': field_a,
                                'to': field_b
                            })

            compare_fields('', schema_a, schema_b)
            return differences

        result = benchmark(compare_nested_schemas)
        assert len(result) > 0

    def test_format_diff_output_text(self, benchmark):
        """Benchmark formatting schema diff as text."""
        diff_result = {
            'only_in_a': ['old_column_1', 'old_column_2'],
            'only_in_b': ['new_column_1', 'new_column_2'],
            'type_changes': [
                {'field': 'user_id', 'type_a': 'STRING', 'type_b': 'INT64'},
                {'field': 'amount', 'type_a': 'INT64', 'type_b': 'FLOAT64'},
            ]
        }

        def format_text():
            lines = []
            lines.append("Schema Comparison Results")
            lines.append("=" * 50)

            if diff_result['only_in_a']:
                lines.append("\nColumns only in Table A:")
                for col in diff_result['only_in_a']:
                    lines.append(f"  - {col}")

            if diff_result['only_in_b']:
                lines.append("\nColumns only in Table B:")
                for col in diff_result['only_in_b']:
                    lines.append(f"  + {col}")

            if diff_result['type_changes']:
                lines.append("\nType Changes:")
                for change in diff_result['type_changes']:
                    lines.append(f"  ~ {change['field']}: {change['type_a']} -> {change['type_b']}")

            return '\n'.join(lines)

        result = benchmark(format_text)
        assert 'Schema Comparison Results' in result
        assert 'old_column_1' in result

    def test_format_diff_output_json(self, benchmark):
        """Benchmark formatting schema diff as JSON."""
        import json

        diff_result = {
            'table_a': 'project.dataset.table_v1',
            'table_b': 'project.dataset.table_v2',
            'only_in_a': [f'old_column_{i}' for i in range(20)],
            'only_in_b': [f'new_column_{i}' for i in range(20)],
            'type_changes': [
                {'field': f'column_{i}', 'type_a': 'STRING', 'type_b': 'INT64'}
                for i in range(10)
            ]
        }

        def format_json_output():
            return json.dumps(diff_result, indent=2)

        result = benchmark(format_json_output)
        parsed = json.loads(result)
        assert len(parsed['only_in_a']) == 20
        assert len(parsed['type_changes']) == 10

    def test_batch_schema_comparison(self, benchmark, mock_bq_client, mock_table_schema):
        """Benchmark comparing schemas for multiple table pairs."""
        table_pairs = [
            (f'project.dataset.table_a_{i}', f'project.dataset.table_b_{i}')
            for i in range(10)
        ]

        # Setup mocks
        def get_mock_table(table_id):
            mock_table = Mock()
            mock_table.schema = mock_table_schema(num_columns=20)
            return mock_table

        mock_bq_client.get_table.side_effect = get_mock_table

        def batch_compare():
            results = []
            for table_a, table_b in table_pairs:
                schema_a_fields = mock_bq_client.get_table(table_a).schema
                schema_b_fields = mock_bq_client.get_table(table_b).schema

                schema_a = {f.name: {'type': f.field_type} for f in schema_a_fields}
                schema_b = {f.name: {'type': f.field_type} for f in schema_b_fields}

                only_in_a = set(schema_a.keys()) - set(schema_b.keys())
                only_in_b = set(schema_b.keys()) - set(schema_a.keys())

                results.append({
                    'table_a': table_a,
                    'table_b': table_b,
                    'differences': len(only_in_a) + len(only_in_b)
                })

            return results

        result = benchmark(batch_compare)
        assert len(result) == 10
