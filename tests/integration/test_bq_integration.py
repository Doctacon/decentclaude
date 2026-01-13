"""
Integration tests for BigQuery utilities

Tests interactions between BigQuery utilities and mocked BigQuery client.
"""
import pytest
import sys
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path

# Add bin directory to path
bin_path = Path(__file__).parent.parent.parent / "bin" / "data-utils"
sys.path.insert(0, str(bin_path))


# --- Integration Test Fixtures ---

@pytest.fixture
def complete_bigquery_environment(mock_bigquery_client, mock_table, mock_schema):
    """Create a complete BigQuery testing environment"""
    mock_table.schema = mock_schema
    mock_bigquery_client.get_table.return_value = mock_table

    # Mock query results for various operations
    mock_query_job = MagicMock()
    mock_query_job.total_bytes_processed = 1024 ** 3  # 1 GB
    mock_query_job.state = "DONE"
    mock_query_job.error_result = None

    mock_bigquery_client.query.return_value = mock_query_job

    return {
        "client": mock_bigquery_client,
        "table": mock_table,
        "schema": mock_schema,
        "query_job": mock_query_job
    }


@pytest.fixture
def multi_table_environment(mock_bigquery_client):
    """Create environment with multiple tables for lineage testing"""
    tables = {}

    # Source table
    source_table = MagicMock()
    source_table.table_id = "source_table"
    source_table.table_type = "TABLE"
    source_table.num_rows = 10000
    source_table.num_bytes = 1024 ** 3
    tables["project.dataset.source"] = source_table

    # View that depends on source
    view_table = MagicMock()
    view_table.table_id = "aggregated_view"
    view_table.table_type = "VIEW"
    view_table.view_query = "SELECT * FROM `project.dataset.source`"
    tables["project.dataset.view"] = view_table

    # Downstream view
    downstream_view = MagicMock()
    downstream_view.table_id = "final_view"
    downstream_view.table_type = "VIEW"
    downstream_view.view_query = "SELECT * FROM `project.dataset.view`"
    tables["project.dataset.downstream"] = downstream_view

    def get_table_side_effect(table_id):
        return tables.get(table_id, tables["project.dataset.source"])

    mock_bigquery_client.get_table.side_effect = get_table_side_effect

    return {
        "client": mock_bigquery_client,
        "tables": tables
    }


# --- Schema Diff Integration Tests ---

@pytest.mark.integration
@pytest.mark.bq
def test_schema_diff_workflow(complete_bigquery_environment):
    """Test complete schema diff workflow"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bq_schema_diff", bin_path / "bq-schema-diff")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    client = complete_bigquery_environment["client"]

    # Get schemas for two tables
    schema_a = module.get_table_schema(client, "project.dataset.table_a")
    schema_b = module.get_table_schema(client, "project.dataset.table_b")

    # Compare
    only_in_a, only_in_b, type_changes = module.compare_schemas(schema_a, schema_b)

    # Verify results structure
    assert isinstance(only_in_a, set)
    assert isinstance(only_in_b, set)
    assert isinstance(type_changes, dict)


@pytest.mark.integration
@pytest.mark.bq
def test_schema_diff_with_real_differences(mock_bigquery_client):
    """Test schema diff detecting real differences"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bq_schema_diff", bin_path / "bq-schema-diff")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Create two different table schemas
    field_a1 = MagicMock()
    field_a1.name = "id"
    field_a1.field_type = "INTEGER"
    field_a1.mode = "REQUIRED"

    field_a2 = MagicMock()
    field_a2.name = "old_field"
    field_a2.field_type = "STRING"
    field_a2.mode = "NULLABLE"

    field_b1 = MagicMock()
    field_b1.name = "id"
    field_b1.field_type = "STRING"  # Changed type
    field_b1.mode = "REQUIRED"

    field_b2 = MagicMock()
    field_b2.name = "new_field"
    field_b2.field_type = "STRING"
    field_b2.mode = "NULLABLE"

    table_a = MagicMock()
    table_a.schema = [field_a1, field_a2]

    table_b = MagicMock()
    table_b.schema = [field_b1, field_b2]

    def get_table_side_effect(table_id):
        if "table_a" in table_id:
            return table_a
        return table_b

    mock_bigquery_client.get_table.side_effect = get_table_side_effect

    schema_a = module.get_table_schema(mock_bigquery_client, "project.dataset.table_a")
    schema_b = module.get_table_schema(mock_bigquery_client, "project.dataset.table_b")

    only_in_a, only_in_b, type_changes = module.compare_schemas(schema_a, schema_b)

    # Should detect differences
    assert "old_field" in only_in_a
    assert "new_field" in only_in_b
    assert "id" in type_changes


# --- Query Cost Integration Tests ---

@pytest.mark.integration
@pytest.mark.bq
def test_query_cost_workflow(complete_bigquery_environment):
    """Test complete query cost estimation workflow"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bq_query_cost", bin_path / "bq-query-cost")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    client = complete_bigquery_environment["client"]
    query = "SELECT * FROM project.dataset.large_table"

    result = module.estimate_query_cost(client, query)

    # Verify cost calculation
    assert "bytes_processed" in result
    assert "gb_processed" in result
    assert "tb_processed" in result
    assert "estimated_cost_usd" in result
    assert result["cost_per_tb"] == 6.25
    assert result["pricing_model"] == "on-demand"


@pytest.mark.integration
@pytest.mark.bq
def test_query_cost_with_large_query(complete_bigquery_environment):
    """Test cost estimation for expensive query"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bq_query_cost", bin_path / "bq-query-cost")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    client = complete_bigquery_environment["client"]
    query_job = complete_bigquery_environment["query_job"]

    # Simulate large query (10 TB)
    query_job.total_bytes_processed = 1024 ** 4 * 10
    client.query.return_value = query_job

    result = module.estimate_query_cost(client, "SELECT * FROM huge_table")

    # Cost should be high
    assert result["tb_processed"] == 10.0
    assert result["estimated_cost_usd"] == 62.5  # 10 TB * $6.25/TB

    # Cost category should be "Very High"
    category, _ = module.get_cost_category(result["estimated_cost_usd"])
    assert category == "Very High"


