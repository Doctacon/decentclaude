#!/usr/bin/env bash
# Generate PR checklist based on changed files
# Usage: ./.github/scripts/generate-pr-checklist.sh [base-branch]

set -euo pipefail

BASE_BRANCH="${1:-main}"

# Get list of changed files
CHANGED_FILES=$(git diff --name-only "$BASE_BRANCH"...HEAD 2>/dev/null || echo "")

if [ -z "$CHANGED_FILES" ]; then
    echo "No changed files detected"
    exit 0
fi

# Initialize checklist items
CHECKLIST=()
DETECTED_TYPES=()

# Function to add checklist item
add_checklist() {
    local item="$1"
    CHECKLIST+=("- [ ] $item")
}

# Function to add detected type
add_type() {
    local type="$1"
    if [[ ! " ${DETECTED_TYPES[*]} " =~ " ${type} " ]]; then
        DETECTED_TYPES+=("$type")
    fi
}

# Detect change types based on file patterns
echo "Analyzing changed files..."
echo ""

# Check for SQL files
if echo "$CHANGED_FILES" | grep -qE '\.(sql|sqlx)$'; then
    add_type "data_model"
    add_checklist "SQL syntax validated"
    add_checklist "BigQuery dry run successful"
    add_checklist "Query cost estimated and acceptable"
    add_checklist "Data model documentation updated"
    echo "Detected: SQL/Data Model changes"
fi

# Check for dbt files
if echo "$CHANGED_FILES" | grep -qE 'models/|dbt_project\.yml|profiles\.yml'; then
    add_type "data_model"
    add_checklist "dbt compilation successful"
    add_checklist "dbt tests added/updated"
    add_checklist "dbt documentation generated"
    echo "Detected: dbt changes"
fi

# Check for SQLMesh files
if echo "$CHANGED_FILES" | grep -qE 'sqlmesh/|config\.yml'; then
    add_type "data_model"
    add_checklist "SQLMesh plan generated successfully"
    add_checklist "SQLMesh tests added/updated"
    echo "Detected: SQLMesh changes"
fi

# Check for Python files
if echo "$CHANGED_FILES" | grep -qE '\.py$'; then
    add_type "code"
    add_checklist "Python tests added/updated"
    add_checklist "Type hints added (where appropriate)"
    add_checklist "Linting passes (ruff/black/mypy)"
    echo "Detected: Python code changes"
fi

# Check for pipeline/workflow files
if echo "$CHANGED_FILES" | grep -qE 'pipelines/|workflows/|airflow/|dagster/'; then
    add_type "pipeline"
    add_checklist "Pipeline tested end-to-end"
    add_checklist "Error handling and retries configured"
    add_checklist "Monitoring and alerting configured"
    add_checklist "Pipeline runbook created/updated"
    echo "Detected: Pipeline/workflow changes"
fi

# Check for configuration files
if echo "$CHANGED_FILES" | grep -qE '\.(yml|yaml|json|toml|env|ini|conf)$'; then
    add_type "config"
    add_checklist "Configuration validated"
    add_checklist "No secrets committed"
    add_checklist "Environment-specific values externalized"
    add_checklist "Configuration documented"
    echo "Detected: Configuration changes"
fi

# Check for documentation files
if echo "$CHANGED_FILES" | grep -qE '\.(md|rst|txt)$'; then
    add_type "documentation"
    add_checklist "Documentation reviewed for accuracy"
    add_checklist "Links verified (no broken links)"
    add_checklist "Examples tested (if applicable)"
    echo "Detected: Documentation changes"
fi

# Check for schema files
if echo "$CHANGED_FILES" | grep -qE 'schema\.yml|\.schema|schemas/'; then
    add_type "data_model"
    add_checklist "Schema changes backward compatible (or migration plan exists)"
    add_checklist "Schema documentation updated"
    add_checklist "Downstream impacts identified"
    echo "Detected: Schema changes"
fi

# Check for infrastructure files
if echo "$CHANGED_FILES" | grep -qE 'terraform/|\.tf$|infrastructure/|k8s/|docker'; then
    add_type "infrastructure"
    add_checklist "Infrastructure changes tested in non-prod"
    add_checklist "Deployment plan documented"
    add_checklist "Rollback plan documented"
    echo "Detected: Infrastructure changes"
fi

# Check for test files
if echo "$CHANGED_FILES" | grep -qE 'tests/|_test\.py$|\.test\.|spec\.'; then
    add_checklist "All tests pass locally"
    add_checklist "Test coverage maintained or improved"
    echo "Detected: Test changes"
fi

# Always include general checklist items
add_checklist "Code follows project conventions"
add_checklist "All validation hooks pass"
add_checklist "No secrets or sensitive data committed"
add_checklist "Reviewed own code before requesting review"

# Generate output
echo ""
echo "================================"
echo "Generated PR Checklist"
echo "================================"
echo ""

# Show detected change types
if [ ${#DETECTED_TYPES[@]} -gt 0 ]; then
    echo "Detected change types:"
    for type in "${DETECTED_TYPES[@]}"; do
        echo "  - $type"
    done
    echo ""

    echo "Recommended template:"
    if [[ " ${DETECTED_TYPES[*]} " =~ " data_model " ]]; then
        echo "  .github/PULL_REQUEST_TEMPLATE/data_model.md"
    elif [[ " ${DETECTED_TYPES[*]} " =~ " pipeline " ]]; then
        echo "  .github/PULL_REQUEST_TEMPLATE/pipeline.md"
    elif [[ " ${DETECTED_TYPES[*]} " =~ " infrastructure " ]]; then
        echo "  .github/PULL_REQUEST_TEMPLATE/config.md"
    elif [[ " ${DETECTED_TYPES[*]} " =~ " documentation " ]] && [ ${#DETECTED_TYPES[@]} -eq 1 ]; then
        echo "  .github/PULL_REQUEST_TEMPLATE/documentation.md"
    elif [[ " ${DETECTED_TYPES[*]} " =~ " config " ]] && [ ${#DETECTED_TYPES[@]} -eq 1 ]; then
        echo "  .github/PULL_REQUEST_TEMPLATE/config.md"
    else
        echo "  .github/pull_request_template.md (default)"
    fi
    echo ""
fi

# Print checklist
echo "Checklist items:"
echo ""
for item in "${CHECKLIST[@]}"; do
    echo "$item"
done
echo ""

# Print usage instructions
echo "================================"
echo "Usage Instructions"
echo "================================"
echo ""
echo "1. Copy the checklist items above into your PR description"
echo "2. Use the recommended template when creating your PR"
echo "3. Check off items as you complete them"
echo ""
echo "To use a specific template via GitHub CLI:"
echo "  gh pr create --template <template-name>.md"
echo ""
