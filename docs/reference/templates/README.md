# Documentation Templates

This directory contains templates for standardizing documentation across data engineering projects. These templates are designed to work seamlessly with Claude Code for AI-assisted development.

## Available Templates

### 1. `data-model.md` - Data Model Documentation

**Purpose**: Document individual data models, tables, views, or materialized views

**Use when:**
- Creating new dbt models
- Creating new SQLMesh models
- Documenting existing tables
- Defining schema for a dataset

**Key sections:**
- Model metadata (location, dependencies, materialization)
- Schema definition (columns, data types, constraints)
- Configuration (dbt/SQLMesh settings)
- Data quality tests
- Usage examples and query patterns
- Performance considerations
- Claude Code integration patterns

**Usage:**
```bash
# Copy template
cp docs/templates/data-model.md docs/models/[model_name].md

# Fill in the template with model-specific information
# Ask Claude: "Document the [model_name] model using the data model template"
```

### 2. `pipeline-runbook.md` - Pipeline Runbook

**Purpose**: Operational documentation for data pipelines

**Use when:**
- Creating new data pipelines
- Documenting ETL processes
- Setting up orchestrated workflows
- Defining production processes

**Key sections:**
- Quick reference (health checks, emergency contacts)
- Pipeline architecture and data flow
- Schedule and dependencies
- Execution procedures (normal, backfill, testing)
- Monitoring and alerting
- Troubleshooting common issues
- Disaster recovery procedures
- Claude Code workflows

**Usage:**
```bash
# Copy template
cp docs/templates/pipeline-runbook.md docs/runbooks/[pipeline_name]_runbook.md

# Fill in pipeline-specific details
# Ask Claude: "Create a runbook for [pipeline_name] using the template"
```

### 3. `troubleshooting-guide.md` - Troubleshooting Guide

**Purpose**: Document common problems and their solutions

**Use when:**
- Setting up a new component/system
- After resolving a complex incident
- Creating support documentation
- Building a knowledge base

**Key sections:**
- Quick diagnostics and health checks
- Diagnostic framework (5-step process)
- Common issues by category
- Escalation process
- Claude Code diagnostic workflows
- Post-incident review template

**Categories covered:**
- Data quality issues (duplicates, nulls, freshness)
- Performance problems (timeouts, high costs)
- Pipeline failures (dbt, SQLMesh, Airflow)
- Authentication/permissions

**Usage:**
```bash
# Copy template
cp docs/templates/troubleshooting-guide.md docs/troubleshooting/[component]_troubleshooting.md

# Customize with component-specific issues
# Ask Claude: "Add troubleshooting section for [specific issue]"
```

### 4. `CLAUDE.md.template` - Claude Code Instructions

**Purpose**: Project-wide instructions for Claude Code

**Use when:**
- Setting up a new project
- Onboarding Claude Code to your codebase
- Defining project-specific workflows
- Establishing coding standards

**Key sections:**
- Project overview and structure
- Environment setup
- Common task workflows (create model, optimize query, debug, etc.)
- Code standards and best practices
- Testing strategy
- Git hooks integration
- Deployment process
- Monitoring and alerts
- Common gotchas and solutions
- Specific instructions for Claude

**Usage:**
```bash
# Copy template to project root
cp docs/templates/CLAUDE.md.template CLAUDE.md

# Customize for your project
# This file provides Claude with context about:
# - How your project is structured
# - What conventions to follow
# - How to handle common tasks
# - Project-specific gotchas
```

## Template Usage Best Practices

### 1. Start with the Template

Don't start from scratch. Copy the relevant template and fill in your specific information.

```bash
# Good approach
cp docs/templates/data-model.md docs/models/user_events.md
# Then customize

# Bad approach
touch docs/models/user_events.md
# Starting from scratch loses structure and consistency
```

### 2. Keep Templates Updated

As you discover new patterns or common issues, update the templates:

```bash
# Update template with new learnings
# Add new sections that proved valuable
# Remove sections that aren't useful
# Submit improvements back to the team
```

### 3. Use Claude Code for Template Filling

