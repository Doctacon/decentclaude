# Guides

This directory contains tutorial and how-to guides for using the DecentClaude data workflows system.

## Contents

### Getting Started

- **[QUICKSTART.md](QUICKSTART.md)** - Quick start guide to get up and running
- **[VIDEO_WALKTHROUGH.md](VIDEO_WALKTHROUGH.md)** - Video walkthrough guide
- **[command-aliases.md](command-aliases.md)** - Install and use short command aliases for faster workflows
- **[aliases-quick-ref.md](aliases-quick-ref.md)** - One-page cheat sheet of all available aliases

### Workflows

Comprehensive workflow guides for common data engineering tasks:

- **[WORKFLOWS_TUTORIAL.md](WORKFLOWS_TUTORIAL.md)** - Main workflow tutorial
- **[Team Workflows](workflows/team-workflows.md)** - Collaborative team workflows
  - PR review workflow
  - Incident response workflow
  - Feature development workflow
  - Code migration and testing
  - Documentation workflow
- **[Session Management](workflows/session-management.md)** - Session resumption and context management
  - Session resumption strategies
  - Context management
  - Background task patterns
  - Multi-agent coordination
  - Hooks and automation

### Patterns and Best Practices

- **[data-engineering-patterns.md](data-engineering-patterns.md)** - Data engineering patterns and practices
- **[data-testing-patterns.md](data-testing-patterns.md)** - Data testing patterns and strategies
- **[playbooks.md](playbooks.md)** - Operational playbooks for common scenarios

### Troubleshooting

- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - General troubleshooting guide for common issues
- **[troubleshooting-tree.md](troubleshooting-tree.md)** - Interactive decision tree for BigQuery issues
  - Comprehensive flowchart covering SQL errors, performance, cost, data quality, and tool errors
  - Diagnostic commands and solutions for each issue type
  - Integration with MCP tools and utilities
  - Interactive CLI tool: `python kb/troubleshooting_tree.py`
- **[troubleshooting-quick-ref.md](troubleshooting-quick-ref.md)** - One-page quick reference cheat sheet
  - Most common issues and solutions
  - Emergency commands
  - Key MCP tools
  - Common query patterns

## Organization

Guides are organized by complexity:

1. **Beginner**: QUICKSTART, VIDEO_WALKTHROUGH
2. **Intermediate**: WORKFLOWS_TUTORIAL, team-workflows
3. **Advanced**: session-management, playbooks, patterns

## Usage

Start with the QUICKSTART guide if you're new to the system. Progress through the workflow tutorials to learn collaborative patterns, then explore the advanced patterns and playbooks for production usage.

## Navigation

- [Back to Main Index](../INDEX.md)
- [Reference](../reference/README.md)
- [Architecture](../architecture/README.md)
