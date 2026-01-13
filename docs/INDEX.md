# Documentation Index

Complete index and navigation for all documentation in the DecentClaude data workflows system.

## Quick Links

- [Getting Started](#getting-started)
- [Reference Documentation](#reference-documentation)
- [Guides and Tutorials](#guides-and-tutorials)
- [Architecture and Design](#architecture-and-design)
- [Search by Topic](#search-by-topic)
- [Search by Use Case](#search-by-use-case)

## Getting Started

New to DecentClaude? Start here:

1. **[Main README](../README.md)** - Project overview and feature list
2. **[QUICKSTART](guides/QUICKSTART.md)** - Get up and running in minutes
3. **[Video Walkthrough](guides/VIDEO_WALKTHROUGH.md)** - Visual guide to the system
4. **[Settings Best Practices](reference/settings-best-practices.md)** - Configure Claude Code properly

## Reference Documentation

API and tool reference for lookup and detailed information.

**[Reference Documentation Home](reference/README.md)**

### MCP Server Reference

- **[BigQuery MCP Server](reference/mcp-servers/bigquery.md)** (942 lines)
  - 40+ tools for data analysis
  - Query optimization and cost management
  - Authentication and security
  - Complete troubleshooting guide

- **[GitHub MCP Server](reference/mcp-servers/github.md)** (1,142 lines)
  - Repository and branch operations
  - PR and issue management
  - Code review workflows
  - CI/CD integration

- **[Database MCP Servers](reference/mcp-servers/databases.md)** (899 lines)
  - PostgreSQL, MySQL, SQLite setup
  - Connection patterns and security
  - Schema introspection and queries
  - Performance tuning

- **[Monitoring Integration](reference/mcp-servers/monitoring.md)** (1,120 lines)
  - DataDog, Prometheus, Grafana, New Relic
  - Metrics and alerting
  - Incident response
  - Dashboard management

- **[MCP Development Guide](reference/mcp-servers/development-guide.md)** (1,087 lines)
  - Building custom MCP servers
  - TypeScript and Python examples
  - Tool and resource patterns
  - Testing and deployment

### Configuration Reference

- **[Settings Best Practices](reference/settings-best-practices.md)** (958 lines)
  - Model selection guidelines
  - Context window optimization
  - MCP server configuration
  - Hook and custom command setup
  - Security and team settings

### Code Review Reference

- **[Code Review README](reference/CODE_REVIEW_README.md)** - Main code review documentation
- **[Code Review Guidelines](reference/code-review-guidelines.md)** - Review guidelines and checklists
- **[Review Comment Templates](reference/review-comment-templates.md)** - Standardized templates
- **[PR Workflow Integration](reference/pr-workflow-integration.md)** - Pull request workflows

### Templates Reference

**[Templates Directory](reference/templates/README.md)**

- [CLAUDE.md Template](reference/templates/) - Project context template
- [Data Model Template](reference/templates/data-model.md) - Data model documentation
- [Pipeline Runbook](reference/templates/pipeline-runbook.md) - Pipeline operations
- [Troubleshooting Guide](reference/templates/troubleshooting-guide.md) - Troubleshooting template

## Guides and Tutorials

Step-by-step instructions and how-to guides.

**[Guides Home](guides/README.md)**

### Quick Start Guides

- **[QUICKSTART](guides/QUICKSTART.md)** (7,510 lines) - Complete quick start guide
- **[Video Walkthrough](guides/VIDEO_WALKTHROUGH.md)** - Visual tutorial

### Workflow Guides

- **[Workflows Tutorial](guides/WORKFLOWS_TUTORIAL.md)** - Main workflow tutorial

#### Team Workflows (906 lines)

**[Team Workflows](guides/workflows/team-workflows.md)**

- PR review workflow
- Incident response workflow
- Feature development workflow
- Code migration and testing
- Documentation workflow

#### Session Management (942 lines)

**[Session Management](guides/workflows/session-management.md)**

- Session resumption strategies
- Context management
- Background task patterns
- Multi-agent coordination
- Hooks and automation

### Pattern Guides

- **[Data Engineering Patterns](guides/data-engineering-patterns.md)** (22,030 lines)
  - dbt patterns
  - SQLMesh patterns
  - Data quality patterns
  - Testing patterns

- **[Data Testing Patterns](guides/data-testing-patterns.md)** (33,216 lines)
  - Unit testing
  - Integration testing
  - Data quality testing
  - Test automation

- **[Playbooks](guides/playbooks.md)** (36,227 lines)
  - Operational runbooks
  - Incident response
  - Deployment procedures
  - Troubleshooting workflows

### Troubleshooting Guides

- **[General Troubleshooting](guides/TROUBLESHOOTING.md)** - Common issues and solutions
- Each MCP server guide includes troubleshooting sections

## Architecture and Design

Design documents and implementation details.

**[Architecture Home](architecture/README.md)**

### Core Systems

- **[Knowledge Base](architecture/knowledge-base.md)** - Knowledge base system architecture
  - System design
  - Search capabilities
  - CLI and web interface
  - Integration patterns

- **[Observability](architecture/observability/)** - Complete observability system
  - Logging infrastructure
  - Metrics collection
  - Health monitoring
  - Analytics and error tracking
  - [Implementation Summary](architecture/observability/IMPLEMENTATION_SUMMARY.md)

- **[Debug System](architecture/debug/)** - AI-assisted debugging
  - [Debug Overview](architecture/debug/README.md)
  - [AI Debug](architecture/debug/AI_DEBUG.md)

### Git Integration

**[Worktrees](architecture/worktrees/)**

- [Worktrees Overview](architecture/worktrees/README.md)
- [Worktree Documentation](architecture/worktrees/WORKTREES.md)
- [Git Hooks](architecture/worktrees/HOOKS.md)
- [Utilities](architecture/worktrees/UTILITIES.md)

### Examples and Validation

**[Examples](architecture/examples/)**

- [Examples Overview](architecture/examples/README.md)
- [Testing Guide](architecture/examples/TESTING_GUIDE.md)
- [Examples Output](architecture/examples/EXAMPLES_OUTPUT.md)
- [Validation Summary](architecture/examples/VALIDATION_SUMMARY.md)

#### Hook Examples

**[Hook Examples](architecture/examples/hooks/)**

- [Hooks README](architecture/examples/hooks/README.md)
- [Hooks Quickstart](architecture/examples/hooks/QUICKSTART.md)
- [Observability](architecture/examples/hooks/OBSERVABILITY.md)
- [Integration Summary](architecture/examples/hooks/INTEGRATION_SUMMARY.md)
- [Quick Reference](architecture/examples/hooks/QUICK_REFERENCE.md)

#### Command Examples

- [Commands README](architecture/examples/commands/README.md)

#### AI-Generated Documentation

- [AI Docs README](architecture/examples/ai-docs/README.md)
- [dbt Model Docs](architecture/examples/ai-docs/dbt_model_docs.md)

## Search by Topic

### Authentication and Security

- [BigQuery Authentication](reference/mcp-servers/bigquery.md#authentication)
- [GitHub Authentication](reference/mcp-servers/github.md#authentication)
- [Database Security](reference/mcp-servers/databases.md#security)
- [Settings Security](reference/settings-best-practices.md#security-best-practices)

### Data Analysis

- [BigQuery Tools](reference/mcp-servers/bigquery.md)
- [Database Queries](reference/mcp-servers/databases.md)
- [Data Engineering Patterns](guides/data-engineering-patterns.md)

### Code Review

- [PR Review Workflow](guides/workflows/team-workflows.md#pr-review-workflow)
- [Code Review Guidelines](reference/code-review-guidelines.md)
- [GitHub Integration](reference/mcp-servers/github.md)
- [Review Templates](reference/review-comment-templates.md)

### Testing

- [Testing Workflow](guides/workflows/team-workflows.md#testing-workflow)
- [Data Testing Patterns](guides/data-testing-patterns.md)
- [Testing Guide](architecture/examples/TESTING_GUIDE.md)

### Incident Response

- [Incident Workflow](guides/workflows/team-workflows.md#incident-response-workflow)
- [Monitoring Integration](reference/mcp-servers/monitoring.md)
- [Playbooks](guides/playbooks.md)
- [Debug System](architecture/debug/)

### Session Management

- [Session Management Guide](guides/workflows/session-management.md)
- [Hooks Configuration](reference/settings-best-practices.md#hook-configuration)
- [Context Management](guides/workflows/session-management.md#context-management)

### Observability

- [Observability System](architecture/observability/)
- [Monitoring Integration](reference/mcp-servers/monitoring.md)
- [Hook Observability](architecture/examples/hooks/OBSERVABILITY.md)

### Custom Development

- [MCP Development Guide](reference/mcp-servers/development-guide.md)
- [Settings Configuration](reference/settings-best-practices.md)
- [Worktrees](architecture/worktrees/)

## Search by Use Case

### "I want to review a pull request"

1. [Team Workflows - PR Review](guides/workflows/team-workflows.md#pr-review-workflow)
2. [GitHub MCP Server](reference/mcp-servers/github.md)
3. [Code Review Guidelines](reference/code-review-guidelines.md)
4. [Review Templates](reference/review-comment-templates.md)

### "I need to analyze data"

1. [BigQuery MCP Server](reference/mcp-servers/bigquery.md)
2. [Database MCP Servers](reference/mcp-servers/databases.md)
3. [Data Engineering Patterns](guides/data-engineering-patterns.md)

### "I'm responding to an incident"

1. [Incident Response Workflow](guides/workflows/team-workflows.md#incident-response-workflow)
2. [Monitoring Integration](reference/mcp-servers/monitoring.md)
3. [Playbooks](guides/playbooks.md)
4. [Debug System](architecture/debug/)

### "I'm developing a new feature"

1. [Feature Development Workflow](guides/workflows/team-workflows.md#feature-development-workflow)
2. [Session Management](guides/workflows/session-management.md)
3. [GitHub MCP Server](reference/mcp-servers/github.md)
4. [Database MCP Servers](reference/mcp-servers/databases.md)

### "I need to set up Claude Code"

1. [QUICKSTART](guides/QUICKSTART.md)
2. [Settings Best Practices](reference/settings-best-practices.md)
3. [Video Walkthrough](guides/VIDEO_WALKTHROUGH.md)

### "I want to build a custom MCP server"

1. [MCP Development Guide](reference/mcp-servers/development-guide.md)
2. [Settings Configuration](reference/settings-best-practices.md#mcp-server-configuration)
3. Existing MCP server guides as examples

### "I need to troubleshoot an issue"

1. [General Troubleshooting](guides/TROUBLESHOOTING.md)
2. [Debug System](architecture/debug/)
3. MCP-specific troubleshooting in each server guide
4. [Playbooks](guides/playbooks.md)

### "I want to understand the architecture"

1. [Architecture Home](architecture/README.md)
2. [Observability System](architecture/observability/)
3. [Knowledge Base](architecture/knowledge-base.md)
4. [Examples](architecture/examples/)

### "I need to write tests"

1. [Testing Workflow](guides/workflows/team-workflows.md#testing-workflow)
2. [Data Testing Patterns](guides/data-testing-patterns.md)
3. [Testing Guide](architecture/examples/TESTING_GUIDE.md)

### "I want to manage sessions better"

1. [Session Management](guides/workflows/session-management.md)
2. [Hooks Configuration](reference/settings-best-practices.md#hook-configuration)
3. [Team Workflows](guides/workflows/team-workflows.md)

## Documentation by Experience Level

### Beginner

Start here if you're new to the system:

1. [Main README](../README.md)
2. [QUICKSTART](guides/QUICKSTART.md)
3. [Video Walkthrough](guides/VIDEO_WALKTHROUGH.md)
4. [Settings Best Practices](reference/settings-best-practices.md)
5. [Workflows Tutorial](guides/WORKFLOWS_TUTORIAL.md)

### Intermediate

Once you're comfortable with basics:

1. [Team Workflows](guides/workflows/team-workflows.md)
2. [GitHub MCP Server](reference/mcp-servers/github.md)
3. [Database MCP Servers](reference/mcp-servers/databases.md)
4. [Session Management](guides/workflows/session-management.md)
5. [Code Review Guidelines](reference/code-review-guidelines.md)

### Advanced

For power users and developers:

1. [MCP Development Guide](reference/mcp-servers/development-guide.md)
2. [Session Management - Advanced Patterns](guides/workflows/session-management.md#advanced-patterns)
3. [Monitoring Integration](reference/mcp-servers/monitoring.md)
4. [BigQuery MCP Server](reference/mcp-servers/bigquery.md)
5. [Architecture Documentation](architecture/)
6. [Data Engineering Patterns](guides/data-engineering-patterns.md)
7. [Playbooks](guides/playbooks.md)

## Documentation Statistics

### Total Documentation
- **Reference**: 8 major documents, 5,190+ lines
- **Guides**: 7 major guides, 99,000+ lines
- **Architecture**: 4 major systems documented

### Coverage Areas
- MCP Server Guides: 5 comprehensive guides
- Workflow Guides: 2 detailed guides
- Pattern Guides: 3 extensive pattern collections
- Configuration: 1 complete guide
- Code Examples: 100+ examples
- Troubleshooting: Sections in every guide

## Quick Reference Tables

### Common Tasks

| Task | Primary Documentation | Supporting Docs |
|------|----------------------|-----------------|
| Set up Claude Code | [Settings Best Practices](reference/settings-best-practices.md) | [QUICKSTART](guides/QUICKSTART.md) |
| Configure GitHub | [GitHub MCP Server](reference/mcp-servers/github.md) | [Settings](reference/settings-best-practices.md) |
| Review PRs | [PR Review Workflow](guides/workflows/team-workflows.md#pr-review-workflow) | [Code Review Guidelines](reference/code-review-guidelines.md) |
| Query databases | [Database MCP Servers](reference/mcp-servers/databases.md) | [BigQuery](reference/mcp-servers/bigquery.md) |
| Analyze data | [BigQuery MCP Server](reference/mcp-servers/bigquery.md) | [Data Patterns](guides/data-engineering-patterns.md) |
| Handle incidents | [Incident Response](guides/workflows/team-workflows.md#incident-response-workflow) | [Monitoring](reference/mcp-servers/monitoring.md) |
| Monitor systems | [Monitoring Integration](reference/mcp-servers/monitoring.md) | [Observability](architecture/observability/) |
| Build MCP server | [MCP Development Guide](reference/mcp-servers/development-guide.md) | [Settings](reference/settings-best-practices.md) |
| Manage sessions | [Session Management](guides/workflows/session-management.md) | [Team Workflows](guides/workflows/team-workflows.md) |
| Write tests | [Testing Workflow](guides/workflows/team-workflows.md#testing-workflow) | [Testing Patterns](guides/data-testing-patterns.md) |

### By Technology

| Technology | Documentation |
|------------|--------------|
| BigQuery | [BigQuery MCP Server](reference/mcp-servers/bigquery.md) |
| PostgreSQL | [Database MCP Servers](reference/mcp-servers/databases.md) |
| MySQL | [Database MCP Servers](reference/mcp-servers/databases.md) |
| SQLite | [Database MCP Servers](reference/mcp-servers/databases.md) |
| GitHub | [GitHub MCP Server](reference/mcp-servers/github.md) |
| DataDog | [Monitoring Integration](reference/mcp-servers/monitoring.md) |
| Prometheus | [Monitoring Integration](reference/mcp-servers/monitoring.md) |
| Grafana | [Monitoring Integration](reference/mcp-servers/monitoring.md) |
| New Relic | [Monitoring Integration](reference/mcp-servers/monitoring.md) |
| TypeScript | [MCP Development Guide](reference/mcp-servers/development-guide.md) |
| Python | [MCP Development Guide](reference/mcp-servers/development-guide.md) |
| dbt | [Data Engineering Patterns](guides/data-engineering-patterns.md) |
| SQLMesh | [Data Engineering Patterns](guides/data-engineering-patterns.md) |
| Git Worktrees | [Worktrees](architecture/worktrees/) |

## Navigation

### Main Sections
- [Reference Documentation](reference/README.md)
- [Guides and Tutorials](guides/README.md)
- [Architecture Documentation](architecture/README.md)

### Root Documentation
- [Main README](../README.md)
- [QUICKSTART](guides/QUICKSTART.md)
- [Project CLAUDE.md](../CLAUDE.md)

## Contributing to Documentation

When adding or updating documentation:

1. **Place it in the right section**:
   - Reference: API docs, tool references, configuration details
   - Guides: Tutorials, how-tos, step-by-step instructions
   - Architecture: Design docs, system architecture, implementation details

2. **Update this index** with new entries in appropriate sections

3. **Update section README** in the relevant directory

4. **Follow existing structure** in similar documents

5. **Include examples** and troubleshooting sections

6. **Test all code snippets** before publishing

7. **Add cross-references** to related documentation

8. **Update quick reference tables** if adding common tasks

## Maintenance

### Regular Updates

- Review quarterly for accuracy
- Update version numbers and compatibility info
- Refresh examples with current best practices
- Add new patterns discovered in production
- Remove or archive deprecated content
- Verify all links are working

### Version Tracking

Documentation versions are tracked in Git. See file history for changes.

## Feedback

For documentation improvements:

1. Identify the specific file and section needing update
2. Note the issue, gap, or suggestion
3. Propose improvements or corrections
4. Test changes if applicable
5. Update this index and related READMEs
6. Submit changes following contribution guidelines
