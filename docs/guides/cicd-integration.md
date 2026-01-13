# CI/CD Integration Guide

Comprehensive guide to integrating DecentClaude utilities and Skills into your CI/CD pipelines for automated quality checks, cost monitoring, and schema validation.

## Table of Contents

1. [Overview](#overview)
2. [GitHub Actions Integration](#github-actions-integration)
3. [GitLab CI Integration](#gitlab-ci-integration)
4. [Pre-commit Hooks](#pre-commit-hooks)
5. [Docker Integration](#docker-integration)
6. [Secrets Management](#secrets-management)
7. [JSON Output and Automation](#json-output-and-automation)
8. [Best Practices](#best-practices)

---

## Overview

### Why Use DecentClaude Utilities in CI/CD?

DecentClaude provides powerful utilities for automated data quality and cost management:

- **Automated Quality Checks**: Validate SQL syntax, schema changes, and data quality before deployment
- **Cost Monitoring**: Estimate BigQuery query costs to prevent budget overruns
- **Schema Validation**: Detect breaking schema changes before they reach production
- **Data Quality**: Run custom validation checks on every commit
- **AI-Powered Reviews**: Get intelligent code review comments on SQL changes

### Key Benefits

1. **Shift Left**: Catch issues in CI before they reach production
2. **Cost Control**: Block PRs with queries exceeding cost thresholds
3. **Compliance**: Enforce data quality standards automatically
4. **Documentation**: Generate schema diff reports for every change
5. **Safety**: Prevent accidental breaking changes to production tables

### Supported CI/CD Platforms

- GitHub Actions (recommended)
- GitLab CI/CD
- Jenkins
- CircleCI
- Any platform supporting Python and Docker

---

## GitHub Actions Integration

### Prerequisites

1. GitHub repository with Actions enabled
2. Secrets configured:
   - `ANTHROPIC_API_KEY` for AI features
   - `GCP_PROJECT_ID` for BigQuery
   - `GOOGLE_APPLICATION_CREDENTIALS_JSON` for service account

### Example 1: SQL Validation on Pull Requests

```yaml
# .github/workflows/sql-validation.yml
name: SQL Validation

on:
  pull_request:
    paths:
      - '**.sql'
      - 'models/**'
      - 'queries/**'

jobs:
  validate-sql:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install sqlparse sqlfluff

      - name: Validate SQL syntax
        run: |
          python3 scripts/data_quality.py

      - name: Run sqlfluff lint
        run: |
          sqlfluff lint models/ queries/ --format github-annotation
        continue-on-error: true
```

### Example 2: BigQuery Cost Check

```yaml
# .github/workflows/bq-cost-check.yml
name: BigQuery Cost Check

on:
  pull_request:
    paths:
      - '**.sql'

env:
  COST_THRESHOLD_GB: 100  # Fail if query scans >100GB

jobs:
  cost-check:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install BigQuery client
        run: |
          pip install google-cloud-bigquery

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GOOGLE_APPLICATION_CREDENTIALS_JSON }}

      - name: Check query costs
        id: cost-check
        run: |
          set -e
          total_cost_gb=0

          for sql_file in $(git diff --name-only origin/main...HEAD | grep '\.sql$'); do
            if [ -f "$sql_file" ]; then
              echo "Checking cost for $sql_file..."

              # Run cost estimation
              cost_output=$(python3 -c "
          from google.cloud import bigquery
          import sys

          client = bigquery.Client()
          with open('$sql_file', 'r') as f:
              query = f.read()

          job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
          query_job = client.query(query, job_config=job_config)

          bytes_processed = query_job.total_bytes_processed
          gb_processed = bytes_processed / (1024**3)

          print(f'{gb_processed:.2f}')
          " 2>&1) || { echo "Failed to estimate cost for $sql_file"; continue; }

              echo "$sql_file will process: ${cost_output} GB"

              # Add to total
              total_cost_gb=$(echo "$total_cost_gb + $cost_output" | bc)
            fi
          done

          echo "total_cost_gb=$total_cost_gb" >> $GITHUB_OUTPUT

          # Check threshold
          if (( $(echo "$total_cost_gb > $COST_THRESHOLD_GB" | bc -l) )); then
            echo "ERROR: Total cost ${total_cost_gb}GB exceeds threshold ${COST_THRESHOLD_GB}GB"
            exit 1
          else
            echo "Cost check passed: ${total_cost_gb}GB (threshold: ${COST_THRESHOLD_GB}GB)"
          fi

      - name: Comment on PR
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const cost = '${{ steps.cost-check.outputs.total_cost_gb }}';
            const threshold = process.env.COST_THRESHOLD_GB;
            const status = parseFloat(cost) > parseFloat(threshold) ? '❌ Failed' : '✅ Passed';

            const comment = `## BigQuery Cost Check ${status}

            **Total data to be processed**: ${cost} GB
            **Threshold**: ${threshold} GB

            ${parseFloat(cost) > parseFloat(threshold)
              ? '⚠️ This PR will scan more data than allowed. Please optimize queries.'
              : '✅ Cost is within acceptable limits.'}
            `;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### Example 3: Schema Validation

```yaml
# .github/workflows/schema-validation.yml
name: Schema Validation

on:
  pull_request:
    paths:
      - 'models/**'
      - 'migrations/**'

jobs:
  schema-diff:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Need full history for comparison

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install google-cloud-bigquery

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GOOGLE_APPLICATION_CREDENTIALS_JSON }}

      - name: Compare schemas
        id: schema-diff
        run: |
          # Extract table references from changed files
          # This is a simplified example - adjust for your schema definition format

          cat > schema_diff.py << 'EOF'
          from google.cloud import bigquery
          import sys
          import json

          def get_schema(table_id):
              client = bigquery.Client()
              table = client.get_table(table_id)
              return [{"name": field.name, "type": field.field_type, "mode": field.mode}
                      for field in table.schema]

          def compare_schemas(old_table, new_table):
              old_schema = get_schema(old_table)
              new_schema = get_schema(new_table)

              old_fields = {f["name"]: f for f in old_schema}
              new_fields = {f["name"]: f for f in new_schema}

              added = [f for f in new_schema if f["name"] not in old_fields]
              removed = [f for f in old_schema if f["name"] not in new_fields]
              modified = []

              for name in set(old_fields.keys()) & set(new_fields.keys()):
                  if old_fields[name] != new_fields[name]:
                      modified.append({
                          "name": name,
                          "old": old_fields[name],
                          "new": new_fields[name]
                      })

              return {"added": added, "removed": removed, "modified": modified}

          if __name__ == "__main__":
              old_table = sys.argv[1]
              new_table = sys.argv[2]
              diff = compare_schemas(old_table, new_table)
              print(json.dumps(diff, indent=2))
          EOF

          # Example: compare staging vs production
          python3 schema_diff.py \
            "${{ secrets.GCP_PROJECT_ID }}.staging.users" \
            "${{ secrets.GCP_PROJECT_ID }}.production.users" \
            > schema_diff.json

          cat schema_diff.json

      - name: Check for breaking changes
        run: |
          # Fail if columns were removed or types changed
          removed=$(cat schema_diff.json | jq '.removed | length')
          modified=$(cat schema_diff.json | jq '.modified | length')

          if [ "$removed" -gt 0 ] || [ "$modified" -gt 0 ]; then
            echo "⚠️ Breaking schema changes detected!"
            cat schema_diff.json
            exit 1
          fi

      - name: Comment schema diff on PR
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const diff = JSON.parse(fs.readFileSync('schema_diff.json', 'utf8'));

            let comment = '## Schema Validation Report\n\n';

            if (diff.added.length > 0) {
              comment += '### ✅ Added Fields\n';
              diff.added.forEach(f => {
                comment += `- \`${f.name}\` (${f.type}, ${f.mode})\n`;
              });
            }

            if (diff.removed.length > 0) {
              comment += '\n### ❌ Removed Fields (BREAKING)\n';
              diff.removed.forEach(f => {
                comment += `- \`${f.name}\` (${f.type}, ${f.mode})\n`;
              });
            }

            if (diff.modified.length > 0) {
              comment += '\n### ⚠️ Modified Fields (POTENTIALLY BREAKING)\n';
              diff.modified.forEach(m => {
                comment += `- \`${m.name}\`: ${m.old.type} → ${m.new.type}\n`;
              });
            }

            if (diff.added.length === 0 && diff.removed.length === 0 && diff.modified.length === 0) {
              comment += '✅ No schema changes detected.\n';
            }

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### Example 4: AI-Powered Code Review

```yaml
# .github/workflows/ai-review.yml
name: AI Code Review

on:
  pull_request:
    paths:
      - '**.sql'
      - 'models/**'
      - 'queries/**'

jobs:
  ai-review:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Anthropic SDK
        run: |
          pip install anthropic

      - name: AI Review SQL Changes
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          cat > ai_review.py << 'EOF'
          import anthropic
          import os
          import sys
          from pathlib import Path

          def review_sql_file(file_path, content):
              client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

              message = client.messages.create(
                  model="claude-sonnet-4-5-20250929",
                  max_tokens=2000,
                  messages=[{
                      "role": "user",
                      "content": f"""Review this SQL file for:
          1. Performance issues (missing indexes, inefficient joins)
          2. Best practices (naming conventions, readability)
          3. Potential bugs (NULL handling, edge cases)
          4. Security concerns (SQL injection risks)

          File: {file_path}

          ```sql
          {content}
          ```

          Provide specific, actionable feedback in markdown format."""
                  }]
              )

              return message.content[0].text

          # Get changed SQL files
          import subprocess
          result = subprocess.run(
              ['git', 'diff', '--name-only', 'origin/main...HEAD'],
              capture_output=True,
              text=True
          )

          changed_files = [f for f in result.stdout.strip().split('\n') if f.endswith('.sql')]

          reviews = []
          for file_path in changed_files:
              if Path(file_path).exists():
                  with open(file_path, 'r') as f:
                      content = f.read()

                  print(f"Reviewing {file_path}...")
                  review = review_sql_file(file_path, content)
                  reviews.append(f"### {file_path}\n\n{review}\n\n")

          # Write all reviews to a file
          with open('ai_reviews.md', 'w') as f:
              f.write("# AI Code Review\n\n")
              f.write('\n'.join(reviews))

          print("Reviews written to ai_reviews.md")
          EOF

          python3 ai_review.py

      - name: Post AI Review
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');

            if (!fs.existsSync('ai_reviews.md')) {
              console.log('No review file found');
              return;
            }

            const review = fs.readFileSync('ai_reviews.md', 'utf8');

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: review
            });
```

### Example 5: Data Quality Audit Workflow

```yaml
# .github/workflows/data-quality.yml
name: Data Quality Audit

on:
  push:
    branches:
      - main
  schedule:
    - cron: '0 8 * * *'  # Daily at 8 AM UTC
  workflow_dispatch:

jobs:
  data-quality:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install sqlparse google-cloud-bigquery

      - name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v2
        with:
          credentials_json: ${{ secrets.GOOGLE_APPLICATION_CREDENTIALS_JSON }}

      - name: Run data quality checks
        run: |
          python3 scripts/data_quality.py --format=json > quality_report.json

      - name: Upload quality report
        uses: actions/upload-artifact@v4
        with:
          name: quality-report
          path: quality_report.json
          retention-days: 30

      - name: Fail on quality issues
        run: |
          # Parse JSON and check for failures
          failures=$(cat quality_report.json | jq '.checks[] | select(.passed == false) | .name' | wc -l)

          if [ "$failures" -gt 0 ]; then
            echo "Data quality checks failed!"
            cat quality_report.json | jq '.checks[] | select(.passed == false)'
            exit 1
          fi

      - name: Create issue on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(fs.readFileSync('quality_report.json', 'utf8'));

            const failedChecks = report.checks.filter(c => !c.passed);

            let body = '## Data Quality Issues Detected\n\n';
            body += `**Date**: ${new Date().toISOString()}\n\n`;
            body += '### Failed Checks\n\n';

            failedChecks.forEach(check => {
              body += `- **${check.name}**: ${check.message}\n`;
            });

            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `Data Quality Issues - ${new Date().toISOString().split('T')[0]}`,
              body: body,
              labels: ['data-quality', 'automated']
            });
```

### Workflow Examples Directory

Copy-paste ready examples are available in `.github/workflows/examples/`. See [Working Workflow Examples](#working-workflow-examples) below.

---

## GitLab CI Integration

### Basic Setup

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - test
  - deploy

variables:
  GCP_PROJECT_ID: "your-project-id"
  COST_THRESHOLD_GB: "100"

before_script:
  - pip install --upgrade pip
  - pip install sqlparse google-cloud-bigquery

# SQL Validation
validate:sql:
  stage: validate
  image: python:3.11-slim
  script:
    - python3 scripts/data_quality.py
  only:
    changes:
      - "**/*.sql"
      - "models/**/*"
      - "queries/**/*"

# BigQuery Cost Check
validate:cost:
  stage: validate
  image: python:3.11-slim
  script:
    - |
      for sql_file in $(git diff --name-only $CI_MERGE_REQUEST_DIFF_BASE_SHA...HEAD | grep '\.sql$'); do
        if [ -f "$sql_file" ]; then
          echo "Checking cost for $sql_file..."
          python3 -c "
      from google.cloud import bigquery
      import os

      client = bigquery.Client()
      with open('$sql_file', 'r') as f:
          query = f.read()

      job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
      query_job = client.query(query, job_config=job_config)

      bytes_processed = query_job.total_bytes_processed
      gb_processed = bytes_processed / (1024**3)

      print(f'$sql_file: {gb_processed:.2f} GB')

      if gb_processed > float(os.environ['COST_THRESHOLD_GB']):
          print(f'ERROR: Query exceeds cost threshold!')
          exit(1)
      "
        fi
      done
  only:
    - merge_requests
  variables:
    GOOGLE_APPLICATION_CREDENTIALS: /tmp/gcp_key.json
  before_script:
    - echo "$GCP_SERVICE_ACCOUNT_KEY" | base64 -d > $GOOGLE_APPLICATION_CREDENTIALS
    - pip install google-cloud-bigquery

# Schema Validation
validate:schema:
  stage: validate
  image: python:3.11-slim
  script:
    - python3 bin/data-utils/bq-schema-diff $OLD_TABLE $NEW_TABLE
  only:
    - merge_requests
  artifacts:
    reports:
      junit: schema-diff-report.xml
    paths:
      - schema-diff-report.xml
    expire_in: 1 week

# Data Quality Tests
test:quality:
  stage: test
  image: python:3.11-slim
  script:
    - python3 scripts/data_quality.py --format=json > quality_report.json
    - |
      failures=$(cat quality_report.json | jq '.checks[] | select(.passed == false) | .name' | wc -l)
      if [ "$failures" -gt 0 ]; then
        echo "Data quality checks failed!"
        cat quality_report.json | jq '.checks[] | select(.passed == false)'
        exit 1
      fi
  artifacts:
    reports:
      junit: quality_report.json
    paths:
      - quality_report.json
    expire_in: 30 days

# Deploy to Production
deploy:production:
  stage: deploy
  image: python:3.11-slim
  script:
    - echo "Deploying to production..."
    - python3 deploy.py
  only:
    - main
  when: manual
```

### Pipeline Stages Best Practices

1. **Validate Stage**: Fast checks (syntax, linting)
2. **Test Stage**: Deeper validation (cost, quality)
3. **Deploy Stage**: Production deployment

### Artifact Handling

```yaml
# Save and download artifacts
artifacts:
  paths:
    - quality_report.json
    - schema_diff.json
    - cost_report.json
  reports:
    junit: test-results.xml
  expire_in: 30 days
```

---

## Pre-commit Hooks

### Installation

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks in your repo
pre-commit install
```

### Example Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      # SQL Syntax Validation
      - id: validate-sql
        name: Validate SQL syntax
        entry: python3 scripts/data_quality.py
        language: system
        files: \.sql$
        pass_filenames: false

      # SQL Linting
      - id: sqlfluff-lint
        name: Lint SQL with sqlfluff
        entry: sqlfluff lint
        language: system
        files: \.sql$
        args: [--dialect=bigquery]

      # BigQuery Cost Check
      - id: bq-cost-check
        name: Check BigQuery query costs
        entry: bash -c 'for file in "$@"; do python3 bin/data-utils/bq-query-cost --file="$file" --threshold=100; done'
        language: system
        files: \.sql$

      # Schema Validation
      - id: schema-check
        name: Validate schema changes
        entry: python3 scripts/validate_schema_changes.py
        language: system
        files: ^models/.*\.sql$
        pass_filenames: false

      # No Hardcoded Secrets
      - id: no-secrets
        name: Check for hardcoded secrets
        entry: bash -c 'if grep -r -i "password\|api_key\|secret" --include="*.sql" .; then exit 1; fi'
        language: system
        files: \.sql$
        pass_filenames: false

  # Standard pre-commit hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: [--maxkb=1000]
```

### Custom Pre-commit Script

```python
# scripts/validate_schema_changes.py
#!/usr/bin/env python3
"""
Pre-commit hook for validating schema changes
"""
import sys
import subprocess
from pathlib import Path

def get_changed_files():
    """Get files changed in this commit"""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=AM'],
        capture_output=True,
        text=True
    )
    return [f for f in result.stdout.strip().split('\n') if f.endswith('.sql')]

def validate_schema_file(file_path):
    """Validate a schema file"""
    # Add your validation logic here
    # Example: check for required fields

    with open(file_path, 'r') as f:
        content = f.read()

    required_patterns = ['created_at', 'updated_at']

    for pattern in required_patterns:
        if pattern not in content.lower():
            print(f"⚠️  {file_path}: Missing recommended field '{pattern}'")
            return False

    return True

def main():
    changed_files = get_changed_files()

    if not changed_files:
        print("✅ No SQL files to validate")
        return 0

    print(f"Validating {len(changed_files)} schema file(s)...")

    all_valid = True
    for file_path in changed_files:
        if 'models/' in file_path or 'schemas/' in file_path:
            if not validate_schema_file(file_path):
                all_valid = False

    if all_valid:
        print("✅ All schema validations passed")
        return 0
    else:
        print("❌ Schema validation failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

---

## Docker Integration

### Dockerfile for Utilities

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    jq \
    bc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy utility scripts
COPY bin/data-utils/ /app/bin/data-utils/
COPY scripts/ /app/scripts/

# Make scripts executable
RUN chmod +x /app/bin/data-utils/*

# Set PATH
ENV PATH="/app/bin/data-utils:${PATH}"

# Default command
CMD ["bash"]
```

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  data-validation:
    build: .
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-key.json
      - GCP_PROJECT_ID=${GCP_PROJECT_ID}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./:/app
      - ./credentials:/app/credentials:ro
      - ./output:/app/output
    command: python3 scripts/data_quality.py

  cost-check:
    build: .
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-key.json
      - GCP_PROJECT_ID=${GCP_PROJECT_ID}
    volumes:
      - ./:/app
      - ./credentials:/app/credentials:ro
    command: bash -c "find /app/queries -name '*.sql' -exec bq-query-cost --file={} \\;"

  schema-validator:
    build: .
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-key.json
      - GCP_PROJECT_ID=${GCP_PROJECT_ID}
    volumes:
      - ./:/app
      - ./credentials:/app/credentials:ro
    command: python3 bin/data-utils/bq-schema-diff ${OLD_TABLE} ${NEW_TABLE}
```

### Running in CI with Docker

```yaml
# .github/workflows/docker-validation.yml
name: Docker Validation

on:
  pull_request:
    paths:
      - '**.sql'

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build validation image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          load: true
          tags: data-validation:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Run validation in Docker
        run: |
          docker run --rm \
            -v $(pwd):/app \
            -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials/gcp-key.json \
            data-validation:latest \
            python3 scripts/data_quality.py
```

### Container Best Practices

1. **Use multi-stage builds** to reduce image size
2. **Pin dependency versions** for reproducibility
3. **Use .dockerignore** to exclude unnecessary files
4. **Cache layers** for faster builds
5. **Run as non-root user** for security

---

## Secrets Management

### GitHub Secrets

#### Setting Up Secrets

1. Go to repository **Settings** > **Secrets and variables** > **Actions**
2. Add the following secrets:

| Secret Name | Description |
|------------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key for AI features |
| `GOOGLE_APPLICATION_CREDENTIALS_JSON` | GCP service account JSON (base64 encoded) |
| `GCP_PROJECT_ID` | Your Google Cloud project ID |

#### Using Secrets in Workflows

```yaml
steps:
  - name: Authenticate to Google Cloud
    uses: google-github-actions/auth@v2
    with:
      credentials_json: ${{ secrets.GOOGLE_APPLICATION_CREDENTIALS_JSON }}

  - name: Use Anthropic API
    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    run: |
      python3 ai_review.py
```

### GitLab CI/CD Variables

#### Setting Up Variables

1. Go to **Settings** > **CI/CD** > **Variables**
2. Add variables:

| Variable | Type | Protected | Masked |
|----------|------|-----------|--------|
| `ANTHROPIC_API_KEY` | Variable | Yes | Yes |
| `GCP_SERVICE_ACCOUNT_KEY` | File | Yes | Yes |
| `GCP_PROJECT_ID` | Variable | No | No |

#### Using Variables

```yaml
validate:ai-review:
  script:
    - export ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
    - echo "$GCP_SERVICE_ACCOUNT_KEY" | base64 -d > /tmp/gcp_key.json
    - export GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp_key.json
    - python3 ai_review.py
```

### Environment Variable Patterns

```bash
# .env.example (DO NOT commit actual secrets)
ANTHROPIC_API_KEY=your_api_key_here
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
COST_THRESHOLD_GB=100
```

### Service Account Setup

#### Creating a GCP Service Account

```bash
# 1. Create service account
gcloud iam service-accounts create data-validation-ci \
  --display-name="Data Validation CI/CD"

# 2. Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:data-validation-ci@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:data-validation-ci@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataViewer"

# 3. Create and download key
gcloud iam service-accounts keys create key.json \
  --iam-account=data-validation-ci@YOUR_PROJECT_ID.iam.gserviceaccount.com

# 4. Base64 encode for GitHub (if needed)
cat key.json | base64 > key.json.b64

# 5. Add to GitHub Secrets as GOOGLE_APPLICATION_CREDENTIALS_JSON
```

#### Minimal Permissions

For cost estimation only:
- `bigquery.jobUser`
- `bigquery.dataViewer` (optional, for schema access)

For full validation:
- `bigquery.jobUser`
- `bigquery.dataViewer`
- `bigquery.admin` (if creating tables)

---

## JSON Output and Automation

### Using --format=json

Most utilities support JSON output for programmatic use:

```bash
# Data quality check with JSON output
python3 scripts/data_quality.py --format=json > report.json

# BigQuery cost estimation (custom script)
python3 bin/data-utils/bq-query-cost --file=query.sql --format=json > cost.json

# Schema diff (custom script)
python3 bin/data-utils/bq-schema-diff table1 table2 --format=json > diff.json
```

### Parsing JSON in CI Scripts

```bash
#!/bin/bash
# parse_quality_report.sh

# Run data quality checks
python3 scripts/data_quality.py --format=json > report.json

# Parse results
total_checks=$(cat report.json | jq '.checks | length')
failed_checks=$(cat report.json | jq '.checks[] | select(.passed == false) | .name' -r)
failure_count=$(echo "$failed_checks" | wc -l)

echo "Total checks: $total_checks"
echo "Failed checks: $failure_count"

if [ "$failure_count" -gt 0 ]; then
  echo "Failed checks:"
  echo "$failed_checks"
  exit 1
fi
```

### JSON Schema Examples

#### Data Quality Report

```json
{
  "timestamp": "2024-01-13T10:00:00Z",
  "checks": [
    {
      "name": "SQL Syntax Validation",
      "passed": true,
      "message": "All 15 SQL files have valid syntax",
      "details": {
        "files_checked": 15,
        "errors": []
      }
    },
    {
      "name": "No Hardcoded Secrets",
      "passed": false,
      "message": "Potential secrets found in: queries/users.sql",
      "details": {
        "suspicious_files": [
          {
            "file": "queries/users.sql",
            "pattern": "password",
            "line": 42
          }
        ]
      }
    }
  ],
  "summary": {
    "total": 4,
    "passed": 3,
    "failed": 1
  }
}
```

#### Cost Estimation Report

```json
{
  "query": "SELECT * FROM dataset.table",
  "estimated_bytes": 1073741824,
  "estimated_gb": 1.0,
  "estimated_cost_usd": 0.005,
  "threshold_gb": 100,
  "within_threshold": true,
  "recommendations": [
    "Consider adding WHERE clause to filter data",
    "Use specific column names instead of SELECT *"
  ]
}
```

#### Schema Diff Report

```json
{
  "old_table": "project.dataset.table_v1",
  "new_table": "project.dataset.table_v2",
  "changes": {
    "added": [
      {"name": "new_column", "type": "STRING", "mode": "NULLABLE"}
    ],
    "removed": [
      {"name": "old_column", "type": "INTEGER", "mode": "NULLABLE"}
    ],
    "modified": [
      {
        "name": "changed_column",
        "old": {"type": "STRING", "mode": "NULLABLE"},
        "new": {"type": "STRING", "mode": "REQUIRED"}
      }
    ]
  },
  "is_breaking": true,
  "breaking_changes": ["removed", "modified"]
}
```

### Exit Code Handling

```bash
# Standard exit codes
# 0 = success
# 1 = validation failed
# 2 = error/exception

# Example usage
if python3 scripts/data_quality.py; then
  echo "Validation passed"
else
  exit_code=$?
  if [ $exit_code -eq 1 ]; then
    echo "Validation failed - check errors above"
  elif [ $exit_code -eq 2 ]; then
    echo "Error running validation - check logs"
  fi
  exit $exit_code
fi
```

---

## Best Practices

### 1. Fail Fast, Fail Clearly

```yaml
# Run fast checks first
stages:
  - syntax      # 5-10 seconds
  - lint        # 30 seconds
  - cost        # 1-2 minutes
  - quality     # 2-5 minutes
```

### 2. Use Caching

```yaml
# GitHub Actions
- name: Cache Python dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

### 3. Set Appropriate Thresholds

```yaml
env:
  COST_THRESHOLD_GB: 100     # Block queries >100GB
  MAX_QUERY_TIME_SEC: 300    # Warn if query >5 minutes
  MIN_TEST_COVERAGE: 80      # Require 80% test coverage
```

### 4. Generate Reports

```yaml
- name: Upload reports
  uses: actions/upload-artifact@v4
  with:
    name: validation-reports
    path: |
      quality_report.json
      cost_report.json
      schema_diff.json
```

### 5. Use Matrix Builds for Multiple Environments

```yaml
strategy:
  matrix:
    environment: [dev, staging, prod]
    python-version: ['3.9', '3.10', '3.11']
```

### 6. Add Status Badges

```markdown
# README.md
![SQL Validation](https://github.com/user/repo/workflows/sql-validation/badge.svg)
![Cost Check](https://github.com/user/repo/workflows/cost-check/badge.svg)
![Data Quality](https://github.com/user/repo/workflows/data-quality/badge.svg)
```

### 7. Notify on Failures

```yaml
- name: Notify Slack on failure
  if: failure()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "Data validation failed for ${{ github.event.pull_request.html_url }}"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### 8. Version Your Workflows

```yaml
# .github/workflows/sql-validation-v2.yml
# Keep old versions for reference and gradual migration
```

### 9. Document Required Secrets

Create a `SETUP.md` in `.github/`:

```markdown
# CI/CD Setup

Required secrets:
- ANTHROPIC_API_KEY
- GOOGLE_APPLICATION_CREDENTIALS_JSON
- GCP_PROJECT_ID

Setup instructions: ...
```

### 10. Test Workflows Locally

```bash
# Use act to test GitHub Actions locally
brew install act

# Run a workflow
act -j validate-sql

# With secrets
act -j validate-sql -s ANTHROPIC_API_KEY=your_key
```

---

## Working Workflow Examples

Ready-to-use workflow files are provided in `.github/workflows/examples/`:

1. `sql-validation.yml` - Basic SQL syntax validation
2. `bq-cost-check.yml` - BigQuery cost estimation with thresholds
3. `schema-validation.yml` - Schema diff and breaking change detection
4. `ai-review.yml` - AI-powered code review using Claude
5. `data-quality.yml` - Comprehensive data quality audit

### Usage

```bash
# Copy examples to your workflows directory
cp .github/workflows/examples/*.yml .github/workflows/

# Customize for your project
# - Update GCP_PROJECT_ID
# - Set appropriate thresholds
# - Adjust file paths

# Test locally (optional)
act -j validate-sql

# Commit and push
git add .github/workflows/
git commit -m "Add CI/CD workflows"
git push
```

---

## Troubleshooting

### Common Issues

#### Authentication Errors

```bash
# Verify service account has correct permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:*" \
  --format="table(bindings.role, bindings.members)"
```

#### Rate Limiting

```yaml
# Add retry logic
- name: Run with retry
  uses: nick-invision/retry@v2
  with:
    timeout_minutes: 10
    max_attempts: 3
    command: python3 scripts/data_quality.py
```

#### Large Files

```yaml
# Use Git LFS for large test data
- name: Checkout LFS
  uses: actions/checkout@v4
  with:
    lfs: true
```

#### Timeout Issues

```yaml
# Increase timeout
jobs:
  validate:
    timeout-minutes: 30  # Default is 360
```

---

## Next Steps

1. **Start Simple**: Begin with SQL validation, add cost checks later
2. **Iterate**: Add more checks as you identify needs
3. **Monitor**: Track CI/CD duration and optimize slow steps
4. **Document**: Keep this guide updated with your customizations
5. **Share**: Help teammates understand the CI/CD setup

For more information:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitLab CI/CD Documentation](https://docs.gitlab.com/ee/ci/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [BigQuery API Documentation](https://cloud.google.com/bigquery/docs/reference/rest)

---

**Last Updated**: 2026-01-13
