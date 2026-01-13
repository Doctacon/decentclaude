"""
Unit tests for bin/data-utils/bq-query-cost

Tests query cost estimation functionality for BigQuery.
"""
import pytest
import sys
import json
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Add bin directory to path for imports
bin_path = Path(__file__).parent.parent.parent / "bin" / "data-utils"
sys.path.insert(0, str(bin_path))

# Import after path modification
import importlib.util
spec = importlib.util.spec_from_file_location("bq_query_cost", bin_path / "bq-query-cost")
bq_query_cost = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bq_query_cost)

estimate_query_cost = bq_query_cost.estimate_query_cost
format_bytes = bq_query_cost.format_bytes
get_cost_category = bq_query_cost.get_cost_category
print_text_report = bq_query_cost.print_text_report
print_json_report = bq_query_cost.print_json_report


# --- format_bytes() Tests ---

@pytest.mark.unit
def test_format_bytes_small():
    """Test formatting small byte values"""
    assert format_bytes(100) == "100.00 B"
    assert format_bytes(512) == "512.00 B"
    assert format_bytes(1023) == "1023.00 B"


@pytest.mark.unit
def test_format_bytes_kilobytes():
    """Test formatting kilobyte values"""
    assert format_bytes(1024) == "1.00 KB"
    assert format_bytes(2048) == "2.00 KB"
    assert format_bytes(1536) == "1.50 KB"


@pytest.mark.unit
def test_format_bytes_megabytes():
    """Test formatting megabyte values"""
    assert format_bytes(1024 * 1024) == "1.00 MB"
    assert format_bytes(1024 * 1024 * 5) == "5.00 MB"
    assert format_bytes(1024 * 1024 * 1.5) == "1.50 MB"


@pytest.mark.unit
def test_format_bytes_gigabytes():
    """Test formatting gigabyte values"""
    assert format_bytes(1024 ** 3) == "1.00 GB"
    assert format_bytes(1024 ** 3 * 10) == "10.00 GB"
    assert format_bytes(1024 ** 3 * 2.5) == "2.50 GB"


@pytest.mark.unit
def test_format_bytes_terabytes():
    """Test formatting terabyte values"""
    assert format_bytes(1024 ** 4) == "1.00 TB"
    assert format_bytes(1024 ** 4 * 5) == "5.00 TB"


@pytest.mark.unit
def test_format_bytes_petabytes():
    """Test formatting petabyte values"""
    assert format_bytes(1024 ** 5) == "1.00 PB"
    assert format_bytes(1024 ** 5 * 2) == "2.00 PB"


@pytest.mark.unit
def test_format_bytes_exabytes():
    """Test formatting exabyte values"""
    assert format_bytes(1024 ** 6) == "1.00 EB"
    assert format_bytes(1024 ** 6 * 3) == "3.00 EB"


@pytest.mark.unit
def test_format_bytes_zero():
    """Test formatting zero bytes"""
    assert format_bytes(0) == "0.00 B"


# --- get_cost_category() Tests ---

@pytest.mark.unit
def test_get_cost_category_very_low():
    """Test very low cost category (< $0.01)"""
    category, color = get_cost_category(0.001)
    assert category == "Very Low"
    assert "32m" in color  # Green color code


@pytest.mark.unit
def test_get_cost_category_low():
    """Test low cost category ($0.01 - $0.10)"""
    category, color = get_cost_category(0.05)
    assert category == "Low"
    assert "32m" in color  # Green color code


@pytest.mark.unit
def test_get_cost_category_moderate():
    """Test moderate cost category ($0.10 - $1.00)"""
    category, color = get_cost_category(0.50)
    assert category == "Moderate"
    assert "33m" in color  # Yellow color code


@pytest.mark.unit
def test_get_cost_category_high():
    """Test high cost category ($1.00 - $10.00)"""
    category, color = get_cost_category(5.00)
    assert category == "High"
    assert "33m" in color  # Yellow color code


@pytest.mark.unit
def test_get_cost_category_very_high():
    """Test very high cost category (>= $10.00)"""
    category, color = get_cost_category(15.00)
    assert category == "Very High"
    assert "31m" in color  # Red color code


