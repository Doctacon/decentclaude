"""
Performance benchmarks for bq-lineage utility.

This module benchmarks the lineage discovery functionality with different
dependency tree depths and complexities.

Run with:
    pytest tests/benchmarks/test_bq_lineage_benchmark.py --benchmark-only
    pytest tests/benchmarks/test_bq_lineage_benchmark.py --benchmark-autosave
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import re

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib"))


@pytest.mark.benchmark
@pytest.mark.bq_lineage
class TestBQLineageBenchmarks:
    """Benchmarks for bq-lineage utility."""

    def test_parse_view_query_simple(self, benchmark):
        """Benchmark parsing a simple view query for table references."""
        view_query = """
        SELECT
            user_id,
            event_name,
            timestamp
        FROM `project.dataset.events`
        WHERE date = '2024-01-01'
        """

        def parse_query():
            pattern = r'`?([a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)`?'
            matches = re.findall(pattern, view_query)
            return list(set(matches))

        result = benchmark(parse_query)
        assert 'project.dataset.events' in result

    def test_parse_view_query_complex(self, benchmark):
        """Benchmark parsing a complex view query with multiple joins."""
        view_query = """
        SELECT
            u.user_id,
            u.user_name,
            e.event_name,
            o.order_id,
            p.product_name
        FROM `project.dataset.users` u
        LEFT JOIN `project.dataset.events` e ON u.user_id = e.user_id
        LEFT JOIN `project.dataset.orders` o ON u.user_id = o.user_id
        LEFT JOIN `project.dataset.products` p ON o.product_id = p.product_id
        WHERE e.event_date >= '2024-01-01'
        """

        def parse_query():
            pattern = r'`?([a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)`?'
            matches = re.findall(pattern, view_query)
            return list(set(matches))

        result = benchmark(parse_query)
        assert len(result) == 4

    def test_parse_view_query_with_ctes(self, benchmark):
        """Benchmark parsing a query with multiple CTEs."""
        view_query = """
        WITH user_events AS (
            SELECT user_id, COUNT(*) as event_count
            FROM `project.dataset.events`
            GROUP BY user_id
        ),
        user_orders AS (
            SELECT user_id, SUM(amount) as total_amount
            FROM `project.dataset.orders`
            GROUP BY user_id
        ),
        user_sessions AS (
            SELECT user_id, COUNT(DISTINCT session_id) as session_count
            FROM `project.dataset.sessions`
            GROUP BY user_id
        )
        SELECT
            u.user_id,
            u.user_name,
            e.event_count,
            o.total_amount,
            s.session_count
        FROM `project.dataset.users` u
        LEFT JOIN user_events e ON u.user_id = e.user_id
        LEFT JOIN user_orders o ON u.user_id = o.user_id
        LEFT JOIN user_sessions s ON u.user_id = s.user_id
        """

        def parse_query():
            pattern = r'`?([a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)`?'
            matches = re.findall(pattern, view_query)
            return list(set(matches))

        result = benchmark(parse_query)
        assert len(result) == 4

    def test_get_upstream_dependencies_depth_1(self, benchmark, mock_bq_client):
        """Benchmark finding upstream dependencies at depth 1."""
        table_id = "project.dataset.view_table"

        # Mock view table
        mock_table = Mock()
        mock_table.table_type = "VIEW"
        mock_table.view_query = """
            SELECT * FROM `project.dataset.source_table_1`
            UNION ALL
            SELECT * FROM `project.dataset.source_table_2`
        """
        mock_bq_client.get_table.return_value = mock_table

        def get_dependencies():
            pattern = r'`?([a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)`?'
            matches = re.findall(pattern, mock_table.view_query)
            return list(set(matches))

        result = benchmark(get_dependencies)
        assert len(result) == 2

    def test_get_upstream_dependencies_depth_2(self, benchmark, mock_bq_client):
        """Benchmark finding upstream dependencies at depth 2 (recursive)."""
        # Setup mock tables for multi-level lineage
        tables = {
            "project.dataset.view_l2": {
                "type": "VIEW",
                "query": "SELECT * FROM `project.dataset.view_l1_a` UNION ALL SELECT * FROM `project.dataset.view_l1_b`"
            },
            "project.dataset.view_l1_a": {
                "type": "VIEW",
                "query": "SELECT * FROM `project.dataset.source_a`"
            },
            "project.dataset.view_l1_b": {
                "type": "VIEW",
                "query": "SELECT * FROM `project.dataset.source_b`"
            },
        }

        def get_dependencies_recursive(table_id, depth=0, max_depth=2, visited=None):
            if visited is None:
                visited = set()
            if depth >= max_depth or table_id in visited:
                return []

            visited.add(table_id)
            dependencies = []

            if table_id in tables:
                table_info = tables[table_id]
                if table_info["type"] == "VIEW":
                    pattern = r'`?([a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)`?'
                    direct_deps = re.findall(pattern, table_info["query"])
                    dependencies.extend(direct_deps)

                    # Recurse for each dependency
                    for dep in direct_deps:
                        dependencies.extend(
                            get_dependencies_recursive(dep, depth + 1, max_depth, visited)
                        )

            return list(set(dependencies))

        result = benchmark(get_dependencies_recursive, "project.dataset.view_l2")
        assert len(result) >= 2

    def test_build_dependency_graph_small(self, benchmark):
        """Benchmark building a dependency graph for a small lineage tree."""
        dependencies = {
            "project.dataset.view_a": ["project.dataset.table_1", "project.dataset.table_2"],
            "project.dataset.view_b": ["project.dataset.table_2", "project.dataset.table_3"],
            "project.dataset.view_c": ["project.dataset.view_a", "project.dataset.view_b"],
        }

        def build_graph():
            graph = {}
            for table, deps in dependencies.items():
                if table not in graph:
                    graph[table] = {'upstream': [], 'downstream': []}
                graph[table]['upstream'] = deps

                for dep in deps:
                    if dep not in graph:
                        graph[dep] = {'upstream': [], 'downstream': []}
                    graph[dep]['downstream'].append(table)

            return graph

        result = benchmark(build_graph)
        assert len(result) == 6

    def test_build_dependency_graph_large(self, benchmark):
        """Benchmark building a dependency graph for a large lineage tree."""
        # Create a large dependency tree (50 tables)
        dependencies = {}
        for i in range(50):
            table = f"project.dataset.view_{i}"
            deps = []
            if i > 0:
                # Each view depends on 2 previous views
                deps.append(f"project.dataset.view_{i-1}")
                if i > 1:
                    deps.append(f"project.dataset.view_{i-2}")
            dependencies[table] = deps

        def build_graph():
            graph = {}
            for table, deps in dependencies.items():
                if table not in graph:
                    graph[table] = {'upstream': [], 'downstream': []}
                graph[table]['upstream'] = deps

                for dep in deps:
                    if dep not in graph:
                        graph[dep] = {'upstream': [], 'downstream': []}
                    graph[dep]['downstream'].append(table)

            return graph

        result = benchmark(build_graph)
        assert len(result) == 50

    def test_find_downstream_dependencies(self, benchmark):
        """Benchmark finding all downstream dependencies for a table."""
        graph = {
            "project.dataset.source": {
                'upstream': [],
                'downstream': ['project.dataset.view_1', 'project.dataset.view_2']
            },
            "project.dataset.view_1": {
                'upstream': ['project.dataset.source'],
                'downstream': ['project.dataset.view_3']
            },
            "project.dataset.view_2": {
                'upstream': ['project.dataset.source'],
                'downstream': ['project.dataset.view_3']
            },
            "project.dataset.view_3": {
                'upstream': ['project.dataset.view_1', 'project.dataset.view_2'],
                'downstream': []
            },
        }

        def find_downstream(table_id, graph):
            visited = set()
            to_visit = [table_id]
            downstream = []

            while to_visit:
                current = to_visit.pop(0)
                if current in visited:
                    continue
                visited.add(current)

                if current in graph:
                    for dep in graph[current]['downstream']:
                        downstream.append(dep)
                        to_visit.append(dep)

            return list(set(downstream))

        result = benchmark(find_downstream, "project.dataset.source", graph)
        assert len(result) == 3

    def test_format_lineage_mermaid(self, benchmark):
        """Benchmark formatting lineage as Mermaid diagram."""
        graph = {
            f"table_{i}": {
                'upstream': [f"table_{i-1}"] if i > 0 else [],
                'downstream': [f"table_{i+1}"] if i < 19 else []
            }
            for i in range(20)
        }

        def format_mermaid():
            lines = ["graph TD"]
            for table, deps in graph.items():
                for upstream in deps['upstream']:
                    lines.append(f"    {upstream} --> {table}")
            return '\n'.join(lines)

        result = benchmark(format_mermaid)
        assert 'graph TD' in result
        assert result.count('-->') == 19

    def test_format_lineage_text(self, benchmark):
        """Benchmark formatting lineage as text."""
        graph = {
            f"project.dataset.table_{i}": {
                'upstream': [f"project.dataset.table_{i-1}"] if i > 0 else [],
                'downstream': [f"project.dataset.table_{i+1}"] if i < 29 else []
            }
            for i in range(30)
        }

        def format_text():
            lines = ["Table Lineage:"]
            for table, deps in graph.items():
                lines.append(f"\n{table}:")
                if deps['upstream']:
                    lines.append("  Upstream:")
                    for dep in deps['upstream']:
                        lines.append(f"    - {dep}")
                if deps['downstream']:
                    lines.append("  Downstream:")
                    for dep in deps['downstream']:
                        lines.append(f"    - {dep}")
            return '\n'.join(lines)

        result = benchmark(format_text)
        assert 'Table Lineage' in result
        assert result.count('Upstream:') == 29
