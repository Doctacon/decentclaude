# Knowledge Base System

A searchable knowledge base for capturing tribal knowledge, documenting common issues, storing solutions and workarounds, and tracking decisions and rationale.

## Features

- **Capture Tribal Knowledge**: Document team expertise and best practices
- **Track Issues**: Record common problems and their context
- **Store Solutions**: Save workarounds and fixes for future reference
- **Document Decisions**: Track architectural decisions and their rationale
- **Link to Code/Docs**: Connect knowledge to relevant code and documentation
- **Full-Text Search**: Search across all content using SQLite FTS5
- **Tagging**: Organize content with tags for easy filtering
- **Multiple Interfaces**: CLI for automation, web UI for browsing

## Architecture

### Storage Backend (`kb/storage.py`)

SQLite database with:
- **Full-text search** using FTS5 virtual tables
- **Articles**: Main content with title, content (markdown), type, and metadata
- **Tags**: Flexible tagging system with many-to-many relationships
- **Links**: External references to code, docs, or other resources
- **Automatic indexing**: Triggers keep search index synchronized

**Article Types:**
- `knowledge`: General tribal knowledge and best practices
- `issue`: Common problems and their context
- `solution`: Solutions and workarounds
- `decision`: Architectural decisions and rationale

### CLI Interface (`bin/kb`)

Command-line tool following project patterns:
- Python 3 with argparse
- ANSI color output
- JSON/text/markdown output formats
- Subcommands for all operations

### Web Interface (`kb/web.py`, `bin/kb-web`)

FastAPI-based REST API and web UI:
- RESTful endpoints for CRUD operations
- Full-text search API
- Single-page HTML interface
- Responsive design
- Statistics dashboard

## Installation

The knowledge base is part of the decentclaude toolkit. No additional installation required if you have the project set up.

### Dependencies

Add to your Python environment:

```bash
pip install fastapi uvicorn
```

(Note: The storage backend has no external dependencies, only the web interface requires FastAPI)

## CLI Usage

### Basic Commands

```bash
# Add a new article
kb add "How to deploy to production" \
  --type knowledge \
  --tags "deployment,production" \
  --content "Step-by-step deployment guide..."

# Add from file
kb add "API Rate Limiting" \
  --type decision \
  --file docs/api-rate-limit.md \
  --tags "api,architecture"

# Search
kb search "deployment production"
kb search "rate limit" --type decision
kb search "api" --tags "architecture,performance"

# List articles
kb list
kb list --type issue --limit 10
kb list --tags "python,data-engineering"

# Get specific article
kb get 42
kb get 42 --format markdown
kb get 42 --format json

# Update article
kb update 42 --title "New Title"
kb update 42 --file updated-content.md
kb update 42 --tags "new,tags"

# Delete article
kb delete 42
kb delete 42 --yes  # Skip confirmation

# Show statistics
kb stats

# List all tags
kb tags
```

### Output Formats

```bash
# Text output (default, colored)
kb search "deployment"

# JSON output (for scripting)
kb search "deployment" --format json | jq '.results[].title'

# Markdown output (for documentation)
kb get 42 --format markdown > article.md
```

### Adding Links

Links connect knowledge to code, documentation, or external resources:

```bash
kb add "Database Migration Process" \
  --links \
    "https://github.com/org/repo/blob/main/migrations/README.md,code,Migration scripts" \
    "https://docs.sqlalchemy.org/,docs,SQLAlchemy docs" \
    "https://wiki.internal/database,wiki,Internal wiki"
```

Link format: `url[,type[,description]]`

### Piping Content

```bash
# From stdin
echo "Quick note about caching" | kb add "Caching Strategy" --type knowledge

# From command output
curl https://api.example.com/docs | kb add "API Documentation" --type knowledge
```

## Web Interface Usage

### Starting the Server

