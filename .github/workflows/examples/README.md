# GitHub Actions Workflow Examples

Ready-to-use GitHub Actions workflows for data engineering CI/CD pipelines using DecentClaude utilities.

## Quick Start

1. **Copy workflows you need** to `.github/workflows/`:
   ```bash
   cp .github/workflows/examples/sql-validation.yml .github/workflows/
   cp .github/workflows/examples/bq-cost-check.yml .github/workflows/
   ```

2. **Set up required secrets** in GitHub repository settings:
   - Go to Settings > Secrets and variables > Actions
   - Add secrets (see table below)

3. **Customize** workflows for your project:
   - Update dataset names
   - Adjust thresholds
   - Modify file paths

4. **Test** by creating a PR with SQL changes

## Available Workflows

### 1. SQL Validation (`sql-validation.yml`)

**Purpose**: Validates SQL syntax and checks for common issues on every PR

**Runs on**: Pull requests that change `.sql` files

**Duration**: ~30 seconds

**Required Secrets**: None (optional: SLACK_WEBHOOK for notifications)

**What it does**:
- Validates SQL syntax with sqlparse
- Lints SQL with sqlfluff
- Checks for hardcoded secrets
- Posts results as PR comment

**Setup**:
```bash
cp .github/workflows/examples/sql-validation.yml .github/workflows/
# No additional configuration needed!
```

---

### 2. BigQuery Cost Check (`bq-cost-check.yml`)

**Purpose**: Estimates query costs and blocks PRs exceeding threshold

**Runs on**: Pull requests that change `.sql` files

**Duration**: ~1-2 minutes

**Required Secrets**:
- `GOOGLE_APPLICATION_CREDENTIALS_JSON` - GCP service account JSON (base64)
- `GCP_PROJECT_ID` - Your Google Cloud project ID

**Environment Variables**:
- `COST_THRESHOLD_GB` - Maximum GB to scan (default: 100)
- `COST_PER_TB` - BigQuery pricing (default: $5.00/TB)

**What it does**:
- Estimates data processed by each query
- Calculates cost per query and total
- Fails if total exceeds threshold
- Posts detailed cost breakdown as PR comment

**Setup**:
```bash
# 1. Copy workflow
cp .github/workflows/examples/bq-cost-check.yml .github/workflows/

# 2. Create service account (see below)
gcloud iam service-accounts create data-ci \
  --display-name="Data CI/CD"

# 3. Grant permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:data-ci@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"

# 4. Create and encode key
gcloud iam service-accounts keys create key.json \
  --iam-account=data-ci@YOUR_PROJECT_ID.iam.gserviceaccount.com
cat key.json | base64 > key.json.b64

# 5. Add to GitHub Secrets:
#    - GOOGLE_APPLICATION_CREDENTIALS_JSON: (paste content of key.json.b64)
#    - GCP_PROJECT_ID: your-project-id

# 6. Delete local key files
rm key.json key.json.b64
```

**Customization**:
```yaml
env:
  COST_THRESHOLD_GB: 500  # Increase threshold to 500GB
  COST_PER_TB: 6.25       # Update for reserved pricing
```

---

### 3. Schema Validation (`schema-validation.yml`)

**Purpose**: Detects breaking schema changes between environments

**Runs on**: Pull requests affecting model/schema files

**Duration**: ~2-3 minutes

**Required Secrets**:
- `GOOGLE_APPLICATION_CREDENTIALS_JSON`
- `GCP_PROJECT_ID`

**Environment Variables**:
- `STAGING_DATASET` - Staging dataset name (default: staging)
- `PRODUCTION_DATASET` - Production dataset name (default: production)

**What it does**:
- Compares schemas between staging and production
- Identifies added, removed, and modified columns
- Flags breaking changes (removed fields, type changes)
- Posts schema diff as PR comment
- Fails on breaking changes (can skip with label)

**Setup**:
```bash
# 1. Copy workflow
cp .github/workflows/examples/schema-validation.yml .github/workflows/

# 2. Customize datasets
# Edit .github/workflows/schema-validation.yml:
env:
  STAGING_DATASET: dev_dataset
  PRODUCTION_DATASET: prod_dataset
```

**Bypass breaking change check**:
Add label `skip-schema-check` to PR to allow breaking changes

