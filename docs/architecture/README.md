# Architecture Documentation

This directory contains design documents, architecture decisions, and implementation details for the DecentClaude data workflows system.

## Contents

### Knowledge Base System

- **[knowledge-base.md](knowledge-base.md)** - Knowledge base architecture and implementation
  - System design
  - Search capabilities
  - CLI and web interface
  - Integration patterns

### Worktrees and Git Integration

- **[worktrees/](worktrees/)** - Git worktree integration
  - [WORKTREES.md](worktrees/WORKTREES.md) - Worktree documentation
  - [HOOKS.md](worktrees/HOOKS.md) - Git hooks documentation
  - [UTILITIES.md](worktrees/UTILITIES.md) - Utility scripts
  - [README.md](worktrees/README.md) - Worktrees overview

### Observability System

- **[observability/](observability/)** - Comprehensive observability implementation
  - Logging infrastructure
  - Metrics collection
  - Health monitoring
  - Analytics
  - Error tracking
  - Implementation summary

### Examples and Validation

- **[examples/](examples/)** - Working examples and validation
  - Hook examples
  - Command examples
  - AI-generated documentation examples
  - Testing guides
  - Validation summaries

### Debug Architecture

- **[debug/](debug/)** - Debugging system architecture
  - [README.md](debug/README.md) - Debug system overview
  - [AI_DEBUG.md](debug/AI_DEBUG.md) - AI-assisted debugging

## Organization

Architecture documentation is organized by system component:

1. **Core Systems**: Knowledge base, observability, debugging
2. **Integration**: Worktrees, git hooks, MCP servers
3. **Examples**: Real-world implementations and validations

## Purpose

This documentation explains:

- **Why** design decisions were made
- **How** systems are implemented
- **What** patterns are used throughout the codebase
- **When** to use specific approaches

For step-by-step instructions, see the [Guides](../guides/) directory.

For API and tool references, see the [Reference](../reference/) directory.

## Navigation

- [Back to Main Index](../INDEX.md)
- [Reference](../reference/README.md)
- [Guides](../guides/README.md)
