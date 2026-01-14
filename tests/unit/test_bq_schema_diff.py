"""
Unit tests for bin/data-utils/bq-schema-diff

Tests schema comparison functionality for BigQuery tables.
"""
import pytest
import sys
import json
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Add bin directory to path for imports
bin_path = Path(__file__).parent.parent.parent / "bin" / "data-utils"
sys.path.insert(0, str(bin_path))

# Import after path modification using SourceFileLoader
from importlib.machinery import SourceFileLoader

# Mock google.cloud and bq_cache before importing
sys.modules['google'] = MagicMock()
sys.modules['google.cloud'] = MagicMock()
sys.modules['google.cloud.bigquery'] = MagicMock()
sys.modules['bq_cache'] = MagicMock()

loader = SourceFileLoader("bq_schema_diff", str(bin_path / "bq-schema-diff"))
bq_schema_diff = loader.load_module()

get_table_schema = bq_schema_diff.get_table_schema
compare_schemas = bq_schema_diff.compare_schemas
print_text_report = bq_schema_diff.print_text_report
print_json_report = bq_schema_diff.print_json_report


# --- Fixtures ---

@pytest.fixture
def simple_schema():
    """A simple schema with basic types"""
    return {
        "id": "INTEGER",
        "name": "STRING",
        "email": "STRING",
        "age": "INTEGER",
    }


@pytest.fixture
def schema_with_modes():
    """Schema with different field modes"""
    return {
        "id": "INTEGER (REQUIRED)",
        "name": "STRING",
        "tags": "STRING (REPEATED)",
        "metadata": "STRING",
    }


@pytest.fixture
def schema_with_nested():
    """Schema with nested RECORD type"""
    return {
        "id": "INTEGER",
        "name": "STRING",
        "address": "RECORD<street:STRING, city:STRING, zip:STRING>",
    }


@pytest.fixture
def mock_bigquery_field():
    """Create a mock BigQuery field"""
    def _create_field(name, field_type, mode="NULLABLE", fields=None):
        field = MagicMock()
        field.name = name
        field.field_type = field_type
        field.mode = mode
        field.fields = fields or []
        return field
    return _create_field


@pytest.fixture
def mock_table_with_schema(mock_bigquery_field):
    """Create a mock BigQuery table with schema"""
    def _create_table(schema_fields):
        table = MagicMock()
        table.schema = schema_fields
        return table
    return _create_table


# --- get_table_schema() Tests ---

@pytest.mark.unit
@pytest.mark.bq
def test_get_table_schema_simple(mock_bigquery_client, mock_bigquery_field, mock_table_with_schema):
    """Test getting schema for a table with simple types"""
    fields = [
        mock_bigquery_field("id", "INTEGER", "NULLABLE"),
        mock_bigquery_field("name", "STRING", "NULLABLE"),
        mock_bigquery_field("age", "INTEGER", "NULLABLE"),
    ]
    mock_table = mock_table_with_schema(fields)
    mock_bigquery_client.get_table.return_value = mock_table

    schema = get_table_schema(mock_bigquery_client, "project.dataset.table")

    assert schema == {
        "id": "INTEGER",
        "name": "STRING",
        "age": "INTEGER",
    }
    mock_bigquery_client.get_table.assert_called_once_with("project.dataset.table")


@pytest.mark.unit
@pytest.mark.bq
def test_get_table_schema_with_required_fields(mock_bigquery_client, mock_bigquery_field, mock_table_with_schema):
    """Test schema retrieval with REQUIRED mode fields"""
    fields = [
        mock_bigquery_field("id", "INTEGER", "REQUIRED"),
        mock_bigquery_field("name", "STRING", "NULLABLE"),
    ]
    mock_table = mock_table_with_schema(fields)
    mock_bigquery_client.get_table.return_value = mock_table

    schema = get_table_schema(mock_bigquery_client, "project.dataset.table")

    assert schema == {
        "id": "INTEGER (REQUIRED)",
        "name": "STRING",
    }


@pytest.mark.unit
@pytest.mark.bq
def test_get_table_schema_with_repeated_fields(mock_bigquery_client, mock_bigquery_field, mock_table_with_schema):
    """Test schema retrieval with REPEATED mode fields"""
    fields = [
        mock_bigquery_field("id", "INTEGER", "NULLABLE"),
        mock_bigquery_field("tags", "STRING", "REPEATED"),
    ]
    mock_table = mock_table_with_schema(fields)
    mock_bigquery_client.get_table.return_value = mock_table

    schema = get_table_schema(mock_bigquery_client, "project.dataset.table")

    assert schema == {
        "id": "INTEGER",
        "tags": "STRING (REPEATED)",
    }


