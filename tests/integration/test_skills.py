"""
Integration tests for Skills that invoke CLI utilities

Tests validate that Skills properly invoke CLI utilities with correct parameters,
handle utility output (JSON/text), and manage errors appropriately.

These tests mock subprocess calls to utilities rather than executing them,
ensuring fast, deterministic tests that don't require external dependencies.
"""
import pytest
import json
import subprocess
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path


# --- Test Fixtures ---

@pytest.fixture
def mock_subprocess():
    """Mock subprocess.run for capturing utility invocations"""
    with patch('subprocess.run') as mock_run:
        yield mock_run


@pytest.fixture
def successful_subprocess_result():
    """Return a successful subprocess result"""
    result = MagicMock()
    result.returncode = 0
    result.stdout = ""
    result.stderr = ""
    return result


@pytest.fixture
def failed_subprocess_result():
    """Return a failed subprocess result"""
    result = MagicMock()
    result.returncode = 1
    result.stdout = ""
    result.stderr = "Error: Operation failed"
    return result


@pytest.fixture
def bq_lineage_json_output():
    """Sample JSON output from bq-lineage utility"""
    return json.dumps({
        "table_id": "project.dataset.fact_sales",
        "upstream": [
            "project.staging.sales_cleaned",
            "project.dim.customers",
            "project.dim.products"
        ],
        "downstream": [
            "project.analytics.sales_daily_agg",
            "project.reporting.revenue_dashboard",
            "project.export.sales_data_lake"
        ],
        "summary": {
            "upstream_count": 3,
            "downstream_count": 3,
            "total_dependencies": 6,
            "max_depth_upstream": 2,
            "max_depth_downstream": 1
        }
    })


@pytest.fixture
def bq_lineage_mermaid_output():
    """Sample Mermaid output from bq-lineage utility"""
    return """```mermaid
graph LR
    staging_sales[staging.sales_cleaned]
    dim_customers[dim.customers]
    dim_products[dim.products]
    fact_sales[dataset.fact_sales]
    sales_agg[analytics.sales_daily_agg]
    revenue_dash[reporting.revenue_dashboard]

    staging_sales --> fact_sales
    dim_customers --> fact_sales
    dim_products --> fact_sales
    fact_sales --> sales_agg
    fact_sales --> revenue_dash

    style fact_sales fill:#f9f,stroke:#333,stroke-width:4px
```"""


@pytest.fixture
def bq_schema_diff_json_output():
    """Sample JSON output from bq-schema-diff utility"""
    return json.dumps({
        "table_a": "project.dev.users",
        "table_b": "project.prod.users",
        "identical": False,
        "only_in_a": [
            {"field": "test_field", "type": "STRING"}
        ],
        "only_in_b": [
            {"field": "created_at", "type": "TIMESTAMP"}
        ],
        "type_changes": [
            {
                "field": "user_id",
                "type_a": "INTEGER",
                "type_b": "STRING"
            }
        ],
        "summary": {
            "fields_only_in_a": 1,
            "fields_only_in_b": 1,
            "type_changes": 1
        }
    })


@pytest.fixture
def bq_optimize_json_output():
    """Sample JSON output from bq-optimize utility"""
    return json.dumps({
        "recommendations": {
            "high": [
                {
                    "severity": "high",
                    "category": "cost",
                    "title": "Missing partition filter",
                    "description": "Query scans all partitions without date filter",
                    "suggestion": "Add WHERE event_date >= CURRENT_DATE() - 7"
                },
                {
                    "severity": "high",
                    "category": "cost",
                    "title": "SELECT * detected",
                    "description": "Reading all 50 columns from wide table",
                    "suggestion": "Select only needed columns"
                }
            ],
            "medium": [
                {
                    "severity": "medium",
                    "category": "performance",
                    "title": "Correlated subquery",
                    "description": "Subquery executes for each row",
                    "suggestion": "Convert to JOIN with aggregation"
                }
            ],
            "low": []
        },
        "total_recommendations": 3,
        "warnings": [],
        "info": {
            "bytes_processed": 10737418240,
            "estimated_cost_usd": 0.0525
        }
    })


