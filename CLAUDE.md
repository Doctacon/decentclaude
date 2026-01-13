# decentclaude - World-Class Claude Code Best Practices

**A comprehensive toolkit for data engineers and software developers using Claude Code**

> **Recovery**: Run `gt prime` after compaction, clear, or new session

## Overview

decentclaude is a curated collection of Claude Code best practices, workflows, and integrations specifically designed for world-class data engineering and software development. This repository contains production-ready Skills, Subagents, hooks, custom commands, and comprehensive documentation to supercharge your Claude Code workflows.

## What's Inside

### 🎯 Skills (22 General + 6 Data-Focused)

**General Engineering Workflows:**
- `/troubleshoot` - Systematic debugging with hypothesis testing
- `/iterate` - Build → Test → Review → Refine TDD cycle
- `/review-code` - Comprehensive code review workflow
- `/refactor` - Safe refactoring with test preservation
- `/add-tests` - Test addition with coverage analysis
- `/document` - README, API docs, architecture diagrams
- `/security-audit` - Security vulnerability scanning
- `/fix-ci` - CI/CD troubleshooting workflow
- `/triage-incident` - Incident response workflow
- `/optimize` - Performance profiling and optimization
- `/plan-architecture` - Architecture planning with ADRs
- `/design-api` - REST/GraphQL/gRPC API design
- `/migrate` - Database/framework migration planning
- `/add-monitoring` - Logging, metrics, tracing setup
- `/build-component` - React/Vue/Svelte scaffolding
- `/update-deps` - Dependency update workflow
- `/explain-code` - Code analysis and explanation
- `/generate-tests` - Automated test suite generation
- `/containerize` - Docker optimization
- `/setup-iac` - Terraform/Pulumi/CDK scaffolding
- `/make-accessible` - WCAG compliance auditing
- `/setup-env` - Environment variable management

**Data Engineering Workflows:**
- `/data-lineage-doc` - Auto-generate data lineage documentation with Mermaid diagrams
- `/schema-doc-generator` - Comprehensive schema documentation with quality metrics
- `/sql-optimizer` - Query analysis and optimization recommendations
- `/doc-generator` - Auto-generate project documentation from codebase

### 🤖 Subagents (3 General + 4 Data-Focused)

**General Engineering Experts:**
- `debugging-expert` - Stack trace analysis, log parsing, root cause identification
- `performance-expert` - Profiling and optimization strategies
- `architecture-reviewer` - System design and ADR review

**Data Engineering Experts:**
- `sql-reviewer` - BigQuery SQL code review and optimization
- `data-quality-tester` - Data profiling, anomaly detection, validation
- `schema-analyzer` - Schema design patterns and optimization
- `testing-orchestrator` - Test strategy and orchestration

### 🪝 Hooks (3)

Located in `examples/hooks/`:
- `PreToolUse__sql-validation.sh` - Validates SQL before execution, prevents costly mistakes
- `PostToolUse__auto-formatting.sh` - Auto-formats code files after edits (Python, SQL, JS, etc.)
- `PostToolUse__cost-tracking.sh` - Tracks BigQuery query costs, warns on budget thresholds

### ⚡ Custom Commands (3)

Located in `examples/commands/`:
- `query-explain` - Explains BigQuery query execution plans with cost estimates
- `schema-compare` - Compares schemas of two BigQuery tables
- `data-profile` - Generates data quality profiles for tables

### 📚 Documentation

Comprehensive guides in `docs/`:

**MCP Server Setup:**
- `mcp-servers/bigquery.md` - BigQuery MCP (40+ tools)
- `mcp-servers/github.md` - GitHub integration
- `mcp-servers/databases.md` - PostgreSQL, MySQL, SQLite
- `mcp-servers/monitoring.md` - DataDog, Prometheus, Grafana, New Relic
- `mcp-servers/development-guide.md` - Build custom MCP servers

**Workflows:**
- `workflows/team-workflows.md` - PR review, incident response, feature development
- `workflows/session-management.md` - Advanced session patterns

**Configuration:**
- `settings-best-practices.md` - Recommended Claude Code settings

## Quick Start

### 1. Clone Skills and Subagents

```bash
# Copy to your local Claude Code config
cp -r .claude/skills ~/.claude/skills
cp -r .claude/agents ~/.claude/agents
```

### 2. Install Hooks (Optional)

```bash
mkdir -p ~/.claude/hooks
cp examples/hooks/*.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/*.sh
```

### 3. Install Custom Commands (Optional)

```bash
mkdir -p ~/bin
ln -s $(pwd)/examples/commands/* ~/bin/
# Ensure ~/bin is in your PATH
```

### 4. Configure MCP Servers

Follow the guides in `docs/mcp-servers/` to set up:
- BigQuery MCP (for data engineering workflows)
- GitHub MCP (for PR reviews and issue management)
- Database MCPs (for schema analysis)

### 5. Start Using

```bash
# Use Skills via slash commands
/troubleshoot
/iterate
/data-lineage-doc

# Use custom commands
/query-explain "SELECT * FROM table"
/schema-compare project.dev.users project.prod.users
/data-profile project.dataset.table

# Hooks run automatically when enabled
```

## Git Worktree Best Practices

decentclaude is designed to work seamlessly with Git worktrees for parallel development:

### Creating Worktrees

```bash
# Create a worktree for feature development
git worktree add ../decentclaude-feature feature-branch

# Work in isolated environment
cd ../decentclaude-feature
# Make changes, test, commit

# Return to main worktree
cd ../decentclaude
git worktree list
```

### Benefits
- **Parallel work**: Multiple branches without stashing
- **Testing**: Compare implementations side-by-side
- **Code review**: Check out PR branches without disrupting current work
- **Experimentation**: Try risky changes in isolation

### Cleanup

```bash
# Remove completed worktree
git worktree remove ../decentclaude-feature
git worktree prune
```

## Integration with Gas Town

This repository is designed to work with the Gas Town multi-agent workflow:

- **Polecats** use these Skills and Subagents for autonomous work
- **Witness** leverages hooks for validation and tracking
- **Refinery** uses workflows for merge queue processing
- **Mayor** coordinates using team workflows

## Contributing

When adding new capabilities:
1. Follow existing patterns in `.claude/skills/` and `.claude/agents/`
2. Include comprehensive documentation
3. Add examples and troubleshooting
4. Test with real workflows
5. Update this CLAUDE.md with new capabilities

## Support

- Check `docs/` for comprehensive guides
- See `examples/` for working code
- Review existing Skills/Subagents for patterns
- File issues for bugs or feature requests

## License

MIT - Use freely in your own projects

---

**Built for world-class data engineers who demand excellence** 🚀