---

### 4. AI Code Review (`ai-review.yml`)

**Purpose**: AI-powered code review for SQL and data model changes

**Runs on**: Pull requests with SQL/model changes

**Duration**: ~2-4 minutes (depends on file count)

**Required Secrets**:
- `ANTHROPIC_API_KEY` - Your Anthropic API key

**Environment Variables**:
- `MAX_FILES_TO_REVIEW` - Max files per PR (default: 10)
- `CLAUDE_MODEL` - Model to use (default: claude-sonnet-4-5-20250929)

**What it does**:
- Reviews each changed SQL file with Claude
- Checks for performance issues, best practices, security
- Provides specific, actionable feedback
- Posts reviews as PR comments

**Setup**:
```bash
# 1. Copy workflow
cp .github/workflows/examples/ai-review.yml .github/workflows/

# 2. Get Anthropic API key
# Visit: https://console.anthropic.com/settings/keys

# 3. Add to GitHub Secrets:
#    - ANTHROPIC_API_KEY: sk-ant-...
```

**Cost Optimization**:
```yaml
env:
  MAX_FILES_TO_REVIEW: 5  # Reduce to 5 files to lower API costs
```

---

### 5. Data Quality Audit (`data-quality.yml`)

**Purpose**: Comprehensive data quality checks on schedule

**Runs on**:
- Push to main/develop
- Daily schedule (8 AM UTC)
- Manual trigger

**Duration**: ~5-10 minutes

**Required Secrets**: None (optional: GOOGLE_APPLICATION_CREDENTIALS_JSON)

**What it does**:
- Validates SQL syntax for all files
- Checks best practices (SELECT *, WHERE clauses)
- Scans for security issues (hardcoded secrets)
- Generates quality report
- Creates GitHub issue on failure (scheduled runs)

**Setup**:
```bash
# 1. Copy workflow
cp .github/workflows/examples/data-quality.yml .github/workflows/

# 2. Adjust schedule if needed
# Edit .github/workflows/data-quality.yml:
on:
  schedule:
    - cron: '0 14 * * *'  # Change to 2 PM UTC
```

**Manual Run**:
Go to Actions > Data Quality Audit > Run workflow

---

## Secrets Setup Guide

### Required Secrets Summary

| Workflow | ANTHROPIC_API_KEY | GOOGLE_APPLICATION_CREDENTIALS_JSON | GCP_PROJECT_ID |
|----------|-------------------|-------------------------------------|----------------|
| sql-validation | ❌ | ❌ | ❌ |
| bq-cost-check | ❌ | ✅ | ✅ |
| schema-validation | ❌ | ✅ | ✅ |
| ai-review | ✅ | ❌ | ❌ |
| data-quality | ❌ | Optional | Optional |

### Setting Up Secrets

1. **Navigate to GitHub Settings**:
   - Repository > Settings > Secrets and variables > Actions

2. **Add New Repository Secret**:
   - Click "New repository secret"
   - Enter name and value
   - Click "Add secret"

### GCP Service Account Setup (Detailed)

```bash
#!/bin/bash
# setup_gcp_sa.sh

PROJECT_ID="your-project-id"
SA_NAME="data-ci"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

# 1. Create service account
gcloud iam service-accounts create $SA_NAME \
  --project=$PROJECT_ID \
  --display-name="Data CI/CD Service Account" \
  --description="Used by GitHub Actions for data validation"

# 2. Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/bigquery.dataViewer"

# 3. Create key
gcloud iam service-accounts keys create key.json \
  --iam-account=$SA_EMAIL \
  --project=$PROJECT_ID

# 4. Base64 encode for GitHub
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  base64 -i key.json -o key.json.b64
else
  # Linux
  base64 -w 0 key.json > key.json.b64
fi

echo ""
echo "✅ Service account created!"
echo ""
echo "Add these secrets to GitHub:"
echo "  GOOGLE_APPLICATION_CREDENTIALS_JSON: (paste content below)"
echo ""
cat key.json.b64
echo ""
echo "  GCP_PROJECT_ID: $PROJECT_ID"
echo ""
echo "⚠️  Delete local key files after adding to GitHub:"
echo "  rm key.json key.json.b64"
```