@pytest.mark.unit
def test_get_cost_category_boundaries():
    """Test cost category boundaries"""
    # Right at boundaries
    assert get_cost_category(0.01)[0] == "Low"
    assert get_cost_category(0.10)[0] == "Moderate"
    assert get_cost_category(1.00)[0] == "High"
    assert get_cost_category(10.00)[0] == "Very High"


# --- estimate_query_cost() Tests ---

@pytest.mark.unit
@pytest.mark.bq
def test_estimate_query_cost_basic(mock_bigquery_client, mock_query_job):
    """Test basic query cost estimation"""
    mock_query_job.total_bytes_processed = 1024 ** 3  # 1 GB
    mock_bigquery_client.query.return_value = mock_query_job

    result = estimate_query_cost(mock_bigquery_client, "SELECT * FROM table")

    assert result["bytes_processed"] == 1024 ** 3
    assert result["gb_processed"] == 1.0
    assert abs(result["tb_processed"] - (1.0 / 1024)) < 0.001
    assert result["pricing_model"] == "on-demand"
    assert result["cost_per_tb"] == 6.25
    assert result["query"] == "SELECT * FROM table"


@pytest.mark.unit
@pytest.mark.bq
def test_estimate_query_cost_large_query(mock_bigquery_client, mock_query_job):
    """Test cost estimation for large query (multiple TB)"""
    mock_query_job.total_bytes_processed = 1024 ** 4 * 5  # 5 TB
    mock_bigquery_client.query.return_value = mock_query_job

    result = estimate_query_cost(mock_bigquery_client, "SELECT * FROM large_table")

    assert result["tb_processed"] == 5.0
    assert result["estimated_cost_usd"] == 5.0 * 6.25  # 5 TB * $6.25/TB


@pytest.mark.unit
@pytest.mark.bq
def test_estimate_query_cost_small_query(mock_bigquery_client, mock_query_job):
    """Test cost estimation for small query (< 1 GB)"""
    mock_query_job.total_bytes_processed = 1024 ** 2 * 100  # 100 MB
    mock_bigquery_client.query.return_value = mock_query_job

    result = estimate_query_cost(mock_bigquery_client, "SELECT id FROM table LIMIT 10")

    assert result["bytes_processed"] == 1024 ** 2 * 100
    assert result["gb_processed"] < 1.0
    assert result["tb_processed"] < 0.001
    assert result["estimated_cost_usd"] < 0.01  # Should be very cheap


@pytest.mark.unit
@pytest.mark.bq
def test_estimate_query_cost_zero_bytes(mock_bigquery_client, mock_query_job):
    """Test cost estimation for query that processes 0 bytes"""
    mock_query_job.total_bytes_processed = 0
    mock_bigquery_client.query.return_value = mock_query_job

    result = estimate_query_cost(mock_bigquery_client, "SELECT 1")

    assert result["bytes_processed"] == 0
    assert result["gb_processed"] == 0
    assert result["tb_processed"] == 0
    assert result["estimated_cost_usd"] == 0


@pytest.mark.unit
@pytest.mark.bq
def test_estimate_query_cost_dry_run_config(mock_bigquery_client, mock_query_job):
    """Test that dry run configuration is set correctly"""
    mock_query_job.total_bytes_processed = 1000
    mock_bigquery_client.query.return_value = mock_query_job

    estimate_query_cost(mock_bigquery_client, "SELECT * FROM table")

    # Verify query was called with dry run configuration
    call_args = mock_bigquery_client.query.call_args
    job_config = call_args[1]['job_config']
    assert job_config.dry_run is True
    assert job_config.use_query_cache is False


@pytest.mark.unit
@pytest.mark.bq
def test_estimate_query_cost_error_handling(mock_bigquery_client, capsys):
    """Test error handling when query estimation fails"""
    mock_bigquery_client.query.side_effect = Exception("Invalid query syntax")

    with pytest.raises(SystemExit) as exc_info:
        estimate_query_cost(mock_bigquery_client, "INVALID SQL")

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error estimating query cost" in captured.err
    assert "Invalid query syntax" in captured.err


# --- print_text_report() Tests ---