@pytest.mark.unit
@pytest.mark.bq
def test_get_table_schema_with_nested_record(mock_bigquery_client, mock_bigquery_field, mock_table_with_schema):
    """Test schema retrieval with nested RECORD type"""
    # Create nested fields
    nested_fields = [
        mock_bigquery_field("street", "STRING"),
        mock_bigquery_field("city", "STRING"),
        mock_bigquery_field("zip", "STRING"),
    ]

    fields = [
        mock_bigquery_field("id", "INTEGER"),
        mock_bigquery_field("address", "RECORD", fields=nested_fields),
    ]
    mock_table = mock_table_with_schema(fields)
    mock_bigquery_client.get_table.return_value = mock_table

    schema = get_table_schema(mock_bigquery_client, "project.dataset.table")

    assert schema["id"] == "INTEGER"
    assert "RECORD<" in schema["address"]
    assert "street:STRING" in schema["address"]
    assert "city:STRING" in schema["address"]
    assert "zip:STRING" in schema["address"]


@pytest.mark.unit
@pytest.mark.bq
def test_get_table_schema_error_handling(mock_bigquery_client, capsys):
    """Test error handling when table fetch fails"""
    mock_bigquery_client.get_table.side_effect = Exception("Table not found")

    with pytest.raises(SystemExit) as exc_info:
        get_table_schema(mock_bigquery_client, "project.dataset.nonexistent")

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error fetching schema" in captured.err
    assert "Table not found" in captured.err


# --- compare_schemas() Tests ---

@pytest.mark.unit
def test_compare_schemas_identical(simple_schema):
    """Test comparing identical schemas"""
    only_in_a, only_in_b, type_changes = compare_schemas(simple_schema, simple_schema)

    assert len(only_in_a) == 0
    assert len(only_in_b) == 0
    assert len(type_changes) == 0


@pytest.mark.unit
def test_compare_schemas_added_fields():
    """Test schema comparison when fields are added"""
    schema_a = {
        "id": "INTEGER",
        "name": "STRING",
    }
    schema_b = {
        "id": "INTEGER",
        "name": "STRING",
        "email": "STRING",
        "age": "INTEGER",
    }

    only_in_a, only_in_b, type_changes = compare_schemas(schema_a, schema_b)

    assert len(only_in_a) == 0
    assert only_in_b == {"email", "age"}
    assert len(type_changes) == 0


@pytest.mark.unit
def test_compare_schemas_removed_fields():
    """Test schema comparison when fields are removed"""
    schema_a = {
        "id": "INTEGER",
        "name": "STRING",
        "email": "STRING",
    }
    schema_b = {
        "id": "INTEGER",
        "name": "STRING",
    }

    only_in_a, only_in_b, type_changes = compare_schemas(schema_a, schema_b)

    assert only_in_a == {"email"}
    assert len(only_in_b) == 0
    assert len(type_changes) == 0


@pytest.mark.unit
def test_compare_schemas_type_changes():
    """Test schema comparison with type changes"""
    schema_a = {
        "id": "INTEGER",
        "name": "STRING",
        "amount": "FLOAT",
    }
    schema_b = {
        "id": "STRING",  # Changed from INTEGER
        "name": "STRING",
        "amount": "NUMERIC",  # Changed from FLOAT
    }

    only_in_a, only_in_b, type_changes = compare_schemas(schema_a, schema_b)

    assert len(only_in_a) == 0
    assert len(only_in_b) == 0
    assert type_changes == {
        "id": ("INTEGER", "STRING"),
        "amount": ("FLOAT", "NUMERIC"),
    }


@pytest.mark.unit
def test_compare_schemas_mode_changes():
    """Test schema comparison with field mode changes"""
    schema_a = {
        "id": "INTEGER",
        "tags": "STRING",
    }
    schema_b = {
        "id": "INTEGER (REQUIRED)",
        "tags": "STRING (REPEATED)",
    }

    only_in_a, only_in_b, type_changes = compare_schemas(schema_a, schema_b)

    assert len(only_in_a) == 0
    assert len(only_in_b) == 0
    assert type_changes == {
        "id": ("INTEGER", "INTEGER (REQUIRED)"),
        "tags": ("STRING", "STRING (REPEATED)"),
    }


