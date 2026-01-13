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

## License

Part of the decentclaude data engineering toolkit.
