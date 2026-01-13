# Code Review Infrastructure

> **Complete guide** to the code review process, PR templates, and automation tools

## Quick Start

### Creating a Pull Request

1. **Generate a checklist** for your changes:
   ```bash
   ./.github/scripts/generate-pr-checklist.sh main
   ```

2. **Choose the appropriate template** based on your change type:
   - 🚀 **Feature**: `.github/PULL_REQUEST_TEMPLATE/feature.md`
   - 🐛 **Bug Fix**: `.github/PULL_REQUEST_TEMPLATE/bugfix.md`
   - 📊 **Data Model**: `.github/PULL_REQUEST_TEMPLATE/data_model.md`
   - ⚙️ **Pipeline**: `.github/PULL_REQUEST_TEMPLATE/pipeline.md`
   - 📚 **Documentation**: `.github/PULL_REQUEST_TEMPLATE/documentation.md`
   - 🔧 **Configuration**: `.github/PULL_REQUEST_TEMPLATE/config.md`

3. **Create the PR**:
   ```bash
   gh pr create --template feature.md  # Replace with your template
   ```

### Reviewing a Pull Request

1. **Read the review guidelines**: [code-review-guidelines.md](code-review-guidelines.md)
2. **Use comment templates**: [review-comment-templates.md](review-comment-templates.md)
3. **Check automated validations**: Ensure Claude Code hooks pass
4. **Review thoroughly**: Follow the appropriate review checklist

## What's Included

### 📝 PR Templates

Six specialized templates for different change types:

| Template | Use Case | Key Features |
|----------|----------|--------------|
| [Default](../.github/pull_request_template.md) | General changes | Basic checklist, impact assessment |
| [Feature](../.github/PULL_REQUEST_TEMPLATE/feature.md) | New functionality | User story, deployment notes, testing |
| [Bug Fix](../.github/PULL_REQUEST_TEMPLATE/bugfix.md) | Bug fixes | Root cause analysis, prevention steps |
| [Data Model](../.github/PULL_REQUEST_TEMPLATE/data_model.md) | SQL/dbt/SQLMesh | Schema changes, data quality, cost |
| [Pipeline](../.github/PULL_REQUEST_TEMPLATE/pipeline.md) | Workflows | Monitoring, runbook, error handling |
| [Documentation](../.github/PULL_REQUEST_TEMPLATE/documentation.md) | Docs only | Accuracy, completeness checks |
| [Configuration](../.github/PULL_REQUEST_TEMPLATE/config.md) | Config/infra | Security, deployment, rollback |

**Location**: `.github/PULL_REQUEST_TEMPLATE/`

**Documentation**: [PR Template README](../.github/PULL_REQUEST_TEMPLATE/README.md)

### 🤖 Automated Checklist Generation

Smart script that analyzes your changes and generates a contextual checklist:

```bash
./.github/scripts/generate-pr-checklist.sh [base-branch]
```

**Features**:
- Detects change types (SQL, Python, docs, config, etc.)
- Recommends appropriate PR template
- Generates relevant checklist items
- Integrates with Claude Code validation hooks

**Example Output**:
```
Detected change types:
  - data_model
  - documentation

Recommended template:
  .github/PULL_REQUEST_TEMPLATE/data_model.md

Checklist items:
- [ ] SQL syntax validated
- [ ] BigQuery dry run successful
- [ ] Data model documentation updated
- [ ] Documentation reviewed for accuracy
```

### 📖 Code Review Guidelines

Comprehensive guidelines for effective code reviews:

**[Code Review Guidelines](code-review-guidelines.md)**

Covers:
- Review principles and responsibilities
- What to look for in reviews
- Review process and timelines
- Approval criteria
- Handling disagreements
- Gas Town specific considerations

### 💬 Review Comment Templates

Pre-written templates for common review feedback:

**[Review Comment Templates](review-comment-templates.md)**

Categories:
- General feedback (questions, suggestions, blocking issues)
- Code quality (complexity, naming, duplication)
- Security (secrets, injection, auth)
- Performance (N+1 queries, BigQuery optimization)
- Testing (missing tests, quality, flaky tests)
- Data engineering (quality, schema, cost)
- Documentation (missing, outdated, examples)
- Positive feedback (good patterns, learning)

### 🔄 Workflow Integration

Complete integration guide for GitHub and GitLab:

**[PR Workflow Integration](pr-workflow-integration.md)**

