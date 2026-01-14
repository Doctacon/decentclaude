# Documentation

Welcome to the DecentClaude data workflows documentation. This documentation has been reorganized into three main sections for easier navigation.

## Quick Navigation

- **[Complete Documentation Index](INDEX.md)** - Full searchable index with quick links
- **[Claude Code Setup](CLAUDE_CODE_SETUP.md)** - Integrate DecentClaude with Claude Code (<5 minutes)
- **[Tool Registry](../lib/tool_registry.json)** - Complete catalog of all 23+ tools
- **[JSON Schemas](../schemas/README.md)** - Output schemas for all tools
- **[Reference Documentation](reference/)** - API and tool references
- **[Guides and Tutorials](guides/)** - Step-by-step instructions
- **[Architecture Documentation](architecture/)** - Design docs and system architecture

## Documentation Structure

### Reference Documentation

API and tool reference documentation for lookup and detailed information.

**Location**: `docs/reference/`

**Contents**:
- MCP Server documentation (BigQuery, GitHub, Databases, Monitoring)
- MCP Development Guide
- Settings and configuration reference
- Code review guidelines and templates
- Documentation templates

**[Browse Reference Docs](reference/README.md)**

### Guides and Tutorials

Step-by-step instructions and how-to guides for common tasks.

**Location**: `docs/guides/`

**Contents**:
- QUICKSTART guide
- Workflow tutorials
- Team workflows and session management
- Data engineering and testing patterns
- Playbooks and troubleshooting guides

**[Browse Guides](guides/README.md)**

### Architecture Documentation

Design documents and implementation details for the system.

**Location**: `docs/architecture/`

**Contents**:
- Knowledge base architecture
- Observability system
- Debug system design
- Git worktrees integration
- Examples and validation

**[Browse Architecture Docs](architecture/README.md)**

## Getting Started

New to DecentClaude? Follow this path:

1. **[Main README](../README.md)** - Start with the project overview
2. **[Claude Code Setup](CLAUDE_CODE_SETUP.md)** - Integrate with Claude Code (<5 minutes)
3. **[Tool Registry](../lib/tool_registry.json)** - Discover available tools
4. **[QUICKSTART](guides/QUICKSTART.md)** - Get up and running in minutes
5. **[Settings Best Practices](reference/settings-best-practices.md)** - Configure your environment
6. **[Workflows Tutorial](guides/WORKFLOWS_TUTORIAL.md)** - Learn the workflows

## Mayor CLI

DecentClaude provides a unified CLI for all tools:

```bash
mayor --help                    # Show all commands
mayor list                      # List all available tools
mayor search "data quality"     # Search tools by keyword
mayor config init               # Interactive configuration wizard
```

### Quick Commands

```bash
# BigQuery Tools
mayor bq profile <table>        # Profile table with quality scores
mayor bq explain <sql>          # Analyze query execution plan
mayor bq optimize <sql>         # Get optimization suggestions
mayor bq validate <sql>         # Validate SQL syntax
mayor bq lineage <table>        # Trace table dependencies

# dbt Tools
mayor dbt test                  # Run dbt tests
mayor dbt compile               # Compile dbt models
mayor dbt run                   # Execute dbt models

# AI Tools
mayor ai generate <prompt>      # Generate code with LLMs
mayor ai review <file>          # AI code review
mayor ai docs <file>            # Generate documentation

# Workflows
mayor workflow run data-quality-audit     # Run DQ audit
mayor workflow run schema-migration       # Schema migration planning
```

See [Tool Registry](../lib/tool_registry.json) for complete tool catalog.

## Finding What You Need

### By Task

Use the [Documentation Index](INDEX.md) to find documentation by:
- **Common tasks** (set up, configure, review PRs, analyze data, etc.)
- **Technology** (BigQuery, GitHub, PostgreSQL, etc.)
- **Use case** ("I want to...", "I need to...")
- **Experience level** (beginner, intermediate, advanced)

### By Section

- **Looking up API details?** → [Reference](reference/README.md)
- **Learning how to do something?** → [Guides](guides/README.md)
- **Understanding system design?** → [Architecture](architecture/README.md)

## Quick Links

### Most Popular Docs

- [QUICKSTART](guides/QUICKSTART.md) - Quick start guide
- [Team Workflows](guides/workflows/team-workflows.md) - Collaborative workflows
- [Settings Best Practices](reference/settings-best-practices.md) - Configuration guide
- [BigQuery MCP Server](reference/mcp-servers/bigquery.md) - BigQuery integration
- [GitHub MCP Server](reference/mcp-servers/github.md) - GitHub integration

### Common Tasks

