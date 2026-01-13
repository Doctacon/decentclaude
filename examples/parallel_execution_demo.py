#!/usr/bin/env python3
"""
Parallel Execution Demo for BigQuery Utilities

This script demonstrates the performance improvements achieved by using
parallel execution for batch operations in BigQuery utilities.

Usage:
    python parallel_execution_demo.py

Requirements:
    - google-cloud-bigquery
    - rich (for progress bars)
"""

import time
import subprocess
import sys
from typing import List, Tuple
from pathlib import Path

# Sample table IDs for demonstration
# Replace these with your actual BigQuery table IDs
SAMPLE_TABLES = [
    "bigquery-public-data.samples.shakespeare",
    "bigquery-public-data.samples.gsod",
    "bigquery-public-data.samples.natality",
    "bigquery-public-data.samples.github_timeline",
]

# Sample table pairs for comparison
SAMPLE_PAIRS = [
    ("bigquery-public-data.samples.shakespeare", "bigquery-public-data.samples.shakespeare"),
    ("bigquery-public-data.samples.gsod", "bigquery-public-data.samples.gsod"),
]


def run_command(cmd: List[str], description: str) -> Tuple[float, int]:
    """
    Run a command and measure execution time.

    Args:
        cmd: Command to run as list of arguments
        description: Description of the command

    Returns:
        Tuple of (execution_time, return_code)
    """
    print(f"\n{description}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 80)

    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    execution_time = time.time() - start_time

    print(f"Execution time: {execution_time:.2f} seconds")
    print(f"Return code: {result.returncode}")

    if result.returncode != 0:
        print(f"Error output: {result.stderr}")

    return execution_time, result.returncode


def demo_bq_profile():
    """Demonstrate parallel profiling with bq-profile"""
    print("\n" + "=" * 80)
    print("BQ-PROFILE PARALLEL EXECUTION DEMO")
    print("=" * 80)

    # Find the bq-profile script
    script_dir = Path(__file__).parent.parent / "bin" / "data-utils"
    bq_profile = script_dir / "bq-profile"

    if not bq_profile.exists():
        print(f"Error: bq-profile not found at {bq_profile}")
        return

    tables = SAMPLE_TABLES[:2]  # Use first 2 tables

    print(f"\nProfiling {len(tables)} tables:")
    for table in tables:
        print(f"  - {table}")

    # Sequential execution (simulate by running one at a time)
    print("\n--- Sequential Execution (baseline) ---")
    sequential_time = 0
    for table in tables:
        cmd = [str(bq_profile), table, "--format=json", "--no-cache"]
        exec_time, _ = run_command(cmd, f"Profiling {table}")
        sequential_time += exec_time

    print(f"\nTotal sequential time: {sequential_time:.2f} seconds")

    # Parallel execution
    print("\n--- Parallel Execution (2 workers) ---")
    cmd = [
        str(bq_profile),
        *tables,
        "--parallel", "2",
        "--format=json",
        "--no-cache"
    ]
    parallel_time, _ = run_command(cmd, f"Profiling {len(tables)} tables in parallel")

    # Calculate speedup
    if parallel_time > 0:
        speedup = sequential_time / parallel_time
        print(f"\n{'-' * 80}")
        print(f"Performance Improvement:")
        print(f"  Sequential time: {sequential_time:.2f}s")
        print(f"  Parallel time:   {parallel_time:.2f}s")
        print(f"  Speedup:         {speedup:.2f}x")
        print(f"  Time saved:      {sequential_time - parallel_time:.2f}s ({((1 - parallel_time/sequential_time) * 100):.1f}%)")


def demo_bq_schema_diff():
    """Demonstrate parallel schema comparison with bq-schema-diff"""
    print("\n" + "=" * 80)
    print("BQ-SCHEMA-DIFF PARALLEL EXECUTION DEMO")
    print("=" * 80)

    # Find the bq-schema-diff script
    script_dir = Path(__file__).parent.parent / "bin" / "data-utils"
    bq_schema_diff = script_dir / "bq-schema-diff"

    if not bq_schema_diff.exists():
        print(f"Error: bq-schema-diff not found at {bq_schema_diff}")
        return

    pairs = SAMPLE_PAIRS

    print(f"\nComparing {len(pairs)} table pairs:")
    for table_a, table_b in pairs:
        print(f"  - {table_a} vs {table_b}")

    # Sequential execution
    print("\n--- Sequential Execution (baseline) ---")
    sequential_time = 0
    for table_a, table_b in pairs:
        cmd = [str(bq_schema_diff), table_a, table_b, "--format=json", "--no-cache"]
        exec_time, _ = run_command(cmd, f"Comparing {table_a} vs {table_b}")
        sequential_time += exec_time

    print(f"\nTotal sequential time: {sequential_time:.2f} seconds")

    # Parallel execution using stdin
    print("\n--- Parallel Execution (2 workers) ---")

    # Create pairs input
    pairs_input = "\n".join([f"{a}:{b}" for a, b in pairs])

    cmd = [
        str(bq_schema_diff),
        "--parallel", "2",
        "--format=json",
        "--no-cache"
    ]

    print(f"Comparing {len(pairs)} pairs in parallel")
    print(f"Command: echo '{pairs_input}' | {' '.join(cmd)}")
    print("-" * 80)

    start_time = time.time()
    result = subprocess.run(
        cmd,
        input=pairs_input,
        capture_output=True,
        text=True
    )
    parallel_time = time.time() - start_time

    print(f"Execution time: {parallel_time:.2f} seconds")
    print(f"Return code: {result.returncode}")

    # Calculate speedup
    if parallel_time > 0:
        speedup = sequential_time / parallel_time
        print(f"\n{'-' * 80}")
        print(f"Performance Improvement:")
        print(f"  Sequential time: {sequential_time:.2f}s")
        print(f"  Parallel time:   {parallel_time:.2f}s")
        print(f"  Speedup:         {speedup:.2f}x")
        print(f"  Time saved:      {sequential_time - parallel_time:.2f}s ({((1 - parallel_time/sequential_time) * 100):.1f}%)")


def demo_bq_table_compare():
    """Demonstrate parallel table comparison with bq-table-compare"""
    print("\n" + "=" * 80)
    print("BQ-TABLE-COMPARE PARALLEL EXECUTION DEMO")
    print("=" * 80)

    # Find the bq-table-compare script
    script_dir = Path(__file__).parent.parent / "bin" / "data-utils"
    bq_table_compare = script_dir / "bq-table-compare"

    if not bq_table_compare.exists():
        print(f"Error: bq-table-compare not found at {bq_table_compare}")
        return

    pairs = SAMPLE_PAIRS

    print(f"\nComparing {len(pairs)} table pairs:")
    for table_a, table_b in pairs:
        print(f"  - {table_a} vs {table_b}")

    # Sequential execution
    print("\n--- Sequential Execution (baseline) ---")
    sequential_time = 0
    for table_a, table_b in pairs:
        cmd = [
            str(bq_table_compare),
            table_a, table_b,
            "--format=json",
            "--skip-stats",
            "--skip-samples"
        ]
        exec_time, _ = run_command(cmd, f"Comparing {table_a} vs {table_b}")
        sequential_time += exec_time

    print(f"\nTotal sequential time: {sequential_time:.2f} seconds")

    # Parallel execution using stdin
    print("\n--- Parallel Execution (2 workers) ---")

    # Create pairs input
    pairs_input = "\n".join([f"{a}:{b}" for a, b in pairs])

    cmd = [
        str(bq_table_compare),
        "--parallel", "2",
        "--format=json",
        "--skip-stats",
        "--skip-samples"
    ]

    print(f"Comparing {len(pairs)} pairs in parallel")
    print(f"Command: echo '{pairs_input}' | {' '.join(cmd)}")
    print("-" * 80)

    start_time = time.time()
    result = subprocess.run(
        cmd,
        input=pairs_input,
        capture_output=True,
        text=True
    )
    parallel_time = time.time() - start_time

    print(f"Execution time: {parallel_time:.2f} seconds")
    print(f"Return code: {result.returncode}")

    # Calculate speedup
    if parallel_time > 0:
        speedup = sequential_time / parallel_time
        print(f"\n{'-' * 80}")
        print(f"Performance Improvement:")
        print(f"  Sequential time: {sequential_time:.2f}s")
        print(f"  Parallel time:   {parallel_time:.2f}s")
        print(f"  Speedup:         {speedup:.2f}x")
        print(f"  Time saved:      {sequential_time - parallel_time:.2f}s ({((1 - parallel_time/sequential_time) * 100):.1f}%)")


def print_summary():
    """Print summary and usage recommendations"""
    print("\n" + "=" * 80)
    print("SUMMARY AND RECOMMENDATIONS")
    print("=" * 80)

    print("""
Parallel Execution Benefits:
- Significant speedup for batch operations (typically 1.5x to 3x faster)
- Better resource utilization on multi-core systems
- Progress tracking with rich library integration
- Graceful error handling (partial failures don't stop batch)

Best Practices:
1. Use --parallel N where N is based on:
   - Number of CPU cores (typically 2-4x core count)
   - Network bandwidth and BigQuery quota
   - Complexity of operations

2. Enable --progress for long-running batch operations:
   bq-profile --parallel 4 --progress table1 table2 table3 table4

3. Use --pairs-file for large batch operations:
   bq-schema-diff --parallel 4 --pairs-file=pairs.txt

4. Pipeline with stdin for dynamic workflows:
   cat tables.txt | bq-profile --parallel 4 --progress

Optimal Worker Counts:
- Small operations (metadata only): 8-16 workers
- Medium operations (with stats): 4-8 workers
- Large operations (with samples): 2-4 workers

Trade-offs:
- More workers = faster completion
- But also = higher API quota consumption
- Monitor BigQuery quota and adjust accordingly
""")


def main():
    """Run all demos"""
    print("""
=================================================================================
BIGQUERY UTILITIES - PARALLEL EXECUTION PERFORMANCE DEMO
=================================================================================

This demo shows the performance improvements from parallel execution in:
- bq-profile: Batch table profiling
- bq-schema-diff: Batch schema comparison
- bq-table-compare: Batch table comparison

NOTE: This demo uses public BigQuery datasets. You need:
1. Google Cloud credentials configured
2. Access to bigquery-public-data

Press Ctrl+C to skip any demo.
=================================================================================
""")

    try:
        # Run demos
        demo_bq_profile()
    except KeyboardInterrupt:
        print("\n\nSkipping bq-profile demo...")
    except Exception as e:
        print(f"\nError in bq-profile demo: {e}")

    try:
        demo_bq_schema_diff()
    except KeyboardInterrupt:
        print("\n\nSkipping bq-schema-diff demo...")
    except Exception as e:
        print(f"\nError in bq-schema-diff demo: {e}")

    try:
        demo_bq_table_compare()
    except KeyboardInterrupt:
        print("\n\nSkipping bq-table-compare demo...")
    except Exception as e:
        print(f"\nError in bq-table-compare demo: {e}")

    # Print summary
    print_summary()

    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
