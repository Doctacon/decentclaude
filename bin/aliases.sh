#!/usr/bin/env bash
#
# DecentClaude Data Utilities - Command Aliases
#
# This file provides short aliases for frequently used data utilities.
# These aliases make it faster to run common data engineering commands.
#
# INSTALLATION:
#   Option 1 - Source in your shell configuration:
#     echo 'source /path/to/aliases.sh' >> ~/.bashrc  # bash
#     echo 'source /path/to/aliases.sh' >> ~/.zshrc   # zsh
#
#   Option 2 - Use the automated installer:
#     ./bin/install-aliases.sh
#
#   Option 3 - Add bin directory to PATH:
#     echo 'export PATH="$PATH:/path/to/rig/bin"' >> ~/.bashrc
#
# USAGE:
#   After sourcing, use short aliases instead of full command names:
#     bqp my-project.dataset.table    # instead of bq-profile
#     aig --type model                # instead of ai-generate
#
# SUPPORTED SHELLS: bash, zsh
#

# Get the directory where this script is located
# Support both bash and zsh
if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [[ -n "${(%):-%x}" ]]; then
    # zsh - use ${(%):-%x} to get the script path
    SCRIPT_DIR="$(cd "$(dirname "${(%):-%x}")" && pwd)"
else
    # Fallback
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
fi
DATA_UTILS_DIR="${SCRIPT_DIR}/data-utils"

# Check if data-utils directory exists
if [[ ! -d "${DATA_UTILS_DIR}" ]]; then
    echo "Error: data-utils directory not found at ${DATA_UTILS_DIR}" >&2
    return 1 2>/dev/null || exit 1
fi

# ============================================================================
# BigQuery Utilities
# ============================================================================

alias bqp="${DATA_UTILS_DIR}/bq-profile"
alias bqe="${DATA_UTILS_DIR}/bq-explain"
alias bqo="${DATA_UTILS_DIR}/bq-optimize"
alias bql="${DATA_UTILS_DIR}/bq-lineage"
alias bqd="${DATA_UTILS_DIR}/bq-schema-diff"
alias bqc="${DATA_UTILS_DIR}/bq-table-compare"
alias bqx="${DATA_UTILS_DIR}/bq-explore"
alias bqb="${DATA_UTILS_DIR}/bq-benchmark"
alias bqcost="${DATA_UTILS_DIR}/bq-query-cost"
alias bqpart="${DATA_UTILS_DIR}/bq-partition-info"
alias bqrep="${DATA_UTILS_DIR}/bq-cost-report"

# ============================================================================
# dbt Utilities
# ============================================================================

alias dbtt="${DATA_UTILS_DIR}/dbt-test-gen"
alias dbtd="${DATA_UTILS_DIR}/dbt-deps"
alias dbtserve="${DATA_UTILS_DIR}/dbt-docs-serve"
alias dbts="${DATA_UTILS_DIR}/dbt-model-search"

# ============================================================================
# SQLMesh Utilities
# ============================================================================

alias smdiff="${DATA_UTILS_DIR}/sqlmesh-diff"
alias smmig="${DATA_UTILS_DIR}/sqlmesh-migrate"
alias smval="${DATA_UTILS_DIR}/sqlmesh-validate"
alias smviz="${DATA_UTILS_DIR}/sqlmesh-visualize"

# ============================================================================
# AI Generation Utilities
# ============================================================================

alias aig="${DATA_UTILS_DIR}/ai-generate"
alias aiq="${DATA_UTILS_DIR}/ai-query"
alias air="${DATA_UTILS_DIR}/ai-review"
alias aid="${DATA_UTILS_DIR}/ai-docs"

# ============================================================================
# Debug Utilities
# ============================================================================

if [[ -f "${SCRIPT_DIR}/debug-utils/ai-debug" ]]; then
    alias aidbg="${SCRIPT_DIR}/debug-utils/ai-debug"
fi

# ============================================================================
# Incident Response Utilities
# ============================================================================

INCIDENT_DIR="${SCRIPT_DIR}/incident-response"

if [[ -d "${INCIDENT_DIR}" ]]; then
    alias inc="${INCIDENT_DIR}/incident-report"
    alias inct="${INCIDENT_DIR}/incident-timeline"
    alias incpm="${INCIDENT_DIR}/incident-postmortem"
    alias runbook="${INCIDENT_DIR}/runbook-tracker"
fi

# ============================================================================
# Knowledge Base Utilities
# ============================================================================

if [[ -f "${SCRIPT_DIR}/kb" ]]; then
    alias kb="${SCRIPT_DIR}/kb"
fi

if [[ -f "${SCRIPT_DIR}/kb-web" ]]; then
    alias kbw="${SCRIPT_DIR}/kb-web"
fi

# ============================================================================
# Helper Functions
# ============================================================================

# List all available aliases
decentclaude-aliases() {
    cat << 'EOF'
DecentClaude Data Utilities - Available Aliases

BigQuery Utilities:
  bqp         bq-profile           Generate comprehensive data profiles
  bqe         bq-explain           Visualize query execution plans
  bqo         bq-optimize          Analyze queries and suggest optimizations
  bql         bq-lineage           Explore table dependencies
  bqd         bq-schema-diff       Compare schemas of two tables
  bqc         bq-table-compare     Comprehensive table comparison
  bqx         bq-explore           Interactive TUI for exploring datasets
  bqb         bq-benchmark         Benchmark query performance
  bqcost      bq-query-cost        Estimate query costs
  bqpart      bq-partition-info    Analyze partitioning configuration
  bqrep       bq-cost-report       Analyze historical costs

dbt Utilities:
  dbtt        dbt-test-gen         Auto-generate dbt tests
  dbtd        dbt-deps             Visualize dbt model dependencies
  dbtserve    dbt-docs-serve       Enhanced local docs server
  dbts        dbt-model-search     Search models by name or description

SQLMesh Utilities:
  smdiff      sqlmesh-diff         Show model diffs
  smmig       sqlmesh-migrate      Migrate SQLMesh project
  smval       sqlmesh-validate     Validate SQLMesh models
  smviz       sqlmesh-visualize    Visualize SQLMesh lineage

AI Generation:
  aig         ai-generate          AI-powered code generation
  aiq         ai-query             Natural language to SQL
  air         ai-review            AI-powered code reviewer
  aid         ai-docs              AI-powered documentation

Debug & Incident Response:
  aidbg       ai-debug             Intelligent error analysis
  inc         incident-report      Generate incident reports
  inct        incident-timeline    Track incident timelines
  incpm       incident-postmortem  Generate post-mortem reports
  runbook     runbook-tracker      Track runbook execution

Knowledge Base:
  kb          kb                   Knowledge base CLI
  kbw         kb-web               Knowledge base web interface

Usage Examples:
  bqp my-project.dataset.table              # Profile a table
  bqe "SELECT * FROM dataset.table"         # Explain a query
  aig --type model --name users             # Generate a dbt model
  aiq "show me top 10 users by revenue"     # Natural language query
  kb search "partition optimization"        # Search knowledge base

For more information, see:
  docs/guides/command-aliases.md
EOF
}

# Shorter alias for listing aliases
alias dca='decentclaude-aliases'

# Print success message when sourced
if [[ "${BASH_SOURCE[0]:-}" != "${0:-}" ]] || [[ -n "${ZSH_VERSION:-}" && "${(%):-%N}" != "${0}" ]]; then
    echo "DecentClaude aliases loaded successfully!"
    echo "Run 'decentclaude-aliases' or 'dca' to see all available aliases."
fi
