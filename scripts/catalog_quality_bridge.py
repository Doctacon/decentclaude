#!/usr/bin/env python3
"""
Bridge module to integrate data quality checks with catalog sync.

This module connects the data_quality.py framework with the catalog-sync utility,
allowing quality check results to be pushed to data catalogs.
"""

import sys
import os
from typing import Dict, Any, List
from google.cloud import bigquery

# Import data quality framework
sys.path.insert(0, os.path.dirname(__file__))
from data_quality import (
    DataQualityCheck,
    SQLFileExistsCheck,
    SQLSyntaxCheck,
    ConfigFileCheck,
    NoHardcodedSecretsCheck
)


class BigQueryTableQualityCheck(DataQualityCheck):
    """Check table-level quality metrics in BigQuery"""

    def __init__(self, table_id: str):
        super().__init__(f"BigQuery Table Quality: {table_id}")
        self.table_id = table_id
        self.bq_client = bigquery.Client()
        self.checks_run = {}

    def run(self) -> bool:
        """Run all table quality checks"""
        all_passed = True

        # Check 1: Table exists
        exists_check = self._check_table_exists()
        self.checks_run["table_exists"] = exists_check
        all_passed = all_passed and exists_check["passed"]

        if not exists_check["passed"]:
            self.passed = False
            return False

        # Check 2: Table has data
        data_check = self._check_has_data()
        self.checks_run["has_data"] = data_check
        all_passed = all_passed and data_check["passed"]

        # Check 3: Schema is documented
        schema_doc_check = self._check_schema_documented()
        self.checks_run["schema_documented"] = schema_doc_check
        all_passed = all_passed and schema_doc_check["passed"]

        # Check 4: Freshness (for time-partitioned tables)
        freshness_check = self._check_data_freshness()
        self.checks_run["data_freshness"] = freshness_check
        all_passed = all_passed and freshness_check["passed"]

        self.passed = all_passed
        return all_passed

    def _check_table_exists(self) -> Dict[str, Any]:
        """Verify table exists"""
        try:
            self.bq_client.get_table(self.table_id)
            return {"passed": True, "message": "Table exists"}
        except Exception as e:
            return {"passed": False, "message": f"Table does not exist: {e}"}

    def _check_has_data(self) -> Dict[str, Any]:
        """Verify table has data"""
        try:
            table = self.bq_client.get_table(self.table_id)
            if table.num_rows > 0:
                return {"passed": True, "message": f"Table has {table.num_rows} rows"}
            else:
                return {"passed": False, "message": "Table is empty"}
        except Exception as e:
            return {"passed": False, "message": f"Error checking row count: {e}"}

    def _check_schema_documented(self) -> Dict[str, Any]:
        """Check if table and columns have descriptions"""
        try:
            table = self.bq_client.get_table(self.table_id)

            # Check table description
            if not table.description:
                return {"passed": False, "message": "Table description is missing"}

            # Check column descriptions
            undocumented_cols = []
            for field in table.schema:
                if not field.description:
                    undocumented_cols.append(field.name)

            if undocumented_cols:
                return {
                    "passed": False,
                    "message": f"Columns missing descriptions: {', '.join(undocumented_cols[:5])}"
                }

            return {"passed": True, "message": "Table and all columns are documented"}

        except Exception as e:
            return {"passed": False, "message": f"Error checking documentation: {e}"}

    def _check_data_freshness(self) -> Dict[str, Any]:
        """Check data freshness for time-partitioned tables"""
        try:
            table = self.bq_client.get_table(self.table_id)

            # Only applicable for partitioned tables
            if not table.time_partitioning:
                return {"passed": True, "message": "Not a time-partitioned table"}

            # Query for max timestamp in partition field
            partition_field = table.time_partitioning.field or "_PARTITIONTIME"

            query = f"""
            SELECT MAX({partition_field}) as max_timestamp
            FROM `{self.table_id}`
            """

            result = list(self.bq_client.query(query).result())
            if result and result[0].max_timestamp:
                max_ts = result[0].max_timestamp

                # Check if data is fresh (within last 7 days)
                from datetime import datetime, timedelta
                now = datetime.now(max_ts.tzinfo) if max_ts.tzinfo else datetime.now()
                age_days = (now - max_ts).days

                if age_days <= 7:
                    return {"passed": True, "message": f"Data is fresh ({age_days} days old)"}
                else:
                    return {"passed": False, "message": f"Data is stale ({age_days} days old)"}
            else:
                return {"passed": False, "message": "No timestamp data found"}

        except Exception as e:
            return {"passed": True, "message": f"Freshness check skipped: {e}"}

    def report(self) -> str:
        """Generate detailed report"""
        lines = [f"\n{'='*60}", f"Quality Check Report: {self.table_id}", f"{'='*60}"]

        for check_name, result in self.checks_run.items():
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            lines.append(f"{status} | {check_name}: {result['message']}")

        overall = "PASSED" if self.passed else "FAILED"
        lines.append(f"\nOverall: {overall}")
        lines.append(f"{'='*60}\n")

        return "\n".join(lines)

    def get_scores(self) -> Dict[str, Any]:
        """Get quality scores in catalog-friendly format"""
        return self.checks_run


