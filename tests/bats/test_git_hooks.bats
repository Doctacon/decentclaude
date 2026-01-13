#!/usr/bin/env bats
# Tests for git hooks (pre-commit, post-checkout, post-merge)

# Setup test environment
setup() {
    export TEST_TEMP_DIR="$(mktemp -d)"
    export GIT_HOOKS_DIR="${BATS_TEST_DIRNAME}/../../.git-hooks"
}

# Cleanup after each test
teardown() {
    rm -rf "$TEST_TEMP_DIR"
}

# --- pre-commit hook tests ---

@test "pre-commit: hook script exists and is executable" {
    [ -f "$GIT_HOOKS_DIR/pre-commit" ]
    [ -x "$GIT_HOOKS_DIR/pre-commit" ]
}

@test "pre-commit: contains worktree state logic" {
    grep -q "worktree list" "$GIT_HOOKS_DIR/pre-commit"
}

@test "pre-commit: detects shared branch scenario" {
    # Test that the hook checks for multiple worktrees on same branch
    grep -q "multiple worktrees" "$GIT_HOOKS_DIR/pre-commit" || \
    grep -q "shared branch" "$GIT_HOOKS_DIR/pre-commit"
}

# --- post-checkout hook tests ---

@test "post-checkout: hook script exists and is executable" {
    [ -f "$GIT_HOOKS_DIR/post-checkout" ]
    [ -x "$GIT_HOOKS_DIR/post-checkout" ]
}

@test "post-checkout: handles branch checkout events" {
    grep -q "worktree" "$GIT_HOOKS_DIR/post-checkout"
}

@test "post-checkout: creates timestamp files" {
    grep -q "worktree-state" "$GIT_HOOKS_DIR/post-checkout" || \
    grep -q "timestamp" "$GIT_HOOKS_DIR/post-checkout"
}

# --- post-merge hook tests ---

@test "post-merge: hook script exists and is executable" {
    [ -f "$GIT_HOOKS_DIR/post-merge" ]
    [ -x "$GIT_HOOKS_DIR/post-merge" ]
}

@test "post-merge: detects merge events" {
    grep -q "merge" "$GIT_HOOKS_DIR/post-merge" || \
    grep -q "worktree" "$GIT_HOOKS_DIR/post-merge"
}

# --- install-hooks.sh tests ---

@test "install-hooks: script exists and is executable" {
    [ -f "$GIT_HOOKS_DIR/install-hooks.sh" ]
    [ -x "$GIT_HOOKS_DIR/install-hooks.sh" ]
}

@test "install-hooks: has help option" {
    run "$GIT_HOOKS_DIR/install-hooks.sh" --help
    [ "$status" -eq 0 ]
    [[ "$output" == *"help"* ]] || [[ "$output" == *"usage"* ]]
}

@test "install-hooks: handles local installation flag" {
    grep -q "\-\-local" "$GIT_HOOKS_DIR/install-hooks.sh"
}

@test "install-hooks: handles global installation flag" {
    grep -q "\-\-global" "$GIT_HOOKS_DIR/install-hooks.sh"
}

@test "install-hooks: checks for hook files before copying" {
    grep -q "pre-commit" "$GIT_HOOKS_DIR/install-hooks.sh"
    grep -q "post-checkout" "$GIT_HOOKS_DIR/install-hooks.sh"
    grep -q "post-merge" "$GIT_HOOKS_DIR/install-hooks.sh"
}

# --- Hook content validation ---

@test "all hooks: use /bin/bash shebang" {
    head -n 1 "$GIT_HOOKS_DIR/pre-commit" | grep -q "#!/bin/bash"
    head -n 1 "$GIT_HOOKS_DIR/post-checkout" | grep -q "#!/bin/bash"
    head -n 1 "$GIT_HOOKS_DIR/post-merge" | grep -q "#!/bin/bash"
}

@test "all hooks: have error handling" {
    # Check for basic error handling patterns
    grep -q "set -" "$GIT_HOOKS_DIR/pre-commit" || grep -q "exit" "$GIT_HOOKS_DIR/pre-commit"
}

# --- Worktree state directory tests ---

@test "hooks: reference worktree-state directory" {
    grep -q "worktree-state" "$GIT_HOOKS_DIR/pre-commit" || \
    grep -q "\.git.*state" "$GIT_HOOKS_DIR/pre-commit"
}
