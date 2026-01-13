#!/usr/bin/env python3
"""
Team Metrics Collector for Data Engineering Teams

Collects and analyzes metrics across query performance, costs, pipeline success,
test coverage, documentation, and contributions.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from google.cloud import bigquery
import json


@dataclass
class MetricResult:
    """Container for metric results"""
    metric_name: str
    value: Any
    unit: str
    timestamp: datetime
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict:
        return {
            'metric_name': self.metric_name,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata or {}
        }


class TeamMetricsCollector:
    """Collects team analytics and performance metrics from BigQuery"""

    def __init__(self, project_id: Optional[str] = None):
        """Initialize metrics collector

        Args:
            project_id: GCP project ID (uses default if not specified)
        """
        self.client = bigquery.Client(project=project_id)
        self.project_id = project_id or self.client.project

    def get_query_performance_trends(
        self,
        days: int = 30,
        team_filter: Optional[str] = None
    ) -> List[MetricResult]:
        """Analyze query performance trends over time

        Args:
            days: Number of days to look back
            team_filter: Filter by team label (optional)

        Returns:
            List of metric results with performance data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = f"""
        SELECT
            DATE(creation_time) as query_date,
            COUNT(*) as query_count,
            AVG(total_slot_ms) / 1000 as avg_slot_seconds,
            AVG(total_bytes_processed) / POW(10, 9) as avg_gb_processed,
            APPROX_QUANTILES(total_slot_ms / 1000, 100)[OFFSET(50)] as median_slot_seconds,
            APPROX_QUANTILES(total_slot_ms / 1000, 100)[OFFSET(95)] as p95_slot_seconds,
            COUNTIF(error_result IS NOT NULL) as error_count,
            COUNTIF(cache_hit) as cache_hit_count
        FROM
            `{self.project_id}.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
        WHERE
            creation_time >= TIMESTAMP('{start_date.isoformat()}')
            AND creation_time <= TIMESTAMP('{end_date.isoformat()}')
            AND job_type = 'QUERY'
            AND state = 'DONE'
        GROUP BY
            query_date
        ORDER BY
            query_date DESC
        """

        results = []
        for row in self.client.query(query).result():
            results.append(MetricResult(
                metric_name='query_performance_daily',
                value={
                    'date': row.query_date.isoformat(),
                    'query_count': row.query_count,
                    'avg_slot_seconds': float(row.avg_slot_seconds or 0),
                    'avg_gb_processed': float(row.avg_gb_processed or 0),
                    'median_slot_seconds': float(row.median_slot_seconds or 0),
                    'p95_slot_seconds': float(row.p95_slot_seconds or 0),
                    'error_count': row.error_count,
                    'cache_hit_count': row.cache_hit_count,
                    'cache_hit_rate': (row.cache_hit_count / row.query_count * 100) if row.query_count > 0 else 0
                },
                unit='daily_stats',
                timestamp=datetime.combine(row.query_date, datetime.min.time())
            ))

        return results

    def get_cost_tracking(
        self,
        days: int = 30,
        team_filter: Optional[str] = None,
        project_filter: Optional[str] = None
    ) -> List[MetricResult]:
        """Track BigQuery costs per team/project

        Args:
            days: Number of days to look back
            team_filter: Filter by team label
            project_filter: Filter by project label

        Returns:
            List of metric results with cost data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # BigQuery pricing: $5 per TB processed (on-demand)
        cost_per_tb = 5.0

        query = f"""
        SELECT
            DATE(creation_time) as cost_date,
            user_email,
            SUM(total_bytes_billed) / POW(10, 12) as tb_billed,
            COUNT(*) as query_count
        FROM
            `{self.project_id}.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
        WHERE
            creation_time >= TIMESTAMP('{start_date.isoformat()}')
            AND creation_time <= TIMESTAMP('{end_date.isoformat()}')
            AND job_type = 'QUERY'
            AND state = 'DONE'
            AND total_bytes_billed > 0
        GROUP BY
            cost_date,
            user_email
        ORDER BY
            cost_date DESC,
            tb_billed DESC
        """

        results = []
        for row in self.client.query(query).result():
            cost_usd = float(row.tb_billed or 0) * cost_per_tb
            results.append(MetricResult(
                metric_name='cost_by_user_daily',
                value={
                    'date': row.cost_date.isoformat(),
                    'user': row.user_email,
                    'tb_billed': float(row.tb_billed or 0),
                    'cost_usd': cost_usd,
                    'query_count': row.query_count
                },
                unit='usd',
                timestamp=datetime.combine(row.cost_date, datetime.min.time()),
                metadata={'cost_per_tb': cost_per_tb}
            ))

        return results

    def get_pipeline_success_rates(
        self,
        days: int = 30
    ) -> List[MetricResult]:
        """Analyze pipeline/job success rates

        Args:
            days: Number of days to look back

        Returns:
            List of metric results with pipeline success data
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = f"""
        SELECT
            DATE(creation_time) as run_date,
            job_type,
            state,
            COUNT(*) as job_count,
            COUNTIF(error_result IS NOT NULL) as error_count,
            AVG(TIMESTAMP_DIFF(end_time, start_time, SECOND)) as avg_duration_seconds
        FROM
            `{self.project_id}.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
        WHERE
            creation_time >= TIMESTAMP('{start_date.isoformat()}')
            AND creation_time <= TIMESTAMP('{end_date.isoformat()}')
        GROUP BY
            run_date,
            job_type,
            state
        ORDER BY
            run_date DESC,
            job_type
        """

        results = []
        for row in self.client.query(query).result():
            success_rate = ((row.job_count - row.error_count) / row.job_count * 100) if row.job_count > 0 else 0
            results.append(MetricResult(
                metric_name='pipeline_success_rate',
                value={
                    'date': row.run_date.isoformat(),
                    'job_type': row.job_type,
                    'state': row.state,
                    'job_count': row.job_count,
                    'error_count': row.error_count,
                    'success_rate': success_rate,
                    'avg_duration_seconds': float(row.avg_duration_seconds or 0)
                },
                unit='percentage',
                timestamp=datetime.combine(row.run_date, datetime.min.time())
            ))

        return results

    def get_test_coverage_metrics(
        self,
        dataset_filter: Optional[str] = None
    ) -> List[MetricResult]:
        """Calculate test coverage for data pipelines

        Analyzes presence of test tables/views relative to production tables

        Args:
            dataset_filter: Filter by dataset pattern

        Returns:
            List of metric results with test coverage data
        """
        query = f"""
        WITH production_tables AS (
            SELECT
                table_schema,
                COUNT(*) as prod_table_count
            FROM
                `{self.project_id}.region-us.INFORMATION_SCHEMA.TABLES`
            WHERE
                table_schema NOT LIKE '%test%'
                AND table_schema NOT LIKE '%dev%'
                AND table_type IN ('BASE TABLE', 'VIEW')
            GROUP BY
                table_schema
        ),
        test_tables AS (
            SELECT
                REGEXP_REPLACE(table_schema, r'_(test|dev)$', '') as base_schema,
                COUNT(*) as test_table_count
            FROM
                `{self.project_id}.region-us.INFORMATION_SCHEMA.TABLES`
            WHERE
                (table_schema LIKE '%test%' OR table_schema LIKE '%dev%')
                AND table_type IN ('BASE TABLE', 'VIEW')
            GROUP BY
                base_schema
        )
        SELECT
            p.table_schema,
            p.prod_table_count,
            COALESCE(t.test_table_count, 0) as test_table_count
        FROM
            production_tables p
        LEFT JOIN
            test_tables t
        ON
            p.table_schema = t.base_schema
        ORDER BY
            p.table_schema
        """

        results = []
        timestamp = datetime.now()

        for row in self.client.query(query).result():
            coverage_pct = (row.test_table_count / row.prod_table_count * 100) if row.prod_table_count > 0 else 0
            results.append(MetricResult(
                metric_name='test_coverage_by_dataset',
                value={
                    'dataset': row.table_schema,
                    'prod_table_count': row.prod_table_count,
                    'test_table_count': row.test_table_count,
                    'coverage_percentage': coverage_pct
                },
                unit='percentage',
                timestamp=timestamp
            ))

        return results

    def get_documentation_completeness(
        self
    ) -> List[MetricResult]:
        """Check documentation completeness for tables

        Analyzes presence of table and column descriptions

        Returns:
            List of metric results with documentation completeness
        """
        query = f"""
        WITH table_docs AS (
            SELECT
                table_schema,
                COUNT(*) as total_tables,
                COUNTIF(COALESCE(ddl, '') LIKE '%DESCRIPTION%') as documented_tables
            FROM
                `{self.project_id}.region-us.INFORMATION_SCHEMA.TABLES`
            WHERE
                table_type IN ('BASE TABLE', 'VIEW')
            GROUP BY
                table_schema
        ),
        column_docs AS (
            SELECT
                table_schema,
                COUNT(*) as total_columns,
                COUNTIF(description IS NOT NULL AND description != '') as documented_columns
            FROM
                `{self.project_id}.region-us.INFORMATION_SCHEMA.COLUMNS`
            GROUP BY
                table_schema
        )
        SELECT
            t.table_schema,
            t.total_tables,
            t.documented_tables,
            c.total_columns,
            c.documented_columns
        FROM
            table_docs t
        JOIN
            column_docs c
        ON
            t.table_schema = c.table_schema
        ORDER BY
            t.table_schema
        """

        results = []
        timestamp = datetime.now()

        for row in self.client.query(query).result():
            table_doc_pct = (row.documented_tables / row.total_tables * 100) if row.total_tables > 0 else 0
            column_doc_pct = (row.documented_columns / row.total_columns * 100) if row.total_columns > 0 else 0

            results.append(MetricResult(
                metric_name='documentation_completeness',
                value={
                    'dataset': row.table_schema,
                    'total_tables': row.total_tables,
                    'documented_tables': row.documented_tables,
                    'table_doc_percentage': table_doc_pct,
                    'total_columns': row.total_columns,
                    'documented_columns': row.documented_columns,
                    'column_doc_percentage': column_doc_pct
                },
                unit='percentage',
                timestamp=timestamp
            ))

        return results

    def get_contribution_analytics(
        self,
        days: int = 30
    ) -> List[MetricResult]:
        """Analyze contribution patterns by user

        Args:
            days: Number of days to look back

        Returns:
            List of metric results with contribution analytics
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = f"""
        SELECT
            user_email,
            COUNT(DISTINCT DATE(creation_time)) as active_days,
            COUNT(*) as total_queries,
            SUM(total_bytes_processed) / POW(10, 12) as tb_processed,
            COUNTIF(job_type = 'LOAD') as load_jobs,
            COUNTIF(job_type = 'QUERY') as query_jobs,
            COUNTIF(job_type = 'COPY') as copy_jobs,
            COUNTIF(job_type = 'EXTRACT') as extract_jobs,
            AVG(TIMESTAMP_DIFF(end_time, start_time, SECOND)) as avg_job_duration_seconds
        FROM
            `{self.project_id}.region-us.INFORMATION_SCHEMA.JOBS_BY_PROJECT`
        WHERE
            creation_time >= TIMESTAMP('{start_date.isoformat()}')
            AND creation_time <= TIMESTAMP('{end_date.isoformat()}')
            AND state = 'DONE'
        GROUP BY
            user_email
        ORDER BY
            total_queries DESC
        """

        results = []
        timestamp = datetime.now()

        for row in self.client.query(query).result():
            results.append(MetricResult(
                metric_name='user_contributions',
                value={
                    'user': row.user_email,
                    'active_days': row.active_days,
                    'total_queries': row.total_queries,
                    'tb_processed': float(row.tb_processed or 0),
                    'load_jobs': row.load_jobs,
                    'query_jobs': row.query_jobs,
                    'copy_jobs': row.copy_jobs,
                    'extract_jobs': row.extract_jobs,
                    'avg_job_duration_seconds': float(row.avg_job_duration_seconds or 0)
                },
                unit='activity',
                timestamp=timestamp
            ))

        return results

    def collect_all_metrics(
        self,
        days: int = 30,
        team_filter: Optional[str] = None,
        project_filter: Optional[str] = None
    ) -> Dict[str, List[MetricResult]]:
        """Collect all team metrics

        Args:
            days: Number of days to look back for time-series metrics
            team_filter: Filter by team label
            project_filter: Filter by project label

        Returns:
            Dictionary mapping metric categories to results
        """
        return {
            'query_performance': self.get_query_performance_trends(days, team_filter),
            'costs': self.get_cost_tracking(days, team_filter, project_filter),
            'pipeline_success': self.get_pipeline_success_rates(days),
            'test_coverage': self.get_test_coverage_metrics(),
            'documentation': self.get_documentation_completeness(),
            'contributions': self.get_contribution_analytics(days)
        }

    def export_to_json(self, metrics: Dict[str, List[MetricResult]]) -> str:
        """Export metrics to JSON format

        Args:
            metrics: Dictionary of metric results

        Returns:
            JSON string of all metrics
        """
        output = {}
        for category, results in metrics.items():
            output[category] = [r.to_dict() for r in results]

        return json.dumps(output, indent=2, default=str)


def main():
    """CLI entry point for testing"""
    import sys

    collector = TeamMetricsCollector()

    print("Collecting team metrics...")
    metrics = collector.collect_all_metrics(days=7)

    print("\nMetrics Summary:")
    for category, results in metrics.items():
        print(f"\n{category.upper()}: {len(results)} data points")

    # Export to JSON
    json_output = collector.export_to_json(metrics)
    print("\n" + json_output)


if __name__ == '__main__':
    main()
