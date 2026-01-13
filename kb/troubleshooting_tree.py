#!/usr/bin/env python3
"""
Interactive Troubleshooting Decision Tree

Guides users through diagnosing and resolving common BigQuery issues
through an interactive CLI decision tree.

Usage:
    python troubleshooting_tree.py
    python troubleshooting_tree.py --category sql
    python troubleshooting_tree.py --search "permission denied"
"""

import argparse
import sys
from typing import Dict, List, Optional, Tuple


class TroubleshootingTree:
    """Interactive decision tree for troubleshooting BigQuery issues."""

    def __init__(self):
        self.history = []
        self.solutions_shown = []

    def clear_screen(self):
        """Clear the terminal screen."""
        print("\n" * 2)

    def print_header(self, text: str):
        """Print a formatted header."""
        print(f"\n{'=' * 70}")
        print(f"  {text}")
        print(f"{'=' * 70}\n")

    def print_section(self, title: str, content: str):
        """Print a formatted section."""
        print(f"\n{title}")
        print(f"{'-' * len(title)}")
        print(content)

    def print_commands(self, commands: List[str]):
        """Print a list of commands to run."""
        print("\nCommands to run:")
        for i, cmd in enumerate(commands, 1):
            print(f"  {i}. {cmd}")

    def print_links(self, links: List[Tuple[str, str]]):
        """Print a list of documentation links."""
        print("\nRelated documentation:")
        for title, path in links:
            print(f"  - {title}: {path}")

    def get_choice(self, prompt: str, choices: List[str]) -> int:
        """Get user choice from a list of options."""
        print(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        print(f"  0. Go back")

        while True:
            try:
                choice = input("\nYour choice: ").strip()
                idx = int(choice)
                if 0 <= idx <= len(choices):
                    return idx
                print(f"Please enter a number between 0 and {len(choices)}")
            except ValueError:
                print("Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\nExiting...")
                sys.exit(0)

    def start(self):
        """Start the interactive troubleshooting session."""
        self.clear_screen()
        self.print_header("BigQuery Troubleshooting Assistant")

        print("Welcome! I'll help you diagnose and resolve BigQuery issues.")
        print("Answer a few questions to find the solution.\n")

        # Main category selection
        choice = self.get_choice(
            "What type of problem are you experiencing?",
            [
                "SQL Error",
                "Performance Issue",
                "Cost Problem",
                "Data Quality Issue",
                "Tool/Configuration Error",
            ]
        )

        if choice == 0:
            print("\nGoodbye!")
            return

        # Route to appropriate handler
        handlers = {
            1: self.handle_sql_error,
            2: self.handle_performance,
            3: self.handle_cost,
            4: self.handle_data_quality,
            5: self.handle_tool_error,
        }

        handler = handlers.get(choice)
        if handler:
            handler()

    # SQL Error Handlers
    def handle_sql_error(self):
        """Handle SQL error troubleshooting."""
        self.print_header("SQL Error Troubleshooting")

        choice = self.get_choice(
            "What type of SQL error are you getting?",
            [
                "Syntax Error",
                "Permission Denied",
                "Table/Dataset Not Found",
                "Query Timeout",
                "Resources Exceeded",
            ]
        )

        if choice == 0:
            self.start()
            return

        handlers = {
            1: self.solve_syntax_error,
            2: self.solve_permission_error,
            3: self.solve_not_found,
            4: self.solve_timeout,
            5: self.solve_resources,
        }

        handler = handlers.get(choice)
        if handler:
            handler()
            self.ask_next_step()

    def solve_syntax_error(self):
        """Provide solution for syntax errors."""
        self.print_section(
            "Solution: SQL Syntax Error",
            "Your query has invalid SQL syntax. Let's validate and fix it."
        )

        self.print_commands([
            "sqlfluff lint your_query.sql",
            "bq query --dry_run < your_query.sql",
            "grep -i 'select \\*' your_query.sql  # Check for SELECT *",
        ])

        print("\nCommon causes:")
        print("  - Missing commas between columns")
        print("  - Unclosed quotes or parentheses")
        print("  - Invalid function names")
        print("  - Wrong keyword order (e.g., WHERE after GROUP BY)")

        print("\nQuick fixes:")
        print("  1. Check for missing/extra commas")
        print("  2. Ensure all parentheses are balanced")
        print("  3. Verify function names are correct")
        print("  4. Use a SQL linter for automatic detection")

        self.print_links([
            ("SQL Style Guide", "/Users/crlough/gt/decentclaude/mayor/rig/docs/sql-style-guide.md"),
            ("Troubleshooting Guide", "/Users/crlough/gt/decentclaude/mayor/rig/docs/guides/troubleshooting-tree.md"),
        ])

    def solve_permission_error(self):
        """Provide solution for permission errors."""
        self.print_section(
            "Solution: Permission Denied",
            "You don't have access to the requested resource."
        )

        auth_choice = self.get_choice(
            "Can you access BigQuery at all?",
            ["No - I can't connect", "Yes - But specific tables/datasets are blocked"]
        )

        if auth_choice == 1:
            # Authentication issue
            self.print_commands([
                "gcloud auth list",
                "gcloud auth login",
                "gcloud auth application-default login",
            ])

            print("\nSteps:")
            print("  1. Check which account is authenticated")
            print("  2. Login with the correct account")
            print("  3. Set application default credentials")
            print("  4. Verify project access")

        elif auth_choice == 2:
            # Table access issue
            self.print_commands([
                "bq ls --project_id=PROJECT_ID",
                "bq show PROJECT:DATASET.TABLE",
            ])

            print("\nSteps:")
            print("  1. Verify the table exists")
            print("  2. Check dataset permissions in GCP Console")
            print("  3. Request access from dataset owner")
            print("  4. Verify IAM roles (bigquery.dataViewer, etc.)")

        self.print_links([
            ("Authentication Setup", "/Users/crlough/gt/decentclaude/mayor/rig/docs/guides/authentication.md"),
        ])

    def solve_not_found(self):
        """Provide solution for not found errors."""
        self.print_section(
            "Solution: Table/Dataset Not Found",
            "The table or dataset doesn't exist or has a different name."
        )

        know_name = self.get_choice(
            "Do you know the exact table name?",
            ["Yes - I know what it should be called", "No - I need to find it"]
        )

        if know_name == 1:
            # Verify existence
            self.print_commands([
                "bq ls PROJECT_ID:DATASET",
                "bq show PROJECT:DATASET.TABLE",
            ])

            print("\nChecklist:")
            print("  - Verify spelling and case (BigQuery is case-sensitive)")
            print("  - Check project ID is correct")
            print("  - Ensure dataset name is right")
            print("  - Use backticks for special characters")

        elif know_name == 2:
            # Find table
            self.print_commands([
                'python -c "from mayor.rig.mcp import find_tables_with_column; print(find_tables_with_column(\'column_name\'))"',
                "bq query \"SELECT * FROM PROJECT.DATASET.INFORMATION_SCHEMA.TABLES WHERE table_name LIKE '%search%'\"",
            ])

            print("\nSearch strategies:")
            print("  1. Search by column name if you know a column")
            print("  2. Browse Information Schema")
            print("  3. Check Data Catalog")
            print("  4. Ask data owner/team")

        self.print_links([
            ("MCP Tools Reference", "/Users/crlough/gt/decentclaude/mayor/rig/docs/reference/mcp-tools.md"),
        ])

    def solve_timeout(self):
        """Provide solution for timeout errors."""
        self.print_section(
            "Solution: Query Timeout",
            "Your query is taking too long to execute."
        )

        self.print_commands([
            "bq query --dry_run < your_query.sql",
            "bq show -j JOB_ID",
        ])

        print("\nImmediate fixes:")
        print("  1. Add LIMIT clause for testing")
        print("  2. Add WHERE filters to reduce data scanned")
        print("  3. Use partitioned tables and filter on partition column")
        print("  4. Break into smaller queries")

        print("\nLong-term optimizations:")
        print("  - Create intermediate temp tables")
        print("  - Use materialized views")
        print("  - Optimize with the /optimize Skill")

        self.print_links([
            ("Performance Optimization", "/Users/crlough/gt/decentclaude/mayor/rig/docs/guides/performance-optimization.md"),
            ("Query Optimization", "/Users/crlough/gt/decentclaude/mayor/rig/docs/guides/query-optimization.md"),
        ])

    def solve_resources(self):
        """Provide solution for resource exceeded errors."""
        self.print_section(
            "Solution: Resources Exceeded",
            "Your query exceeded available resources (memory, slots, etc.)."
        )

        self.print_commands([
            "bq show -j JOB_ID --format=prettyjson | jq '.statistics'",
        ])

        print("\nSolutions:")
        print("  1. Reduce query complexity")
        print("  2. Break into smaller queries")
        print("  3. Use temp tables for intermediate results")
        print("  4. Request quota increase if needed")
        print("  5. Use materialized views")

        self.print_links([
            ("Cost Management", "/Users/crlough/gt/decentclaude/mayor/rig/docs/guides/cost-management.md"),
        ])

    # Performance Handlers
    def handle_performance(self):
        """Handle performance issue troubleshooting."""
        self.print_header("Performance Issue Troubleshooting")

        choice = self.get_choice(
            "What performance issue are you experiencing?",
            [
                "Query execution is slow",
                "High bytes scanned",
                "Long queue time",
            ]
        )

        if choice == 0:
            self.start()
            return

        handlers = {
            1: self.solve_slow_query,
            2: self.solve_high_bytes,
            3: self.solve_queue_time,
        }

        handler = handlers.get(choice)
        if handler:
            handler()
            self.ask_next_step()

    def solve_slow_query(self):
        """Provide solution for slow queries."""
        self.print_section(
            "Solution: Slow Query Execution",
            "Let's optimize your query performance."
        )

        self.print_commands([
            "bq query --dry_run < query.sql",
            "bq show -j JOB_ID --format=prettyjson | jq '.statistics.query.queryPlan'",
            'python -c "from mayor.rig.mcp import estimate_query_cost; print(estimate_query_cost(\'your query\'))"',
        ])

        print("\nOptimization checklist:")
        print("  1. Add WHERE filters to reduce data")
        print("  2. Select only needed columns (avoid SELECT *)")
        print("  3. Use partitioned/clustered tables")
        print("  4. Optimize JOIN order (smaller table first)")
        print("  5. Use WITH clauses for readability")
        print("  6. Consider materialized views")

        print("\nNext steps:")
        print("  - Run the /optimize Skill on your query")
        print("  - Check table partitioning/clustering")
        print("  - Review execution plan")

        self.print_links([
            ("Query Optimization", "/Users/crlough/gt/decentclaude/mayor/rig/docs/guides/query-optimization.md"),
            ("Performance Guide", "/Users/crlough/gt/decentclaude/mayor/rig/docs/guides/performance-optimization.md"),
        ])

    def solve_high_bytes(self):
        """Provide solution for high bytes scanned."""
        self.print_section(
            "Solution: Reduce Bytes Scanned",
            "Your query is scanning too much data, leading to high costs."
        )

        self.print_commands([
            "bq query --dry_run < query.sql",
            'python -c "from mayor.rig.mcp import get_table_size_bytes; print(get_table_size_bytes(\'project.dataset.table\'))"',
        ])

        print("\nKey optimizations:")
        print("  1. SELECT specific columns, not SELECT *")
        print("  2. Add WHERE filters, especially on partition columns")
        print("  3. Use LIMIT for testing")
        print("  4. Filter on clustered columns")
        print("  5. Use table samples for development")

        print("\nExample:")
        print("  -- Bad: Scans entire table")
        print("  SELECT * FROM large_table;")
        print("")
        print("  -- Good: Scans only needed data")
        print("  SELECT id, name FROM large_table")
        print("  WHERE partition_date = CURRENT_DATE()")
        print("    AND status = 'active';")

        self.print_links([
            ("Cost Management", "/Users/crlough/gt/decentclaude/mayor/rig/docs/guides/cost-management.md"),
        ])

    def solve_queue_time(self):
        """Provide solution for long queue times."""
        self.print_section(
            "Solution: Long Queue Time",
            "Your queries are waiting too long in the queue."
        )

        print("\nCauses and solutions:")
        print("  - Too many concurrent queries → Spread queries over time")
        print("  - Insufficient slots → Purchase slot reservations")
        print("  - Peak usage time → Schedule for off-peak hours")
        print("  - Project quota limits → Contact admin for increase")

        self.print_commands([
            "bq show -j JOB_ID | grep 'Slot Time'",
        ])

    # Cost Handlers
    def handle_cost(self):
        """Handle cost issue troubleshooting."""
        self.print_header("Cost Issue Troubleshooting")

        choice = self.get_choice(
            "What cost issue are you experiencing?",
            [
                "Unexpected charges",
                "Quota exceeded",
                "Need cost forecast",
            ]
        )

        if choice == 0:
            self.start()
            return

        handlers = {
            1: self.solve_unexpected_charges,
            2: self.solve_quota_exceeded,
            3: self.solve_cost_forecast,
        }

        handler = handlers.get(choice)
        if handler:
            handler()
            self.ask_next_step()

    def solve_unexpected_charges(self):
        """Provide solution for unexpected charges."""
        self.print_section(
            "Solution: Audit Costs",
            "Let's find what's causing high costs."
        )

        self.print_commands([
            r"bq query \"SELECT user_email, query, total_bytes_processed, creation_time FROM \`region-us\`.INFORMATION_SCHEMA.JOBS_BY_PROJECT WHERE creation_time >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY) AND total_bytes_processed > 1000000000000 ORDER BY total_bytes_processed DESC LIMIT 100\"",
            "bq ls -j --max_results=100",
        ])

        print("\nAudit steps:")
        print("  1. Review INFORMATION_SCHEMA.JOBS_BY_PROJECT")
        print("  2. Find expensive queries")
        print("  3. Check scheduled queries")
        print("  4. Review billing dashboard")
        print("  5. Set up cost allocation labels")
        print("  6. Implement query cost budgets")

        self.print_links([
            ("Cost Management", "/Users/crlough/gt/decentclaude/mayor/rig/docs/guides/cost-management.md"),
        ])

    def solve_quota_exceeded(self):
        """Provide solution for quota exceeded."""
        self.print_section(
            "Solution: Quota Limits",
            "You've hit a quota limit."
        )

        print("\nActions:")
        print("  1. Request quota increase via GCP Console")
        print("  2. Spread queries over time")
        print("  3. Use batch query API for large jobs")
        print("  4. Purchase slot reservations")
        print("  5. Optimize to reduce resource usage")

    def solve_cost_forecast(self):
        """Provide solution for cost forecasting."""
        self.print_section(
            "Solution: Cost Planning",
            "Estimate costs before running queries."
        )

        self.print_commands([
            'python -c "from mayor.rig.mcp import estimate_query_cost; print(estimate_query_cost(\'your query\'))"',
            "bq query --dry_run < query.sql",
        ])

        print("\nBest practices:")
        print("  1. Always dry run queries first")
        print("  2. Set up budget alerts")
        print("  3. Monitor cost trends")
        print("  4. Use table samples for development")

    # Data Quality Handlers
    def handle_data_quality(self):
        """Handle data quality issue troubleshooting."""
        self.print_header("Data Quality Issue Troubleshooting")

        choice = self.get_choice(
            "What data quality issue are you seeing?",
            [
                "Unexpected NULL values",
                "Duplicate records",
                "Schema problems",
                "Stale/outdated data",
            ]
        )

        if choice == 0:
            self.start()
            return

        handlers = {
            1: self.solve_nulls,
            2: self.solve_duplicates,
            3: self.solve_schema,
            4: self.solve_stale_data,
        }

        handler = handlers.get(choice)
        if handler:
            handler()
            self.ask_next_step()

    def solve_nulls(self):
        """Provide solution for NULL values."""
        self.print_section(
            "Solution: NULL Analysis",
            "Let's analyze NULL values in your data."
        )

        self.print_commands([
            'python -c "from mayor.rig.mcp import get_table_null_percentages; print(get_table_null_percentages(\'project.dataset.table\'))"',
            'python -c "from mayor.rig.mcp import describe_column; print(describe_column(\'project.dataset.table\', \'column_name\'))"',
            r"bq query \"SELECT COUNT(*) as total, COUNT(column_name) as non_null FROM \`project.dataset.table\`\"",
        ])

        print("\nSteps:")
        print("  1. Check NULL percentages across all columns")
        print("  2. Analyze specific columns with high NULL rates")
        print("  3. Check source data quality")
        print("  4. Look for patterns (e.g., NULLs after specific date)")

        print("\nSolutions:")
        print("  - Use COALESCE for default values")
        print("  - Add NOT NULL constraints")
        print("  - Validate at data ingestion")
        print("  - Check for LEFT JOIN creating NULLs")

    def solve_duplicates(self):
        """Provide solution for duplicate records."""
        self.print_section(
            "Solution: Find Duplicates",
            "Let's identify and remove duplicate records."
        )

        self.print_commands([
            'python -c "from mayor.rig.mcp import get_uniqueness_details; print(get_uniqueness_details(\'project.dataset.table\', \'id\'))"',
            r"bq query \"SELECT id, COUNT(*) as count FROM \`project.dataset.table\` GROUP BY id HAVING COUNT(*) > 1 ORDER BY count DESC\"",
        ])

        print("\nDeduplication example:")
        print("  CREATE OR REPLACE TABLE project.dataset.table AS")
        print("  SELECT * EXCEPT(rn)")
        print("  FROM (")
        print("    SELECT")
        print("      *,")
        print("      ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) as rn")
        print("    FROM project.dataset.table")
        print("  )")
        print("  WHERE rn = 1;")

        print("\nPrevention:")
        print("  - Add unique key constraints")
        print("  - Use MERGE for upserts")
        print("  - Check source for duplicates")
        print("  - Review JOIN logic")

    def solve_schema(self):
        """Provide solution for schema issues."""
        self.print_section(
            "Solution: Schema Analysis",
            "Let's examine your table schema."
        )

        know_schema = self.get_choice(
            "Do you know what the schema should be?",
            ["Yes - I can compare it", "No - I need to explore it"]
        )

        if know_schema == 1:
            # Compare schemas
            self.print_commands([
                'python -c "from mayor.rig.mcp import compare_schemas; print(compare_schemas(\'project.dataset.table_a\', \'project.dataset.table_b\'))"',
                "bq show --schema --format=prettyjson PROJECT:DATASET.TABLE",
            ])

            print("\nUse compare_schemas to find:")
            print("  - Columns only in one table")
            print("  - Type mismatches")
            print("  - Schema evolution issues")

        elif know_schema == 2:
            # Explore schema
            self.print_commands([
                'python -c "from mayor.rig.mcp import get_table_metadata; print(get_table_metadata(\'project.dataset.table\'))"',
                'python -c "from mayor.rig.mcp import describe_table_columns; print(describe_table_columns(\'project.dataset.table\'))"',
            ])

            print("\nExploration steps:")
            print("  1. Get table metadata")
            print("  2. Describe all columns")
            print("  3. Check data types")
            print("  4. Review documentation")

    def solve_stale_data(self):
        """Provide solution for stale data."""
        self.print_section(
            "Solution: Data Freshness",
            "Let's check when your data was last updated."
        )

        self.print_commands([
            'python -c "from mayor.rig.mcp import get_data_freshness; print(get_data_freshness(\'project.dataset.table\', \'timestamp_column\'))"',
            r"bq query \"SELECT MAX(timestamp_column) as latest, TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX(timestamp_column), HOUR) as hours_old FROM \`project.dataset.table\`\"",
            "bq show --format=prettyjson PROJECT:DATASET.TABLE | jq '.lastModifiedTime'",
        ])

        print("\nInvestigate:")
        print("  1. Check pipeline logs for failures")
        print("  2. Verify data source availability")
        print("  3. Review scheduler configuration")
        print("  4. Check for timezone issues")

        print("\nSolutions:")
        print("  - Set up freshness alerts")
        print("  - Add data validation checks")
        print("  - Monitor pipeline health")

    # Tool Error Handlers
    def handle_tool_error(self):
        """Handle tool/configuration error troubleshooting."""
        self.print_header("Tool/Configuration Error Troubleshooting")

        choice = self.get_choice(
            "What type of error are you getting?",
            [
                "Missing dependency/import error",
                "Configuration error",
                "API error",
            ]
        )

        if choice == 0:
            self.start()
            return

        handlers = {
            1: self.solve_missing_dependency,
            2: self.solve_config_error,
            3: self.solve_api_error,
        }

        handler = handlers.get(choice)
        if handler:
            handler()
            self.ask_next_step()

    def solve_missing_dependency(self):
        """Provide solution for missing dependencies."""
        self.print_section(
            "Solution: Missing Dependencies",
            "Let's install the required dependencies."
        )

        self.print_commands([
            "pip list | grep google-cloud-bigquery",
            "which gcloud",
            "python --version",
            'python -c "from google.cloud import bigquery; print(\'OK\')"',
        ])

        print("\nInstallation steps:")
        print("  1. Install BigQuery client:")
        print("     pip install google-cloud-bigquery")
        print("")
        print("  2. Install all requirements:")
        print("     pip install -r requirements.txt")
        print("")
        print("  3. Install gcloud CLI:")
        print("     curl https://sdk.cloud.google.com | bash")
        print("")
        print("  4. Activate virtual environment:")
        print("     source venv/bin/activate")

    def solve_config_error(self):
        """Provide solution for configuration errors."""
        self.print_section(
            "Solution: Configuration Error",
            "Let's fix your configuration."
        )

        self.print_commands([
            "gcloud config list",
            "echo $GOOGLE_CLOUD_PROJECT",
            "ls ~/.config/gcloud/application_default_credentials.json",
            "bq ls",
        ])

        print("\nConfiguration steps:")
        print("  1. Set project:")
        print("     gcloud config set project PROJECT_ID")
        print("")
        print("  2. Set environment variable:")
        print("     export GOOGLE_CLOUD_PROJECT=your-project-id")
        print("")
        print("  3. Create .env file:")
        print("     echo 'GOOGLE_CLOUD_PROJECT=your-project-id' > .env")
        print("")
        print("  4. Re-authenticate:")
        print("     gcloud auth login")
        print("     gcloud auth application-default login")

    def solve_api_error(self):
        """Provide solution for API errors."""
        self.print_section(
            "Solution: API Error",
            "Let's troubleshoot the API issue."
        )

        print("\nCheck:")
        print("  1. Is BigQuery API enabled?")
        print("     - Go to GCP Console > APIs & Services")
        print("     - Enable BigQuery API")
        print("")
        print("  2. Are you hitting quota limits?")
        print("     - Check quota usage in console")
        print("     - Request increase if needed")
        print("")
        print("  3. Network connectivity")
        print("     - Test internet connection")
        print("     - Check firewall settings")
        print("")
        print("  4. Read the error message carefully")
        print("     - Often contains the exact issue")
        print("     - Search for error code")

    def ask_next_step(self):
        """Ask user what to do next."""
        print("\n" + "=" * 70)
        choice = self.get_choice(
            "What would you like to do next?",
            [
                "Start over with a new problem",
                "Exit",
            ]
        )

        if choice == 1:
            self.start()
        else:
            print("\nGoodbye! Check the documentation for more help:")
            print("  /Users/crlough/gt/decentclaude/mayor/rig/docs/guides/troubleshooting-tree.md")


def search_knowledge_base(query: str):
    """Search the knowledge base for similar issues."""
    print(f"\nSearching knowledge base for: '{query}'")
    print("\nNote: Full knowledge base search integration coming soon!")
    print("For now, check these resources:")
    print("  - /Users/crlough/gt/decentclaude/mayor/rig/docs/guides/troubleshooting-tree.md")
    print("  - /Users/crlough/gt/decentclaude/mayor/rig/docs/sql-style-guide.md")
    print("  - /Users/crlough/gt/decentclaude/mayor/rig/docs/guides/performance-optimization.md")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Interactive BigQuery troubleshooting assistant"
    )
    parser.add_argument(
        "--category",
        choices=["sql", "performance", "cost", "quality", "tool"],
        help="Jump directly to a specific category"
    )
    parser.add_argument(
        "--search",
        type=str,
        help="Search knowledge base for similar issues"
    )

    args = parser.parse_args()

    if args.search:
        search_knowledge_base(args.search)
        return

    tree = TroubleshootingTree()

    # Jump to specific category if requested
    if args.category:
        handlers = {
            "sql": tree.handle_sql_error,
            "performance": tree.handle_performance,
            "cost": tree.handle_cost,
            "quality": tree.handle_data_quality,
            "tool": tree.handle_tool_error,
        }
        handler = handlers.get(args.category)
        if handler:
            tree.print_header("BigQuery Troubleshooting Assistant")
            handler()
            tree.ask_next_step()
    else:
        tree.start()


if __name__ == "__main__":
    main()
