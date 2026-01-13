#!/usr/bin/env bash
#
# DecentClaude Data Utilities - Alias Installer
#
# This script automates the installation of command aliases for DecentClaude
# data utilities. It supports multiple installation methods and shell types.
#
# Usage:
#   ./install-aliases.sh [OPTIONS]
#
# Options:
#   --method <source|path|symlink>  Installation method (default: source)
#   --shell <bash|zsh|fish|auto>    Target shell (default: auto)
#   --uninstall                     Remove installed aliases
#   --dry-run                       Show what would be done without doing it
#   --help                          Show this help message
#
# Installation Methods:
#   source    - Add 'source aliases.sh' to shell config (recommended)
#   path      - Add bin directory to PATH
#   symlink   - Create symlinks in ~/.local/bin (requires ~/.local/bin in PATH)
#

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ALIASES_FILE="${SCRIPT_DIR}/aliases.sh"
DATA_UTILS_DIR="${SCRIPT_DIR}/data-utils"

# Default options
INSTALL_METHOD="source"
SHELL_TYPE="auto"
DRY_RUN=false
UNINSTALL=false

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# Helper Functions
# ============================================================================

print_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

show_help() {
    cat << 'EOF'
DecentClaude Alias Installer

Usage:
  ./install-aliases.sh [OPTIONS]

Options:
  --method <source|path|symlink>  Installation method (default: source)
  --shell <bash|zsh|fish|auto>    Target shell (default: auto)
  --uninstall                     Remove installed aliases
  --dry-run                       Show what would be done without doing it
  --help                          Show this help message

Installation Methods:

  source (recommended)
    Adds 'source /path/to/aliases.sh' to your shell configuration file.
    This loads the aliases each time you start a new shell session.

    Pros: Fast, works with all shells, easy to update
    Cons: Slight startup delay (negligible)

  path
    Adds the bin directory to your PATH environment variable.
    Allows you to run utilities directly by name (e.g., 'bq-profile').

    Pros: No aliases needed, works with all programs
    Cons: Longer command names, no shell completion improvements

  symlink
    Creates symbolic links in ~/.local/bin for each utility with short names.
    Requires ~/.local/bin to be in your PATH.

    Pros: Works system-wide, no shell config changes
    Cons: Requires manual updates, clutters ~/.local/bin

Examples:
  # Install with default method (source) for current shell
  ./install-aliases.sh

  # Install using PATH method for bash
  ./install-aliases.sh --method path --shell bash

  # Create symlinks
  ./install-aliases.sh --method symlink

  # Preview what would be installed
  ./install-aliases.sh --dry-run

  # Uninstall aliases
  ./install-aliases.sh --uninstall

EOF
}

detect_shell() {
    if [[ -n "${SHELL:-}" ]]; then
        basename "$SHELL"
    elif [[ -n "${ZSH_VERSION:-}" ]]; then
        echo "zsh"
    elif [[ -n "${BASH_VERSION:-}" ]]; then
        echo "bash"
    else
        echo "sh"
    fi
}

get_shell_config() {
    local shell_type="$1"
    case "$shell_type" in
        bash)
            if [[ -f "$HOME/.bashrc" ]]; then
                echo "$HOME/.bashrc"
            else
                echo "$HOME/.bash_profile"
            fi
            ;;
        zsh)
            echo "$HOME/.zshrc"
            ;;
        fish)
            echo "$HOME/.config/fish/config.fish"
            ;;
        *)
            print_error "Unsupported shell: $shell_type"
            return 1
            ;;
    esac
}

# ============================================================================
# Installation Methods
# ============================================================================

install_source() {
    local shell_type="$1"
    local config_file
    config_file="$(get_shell_config "$shell_type")"

    print_info "Installing aliases using source method for $shell_type"
    print_info "Config file: $config_file"

    # Check if aliases are already sourced
    if [[ -f "$config_file" ]] && grep -q "aliases.sh" "$config_file"; then
        print_warning "Aliases already configured in $config_file"
        return 0
    fi

    # Add source line to config
    local source_line="source '${ALIASES_FILE}'"

    if [[ "$DRY_RUN" == true ]]; then
        print_info "[DRY RUN] Would add to $config_file:"
        echo "  $source_line"
        return 0
    fi

    # Create config file if it doesn't exist
    if [[ ! -f "$config_file" ]]; then
        touch "$config_file"
    fi

    # Add source line with comments
    {
        echo ""
        echo "# DecentClaude Data Utilities aliases"
        echo "$source_line"
    } >> "$config_file"

    print_success "Aliases installed successfully!"
    print_info "Reload your shell or run: source $config_file"
}