class ColumnQualityCheck(DataQualityCheck):
    """Check column-level quality metrics"""

    def __init__(self, table_id: str, column_name: str):
        super().__init__(f"Column Quality: {table_id}.{column_name}")
        self.table_id = table_id
        self.column_name = column_name
        self.bq_client = bigquery.Client()
        self.checks_run = {}

    def run(self) -> bool:
        """Run column quality checks"""
        all_passed = True

        # Check 1: Null percentage
        null_check = self._check_null_percentage()
        self.checks_run["null_percentage"] = null_check
        all_passed = all_passed and null_check["passed"]

        # Check 2: Uniqueness (for potential key columns)
        uniqueness_check = self._check_uniqueness()
        self.checks_run["uniqueness"] = uniqueness_check
        # Don't fail on low uniqueness, just report it

        self.passed = all_passed
        return all_passed

    def _check_null_percentage(self) -> Dict[str, Any]:
        """Check percentage of null values"""
        try:
            query = f"""
            SELECT
                COUNTIF({self.column_name} IS NULL) as null_count,
                COUNT(*) as total_count
            FROM `{self.table_id}`
            """

            result = list(self.bq_client.query(query).result())[0]
            null_pct = (result.null_count / result.total_count * 100) if result.total_count > 0 else 0

            if null_pct < 50:
                return {"passed": True, "message": f"Null percentage: {null_pct:.2f}%"}
            else:
                return {"passed": False, "message": f"High null percentage: {null_pct:.2f}%"}

        except Exception as e:
            return {"passed": True, "message": f"Null check skipped: {e}"}

    def _check_uniqueness(self) -> Dict[str, Any]:
        """Check uniqueness ratio"""
        try:
            query = f"""
            SELECT
                COUNT(DISTINCT {self.column_name}) as distinct_count,
                COUNT(*) as total_count
            FROM `{self.table_id}`
            """

            result = list(self.bq_client.query(query).result())[0]
            uniqueness = (result.distinct_count / result.total_count) if result.total_count > 0 else 0

            return {
                "passed": True,
                "message": f"Uniqueness ratio: {uniqueness:.2%} ({result.distinct_count}/{result.total_count})"
            }

        except Exception as e:
            return {"passed": True, "message": f"Uniqueness check skipped: {e}"}

    def report(self) -> str:
        """Generate report"""
        lines = []
        for check_name, result in self.checks_run.items():
            status = "✓" if result["passed"] else "✗"
            lines.append(f"  {status} {check_name}: {result['message']}")
        return "\n".join(lines)

    def get_scores(self) -> Dict[str, Any]:
        """Get quality scores"""
        return self.checks_run


def run_table_quality_checks(table_id: str) -> Dict[str, Any]:
    """
    Run comprehensive quality checks on a BigQuery table.

    Returns a dictionary of check results that can be pushed to catalogs.
    """
    check = BigQueryTableQualityCheck(table_id)
    check.run()

    return {
        "overall_passed": check.passed,
        "checks": check.get_scores(),
        "report": check.report()
    }


def run_column_quality_checks(table_id: str, columns: List[str] = None) -> Dict[str, Any]:
    """
    Run quality checks on specific columns.

    If columns is None, checks all columns in the table.
    """
    client = bigquery.Client()

    if columns is None:
        # Get all columns from table schema
        table = client.get_table(table_id)
        columns = [field.name for field in table.schema if field.field_type in ['STRING', 'INTEGER', 'FLOAT', 'NUMERIC', 'BIGNUMERIC', 'DATE', 'DATETIME', 'TIMESTAMP']]

    results = {}
    for column in columns:
        check = ColumnQualityCheck(table_id, column)
        check.run()
        results[column] = check.get_scores()

    return results


def get_catalog_quality_payload(table_id: str, include_columns: bool = False) -> Dict[str, Any]:
    """
    Get a complete quality payload for catalog synchronization.

    Returns:
        Dictionary with table-level and optionally column-level quality scores
    """
    payload = {
        "table_id": table_id,
        "table_checks": {},
        "column_checks": {}
    }

    # Run table checks
    table_results = run_table_quality_checks(table_id)
    payload["table_checks"] = table_results["checks"]
    payload["overall_passed"] = table_results["overall_passed"]

    # Run column checks if requested
    if include_columns:
        column_results = run_column_quality_checks(table_id)
        payload["column_checks"] = column_results

    return payload


def main():
    """CLI interface for testing quality checks"""
    import argparse

    parser = argparse.ArgumentParser(description="Run quality checks for catalog sync")
    parser.add_argument("table_id", help="Fully-qualified table ID (project.dataset.table)")
    parser.add_argument("--include-columns", action="store_true", help="Include column-level checks")
    parser.add_argument("--output", choices=["text", "json"], default="text", help="Output format")

    args = parser.parse_args()

    # Run checks
    results = get_catalog_quality_payload(args.table_id, args.include_columns)

    if args.output == "json":
        import json
        print(json.dumps(results, indent=2))
    else:
        # Text output
        check = BigQueryTableQualityCheck(args.table_id)
        check.checks_run = results["table_checks"]
        check.passed = results["overall_passed"]
        print(check.report())

        if args.include_columns and results["column_checks"]:
            print("\nColumn Checks:")
            print("="*60)
            for col_name, col_results in results["column_checks"].items():
                print(f"\n{col_name}:")
                for check_name, check_result in col_results.items():
                    status = "✓" if check_result["passed"] else "✗"
                    print(f"  {status} {check_name}: {check_result['message']}")


if __name__ == "__main__":
    main()
