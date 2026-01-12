#!/usr/bin/env bash
# install-hooks.sh - Install worktree-aware git hooks
#
# Usage: ./install-hooks.sh [--global|--local]
#
# Options:
#   --global    Install hooks globally for all worktrees (in bare repo)
#   --local     Install hooks only in current worktree (default)

set -euo pipefail

MODE="local"

if [[ $# -gt 0 ]]; then
    case $1 in
        --global)
            MODE="global"
            ;;
        --local)
            MODE="local"
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--global|--local]"
            exit 1
            ;;
    esac
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$MODE" == "global" ]]; then
    # Install in bare repo (affects all worktrees)
    HOOKS_DIR="$(git rev-parse --git-common-dir)/hooks"
    echo "Installing hooks globally for all worktrees..."
else
    # Install in current worktree only
    HOOKS_DIR="$(git rev-parse --git-dir)/hooks"
    echo "Installing hooks for current worktree..."
fi

mkdir -p "$HOOKS_DIR"

# Install each hook
for hook in post-checkout pre-commit post-merge; do
    if [[ -f "$SCRIPT_DIR/$hook" ]]; then
        cp "$SCRIPT_DIR/$hook" "$HOOKS_DIR/$hook"
        chmod +x "$HOOKS_DIR/$hook"
        echo "  ✓ Installed $hook"
    fi
done

echo ""
echo "Hooks installed successfully in: $HOOKS_DIR"
echo ""

if [[ "$MODE" == "global" ]]; then
    echo "These hooks will run in all worktrees."
else
    echo "These hooks will only run in this worktree."
    echo "To install for all worktrees, run: $0 --global"
fi