# --- Partition Info Integration Tests ---

@pytest.mark.integration
@pytest.mark.bq
def test_partition_info_workflow(mock_bigquery_client, mock_partitioned_table):
    """Test complete partition info workflow"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bq_partition_info", bin_path / "bq-partition-info")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    mock_bigquery_client.get_table.return_value = mock_partitioned_table

    # Mock partition query results
    mock_row1 = MagicMock()
    mock_row1.partition_id = "20240101"
    mock_row1.total_rows = 1000
    mock_row1.total_logical_bytes = 1024 ** 3
    mock_row1.total_billable_bytes = 1024 ** 3
    mock_row1.last_modified_time = None

    mock_row2 = MagicMock()
    mock_row2.partition_id = "20240102"
    mock_row2.total_rows = 2000
    mock_row2.total_logical_bytes = 2 * 1024 ** 3
    mock_row2.total_billable_bytes = 2 * 1024 ** 3
    mock_row2.last_modified_time = None

    mock_bigquery_client.query.return_value = [mock_row1, mock_row2]

    result = module.get_partition_info(mock_bigquery_client, "project.dataset.table")

    # Verify partition analysis
    assert result["is_partitioned"] is True
    assert "TIME" in result["partitioning_type"]
    assert len(result["partitions"]) == 2
    assert result["partition_count"] == 2


# --- Lineage Integration Tests ---

@pytest.mark.integration
@pytest.mark.bq
def test_lineage_workflow(multi_table_environment):
    """Test complete lineage exploration workflow"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bq_lineage", bin_path / "bq-lineage")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    client = multi_table_environment["client"]

    # Get upstream dependencies for view
    upstream = module.get_upstream_dependencies(
        client,
        "project.dataset.view",
        "project.dataset"
    )

    # Should find source table
    assert isinstance(upstream, list)
    assert any("source" in dep for dep in upstream)


@pytest.mark.integration
@pytest.mark.bq
def test_lineage_chain(multi_table_environment):
    """Test lineage across multiple levels"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bq_lineage", bin_path / "bq-lineage")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    client = multi_table_environment["client"]

    # Get dependencies for final view
    upstream = module.get_upstream_dependencies(
        client,
        "project.dataset.downstream",
        "project.dataset"
    )

    # Should find intermediate view
    assert isinstance(upstream, list)
    assert any("view" in dep for dep in upstream)


# --- Cross-Utility Integration Tests ---

@pytest.mark.integration
@pytest.mark.bq
@pytest.mark.slow
def test_full_table_analysis_workflow(complete_bigquery_environment):
    """Test analyzing a table using multiple utilities"""
    # This would be a workflow where:
    # 1. Get table schema (schema-diff)
    # 2. Check partition info (partition-info)
    # 3. Analyze lineage (lineage)
    # 4. Estimate query cost (query-cost)

    import importlib.util

    # Load all utilities
    schema_diff = importlib.util.module_from_spec(
        importlib.util.spec_from_file_location("bq_schema_diff", bin_path / "bq-schema-diff")
    )
    spec = importlib.util.spec_from_file_location("bq_schema_diff", bin_path / "bq-schema-diff")
    schema_diff = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schema_diff)

    client = complete_bigquery_environment["client"]
    table_id = "project.dataset.table"

    # Step 1: Get schema
    schema = schema_diff.get_table_schema(client, table_id)
    assert isinstance(schema, dict)

    # Step 2: Verify we can use the same client for multiple operations
    # This ensures our mocking is consistent
    schema2 = schema_diff.get_table_schema(client, table_id)
    assert schema == schema2


# --- Error Recovery Integration Tests ---

@pytest.mark.integration
@pytest.mark.bq
def test_utilities_handle_api_errors_gracefully(mock_bigquery_client):
    """Test that utilities handle BigQuery API errors appropriately"""
    import importlib.util

    # Make client raise errors
    mock_bigquery_client.get_table.side_effect = Exception("API Error: Table not found")

    # Test schema-diff error handling
    spec = importlib.util.spec_from_file_location("bq_schema_diff", bin_path / "bq-schema-diff")
    schema_diff = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(schema_diff)

    with pytest.raises(SystemExit):
        schema_diff.get_table_schema(mock_bigquery_client, "nonexistent.table.id")


@pytest.mark.integration
@pytest.mark.bq
def test_utilities_validate_table_id_format(mock_bigquery_client):
    """Test that utilities validate table ID format"""
    import importlib.util

    spec = importlib.util.spec_from_file_location("bq_lineage", bin_path / "bq-lineage")
    lineage = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lineage)

    # Invalid table ID (missing parts)
    result = lineage.get_upstream_dependencies(
        mock_bigquery_client,
        "invalid_table_id",
        "dataset"
    )

    # Should handle gracefully
    assert result == []
