#!/bin/bash
# DecentClaude Setup Wizard
# Interactive first-time setup for new users

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

prompt_yes_no() {
    local question="$1"
    local default="${2:-n}"

    while true; do
        if [ "$default" = "y" ]; then
            read -p "$question [Y/n]: " yn
            yn=${yn:-y}
        else
            read -p "$question [y/N]: " yn
            yn=${yn:-n}
        fi

        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

# Welcome message
clear
cat << "EOF"
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ██████╗ ███████╗ ██████╗███████╗███╗   ██╗████████╗   ║
║   ██╔══██╗██╔════╝██╔════╝██╔════╝████╗  ██║╚══██╔══╝   ║
║   ██║  ██║█████╗  ██║     █████╗  ██╔██╗ ██║   ██║      ║
║   ██║  ██║██╔══╝  ██║     ██╔══╝  ██║╚██╗██║   ██║      ║
║   ██████╔╝███████╗╚██████╗███████╗██║ ╚████║   ██║      ║
║   ╚═════╝ ╚══════╝ ╚═════╝╚══════╝╚═╝  ╚═══╝   ╚═╝      ║
║                                                          ║
║        CLAUDE - Data Engineering Setup Wizard           ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
EOF

echo -e "\nWelcome to DecentClaude! This wizard will help you set up your environment.\n"
print_info "This will take approximately 10-15 minutes."
echo ""

if ! prompt_yes_no "Ready to begin?" "y"; then
    echo "Setup cancelled. Run this script again when you're ready."
    exit 0
fi

# Track what we've completed
SETUP_LOG="/tmp/decentclaude_setup_$(date +%Y%m%d_%H%M%S).log"
echo "Setup started at $(date)" > "$SETUP_LOG"

# Step 1: Check prerequisites
print_header "Step 1: Checking Prerequisites"

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python 3 installed: $PYTHON_VERSION"
    echo "Python: $PYTHON_VERSION" >> "$SETUP_LOG"
else
    print_error "Python 3 not found"
    print_info "Install Python 3.7+ from https://www.python.org/"
    exit 1
fi

# Check gcloud
if command -v gcloud &> /dev/null; then
    GCLOUD_VERSION=$(gcloud --version | head -n1)
    print_success "gcloud CLI installed"
    echo "gcloud: installed" >> "$SETUP_LOG"
else
    print_warning "gcloud CLI not found"
    if prompt_yes_no "Install gcloud CLI now?" "y"; then
        print_info "Opening installation page..."
        open "https://cloud.google.com/sdk/docs/install" || xdg-open "https://cloud.google.com/sdk/docs/install"
        print_info "Please complete the installation and run this script again."
        exit 0
    fi
fi

# Check git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    print_success "Git installed: $GIT_VERSION"
else
    print_error "Git not found"
    print_info "Install Git from https://git-scm.com/"
    exit 1
fi

# Check Claude Code
if command -v claude &> /dev/null; then
    print_success "Claude Code installed"
    echo "Claude Code: installed" >> "$SETUP_LOG"
else
    print_warning "Claude Code not found"
    print_info "Install from: https://claude.com/claude-code"
fi

# Step 2: BigQuery Setup
print_header "Step 2: BigQuery Authentication"

if prompt_yes_no "Do you have a Google Cloud project for this work?" "y"; then
    read -p "Enter your GCP Project ID: " GCP_PROJECT_ID

    print_info "Authenticating with Google Cloud..."

    # Login to gcloud
    if gcloud auth list --filter="status:ACTIVE" --format="value(account)" | grep -q "@"; then
        print_success "Already authenticated with gcloud"
    else
        gcloud auth login
    fi

    # Set project
    gcloud config set project "$GCP_PROJECT_ID"
    print_success "Project set to: $GCP_PROJECT_ID"

    # Create application default credentials
    print_info "Setting up application default credentials..."
    gcloud auth application-default login

    # Test BigQuery access
    print_info "Testing BigQuery access..."
    if bq ls --project_id="$GCP_PROJECT_ID" &> /dev/null; then
        print_success "BigQuery access verified"
        echo "BigQuery: configured for $GCP_PROJECT_ID" >> "$SETUP_LOG"
    else
        print_warning "Could not verify BigQuery access"
        print_info "You may need to enable the BigQuery API"
    fi
else
    print_info "You'll need a GCP project to use DecentClaude"
    print_info "Create one at: https://console.cloud.google.com/"
    exit 0
fi

# Step 3: Environment Configuration
print_header "Step 3: Environment Configuration"

read -p "Enter your BigQuery dataset name (default: dbt_dev): " BQ_DATASET
BQ_DATASET=${BQ_DATASET:-dbt_dev}

# Create .env file
ENV_FILE=".env"
cat > "$ENV_FILE" << EOL
# DecentClaude Environment Configuration
# Generated by setup wizard on $(date)

# BigQuery Configuration
export GCP_PROJECT_ID="$GCP_PROJECT_ID"
export BQ_DATASET="$BQ_DATASET"

# dbt Configuration
export DBT_PROFILES_DIR="\$HOME/.dbt"

# SQLMesh Configuration
export PYTHONPATH="."
EOL

print_success "Created .env file"
print_info "To use: source .env"

# Add to .gitignore if not already there
if [ -f .gitignore ]; then
    if ! grep -q "^.env$" .gitignore; then
        echo ".env" >> .gitignore
        print_success "Added .env to .gitignore"
    fi
fi

# Step 4: dbt Setup
print_header "Step 4: dbt Configuration"

if prompt_yes_no "Are you using dbt?" "y"; then
    mkdir -p ~/.dbt

    DBT_PROFILE=~/.dbt/profiles.yml
    if [ -f "$DBT_PROFILE" ]; then
        print_warning "dbt profiles.yml already exists"
        if ! prompt_yes_no "Overwrite with DecentClaude defaults?" "n"; then
            print_info "Skipping dbt configuration"
        else
            create_dbt_profile=true
        fi
    else
        create_dbt_profile=true
    fi

    if [ "$create_dbt_profile" = true ]; then
        cat > "$DBT_PROFILE" << EOL
default:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: oauth
      project: $GCP_PROJECT_ID
      dataset: $BQ_DATASET
      threads: 4
      timeout_seconds: 300
      location: US
      priority: interactive

    prod:
      type: bigquery
      method: oauth
      project: $GCP_PROJECT_ID
      dataset: ${BQ_DATASET}_prod
      threads: 8
      timeout_seconds: 300
      location: US
      priority: interactive
EOL
        print_success "Created dbt profiles.yml"

        # Test dbt connection
        if command -v dbt &> /dev/null; then
            print_info "Testing dbt connection..."
            if dbt debug &> /dev/null; then
                print_success "dbt connection verified"
            else
                print_warning "dbt connection test failed"
                print_info "Run 'dbt debug' for more details"
            fi
        else
            print_info "Install dbt with: pip install dbt-bigquery"
        fi
    fi
else
    print_info "Skipping dbt configuration"
fi

# Step 5: Python Dependencies
print_header "Step 5: Python Dependencies"

if [ -f requirements.txt ]; then
    if prompt_yes_no "Install Python dependencies from requirements.txt?" "y"; then
        print_info "Creating virtual environment..."
        python3 -m venv venv

        print_info "Installing dependencies..."
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Dependencies installed"
        print_info "Activate with: source venv/bin/activate"
    fi
else
    print_info "No requirements.txt found, skipping dependency installation"
fi

# Step 6: Claude Code Configuration
print_header "Step 6: Claude Code Configuration"

if [ ! -f CLAUDE.md ]; then
    if prompt_yes_no "Create CLAUDE.md from template?" "y"; then
        if [ -f docs/templates/CLAUDE.md.template ]; then
            cp docs/templates/CLAUDE.md.template CLAUDE.md
            print_success "Created CLAUDE.md"
            print_info "Customize it with your project details"
        else
            print_warning "Template not found"
        fi
    fi
fi

# Step 7: Validation
print_header "Step 7: Validation"

print_info "Running setup validation..."

VALIDATION_PASSED=true

# Validate environment variables
source .env
if [ -n "$GCP_PROJECT_ID" ]; then
    print_success "Environment variables configured"
else
    print_error "Environment variables not set correctly"
    VALIDATION_PASSED=false
fi

# Validate BigQuery access
if bq ls --project_id="$GCP_PROJECT_ID" &> /dev/null; then
    print_success "BigQuery access working"
else
    print_warning "BigQuery access could not be verified"
fi

# Validate dbt (if installed)
if command -v dbt &> /dev/null; then
    if dbt debug &> /dev/null; then
        print_success "dbt configuration valid"
    else
        print_warning "dbt configuration issues detected"
    fi
fi

# Step 8: Next Steps
print_header "Setup Complete!"

if [ "$VALIDATION_PASSED" = true ]; then
    print_success "Your environment is ready to use!"
else
    print_warning "Setup completed with warnings"
fi

echo -e "\n${BLUE}Next Steps:${NC}\n"
echo "1. Activate your environment:"
echo -e "   ${GREEN}source .env${NC}"
if [ -d venv ]; then
    echo -e "   ${GREEN}source venv/bin/activate${NC}"
fi

echo -e "\n2. Start the Getting Started tutorial:"
echo -e "   ${GREEN}cat tutorials/getting-started/README.md${NC}"

echo -e "\n3. Explore the knowledge base:"
echo "   - data-engineering-patterns.md"
echo "   - data-testing-patterns.md"
echo "   - playbooks.md"

echo -e "\n4. Run your first dbt model:"
echo -e "   ${GREEN}dbt run${NC}"

echo -e "\n${BLUE}Documentation:${NC}"
echo "   - Setup log: $SETUP_LOG"
echo "   - Configuration: .env"
echo "   - dbt profile: ~/.dbt/profiles.yml"

echo -e "\n${BLUE}Need help?${NC}"
echo "   - Check: onboarding/checklist.md"
echo "   - Review: tutorials/getting-started/"
echo "   - Ask Claude Code for assistance"

echo -e "\n${GREEN}Happy data engineering! 🚀${NC}\n"
