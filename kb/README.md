# Knowledge Base Module

A searchable knowledge base system for capturing tribal knowledge, common issues, solutions, and decisions.

## Quick Start

### CLI Usage

```bash
# Add an article
kb add "How to deploy" --content "Deploy using..." --tags "deployment"

# Search
kb search "deployment"

# List all
kb list

# Get specific article
kb get 1
```

### Web Interface

```bash
# Start web server
kb-web

# Open http://localhost:8000 in browser
```

### Python API

```python
from kb.storage import KnowledgeBase

kb = KnowledgeBase()
article_id = kb.add_article(
    title="My Article",
    content="Content here",
    tags=["tag1", "tag2"]
)
```

## Documentation

Full documentation: [docs/knowledge-base.md](../docs/knowledge-base.md)

## Module Structure

```
kb/
├── __init__.py     # Package initialization
├── storage.py      # SQLite storage backend with FTS5 search
├── web.py          # FastAPI web interface
└── README.md       # This file

bin/
├── kb              # CLI interface
└── kb-web          # Web server launcher

tests/
└── test_kb_storage.py  # Unit tests

docs/
└── knowledge-base.md   # Full documentation
```

## Features

- **Full-text search** using SQLite FTS5
- **Multiple article types**: knowledge, issue, solution, decision
- **Tagging system** for organization
- **Links** to code, docs, and resources
- **CLI** for automation
- **Web UI** for browsing
- **REST API** for integrations

## Dependencies

Core (storage + CLI):
- Python 3.7+ (no external dependencies)

Web interface:
- fastapi
- uvicorn

Testing:
- pytest

## Testing

```bash
# Run tests
pytest tests/test_kb_storage.py

# With coverage
pytest tests/test_kb_storage.py --cov=kb --cov-report=html
```

## Database

Default location: `~/.kb/knowledge.db`

SQLite database with:
- Articles table (with FTS5 index)
- Tags table
- Article-tag mapping
- Links table

## Troubleshooting Tools

### troubleshooting_tree.py

Interactive CLI decision tree for diagnosing and resolving common BigQuery issues.

**Usage**:
```bash
# Interactive mode - guided troubleshooting
python troubleshooting_tree.py

# Jump to specific category
python troubleshooting_tree.py --category sql
python troubleshooting_tree.py --category performance
python troubleshooting_tree.py --category cost
python troubleshooting_tree.py --category quality
python troubleshooting_tree.py --category tool

# Search knowledge base
python troubleshooting_tree.py --search "permission denied"
```

**Features**:
- Interactive decision tree with questions
- Diagnostic commands for each issue
- Links to relevant documentation
- Common solutions and examples
- Integration with MCP tools

**Categories**:
1. **SQL Errors** - Syntax, permissions, not found, timeouts, resources
2. **Performance** - Slow queries, high bytes scanned, queue times
3. **Cost** - Unexpected charges, quota exceeded, forecasting
4. **Data Quality** - NULLs, duplicates, schema issues, stale data
5. **Tool Errors** - Dependencies, configuration, API errors

**Documentation**: See [Troubleshooting Decision Tree](../docs/guides/troubleshooting-tree.md)

**Examples**:

```bash
# Example 1: SQL Error
$ python troubleshooting_tree.py --category sql

What type of SQL error are you getting?
  1. Syntax Error
  2. Permission Denied
  3. Table/Dataset Not Found
  4. Query Timeout
  5. Resources Exceeded

Your choice: 2

# Guides through permission troubleshooting...
```

```bash
# Example 2: Performance Issue
$ python troubleshooting_tree.py --category performance

What performance issue are you experiencing?
  1. Query execution is slow
  2. High bytes scanned
  3. Long queue time

Your choice: 1

# Shows optimization commands and suggestions...
```

## License

Part of the decentclaude data engineering toolkit.
