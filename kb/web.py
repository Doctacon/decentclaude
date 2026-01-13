"""
Knowledge Base Web Interface

FastAPI-based REST API and web UI for the knowledge base.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import uvicorn

from kb.storage import KnowledgeBase


# Pydantic models
class ArticleCreate(BaseModel):
    """Model for creating an article."""
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    article_type: str = Field(default='knowledge', pattern='^(knowledge|issue|solution|decision)$')
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    links: Optional[List[Dict[str, str]]] = None


class ArticleUpdate(BaseModel):
    """Model for updating an article."""
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    links: Optional[List[Dict[str, str]]] = None


class SearchQuery(BaseModel):
    """Model for search query."""
    query: str
    article_type: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = Field(default=50, le=100)


# Initialize FastAPI app
app = FastAPI(
    title="Knowledge Base API",
    description="Team knowledge base for tribal knowledge, issues, and solutions",
    version="1.0.0"
)

# Initialize knowledge base
kb = KnowledgeBase()


# API Routes
@app.get("/api/articles", response_model=Dict)
async def list_articles(
    article_type: Optional[str] = Query(None, regex='^(knowledge|issue|solution|decision)$'),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
):
    """List articles with optional filters."""
    tag_list = tags.split(',') if tags else None
    articles, total = kb.list_articles(
        article_type=article_type,
        tags=tag_list,
        limit=limit,
        offset=offset
    )
    return {
        'articles': articles,
        'total': total,
        'limit': limit,
        'offset': offset
    }


@app.get("/api/articles/{article_id}")
async def get_article(article_id: int):
    """Get an article by ID."""
    article = kb.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.post("/api/articles", response_model=Dict, status_code=201)
async def create_article(article: ArticleCreate):
    """Create a new article."""
    article_id = kb.add_article(
        title=article.title,
        content=article.content,
        article_type=article.article_type,
        author=article.author,
        tags=article.tags,
        links=article.links
    )
    return {'id': article_id, 'status': 'created'}


@app.put("/api/articles/{article_id}")
async def update_article(article_id: int, article: ArticleUpdate):
    """Update an article."""
    success = kb.update_article(
        article_id=article_id,
        title=article.title,
        content=article.content,
        tags=article.tags,
        links=article.links
    )
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return {'id': article_id, 'status': 'updated'}


@app.delete("/api/articles/{article_id}")
async def delete_article(article_id: int):
    """Delete an article."""
    success = kb.delete_article(article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return {'id': article_id, 'status': 'deleted'}


@app.post("/api/search")
async def search_articles(search: SearchQuery):
    """Search articles using full-text search."""
    results = kb.search(
        query=search.query,
        article_type=search.article_type,
        tags=search.tags,
        limit=search.limit
    )
    return {
        'results': results,
        'count': len(results)
    }


@app.get("/api/tags")
async def get_tags():
    """Get all tags."""
    tags = kb.get_all_tags()
    return {'tags': tags}


@app.get("/api/stats")
async def get_stats():
    """Get knowledge base statistics."""
    stats = kb.get_stats()
    return stats


# HTML UI
@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main HTML interface."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Knowledge Base</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            background: #2c3e50;
            color: white;
            padding: 20px 0;
            margin-bottom: 30px;
        }

        h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }

        .search-box {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }

        .search-input {
            width: 100%;
            padding: 12px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 4px;
            margin-bottom: 10px;
        }

        .search-input:focus {
            outline: none;
            border-color: #3498db;
        }

        .filters {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-top: 10px;
        }

        .filter-select {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background: white;
        }

        .btn {
            padding: 10px 20px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }

        .btn:hover {
            background: #2980b9;
        }

        .btn-success {
            background: #27ae60;
        }

        .btn-success:hover {
            background: #229954;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }

        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }

        .stat-label {
            color: #7f8c8d;
            font-size: 0.9em;
        }

        .articles {
            display: grid;
            gap: 20px;
        }

        .article-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: box-shadow 0.2s;
        }

        .article-card:hover {
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }

        .article-header {
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 10px;
        }

        .article-title {
            font-size: 1.3em;
            font-weight: bold;
            color: #2c3e50;
        }

        .article-id {
            color: #7f8c8d;
            font-size: 0.9em;
        }

        .article-meta {
            display: flex;
            gap: 15px;
            margin-bottom: 10px;
            color: #7f8c8d;
            font-size: 0.9em;
        }

        .article-type {
            display: inline-block;
            padding: 3px 8px;
            background: #ecf0f1;
            border-radius: 3px;
            font-size: 0.85em;
        }

        .article-type.knowledge { background: #e8f4f8; color: #2980b9; }
        .article-type.issue { background: #fadbd8; color: #c0392b; }
        .article-type.solution { background: #d5f4e6; color: #27ae60; }
        .article-type.decision { background: #fef5e7; color: #f39c12; }

        .article-content {
            margin: 15px 0;
            color: #555;
        }

        .article-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 10px;
        }

        .tag {
            display: inline-block;
            padding: 3px 10px;
            background: #f39c12;
            color: white;
            border-radius: 12px;
            font-size: 0.85em;
        }

        .article-links {
            margin-top: 10px;
        }

        .article-link {
            display: block;
            color: #3498db;
            text-decoration: none;
            padding: 5px 0;
        }

        .article-link:hover {
            text-decoration: underline;
        }

        .loading {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }

        .error {
            background: #fadbd8;
            color: #c0392b;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
        }

        .modal.active {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 8px;
            max-width: 600px;
            width: 90%;
            max-height: 90vh;
            overflow-y: auto;
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .modal-close {
            font-size: 1.5em;
            cursor: pointer;
            color: #7f8c8d;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-label {
            display: block;
            margin-bottom: 5px;
            font-weight: 500;
        }

        .form-input,
        .form-textarea,
        .form-select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: inherit;
        }

        .form-textarea {
            min-height: 200px;
            resize: vertical;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>📚 Knowledge Base</h1>
            <p>Team knowledge, issues, solutions, and decisions</p>
        </div>
    </header>

    <div class="container">
        <div class="search-box">
            <input
                type="text"
                id="searchInput"
                class="search-input"
                placeholder="Search knowledge base..."
            >
            <div class="filters">
                <select id="typeFilter" class="filter-select">
                    <option value="">All Types</option>
                    <option value="knowledge">Knowledge</option>
                    <option value="issue">Issue</option>
                    <option value="solution">Solution</option>
                    <option value="decision">Decision</option>
                </select>
                <button class="btn" onclick="searchArticles()">Search</button>
                <button class="btn" onclick="loadArticles()">Show All</button>
                <button class="btn btn-success" onclick="showAddModal()">+ New Article</button>
            </div>
        </div>

        <div id="stats" class="stats"></div>
        <div id="error" class="error" style="display: none;"></div>
        <div id="articles" class="articles"></div>
    </div>

    <!-- Add/Edit Modal -->
    <div id="modal" class="modal">
        <div class="modal-content">
            <div class="modal-header">
                <h2 id="modalTitle">New Article</h2>
                <span class="modal-close" onclick="closeModal()">&times;</span>
            </div>
            <form id="articleForm" onsubmit="saveArticle(event)">
                <div class="form-group">
                    <label class="form-label">Title</label>
                    <input type="text" id="formTitle" class="form-input" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Type</label>
                    <select id="formType" class="form-select">
                        <option value="knowledge">Knowledge</option>
                        <option value="issue">Issue</option>
                        <option value="solution">Solution</option>
                        <option value="decision">Decision</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Content (Markdown supported)</label>
                    <textarea id="formContent" class="form-textarea" required></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">Tags (comma-separated)</label>
                    <input type="text" id="formTags" class="form-input" placeholder="e.g., python, api, deployment">
                </div>
                <div class="form-group">
                    <label class="form-label">Author</label>
                    <input type="text" id="formAuthor" class="form-input">
                </div>
                <button type="submit" class="btn btn-success">Save</button>
            </form>
        </div>
    </div>

    <script>
        let currentArticleId = null;

        // Load stats on page load
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();

                const statsHtml = `
                    <div class="stat-card">
                        <div class="stat-value">${stats.total_articles}</div>
                        <div class="stat-label">Total Articles</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.total_tags}</div>
                        <div class="stat-label">Tags</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.total_links}</div>
                        <div class="stat-label">Links</div>
                    </div>
                `;

                document.getElementById('stats').innerHTML = statsHtml;
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        // Load articles
        async function loadArticles(type = null) {
            const articlesDiv = document.getElementById('articles');
            articlesDiv.innerHTML = '<div class="loading">Loading...</div>';

            try {
                let url = '/api/articles?limit=50';
                if (type) url += `&article_type=${type}`;

                const response = await fetch(url);
                const data = await response.json();

                if (data.articles.length === 0) {
                    articlesDiv.innerHTML = '<div class="loading">No articles found</div>';
                    return;
                }

                renderArticles(data.articles);
            } catch (error) {
                showError('Error loading articles: ' + error.message);
            }
        }

        // Search articles
        async function searchArticles() {
            const query = document.getElementById('searchInput').value;
            const type = document.getElementById('typeFilter').value;

            if (!query.trim()) {
                loadArticles(type || null);
                return;
            }

            const articlesDiv = document.getElementById('articles');
            articlesDiv.innerHTML = '<div class="loading">Searching...</div>';

            try {
                const response = await fetch('/api/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        query: query,
                        article_type: type || null,
                        limit: 50
                    })
                });

                const data = await response.json();

                if (data.results.length === 0) {
                    articlesDiv.innerHTML = '<div class="loading">No results found</div>';
                    return;
                }

                renderArticles(data.results);
            } catch (error) {
                showError('Error searching: ' + error.message);
            }
        }

        // Render articles
        function renderArticles(articles) {
            const articlesDiv = document.getElementById('articles');

            const html = articles.map(article => {
                const tagsHtml = (article.tags || []).map(tag =>
                    `<span class="tag">${tag}</span>`
                ).join('');

                const linksHtml = (article.links || []).map(link =>
                    `<a href="${link.url}" class="article-link" target="_blank">
                        🔗 ${link.url} ${link.description ? '- ' + link.description : ''}
                    </a>`
                ).join('');

                const preview = article.content.substring(0, 300) +
                    (article.content.length > 300 ? '...' : '');

                return `
                    <div class="article-card">
                        <div class="article-header">
                            <div class="article-title">${article.title}</div>
                            <div class="article-id">#${article.id}</div>
                        </div>
                        <div class="article-meta">
                            <span class="article-type ${article.article_type}">${article.article_type}</span>
                            <span>Updated: ${article.updated_at.substring(0, 10)}</span>
                            ${article.author ? `<span>By: ${article.author}</span>` : ''}
                        </div>
                        <div class="article-content">${preview}</div>
                        ${tagsHtml ? `<div class="article-tags">${tagsHtml}</div>` : ''}
                        ${linksHtml ? `<div class="article-links">${linksHtml}</div>` : ''}
                    </div>
                `;
            }).join('');

            articlesDiv.innerHTML = html;
        }

        // Show add modal
        function showAddModal() {
            currentArticleId = null;
            document.getElementById('modalTitle').textContent = 'New Article';
            document.getElementById('articleForm').reset();
            document.getElementById('modal').classList.add('active');
        }

        // Close modal
        function closeModal() {
            document.getElementById('modal').classList.remove('active');
        }

        // Save article
        async function saveArticle(event) {
            event.preventDefault();

            const title = document.getElementById('formTitle').value;
            const content = document.getElementById('formContent').value;
            const article_type = document.getElementById('formType').value;
            const author = document.getElementById('formAuthor').value;
            const tagsStr = document.getElementById('formTags').value;

            const tags = tagsStr ? tagsStr.split(',').map(t => t.trim()) : null;

            try {
                const response = await fetch('/api/articles', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        title,
                        content,
                        article_type,
                        author: author || null,
                        tags
                    })
                });

                if (response.ok) {
                    closeModal();
                    loadArticles();
                    loadStats();
                } else {
                    showError('Error saving article');
                }
            } catch (error) {
                showError('Error saving article: ' + error.message);
            }
        }

        // Show error
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }

        // Search on Enter key
        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') searchArticles();
        });

        // Load initial data
        loadStats();
        loadArticles();
    </script>
</body>
</html>
    """


def run_server(host: str = "0.0.0.0", port: int = 8000, db_path: Optional[str] = None):
    """Run the web server.

    Args:
        host: Host to bind to (default: 0.0.0.0)
        port: Port to listen on (default: 8000)
        db_path: Path to knowledge base database
    """
    global kb
    if db_path:
        kb = KnowledgeBase(db_path)

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
