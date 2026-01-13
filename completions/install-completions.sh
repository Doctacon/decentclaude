#!/usr/bin/env bash
# Installation script for bash/zsh completion scripts
# Supports both user and system-wide installation

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Functions
print_info() {
    echo -e "${BLUE}[INFO]${RESET} $*"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${RESET} $*"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${RESET} $*"
}

print_error() {
    echo -e "${RED}[ERROR]${RESET} $*"
}

detect_shell() {
    local shell_name
    shell_name="$(basename "$SHELL")"

    case "$shell_name" in
        bash|sh)
            echo "bash"
            ;;
        zsh)
            echo "zsh"
            ;;
        *)
            echo "unknown"
            ;;
    esac
}

install_bash_completion() {
    local system_wide="${1:-false}"
    local source_file="$SCRIPT_DIR/bash_completion"

    if [[ ! -f "$source_file" ]]; then
        print_error "Bash completion file not found: $source_file"
        return 1
    fi

    if [[ "$system_wide" == "true" ]]; then
        # System-wide installation (requires sudo)
        if [[ ! -d /etc/bash_completion.d ]]; then
            print_warning "/etc/bash_completion.d not found, creating it"
            sudo mkdir -p /etc/bash_completion.d
        fi

        print_info "Installing bash completion system-wide to /etc/bash_completion.d/"
        sudo cp "$source_file" /etc/bash_completion.d/bq-utils
        print_success "Bash completion installed system-wide"
    else
        # User installation
        local completion_dir="$HOME/.bash_completion.d"

        if [[ ! -d "$completion_dir" ]]; then
            print_info "Creating $completion_dir"
            mkdir -p "$completion_dir"
        fi

        print_info "Installing bash completion to $completion_dir/"
        cp "$source_file" "$completion_dir/bq-utils"
        print_success "Bash completion installed to $completion_dir/bq-utils"

        # Check if it's sourced in .bashrc
        local bashrc="$HOME/.bashrc"
        if [[ -f "$bashrc" ]]; then
            if ! grep -q "bash_completion.d/bq-utils" "$bashrc"; then
                print_info "Adding completion source to $bashrc"
                cat >> "$bashrc" << 'EOF'

# BigQuery utilities completion
if [ -f "$HOME/.bash_completion.d/bq-utils" ]; then
    . "$HOME/.bash_completion.d/bq-utils"
fi
EOF
                print_success "Added source line to $bashrc"
            else
                print_info "Completion already sourced in $bashrc"
            fi
        fi

        # Also check .bash_profile for macOS
        if [[ "$(uname)" == "Darwin" ]] && [[ -f "$HOME/.bash_profile" ]]; then
            if ! grep -q "bash_completion.d/bq-utils" "$HOME/.bash_profile"; then
                print_info "Adding completion source to .bash_profile (macOS)"
                cat >> "$HOME/.bash_profile" << 'EOF'

# BigQuery utilities completion
if [ -f "$HOME/.bash_completion.d/bq-utils" ]; then
    . "$HOME/.bash_completion.d/bq-utils"
fi
EOF
                print_success "Added source line to .bash_profile"
            fi
        fi
    fi
}

install_zsh_completion() {
    local system_wide="${1:-false}"
    local source_file="$SCRIPT_DIR/zsh_completion"

    if [[ ! -f "$source_file" ]]; then
        print_error "Zsh completion file not found: $source_file"
        return 1
    fi

    if [[ "$system_wide" == "true" ]]; then
        # System-wide installation (requires sudo)
        local completion_dir="/usr/local/share/zsh/site-functions"

        if [[ ! -d "$completion_dir" ]]; then
            print_warning "$completion_dir not found, creating it"
            sudo mkdir -p "$completion_dir"
        fi

        print_info "Installing zsh completion system-wide to $completion_dir/"
        sudo cp "$source_file" "$completion_dir/_bq-utils"
        print_success "Zsh completion installed system-wide"
    else
        # User installation
        local completion_dir="$HOME/.zsh/completion"

        if [[ ! -d "$completion_dir" ]]; then
            print_info "Creating $completion_dir"
            mkdir -p "$completion_dir"
        fi

        print_info "Installing zsh completion to $completion_dir/"
        cp "$source_file" "$completion_dir/_bq-utils"
        print_success "Zsh completion installed to $completion_dir/_bq-utils"

        # Check if completion directory is in fpath
        local zshrc="$HOME/.zshrc"
        if [[ -f "$zshrc" ]]; then
            if ! grep -q "fpath.*\.zsh/completion" "$zshrc"; then
                print_info "Adding completion directory to fpath in $zshrc"
                cat >> "$zshrc" << 'EOF'

# BigQuery utilities completion
fpath=(~/.zsh/completion $fpath)
autoload -Uz compinit
compinit
EOF
                print_success "Added fpath configuration to $zshrc"
            else
                print_info "Completion directory already in fpath"
            fi
        fi
    fi
}

