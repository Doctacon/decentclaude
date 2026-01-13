#!/bin/bash
# Setup script for GitHub Actions workflows
# Helps you configure CI/CD pipelines with DecentClaude utilities

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKFLOWS_DIR="$(dirname "$SCRIPT_DIR")"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   DecentClaude CI/CD Workflows Setup                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if .github/workflows directory exists
if [ ! -d "$WORKFLOWS_DIR" ]; then
    echo "Creating .github/workflows directory..."
    mkdir -p "$WORKFLOWS_DIR"
fi

echo "This script will help you set up GitHub Actions workflows."
echo ""
echo "Available workflows:"
echo "  1. SQL Validation          - Validate SQL syntax on PRs"
echo "  2. BigQuery Cost Check     - Estimate and limit query costs"
echo "  3. Schema Validation       - Detect breaking schema changes"
echo "  4. AI Code Review          - AI-powered SQL review with Claude"
echo "  5. Data Quality Audit      - Comprehensive quality checks"
echo "  6. All workflows           - Install all available workflows"
echo ""

read -p "Which workflows would you like to install? (1-6): " choice

case $choice in
    1)
        workflows=("sql-validation.yml")
        ;;
    2)
        workflows=("bq-cost-check.yml")
        ;;
    3)
        workflows=("schema-validation.yml")
        ;;
    4)
        workflows=("ai-review.yml")
        ;;
    5)
        workflows=("data-quality.yml")
        ;;
    6)
        workflows=("sql-validation.yml" "bq-cost-check.yml" "schema-validation.yml" "ai-review.yml" "data-quality.yml")
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "Installing workflows..."
echo ""

for workflow in "${workflows[@]}"; do
    if [ -f "$WORKFLOWS_DIR/$workflow" ]; then
        read -p "⚠️  $workflow already exists. Overwrite? (y/N): " overwrite
        if [[ ! $overwrite =~ ^[Yy]$ ]]; then
            echo "   Skipping $workflow"
            continue
        fi
    fi

    cp "$SCRIPT_DIR/$workflow" "$WORKFLOWS_DIR/$workflow"
    echo "✅ Installed $workflow"
done

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Setup Requirements"
echo "═══════════════════════════════════════════════════════════"
echo ""

needs_gcp=false
needs_anthropic=false

for workflow in "${workflows[@]}"; do
    case $workflow in
        bq-cost-check.yml|schema-validation.yml)
            needs_gcp=true
            ;;
        ai-review.yml)
            needs_anthropic=true
            ;;
    esac
done

if [ "$needs_gcp" = true ]; then
    echo "📋 Google Cloud Setup Required"
    echo ""
    echo "You need to set up the following GitHub secrets:"
    echo ""
    echo "  1. GOOGLE_APPLICATION_CREDENTIALS_JSON"
    echo "     - Service account JSON (base64 encoded)"
    echo ""
    echo "  2. GCP_PROJECT_ID"
    echo "     - Your Google Cloud project ID"
    echo ""
    echo "To create a service account:"
    echo ""
    echo "  gcloud iam service-accounts create data-ci \\"
    echo "    --display-name='Data CI/CD'"
    echo ""
    echo "  gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \\"
    echo "    --member='serviceAccount:data-ci@YOUR_PROJECT_ID.iam.gserviceaccount.com' \\"
    echo "    --role='roles/bigquery.jobUser'"
    echo ""
    echo "  gcloud iam service-accounts keys create key.json \\"
    echo "    --iam-account=data-ci@YOUR_PROJECT_ID.iam.gserviceaccount.com"
    echo ""
    echo "  # Base64 encode the key"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  base64 -i key.json -o key.json.b64"
    else
        echo "  base64 -w 0 key.json > key.json.b64"
    fi
    echo ""
    echo "  # Add content of key.json.b64 to GitHub Secrets"
    echo ""
fi

if [ "$needs_anthropic" = true ]; then
    echo "📋 Anthropic API Setup Required"
    echo ""
    echo "You need to set up the following GitHub secret:"
    echo ""
    echo "  ANTHROPIC_API_KEY"
    echo "    - Get your API key from: https://console.anthropic.com/settings/keys"
    echo ""
fi

if [ "$needs_gcp" = true ] || [ "$needs_anthropic" = true ]; then
    echo "To add secrets to GitHub:"
    echo "  1. Go to your repository on GitHub"
    echo "  2. Click Settings > Secrets and variables > Actions"
    echo "  3. Click 'New repository secret'"
    echo "  4. Add each required secret"
    echo ""
fi

echo "═══════════════════════════════════════════════════════════"
echo "Next Steps"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "1. Add required secrets to GitHub (see above)"
echo "2. Customize workflow thresholds and settings"
echo "3. Commit and push workflows:"
echo ""
echo "   git add .github/workflows/"
echo "   git commit -m 'Add CI/CD workflows'"
echo "   git push"
echo ""
echo "4. Create a test PR to verify workflows work"
echo ""
echo "For detailed documentation, see:"
echo "  .github/workflows/examples/README.md"
echo "  docs/guides/cicd-integration.md"
echo ""
echo "✅ Setup complete!"
echo ""