Run it:
```bash
chmod +x setup_gcp_sa.sh
./setup_gcp_sa.sh
```

---

## Customization Examples

### Change Cost Threshold Per Environment

```yaml
# Different thresholds for dev vs prod
env:
  COST_THRESHOLD_GB: ${{ github.base_ref == 'main' && 100 || 500 }}
```

### Skip Workflows for Draft PRs

```yaml
jobs:
  validate:
    if: github.event.pull_request.draft == false
    runs-on: ubuntu-latest
```

### Run Only on Specific Paths

```yaml
on:
  pull_request:
    paths:
      - 'models/marts/**'  # Only mart models
      - 'models/staging/**'  # Only staging models
```

### Add Slack Notifications

```yaml
- name: Notify Slack
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Workflow failed: ${{ github.event.pull_request.html_url }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Matrix Builds for Multiple Projects

```yaml
strategy:
  matrix:
    project: [project-a, project-b, project-c]
env:
  GCP_PROJECT_ID: ${{ matrix.project }}
```

---

## Testing Workflows Locally

Use [act](https://github.com/nektos/act) to test workflows locally:

```bash
# Install act
brew install act

# Test SQL validation
act pull_request -j validate-sql

# Test with secrets
act pull_request -j cost-check \
  -s GOOGLE_APPLICATION_CREDENTIALS_JSON="$(cat key.json.b64)" \
  -s GCP_PROJECT_ID="your-project"

# Test specific event
act -j data-quality \
  --eventpath .github/workflows/test-event.json
```

---

## Troubleshooting

### Common Issues

#### "Resource not accessible by integration"
- **Cause**: Workflow doesn't have permission to comment on PRs
- **Fix**: Add to workflow:
  ```yaml
  permissions:
    pull-requests: write
    issues: write
  ```

#### "Service account authentication failed"
- **Cause**: Invalid credentials or missing permissions
- **Fix**:
  1. Verify service account has `bigquery.jobUser` role
  2. Check credentials are base64 encoded correctly
  3. Ensure project ID matches

#### "Module not found" errors
- **Cause**: Missing Python dependencies
- **Fix**: Add to workflow:
  ```yaml
  - name: Install dependencies
    run: |
      pip install sqlparse google-cloud-bigquery anthropic
  ```

#### Workflow runs on every commit
- **Cause**: Missing path filters
- **Fix**: Add path filters:
  ```yaml
  on:
    pull_request:
      paths:
        - '**.sql'
  ```

#### Cost check always passes
- **Cause**: Dry run not configured correctly
- **Fix**: Ensure `dry_run=True` in BigQuery client

---

## Best Practices

1. **Start Simple**: Begin with `sql-validation.yml`, add others gradually

2. **Set Appropriate Thresholds**:
   - Development: Higher cost threshold (500GB)
   - Production: Lower cost threshold (100GB)

3. **Use Caching**:
   ```yaml
   - uses: actions/setup-python@v5
     with:
       cache: 'pip'  # Cache pip dependencies
   ```

4. **Fail Fast**: Run quick checks first
   ```yaml
   stages:
     - syntax (30s)
     - lint (1m)
     - cost (2m)
     - quality (5m)
   ```

5. **Add Status Badges** to README:
   ```markdown
   ![SQL Validation](https://github.com/user/repo/workflows/sql-validation/badge.svg)
   ![Cost Check](https://github.com/user/repo/workflows/cost-check/badge.svg)
   ```

6. **Monitor Workflow Duration**: Optimize if workflows take >5 minutes

7. **Use Artifacts** for debugging:
   ```yaml
   - uses: actions/upload-artifact@v4
     if: always()
   ```

8. **Protect Secrets**: Never log secrets or credentials

---

## Next Steps

1. Copy workflows to `.github/workflows/`
2. Set up required secrets
3. Create a test PR to verify workflows
4. Customize thresholds and checks
5. Document your CI/CD setup for the team

## Need Help?

- GitHub Actions docs: https://docs.github.com/en/actions
- BigQuery API: https://cloud.google.com/bigquery/docs
- Anthropic API: https://docs.anthropic.com

For project-specific help, see the main [CI/CD Integration Guide](../../docs/guides/cicd-integration.md).
