# PR and Code Review Workflow Integration

> **Purpose**: Guide for integrating PR templates, code review processes, and automation with GitHub/GitLab.

## Table of Contents

- [Overview](#overview)
- [GitHub Integration](#github-integration)
- [GitLab Integration](#gitlab-integration)
- [Automation Workflows](#automation-workflows)
- [Claude Code Integration](#claude-code-integration)
- [Gas Town Workflow](#gas-town-workflow)
- [Best Practices](#best-practices)

## Overview

This project uses a multi-layered approach to code review:

1. **PR Templates** - Structured guidance for different change types
2. **Automated Validation** - Claude Code hooks for pre-review checks
3. **Manual Review** - Human review following guidelines
4. **Automated Checklists** - Context-aware checklist generation

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Developer Creates PR                                   │
│  ├─ Chooses appropriate template                        │
│  └─ Fills out PR description                           │
└───────────────┬─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────┐
│  Automated Checks (Claude Code Hooks)                   │
│  ├─ SQL syntax validation                               │
│  ├─ BigQuery dry run                                    │
│  ├─ Secret detection                                    │
│  ├─ Linting (sqlfluff, ruff, etc.)                     │
│  └─ Custom validations                                  │
└───────────────┬─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────┐
│  Automated Checklist Generation                         │
│  ├─ Analyzes changed files                              │
│  ├─ Generates contextual checklist                      │
│  └─ Suggests appropriate template                       │
└───────────────┬─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────┐
│  Manual Code Review                                     │
│  ├─ Reviewer uses review guidelines                     │
│  ├─ Applies comment templates                           │
│  └─ Approves or requests changes                        │
└───────────────┬─────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────┐
│  Merge & Deploy                                         │
│  └─ Branch cleanup via worktree management              │
└─────────────────────────────────────────────────────────┘
```

## GitHub Integration

### Setting Up PR Templates

PR templates are automatically discovered by GitHub when placed in:
- `.github/pull_request_template.md` (default template)
- `.github/PULL_REQUEST_TEMPLATE/` (multiple templates)

**No additional configuration needed** - GitHub will automatically use these templates.

### Using PR Templates

#### Method 1: URL Parameter (Recommended)
```bash
# Create PR with specific template
gh pr create --web

# In browser, add to URL:
?expand=1&template=feature.md
```

#### Method 2: GitHub CLI
```bash
# Not directly supported, but you can:
gh pr create --body-file .github/PULL_REQUEST_TEMPLATE/feature.md
```

#### Method 3: Web Interface
1. Go to "Pull Requests" → "New Pull Request"
2. Select your branch
3. Click template link in PR body
4. Fill out the template

### GitHub Actions Integration (Optional)

While this project uses Claude Code hooks for validation, you can add GitHub Actions for additional automation:

#### Example: PR Template Validator
```yaml
# .github/workflows/pr-template-check.yml
name: PR Template Check

on:
  pull_request:
    types: [opened, edited]

jobs:
  check-template:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check PR Description
        run: |
          if [ -z "${{ github.event.pull_request.body }}" ]; then
            echo "::error::PR description is empty. Please use a PR template."
            exit 1
          fi

          # Check for key sections
          if ! echo "${{ github.event.pull_request.body }}" | grep -q "## Description"; then
            echo "::warning::PR template may not have been used"
          fi
```

#### Example: Auto-Label by File Changes
```yaml
# .github/workflows/auto-label.yml
name: Auto Label PRs

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Label based on files
        uses: actions/labeler@v4
        with:
          repo-token: "${{ secrets.GITHUB_TOKEN }}"
          configuration-path: .github/labeler.yml
```

```yaml
# .github/labeler.yml
'data-model':
  - '**/*.sql'
  - '**/*.sqlx'
  - 'models/**/*'

'pipeline':
  - 'pipelines/**/*'
  - 'workflows/**/*'
  - 'airflow/**/*'

'documentation':
  - '**/*.md'
  - 'docs/**/*'

'python':
  - '**/*.py'
```

#### Example: Checklist Generation on PR Open
```yaml
# .github/workflows/generate-checklist.yml
name: Generate PR Checklist

on:
  pull_request:
    types: [opened]

jobs:
  checklist:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Generate Checklist
        run: |
          ./.github/scripts/generate-pr-checklist.sh ${{ github.base_ref }} > checklist.md

      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const checklist = fs.readFileSync('checklist.md', 'utf8');
            github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: checklist
            });
```

### GitHub CLI Aliases (Recommended)

Add these to your `~/.gitconfig`:

```ini
[alias]
    # Create PR with feature template
    pr-feature = !gh pr create --body-file .github/PULL_REQUEST_TEMPLATE/feature.md

    # Create PR with bug fix template
    pr-bug = !gh pr create --body-file .github/PULL_REQUEST_TEMPLATE/bugfix.md

    # Create PR with data model template
    pr-data = !gh pr create --body-file .github/PULL_REQUEST_TEMPLATE/data_model.md

    # Create PR with pipeline template
    pr-pipeline = !gh pr create --body-file .github/PULL_REQUEST_TEMPLATE/pipeline.md

    # Generate checklist for current branch
    pr-checklist = !./.github/scripts/generate-pr-checklist.sh main
```

Usage:
```bash
git pr-feature  # Creates PR with feature template
git pr-checklist  # Generates checklist for current changes
```

## GitLab Integration

### Setting Up Merge Request Templates

Create templates in `.gitlab/merge_request_templates/`:

```bash
mkdir -p .gitlab/merge_request_templates
cp .github/PULL_REQUEST_TEMPLATE/*.md .gitlab/merge_request_templates/
```

### Using MR Templates

#### Method 1: Web Interface
1. Go to "Merge Requests" → "New Merge Request"
2. Select "Choose a template" dropdown
3. Select appropriate template

#### Method 2: URL Parameter
```bash
# Create MR with specific template
https://gitlab.com/your-org/your-repo/-/merge_requests/new?merge_request[description_template]=feature
```

#### Method 3: GitLab CLI (glab)
```bash
glab mr create --template feature.md
```

### GitLab CI Integration (Optional)

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - review-prep

check-mr-template:
  stage: validate
  script:
    - |
      if [ -z "$CI_MERGE_REQUEST_DESCRIPTION" ]; then
        echo "MR description is empty. Please use an MR template."
        exit 1
      fi
  only:
    - merge_requests

generate-checklist:
  stage: review-prep
  script:
    - ./.github/scripts/generate-pr-checklist.sh $CI_MERGE_REQUEST_TARGET_BRANCH_NAME
  artifacts:
    reports:
      dotenv: checklist.env
  only:
    - merge_requests
```

## Automation Workflows

### Pre-PR Checklist Generation

Generate a contextual checklist before creating PR:

```bash
# Generate checklist for current branch
./.github/scripts/generate-pr-checklist.sh main

# Example output:
# ================================
# Generated PR Checklist
# ================================
#
# Detected change types:
#   - data_model
#   - documentation
#
# Recommended template:
#   .github/PULL_REQUEST_TEMPLATE/data_model.md
#
# Checklist items:
# - [ ] SQL syntax validated
# - [ ] BigQuery dry run successful
# ...
```

### Automated PR Creation (Gas Town)

For autonomous agents in Gas Town environment:

```bash
# In polecat workflow
gt mol status  # Check current work
bd show <bead-id>  # Understand the task

# Make changes...

# Before creating PR:
./.github/scripts/generate-pr-checklist.sh main

# Create PR using appropriate template
gh pr create --template data_model.md --fill
```

### Post-PR Automation

#### Automatic Reviewer Assignment

```yaml
# .github/CODEOWNERS
# Auto-assign reviewers based on file changes

*.sql @data-team
models/** @data-team
pipelines/** @platform-team
*.py @engineering-team
docs/** @docs-team
```

#### Automatic Labels

See [Auto-Label by File Changes](#example-auto-label-by-file-changes) above.

## Claude Code Integration

### Validation Hooks

Claude Code hooks run automatically on file changes. These hooks are configured in the project's Claude Code settings.

#### Current Hooks

See existing hooks in project configuration:
- SQL validation
- BigQuery dry run
- Secret detection
- Linting (sqlfluff)

#### Adding Custom Hooks

Example hook for PR template validation:

```yaml
# In Claude Code settings
hooks:
  pre-pr:
    - name: "Check PR Template Usage"
      command: ".github/scripts/validate-pr-template.sh"
      when: "pr-create"
```

### Checklist Validation

Some checklist items can be automatically validated:

```bash
# Example validation script
#!/bin/bash
# .github/scripts/validate-checklist.sh

# Check SQL validation
if ! sqlfluff lint **/*.sql; then
    echo "❌ SQL linting failed"
    exit 1
fi

# Check BigQuery dry run
if ! bq query --dry_run < query.sql; then
    echo "❌ BigQuery dry run failed"
    exit 1
fi

# Check for secrets
if git diff --cached | grep -i "password\|secret\|api_key"; then
    echo "❌ Potential secret detected"
    exit 1
fi

echo "✅ All validations passed"
```

## Gas Town Workflow

### Multi-Agent Collaboration

In Gas Town's multi-agent environment:

1. **Agent (Polecat) picks up work**
   ```bash
   gt hook  # Check for assigned work
   bd show <bead-id>  # Understand the task
   ```

2. **Agent makes changes**
   - Follows existing patterns
   - Runs validation hooks automatically
   - Uses appropriate templates

3. **Agent creates PR**
   ```bash
   # Generate checklist
   ./.github/scripts/generate-pr-checklist.sh main

   # Create PR with appropriate template
   gh pr create --template <template-name>.md
   ```

4. **Agent completes work**
   ```bash
   git add .
   bd sync
   git commit -m "..."
   bd sync
   git push
   ```

### Worktree Integration

PRs in multi-worktree environment:

```bash
# Check which worktrees have changes
gt worktree status

# Before creating PR, ensure no conflicts
git status

# After PR merged, cleanup
gt worktree cleanup-merged
```

### Bead Integration

Link PRs to beads for traceability:

```markdown
## Related Work

- Addresses: bd-123
- Related to: bd-456
- Blocks: bd-789
```

## Best Practices

### For PR Authors

1. **Choose the right template** - Use the template that matches your change type
2. **Fill out all sections** - Don't skip sections, they're there for a reason
3. **Run checklist generator** - Use automated checklist for context-aware items
4. **Self-review first** - Review your own code before requesting review
5. **Keep PRs focused** - One logical change per PR
6. **Update documentation** - Keep docs in sync with code

### For Reviewers

1. **Review promptly** - Aim for same-day reviews
2. **Use comment templates** - Standard templates for common feedback
3. **Be constructive** - Explain the "why" behind feedback
4. **Check automation results** - Review validation hook results
5. **Verify checklist** - Ensure checklist items are actually completed

### For Teams

1. **Standardize on templates** - Everyone uses the same templates
2. **Keep templates updated** - Templates evolve with team practices
3. **Document exceptions** - If skipping a section, explain why
4. **Measure and improve** - Track review metrics and improve process
5. **Train new members** - Onboard new team members to the process

## Troubleshooting

### Template Not Appearing

**GitHub:**
- Check template is in `.github/PULL_REQUEST_TEMPLATE/`
- Ensure file extension is `.md`
- Try hard refresh (Cmd+Shift+R / Ctrl+Shift+R)

**GitLab:**
- Check template is in `.gitlab/merge_request_templates/`
- Ensure file extension is `.md`
- Check repository settings

### Validation Hooks Not Running

1. Check Claude Code configuration
2. Verify hooks are enabled
3. Check hook script permissions
4. Review hook logs for errors

### Checklist Generator Not Working

```bash
# Make script executable
chmod +x .github/scripts/generate-pr-checklist.sh

# Test manually
./.github/scripts/generate-pr-checklist.sh main

# Check git is available
git --version

# Check you're in a git repository
git status
```

## Additional Resources

- [PR Templates](../.github/PULL_REQUEST_TEMPLATE/README.md)
- [Code Review Guidelines](code-review-guidelines.md)
- [Review Comment Templates](review-comment-templates.md)
- [Gas Town Documentation](../README.md)
- [Worktree Management](worktrees/README.md)

## Appendix: Template Quick Reference

| Change Type | Template | Key Sections |
|-------------|----------|--------------|
| General | `pull_request_template.md` | Description, Testing, Impact |
| Feature | `feature.md` | User Story, Implementation, Deployment |
| Bug Fix | `bugfix.md` | Root Cause, Solution, Prevention |
| Data Model | `data_model.md` | Schema, Quality, Downstream Impact |
| Pipeline | `pipeline.md` | Data Flow, Monitoring, Runbook |
| Documentation | `documentation.md` | Purpose, Accuracy, Completeness |
| Configuration | `config.md` | Security, Deployment, Rollback |

---

**Quick Start**:
```bash
# 1. Make changes
# 2. Generate checklist
./.github/scripts/generate-pr-checklist.sh main

# 3. Create PR with recommended template
gh pr create --template <recommended-template>.md
```
