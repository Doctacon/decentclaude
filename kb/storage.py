"""
Knowledge Base Storage Backend

SQLite-based storage with full-text search for team knowledge.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager


class KnowledgeBase:
    """Manages knowledge base storage and retrieval."""

    def __init__(self, db_path: Optional[str] = None):
        """Initialize knowledge base.

        Args:
            db_path: Path to SQLite database. Defaults to ~/.kb/knowledge.db
        """
        if db_path is None:
            kb_dir = Path.home() / '.kb'
            kb_dir.mkdir(exist_ok=True)
            db_path = str(kb_dir / 'knowledge.db')

        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_conn(self):
        """Get database connection with context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Initialize database schema."""
        with self._get_conn() as conn:
            conn.executescript("""
                -- Main articles table
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    article_type TEXT NOT NULL DEFAULT 'knowledge',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    author TEXT,
                    metadata TEXT
                );

                -- Tags table
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                );

                -- Article-tag mapping
                CREATE TABLE IF NOT EXISTS article_tags (
                    article_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (article_id, tag_id),
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                );

                -- Links to code/docs
                CREATE TABLE IF NOT EXISTS links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    link_type TEXT NOT NULL,
                    description TEXT,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                );

                -- Full-text search index
                CREATE VIRTUAL TABLE IF NOT EXISTS articles_fts USING fts5(
                    title,
                    content,
                    content='articles',
                    content_rowid='id'
                );

                -- Triggers to keep FTS index in sync
                CREATE TRIGGER IF NOT EXISTS articles_ai AFTER INSERT ON articles BEGIN
                    INSERT INTO articles_fts(rowid, title, content)
                    VALUES (new.id, new.title, new.content);
                END;

                CREATE TRIGGER IF NOT EXISTS articles_ad AFTER DELETE ON articles BEGIN
                    DELETE FROM articles_fts WHERE rowid = old.id;
                END;

                CREATE TRIGGER IF NOT EXISTS articles_au AFTER UPDATE ON articles BEGIN
                    UPDATE articles_fts SET title = new.title, content = new.content
                    WHERE rowid = new.id;
                END;

                -- Indexes
                CREATE INDEX IF NOT EXISTS idx_articles_type ON articles(article_type);
                CREATE INDEX IF NOT EXISTS idx_articles_created ON articles(created_at);
                CREATE INDEX IF NOT EXISTS idx_links_article ON links(article_id);
            """)
            conn.commit()

    def add_article(
        self,
        title: str,
        content: str,
        article_type: str = 'knowledge',
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
        links: Optional[List[Dict[str, str]]] = None,
        metadata: Optional[Dict] = None
    ) -> int:
        """Add a new article to the knowledge base.

        Args:
            title: Article title
            content: Article content (markdown supported)
            article_type: Type of article (knowledge, issue, solution, decision)
            author: Author name
            tags: List of tags
            links: List of links with 'url', 'type', and 'description'
            metadata: Additional metadata as dict

        Returns:
            Article ID
        """
        now = datetime.utcnow().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None

        with self._get_conn() as conn:
            cursor = conn.execute(
                """INSERT INTO articles (title, content, article_type, created_at, updated_at, author, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (title, content, article_type, now, now, author, metadata_json)
            )
            article_id = cursor.lastrowid

            # Add tags
            if tags:
                for tag in tags:
                    cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
                    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
                    tag_id = cursor.fetchone()[0]
                    cursor.execute(
                        "INSERT INTO article_tags (article_id, tag_id) VALUES (?, ?)",
                        (article_id, tag_id)
                    )

            # Add links
            if links:
                for link in links:
                    cursor.execute(
                        "INSERT INTO links (article_id, url, link_type, description) VALUES (?, ?, ?, ?)",
                        (article_id, link['url'], link.get('type', 'reference'), link.get('description'))
                    )

            conn.commit()
            return article_id

    def get_article(self, article_id: int) -> Optional[Dict]:
        """Get article by ID with tags and links.

        Args:
            article_id: Article ID

        Returns:
            Article dict or None if not found
        """
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT * FROM articles WHERE id = ?",
                (article_id,)
            )
            row = cursor.fetchone()

            if not row:
                return None

            article = dict(row)
            article['metadata'] = json.loads(article['metadata']) if article['metadata'] else {}

            # Get tags
            cursor.execute("""
                SELECT t.name FROM tags t
                JOIN article_tags at ON t.id = at.tag_id
                WHERE at.article_id = ?
            """, (article_id,))
            article['tags'] = [row[0] for row in cursor.fetchall()]

            # Get links
            cursor.execute(
                "SELECT url, link_type, description FROM links WHERE article_id = ?",
                (article_id,)
            )
            article['links'] = [
                {'url': row[0], 'type': row[1], 'description': row[2]}
                for row in cursor.fetchall()
            ]

            return article

    def update_article(
        self,
        article_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        links: Optional[List[Dict[str, str]]] = None
    ) -> bool:
        """Update an existing article.

        Args:
            article_id: Article ID
            title: New title (optional)
            content: New content (optional)
            tags: New tags list (replaces existing)
            links: New links list (replaces existing)

        Returns:
            True if updated, False if article not found
        """
        with self._get_conn() as conn:
            # Check if article exists
            cursor = conn.execute("SELECT id FROM articles WHERE id = ?", (article_id,))
            if not cursor.fetchone():
                return False

            now = datetime.utcnow().isoformat()

            # Update article
            if title is not None or content is not None:
                updates = ["updated_at = ?"]
                params = [now]

                if title is not None:
                    updates.append("title = ?")
                    params.append(title)

                if content is not None:
                    updates.append("content = ?")
                    params.append(content)

                params.append(article_id)
                conn.execute(
                    f"UPDATE articles SET {', '.join(updates)} WHERE id = ?",
                    params
                )

            # Update tags
            if tags is not None:
                conn.execute("DELETE FROM article_tags WHERE article_id = ?", (article_id,))
                for tag in tags:
                    conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
                    cursor = conn.execute("SELECT id FROM tags WHERE name = ?", (tag,))
                    tag_id = cursor.fetchone()[0]
                    conn.execute(
                        "INSERT INTO article_tags (article_id, tag_id) VALUES (?, ?)",
                        (article_id, tag_id)
                    )

            # Update links
            if links is not None:
                conn.execute("DELETE FROM links WHERE article_id = ?", (article_id,))
                for link in links:
                    conn.execute(
                        "INSERT INTO links (article_id, url, link_type, description) VALUES (?, ?, ?, ?)",
                        (article_id, link['url'], link.get('type', 'reference'), link.get('description'))
                    )

            conn.commit()
            return True

    def delete_article(self, article_id: int) -> bool:
        """Delete an article.

        Args:
            article_id: Article ID

        Returns:
            True if deleted, False if not found
        """
        with self._get_conn() as conn:
            cursor = conn.execute("DELETE FROM articles WHERE id = ?", (article_id,))
            conn.commit()
            return cursor.rowcount > 0

    def search(
        self,
        query: str,
        article_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Search articles using full-text search.

        Args:
            query: Search query
            article_type: Filter by article type
            tags: Filter by tags
            limit: Maximum results

        Returns:
            List of matching articles with relevance score
        """
        with self._get_conn() as conn:
            sql = """
                SELECT a.*,
                       fts.rank as relevance,
                       GROUP_CONCAT(DISTINCT t.name) as tags
                FROM articles_fts fts
                JOIN articles a ON a.id = fts.rowid
                LEFT JOIN article_tags at ON a.id = at.article_id
                LEFT JOIN tags t ON at.tag_id = t.id
                WHERE articles_fts MATCH ?
            """
            params = [query]

            if article_type:
                sql += " AND a.article_type = ?"
                params.append(article_type)

            sql += " GROUP BY a.id"

            if tags:
                sql += f" HAVING {' AND '.join(['tags LIKE ?' for _ in tags])}"
                params.extend([f'%{tag}%' for tag in tags])

            sql += " ORDER BY fts.rank LIMIT ?"
            params.append(limit)

            cursor = conn.execute(sql, params)

            results = []
            for row in cursor.fetchall():
                article = dict(row)
                article['metadata'] = json.loads(article['metadata']) if article['metadata'] else {}
                article['tags'] = article['tags'].split(',') if article['tags'] else []
                results.append(article)

            return results

    def list_articles(
        self,
        article_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Dict], int]:
        """List articles with optional filters.

        Args:
            article_type: Filter by article type
            tags: Filter by tags
            limit: Maximum results
            offset: Offset for pagination

        Returns:
            Tuple of (articles list, total count)
        """
        with self._get_conn() as conn:
            # Build query
            sql = """
                SELECT DISTINCT a.*,
                       GROUP_CONCAT(DISTINCT t.name) as tags
                FROM articles a
                LEFT JOIN article_tags at ON a.id = at.article_id
                LEFT JOIN tags t ON at.tag_id = t.id
            """
            where_clauses = []
            params = []

            if article_type:
                where_clauses.append("a.article_type = ?")
                params.append(article_type)

            if tags:
                for tag in tags:
                    where_clauses.append("a.id IN (SELECT at2.article_id FROM article_tags at2 JOIN tags t2 ON at2.tag_id = t2.id WHERE t2.name = ?)")
                    params.append(tag)

            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)

            sql += " GROUP BY a.id ORDER BY a.updated_at DESC"

            # Get total count
            count_sql = f"SELECT COUNT(*) FROM ({sql})"
            cursor = conn.execute(count_sql, params)
            total = cursor.fetchone()[0]

            # Get paginated results
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor = conn.execute(sql, params)

            results = []
            for row in cursor.fetchall():
                article = dict(row)
                article['metadata'] = json.loads(article['metadata']) if article['metadata'] else {}
                article['tags'] = article['tags'].split(',') if article['tags'] else []
                results.append(article)

            return results, total

    def get_all_tags(self) -> List[str]:
        """Get all tags in the knowledge base.

        Returns:
            List of tag names
        """
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT name FROM tags ORDER BY name")
            return [row[0] for row in cursor.fetchall()]

    def get_stats(self) -> Dict:
        """Get knowledge base statistics.

        Returns:
            Dict with statistics
        """
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM articles")
            total_articles = cursor.fetchone()[0]

            cursor = conn.execute("SELECT article_type, COUNT(*) FROM articles GROUP BY article_type")
            by_type = {row[0]: row[1] for row in cursor.fetchall()}

            cursor = conn.execute("SELECT COUNT(*) FROM tags")
            total_tags = cursor.fetchone()[0]

            cursor = conn.execute("SELECT COUNT(*) FROM links")
            total_links = cursor.fetchone()[0]

            return {
                'total_articles': total_articles,
                'by_type': by_type,
                'total_tags': total_tags,
                'total_links': total_links
            }
