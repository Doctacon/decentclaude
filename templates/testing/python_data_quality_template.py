#!/usr/bin/env python3
"""
Template for Python-based data quality checks
Extends the base data_quality.py framework with custom checks

Usage:
    python python_data_quality_template.py
    python python_data_quality_template.py --check=MyCustomCheck

Author: Your Name
Created: {date}
"""

import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
from google.cloud import bigquery

# Import base classes from existing data_quality.py
# Adjust path as needed
try:
    from scripts.data_quality import DataQualityCheck, run_all_checks
except ImportError:
    print("Error: Could not import from scripts.data_quality")
    print("Make sure data_quality.py is in your scripts/ directory")
    sys.exit(1)


class BigQueryRowCountCheck(DataQualityCheck):
    """Check that BigQuery table has expected row count range"""

    def __init__(self, table_id: str, min_rows: int, max_rows: int):
        super().__init__(f"Row Count Check: {table_id}")
        self.table_id = table_id
        self.min_rows = min_rows
        self.max_rows = max_rows

    def run(self) -> bool:
        try:
            client = bigquery.Client()
            query = f"SELECT COUNT(*) as count FROM `{self.table_id}`"
            result = client.query(query).to_dataframe()
            row_count = result['count'].iloc[0]

            if row_count < self.min_rows:
                self.message = f"Row count {row_count} is below minimum {self.min_rows}"
                self.passed = False
            elif row_count > self.max_rows:
                self.message = f"Row count {row_count} exceeds maximum {self.max_rows}"
                self.passed = False
            else:
                self.message = f"Row count {row_count} is within range [{self.min_rows}, {self.max_rows}]"
                self.passed = True

            return self.passed

        except Exception as e:
            self.message = f"Error running check: {str(e)}"
            self.passed = False
            return False


class BigQuerySchemaCheck(DataQualityCheck):
    """Verify BigQuery table has expected schema"""

    def __init__(self, table_id: str, expected_columns: List[str]):
        super().__init__(f"Schema Check: {table_id}")
        self.table_id = table_id
        self.expected_columns = set(expected_columns)

    def run(self) -> bool:
        try:
            client = bigquery.Client()
            table = client.get_table(self.table_id)
            actual_columns = set([field.name for field in table.schema])

            missing = self.expected_columns - actual_columns
            extra = actual_columns - self.expected_columns

            if missing or extra:
                issues = []
                if missing:
                    issues.append(f"Missing columns: {', '.join(missing)}")
                if extra:
                    issues.append(f"Unexpected columns: {', '.join(extra)}")
                self.message = "; ".join(issues)
                self.passed = False
            else:
                self.message = f"All {len(self.expected_columns)} expected columns present"
                self.passed = True

            return self.passed

        except Exception as e:
            self.message = f"Error running check: {str(e)}"
            self.passed = False
            return False


class BigQueryDataFreshnessCheck(DataQualityCheck):
    """Check that data was updated recently"""

    def __init__(self, table_id: str, timestamp_column: str, max_age_hours: int = 24):
        super().__init__(f"Data Freshness Check: {table_id}")
        self.table_id = table_id
        self.timestamp_column = timestamp_column
        self.max_age_hours = max_age_hours

    def run(self) -> bool:
        try:
            client = bigquery.Client()
            query = f"""
            SELECT
              MAX({self.timestamp_column}) as latest_timestamp,
              TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX({self.timestamp_column}), HOUR) as age_hours
            FROM `{self.table_id}`
            """
            result = client.query(query).to_dataframe()

            if result.empty or result['latest_timestamp'].iloc[0] is None:
                self.message = "No data found in table"
                self.passed = False
                return False

            age_hours = result['age_hours'].iloc[0]

            if age_hours > self.max_age_hours:
                self.message = f"Data is {age_hours} hours old (max: {self.max_age_hours})"
                self.passed = False
            else:
                self.message = f"Data is {age_hours} hours old (within limit)"
                self.passed = True

            return self.passed

        except Exception as e:
            self.message = f"Error running check: {str(e)}"
            self.passed = False
            return False