create_cache_directory() {
    local cache_dir="$HOME/.cache"
    if [[ ! -d "$cache_dir" ]]; then
        print_info "Creating cache directory: $cache_dir"
        mkdir -p "$cache_dir"
    fi
}

print_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Install bash/zsh completion scripts for BigQuery utilities

OPTIONS:
    -h, --help          Show this help message
    -s, --system        Install system-wide (requires sudo)
    -u, --user          Install for current user only (default)
    -b, --bash          Install bash completion only
    -z, --zsh           Install zsh completion only
    --uninstall         Uninstall completion scripts

EXAMPLES:
    # Install for current user (auto-detect shell)
    $0

    # Install system-wide
    $0 --system

    # Install only bash completion
    $0 --bash

    # Uninstall
    $0 --uninstall

EOF
}

uninstall_completions() {
    local shell_type="$1"

    print_info "Uninstalling completions for $shell_type"

    if [[ "$shell_type" == "bash" || "$shell_type" == "auto" ]]; then
        # Remove user installation
        if [[ -f "$HOME/.bash_completion.d/bq-utils" ]]; then
            rm "$HOME/.bash_completion.d/bq-utils"
            print_success "Removed user bash completion"
        fi

        # Remove system installation
        if [[ -f /etc/bash_completion.d/bq-utils ]]; then
            sudo rm /etc/bash_completion.d/bq-utils
            print_success "Removed system bash completion"
        fi
    fi

    if [[ "$shell_type" == "zsh" || "$shell_type" == "auto" ]]; then
        # Remove user installation
        if [[ -f "$HOME/.zsh/completion/_bq-utils" ]]; then
            rm "$HOME/.zsh/completion/_bq-utils"
            print_success "Removed user zsh completion"
        fi

        # Remove system installation
        if [[ -f /usr/local/share/zsh/site-functions/_bq-utils ]]; then
            sudo rm /usr/local/share/zsh/site-functions/_bq-utils
            print_success "Removed system zsh completion"
        fi
    fi

    print_warning "Note: You may need to manually remove sourcing lines from your shell RC files"
}

main() {
    local system_wide=false
    local shell_type="auto"
    local uninstall=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                print_usage
                exit 0
                ;;
            -s|--system)
                system_wide=true
                shift
                ;;
            -u|--user)
                system_wide=false
                shift
                ;;
            -b|--bash)
                shell_type="bash"
                shift
                ;;
            -z|--zsh)
                shell_type="zsh"
                shift
                ;;
            --uninstall)
                uninstall=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done

    # Handle uninstall
    if [[ "$uninstall" == "true" ]]; then
        uninstall_completions "$shell_type"
        exit 0
    fi

    # Auto-detect shell if not specified
    if [[ "$shell_type" == "auto" ]]; then
        shell_type="$(detect_shell)"
        if [[ "$shell_type" == "unknown" ]]; then
            print_error "Could not detect shell type. Please specify --bash or --zsh"
            exit 1
        fi
        print_info "Detected shell: $shell_type"
    fi

    # Create cache directory
    create_cache_directory

    # Install completion based on shell type
    case "$shell_type" in
        bash)
            install_bash_completion "$system_wide"
            ;;
        zsh)
            install_zsh_completion "$system_wide"
            ;;
        *)
            print_error "Unsupported shell: $shell_type"
            exit 1
            ;;
    esac

    # Print next steps
    echo
    print_success "Installation complete!"
    echo
    print_info "Next steps:"
    if [[ "$system_wide" == "true" ]]; then
        echo "  1. Restart your shell or run: exec $SHELL"
    else
        case "$shell_type" in
            bash)
                echo "  1. Restart your shell or run: source ~/.bashrc"
                ;;
            zsh)
                echo "  1. Restart your shell or run: source ~/.zshrc"
                ;;
        esac
    fi
    echo "  2. Try typing 'bq-profile ' and press TAB to test completion"
    echo "  3. Use 'bq-profile --<TAB>' to see available options"
    echo
    print_info "To populate the BigQuery table cache, the completion will attempt to"
    print_info "fetch tables from your default GCP project in the background."
    print_info "This requires 'bq' and 'jq' commands to be installed."
}

main "$@"