- [Review a Pull Request](guides/workflows/team-workflows.md#pr-review-workflow)
- [Set Up Claude Code](reference/settings-best-practices.md)
- [Query BigQuery](reference/mcp-servers/bigquery.md)
- [Respond to an Incident](guides/workflows/team-workflows.md#incident-response-workflow)
- [Build Custom MCP Server](reference/mcp-servers/development-guide.md)

## MCP Server Matrix

Quick reference for available MCP servers:

| Server | Category | Use Cases | Documentation |
|--------|----------|-----------|---------------|
| **GitHub** | Development | PR review, issue tracking, repo management | [github.md](reference/mcp-servers/github.md) |
| **BigQuery** | Data | Analytics, data exploration, reporting | [bigquery.md](reference/mcp-servers/bigquery.md) |
| **PostgreSQL** | Database | Schema management, queries, migrations | [databases.md](reference/mcp-servers/databases.md) |
| **MySQL** | Database | Schema management, queries | [databases.md](reference/mcp-servers/databases.md) |
| **SQLite** | Database | Local databases, testing | [databases.md](reference/mcp-servers/databases.md) |
| **DataDog** | Monitoring | Metrics, alerts, APM, logs | [monitoring.md](reference/mcp-servers/monitoring.md) |
| **Prometheus** | Monitoring | Metrics, time series | [monitoring.md](reference/mcp-servers/monitoring.md) |
| **Grafana** | Monitoring | Dashboards, visualization | [monitoring.md](reference/mcp-servers/monitoring.md) |
| **New Relic** | Monitoring | APM, infrastructure monitoring | [monitoring.md](reference/mcp-servers/monitoring.md) |

## Workflow Matrix

Quick reference for team workflows:

| Workflow | Description | Key Tools | Documentation |
|----------|-------------|-----------|---------------|
| **PR Review** | Comprehensive code review | GitHub | [team-workflows.md](guides/workflows/team-workflows.md#pr-review-workflow) |
| **Incident Response** | Handle production incidents | DataDog, GitHub | [team-workflows.md](guides/workflows/team-workflows.md#incident-response-workflow) |
| **Feature Development** | Full feature lifecycle | GitHub, Database | [team-workflows.md](guides/workflows/team-workflows.md#feature-development-workflow) |
| **Code Migration** | Large-scale refactoring | GitHub, Database | [team-workflows.md](guides/workflows/team-workflows.md#code-migration-workflow) |
| **Testing** | Comprehensive testing | GitHub | [team-workflows.md](guides/workflows/team-workflows.md#testing-workflow) |
| **Documentation** | Create and maintain docs | GitHub | [team-workflows.md](guides/workflows/team-workflows.md#documentation-workflow) |

## Best Practices Summary

### Security

- **Never commit credentials** to version control
- Use environment variables or secure credential storage
- Implement proper access controls
- Regular credential rotation
- Audit MCP server permissions

See: [settings-best-practices.md#security-best-practices](reference/settings-best-practices.md#security-best-practices)

### Performance

- Optimize context window usage
- Use caching where appropriate
- Implement rate limiting
- Monitor resource usage
- Set appropriate timeouts

See: [settings-best-practices.md#performance-optimization](reference/settings-best-practices.md#performance-optimization)

### Collaboration

- Use shared team settings
- Document workflows and decisions
- Implement consistent patterns
- Regular knowledge sharing
- Clear handoff protocols

See: [workflows/team-workflows.md#collaboration-patterns](guides/workflows/team-workflows.md#collaboration-patterns)

## Contributing

When adding new documentation:

1. **Choose the right location**:
   - `reference/` for API docs, tool references, configuration
   - `guides/` for tutorials, how-tos, step-by-step instructions
   - `architecture/` for design docs, system architecture

2. **Update the index**: Add entries to [INDEX.md](INDEX.md)

3. **Update section README**: Update the README in the relevant section

4. **Follow conventions**: Match the structure and style of similar docs

5. **Include examples**: Add code examples and troubleshooting sections

See [INDEX.md - Contributing](INDEX.md#contributing-to-documentation) for detailed guidelines.

## Documentation Statistics

- **Total Documentation**: 100,000+ lines across all docs
- **Reference Docs**: 5,190+ lines
- **Guides**: 99,000+ lines
- **Architecture**: Multiple systems documented
- **Code Examples**: 100+ working examples

## Need Help?

- Check the [Troubleshooting Guide](guides/TROUBLESHOOTING.md)
- Search the [Complete Index](INDEX.md)
- Review the [Playbooks](guides/playbooks.md) for operational guidance

## Resources

### Official Documentation

- [Claude Code](https://docs.anthropic.com/claude-code)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP SDK](https://github.com/modelcontextprotocol/sdk)

### Community

- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [Example Configurations](https://github.com/anthropics/claude-code-examples)