Covers:
- GitHub integration and automation
- GitLab merge request templates
- Claude Code hook integration
- Gas Town multi-agent workflows
- Best practices for teams

## File Structure

```
.
├── .github/
│   ├── pull_request_template.md          # Default PR template
│   ├── PULL_REQUEST_TEMPLATE/
│   │   ├── README.md                     # Template usage guide
│   │   ├── feature.md                    # Feature template
│   │   ├── bugfix.md                     # Bug fix template
│   │   ├── data_model.md                 # Data model template
│   │   ├── pipeline.md                   # Pipeline template
│   │   ├── documentation.md              # Documentation template
│   │   └── config.md                     # Configuration template
│   └── scripts/
│       └── generate-pr-checklist.sh      # Automated checklist generator
│
└── docs/
    ├── CODE_REVIEW_README.md             # This file
    ├── code-review-guidelines.md         # Review guidelines
    ├── review-comment-templates.md       # Comment templates
    └── pr-workflow-integration.md        # Integration guide
```

## Common Workflows

### Workflow 1: Creating a Feature PR

```bash
# 1. Make your changes
# (edit files, write tests, etc.)

# 2. Generate checklist to see what template to use
./.github/scripts/generate-pr-checklist.sh main

# Output suggests: .github/PULL_REQUEST_TEMPLATE/feature.md

# 3. Create PR with feature template
gh pr create --template feature.md

# 4. Fill out template sections
#    - User story
#    - Implementation details
#    - Testing
#    - Documentation
#    - etc.

# 5. Submit PR for review
```

### Workflow 2: Data Model Change

```bash
# 1. Create/modify SQL files
# (make changes to models, schema, etc.)

# 2. Run validation locally
sqlfluff lint models/**/*.sql
bq query --dry_run < models/my_model.sql

# 3. Generate checklist
./.github/scripts/generate-pr-checklist.sh main

# Output suggests: .github/PULL_REQUEST_TEMPLATE/data_model.md

# 4. Document the data model
# (use docs/templates/data-model.md template)

# 5. Create PR with data model template
gh pr create --template data_model.md

# 6. Fill out:
#    - Business context
#    - Schema changes
#    - Data quality tests
#    - Cost estimates
#    - Downstream impacts
```

### Workflow 3: Quick Bug Fix

```bash
# 1. Fix the bug
# (make minimal changes to fix issue)

# 2. Add regression test
# (prevent bug from happening again)

# 3. Generate checklist
./.github/scripts/generate-pr-checklist.sh main

# Output suggests: .github/PULL_REQUEST_TEMPLATE/bugfix.md

# 4. Create PR with bug fix template
gh pr create --template bugfix.md

# 5. Fill out:
#    - Bug description
#    - Root cause
#    - Solution
#    - Prevention measures
```

### Workflow 4: Reviewing a PR

```bash
# 1. Check out the PR
gh pr checkout <pr-number>

# 2. Review the code
#    - Read PR description
#    - Check that template was filled out
#    - Review code changes

# 3. Test locally (if needed)
#    - Run tests
#    - Test manually
#    - Check BigQuery queries

# 4. Leave feedback
#    - Use comment templates from docs/review-comment-templates.md
#    - Be specific and constructive
#    - Link to guidelines or docs

# 5. Approve or request changes
gh pr review --approve  # or --request-changes
```

## Integration with Existing Tools

### Claude Code Hooks

The code review infrastructure integrates with existing Claude Code validation hooks:

✅ **Automated Checks** (run before review):
- SQL syntax validation
- BigQuery dry run
- Secret detection
- SQL linting (sqlfluff)
- dbt/SQLMesh validation

📝 **Manual Checks** (done during review):
- Code logic and design
- Test quality
- Documentation accuracy
- Impact assessment

### Worktree Management

Works seamlessly with Gas Town's worktree system:

```bash
# Before creating PR
gt worktree status  # Check for conflicts

# After PR merged
gt worktree cleanup-merged  # Cleanup merged branches
```

### Beads Integration

Link PRs to beads for work tracking:

```markdown
## Related Work
- Addresses: bd-aqi
- Related to: bd-123
- Blocks: bd-456
```

## Customization

### Adding a New Template

1. Create template file:
   ```bash
   touch .github/PULL_REQUEST_TEMPLATE/my_template.md
   ```

2. Follow structure of existing templates