@pytest.mark.unit
def test_print_text_report_basic(capsys):
    """Test basic text report output"""
    result = {
        "bytes_processed": 1024 ** 3,  # 1 GB
        "gb_processed": 1.0,
        "tb_processed": 1.0 / 1024,
        "estimated_cost_usd": (1.0 / 1024) * 6.25,
        "pricing_model": "on-demand",
        "cost_per_tb": 6.25,
        "query": "SELECT * FROM table"
    }

    print_text_report(result)

    captured = capsys.readouterr()
    assert "BigQuery Query Cost Estimation" in captured.out
    assert "Data Processed:" in captured.out
    assert "Cost Estimate:" in captured.out
    assert "1.00 GB" in captured.out
    assert "on-demand" in captured.out
    assert "SELECT * FROM table" in captured.out


@pytest.mark.unit
def test_print_text_report_large_query(capsys):
    """Test text report for expensive query"""
    result = {
        "bytes_processed": 1024 ** 4 * 10,  # 10 TB
        "gb_processed": 10 * 1024,
        "tb_processed": 10.0,
        "estimated_cost_usd": 10.0 * 6.25,  # $62.50
        "pricing_model": "on-demand",
        "cost_per_tb": 6.25,
        "query": "SELECT * FROM huge_table"
    }

    print_text_report(result)

    captured = capsys.readouterr()
    assert "10.000000" in captured.out  # TB value
    assert "Very High" in captured.out  # Cost category
    assert "SELECT * FROM huge_table" in captured.out


@pytest.mark.unit
def test_print_text_report_multiline_query(capsys):
    """Test text report with multiline query preview"""
    query = "\n".join([f"SELECT field{i} FROM table" for i in range(10)])
    result = {
        "bytes_processed": 1000,
        "gb_processed": 0.001,
        "tb_processed": 0.000001,
        "estimated_cost_usd": 0.00001,
        "pricing_model": "on-demand",
        "cost_per_tb": 6.25,
        "query": query
    }

    print_text_report(result)

    captured = capsys.readouterr()
    assert "Query Preview:" in captured.out
    assert "more lines" in captured.out  # Should show truncation message


@pytest.mark.unit
def test_print_text_report_notes_section(capsys):
    """Test that text report includes helpful notes"""
    result = {
        "bytes_processed": 1000,
        "gb_processed": 0.001,
        "tb_processed": 0.000001,
        "estimated_cost_usd": 0.00001,
        "pricing_model": "on-demand",
        "cost_per_tb": 6.25,
        "query": "SELECT 1"
    }

    print_text_report(result)

    captured = capsys.readouterr()
    assert "Notes:" in captured.out
    assert "First 1 TB per month is free" in captured.out
    assert "Cached query results are free" in captured.out
    assert "Flat-rate customers" in captured.out


# --- print_json_report() Tests ---

@pytest.mark.unit
def test_print_json_report_basic(capsys):
    """Test basic JSON report output"""
    result = {
        "bytes_processed": 1024 ** 3,  # 1 GB
        "gb_processed": 1.0,
        "tb_processed": 1.0 / 1024,
        "estimated_cost_usd": (1.0 / 1024) * 6.25,
        "pricing_model": "on-demand",
        "cost_per_tb": 6.25,
        "query": "SELECT * FROM table"
    }

    print_json_report(result)

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    assert report["bytes_processed"] == 1024 ** 3
    assert report["gb_processed"] == 1.0
    assert report["pricing_model"] == "on-demand"
    assert report["cost_per_tb"] == 6.25
    assert "human_readable" in report
    assert "category" in report


@pytest.mark.unit
def test_print_json_report_structure(capsys):
    """Test JSON report has correct structure"""
    result = {
        "bytes_processed": 5000000,
        "gb_processed": 0.005,
        "tb_processed": 0.000005,
        "estimated_cost_usd": 0.00003125,
        "pricing_model": "on-demand",
        "cost_per_tb": 6.25,
        "query": "SELECT * FROM table"
    }

    print_json_report(result)

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    # Verify all required keys exist
    required_keys = [
        "bytes_processed", "gb_processed", "tb_processed",
        "estimated_cost_usd", "human_readable", "pricing_model",
        "cost_per_tb", "category"
    ]
    for key in required_keys:
        assert key in report