Claude Code can help populate templates automatically:

```bash
# Example prompts:
"Document the user_events model using the data model template"
"Create a runbook for the daily_aggregation pipeline"
"Add troubleshooting section for BigQuery timeouts"
"Generate CLAUDE.md for this project"
```

### 4. Maintain Documentation Alongside Code

Documentation should live with code and be updated together:

```bash
# When creating a new model
1. Create model SQL file
2. Add schema.yml entry
3. Create model documentation from template
4. Commit all together

# Good commit
git add models/marts/user_events.sql
git add models/marts/schema.yml
git add docs/models/user_events.md
git commit -m "Add user_events model with documentation"
```

### 5. Link Related Documentation

Create a web of documentation:

```markdown
## References
- [User Events Model Documentation](../models/user_events.md)
- [Daily Aggregation Runbook](../runbooks/daily_aggregation.md)
- [BigQuery Troubleshooting](../troubleshooting/bigquery.md)
```

## Documentation Standards

### Markdown Formatting

**Follow these conventions:**

1. **Headers**: Use ATX-style headers (`#` not underlines)
   ```markdown
   # H1 for title
   ## H2 for main sections
   ### H3 for subsections
   ```

2. **Code blocks**: Always specify language
   ```markdown
   ```sql
   SELECT * FROM table;
   ```

   ```bash
   dbt run
   ```
   ```

3. **Tables**: Use proper alignment
   ```markdown
   | Column | Type | Description |
   |--------|------|-------------|
   | id     | INT  | Primary key |
   ```

4. **Links**: Use descriptive text
   ```markdown
   [Data Model Documentation](../models/user_events.md)  # Good
   [Link](../models/user_events.md)                      # Bad
   ```

### Keep It Current

**Documentation rots quickly. Prevent it:**

1. **Date everything**: Include "Last Updated" at the top
2. **Review regularly**: Set reminders to review docs quarterly
3. **Update during changes**: When code changes, update docs
4. **Archive outdated docs**: Move old docs to archive/ folder

### Make It Searchable

**Help people find information:**

1. **Use consistent naming**: `[entity]_[type].md`
2. **Add keywords**: Include common search terms
3. **Link liberally**: Connect related documentation
4. **Create index**: Maintain a main index of all docs

## Common Documentation Patterns

### Pattern: Progressive Disclosure

Start with quick reference, then add detail:

```markdown
## Quick Reference
[Commands and links for immediate action]

## Overview
[Brief explanation]

## Detailed Guide
[Comprehensive information]
```

### Pattern: Example-Driven

Show examples before explaining:

```markdown
## Usage Example

```sql
-- Example query
SELECT * FROM table;
```

## Explanation
[Now explain what the example does]
```

### Pattern: Runbook Format

Actionable, step-by-step instructions:

```markdown
## Task: Deploy to Production

1. **Verify tests pass**
   ```bash
   dbt test
   ```

2. **Deploy to staging**
   ```bash
   dbt run --target staging
   ```

3. **Validate staging**
   [Validation steps]

4. **Deploy to production**
   [Production steps]
```

## Integration with Claude Code

### Template Auto-Fill

Ask Claude to populate templates:

```
"Using the data model template, document the user_events table in BigQuery"

Claude will:
1. Read the template
2. Inspect the table schema
3. Analyze the model SQL
4. Fill in the template with accurate information
5. Save to the appropriate location
```

### Documentation Generation

Generate docs from code:

```
"Generate documentation for all models in marts/"

Claude will:
1. Scan all models in marts/
2. Create a doc for each using the template
3. Link them together
4. Create an index
```

### Documentation Review

Ask Claude to review docs:

```
"Review the user_events documentation for completeness"

Claude will:
1. Check if all template sections are filled
2. Verify examples are accurate
3. Test that commands work
4. Suggest improvements
```

### Documentation Updates

Keep docs in sync with code:

```
"Update the user_events documentation to reflect the recent schema changes"

Claude will:
1. Compare current code to docs
2. Identify discrepancies
3. Update documentation
4. Flag breaking changes
```

## Template Customization

### For Your Team

