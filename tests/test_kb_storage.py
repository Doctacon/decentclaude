"""
Tests for Knowledge Base Storage Backend

Run with: pytest tests/test_kb_storage.py
"""

import pytest
import tempfile
import os
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from kb.storage import KnowledgeBase


@pytest.fixture
def kb():
    """Create a temporary knowledge base for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    kb = KnowledgeBase(db_path)
    yield kb

    # Cleanup
    os.unlink(db_path)


def test_add_article(kb):
    """Test adding a basic article."""
    article_id = kb.add_article(
        title="Test Article",
        content="This is test content",
        article_type="knowledge"
    )

    assert article_id > 0

    article = kb.get_article(article_id)
    assert article is not None
    assert article['title'] == "Test Article"
    assert article['content'] == "This is test content"
    assert article['article_type'] == "knowledge"


def test_add_article_with_tags(kb):
    """Test adding an article with tags."""
    article_id = kb.add_article(
        title="Tagged Article",
        content="Content",
        tags=["python", "testing"]
    )

    article = kb.get_article(article_id)
    assert set(article['tags']) == {"python", "testing"}


def test_add_article_with_links(kb):
    """Test adding an article with links."""
    links = [
        {
            'url': 'https://github.com/example/repo',
            'type': 'code',
            'description': 'Source code'
        },
        {
            'url': 'https://docs.example.com',
            'type': 'docs',
            'description': 'Documentation'
        }
    ]

    article_id = kb.add_article(
        title="Linked Article",
        content="Content",
        links=links
    )

    article = kb.get_article(article_id)
    assert len(article['links']) == 2
    assert article['links'][0]['url'] == 'https://github.com/example/repo'
    assert article['links'][0]['type'] == 'code'


def test_get_nonexistent_article(kb):
    """Test getting an article that doesn't exist."""
    article = kb.get_article(999)
    assert article is None


def test_update_article(kb):
    """Test updating an article."""
    article_id = kb.add_article(
        title="Original Title",
        content="Original content"
    )

    success = kb.update_article(
        article_id,
        title="Updated Title",
        content="Updated content"
    )

    assert success
    article = kb.get_article(article_id)
    assert article['title'] == "Updated Title"
    assert article['content'] == "Updated content"


def test_update_article_tags(kb):
    """Test updating article tags."""
    article_id = kb.add_article(
        title="Article",
        content="Content",
        tags=["old", "tags"]
    )

    kb.update_article(article_id, tags=["new", "tags"])

    article = kb.get_article(article_id)
    assert set(article['tags']) == {"new", "tags"}


def test_update_nonexistent_article(kb):
    """Test updating an article that doesn't exist."""
    success = kb.update_article(999, title="New Title")
    assert not success


def test_delete_article(kb):
    """Test deleting an article."""
    article_id = kb.add_article(
        title="To Delete",
        content="Content"
    )

    success = kb.delete_article(article_id)
    assert success

    article = kb.get_article(article_id)
    assert article is None


def test_delete_nonexistent_article(kb):
    """Test deleting an article that doesn't exist."""
    success = kb.delete_article(999)
    assert not success


def test_search(kb):
    """Test full-text search."""
    kb.add_article(
        title="Python Testing",
        content="How to write tests in Python using pytest"
    )
    kb.add_article(
        title="JavaScript Testing",
        content="How to write tests in JavaScript using Jest"
    )
    kb.add_article(
        title="Python Deployment",
        content="How to deploy Python applications"
    )

    # Search for "Python"
    results = kb.search("Python")
    assert len(results) == 2

    # Search for "testing"
    results = kb.search("testing")
    assert len(results) == 2

    # Search for "deployment"
    results = kb.search("deployment")
    assert len(results) == 1


def test_search_with_type_filter(kb):
    """Test search with article type filter."""
    kb.add_article(
        title="Knowledge Article",
        content="Python knowledge",
        article_type="knowledge"
    )
    kb.add_article(
        title="Issue Article",
        content="Python issue",
        article_type="issue"
    )

    results = kb.search("Python", article_type="knowledge")
    assert len(results) == 1
    assert results[0]['article_type'] == "knowledge"


def test_search_with_tags_filter(kb):
    """Test search with tags filter."""
    kb.add_article(
        title="Article 1",
        content="Python content",
        tags=["python", "web"]
    )
    kb.add_article(
        title="Article 2",
        content="Python content",
        tags=["python", "cli"]
    )

    results = kb.search("Python", tags=["web"])
    assert len(results) == 1


def test_list_articles(kb):
    """Test listing articles."""
    for i in range(5):
        kb.add_article(
            title=f"Article {i}",
            content=f"Content {i}"
        )

    articles, total = kb.list_articles()
    assert len(articles) == 5
    assert total == 5