```bash
# Default (http://0.0.0.0:8000)
kb-web

# Custom host and port
kb-web --host localhost --port 3000

# Custom database location
kb-web --db /path/to/custom/knowledge.db
```

### Accessing the UI

1. Start the server: `kb-web`
2. Open browser to: `http://localhost:8000`
3. Use the search box to find content
4. Filter by type or tags
5. Click "+ New Article" to add content

### REST API Endpoints

```bash
# List articles
curl http://localhost:8000/api/articles

# Search
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "deployment", "limit": 10}'

# Get article
curl http://localhost:8000/api/articles/42

# Create article
curl -X POST http://localhost:8000/api/articles \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Article",
    "content": "Content here",
    "article_type": "knowledge",
    "tags": ["tag1", "tag2"]
  }'

# Update article
curl -X PUT http://localhost:8000/api/articles/42 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'

# Delete article
curl -X DELETE http://localhost:8000/api/articles/42

# Get statistics
curl http://localhost:8000/api/stats

# Get all tags
curl http://localhost:8000/api/tags
```

## Database Location

By default, the knowledge base is stored at: `~/.kb/knowledge.db`

You can specify a custom location:

```bash
kb --db /path/to/custom.db list
kb-web --db /path/to/custom.db
```

## Use Cases

### 1. Tribal Knowledge

Capture team expertise that's not in documentation:

```bash
kb add "Why we use UUID primary keys" \
  --type decision \
  --tags "database,architecture" \
  --content "We use UUIDs instead of auto-increment IDs because..." \
  --links "https://github.com/org/repo/pull/123,code,Original PR"
```

### 2. Common Issues

Document recurring problems:

```bash
kb add "Timeout in BigQuery materialized views" \
  --type issue \
  --tags "bigquery,performance" \
  --content "Symptom: Query timeout when refreshing mat views. Root cause: ..."
```

### 3. Solutions Library

Store workarounds and fixes:

```bash
kb add "Fix for materialized view timeout" \
  --type solution \
  --tags "bigquery,performance" \
  --content "Use incremental refresh strategy: ..." \
  --links "https://cloud.google.com/bigquery/docs/materialized-views,docs"
```

### 4. Decision Log

Track architectural decisions:

```bash
kb add "ADR: Switch from REST to GraphQL" \
  --type decision \
  --tags "api,architecture,graphql" \
  --content "# Context\n\n# Decision\n\n# Consequences\n\n# Alternatives Considered"
```

### 5. Onboarding

New team members can search for context:

```bash
# Search for deployment knowledge
kb search "deploy production" --type knowledge

# Find all architecture decisions
kb list --type decision --tags "architecture"

# Get overview of common issues
kb list --type issue
```

## Search Syntax

The knowledge base uses SQLite FTS5 full-text search:

```bash
# Basic search (matches any word)
kb search "deployment production"

# Phrase search
kb search '"exact phrase"'

# Boolean operators
kb search "deployment AND production"
kb search "deployment OR staging"
kb search "deployment NOT deprecated"

# Prefix matching
kb search "deploy*"

# Column-specific search
kb search "title:deployment"
kb search "content:production"
```

## Integration Examples

### Pre-commit Hook

Document decisions before merging:

```bash
# .git/hooks/pre-commit
#!/bin/bash
# Remind to document significant changes
if git diff --cached | grep -q "BREAKING CHANGE"; then
  echo "Consider documenting this breaking change:"
  echo "kb add 'Breaking change in...' --type decision"
fi
```

### Automated Issue Capture

Capture errors from logs:

```bash
# Monitor logs and create issues
tail -f app.log | grep ERROR | while read line; do
  kb add "Error: $(echo $line | cut -d: -f2)" \
    --type issue \
    --tags "error,automated" \
    --content "$line"
done
```

### Documentation Generation

Export knowledge to markdown:

```bash
# Generate architecture decision records
kb list --type decision --format json | \
  jq -r '.articles[].id' | \
  while read id; do
    kb get $id --format markdown > "docs/adr/$(printf %03d $id).md"
  done
```

