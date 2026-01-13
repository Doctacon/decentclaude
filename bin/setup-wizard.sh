#!/bin/bash

# DecentClaude Setup Wizard
# Interactive setup for data workflow automation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Emoji helpers
CHECK="${GREEN}✓${NC}"
CROSS="${RED}✗${NC}"
ARROW="${BLUE}→${NC}"
WARN="${YELLOW}⚠${NC}"

# Track installation state
PYTHON_OK=false
PIP_OK=false
GCLOUD_OK=false
DBT_INSTALLED=false
SQLMESH_INSTALLED=false

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  DecentClaude Data Workflows - Setup Wizard"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "This wizard will help you set up automated data validation"
echo "and quality checks for your data engineering workflows."
echo ""

# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Python version
get_python_version() {
    if command_exists python3; then
        python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1
    else
        echo "0.0"
    fi
}

# Function to compare versions
version_ge() {
    printf '%s\n%s\n' "$2" "$1" | sort -V -C
}

# Check prerequisites
echo "Step 1: Checking Prerequisites"
echo "───────────────────────────────────────────────────────────"
echo ""

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(get_python_version)
    if version_ge "$PYTHON_VERSION" "3.7"; then
        echo -e "${CHECK} Python 3.7+ found (version $PYTHON_VERSION)"
        PYTHON_OK=true
    else
        echo -e "${CROSS} Python $PYTHON_VERSION found, but 3.7+ required"
    fi
else
    echo -e "${CROSS} Python 3 not found"
    echo -e "  ${ARROW} Install Python 3.7+ from https://www.python.org/"
fi

# Check pip
if command_exists pip3; then
    echo -e "${CHECK} pip3 found"
    PIP_OK=true
else
    echo -e "${CROSS} pip3 not found"
fi

# Check gcloud
if command_exists gcloud; then
    echo -e "${CHECK} gcloud CLI found"
    GCLOUD_OK=true
else
    echo -e "${WARN} gcloud CLI not found (optional for BigQuery)"
    echo -e "  ${ARROW} Install from https://cloud.google.com/sdk/docs/install"
fi

echo ""

if ! $PYTHON_OK || ! $PIP_OK; then
    echo -e "${CROSS} Missing required dependencies. Please install:"
    echo "  - Python 3.7+ and pip3"
    echo ""
    exit 1
fi

# Install core dependencies
echo "Step 2: Installing Core Dependencies"
echo "───────────────────────────────────────────────────────────"
echo ""

echo "Installing required Python packages..."
echo ""

# Install sqlparse (required)
echo -e "${ARROW} Installing sqlparse (SQL parsing)..."
if pip3 install --quiet sqlparse 2>/dev/null; then
    echo -e "${CHECK} sqlparse installed"
else
    echo -e "${CROSS} Failed to install sqlparse"
    exit 1
fi

# Install google-cloud-bigquery (required for CLI utilities)
echo -e "${ARROW} Installing google-cloud-bigquery (BigQuery client)..."
if pip3 install --quiet google-cloud-bigquery 2>/dev/null; then
    echo -e "${CHECK} google-cloud-bigquery installed"
else
    echo -e "${WARN} Failed to install google-cloud-bigquery (CLI utilities will not work)"
fi

echo ""

# Optional tools
echo "Step 3: Optional Tool Installation"
echo "───────────────────────────────────────────────────────────"
echo ""
echo "DecentClaude supports additional data tools. Would you like to install them?"
echo ""

# Ask about sqlfluff
read -p "Install sqlfluff (SQL linting)? [y/N]: " install_sqlfluff
if [[ $install_sqlfluff =~ ^[Yy]$ ]]; then
    echo -e "${ARROW} Installing sqlfluff..."
    if pip3 install --quiet sqlfluff 2>/dev/null; then
        echo -e "${CHECK} sqlfluff installed"
    else
        echo -e "${WARN} Failed to install sqlfluff"
    fi
fi

# Ask about dbt
read -p "Install dbt-core and dbt-bigquery? [y/N]: " install_dbt
if [[ $install_dbt =~ ^[Yy]$ ]]; then
    echo -e "${ARROW} Installing dbt-core and dbt-bigquery..."
    if pip3 install --quiet dbt-core dbt-bigquery 2>/dev/null; then
        echo -e "${CHECK} dbt installed"
        DBT_INSTALLED=true
    else
        echo -e "${WARN} Failed to install dbt"
    fi
fi

# Ask about sqlmesh
read -p "Install SQLMesh? [y/N]: " install_sqlmesh
if [[ $install_sqlmesh =~ ^[Yy]$ ]]; then
    echo -e "${ARROW} Installing sqlmesh..."
    if pip3 install --quiet sqlmesh 2>/dev/null; then
        echo -e "${CHECK} sqlmesh installed"
        SQLMESH_INSTALLED=true
    else
        echo -e "${WARN} Failed to install sqlmesh"
    fi
fi

echo ""