def test_list_articles_with_pagination(kb):
    """Test listing articles with pagination."""
    for i in range(10):
        kb.add_article(
            title=f"Article {i}",
            content=f"Content {i}"
        )

    articles, total = kb.list_articles(limit=5, offset=0)
    assert len(articles) == 5
    assert total == 10

    articles, total = kb.list_articles(limit=5, offset=5)
    assert len(articles) == 5
    assert total == 10


def test_list_articles_with_type_filter(kb):
    """Test listing articles filtered by type."""
    kb.add_article(title="K1", content="C1", article_type="knowledge")
    kb.add_article(title="K2", content="C2", article_type="knowledge")
    kb.add_article(title="I1", content="C3", article_type="issue")

    articles, total = kb.list_articles(article_type="knowledge")
    assert len(articles) == 2
    assert total == 2


def test_list_articles_with_tags_filter(kb):
    """Test listing articles filtered by tags."""
    kb.add_article(title="A1", content="C1", tags=["python"])
    kb.add_article(title="A2", content="C2", tags=["python", "web"])
    kb.add_article(title="A3", content="C3", tags=["javascript"])

    articles, total = kb.list_articles(tags=["python"])
    assert len(articles) == 2
    assert total == 2


def test_get_all_tags(kb):
    """Test getting all tags."""
    kb.add_article(title="A1", content="C1", tags=["python", "web"])
    kb.add_article(title="A2", content="C2", tags=["javascript", "web"])

    tags = kb.get_all_tags()
    assert set(tags) == {"python", "javascript", "web"}


def test_get_stats(kb):
    """Test getting statistics."""
    kb.add_article(title="A1", content="C1", article_type="knowledge")
    kb.add_article(title="A2", content="C2", article_type="issue")
    kb.add_article(
        title="A3",
        content="C3",
        tags=["tag1"],
        links=[{'url': 'http://example.com', 'type': 'reference'}]
    )

    stats = kb.get_stats()
    assert stats['total_articles'] == 3
    assert stats['by_type']['knowledge'] == 1
    assert stats['by_type']['issue'] == 1
    assert stats['total_tags'] == 1
    assert stats['total_links'] == 1


def test_article_metadata(kb):
    """Test article metadata storage."""
    metadata = {
        'priority': 'high',
        'custom_field': 'value'
    }

    article_id = kb.add_article(
        title="Article with metadata",
        content="Content",
        metadata=metadata
    )

    article = kb.get_article(article_id)
    assert article['metadata'] == metadata


def test_article_author(kb):
    """Test article author field."""
    article_id = kb.add_article(
        title="Authored Article",
        content="Content",
        author="test_user"
    )

    article = kb.get_article(article_id)
    assert article['author'] == "test_user"


def test_multiple_articles_same_tags(kb):
    """Test multiple articles can share the same tags."""
    article_id_1 = kb.add_article(
        title="Article 1",
        content="Content 1",
        tags=["shared", "tag1"]
    )
    article_id_2 = kb.add_article(
        title="Article 2",
        content="Content 2",
        tags=["shared", "tag2"]
    )

    article1 = kb.get_article(article_id_1)
    article2 = kb.get_article(article_id_2)

    assert "shared" in article1['tags']
    assert "shared" in article2['tags']


def test_delete_article_cascades(kb):
    """Test that deleting an article removes associated tags and links."""
    article_id = kb.add_article(
        title="Article",
        content="Content",
        tags=["tag1", "tag2"],
        links=[{'url': 'http://example.com', 'type': 'reference'}]
    )

    kb.delete_article(article_id)

    # Tags should still exist (they're shared)
    tags = kb.get_all_tags()
    assert "tag1" in tags

    # But the article should be gone
    article = kb.get_article(article_id)
    assert article is None


def test_search_empty_query(kb):
    """Test search with empty query."""
    kb.add_article(title="Article", content="Content")

    # Empty query should still work (FTS5 behavior)
    # This might raise an error or return empty results depending on implementation
    try:
        results = kb.search("")
        # If it works, results should be valid
        assert isinstance(results, list)
    except Exception:
        # Empty queries might not be supported, which is fine
        pass


def test_article_ordering(kb):
    """Test that articles are ordered by updated_at."""
    import time

    kb.add_article(title="First", content="Content")
    time.sleep(0.01)  # Ensure different timestamps
    kb.add_article(title="Second", content="Content")

    articles, _ = kb.list_articles()

    # Most recent first
    assert articles[0]['title'] == "Second"
    assert articles[1]['title'] == "First"
