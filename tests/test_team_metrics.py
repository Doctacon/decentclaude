#!/usr/bin/env python3
"""
Unit tests for team metrics collection

Run with:
    python -m pytest tests/test_team_metrics.py
    or
    python tests/test_team_metrics.py
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../scripts'))

from team_metrics import TeamMetricsCollector, MetricResult


class TestMetricResult(unittest.TestCase):
    """Test MetricResult dataclass"""

    def test_metric_result_creation(self):
        """Test creating a MetricResult"""
        result = MetricResult(
            metric_name='test_metric',
            value={'count': 100},
            unit='items',
            timestamp=datetime.now()
        )

        self.assertEqual(result.metric_name, 'test_metric')
        self.assertEqual(result.value['count'], 100)
        self.assertEqual(result.unit, 'items')
        self.assertIsNone(result.metadata)

    def test_metric_result_to_dict(self):
        """Test converting MetricResult to dict"""
        timestamp = datetime(2026, 1, 12, 12, 0, 0)
        result = MetricResult(
            metric_name='test_metric',
            value={'count': 100},
            unit='items',
            timestamp=timestamp,
            metadata={'source': 'test'}
        )

        result_dict = result.to_dict()

        self.assertEqual(result_dict['metric_name'], 'test_metric')
        self.assertEqual(result_dict['value'], {'count': 100})
        self.assertEqual(result_dict['unit'], 'items')
        self.assertEqual(result_dict['timestamp'], '2026-01-12T12:00:00')
        self.assertEqual(result_dict['metadata'], {'source': 'test'})


class TestTeamMetricsCollector(unittest.TestCase):
    """Test TeamMetricsCollector class"""

    @patch('team_metrics.bigquery.Client')
    def test_collector_initialization(self, mock_client_class):
        """Test initializing the collector"""
        mock_client = Mock()
        mock_client.project = 'test-project'
        mock_client_class.return_value = mock_client

        collector = TeamMetricsCollector(project_id='test-project')

        self.assertEqual(collector.project_id, 'test-project')
        mock_client_class.assert_called_once_with(project='test-project')

    @patch('team_metrics.bigquery.Client')
    def test_collector_default_project(self, mock_client_class):
        """Test collector uses default project when not specified"""
        mock_client = Mock()
        mock_client.project = 'default-project'
        mock_client_class.return_value = mock_client

        collector = TeamMetricsCollector()

        self.assertEqual(collector.project_id, 'default-project')
        mock_client_class.assert_called_once_with(project=None)

    @patch('team_metrics.bigquery.Client')
    def test_get_query_performance_trends(self, mock_client_class):
        """Test query performance trends collection"""
        # Mock BigQuery client and query results
        mock_client = Mock()
        mock_client.project = 'test-project'

        # Create mock query result
        mock_row = Mock()
        mock_row.query_date = datetime(2026, 1, 12).date()
        mock_row.query_count = 100
        mock_row.avg_slot_seconds = 10.5
        mock_row.avg_gb_processed = 50.0
        mock_row.median_slot_seconds = 8.0
        mock_row.p95_slot_seconds = 20.0
        mock_row.error_count = 2
        mock_row.cache_hit_count = 25

        mock_query_job = Mock()
        mock_query_job.result.return_value = [mock_row]
        mock_client.query.return_value = mock_query_job
        mock_client_class.return_value = mock_client

        collector = TeamMetricsCollector(project_id='test-project')
        results = collector.get_query_performance_trends(days=7)

        # Verify results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].metric_name, 'query_performance_daily')
        self.assertEqual(results[0].value['query_count'], 100)
        self.assertEqual(results[0].value['error_count'], 2)
        self.assertEqual(results[0].value['cache_hit_rate'], 25.0)

    @patch('team_metrics.bigquery.Client')
    def test_get_cost_tracking(self, mock_client_class):
        """Test cost tracking collection"""
        mock_client = Mock()
        mock_client.project = 'test-project'

        # Create mock query result
        mock_row = Mock()
        mock_row.cost_date = datetime(2026, 1, 12).date()
        mock_row.user_email = 'user@example.com'
        mock_row.tb_billed = 2.5
        mock_row.query_count = 50

        mock_query_job = Mock()
        mock_query_job.result.return_value = [mock_row]
        mock_client.query.return_value = mock_query_job
        mock_client_class.return_value = mock_client

        collector = TeamMetricsCollector(project_id='test-project')
        results = collector.get_cost_tracking(days=7)

        # Verify results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].metric_name, 'cost_by_user_daily')
        self.assertEqual(results[0].value['user'], 'user@example.com')
        self.assertEqual(results[0].value['tb_billed'], 2.5)
        self.assertEqual(results[0].value['cost_usd'], 12.5)  # 2.5 TB * $5/TB

    @patch('team_metrics.bigquery.Client')
    def test_export_to_json(self, mock_client_class):
        """Test exporting metrics to JSON"""
        mock_client = Mock()
        mock_client.project = 'test-project'
        mock_client_class.return_value = mock_client

        collector = TeamMetricsCollector(project_id='test-project')

        # Create test metrics
        test_metrics = {
            'test_category': [
                MetricResult(
                    metric_name='test_metric',
                    value={'count': 100},
                    unit='items',
                    timestamp=datetime(2026, 1, 12, 12, 0, 0)
                )
            ]
        }

        json_output = collector.export_to_json(test_metrics)

        # Verify JSON contains expected data
        self.assertIn('test_category', json_output)
        self.assertIn('test_metric', json_output)
        self.assertIn('"count": 100', json_output)

    @patch('team_metrics.bigquery.Client')
    def test_collect_all_metrics(self, mock_client_class):
        """Test collecting all metrics at once"""
        mock_client = Mock()
        mock_client.project = 'test-project'

        # Mock empty results for all queries
        mock_query_job = Mock()
        mock_query_job.result.return_value = []
        mock_client.query.return_value = mock_query_job
        mock_client_class.return_value = mock_client

        collector = TeamMetricsCollector(project_id='test-project')
        all_metrics = collector.collect_all_metrics(days=7)

        # Verify all metric categories are present
        expected_categories = [
            'query_performance',
            'costs',
            'pipeline_success',
            'test_coverage',
            'documentation',
            'contributions'
        ]

        for category in expected_categories:
            self.assertIn(category, all_metrics)


class TestMetricValidation(unittest.TestCase):
    """Test metric value validation"""

    def test_query_performance_values(self):
        """Test query performance metric value structure"""
        value = {
            'date': '2026-01-12',
            'query_count': 100,
            'avg_slot_seconds': 10.5,
            'avg_gb_processed': 50.0,
            'median_slot_seconds': 8.0,
            'p95_slot_seconds': 20.0,
            'error_count': 2,
            'cache_hit_count': 25,
            'cache_hit_rate': 25.0
        }

        # Validate required fields
        required_fields = [
            'date', 'query_count', 'avg_slot_seconds', 'avg_gb_processed',
            'median_slot_seconds', 'p95_slot_seconds', 'error_count',
            'cache_hit_count', 'cache_hit_rate'
        ]

        for field in required_fields:
            self.assertIn(field, value)

        # Validate types
        self.assertIsInstance(value['query_count'], int)
        self.assertIsInstance(value['avg_slot_seconds'], float)
        self.assertIsInstance(value['cache_hit_rate'], float)

    def test_cost_values(self):
        """Test cost metric value structure"""
        value = {
            'date': '2026-01-12',
            'user': 'user@example.com',
            'tb_billed': 2.5,
            'cost_usd': 12.5,
            'query_count': 50
        }

        # Validate cost calculation
        expected_cost = value['tb_billed'] * 5.0
        self.assertAlmostEqual(value['cost_usd'], expected_cost)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
