# Pull Request Templates

This directory contains PR templates for different types of changes. Choose the template that best matches your PR:

## Available Templates

| Template | When to Use | Link |
|----------|-------------|------|
| **Default** | General changes that don't fit other categories | [Use default template](../pull_request_template.md) |
| **Feature** | Adding new functionality or capabilities | [Use feature template](?expand=1&template=feature.md) |
| **Bug Fix** | Fixing bugs or issues | [Use bugfix template](?expand=1&template=bugfix.md) |
| **Data Model** | Adding or modifying data models (dbt, SQLMesh, SQL) | [Use data model template](?expand=1&template=data_model.md) |
| **Pipeline** | Adding or modifying pipelines and workflows | [Use pipeline template](?expand=1&template=pipeline.md) |
| **Documentation** | Documentation-only changes | [Use documentation template](?expand=1&template=documentation.md) |
| **Configuration** | Configuration or infrastructure changes | [Use config template](?expand=1&template=config.md) |

## How to Use

### Option 1: Via URL Parameter (GitHub)
Add `?expand=1&template=TEMPLATE_NAME.md` to your PR URL. For example:
```
https://github.com/your-org/your-repo/compare/main...your-branch?expand=1&template=feature.md
```

### Option 2: Manual Selection
1. Click "New Pull Request"
2. Click "Preview" tab
3. Click the template link above that matches your change type
4. Fill out the template

### Option 3: CLI/gh
```bash
# Using GitHub CLI
gh pr create --template feature.md
```

## Template Selection Guide

**Not sure which template to use?** Ask yourself:

1. **Am I adding new functionality?** → Feature template
2. **Am I fixing a bug?** → Bug Fix template
3. **Am I changing SQL models or schemas?** → Data Model template
4. **Am I changing pipelines or workflows?** → Pipeline template
5. **Am I only updating documentation?** → Documentation template
6. **Am I changing configuration or infrastructure?** → Configuration template
7. **None of the above?** → Default template

## Tips for Great PRs

- **Keep PRs focused** - One logical change per PR
- **Fill out all sections** - Help reviewers understand your changes
- **Test thoroughly** - Use the testing checklist
- **Check the impact** - Consider downstream effects
- **Update documentation** - Keep docs in sync with code
- **Run validation hooks** - Ensure all checks pass before requesting review

## Automated Checklists

Some checklist items are automatically validated by Claude Code hooks:

- SQL syntax validation
- BigQuery query validation
- Secret detection
- SQL linting (sqlfluff)
- dbt/SQLMesh validation

Make sure these hooks pass before requesting review.

## Review Guidelines

See [Code Review Guidelines](../docs/code-review-guidelines.md) for detailed review expectations and best practices.
