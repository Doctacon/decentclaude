# DecentClaude Onboarding Checklist

Use this checklist to track your onboarding progress. Check off items as you complete them.

## Pre-Setup

- [ ] Read the main README.md
- [ ] Understand what DecentClaude does
- [ ] Have access to a Google Cloud project
- [ ] Have appropriate permissions (BigQuery Data Editor, Job User)

## Core Setup

### Tools Installation

- [ ] Python 3.7+ installed
- [ ] gcloud CLI installed
- [ ] Git installed
- [ ] Claude Code installed (optional but recommended)
- [ ] dbt installed (if using dbt)
- [ ] SQLMesh installed (if using SQLMesh)

### Authentication

- [ ] Logged in to gcloud: `gcloud auth login`
- [ ] Set GCP project: `gcloud config set project PROJECT_ID`
- [ ] Application default credentials configured: `gcloud auth application-default login`
- [ ] BigQuery access verified: `bq ls`

### Environment Configuration

- [ ] Created .env file
- [ ] Set GCP_PROJECT_ID environment variable
- [ ] Set BQ_DATASET environment variable
- [ ] Added .env to .gitignore

### dbt Configuration (if applicable)

- [ ] Created ~/.dbt directory
- [ ] Created profiles.yml
- [ ] Verified connection: `dbt debug`
- [ ] Can compile models: `dbt compile`

### Project Setup

- [ ] Cloned/forked repository
- [ ] Reviewed project structure
- [ ] Created CLAUDE.md from template
- [ ] Installed Python dependencies (if any)

## Learning Path

### Getting Started Tutorial

- [ ] Read tutorials/getting-started/README.md
- [ ] Completed Step 1: Project Structure
- [ ] Completed Step 2: Environment Setup
- [ ] Completed Step 3: First dbt Model
- [ ] Completed Step 4: Data Quality Checks
- [ ] Completed Exercise 1

### Knowledge Base Review

- [ ] Reviewed data-engineering-patterns.md
- [ ] Reviewed data-testing-patterns.md
- [ ] Reviewed playbooks.md
- [ ] Explored example SQL files

## First Real Task

### Create Your First Model

- [ ] Identified a data transformation need
- [ ] Created staging model
- [ ] Added tests in schema.yml
- [ ] Ran model: `dbt run --select model_name`
- [ ] Tested model: `dbt test --select model_name`
- [ ] Documented the model

### Data Quality

- [ ] Created custom data quality check
- [ ] Ran quality checks successfully
- [ ] Integrated with CI/CD (if applicable)

## Advanced Setup (Optional)

### CLI Utilities

- [ ] Tested bq-schema-diff utility
- [ ] Tested bq-query-cost utility
- [ ] Tested bq-partition-info utility
- [ ] Tested bq-lineage utility

### Git Worktrees (Multi-Agent)

- [ ] Understand worktree concept
- [ ] Tested wt-status utility
- [ ] Tested wt-switch utility
- [ ] Practiced worktree workflow

### Claude Code Integration

- [ ] Configured .claude/settings.json
- [ ] Tested hooks (if configured)
- [ ] Used Claude for model generation
- [ ] Used Claude for troubleshooting

## Validation

### Self-Assessment

- [ ] Can navigate the project structure
- [ ] Can create and test dbt models
- [ ] Can run BigQuery queries
- [ ] Can use CLI utilities
- [ ] Can troubleshoot common issues
- [ ] Understand data quality framework
- [ ] Know where to find documentation

### Practical Test

- [ ] Created a new staging model from scratch
- [ ] Added appropriate tests
- [ ] Verified data quality
- [ ] Documented the model
- [ ] Deployed to development environment

## Next Steps

### Choose Your Path

- [ ] **Junior Engineer**: Complete dbt Basics tutorial
- [ ] **Senior Engineer**: Complete Incident Response tutorial
- [ ] **Ops Focus**: Review playbooks deeply

### Take Assessment

- [ ] Completed dbt fundamentals quiz
- [ ] Completed BigQuery optimization quiz
- [ ] Ready for certification (if pursuing)

## Common Issues

If you're stuck on any item, check:

1. **Environment Issues**
   - Run: `bash onboarding/validation-scripts/verify-setup.sh`
   - Review: Setup log in /tmp/

2. **BigQuery Access**
   - Verify: `gcloud auth list`
   - Test: `bq query --use_legacy_sql=false "SELECT 1"`

3. **dbt Problems**
   - Debug: `dbt debug`
   - Check: ~/.dbt/profiles.yml

4. **General Questions**
   - Ask Claude Code for help
   - Review relevant section in knowledge base
   - Check troubleshooting guide

## Progress Tracking

Record your completion date for each section:

- Pre-Setup: _______________
- Core Setup: _______________
- Learning Path: _______________
- First Real Task: _______________
- Advanced Setup: _______________
- Validation: _______________

**Total Onboarding Time**: _______________

## Feedback

Help us improve the onboarding experience:

- What was most helpful? _______________
- What was confusing? _______________
- What's missing? _______________
- Suggestions: _______________

---

**Congratulations on completing your onboarding!** 🎉

You're now ready to contribute to data engineering with DecentClaude.