@pytest.mark.unit
def test_compare_schemas_complex_differences():
    """Test schema comparison with multiple types of differences"""
    schema_a = {
        "id": "INTEGER",
        "name": "STRING",
        "old_field": "STRING",
        "changed_type": "FLOAT",
    }
    schema_b = {
        "id": "INTEGER",
        "name": "STRING (REQUIRED)",
        "new_field": "STRING",
        "changed_type": "NUMERIC",
    }

    only_in_a, only_in_b, type_changes = compare_schemas(schema_a, schema_b)

    assert only_in_a == {"old_field"}
    assert only_in_b == {"new_field"}
    assert type_changes == {
        "name": ("STRING", "STRING (REQUIRED)"),
        "changed_type": ("FLOAT", "NUMERIC"),
    }


@pytest.mark.unit
def test_compare_schemas_empty():
    """Test comparing empty schemas"""
    only_in_a, only_in_b, type_changes = compare_schemas({}, {})

    assert len(only_in_a) == 0
    assert len(only_in_b) == 0
    assert len(type_changes) == 0


# --- print_text_report() Tests ---

@pytest.mark.unit
def test_print_text_report_identical(capsys):
    """Test text report for identical schemas"""
    schema = {"id": "INTEGER", "name": "STRING"}

    print_text_report("table_a", "table_b", set(), set(), {}, schema, schema)

    captured = capsys.readouterr()
    assert "Schema Comparison" in captured.out
    assert "table_a" in captured.out
    assert "table_b" in captured.out
    assert "Schemas are identical" in captured.out


@pytest.mark.unit
def test_print_text_report_with_differences(capsys):
    """Test text report with schema differences"""
    schema_a = {"id": "INTEGER", "old_field": "STRING"}
    schema_b = {"id": "STRING", "new_field": "INTEGER"}

    only_in_a = {"old_field"}
    only_in_b = {"new_field"}
    type_changes = {"id": ("INTEGER", "STRING")}

    print_text_report("table_a", "table_b", only_in_a, only_in_b, type_changes, schema_a, schema_b)

    captured = capsys.readouterr()
    assert "Fields only in Table A" in captured.out
    assert "old_field" in captured.out
    assert "Fields only in Table B" in captured.out
    assert "new_field" in captured.out
    assert "Fields with type changes" in captured.out
    assert "Schemas differ" in captured.out


@pytest.mark.unit
def test_print_text_report_summary_counts(capsys):
    """Test text report includes correct summary counts"""
    schema_a = {"id": "INTEGER", "field1": "STRING", "field2": "STRING"}
    schema_b = {"id": "STRING", "field3": "INTEGER", "field4": "INTEGER"}

    only_in_a = {"field1", "field2"}
    only_in_b = {"field3", "field4"}
    type_changes = {"id": ("INTEGER", "STRING")}

    print_text_report("table_a", "table_b", only_in_a, only_in_b, type_changes, schema_a, schema_b)

    captured = capsys.readouterr()
    assert "Fields only in A: 2" in captured.out
    assert "Fields only in B: 2" in captured.out
    assert "Type changes: 1" in captured.out


# --- print_json_report() Tests ---

@pytest.mark.unit
def test_print_json_report_identical(capsys):
    """Test JSON report for identical schemas"""
    schema = {"id": "INTEGER", "name": "STRING"}

    print_json_report("table_a", "table_b", set(), set(), {}, schema, schema)

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert report["table_a"] == "table_a"
    assert report["table_b"] == "table_b"
    assert report["identical"] is True
    assert len(report["only_in_a"]) == 0
    assert len(report["only_in_b"]) == 0
    assert len(report["type_changes"]) == 0
    assert report["summary"]["fields_only_in_a"] == 0
    assert report["summary"]["fields_only_in_b"] == 0
    assert report["summary"]["type_changes"] == 0


@pytest.mark.unit
def test_print_json_report_with_differences(capsys):
    """Test JSON report with schema differences"""
    schema_a = {"id": "INTEGER", "old_field": "STRING"}
    schema_b = {"id": "STRING", "new_field": "INTEGER"}

    only_in_a = {"old_field"}
    only_in_b = {"new_field"}
    type_changes = {"id": ("INTEGER", "STRING")}

    print_json_report("table_a", "table_b", only_in_a, only_in_b, type_changes, schema_a, schema_b)

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert report["identical"] is False
    assert len(report["only_in_a"]) == 1
    assert report["only_in_a"][0]["field"] == "old_field"
    assert report["only_in_a"][0]["type"] == "STRING"
    assert len(report["only_in_b"]) == 1
    assert report["only_in_b"][0]["field"] == "new_field"
    assert len(report["type_changes"]) == 1
    assert report["type_changes"][0]["field"] == "id"
    assert report["type_changes"][0]["type_a"] == "INTEGER"
    assert report["type_changes"][0]["type_b"] == "STRING"