@pytest.mark.unit
def test_print_json_report_cost_categories(capsys):
    """Test JSON report includes correct cost categories"""
    test_cases = [
        (0.005, "very_low"),
        (0.05, "low"),
        (0.5, "moderate"),
        (5.0, "high"),
        (50.0, "very_high"),
    ]

    for cost, expected_category in test_cases:
        result = {
            "bytes_processed": 100,
            "gb_processed": 0.1,
            "tb_processed": 0.0001,
            "estimated_cost_usd": cost,
            "pricing_model": "on-demand",
            "cost_per_tb": 6.25,
            "query": "SELECT 1"
        }

        print_json_report(result)
        captured = capsys.readouterr()
        report = json.loads(captured.out)

        assert report["category"] == expected_category


@pytest.mark.unit
def test_print_json_report_rounding(capsys):
    """Test JSON report rounds values appropriately"""
    result = {
        "bytes_processed": 123456789,
        "gb_processed": 0.114978,
        "tb_processed": 0.000112284,
        "estimated_cost_usd": 0.000701775,
        "pricing_model": "on-demand",
        "cost_per_tb": 6.25,
        "query": "SELECT * FROM table"
    }

    print_json_report(result)

    captured = capsys.readouterr()
    report = json.loads(captured.out)

    # Check rounding
    assert report["gb_processed"] == 0.1150  # 4 decimal places
    assert report["tb_processed"] == 0.000112  # 6 decimal places
    assert report["estimated_cost_usd"] == 0.0007  # 4 decimal places


# --- main() Integration Tests ---

@pytest.mark.unit
@pytest.mark.bq
def test_main_with_inline_query(mock_bigquery_client, mock_query_job, capsys):
    """Test main() with inline query argument"""
    mock_query_job.total_bytes_processed = 1024 ** 3
    mock_bigquery_client.query.return_value = mock_query_job

    with patch("google.cloud.bigquery.Client", return_value=mock_bigquery_client):
        with patch("sys.argv", ["bq-query-cost", "SELECT * FROM table"]):
            bq_query_cost.main()

    captured = capsys.readouterr()
    assert "BigQuery Query Cost Estimation" in captured.out


@pytest.mark.unit
@pytest.mark.bq
def test_main_with_file(mock_bigquery_client, mock_query_job, temp_sql_file, capsys):
    """Test main() with SQL file input"""
    mock_query_job.total_bytes_processed = 1024 ** 2
    mock_bigquery_client.query.return_value = mock_query_job

    with patch("google.cloud.bigquery.Client", return_value=mock_bigquery_client):
        with patch("sys.argv", ["bq-query-cost", f"--file={temp_sql_file}"]):
            bq_query_cost.main()

    captured = capsys.readouterr()
    assert "BigQuery Query Cost Estimation" in captured.out


@pytest.mark.unit
@pytest.mark.bq
def test_main_with_json_format(mock_bigquery_client, mock_query_job, capsys):
    """Test main() with JSON output format"""
    mock_query_job.total_bytes_processed = 1000
    mock_bigquery_client.query.return_value = mock_query_job

    with patch("google.cloud.bigquery.Client", return_value=mock_bigquery_client):
        with patch("sys.argv", ["bq-query-cost", "SELECT 1", "--format=json"]):
            bq_query_cost.main()

    captured = capsys.readouterr()
    # Should be valid JSON
    report = json.loads(captured.out)
    assert "bytes_processed" in report


@pytest.mark.unit
def test_main_missing_query_and_file(capsys):
    """Test main() fails when neither query nor file provided"""
    with patch("sys.argv", ["bq-query-cost"]):
        with pytest.raises(SystemExit) as exc_info:
            bq_query_cost.main()

    assert exc_info.value.code == 1


@pytest.mark.unit
def test_main_file_read_error(capsys):
    """Test main() handles file read errors"""
    with patch("sys.argv", ["bq-query-cost", "--file=/nonexistent/file.sql"]):
        with pytest.raises(SystemExit) as exc_info:
            bq_query_cost.main()

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error reading file" in captured.err
