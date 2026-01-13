# CI/CD Quick Reference

Fast lookup guide for DecentClaude CI/CD workflows.

## Quick Setup

```bash
# Run the setup wizard
.github/workflows/examples/setup.sh

# Or copy workflows manually
cp .github/workflows/examples/sql-validation.yml .github/workflows/
cp .github/workflows/examples/bq-cost-check.yml .github/workflows/
```

## Secrets Quick Setup

### GitHub Secrets

| Secret Name | Used By | How to Get |
|------------|---------|------------|
| `ANTHROPIC_API_KEY` | ai-review | https://console.anthropic.com/settings/keys |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | bq-cost-check, schema-validation | See GCP setup below |
| `GCP_PROJECT_ID` | bq-cost-check, schema-validation | Your GCP project ID |

### GCP One-Liner

```bash
# Create service account and generate key (all in one)
PROJECT_ID="your-project-id" && \
gcloud iam service-accounts create data-ci --project=$PROJECT_ID && \
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:data-ci@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser" && \
gcloud iam service-accounts keys create key.json \
  --iam-account=data-ci@${PROJECT_ID}.iam.gserviceaccount.com && \
base64 key.json && \
echo "☝️ Add this to GOOGLE_APPLICATION_CREDENTIALS_JSON" && \
rm key.json
```

## Workflow Cheat Sheet

### SQL Validation
- **Trigger**: PR with `.sql` changes
- **Duration**: ~30s
- **Fails on**: Syntax errors, hardcoded secrets
- **Secrets**: None

### BigQuery Cost Check
- **Trigger**: PR with `.sql` changes
- **Duration**: ~1-2min
- **Fails on**: Cost > threshold (default 100GB)
- **Secrets**: GCP credentials
- **Customize**: Edit `COST_THRESHOLD_GB` in workflow

### Schema Validation
- **Trigger**: PR affecting models/schemas
- **Duration**: ~2-3min
- **Fails on**: Breaking schema changes
- **Secrets**: GCP credentials
- **Bypass**: Add `skip-schema-check` label to PR

### AI Code Review
- **Trigger**: PR with SQL changes
- **Duration**: ~2-4min
- **Fails on**: Never (informational only)
- **Secrets**: Anthropic API key
- **Customize**: Edit `MAX_FILES_TO_REVIEW` to reduce API costs

### Data Quality Audit
- **Trigger**: Push to main, daily schedule
- **Duration**: ~5-10min
- **Fails on**: Syntax errors, security issues
- **Secrets**: None (optional GCP)
- **Manual run**: Actions > Data Quality Audit > Run workflow

## Common Customizations

### Change Cost Threshold

```yaml
# In bq-cost-check.yml
env:
  COST_THRESHOLD_GB: 500  # Change from 100 to 500
```

### Change Schedule

```yaml
# In data-quality.yml
schedule:
  - cron: '0 14 * * *'  # Run at 2 PM UTC instead of 8 AM
```

### Limit Files for AI Review

```yaml
# In ai-review.yml
env:
  MAX_FILES_TO_REVIEW: 5  # Review only 5 files to reduce API costs
```

### Skip Workflow for Draft PRs

```yaml
# Add to any workflow
jobs:
  your-job:
    if: github.event.pull_request.draft == false
```

### Different Thresholds by Branch

```yaml
# Higher threshold for dev branches
env:
  COST_THRESHOLD_GB: ${{ github.base_ref == 'main' && 100 || 500 }}
```

## Troubleshooting Quick Fixes

### "Resource not accessible by integration"

Add to workflow:
```yaml
permissions:
  pull-requests: write
  issues: write
```

### Service Account Auth Failed

```bash
# Check permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:*"

# Re-create key
gcloud iam service-accounts keys create key.json \
  --iam-account=data-ci@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### Workflow Runs Too Often

Add path filters:
```yaml
on:
  pull_request:
    paths:
      - 'models/**'
      - '**.sql'
```

### Cost Check Always Passes

Verify dry run is enabled:
```python
job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
```

## Testing Workflows

### Test Locally with act

```bash
# Install
brew install act

# Test workflow
act pull_request -j validate-sql

# With secrets
act pull_request -j cost-check \
  -s GCP_PROJECT_ID="your-project" \
  -s GOOGLE_APPLICATION_CREDENTIALS_JSON="$(cat key.json.b64)"
```

### Manual Trigger

```bash
# Using GitHub CLI
gh workflow run data-quality.yml

# In browser
Actions > [Workflow Name] > Run workflow
```

## Cost Optimization

### Reduce AI Review Costs

```yaml
env:
  MAX_FILES_TO_REVIEW: 3  # Review fewer files
  CLAUDE_MODEL: claude-haiku-3-5-20250129  # Use cheaper model
```

### Cache Dependencies

```yaml
- uses: actions/setup-python@v5
  with:
    cache: 'pip'  # Cache pip packages
```

### Skip Redundant Runs

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## Common Commands

```bash
# Check workflow status
gh run list --workflow=sql-validation.yml

# View workflow run
gh run view 12345678

# Re-run failed jobs
gh run rerun 12345678

# Download artifacts
gh run download 12345678

# Add secret
gh secret set ANTHROPIC_API_KEY

# List secrets
gh secret list
```

## Best Practices

1. ✅ Start with `sql-validation.yml` only
2. ✅ Set appropriate cost thresholds for your use case
3. ✅ Use caching to speed up workflows
4. ✅ Add status badges to README
5. ✅ Monitor workflow duration and optimize
6. ✅ Use matrix builds for multiple environments
7. ✅ Keep secrets minimal and rotate regularly
8. ✅ Document custom configurations for your team

## Status Badges

Add to your README.md:

```markdown
![SQL Validation](https://github.com/user/repo/actions/workflows/sql-validation.yml/badge.svg)
![Cost Check](https://github.com/user/repo/actions/workflows/bq-cost-check.yml/badge.svg)
![Data Quality](https://github.com/user/repo/actions/workflows/data-quality.yml/badge.svg)
```

## File Locations

- **Main guide**: `docs/guides/cicd-integration.md`
- **Examples**: `.github/workflows/examples/`
- **Your workflows**: `.github/workflows/`

## Getting Help

- 📖 Full documentation: `docs/guides/cicd-integration.md`
- 📋 Examples README: `.github/workflows/examples/README.md`
- 🔧 GitHub Actions: https://docs.github.com/en/actions
- ☁️ BigQuery API: https://cloud.google.com/bigquery/docs
- 🤖 Anthropic API: https://docs.anthropic.com

---

**Last Updated**: 2026-01-13
