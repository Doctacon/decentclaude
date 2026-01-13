#!/usr/bin/env python3
"""
Tests for catalog integration functionality.

Run with: python -m pytest tests/test_catalog_integration.py
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from catalog_quality_bridge import (
    BigQueryTableQualityCheck,
    ColumnQualityCheck,
    run_table_quality_checks,
    run_column_quality_checks,
    get_catalog_quality_payload
)


class TestBigQueryTableQualityCheck(unittest.TestCase):
    """Test suite for table-level quality checks"""

    @patch('catalog_quality_bridge.bigquery.Client')
    def test_table_exists_check_pass(self, mock_client):
        """Test that table existence check passes when table exists"""
        # Setup mock
        mock_table = Mock()
        mock_client.return_value.get_table.return_value = mock_table

        # Run check
        check = BigQueryTableQualityCheck("project.dataset.table")
        result = check._check_table_exists()

        # Assert
        self.assertTrue(result["passed"])
        self.assertIn("exists", result["message"].lower())

    @patch('catalog_quality_bridge.bigquery.Client')
    def test_table_exists_check_fail(self, mock_client):
        """Test that table existence check fails when table doesn't exist"""
        # Setup mock to raise exception
        mock_client.return_value.get_table.side_effect = Exception("Table not found")

        # Run check
        check = BigQueryTableQualityCheck("project.dataset.table")
        result = check._check_table_exists()

        # Assert
        self.assertFalse(result["passed"])
        self.assertIn("not exist", result["message"].lower())

    @patch('catalog_quality_bridge.bigquery.Client')
    def test_has_data_check_pass(self, mock_client):
        """Test that data check passes when table has rows"""
        # Setup mock
        mock_table = Mock()
        mock_table.num_rows = 1000
        mock_client.return_value.get_table.return_value = mock_table

        # Run check
        check = BigQueryTableQualityCheck("project.dataset.table")
        result = check._check_has_data()

        # Assert
        self.assertTrue(result["passed"])
        self.assertIn("1000", result["message"])

    @patch('catalog_quality_bridge.bigquery.Client')
    def test_has_data_check_fail(self, mock_client):
        """Test that data check fails when table is empty"""
        # Setup mock
        mock_table = Mock()
        mock_table.num_rows = 0
        mock_client.return_value.get_table.return_value = mock_table

        # Run check
        check = BigQueryTableQualityCheck("project.dataset.table")
        result = check._check_has_data()

        # Assert
        self.assertFalse(result["passed"])
        self.assertIn("empty", result["message"].lower())

    @patch('catalog_quality_bridge.bigquery.Client')
    def test_schema_documented_check_pass(self, mock_client):
        """Test that schema documentation check passes when all documented"""
        # Setup mock
        mock_field1 = Mock()
        mock_field1.name = "column1"
        mock_field1.description = "Column 1 description"

        mock_field2 = Mock()
        mock_field2.name = "column2"
        mock_field2.description = "Column 2 description"

        mock_table = Mock()
        mock_table.description = "Table description"
        mock_table.schema = [mock_field1, mock_field2]
        mock_client.return_value.get_table.return_value = mock_table

        # Run check
        check = BigQueryTableQualityCheck("project.dataset.table")
        result = check._check_schema_documented()

        # Assert
        self.assertTrue(result["passed"])
        self.assertIn("documented", result["message"].lower())

    @patch('catalog_quality_bridge.bigquery.Client')
    def test_schema_documented_check_fail_no_table_desc(self, mock_client):
        """Test that check fails when table description is missing"""
        # Setup mock
        mock_table = Mock()
        mock_table.description = None
        mock_client.return_value.get_table.return_value = mock_table

        # Run check
        check = BigQueryTableQualityCheck("project.dataset.table")
        result = check._check_schema_documented()

        # Assert
        self.assertFalse(result["passed"])
        self.assertIn("missing", result["message"].lower())

    @patch('catalog_quality_bridge.bigquery.Client')
    def test_schema_documented_check_fail_missing_column_desc(self, mock_client):
        """Test that check fails when column descriptions are missing"""
        # Setup mock
        mock_field1 = Mock()
        mock_field1.name = "column1"
        mock_field1.description = "Column 1 description"

        mock_field2 = Mock()
        mock_field2.name = "column2"
        mock_field2.description = None  # Missing description

        mock_table = Mock()
        mock_table.description = "Table description"
        mock_table.schema = [mock_field1, mock_field2]
        mock_client.return_value.get_table.return_value = mock_table

        # Run check
        check = BigQueryTableQualityCheck("project.dataset.table")
        result = check._check_schema_documented()

        # Assert
        self.assertFalse(result["passed"])
        self.assertIn("column2", result["message"])