### Slack Integration

Search from Slack (pseudo-code):

```bash
# Slack bot command: /kb search <query>
kb search "$query" --format json | \
  jq -r '.results[] | "[\(.id)] \(.title) - \(.content[:100])"'
```

## Best Practices

1. **Use Descriptive Titles**: Make titles searchable and clear
2. **Tag Consistently**: Establish a tagging convention early
3. **Link to Code**: Always link to relevant code or PRs
4. **Type Appropriately**: Use the right article type for discoverability
5. **Markdown Formatting**: Use headers, lists, and code blocks
6. **Update, Don't Duplicate**: Update existing articles instead of creating similar ones
7. **Add Context**: Explain the "why" not just the "what"
8. **Review Regularly**: Tag articles for review and keep content fresh

## Schema

### Articles Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Article title |
| content | TEXT | Markdown content |
| article_type | TEXT | knowledge/issue/solution/decision |
| created_at | TEXT | ISO8601 timestamp |
| updated_at | TEXT | ISO8601 timestamp |
| author | TEXT | Author name |
| metadata | TEXT | JSON metadata |

### Tags Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Tag name (unique) |

### Links Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| article_id | INTEGER | Foreign key to articles |
| url | TEXT | Link URL |
| link_type | TEXT | Type (code/docs/wiki/reference) |
| description | TEXT | Optional description |

## Backup and Restore

### Backup

```bash
# SQLite backup
sqlite3 ~/.kb/knowledge.db ".backup /path/to/backup.db"

# Export to JSON
kb list --format json --limit 999999 > kb-export.json

# Export all articles to markdown
mkdir -p kb-backup
kb list --format json --limit 999999 | \
  jq -r '.articles[].id' | \
  while read id; do
    kb get $id --format markdown > "kb-backup/$id.md"
  done
```

### Restore

```bash
# SQLite restore
cp /path/to/backup.db ~/.kb/knowledge.db

# Import from JSON (requires custom script)
# See kb/storage.py for programmatic access
```

## Troubleshooting

### Database locked error

If you get "database is locked":
- Close other kb processes
- Check for stuck web server (`pkill -f kb-web`)
- SQLite uses file-level locking, so concurrent writes are limited

### Search not finding results

- Check search syntax (use quotes for exact phrases)
- Verify article exists: `kb list`
- Check FTS index: `sqlite3 ~/.kb/knowledge.db "SELECT * FROM articles_fts LIMIT 1"`

### Web interface not accessible

```bash
# Check if server is running
ps aux | grep kb-web

# Check port availability
lsof -i :8000

# Start with different port
kb-web --port 8001
```

## Python API

For programmatic access:

```python
from kb.storage import KnowledgeBase

# Initialize
kb = KnowledgeBase()  # Uses default location
kb = KnowledgeBase('/path/to/custom.db')

# Add article
article_id = kb.add_article(
    title="My Article",
    content="Content here",
    article_type="knowledge",
    tags=["tag1", "tag2"],
    links=[{
        'url': 'https://example.com',
        'type': 'reference',
        'description': 'Related docs'
    }]
)

# Search
results = kb.search("my query", limit=10)

# Get article
article = kb.get_article(article_id)

# Update
kb.update_article(article_id, title="New Title")

# Delete
kb.delete_article(article_id)

# List
articles, total = kb.list_articles(article_type="knowledge", limit=50)

# Stats
stats = kb.get_stats()
```

## Future Enhancements

Potential future features:

- [ ] Version history for articles
- [ ] Article relationships (related to, supersedes, etc.)
- [ ] Rich media attachments
- [ ] Export to different formats (PDF, HTML)
- [ ] Import from Confluence, Notion, etc.
- [ ] AI-powered search and summarization
- [ ] Slack/Teams integration
- [ ] Automated tagging suggestions
- [ ] Access control and permissions
- [ ] Analytics and usage tracking