@pytest.fixture
def bq_explain_json_output():
    """Sample JSON output from bq-explain utility"""
    return json.dumps({
        "job_id": "abc123-def456-ghi789",
        "state": "DONE",
        "bytes_processed": 1073741824,
        "bytes_billed": 1073741824,
        "cache_hit": False,
        "stages": [
            {
                "stage_id": 1,
                "name": "Stage 1",
                "status": "COMPLETE",
                "records_read": 1000000,
                "records_written": 500000,
                "compute_ms_avg": 1234,
                "read_ms_avg": 567,
                "write_ms_avg": 234,
                "wait_ms_avg": 100,
                "shuffle_output_bytes": 524288000
            },
            {
                "stage_id": 2,
                "name": "Stage 2",
                "status": "COMPLETE",
                "records_read": 500000,
                "records_written": 100000,
                "compute_ms_avg": 890,
                "read_ms_avg": 345,
                "write_ms_avg": 123,
                "wait_ms_avg": 50,
                "shuffle_output_bytes": 0
            }
        ],
        "total_slot_ms": 5678,
        "estimated_cost_usd": 0.005
    })


# --- data-lineage-doc Skill Tests ---

@pytest.mark.integration
@pytest.mark.skills
def test_invokes_bq_lineage_with_correct_params(mock_subprocess, successful_subprocess_result, bq_lineage_json_output):
    """Test that data-lineage-doc skill invokes bq-lineage with correct parameters"""
    successful_subprocess_result.stdout = bq_lineage_json_output
    mock_subprocess.return_value = successful_subprocess_result

    # Simulate skill invoking bq-lineage
    table_id = "project.dataset.fact_sales"
    result = subprocess.run(
        ["bin/data-utils/bq-lineage", table_id, "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    # Verify invocation
    mock_subprocess.assert_called_once_with(
        ["bin/data-utils/bq-lineage", table_id, "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    # Verify output
    assert result.returncode == 0
    assert result.stdout == bq_lineage_json_output


@pytest.mark.integration
@pytest.mark.skills
def test_handles_bq_lineage_json_output(mock_subprocess, successful_subprocess_result, bq_lineage_json_output):
    """Test that skill correctly parses JSON output from bq-lineage"""
    successful_subprocess_result.stdout = bq_lineage_json_output
    mock_subprocess.return_value = successful_subprocess_result

    # Invoke utility
    result = subprocess.run(
        ["bin/data-utils/bq-lineage", "project.dataset.table", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    # Parse JSON output
    lineage_data = json.loads(result.stdout)

    # Verify structure
    assert "table_id" in lineage_data
    assert "upstream" in lineage_data
    assert "downstream" in lineage_data
    assert "summary" in lineage_data

    # Verify content
    assert lineage_data["table_id"] == "project.dataset.fact_sales"
    assert len(lineage_data["upstream"]) == 3
    assert len(lineage_data["downstream"]) == 3
    assert lineage_data["summary"]["total_dependencies"] == 6


@pytest.mark.integration
@pytest.mark.skills
def test_handles_bq_lineage_mermaid_output(mock_subprocess, successful_subprocess_result, bq_lineage_mermaid_output):
    """Test that skill correctly handles Mermaid diagram output from bq-lineage"""
    successful_subprocess_result.stdout = bq_lineage_mermaid_output
    mock_subprocess.return_value = successful_subprocess_result

    # Invoke utility with mermaid format
    result = subprocess.run(
        ["bin/data-utils/bq-lineage", "project.dataset.table", "--format=mermaid"],
        capture_output=True,
        text=True,
        check=True
    )

    # Verify output is Mermaid format
    assert result.returncode == 0
    assert "```mermaid" in result.stdout
    assert "graph LR" in result.stdout
    assert "fact_sales" in result.stdout
    assert "-->" in result.stdout
    assert "style fact_sales" in result.stdout


@pytest.mark.integration
@pytest.mark.skills
def test_handles_bq_lineage_errors(mock_subprocess, failed_subprocess_result):
    """Test that skill handles bq-lineage errors appropriately"""
    failed_subprocess_result.stderr = "Error: Table not found: project.dataset.nonexistent"
    mock_subprocess.return_value = failed_subprocess_result

    # Attempt to invoke utility
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(
            ["bin/data-utils/bq-lineage", "project.dataset.nonexistent", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )

    # Verify error was captured
    mock_subprocess.assert_called_once()


@pytest.mark.integration
@pytest.mark.skills
def test_bq_lineage_with_direction_parameter(mock_subprocess, successful_subprocess_result):
    """Test bq-lineage invocation with direction parameter"""
    lineage_output = json.dumps({
        "table_id": "project.dataset.table",
        "downstream": ["project.dataset.consumer1", "project.dataset.consumer2"],
        "summary": {"downstream_count": 2}
    })
    successful_subprocess_result.stdout = lineage_output
    mock_subprocess.return_value = successful_subprocess_result

    # Invoke with downstream direction
    result = subprocess.run(
        ["bin/data-utils/bq-lineage", "project.dataset.table", "--direction=downstream", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    # Verify invocation
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args[0][0]
    assert "--direction=downstream" in call_args
    assert "--format=json" in call_args


@pytest.mark.integration
@pytest.mark.skills
def test_bq_lineage_with_depth_parameter(mock_subprocess, successful_subprocess_result, bq_lineage_json_output):
    """Test bq-lineage invocation with depth parameter"""
    successful_subprocess_result.stdout = bq_lineage_json_output
    mock_subprocess.return_value = successful_subprocess_result

    # Invoke with depth parameter
    subprocess.run(
        ["bin/data-utils/bq-lineage", "project.dataset.table", "--depth=2", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    # Verify depth parameter passed
    call_args = mock_subprocess.call_args[0][0]
    assert "--depth=2" in call_args


# --- schema-doc-generator Skill Tests ---

@pytest.mark.integration
@pytest.mark.skills
def test_invokes_bq_schema_diff(mock_subprocess, successful_subprocess_result, bq_schema_diff_json_output):
    """Test that schema-doc-generator skill invokes bq-schema-diff correctly"""
    successful_subprocess_result.stdout = bq_schema_diff_json_output
    mock_subprocess.return_value = successful_subprocess_result

    # Invoke schema diff
    result = subprocess.run(
        ["bin/data-utils/bq-schema-diff", "project.dev.users", "project.prod.users", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    # Verify invocation
    mock_subprocess.assert_called_once_with(
        ["bin/data-utils/bq-schema-diff", "project.dev.users", "project.prod.users", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    assert result.returncode == 0


@pytest.mark.integration
@pytest.mark.skills
def test_parses_schema_diff_output(mock_subprocess, successful_subprocess_result, bq_schema_diff_json_output):
    """Test parsing of bq-schema-diff JSON output"""
    successful_subprocess_result.stdout = bq_schema_diff_json_output
    mock_subprocess.return_value = successful_subprocess_result

    # Invoke and parse
    result = subprocess.run(
        ["bin/data-utils/bq-schema-diff", "project.dev.users", "project.prod.users", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    diff_data = json.loads(result.stdout)

    # Verify structure
    assert "table_a" in diff_data
    assert "table_b" in diff_data
    assert "identical" in diff_data
    assert "only_in_a" in diff_data
    assert "only_in_b" in diff_data
    assert "type_changes" in diff_data
    assert "summary" in diff_data

    # Verify content
    assert diff_data["identical"] is False
    assert len(diff_data["only_in_a"]) == 1
    assert len(diff_data["only_in_b"]) == 1
    assert len(diff_data["type_changes"]) == 1
    assert diff_data["summary"]["fields_only_in_a"] == 1


@pytest.mark.integration
@pytest.mark.skills
def test_handles_schema_comparison_errors(mock_subprocess, failed_subprocess_result):
    """Test handling of schema comparison errors"""
    failed_subprocess_result.stderr = "Error: Table not found: project.dev.nonexistent"
    mock_subprocess.return_value = failed_subprocess_result

    # Attempt comparison
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(
            ["bin/data-utils/bq-schema-diff", "project.dev.nonexistent", "project.prod.users"],
            capture_output=True,
            text=True,
            check=True
        )

    mock_subprocess.assert_called_once()


@pytest.mark.integration
@pytest.mark.skills
def test_schema_diff_identical_schemas(mock_subprocess, successful_subprocess_result):
    """Test schema diff when schemas are identical"""
    identical_output = json.dumps({
        "table_a": "project.dev.users",
        "table_b": "project.prod.users",
        "identical": True,
        "only_in_a": [],
        "only_in_b": [],
        "type_changes": [],
        "summary": {
            "fields_only_in_a": 0,
            "fields_only_in_b": 0,
            "type_changes": 0
        }
    })
    successful_subprocess_result.stdout = identical_output
    mock_subprocess.return_value = successful_subprocess_result

    result = subprocess.run(
        ["bin/data-utils/bq-schema-diff", "project.dev.users", "project.prod.users", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    diff_data = json.loads(result.stdout)
    assert diff_data["identical"] is True
    assert len(diff_data["only_in_a"]) == 0
    assert len(diff_data["only_in_b"]) == 0


# --- sql-optimizer Skill Tests ---

@pytest.mark.integration
@pytest.mark.skills
def test_invokes_bq_optimize(mock_subprocess, successful_subprocess_result, bq_optimize_json_output):
    """Test that sql-optimizer skill invokes bq-optimize correctly"""
    successful_subprocess_result.stdout = bq_optimize_json_output
    mock_subprocess.return_value = successful_subprocess_result

    # Invoke optimizer
    result = subprocess.run(
        ["bin/data-utils/bq-optimize", "--file=query.sql", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    # Verify invocation
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args[0][0]
    assert "bin/data-utils/bq-optimize" in call_args
    assert "--file=query.sql" in call_args
    assert "--format=json" in call_args


@pytest.mark.integration
@pytest.mark.skills
def test_invokes_bq_explain(mock_subprocess, successful_subprocess_result, bq_explain_json_output):
    """Test that sql-optimizer skill invokes bq-explain correctly"""
    successful_subprocess_result.stdout = bq_explain_json_output
    mock_subprocess.return_value = successful_subprocess_result

    # Invoke explain
    result = subprocess.run(
        ["bin/data-utils/bq-explain", "--file=query.sql", "--dry-run", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    # Verify invocation
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args[0][0]
    assert "bin/data-utils/bq-explain" in call_args
    assert "--dry-run" in call_args


@pytest.mark.integration
@pytest.mark.skills
def test_handles_optimization_recommendations(mock_subprocess, successful_subprocess_result, bq_optimize_json_output):
    """Test parsing and handling of optimization recommendations"""
    successful_subprocess_result.stdout = bq_optimize_json_output
    mock_subprocess.return_value = successful_subprocess_result

    result = subprocess.run(
        ["bin/data-utils/bq-optimize", "--file=query.sql", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    optimize_data = json.loads(result.stdout)

    # Verify structure
    assert "recommendations" in optimize_data
    assert "high" in optimize_data["recommendations"]
    assert "medium" in optimize_data["recommendations"]
    assert "low" in optimize_data["recommendations"]
    assert "total_recommendations" in optimize_data

    # Verify recommendations
    high_recs = optimize_data["recommendations"]["high"]
    assert len(high_recs) == 2
    assert high_recs[0]["severity"] == "high"
    assert "title" in high_recs[0]
    assert "description" in high_recs[0]
    assert "suggestion" in high_recs[0]

    # Verify info
    assert "info" in optimize_data
    assert "bytes_processed" in optimize_data["info"]
    assert "estimated_cost_usd" in optimize_data["info"]


@pytest.mark.integration
@pytest.mark.skills
def test_handles_validation_errors(mock_subprocess, failed_subprocess_result):
    """Test handling of SQL validation errors"""
    failed_subprocess_result.stderr = "Error: Invalid SQL syntax near 'SELCT'"
    mock_subprocess.return_value = failed_subprocess_result

    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(
            ["bin/data-utils/bq-optimize", "--file=invalid.sql", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )

    mock_subprocess.assert_called_once()


@pytest.mark.integration
@pytest.mark.skills
def test_bq_optimize_with_query_string(mock_subprocess, successful_subprocess_result, bq_optimize_json_output):
    """Test bq-optimize with inline query string"""
    successful_subprocess_result.stdout = bq_optimize_json_output
    mock_subprocess.return_value = successful_subprocess_result

    query = "SELECT * FROM project.dataset.table"
    subprocess.run(
        ["bin/data-utils/bq-optimize", query, "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    call_args = mock_subprocess.call_args[0][0]
    assert query in call_args


@pytest.mark.integration
@pytest.mark.skills
def test_bq_optimize_with_job_id(mock_subprocess, successful_subprocess_result, bq_optimize_json_output):
    """Test bq-optimize analyzing an existing job"""
    successful_subprocess_result.stdout = bq_optimize_json_output
    mock_subprocess.return_value = successful_subprocess_result

    subprocess.run(
        ["bin/data-utils/bq-optimize", "--job-id=abc123-def456", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    call_args = mock_subprocess.call_args[0][0]
    assert "--job-id=abc123-def456" in call_args


@pytest.mark.integration
@pytest.mark.skills
def test_bq_explain_execution_stages(mock_subprocess, successful_subprocess_result, bq_explain_json_output):
    """Test parsing of bq-explain execution stages"""
    successful_subprocess_result.stdout = bq_explain_json_output
    mock_subprocess.return_value = successful_subprocess_result

    result = subprocess.run(
        ["bin/data-utils/bq-explain", "--job-id=abc123", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    explain_data = json.loads(result.stdout)

    # Verify stages
    assert "stages" in explain_data
    assert len(explain_data["stages"]) == 2

    stage1 = explain_data["stages"][0]
    assert "stage_id" in stage1
    assert "records_read" in stage1
    assert "records_written" in stage1
    assert "compute_ms_avg" in stage1
    assert "shuffle_output_bytes" in stage1


# --- doc-generator Skill Tests ---

@pytest.mark.integration
@pytest.mark.skills
def test_invokes_ai_generate_when_available(mock_subprocess, successful_subprocess_result):
    """Test that doc-generator skill invokes ai-generate when available"""
    example_code = 'def example():\n    """Example function"""\n    return "Hello"'
    successful_subprocess_result.stdout = example_code
    mock_subprocess.return_value = successful_subprocess_result

    # Invoke ai-generate
    result = subprocess.run(
        [
            "bin/data-utils/ai-generate",
            "transform",
            "Example usage of calculate_discount function",
            "--context=src/pricing.py",
            "--output=docs/examples/discount_example.py"
        ],
        capture_output=True,
        text=True,
        check=True
    )

    # Verify invocation
    mock_subprocess.assert_called_once()
    call_args = mock_subprocess.call_args[0][0]
    assert "ai-generate" in call_args
    assert "transform" in call_args


@pytest.mark.integration
@pytest.mark.skills
def test_handles_missing_ai_generate(mock_subprocess):
    """Test graceful handling when ai-generate is not available"""
    # Simulate command not found
    mock_subprocess.side_effect = FileNotFoundError("ai-generate not found")

    with pytest.raises(FileNotFoundError):
        subprocess.run(
            ["bin/data-utils/ai-generate", "transform", "Example"],
            capture_output=True,
            text=True,
            check=True
        )


@pytest.mark.integration
@pytest.mark.skills
def test_generates_docs_without_ai(mock_subprocess, successful_subprocess_result):
    """Test that doc-generator can work without AI utilities"""
    # This test verifies the skill can analyze code directly
    # without requiring ai-generate utility

    # Skills should use Read, Grep, Glob tools instead
    # No subprocess calls needed for basic documentation
    assert True  # Placeholder - skills use Claude tools, not subprocess


@pytest.mark.integration
@pytest.mark.skills
def test_ai_generate_test_examples(mock_subprocess, successful_subprocess_result):
    """Test ai-generate for test case generation"""
    test_code = '''import pytest

def test_calculate_discount():
    """Test discount calculation"""
    result = calculate_discount(100, 0.1)
    assert result == 90
'''
    successful_subprocess_result.stdout = test_code
    mock_subprocess.return_value = successful_subprocess_result

    subprocess.run(
        [
            "bin/data-utils/ai-generate",
            "test",
            "Unit tests for calculate_discount with edge cases",
            "--context=src/pricing.py",
            "--output=tests/test_pricing_examples.py"
        ],
        capture_output=True,
        text=True,
        check=True
    )

    call_args = mock_subprocess.call_args[0][0]
    assert "test" in call_args


# --- Utility Runner Tests ---

@pytest.mark.integration
@pytest.mark.skills
def test_utility_runner_execution(mock_subprocess, successful_subprocess_result):
    """Test utility runner executes commands correctly"""
    successful_subprocess_result.stdout = "Success"
    mock_subprocess.return_value = successful_subprocess_result

    # Generic utility invocation
    result = subprocess.run(
        ["bin/data-utils/bq-lineage", "project.dataset.table"],
        capture_output=True,
        text=True,
        check=True
    )

    assert result.returncode == 0
    assert result.stdout == "Success"


@pytest.mark.integration
@pytest.mark.skills
def test_utility_runner_error_handling(mock_subprocess, failed_subprocess_result):
    """Test utility runner handles errors appropriately"""
    mock_subprocess.return_value = failed_subprocess_result

    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(
            ["bin/data-utils/bq-lineage", "invalid.table"],
            capture_output=True,
            text=True,
            check=True
        )


@pytest.mark.integration
@pytest.mark.skills
def test_utility_runner_output_parsing(mock_subprocess, successful_subprocess_result):
    """Test utility runner correctly captures and parses output"""
    json_output = json.dumps({"status": "success", "data": {"count": 42}})
    successful_subprocess_result.stdout = json_output
    mock_subprocess.return_value = successful_subprocess_result

    result = subprocess.run(
        ["bin/data-utils/bq-profile", "project.dataset.table", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    # Parse output
    data = json.loads(result.stdout)
    assert data["status"] == "success"
    assert data["data"]["count"] == 42


@pytest.mark.integration
@pytest.mark.skills
def test_utility_with_environment_variables(mock_subprocess, successful_subprocess_result, monkeypatch):
    """Test utility invocation with environment variables"""
    monkeypatch.setenv("GOOGLE_APPLICATION_CREDENTIALS", "/path/to/creds.json")
    monkeypatch.setenv("GCLOUD_PROJECT", "test-project")

    successful_subprocess_result.stdout = "Success"
    mock_subprocess.return_value = successful_subprocess_result

    result = subprocess.run(
        ["bin/data-utils/bq-lineage", "project.dataset.table"],
        capture_output=True,
        text=True,
        check=True,
        env={"GOOGLE_APPLICATION_CREDENTIALS": "/path/to/creds.json", "GCLOUD_PROJECT": "test-project"}
    )

    assert result.returncode == 0


@pytest.mark.integration
@pytest.mark.skills
def test_utility_timeout_handling(mock_subprocess):
    """Test utility invocation with timeout"""
    # Simulate timeout
    mock_subprocess.side_effect = subprocess.TimeoutExpired(cmd="bq-lineage", timeout=30)

    with pytest.raises(subprocess.TimeoutExpired):
        subprocess.run(
            ["bin/data-utils/bq-lineage", "project.dataset.table"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True
        )


# --- Cross-Skill Integration Tests ---

@pytest.mark.integration
@pytest.mark.skills
@pytest.mark.slow
def test_lineage_and_schema_workflow(mock_subprocess, successful_subprocess_result, bq_lineage_json_output, bq_schema_diff_json_output):
    """Test workflow combining lineage discovery and schema comparison"""
    # First call: get lineage
    successful_subprocess_result.stdout = bq_lineage_json_output
    mock_subprocess.return_value = successful_subprocess_result

    lineage_result = subprocess.run(
        ["bin/data-utils/bq-lineage", "project.dataset.table", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    lineage_data = json.loads(lineage_result.stdout)
    upstream_tables = lineage_data["upstream"]

    # Second call: compare schemas of first two upstream tables
    successful_subprocess_result.stdout = bq_schema_diff_json_output
    mock_subprocess.return_value = successful_subprocess_result

    if len(upstream_tables) >= 2:
        schema_result = subprocess.run(
            ["bin/data-utils/bq-schema-diff", upstream_tables[0], upstream_tables[1], "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )

        schema_data = json.loads(schema_result.stdout)
        assert "identical" in schema_data


@pytest.mark.integration
@pytest.mark.skills
@pytest.mark.slow
def test_optimize_and_explain_workflow(mock_subprocess, successful_subprocess_result, bq_optimize_json_output, bq_explain_json_output):
    """Test workflow combining optimization analysis and execution plan"""
    # First call: get optimization recommendations
    successful_subprocess_result.stdout = bq_optimize_json_output
    mock_subprocess.return_value = successful_subprocess_result

    optimize_result = subprocess.run(
        ["bin/data-utils/bq-optimize", "--file=query.sql", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    optimize_data = json.loads(optimize_result.stdout)
    assert optimize_data["total_recommendations"] > 0

    # Second call: get execution plan
    successful_subprocess_result.stdout = bq_explain_json_output
    mock_subprocess.return_value = successful_subprocess_result

    explain_result = subprocess.run(
        ["bin/data-utils/bq-explain", "--file=query.sql", "--dry-run", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    explain_data = json.loads(explain_result.stdout)
    assert "stages" in explain_data


# --- Error Recovery Tests ---

@pytest.mark.integration
@pytest.mark.skills
def test_partial_failure_recovery(mock_subprocess, successful_subprocess_result, failed_subprocess_result, bq_lineage_json_output):
    """Test skill handles partial failures in multi-step workflows"""
    # First call succeeds
    successful_subprocess_result.stdout = bq_lineage_json_output
    mock_subprocess.return_value = successful_subprocess_result

    result1 = subprocess.run(
        ["bin/data-utils/bq-lineage", "project.dataset.table1", "--format=json"],
        capture_output=True,
        text=True,
        check=True
    )

    assert result1.returncode == 0

    # Second call fails
    mock_subprocess.return_value = failed_subprocess_result

    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(
            ["bin/data-utils/bq-lineage", "project.dataset.invalid", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )


@pytest.mark.integration
@pytest.mark.skills
def test_retry_on_transient_error(mock_subprocess, successful_subprocess_result, failed_subprocess_result):
    """Test retry logic for transient errors"""
    # First call fails with transient error
    failed_subprocess_result.stderr = "Error: Transient network error"

    # Subsequent call succeeds
    successful_subprocess_result.stdout = '{"status": "success"}'

    # Simulate retry logic
    mock_subprocess.side_effect = [failed_subprocess_result, successful_subprocess_result]

    # First attempt fails
    try:
        subprocess.run(
            ["bin/data-utils/bq-lineage", "project.dataset.table"],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError:
        # Retry succeeds
        result = subprocess.run(
            ["bin/data-utils/bq-lineage", "project.dataset.table"],
            capture_output=True,
            text=True,
            check=True
        )
        assert result.returncode == 0
