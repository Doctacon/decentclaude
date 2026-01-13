# Step 2: Environment Setup and Configuration

## Overview

Before you can start building data pipelines, you need to configure your development environment. This step guides you through the essential setup.

## Prerequisites Check

First, verify you have the required tools installed:

```bash
# Check Python version (need 3.7+)
python --version

# Check gcloud CLI
gcloud --version

# Check git
git --version

# Check Claude Code
claude --version
```

## 1. BigQuery Authentication

### Set up gcloud credentials:

```bash
# Login to Google Cloud
gcloud auth login

# Set your project (replace with your project ID)
gcloud config set project YOUR_PROJECT_ID

# Create application default credentials
gcloud auth application-default login
```

### Verify BigQuery access:

```bash
# Test connection (replace with your project)
bq ls --project_id=YOUR_PROJECT_ID

# Or use the DecentClaude utility
bin/data-utils/bq-query-cost "SELECT 1"
```

## 2. Environment Variables

Create a `.env` file in your project root (this file is gitignored):

```bash
# BigQuery Configuration
export GCP_PROJECT_ID="your-project-id"
export BQ_DATASET="your_dataset"

# dbt Configuration
export DBT_PROFILES_DIR="$HOME/.dbt"

# SQLMesh Configuration (if using SQLMesh)
export PYTHONPATH="."
```

Load the environment variables:

```bash
source .env
```

## 3. Python Dependencies

If the project has a `requirements.txt`:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 4. Claude Code Configuration

### Set up project-specific instructions:

```bash
# Copy the CLAUDE.md template
cp docs/templates/CLAUDE.md.template CLAUDE.md

# Edit CLAUDE.md with your project details
# This tells Claude Code about your project context
```

### Configure Claude Code hooks (if using):

```bash
# Check existing hooks
cat .claude/settings.json

# Hooks are already configured for:
# - dbt compilation checks
# - SQL linting (sqlfluff)
# - Data quality validation
```

## 5. dbt Setup (if using dbt)

### Initialize dbt profile:

```bash
# Create dbt profiles directory
mkdir -p ~/.dbt

# Copy example profile
cat > ~/.dbt/profiles.yml <<EOF
default:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: oauth
      project: YOUR_PROJECT_ID
      dataset: YOUR_DATASET
      threads: 4
      timeout_seconds: 300
EOF
```

### Test dbt connection:

```bash
dbt debug
```

## 6. Verify Setup

Run the validation script:

```bash
# Use the onboarding validation script
bash onboarding/validation-scripts/verify-setup.sh
```

Expected output:
```
✓ Python 3.7+ installed
✓ gcloud CLI configured
✓ BigQuery access verified
✓ Claude Code configured
✓ dbt profile configured
✓ Environment variables set

Setup complete! You're ready to go.
```

## Common Issues

### Issue: BigQuery access denied

**Solution**:
```bash
# Re-authenticate
gcloud auth application-default login

# Verify project access
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

### Issue: dbt connection fails

**Solution**:
```bash
# Check profiles.yml location
echo $DBT_PROFILES_DIR

# Verify profile syntax
dbt debug --profiles-dir ~/.dbt
```

### Issue: Claude Code not finding project context

**Solution**:
```bash
# Ensure CLAUDE.md exists in project root
ls -la CLAUDE.md

# Check .claude/settings.json
cat .claude/settings.json
```

## Interactive Exercise

Complete your setup by running:

```bash
# 1. Authenticate with BigQuery
gcloud auth application-default login

# 2. Test a simple query
echo "SELECT 'Setup successful!' as message" | bq query --use_legacy_sql=false

# 3. Verify environment
env | grep -E "GCP_PROJECT_ID|BQ_DATASET"

# 4. Check dbt connection (if using dbt)
dbt debug
```

## Checkpoint Questions

1. What command authenticates you with BigQuery for local development?
2. Where should you store project-specific environment variables?
3. What file tells Claude Code about your project context?

<details>
<summary>View Answers</summary>

1. `gcloud auth application-default login`
2. `.env` file (gitignored)
3. `CLAUDE.md` in project root

</details>

## What You Learned

- How to authenticate with BigQuery
- Setting up environment variables
- Configuring Claude Code for your project
- Verifying your setup with validation scripts

## Next Step

Continue to [Step 3: Your First dbt Model](03-first-dbt-model.md) to create your first data transformation.
