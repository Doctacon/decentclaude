# Step 1: Understanding the Project Structure

## Overview

DecentClaude is organized to support efficient data engineering workflows with Claude Code integration. Let's explore the key directories and their purposes.

## Core Directory Structure

```
decentclaude/
├── bin/                    # CLI utilities
│   ├── data-utils/        # BigQuery tools
│   └── worktree-utils/    # Git worktree management
├── docs/                   # Documentation and templates
│   └── templates/         # Reusable doc templates
├── examples/              # Example SQL and transformations
├── scripts/               # Python automation scripts
├── tutorials/             # Interactive learning (you are here!)
├── onboarding/            # First-time setup resources
├── assessments/           # Quizzes and certifications
└── progress-tracking/     # Skill progression system
```

## Key Components

### 1. CLI Utilities (`bin/`)

The `bin/` directory contains executable scripts for common tasks:

**BigQuery Utilities**:
- `bq-schema-diff` - Compare schemas between tables
- `bq-query-cost` - Estimate query costs before running
- `bq-partition-info` - View partition information
- `bq-lineage` - Trace data lineage

**Worktree Utilities** (for multi-agent coordination):
- `wt-clean` - Clean up worktrees
- `wt-switch` - Switch between worktrees
- `wt-sync` - Sync worktree changes
- `wt-status` - View worktree status

### 2. Documentation (`docs/`)

Templates for standardizing your data documentation:

- `CLAUDE.md.template` - Project instructions for Claude Code
- `data-model.md` - Model documentation template
- `pipeline-runbook.md` - Operational procedures
- `troubleshooting-guide.md` - Problem resolution guide

### 3. Scripts (`scripts/`)

Python automation scripts:

- `data_quality.py` - Data quality validation framework

### 4. Knowledge Base

- `data-engineering-patterns.md` - Best practices for dbt, SQLMesh, BigQuery
- `data-testing-patterns.md` - Testing strategies and patterns
- `playbooks.md` - Operational playbooks and procedures

## Interactive Exercise

Let's explore the project structure hands-on:

```bash
# View the directory structure
tree -L 2 -d

# Check out the BigQuery utilities
ls -l bin/data-utils/

# Read about data engineering patterns
head -n 50 data-engineering-patterns.md

# Explore example SQL
ls -l examples/sql/
```

## Key Concepts

### Claude Code Integration

DecentClaude is designed to work seamlessly with Claude Code:

- **Hooks**: Automated validation on file changes
- **Templates**: Auto-fillable documentation
- **Guided workflows**: Claude assists with complex tasks

### Multi-Agent Architecture

The project supports multiple agents working simultaneously:

- **Git worktrees**: Isolated working directories per agent
- **Coordination hooks**: Prevent conflicts
- **Shared knowledge**: Centralized documentation

## Checkpoint Questions

1. Where would you find utilities for checking BigQuery query costs?
2. Which file contains best practices for BigQuery partitioning?
3. What directory contains reusable documentation templates?

<details>
<summary>View Answers</summary>

1. `bin/data-utils/bq-query-cost`
2. `data-engineering-patterns.md`
3. `docs/templates/`

</details>

## What You Learned

- DecentClaude's directory organization
- Purpose of key components (bin, docs, scripts)
- How Claude Code integrates with the project
- Where to find utilities and documentation

## Next Step

Continue to [Step 2: Environment Setup](02-environment-setup.md) to configure your development environment.