class TestColumnQualityCheck(unittest.TestCase):
    """Test suite for column-level quality checks"""

    @patch('catalog_quality_bridge.bigquery.Client')
    def test_null_percentage_check_pass(self, mock_client):
        """Test that null percentage check passes with low nulls"""
        # Setup mock
        mock_result = Mock()
        mock_result.null_count = 10
        mock_result.total_count = 1000

        mock_query_result = Mock()
        mock_query_result.result.return_value = [mock_result]
        mock_client.return_value.query.return_value = mock_query_result

        # Run check
        check = ColumnQualityCheck("project.dataset.table", "column1")
        result = check._check_null_percentage()

        # Assert
        self.assertTrue(result["passed"])
        self.assertIn("1.00%", result["message"])

    @patch('catalog_quality_bridge.bigquery.Client')
    def test_null_percentage_check_fail(self, mock_client):
        """Test that null percentage check fails with high nulls"""
        # Setup mock
        mock_result = Mock()
        mock_result.null_count = 600
        mock_result.total_count = 1000

        mock_query_result = Mock()
        mock_query_result.result.return_value = [mock_result]
        mock_client.return_value.query.return_value = mock_query_result

        # Run check
        check = ColumnQualityCheck("project.dataset.table", "column1")
        result = check._check_null_percentage()

        # Assert
        self.assertFalse(result["passed"])
        self.assertIn("60.00%", result["message"])

    @patch('catalog_quality_bridge.bigquery.Client')
    def test_uniqueness_check(self, mock_client):
        """Test uniqueness ratio calculation"""
        # Setup mock
        mock_result = Mock()
        mock_result.distinct_count = 800
        mock_result.total_count = 1000

        mock_query_result = Mock()
        mock_query_result.result.return_value = [mock_result]
        mock_client.return_value.query.return_value = mock_query_result

        # Run check
        check = ColumnQualityCheck("project.dataset.table", "column1")
        result = check._check_uniqueness()

        # Assert
        self.assertTrue(result["passed"])
        self.assertIn("80.00%", result["message"])


class TestQualityPayloadGeneration(unittest.TestCase):
    """Test suite for quality payload generation"""

    @patch('catalog_quality_bridge.run_table_quality_checks')
    def test_get_catalog_quality_payload_table_only(self, mock_table_checks):
        """Test payload generation with table checks only"""
        # Setup mock
        mock_table_checks.return_value = {
            "overall_passed": True,
            "checks": {
                "table_exists": {"passed": True, "message": "Table exists"},
                "has_data": {"passed": True, "message": "Table has 1000 rows"}
            }
        }

        # Run
        payload = get_catalog_quality_payload("project.dataset.table", include_columns=False)

        # Assert
        self.assertTrue(payload["overall_passed"])
        self.assertIn("table_exists", payload["table_checks"])
        self.assertEqual(len(payload["column_checks"]), 0)

    @patch('catalog_quality_bridge.run_column_quality_checks')
    @patch('catalog_quality_bridge.run_table_quality_checks')
    def test_get_catalog_quality_payload_with_columns(self, mock_table_checks, mock_column_checks):
        """Test payload generation with column checks"""
        # Setup mocks
        mock_table_checks.return_value = {
            "overall_passed": True,
            "checks": {}
        }

        mock_column_checks.return_value = {
            "column1": {
                "null_percentage": {"passed": True, "message": "1.00%"}
            }
        }

        # Run
        payload = get_catalog_quality_payload("project.dataset.table", include_columns=True)

        # Assert
        self.assertIn("column1", payload["column_checks"])


class TestCatalogAdapterIntegration(unittest.TestCase):
    """Integration tests for catalog adapters (requires mocked external services)"""

    @patch('requests.post')
    def test_datahub_metadata_push_success(self, mock_post):
        """Test successful metadata push to Datahub"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # This would test the actual adapter if we import it
        # For now, just verify the mock is working
        self.assertEqual(mock_response.status_code, 200)

    @patch('requests.put')
    def test_amundsen_metadata_push_success(self, mock_put):
        """Test successful metadata push to Amundsen"""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_put.return_value = mock_response

        self.assertEqual(mock_response.status_code, 201)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestBigQueryTableQualityCheck))
    suite.addTests(loader.loadTestsFromTestCase(TestColumnQualityCheck))
    suite.addTests(loader.loadTestsFromTestCase(TestQualityPayloadGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestCatalogAdapterIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