install_path() {
    local shell_type="$1"
    local config_file
    config_file="$(get_shell_config "$shell_type")"

    print_info "Installing utilities using PATH method for $shell_type"
    print_info "Config file: $config_file"

    # Check if PATH is already configured
    if [[ -f "$config_file" ]] && grep -q "decentclaude.*bin" "$config_file"; then
        print_warning "PATH already configured in $config_file"
        return 0
    fi

    # Add PATH line to config
    local path_line="export PATH=\"\$PATH:${SCRIPT_DIR}\""

    if [[ "$DRY_RUN" == true ]]; then
        print_info "[DRY RUN] Would add to $config_file:"
        echo "  $path_line"
        return 0
    fi

    # Create config file if it doesn't exist
    if [[ ! -f "$config_file" ]]; then
        touch "$config_file"
    fi

    # Add PATH line with comments
    {
        echo ""
        echo "# DecentClaude Data Utilities PATH"
        echo "$path_line"
    } >> "$config_file"

    print_success "PATH configured successfully!"
    print_info "Reload your shell or run: source $config_file"
}

install_symlink() {
    local target_dir="$HOME/.local/bin"

    print_info "Installing utilities using symlink method"
    print_info "Target directory: $target_dir"

    # Create target directory if it doesn't exist
    if [[ ! -d "$target_dir" ]]; then
        if [[ "$DRY_RUN" == true ]]; then
            print_info "[DRY RUN] Would create directory: $target_dir"
        else
            mkdir -p "$target_dir"
            print_info "Created directory: $target_dir"
        fi
    fi

    # Check if target directory is in PATH
    if [[ ":$PATH:" != *":$target_dir:"* ]]; then
        print_warning "$target_dir is not in your PATH"
        print_info "Add it with: export PATH=\"\$PATH:$target_dir\""
    fi

    # Define alias mappings
    declare -A ALIASES=(
        # BigQuery
        ["bqp"]="bq-profile"
        ["bqe"]="bq-explain"
        ["bqo"]="bq-optimize"
        ["bql"]="bq-lineage"
        ["bqd"]="bq-schema-diff"
        ["bqc"]="bq-table-compare"
        ["bqx"]="bq-explore"
        ["bqb"]="bq-benchmark"
        # dbt
        ["dbtt"]="dbt-test-gen"
        ["dbtd"]="dbt-deps"
        # AI
        ["aig"]="ai-generate"
        ["aiq"]="ai-query"
        ["air"]="ai-review"
        ["aid"]="ai-docs"
        # SQLMesh
        ["smdiff"]="sqlmesh-diff"
        ["smmig"]="sqlmesh-migrate"
        ["smval"]="sqlmesh-validate"
        ["smviz"]="sqlmesh-visualize"
    )

    # Create symlinks
    local count=0
    for alias_name in "${!ALIASES[@]}"; do
        local util_name="${ALIASES[$alias_name]}"
        local source_file="${DATA_UTILS_DIR}/${util_name}"
        local target_file="${target_dir}/${alias_name}"

        if [[ ! -f "$source_file" ]]; then
            print_warning "Utility not found: $source_file"
            continue
        fi

        if [[ -e "$target_file" ]] && [[ ! -L "$target_file" ]]; then
            print_warning "File exists and is not a symlink: $target_file"
            continue
        fi

        if [[ "$DRY_RUN" == true ]]; then
            print_info "[DRY RUN] Would create symlink: $alias_name -> $util_name"
        else
            ln -sf "$source_file" "$target_file"
            ((count++))
        fi
    done

    if [[ "$DRY_RUN" == false ]]; then
        print_success "Created $count symlinks in $target_dir"
    fi
}

# ============================================================================
# Uninstallation
# ============================================================================

