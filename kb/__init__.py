"""
Knowledge Base Package

A searchable knowledge base system for capturing tribal knowledge,
documenting common issues, storing solutions and workarounds, and
tracking decisions and rationale.

Features:
- SQLite-based storage with full-text search
- CLI interface for command-line operations
- Web interface for browsing and searching
- Support for tags, links, and metadata
- Multiple article types: knowledge, issue, solution, decision
"""

from kb.storage import KnowledgeBase

__version__ = "1.0.0"
__all__ = ['KnowledgeBase']