Customize templates to match your team's needs:

1. **Add sections** specific to your workflow
2. **Remove sections** that aren't applicable
3. **Adjust formatting** to match your style guide
4. **Add team-specific** tools and processes

### For Your Tech Stack

Adapt templates for your technologies:

```markdown
# If using Snowflake instead of BigQuery
Replace:
- BigQuery-specific SQL
- BigQuery cost calculations
- GCP commands

With:
- Snowflake SQL
- Snowflake credit calculations
- Snowflake commands
```

### For Your Domain

Add domain-specific sections:

```markdown
# For financial data pipelines, add:
- Compliance requirements
- Audit trail
- PII handling
- Reconciliation procedures

# For ML pipelines, add:
- Feature definitions
- Model performance metrics
- Retraining schedule
- Drift detection
```

## Examples

### Example: Documenting a New Model

```bash
# 1. Copy template
cp docs/templates/data-model.md docs/models/fct_orders.md

# 2. Ask Claude to fill it in
# "Document fct_orders using the data model template"

# 3. Review and customize
# Add any project-specific context

# 4. Commit with model
git add models/marts/fct_orders.sql
git add models/marts/schema.yml
git add docs/models/fct_orders.md
git commit -m "Add fct_orders model with documentation"
```

### Example: Creating a Pipeline Runbook

```bash
# 1. Copy template
cp docs/templates/pipeline-runbook.md docs/runbooks/daily_orders_pipeline.md

# 2. Ask Claude for help
# "Create a runbook for the daily_orders pipeline that:
#  - Runs daily at 3am UTC
#  - Processes yesterday's orders
#  - Loads to fct_orders and dim_customers
#  - Alerts #data-eng on failure"

# 3. Claude fills in the template with your specifics

# 4. Add operational details
# - Emergency contacts
# - Known issues
# - Recent incidents

# 5. Share with team
# Link from main documentation index
```

### Example: Building Troubleshooting Guide

```bash
# 1. Start with template
cp docs/templates/troubleshooting-guide.md docs/troubleshooting/dbt_common_issues.md

# 2. After resolving an incident, document it
# "Add troubleshooting section for the dbt compilation error we just fixed"

# 3. Claude adds:
# - Symptoms
# - Diagnosis steps
# - Resolution
# - Prevention measures

# 4. Over time, build comprehensive guide
# Each incident adds to the knowledge base
```

## Maintenance

### Regular Reviews

**Quarterly documentation review:**

```bash
# Check for outdated information
find docs/ -name "*.md" -mtime +90

# Review and update
# - Verify commands still work
# - Update screenshots/examples
# - Archive obsolete docs
# - Update "Last Updated" dates
```

### Documentation Metrics

**Track documentation health:**

- Coverage: % of models with documentation
- Freshness: Average age of documentation
- Usage: Which docs are accessed most
- Quality: Completeness of template sections

### Continuous Improvement

**Improve templates based on usage:**

1. **Collect feedback**: What sections are most/least useful?
2. **Analyze patterns**: What gets added to every doc?
3. **Update templates**: Add common patterns
4. **Share learnings**: Contribute improvements back

## Getting Help

### Using These Templates

**Ask Claude:**
- "How do I use the data model template?"
- "Generate documentation using the pipeline runbook template"
- "What template should I use for documenting this?"

### Improving Templates

**Submit improvements:**
1. Update the template
2. Document the change
3. Share with the team
4. Update this README

### Questions and Issues

**Contact:**
- [Team channel]
- [Documentation owner]
- [Project repository issues]

## Additional Resources

### Internal

- [Data Engineering Patterns](../../data-engineering-patterns.md)
- [Style Guide](../style-guide.md) (if exists)
- [Team Wiki](link)

### External

- [Writing Better Documentation](https://www.divio.com/blog/documentation/)
- [Markdown Guide](https://www.markdownguide.org/)
- [Technical Writing Best Practices](https://google.github.io/styleguide/docguide/)

---

**Last Updated**: [YYYY-MM-DD]
**Template Version**: 1.0
**Maintainer**: [Team/Individual]