uninstall_aliases() {
    local shell_type="$1"
    local config_file
    config_file="$(get_shell_config "$shell_type")"

    print_info "Uninstalling DecentClaude aliases for $shell_type"
    print_info "Config file: $config_file"

    if [[ ! -f "$config_file" ]]; then
        print_warning "Config file not found: $config_file"
        return 0
    fi

    # Check if aliases are configured
    if ! grep -q "DecentClaude" "$config_file"; then
        print_info "No DecentClaude configuration found in $config_file"
        return 0
    fi

    if [[ "$DRY_RUN" == true ]]; then
        print_info "[DRY RUN] Would remove DecentClaude configuration from $config_file"
        return 0
    fi

    # Create backup
    local backup_file="${config_file}.decentclaude.backup"
    cp "$config_file" "$backup_file"
    print_info "Created backup: $backup_file"

    # Remove DecentClaude configuration
    sed -i.tmp '/# DecentClaude/,+2d' "$config_file"
    rm -f "${config_file}.tmp"

    print_success "DecentClaude aliases uninstalled"
    print_info "Backup saved to: $backup_file"
}

uninstall_symlinks() {
    local target_dir="$HOME/.local/bin"

    print_info "Removing DecentClaude symlinks from $target_dir"

    if [[ ! -d "$target_dir" ]]; then
        print_info "Directory not found: $target_dir"
        return 0
    fi

    # Find and remove symlinks pointing to our utilities
    local count=0
    while IFS= read -r -d '' link; do
        if [[ "$DRY_RUN" == true ]]; then
            print_info "[DRY RUN] Would remove symlink: $(basename "$link")"
        else
            rm "$link"
            ((count++))
        fi
    done < <(find "$target_dir" -type l -lname "${DATA_UTILS_DIR}/*" -print0)

    if [[ "$DRY_RUN" == false ]] && [[ $count -gt 0 ]]; then
        print_success "Removed $count symlinks from $target_dir"
    elif [[ "$DRY_RUN" == false ]]; then
        print_info "No DecentClaude symlinks found in $target_dir"
    fi
}

# ============================================================================
# Main
# ============================================================================

main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --method)
                INSTALL_METHOD="$2"
                shift 2
                ;;
            --shell)
                SHELL_TYPE="$2"
                shift 2
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --uninstall)
                UNINSTALL=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Run with --help for usage information"
                exit 1
                ;;
        esac
    done

    # Validate installation method
    if [[ ! "$INSTALL_METHOD" =~ ^(source|path|symlink)$ ]]; then
        print_error "Invalid installation method: $INSTALL_METHOD"
        echo "Valid methods: source, path, symlink"
        exit 1
    fi

    # Detect shell if auto
    if [[ "$SHELL_TYPE" == "auto" ]]; then
        SHELL_TYPE="$(detect_shell)"
        print_info "Detected shell: $SHELL_TYPE"
    fi

    # Validate shell type
    if [[ ! "$SHELL_TYPE" =~ ^(bash|zsh|fish)$ ]] && [[ "$INSTALL_METHOD" != "symlink" ]]; then
        print_error "Invalid or unsupported shell: $SHELL_TYPE"
        echo "Supported shells: bash, zsh, fish"
        exit 1
    fi

    # Check if aliases.sh exists
    if [[ ! -f "$ALIASES_FILE" ]]; then
        print_error "Aliases file not found: $ALIASES_FILE"
        exit 1
    fi

    # Check if data-utils directory exists
    if [[ ! -d "$DATA_UTILS_DIR" ]]; then
        print_error "Data utilities directory not found: $DATA_UTILS_DIR"
        exit 1
    fi

    # Perform installation or uninstallation
    if [[ "$UNINSTALL" == true ]]; then
        if [[ "$INSTALL_METHOD" == "symlink" ]]; then
            uninstall_symlinks
        else
            uninstall_aliases "$SHELL_TYPE"
        fi
    else
        case "$INSTALL_METHOD" in
            source)
                install_source "$SHELL_TYPE"
                ;;
            path)
                install_path "$SHELL_TYPE"
                ;;
            symlink)
                install_symlink
                ;;
        esac
    fi

    # Print usage hint
    if [[ "$UNINSTALL" == false ]] && [[ "$DRY_RUN" == false ]]; then
        echo ""
        print_info "To start using the aliases:"
        if [[ "$INSTALL_METHOD" == "symlink" ]]; then
            echo "  The aliases are ready to use immediately!"
        else
            local config_file
            config_file="$(get_shell_config "$SHELL_TYPE")"
            echo "  source $config_file"
            echo "  OR start a new shell session"
        fi
        echo ""
        print_info "Run 'decentclaude-aliases' or 'dca' to see all available aliases"
    fi
}

# Run main function
main "$@"