@pytest.mark.unit
def test_print_json_report_structure(capsys):
    """Test JSON report has correct structure"""
    schema_a = {"id": "INTEGER"}
    schema_b = {"id": "INTEGER", "name": "STRING"}

    only_in_a = set()
    only_in_b = {"name"}
    type_changes = {}

    print_json_report("table_a", "table_b", only_in_a, only_in_b, type_changes, schema_a, schema_b)

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    # Verify all required keys exist
    required_keys = ["table_a", "table_b", "only_in_a", "only_in_b", "type_changes", "identical", "summary"]
    for key in required_keys:
        assert key in report

    assert "fields_only_in_a" in report["summary"]
    assert "fields_only_in_b" in report["summary"]
    assert "type_changes" in report["summary"]


# --- main() Integration Tests ---

@pytest.mark.unit
@pytest.mark.bq
def test_main_identical_schemas_exit_code(mock_bigquery_client, mock_bigquery_field, mock_table_with_schema, monkeypatch):
    """Test main() exits with 0 for identical schemas"""
    fields = [mock_bigquery_field("id", "INTEGER")]
    mock_table = mock_table_with_schema(fields)
    mock_bigquery_client.get_table.return_value = mock_table

    with patch("google.cloud.bigquery.Client", return_value=mock_bigquery_client):
        with patch("sys.argv", ["bq-schema-diff", "table_a", "table_b"]):
            with pytest.raises(SystemExit) as exc_info:
                bq_schema_diff.main()

    assert exc_info.value.code == 0


@pytest.mark.unit
@pytest.mark.bq
def test_main_different_schemas_exit_code(mock_bigquery_client, mock_bigquery_field, mock_table_with_schema):
    """Test main() exits with 1 for different schemas"""
    # Return different schemas for each table
    fields_a = [mock_bigquery_field("id", "INTEGER")]
    fields_b = [mock_bigquery_field("id", "STRING")]
    table_a = mock_table_with_schema(fields_a)
    table_b = mock_table_with_schema(fields_b)

    mock_bigquery_client.get_table.side_effect = [table_a, table_b]

    with patch("google.cloud.bigquery.Client", return_value=mock_bigquery_client):
        with patch("sys.argv", ["bq-schema-diff", "table_a", "table_b"]):
            with pytest.raises(SystemExit) as exc_info:
                bq_schema_diff.main()

    assert exc_info.value.code == 1


@pytest.mark.unit
@pytest.mark.bq
def test_main_json_format(mock_bigquery_client, mock_bigquery_field, mock_table_with_schema, capsys):
    """Test main() with JSON output format"""
    fields = [mock_bigquery_field("id", "INTEGER")]
    mock_table = mock_table_with_schema(fields)
    mock_bigquery_client.get_table.return_value = mock_table

    with patch("google.cloud.bigquery.Client", return_value=mock_bigquery_client):
        with patch("sys.argv", ["bq-schema-diff", "table_a", "table_b", "--format=json"]):
            with pytest.raises(SystemExit):
                bq_schema_diff.main()

    captured = capsys.readouterr()
    # Should be valid JSON
    report = json.loads(captured.out)
    assert "table_a" in report
    assert "table_b" in report


@pytest.mark.unit
@pytest.mark.bq
def test_main_text_format_default(mock_bigquery_client, mock_bigquery_field, mock_table_with_schema, capsys):
    """Test main() defaults to text format"""
    fields = [mock_bigquery_field("id", "INTEGER")]
    mock_table = mock_table_with_schema(fields)
    mock_bigquery_client.get_table.return_value = mock_table

    with patch("google.cloud.bigquery.Client", return_value=mock_bigquery_client):
        with patch("sys.argv", ["bq-schema-diff", "table_a", "table_b"]):
            with pytest.raises(SystemExit):
                bq_schema_diff.main()

    captured = capsys.readouterr()
    # Should have text format markers
    assert "Schema Comparison" in captured.out
    assert "Schemas are identical" in captured.out