3. Update `.github/PULL_REQUEST_TEMPLATE/README.md` with new template

4. Add detection logic to `generate-pr-checklist.sh` (optional)

### Customizing Checklist Generator

Edit `.github/scripts/generate-pr-checklist.sh`:

```bash
# Add new file pattern detection
if echo "$CHANGED_FILES" | grep -qE 'pattern'; then
    add_type "custom_type"
    add_checklist "Custom checklist item"
    echo "Detected: Custom changes"
fi
```

### Customizing Comment Templates

Edit `docs/review-comment-templates.md` to add project-specific templates.

## Best Practices

### For Authors

✅ **DO**:
- Use the appropriate template
- Fill out all sections (don't skip)
- Run the checklist generator
- Self-review before requesting review
- Link to related beads/issues
- Keep PRs focused and small

❌ **DON'T**:
- Create PRs without templates
- Skip validation hooks
- Request review with failing checks
- Create giant PRs (>1000 lines)
- Mix unrelated changes

### For Reviewers

✅ **DO**:
- Review within 1 business day
- Use comment templates for consistency
- Explain the "why" behind feedback
- Check automated validation results
- Be constructive and helpful
- Leave positive feedback too

❌ **DON'T**:
- Nitpick formatting (use automation)
- Request changes without explanation
- Review code you don't understand
- Skip the checklist verification

### For Teams

✅ **DO**:
- Standardize on these templates
- Keep templates up to date
- Train new team members
- Measure and improve process
- Share knowledge through reviews

❌ **DON'T**:
- Skip templates for "small" changes
- Ignore the guidelines
- Approve without proper review
- Rush reviews

## Troubleshooting

### Template Not Loading

**Issue**: PR template doesn't appear in GitHub

**Solutions**:
1. Check file is in `.github/PULL_REQUEST_TEMPLATE/`
2. Ensure `.md` extension
3. Hard refresh browser
4. Use URL parameter: `?expand=1&template=feature.md`

### Checklist Generator Fails

**Issue**: Script doesn't run or produces errors

**Solutions**:
```bash
# Make executable
chmod +x .github/scripts/generate-pr-checklist.sh

# Check git is working
git status

# Run with debug
bash -x .github/scripts/generate-pr-checklist.sh main
```

### Validation Hooks Not Running

**Issue**: Claude Code hooks don't run

**Solutions**:
1. Check Claude Code configuration
2. Verify hooks are enabled
3. Check script permissions
4. Review hook logs

## Metrics and Improvement

Track these metrics to improve your review process:

- ⏱️ **Time to first review**: How long until first reviewer responds
- 🔄 **Review cycles**: Number of back-and-forth rounds
- 🐛 **Issues found in review vs production**: Quality indicator
- 📊 **PR size distribution**: Are PRs appropriately sized?
- ✅ **Template usage**: Are teams using templates?
- 💬 **Comment quality**: Are reviews constructive?

## Additional Resources

### Documentation
- [Build Documentation Standards](BUILD.md)
- [Data Engineering Patterns](data-engineering-patterns.md)
- [Data Testing Patterns](data-testing-patterns.md)
- [Playbooks](playbooks.md)
- [Worktree Management](worktrees/README.md)

### Templates
- [Data Model Template](templates/data-model.md)
- [Pipeline Runbook Template](templates/pipeline-runbook.md)
- [Troubleshooting Guide Template](templates/troubleshooting-guide.md)

### External Resources
- [GitHub PR Best Practices](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests)
- [GitLab MR Guidelines](https://docs.gitlab.com/ee/user/project/merge_requests/)
- [Code Review Best Practices](https://google.github.io/eng-practices/review/)

## Support

### Getting Help

- **Questions**: Ask in team chat or create an issue
- **Bugs**: Report in project issues
- **Improvements**: Submit a PR with your suggestions

### Contributing

To improve this code review infrastructure:

1. Make your changes
2. Test with your team
3. Create a PR using the documentation template
4. Link to the improvement bead (if exists)

---

**Quick Command Reference**:
```bash
# Generate checklist
./.github/scripts/generate-pr-checklist.sh main

# Create PR with template
gh pr create --template <template-name>.md

# Review a PR
gh pr checkout <pr-number>
gh pr review --approve

# Cleanup after merge
gt worktree cleanup-merged
```

**Remember**: Great code reviews improve code quality, share knowledge, and build better teams. Use these tools to make reviews more effective and efficient!
