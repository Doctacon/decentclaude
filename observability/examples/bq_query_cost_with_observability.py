#!/usr/bin/env python3
"""
BigQuery Query Cost Estimator with Observability

This is an example of integrating the observability framework with
the existing bq-query-cost utility. It demonstrates:
- Structured logging
- Performance tracking
- Cost monitoring and alerting
- Error tracking
- Usage analytics
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to import observability
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from observability import (
    LogContext,
    capture_exception,
    get_analytics,
    get_logger,
    init_observability,
    set_correlation_id,
    track_cli_command,
    track_cost,
    track_performance,
    with_error_tracking,
)

# Initialize observability
init_observability()

logger = get_logger(__name__)
analytics = get_analytics()


@with_error_tracking(context={"module": "bq_query_cost"})
def estimate_query_cost(query: str, output_format: str = "text") -> dict:
    """
    Estimate the cost of running a BigQuery query.

    Args:
        query: SQL query to estimate
        output_format: Output format (text or json)

    Returns:
        Dictionary with cost estimate details
    """
    with track_performance("estimate_query_cost", tags={"output_format": output_format}):
        try:
            from google.cloud import bigquery

            client = bigquery.Client()

            logger.info("Starting cost estimation", query_length=len(query))

            # Dry run to get bytes that would be processed
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            query_job = client.query(query, job_config=job_config)

            bytes_processed = query_job.total_bytes_processed
            tb_processed = bytes_processed / (1024**4)

            # BigQuery pricing: $5 per TB processed (on-demand pricing)
            cost_per_tb = 5.0
            estimated_cost = tb_processed * cost_per_tb

            # Track cost metrics
            track_cost(
                operation="query_cost_estimate",
                bytes_processed=bytes_processed,
                estimated_cost_usd=estimated_cost,
                tags={
                    "project": client.project,
                    "output_format": output_format,
                },
            )

            # Track BigQuery operation
            analytics.track_bigquery_operation(
                operation_type="cost_estimate",
                bytes_processed=bytes_processed,
            )

            result = {
                "query_length": len(query),
                "bytes_processed": bytes_processed,
                "tb_processed": round(tb_processed, 6),
                "estimated_cost_usd": round(estimated_cost, 4),
                "project": client.project,
                "pricing_model": "on-demand",
                "cost_per_tb": cost_per_tb,
            }

            logger.info(
                "Cost estimation completed",
                bytes_processed=bytes_processed,
                estimated_cost_usd=round(estimated_cost, 4),
            )

            return result

        except ImportError as e:
            logger.error("BigQuery client library not installed")
            capture_exception(
                e,
                context={"module": "bq_query_cost", "operation": "estimate_query_cost"},
            )
            raise
        except Exception as e:
            logger.error(
                "Cost estimation failed",
                error=str(e),
                error_type=type(e).__name__,
            )
            capture_exception(
                e,
                context={
                    "module": "bq_query_cost",
                    "operation": "estimate_query_cost",
                    "query_length": len(query),
                },
            )
            raise


def format_output(result: dict, output_format: str) -> str:
    """Format the output based on requested format."""
    if output_format == "json":
        import json

        return json.dumps(result, indent=2)
    else:
        # Text format with colors
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        RED = "\033[31m"
        BLUE = "\033[34m"
        RESET = "\033[0m"

        # Determine color based on cost
        cost = result["estimated_cost_usd"]
        if cost < 0.01:
            cost_color = GREEN
        elif cost < 1.0:
            cost_color = YELLOW
        else:
            cost_color = RED

        output = f"""
{BLUE}BigQuery Query Cost Estimate{RESET}
{'=' * 50}

Query Length:        {result['query_length']} characters
Bytes Processed:     {result['bytes_processed']:,} bytes
TB Processed:        {result['tb_processed']:.6f} TB
Project:             {result['project']}
Pricing Model:       {result['pricing_model']}
Cost per TB:         ${result['cost_per_tb']:.2f}

{cost_color}Estimated Cost:      ${result['estimated_cost_usd']:.4f} USD{RESET}
"""
        return output


def main():
    """Main entry point with full observability."""
    parser = argparse.ArgumentParser(
        description="Estimate BigQuery query cost with observability"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="SQL query to estimate (or use --file)",
    )
    parser.add_argument(
        "-f",
        "--file",
        help="Read query from file",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--correlation-id",
        help="Set correlation ID for distributed tracing",
    )

    args = parser.parse_args()

    # Set correlation ID for tracing
    correlation_id = set_correlation_id(args.correlation_id)

    # Track command arguments (without sensitive data)
    analytics.track_command_argument(
        "bq-query-cost",
        "format",
        args.format,
    )
    if args.file:
        analytics.track_command_argument(
            "bq-query-cost",
            "file",
            args.file,
        )

    # Get query from file or argument
    if args.file:
        try:
            query = Path(args.file).read_text()
            logger.debug("Query loaded from file", file=args.file)
        except Exception as e:
            logger.error("Failed to read query file", file=args.file, error=str(e))
            capture_exception(e, context={"file": args.file})
            sys.exit(1)
    elif args.query:
        query = args.query
    else:
        parser.print_help()
        sys.exit(1)

    # Track the command execution
    with track_cli_command(
        "bq-query-cost",
        args={
            "format": args.format,
            "has_file": bool(args.file),
            "query_length": len(query),
        },
    ):
        try:
            # Use LogContext for operation tracking
            with LogContext(operation="bq_query_cost", correlation_id=correlation_id):
                result = estimate_query_cost(query, args.format)
                output = format_output(result, args.format)
                print(output)

                # Track feature usage
                analytics.track_feature_usage(
                    "query_cost_estimation",
                    context={
                        "format": args.format,
                        "cost_usd": result["estimated_cost_usd"],
                    },
                )

        except Exception as e:
            logger.critical("Command failed", error=str(e))
            sys.exit(1)


if __name__ == "__main__":
    main()