class BigQueryNullCheck(DataQualityCheck):
    """Check for nulls in critical columns"""

    def __init__(self, table_id: str, required_columns: List[str]):
        super().__init__(f"Null Check: {table_id}")
        self.table_id = table_id
        self.required_columns = required_columns

    def run(self) -> bool:
        try:
            client = bigquery.Client()

            # Build WHERE clause
            null_conditions = [f"{col} IS NULL" for col in self.required_columns]
            where_clause = " OR ".join(null_conditions)

            query = f"""
            SELECT COUNT(*) as null_count
            FROM `{self.table_id}`
            WHERE {where_clause}
            """

            result = client.query(query).to_dataframe()
            null_count = result['null_count'].iloc[0]

            if null_count > 0:
                self.message = f"Found {null_count} rows with nulls in critical columns"
                self.passed = False
            else:
                self.message = f"No nulls found in {len(self.required_columns)} critical columns"
                self.passed = True

            return self.passed

        except Exception as e:
            self.message = f"Error running check: {str(e)}"
            self.passed = False
            return False


class BigQueryReconciliationCheck(DataQualityCheck):
    """Reconcile aggregates between source and target tables"""

    def __init__(self,
                 source_table: str,
                 target_table: str,
                 metric_column: str,
                 max_pct_diff: float = 0.01):
        super().__init__(f"Reconciliation: {source_table} vs {target_table}")
        self.source_table = source_table
        self.target_table = target_table
        self.metric_column = metric_column
        self.max_pct_diff = max_pct_diff

    def run(self) -> bool:
        try:
            client = bigquery.Client()

            query = f"""
            WITH source_sum AS (
              SELECT SUM({self.metric_column}) as total
              FROM `{self.source_table}`
            ),
            target_sum AS (
              SELECT SUM({self.metric_column}) as total
              FROM `{self.target_table}`
            )
            SELECT
              s.total as source_total,
              t.total as target_total,
              ABS(s.total - t.total) / s.total as pct_diff
            FROM source_sum s, target_sum t
            """

            result = client.query(query).to_dataframe()

            if result.empty:
                self.message = "No data to reconcile"
                self.passed = False
                return False

            pct_diff = result['pct_diff'].iloc[0]
            source_total = result['source_total'].iloc[0]
            target_total = result['target_total'].iloc[0]

            if pct_diff > self.max_pct_diff:
                self.message = (
                    f"Reconciliation failed: {pct_diff*100:.2f}% difference "
                    f"(source: {source_total}, target: {target_total})"
                )
                self.passed = False
            else:
                self.message = f"Reconciliation passed: {pct_diff*100:.4f}% difference"
                self.passed = True

            return self.passed

        except Exception as e:
            self.message = f"Error running check: {str(e)}"
            self.passed = False
            return False


def run_custom_checks() -> Tuple[List[DataQualityCheck], bool]:
    """Run all custom BigQuery quality checks"""

    # CUSTOMIZE THESE CHECKS FOR YOUR PROJECT
    checks = [
        # Row count checks
        BigQueryRowCountCheck(
            table_id="project.dataset.fct_orders",
            min_rows=1000,
            max_rows=10000000
        ),

        # Schema validation
        BigQuerySchemaCheck(
            table_id="project.dataset.fct_orders",
            expected_columns=['order_id', 'customer_id', 'order_total', 'order_date']
        ),

        # Data freshness
        BigQueryDataFreshnessCheck(
            table_id="project.dataset.fct_orders",
            timestamp_column="created_at",
            max_age_hours=24
        ),

        # Null checks
        BigQueryNullCheck(
            table_id="project.dataset.fct_orders",
            required_columns=['order_id', 'customer_id', 'order_total']
        ),

        # Reconciliation
        BigQueryReconciliationCheck(
            source_table="project.raw.orders",
            target_table="project.marts.fct_orders",
            metric_column="order_total",
            max_pct_diff=0.001  # 0.1% tolerance
        ),
    ]

    all_passed = True
    results = []

    print("=" * 60)
    print("Running BigQuery Data Quality Checks")
    print("=" * 60)

    for check in checks:
        try:
            check.run()
            results.append(check)
            if not check.passed:
                all_passed = False
        except Exception as e:
            check.message = f"Error running check: {str(e)}"
            check.passed = False
            results.append(check)
            all_passed = False

    return results, all_passed


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Run BigQuery data quality checks"
    )
    parser.add_argument(
        '--check',
        help="Run specific check only",
        choices=['row_count', 'schema', 'freshness', 'null', 'reconciliation']
    )

    args = parser.parse_args()

    # Run checks
    results, all_passed = run_custom_checks()

    # Print results
    print()
    for result in results:
        print(result.report())

    print()
    print("=" * 60)
    if all_passed:
        print("✓ All data quality checks passed")
        print("=" * 60)
        sys.exit(0)
    else:
        print("✗ Some data quality checks failed")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
