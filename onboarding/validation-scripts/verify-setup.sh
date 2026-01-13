#!/bin/bash
# DecentClaude Setup Validation Script
# Verifies that your environment is correctly configured

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_header "DecentClaude Setup Validation"

# Check 1: Python
print_header "1. Python Installation"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 7 ]; then
        check_pass "Python $PYTHON_VERSION installed (>= 3.7 required)"
    else
        check_fail "Python $PYTHON_VERSION is too old (need >= 3.7)"
    fi
else
    check_fail "Python 3 not found"
    echo "   Install from: https://www.python.org/"
fi

# Check 2: gcloud CLI
print_header "2. Google Cloud SDK"
if command -v gcloud &> /dev/null; then
    check_pass "gcloud CLI installed"

    # Check if authenticated
    if gcloud auth list --filter="status:ACTIVE" --format="value(account)" | grep -q "@"; then
        ACTIVE_ACCOUNT=$(gcloud auth list --filter="status:ACTIVE" --format="value(account)")
        check_pass "Authenticated as: $ACTIVE_ACCOUNT"
    else
        check_fail "Not authenticated with gcloud"
        echo "   Run: gcloud auth login"
    fi

    # Check project
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
    if [ -n "$CURRENT_PROJECT" ]; then
        check_pass "Active project: $CURRENT_PROJECT"
    else
        check_fail "No active GCP project"
        echo "   Run: gcloud config set project YOUR_PROJECT_ID"
    fi
else
    check_fail "gcloud CLI not found"
    echo "   Install from: https://cloud.google.com/sdk/docs/install"
fi

# Check 3: BigQuery
print_header "3. BigQuery Access"
if command -v bq &> /dev/null; then
    check_pass "BigQuery CLI (bq) installed"

    # Test BigQuery access
    if [ -n "$CURRENT_PROJECT" ]; then
        if bq ls --project_id="$CURRENT_PROJECT" &> /dev/null; then
            check_pass "BigQuery access verified for $CURRENT_PROJECT"

            # Check for application default credentials
            if [ -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
                check_pass "Application default credentials configured"
            else
                check_warn "Application default credentials not found"
                echo "   Run: gcloud auth application-default login"
            fi
        else
            check_fail "Cannot access BigQuery in $CURRENT_PROJECT"
            echo "   Verify permissions and run: gcloud auth application-default login"
        fi
    else
        check_warn "Skipping BigQuery test (no active project)"
    fi
else
    check_fail "BigQuery CLI not found (should come with gcloud SDK)"
fi

# Check 4: Git
print_header "4. Git Installation"
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    check_pass "$GIT_VERSION installed"

    # Check if in a git repo
    if git rev-parse --git-dir &> /dev/null; then
        check_pass "Inside git repository"
    else
        check_warn "Not in a git repository"
    fi
else
    check_fail "Git not found"
    echo "   Install from: https://git-scm.com/"
fi

# Check 5: Claude Code (optional)
print_header "5. Claude Code (Optional)"
if command -v claude &> /dev/null; then
    check_pass "Claude Code installed"
else
    check_warn "Claude Code not found (optional)"
    echo "   Install from: https://claude.com/claude-code"
fi

# Check 6: Environment Variables
print_header "6. Environment Variables"

# Try to source .env if it exists
if [ -f .env ]; then
    check_pass ".env file exists"
    source .env

    if [ -n "$GCP_PROJECT_ID" ]; then
        check_pass "GCP_PROJECT_ID set: $GCP_PROJECT_ID"
    else
        check_fail "GCP_PROJECT_ID not set in .env"
    fi

    if [ -n "$BQ_DATASET" ]; then
        check_pass "BQ_DATASET set: $BQ_DATASET"
    else
        check_fail "BQ_DATASET not set in .env"
    fi

    if [ -n "$PYTHONPATH" ]; then
        check_pass "PYTHONPATH set: $PYTHONPATH"
    else
        check_warn "PYTHONPATH not set (needed for SQLMesh)"
    fi
else
    check_fail ".env file not found"
    echo "   Run: onboarding/setup-wizard.sh"
fi

# Check 7: dbt (optional)
print_header "7. dbt Configuration (Optional)"
if command -v dbt &> /dev/null; then
    check_pass "dbt installed"

    # Check for profiles.yml
    if [ -f "$HOME/.dbt/profiles.yml" ]; then
        check_pass "dbt profiles.yml exists"

        # Try dbt debug
        if dbt debug &> /dev/null; then
            check_pass "dbt connection successful"
        else
            check_fail "dbt debug failed"
            echo "   Run: dbt debug (for details)"
        fi
    else
        check_fail "dbt profiles.yml not found"
        echo "   Create: ~/.dbt/profiles.yml"
    fi
else
    check_warn "dbt not installed (optional for dbt users)"
    echo "   Install with: pip install dbt-bigquery"
fi

# Check 8: Project Files
print_header "8. Project Configuration"

if [ -f CLAUDE.md ]; then
    check_pass "CLAUDE.md exists"
else
    check_warn "CLAUDE.md not found"
    echo "   Copy from: docs/templates/CLAUDE.md.template"
fi

if [ -f .gitignore ]; then
    if grep -q "^.env$" .gitignore; then
        check_pass ".env in .gitignore"
    else
        check_warn ".env not in .gitignore (should add it)"
    fi
else
    check_warn ".gitignore not found"
fi

# Check 9: Python Dependencies
print_header "9. Python Dependencies"

if [ -f requirements.txt ]; then
    check_pass "requirements.txt exists"

    if [ -d venv ]; then
        check_pass "Virtual environment (venv) exists"
        echo "   Activate with: source venv/bin/activate"
    else
        check_warn "Virtual environment not created"
        echo "   Create with: python3 -m venv venv"
    fi
else
    check_warn "No requirements.txt found"
fi

# Check 10: DecentClaude Utilities
print_header "10. DecentClaude CLI Utilities"

if [ -d bin/data-utils ]; then
    check_pass "bin/data-utils directory exists"

    UTILS=("bq-schema-diff" "bq-query-cost" "bq-partition-info" "bq-lineage")
    for util in "${UTILS[@]}"; do
        if [ -f "bin/data-utils/$util" ] && [ -x "bin/data-utils/$util" ]; then
            check_pass "$util is executable"
        else
            check_warn "$util not found or not executable"
        fi
    done
else
    check_warn "bin/data-utils directory not found"
fi

# Summary
print_header "Validation Summary"

TOTAL=$((PASSED + FAILED + WARNINGS))

echo -e "${GREEN}Passed:${NC}   $PASSED / $TOTAL"
echo -e "${RED}Failed:${NC}   $FAILED / $TOTAL"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS / $TOTAL"

echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ Your environment is ready to use!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. source .env"
    echo "  2. Start the Getting Started tutorial:"
    echo "     cat tutorials/getting-started/README.md"
    exit 0
else
    echo -e "${RED}✗ Please fix the failed checks above${NC}"
    echo ""
    echo "Need help?"
    echo "  - Run the setup wizard: bash onboarding/setup-wizard.sh"
    echo "  - Check the checklist: cat onboarding/checklist.md"
    echo "  - Ask Claude Code for assistance"
    exit 1
fi