# Configure dbt if installed
if $DBT_INSTALLED; then
    echo "Step 4: dbt Configuration"
    echo "───────────────────────────────────────────────────────────"
    echo ""
    echo "dbt requires a profiles.yml configuration file."
    echo ""

    if [ -f ~/.dbt/profiles.yml ]; then
        echo -e "${CHECK} Found existing dbt configuration at ~/.dbt/profiles.yml"
        read -p "Would you like to view/edit it? [y/N]: " edit_dbt
        if [[ $edit_dbt =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} ~/.dbt/profiles.yml
        fi
    else
        read -p "Would you like to create a basic dbt configuration? [y/N]: " create_dbt
        if [[ $create_dbt =~ ^[Yy]$ ]]; then
            mkdir -p ~/.dbt

            read -p "Enter your BigQuery project ID: " project_id
            read -p "Enter your default dataset name: " dataset
            read -p "Enter path to service account keyfile (or press Enter to skip): " keyfile

            cat > ~/.dbt/profiles.yml << EOF
default:
  target: dev
  outputs:
    dev:
      type: bigquery
      project: ${project_id}
      dataset: ${dataset}
      threads: 4
EOF

            if [ -n "$keyfile" ]; then
                cat >> ~/.dbt/profiles.yml << EOF
      method: service-account
      keyfile: ${keyfile}
EOF
            else
                cat >> ~/.dbt/profiles.yml << EOF
      method: oauth
EOF
            fi

            echo -e "${CHECK} Created dbt configuration at ~/.dbt/profiles.yml"
        fi
    fi
    echo ""
fi

# Test BigQuery connection if gcloud is available
if $GCLOUD_OK; then
    echo "Step 5: Testing BigQuery Connection"
    echo "───────────────────────────────────────────────────────────"
    echo ""

    # Check if authenticated
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | grep -q @; then
        echo -e "${CHECK} gcloud authentication active"

        # Get active project
        PROJECT=$(gcloud config get-value project 2>/dev/null)
        if [ -n "$PROJECT" ]; then
            echo -e "${CHECK} Active project: $PROJECT"
        else
            echo -e "${WARN} No active project set"
            read -p "Would you like to set one now? [y/N]: " set_project
            if [[ $set_project =~ ^[Yy]$ ]]; then
                read -p "Enter project ID: " project_id
                gcloud config set project "$project_id"
            fi
        fi
    else
        echo -e "${WARN} Not authenticated with gcloud"
        read -p "Would you like to authenticate now? [y/N]: " do_auth
        if [[ $do_auth =~ ^[Yy]$ ]]; then
            gcloud auth login
            gcloud auth application-default login
        fi
    fi
    echo ""
fi

# Add CLI utilities to PATH
echo "Step 6: CLI Utilities Setup"
echo "───────────────────────────────────────────────────────────"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
UTILS_DIR="$SCRIPT_DIR/data-utils"

echo "DecentClaude includes powerful CLI utilities for BigQuery:"
echo "  - bq-schema-diff: Compare table schemas"
echo "  - bq-query-cost: Estimate query costs"
echo "  - bq-partition-info: Analyze partitioning"
echo "  - bq-lineage: Explore table dependencies"
echo ""

# Check if already in PATH
if echo "$PATH" | grep -q "$UTILS_DIR"; then
    echo -e "${CHECK} CLI utilities already in PATH"
else
    echo "To use these utilities from anywhere, add them to your PATH."
    echo ""
    echo "Add this line to your shell configuration file:"
    echo ""
    echo -e "${BLUE}export PATH=\"\$PATH:$UTILS_DIR\"${NC}"
    echo ""

    read -p "Would you like me to add this to your shell config? [y/N]: " add_path
    if [[ $add_path =~ ^[Yy]$ ]]; then
        # Detect shell
        if [ -n "$ZSH_VERSION" ]; then
            SHELL_CONFIG="$HOME/.zshrc"
        elif [ -n "$BASH_VERSION" ]; then
            SHELL_CONFIG="$HOME/.bashrc"
        else
            SHELL_CONFIG="$HOME/.profile"
        fi

        echo "" >> "$SHELL_CONFIG"
        echo "# DecentClaude CLI utilities" >> "$SHELL_CONFIG"
        echo "export PATH=\"\$PATH:$UTILS_DIR\"" >> "$SHELL_CONFIG"

        echo -e "${CHECK} Added to $SHELL_CONFIG"
        echo -e "  ${ARROW} Run: source $SHELL_CONFIG"
    fi
fi

echo ""

# Summary
echo "═══════════════════════════════════════════════════════════"
echo "  Setup Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Installation Summary:"
echo -e "  ${CHECK} Core dependencies installed"
if $DBT_INSTALLED; then
    echo -e "  ${CHECK} dbt installed"
fi
if $SQLMESH_INSTALLED; then
    echo -e "  ${CHECK} SQLMesh installed"
fi
if $GCLOUD_OK; then
    echo -e "  ${CHECK} BigQuery ready"
fi
echo ""
echo "Next Steps:"
echo ""
echo "1. Read the Quick Start Guide:"
echo -e "   ${ARROW} cat QUICKSTART.md"
echo ""
echo "2. Try the CLI utilities:"
echo -e "   ${ARROW} bin/data-utils/bq-schema-diff --help"
echo ""
echo "3. Explore example workflows:"
echo -e "   ${ARROW} cat playbooks.md"
echo ""
echo "4. View available hooks:"
echo -e "   ${ARROW} cat docs/worktrees/HOOKS.md"
echo ""
echo "For help and documentation:"
echo "  - README.md: Full documentation"
echo "  - QUICKSTART.md: 5-minute getting started guide"
echo "  - playbooks.md: Common workflow patterns"
echo "  - data-engineering-patterns.md: Best practices"
echo ""
echo "Happy data engineering!"
echo ""
