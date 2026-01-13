# Documentation Index

Complete index of all documentation in the decentclaude/mayor/rig project.

## Quick Navigation

- [New Documentation](#new-documentation) - Comprehensive MCP and workflow guides
- [Existing Documentation](#existing-documentation) - Pre-existing project docs
- [By Topic](#documentation-by-topic) - Organized by subject matter
- [By Use Case](#documentation-by-use-case) - Organized by task

## New Documentation

### MCP Server Setup (8,341 lines)

**[Main README](README.md)** - Start here for overview and quick start

#### Server Guides

1. **[BigQuery MCP Server](mcp-servers/bigquery.md)** (942 lines)
   - 40+ tools for data analysis
   - Query optimization and cost management
   - Authentication and security
   - Complete troubleshooting guide

2. **[GitHub MCP Server](mcp-servers/github.md)** (1,142 lines)
   - Repository and branch operations
   - PR and issue management
   - Code review workflows
   - CI/CD integration

3. **[Database MCP Servers](mcp-servers/databases.md)** (899 lines)
   - PostgreSQL, MySQL, SQLite setup
   - Connection patterns and security
   - Schema introspection and queries
   - Performance tuning

4. **[Monitoring Integration](mcp-servers/monitoring.md)** (1,120 lines)
   - DataDog, Prometheus, Grafana, New Relic
   - Metrics and alerting
   - Incident response
   - Dashboard management

5. **[MCP Development Guide](mcp-servers/development-guide.md)** (1,087 lines)
   - Building custom MCP servers
   - TypeScript and Python examples
   - Tool and resource patterns
   - Testing and deployment

### Team Workflows (1,848 lines)

1. **[Team Workflows](workflows/team-workflows.md)** (906 lines)
   - PR review workflow
   - Incident response workflow
   - Feature development workflow
   - Code migration and testing
   - Documentation workflow

2. **[Session Management](workflows/session-management.md)** (942 lines)
   - Session resumption strategies
   - Context management
   - Background task patterns
   - Multi-agent coordination
   - Hooks and automation

### Configuration

**[Settings Best Practices](settings-best-practices.md)** (958 lines)
- Model selection guidelines
- Context window optimization
- MCP server configuration
- Hook and custom command setup
- Security and team settings

## Existing Documentation

### Code Review System

- **[CODE_REVIEW_README.md](CODE_REVIEW_README.md)** - Main code review documentation
- **[code-review-guidelines.md](code-review-guidelines.md)** - Review guidelines and checklists
- **[review-comment-templates.md](review-comment-templates.md)** - Comment templates
- **[pr-workflow-integration.md](pr-workflow-integration.md)** - PR workflow integration

### Workflows and Tutorials

- **[WORKFLOWS_TUTORIAL.md](WORKFLOWS_TUTORIAL.md)** - Workflow tutorials
- **[VIDEO_WALKTHROUGH.md](VIDEO_WALKTHROUGH.md)** - Video walkthrough guide
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - General troubleshooting

### Knowledge Base

- **[knowledge-base.md](knowledge-base.md)** - Project knowledge base

### Debug Documentation

Directory: `debug/`
- **[README.md](debug/README.md)** - Debug documentation overview
- **[AI_DEBUG.md](debug/AI_DEBUG.md)** - AI debugging guide

### Templates

Directory: `templates/`
- **[README.md](templates/README.md)** - Templates overview
- **[CLAUDE.md.template](templates/CLAUDE.md.template)** - Claude context template
- **[data-model.md](templates/data-model.md)** - Data model template
- **[pipeline-runbook.md](templates/pipeline-runbook.md)** - Pipeline runbook template
- **[troubleshooting-guide.md](templates/troubleshooting-guide.md)** - Troubleshooting template

### Worktrees

Directory: `worktrees/`
- **[README.md](worktrees/README.md)** - Worktrees overview
- **[WORKTREES.md](worktrees/WORKTREES.md)** - Worktree documentation
- **[HOOKS.md](worktrees/HOOKS.md)** - Git hooks documentation
- **[UTILITIES.md](worktrees/UTILITIES.md)** - Utility scripts

## Documentation by Topic

### Getting Started

1. [Main README](README.md) - Start here
2. [Settings Best Practices](settings-best-practices.md) - Configure Claude Code
3. [Workflows Tutorial](WORKFLOWS_TUTORIAL.md) - Learn workflows

### MCP Servers

#### Data and Analytics
- [BigQuery MCP Server](mcp-servers/bigquery.md)
- [Database MCP Servers](mcp-servers/databases.md) (PostgreSQL, MySQL, SQLite)

#### Development Tools
- [GitHub MCP Server](mcp-servers/github.md)

#### Monitoring and Observability
- [Monitoring Integration](mcp-servers/monitoring.md) (DataDog, Prometheus, Grafana, New Relic)

#### Custom Development
- [MCP Development Guide](mcp-servers/development-guide.md)

### Workflows

#### Daily Operations
- [Team Workflows](workflows/team-workflows.md)
- [PR Workflow Integration](pr-workflow-integration.md)
- [Code Review Guidelines](code-review-guidelines.md)

#### Advanced Patterns
- [Session Management](workflows/session-management.md)
- [Worktrees](worktrees/README.md)

### Configuration

- [Settings Best Practices](settings-best-practices.md)
- [Templates](templates/README.md)

### Troubleshooting

- [Main Troubleshooting](TROUBLESHOOTING.md)
- [Debug Guide](debug/README.md)
- Each MCP server guide has troubleshooting section

## Documentation by Use Case

### Code Review

**Primary Docs**:
- [Team Workflows - PR Review](workflows/team-workflows.md#pr-review-workflow)
- [Code Review Guidelines](code-review-guidelines.md)
- [GitHub MCP Server](mcp-servers/github.md)

**Supporting Docs**:
- [Review Comment Templates](review-comment-templates.md)
- [PR Workflow Integration](pr-workflow-integration.md)
- [CODE_REVIEW_README.md](CODE_REVIEW_README.md)

### Data Analysis

**Primary Docs**:
- [BigQuery MCP Server](mcp-servers/bigquery.md)
- [Database MCP Servers](mcp-servers/databases.md)

**Supporting Docs**:
- [Settings Best Practices](settings-best-practices.md#mcp-server-configuration)

### Incident Response

**Primary Docs**:
- [Team Workflows - Incident Response](workflows/team-workflows.md#incident-response-workflow)
- [Monitoring Integration](mcp-servers/monitoring.md)

**Supporting Docs**:
- [Troubleshooting Guide Template](templates/troubleshooting-guide.md)
- [Session Management](workflows/session-management.md)

### Feature Development

**Primary Docs**:
- [Team Workflows - Feature Development](workflows/team-workflows.md#feature-development-workflow)
- [Session Management](workflows/session-management.md)

**Supporting Docs**:
- [GitHub MCP Server](mcp-servers/github.md)
- [Database MCP Servers](mcp-servers/databases.md)
- [Settings Best Practices](settings-best-practices.md)

### Database Management

**Primary Docs**:
- [Database MCP Servers](mcp-servers/databases.md)
- [BigQuery MCP Server](mcp-servers/bigquery.md)

**Supporting Docs**:
- [Data Model Template](templates/data-model.md)
- [Team Workflows - Testing](workflows/team-workflows.md#testing-workflow)

### Testing

**Primary Docs**:
- [Team Workflows - Testing](workflows/team-workflows.md#testing-workflow)

**Supporting Docs**:
- [GitHub MCP Server](mcp-servers/github.md)
- [Settings Best Practices](settings-best-practices.md#custom-commands)

### Documentation

**Primary Docs**:
- [Team Workflows - Documentation](workflows/team-workflows.md#documentation-workflow)

**Supporting Docs**:
- [Templates](templates/README.md)
- [Knowledge Base](knowledge-base.md)

### Custom Integration

**Primary Docs**:
- [MCP Development Guide](mcp-servers/development-guide.md)

**Supporting Docs**:
- [Settings Best Practices](settings-best-practices.md#mcp-server-configuration)
- All MCP server guides as examples

### Session Management

**Primary Docs**:
- [Session Management](workflows/session-management.md)

**Supporting Docs**:
- [Settings Best Practices](settings-best-practices.md#hook-configuration)
- [Team Workflows](workflows/team-workflows.md)

### Debugging

**Primary Docs**:
- [Debug Guide](debug/README.md)
- [AI Debug](debug/AI_DEBUG.md)
- [Main Troubleshooting](TROUBLESHOOTING.md)

**Supporting Docs**:
- Troubleshooting sections in each guide
- [Troubleshooting Template](templates/troubleshooting-guide.md)

## Documentation Statistics

### New Documentation
- **Total Lines**: 8,341
- **Total Files**: 8
- **Topics Covered**: 40+

### Line Count by Section
- MCP Servers: 5,190 lines
- Team Workflows: 1,848 lines
- Settings: 958 lines
- Main README: 345 lines

### Coverage
- **MCP Server Guides**: 5 comprehensive guides
- **Workflow Guides**: 2 detailed guides
- **Configuration Guide**: 1 complete guide
- **Code Examples**: 100+ examples
- **Troubleshooting Sections**: In every guide

## Quick Reference

### Common Tasks

| Task | Documentation |
|------|--------------|
| Set up Claude Code | [Settings Best Practices](settings-best-practices.md) |
| Configure GitHub | [GitHub MCP Server](mcp-servers/github.md) |
| Review PRs | [PR Review Workflow](workflows/team-workflows.md#pr-review-workflow) |
| Query databases | [Database MCP Servers](mcp-servers/databases.md) |
| Analyze data | [BigQuery MCP Server](mcp-servers/bigquery.md) |
| Handle incidents | [Incident Response](workflows/team-workflows.md#incident-response-workflow) |
| Monitor systems | [Monitoring Integration](mcp-servers/monitoring.md) |
| Build custom server | [MCP Development Guide](mcp-servers/development-guide.md) |
| Manage sessions | [Session Management](workflows/session-management.md) |
| Write tests | [Testing Workflow](workflows/team-workflows.md#testing-workflow) |

### By Experience Level

**Beginners**:
1. [Main README](README.md)
2. [Settings Best Practices](settings-best-practices.md)
3. [Workflows Tutorial](WORKFLOWS_TUTORIAL.md)
4. [Video Walkthrough](VIDEO_WALKTHROUGH.md)

**Intermediate**:
1. [Team Workflows](workflows/team-workflows.md)
2. [GitHub MCP Server](mcp-servers/github.md)
3. [Session Management](workflows/session-management.md)
4. [Database MCP Servers](mcp-servers/databases.md)

**Advanced**:
1. [MCP Development Guide](mcp-servers/development-guide.md)
2. [Session Management - Advanced](workflows/session-management.md#advanced-patterns)
3. [Monitoring Integration](mcp-servers/monitoring.md)
4. [BigQuery MCP Server](mcp-servers/bigquery.md)

## Search Tips

### By Keyword

- **Authentication**: Check MCP server guides (BigQuery, GitHub, databases, monitoring)
- **Hooks**: See [Settings Best Practices](settings-best-practices.md#hook-configuration) and [Session Management](workflows/session-management.md#session-hooks-and-automation)
- **Context**: See [Session Management](workflows/session-management.md#context-management)
- **Security**: See [Settings Best Practices](settings-best-practices.md#security-best-practices) and individual MCP guides
- **Testing**: See [Team Workflows](workflows/team-workflows.md#testing-workflow)
- **Performance**: Check optimization sections in each guide

### By Technology

- **BigQuery**: [BigQuery MCP Server](mcp-servers/bigquery.md)
- **PostgreSQL**: [Database MCP Servers](mcp-servers/databases.md)
- **GitHub**: [GitHub MCP Server](mcp-servers/github.md)
- **DataDog**: [Monitoring Integration](mcp-servers/monitoring.md)
- **Prometheus**: [Monitoring Integration](mcp-servers/monitoring.md)
- **TypeScript**: [MCP Development Guide](mcp-servers/development-guide.md)
- **Python**: [MCP Development Guide](mcp-servers/development-guide.md)

## Contributing

When adding new documentation:

1. **Update this index** with new entries
2. **Update main README** if adding major sections
3. **Follow existing structure** in similar docs
4. **Include examples** and troubleshooting
5. **Test all code snippets**
6. **Add cross-references** to related docs

## Maintenance

### Regular Updates

- Review quarterly for accuracy
- Update version numbers
- Refresh examples
- Add new patterns discovered
- Remove deprecated content

### Version Tracking

Document versions are tracked in individual files. See each file's version history section.

## Feedback

For documentation improvements:
1. Identify the specific file and section
2. Note the issue or gap
3. Propose improvements
4. Update and test
5. Update this index if needed
