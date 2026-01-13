"""
Performance benchmarks for kb search functionality.

This module benchmarks the knowledge base search operations with different
database sizes and query complexities.

Run with:
    pytest tests/benchmarks/test_kb_search_benchmark.py --benchmark-only
    pytest tests/benchmarks/test_kb_search_benchmark.py --benchmark-autosave
"""

import pytest
import sys
from pathlib import Path
import sqlite3
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kb.storage import KnowledgeBase


@pytest.mark.benchmark
@pytest.mark.kb_search
class TestKBSearchBenchmarks:
    """Benchmarks for knowledge base search functionality."""

    @pytest.fixture
    def kb_small(self, tmp_path):
        """Create a small knowledge base with 10 articles."""
        db_path = tmp_path / "kb_small.db"
        kb = KnowledgeBase(str(db_path))

        # Add 10 articles
        for i in range(10):
            kb.add_article(
                title=f"Article {i}",
                content=f"This is test content for article {i}. It contains useful information about topic {i}.",
                article_type="knowledge",
                tags=[f"tag{i}", "common_tag"],
            )

        return kb

    @pytest.fixture
    def kb_medium(self, tmp_path):
        """Create a medium knowledge base with 100 articles."""
        db_path = tmp_path / "kb_medium.db"
        kb = KnowledgeBase(str(db_path))

        # Add 100 articles
        for i in range(100):
            kb.add_article(
                title=f"Technical Article {i}",
                content=f"""
                This is article {i} about software engineering best practices.
                It covers topics like testing, deployment, monitoring, and debugging.
                The article includes code examples and real-world scenarios.
                Tags: python, testing, deployment, monitoring
                """,
                article_type="knowledge",
                tags=[f"tag{i % 10}", "engineering", "best-practices"],
            )

        return kb

    @pytest.fixture
    def kb_large(self, tmp_path):
        """Create a large knowledge base with 1000 articles."""
        db_path = tmp_path / "kb_large.db"
        kb = KnowledgeBase(str(db_path))

        # Add 1000 articles with varying content
        article_types = ["knowledge", "issue", "solution", "decision"]
        for i in range(1000):
            kb.add_article(
                title=f"Article {i}: {article_types[i % 4].title()} Base",
                content=f"""
                Detailed content for article {i}.
                This article discusses important concepts related to data engineering,
                including BigQuery optimization, dbt best practices, and testing strategies.
                It contains examples, code snippets, and troubleshooting guides.
                Keywords: bigquery, dbt, sqlmesh, testing, optimization, performance
                Related topics: article {i-1}, article {i+1}
                """,
                article_type=article_types[i % 4],
                tags=[f"category{i % 20}", "data-engineering", "documentation"],
            )

        return kb

    def test_search_single_term_small_kb(self, benchmark, kb_small):
        """Benchmark searching for a single term in small KB."""
        result = benchmark(kb_small.search, "content", limit=50)
        assert len(result) > 0

    def test_search_single_term_medium_kb(self, benchmark, kb_medium):
        """Benchmark searching for a single term in medium KB."""
        result = benchmark(kb_medium.search, "testing", limit=50)
        assert len(result) > 0

    def test_search_single_term_large_kb(self, benchmark, kb_large):
        """Benchmark searching for a single term in large KB."""
        result = benchmark(kb_large.search, "bigquery", limit=50)
        assert len(result) > 0

    def test_search_multiple_terms_medium_kb(self, benchmark, kb_medium):
        """Benchmark searching for multiple terms in medium KB."""
        result = benchmark(kb_medium.search, "testing deployment monitoring", limit=50)
        assert len(result) > 0

    def test_search_multiple_terms_large_kb(self, benchmark, kb_large):
        """Benchmark searching for multiple terms in large KB."""
        result = benchmark(kb_large.search, "bigquery optimization performance", limit=50)
        assert len(result) > 0

    def test_search_with_type_filter_medium_kb(self, benchmark, kb_medium):
        """Benchmark searching with article type filter in medium KB."""
        result = benchmark(kb_medium.search, "engineering", article_type="knowledge", limit=50)
        assert len(result) > 0

    def test_search_with_type_filter_large_kb(self, benchmark, kb_large):
        """Benchmark searching with article type filter in large KB."""
        result = benchmark(kb_large.search, "optimization", article_type="solution", limit=50)
        assert len(result) > 0

    def test_search_with_tag_filter_medium_kb(self, benchmark, kb_medium):
        """Benchmark searching with tag filter in medium KB."""
        result = benchmark(kb_medium.search, "best", tags=["engineering"], limit=50)
        assert len(result) > 0

    def test_search_with_tag_filter_large_kb(self, benchmark, kb_large):
        """Benchmark searching with tag filter in large KB."""
        result = benchmark(kb_large.search, "dbt", tags=["data-engineering"], limit=50)
        assert len(result) > 0

    def test_search_with_multiple_filters_large_kb(self, benchmark, kb_large):
        """Benchmark searching with multiple filters in large KB."""
        result = benchmark(
            kb_large.search,
            "bigquery",
            article_type="knowledge",
            tags=["data-engineering"],
            limit=50
        )
        assert len(result) >= 0

    def test_list_articles_small_kb(self, benchmark, kb_small):
        """Benchmark listing all articles in small KB."""
        result, total = benchmark(kb_small.list_articles, limit=50)
        assert total == 10

    def test_list_articles_medium_kb(self, benchmark, kb_medium):
        """Benchmark listing all articles in medium KB."""
        result, total = benchmark(kb_medium.list_articles, limit=50)
        assert total == 100

    def test_list_articles_large_kb(self, benchmark, kb_large):
        """Benchmark listing all articles in large KB."""
        result, total = benchmark(kb_large.list_articles, limit=50)
        assert total == 1000

    def test_list_articles_with_pagination_large_kb(self, benchmark, kb_large):
        """Benchmark paginated article listing in large KB."""
        result, total = benchmark(kb_large.list_articles, limit=25, offset=100)
        assert len(result) == 25

    def test_get_article_by_id_small_kb(self, benchmark, kb_small):
        """Benchmark retrieving article by ID in small KB."""
        result = benchmark(kb_small.get_article, 1)
        assert result is not None

    def test_get_article_by_id_large_kb(self, benchmark, kb_large):
        """Benchmark retrieving article by ID in large KB."""
        result = benchmark(kb_large.get_article, 500)
        assert result is not None

    def test_add_article_to_medium_kb(self, benchmark, kb_medium):
        """Benchmark adding a new article to medium KB."""
        def add_article():
            return kb_medium.add_article(
                title="New Article",
                content="New content about testing and deployment",
                article_type="knowledge",
                tags=["new", "testing"]
            )

        result = benchmark(add_article)
        assert result > 100

    def test_add_article_to_large_kb(self, benchmark, kb_large):
        """Benchmark adding a new article to large KB."""
        def add_article():
            return kb_large.add_article(
                title="Performance Optimization Guide",
                content="Comprehensive guide on optimizing BigQuery queries and dbt models",
                article_type="knowledge",
                tags=["performance", "bigquery", "dbt"]
            )

        result = benchmark(add_article)
        assert result > 1000

    def test_update_article_medium_kb(self, benchmark, kb_medium):
        """Benchmark updating an article in medium KB."""
        def update_article():
            return kb_medium.update_article(
                article_id=50,
                title="Updated Title",
                content="Updated content with new information"
            )

        result = benchmark(update_article)
        assert result is True

    def test_update_article_large_kb(self, benchmark, kb_large):
        """Benchmark updating an article in large KB."""
        def update_article():
            return kb_large.update_article(
                article_id=500,
                title="Updated Performance Guide",
                content="Comprehensive updates on query optimization techniques"
            )

        result = benchmark(update_article)
        assert result is True

    def test_delete_article_medium_kb(self, benchmark, kb_medium):
        """Benchmark deleting an article from medium KB."""
        # Add an article to delete
        article_id = kb_medium.add_article(
            title="Temporary Article",
            content="This will be deleted",
            article_type="knowledge"
        )

        result = benchmark(kb_medium.delete_article, article_id)
        assert result is True

    def test_get_all_tags_medium_kb(self, benchmark, kb_medium):
        """Benchmark retrieving all tags from medium KB."""
        result = benchmark(kb_medium.get_all_tags)
        assert len(result) > 0

    def test_get_all_tags_large_kb(self, benchmark, kb_large):
        """Benchmark retrieving all tags from large KB."""
        result = benchmark(kb_large.get_all_tags)
        assert len(result) > 0

    def test_get_stats_small_kb(self, benchmark, kb_small):
        """Benchmark getting KB statistics for small KB."""
        result = benchmark(kb_small.get_stats)
        assert result['total_articles'] == 10

    def test_get_stats_medium_kb(self, benchmark, kb_medium):
        """Benchmark getting KB statistics for medium KB."""
        result = benchmark(kb_medium.get_stats)
        assert result['total_articles'] == 100

    def test_get_stats_large_kb(self, benchmark, kb_large):
        """Benchmark getting KB statistics for large KB."""
        result = benchmark(kb_large.get_stats)
        assert result['total_articles'] == 1000

    def test_complex_search_pattern_large_kb(self, benchmark, kb_large):
        """Benchmark complex search with wildcard patterns in large KB."""
        result = benchmark(kb_large.search, "bigquery OR dbt OR sqlmesh", limit=50)
        assert len(result) > 0

    def test_search_sorting_by_relevance_large_kb(self, benchmark, kb_large):
        """Benchmark search with relevance sorting in large KB."""
        results = benchmark(kb_large.search, "optimization performance", limit=100)

        # Verify results are sorted by relevance (rank)
        if len(results) > 1:
            # FTS5 rank is negative, lower is better
            assert all(
                results[i].get('relevance', 0) <= results[i+1].get('relevance', 0)
                for i in range(len(results)-1)
            )

    def test_batch_article_retrieval_large_kb(self, benchmark, kb_large):
        """Benchmark retrieving multiple articles by ID in large KB."""
        article_ids = list(range(1, 51))  # First 50 articles

        def batch_retrieve():
            articles = []
            for article_id in article_ids:
                article = kb_large.get_article(article_id)
                if article:
                    articles.append(article)
            return articles

        result = benchmark(batch_retrieve)
        assert len(result) == 50

    def test_search_with_no_results_large_kb(self, benchmark, kb_large):
        """Benchmark search with query that returns no results in large KB."""
        result = benchmark(kb_large.search, "nonexistent_term_xyz123", limit=50)
        assert len(result) == 0
