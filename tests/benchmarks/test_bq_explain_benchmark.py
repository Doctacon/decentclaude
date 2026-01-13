"""
Performance benchmarks for bq-explain utility.

This module benchmarks the query execution plan analysis functionality
with different query complexities.

Run with:
    pytest tests/benchmarks/test_bq_explain_benchmark.py --benchmark-only
    pytest tests/benchmarks/test_bq_explain_benchmark.py --benchmark-autosave
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib"))


@pytest.mark.benchmark
@pytest.mark.bq_explain
class TestBQExplainBenchmarks:
    """Benchmarks for bq-explain utility."""

    def test_parse_simple_query_plan(self, benchmark, mock_query_job):
        """Benchmark parsing a simple query plan with 3 stages."""
        job = mock_query_job(
            job_id="test-job-1",
            total_bytes_processed=1000000,
            total_slot_ms=5000,
            query_plan_stages=3
        )

        def parse_plan():
            plan_info = {
                'job_id': job.job_id,
                'total_bytes_processed': job.total_bytes_processed,
                'total_slot_ms': job.total_slot_ms,
                'stages': []
            }

            for stage in job.query_plan:
                stage_info = {
                    'name': stage.name,
                    'read_ratio': stage.read_ratio_avg,
                    'write_ratio': stage.write_ratio_avg,
                    'compute_ratio': stage.compute_ratio_avg,
                    'wait_ratio': stage.wait_ratio_avg,
                    'records_read': stage.records_read,
                    'records_written': stage.records_written,
                }
                plan_info['stages'].append(stage_info)

            return plan_info

        result = benchmark(parse_plan)
        assert len(result['stages']) == 3
        assert result['job_id'] == 'test-job-1'

    def test_parse_complex_query_plan(self, benchmark, mock_query_job):
        """Benchmark parsing a complex query plan with 20 stages."""
        job = mock_query_job(
            job_id="test-job-2",
            total_bytes_processed=100000000,
            total_slot_ms=50000,
            query_plan_stages=20
        )

        def parse_plan():
            plan_info = {
                'job_id': job.job_id,
                'total_bytes_processed': job.total_bytes_processed,
                'total_slot_ms': job.total_slot_ms,
                'stages': []
            }

            for stage in job.query_plan:
                stage_info = {
                    'name': stage.name,
                    'read_ratio': stage.read_ratio_avg,
                    'write_ratio': stage.write_ratio_avg,
                    'compute_ratio': stage.compute_ratio_avg,
                    'wait_ratio': stage.wait_ratio_avg,
                    'records_read': stage.records_read,
                    'records_written': stage.records_written,
                    'shuffle_output_bytes': stage.shuffle_output_bytes,
                }
                plan_info['stages'].append(stage_info)

            return plan_info

        result = benchmark(parse_plan)
        assert len(result['stages']) == 20

    def test_analyze_stage_performance(self, benchmark, mock_query_job):
        """Benchmark analyzing performance bottlenecks in query stages."""
        job = mock_query_job(query_plan_stages=10)

        def analyze_performance():
            bottlenecks = []
            total_time = sum(
                stage.read_ratio_avg + stage.write_ratio_avg +
                stage.compute_ratio_avg + stage.wait_ratio_avg
                for stage in job.query_plan
            )

            for stage in job.query_plan:
                stage_time = (
                    stage.read_ratio_avg + stage.write_ratio_avg +
                    stage.compute_ratio_avg + stage.wait_ratio_avg
                )
                stage_pct = (stage_time / total_time * 100) if total_time > 0 else 0

                if stage_pct > 20:  # Stages taking more than 20% of time
                    bottleneck = {
                        'stage': stage.name,
                        'percentage': stage_pct,
                        'read_ratio': stage.read_ratio_avg,
                        'write_ratio': stage.write_ratio_avg,
                        'compute_ratio': stage.compute_ratio_avg,
                        'wait_ratio': stage.wait_ratio_avg,
                    }
                    bottlenecks.append(bottleneck)

            return bottlenecks

        result = benchmark(analyze_performance)
        assert isinstance(result, list)

    def test_calculate_cost_estimate(self, benchmark, mock_query_job):
        """Benchmark calculating cost estimates from query plan."""
        job = mock_query_job(
            total_bytes_processed=100000000000,  # 100GB
            total_slot_ms=500000
        )

        def calculate_cost():
            # BigQuery pricing: $5 per TB processed
            bytes_in_tb = job.total_bytes_processed / (1024 ** 4)
            scan_cost = bytes_in_tb * 5.0

            # Slot time cost (if using on-demand)
            slot_hours = job.total_slot_ms / (1000 * 3600)
            slot_cost = slot_hours * 0.04  # Approximate on-demand cost

            return {
                'scan_cost': round(scan_cost, 2),
                'slot_cost': round(slot_cost, 2),
                'total_cost': round(scan_cost + slot_cost, 2),
                'bytes_processed': job.total_bytes_processed,
                'slot_ms': job.total_slot_ms,
            }

        result = benchmark(calculate_cost)
        assert 'total_cost' in result
        assert result['bytes_processed'] > 0

    def test_format_bytes_to_human_readable(self, benchmark):
        """Benchmark formatting bytes into human-readable sizes."""
        byte_values = [
            100,
            1024,
            1024 * 1024,
            1024 * 1024 * 1024,
            1024 * 1024 * 1024 * 1024,
            1024 * 1024 * 1024 * 1024 * 1024,
        ]

        def format_bytes():
            results = []
            for bytes_value in byte_values:
                value = bytes_value
                for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
                    if value < 1024.0:
                        results.append(f"{value:.2f} {unit}")
                        break
                    value /= 1024.0
            return results

        result = benchmark(format_bytes)
        assert len(result) == len(byte_values)
        assert 'B' in result[0]
        assert 'KB' in result[1]

    def test_format_duration_to_human_readable(self, benchmark):
        """Benchmark formatting milliseconds into human-readable durations."""
        durations_ms = [
            100,      # milliseconds
            1000,     # 1 second
            60000,    # 1 minute
            3600000,  # 1 hour
            86400000, # 1 day
        ]

        def format_duration():
            results = []
            for ms in durations_ms:
                if ms < 1000:
                    results.append(f"{ms:.0f}ms")
                elif ms < 60000:
                    results.append(f"{ms/1000:.2f}s")
                elif ms < 3600000:
                    results.append(f"{ms/60000:.2f}m")
                else:
                    results.append(f"{ms/3600000:.2f}h")
            return results

        result = benchmark(format_duration)
        assert len(result) == len(durations_ms)
        assert 'ms' in result[0]
        assert 's' in result[1]

    def test_identify_optimization_opportunities(self, benchmark, mock_query_job):
        """Benchmark identifying optimization opportunities from query plan."""
        job = mock_query_job(query_plan_stages=15)

        def find_optimizations():
            opportunities = []

            # Check for high shuffle operations
            for stage in job.query_plan:
                if stage.shuffle_output_bytes > 10000000:  # 10MB
                    opportunities.append({
                        'type': 'high_shuffle',
                        'stage': stage.name,
                        'shuffle_bytes': stage.shuffle_output_bytes,
                        'recommendation': 'Consider partitioning or clustering to reduce shuffle'
                    })

                # Check for high wait ratios
                if stage.wait_ratio_avg > 0.3:
                    opportunities.append({
                        'type': 'high_wait',
                        'stage': stage.name,
                        'wait_ratio': stage.wait_ratio_avg,
                        'recommendation': 'Consider increasing slot allocation'
                    })

                # Check for large reads
                if stage.records_read > 1000000:
                    opportunities.append({
                        'type': 'large_scan',
                        'stage': stage.name,
                        'records_read': stage.records_read,
                        'recommendation': 'Add WHERE clauses to filter data earlier'
                    })

            return opportunities

        result = benchmark(find_optimizations)
        assert isinstance(result, list)

    def test_format_explain_output_text(self, benchmark, mock_query_job):
        """Benchmark formatting explain output as text."""
        job = mock_query_job(query_plan_stages=10)

        def format_text():
            lines = []
            lines.append("Query Execution Plan")
            lines.append("=" * 50)
            lines.append(f"Job ID: {job.job_id}")
            lines.append(f"Total Bytes Processed: {job.total_bytes_processed:,}")
            lines.append(f"Total Slot Milliseconds: {job.total_slot_ms:,}")
            lines.append("\nStages:")

            for i, stage in enumerate(job.query_plan):
                lines.append(f"\n  Stage {i}: {stage.name}")
                lines.append(f"    Read Ratio: {stage.read_ratio_avg:.2%}")
                lines.append(f"    Write Ratio: {stage.write_ratio_avg:.2%}")
                lines.append(f"    Compute Ratio: {stage.compute_ratio_avg:.2%}")
                lines.append(f"    Wait Ratio: {stage.wait_ratio_avg:.2%}")
                lines.append(f"    Records Read: {stage.records_read:,}")
                lines.append(f"    Records Written: {stage.records_written:,}")

            return '\n'.join(lines)

        result = benchmark(format_text)
        assert 'Query Execution Plan' in result
        assert 'Job ID' in result

    def test_format_explain_output_json(self, benchmark, mock_query_job):
        """Benchmark formatting explain output as JSON."""
        import json

        job = mock_query_job(query_plan_stages=20)

        def format_json():
            plan_data = {
                'job_id': job.job_id,
                'total_bytes_processed': job.total_bytes_processed,
                'total_slot_ms': job.total_slot_ms,
                'stages': []
            }

            for stage in job.query_plan:
                stage_data = {
                    'name': stage.name,
                    'read_ratio': stage.read_ratio_avg,
                    'write_ratio': stage.write_ratio_avg,
                    'compute_ratio': stage.compute_ratio_avg,
                    'wait_ratio': stage.wait_ratio_avg,
                    'records_read': stage.records_read,
                    'records_written': stage.records_written,
                    'shuffle_output_bytes': stage.shuffle_output_bytes,
                }
                plan_data['stages'].append(stage_data)

            return json.dumps(plan_data, indent=2)

        result = benchmark(format_json)
        parsed = json.loads(result)
        assert len(parsed['stages']) == 20
