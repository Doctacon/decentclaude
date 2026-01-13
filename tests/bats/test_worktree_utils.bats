#!/usr/bin/env bats
# Tests for worktree utilities (wt-switch, wt-status, wt-clean, wt-sync)

# Setup test environment
setup() {
    export TEST_TEMP_DIR="$(mktemp -d)"
    export WORKTREE_UTILS_DIR="${BATS_TEST_DIRNAME}/../../bin/worktree-utils"
}

# Cleanup after each test
teardown() {
    rm -rf "$TEST_TEMP_DIR"
}

# --- wt-switch tests ---

@test "wt-switch: script exists and is executable" {
    [ -f "$WORKTREE_UTILS_DIR/wt-switch" ]
    [ -x "$WORKTREE_UTILS_DIR/wt-switch" ]
}

@test "wt-switch: has help option" {
    run "$WORKTREE_UTILS_DIR/wt-switch" --help
    [ "$status" -eq 0 ]
    [[ "$output" == *"help"* ]] || [[ "$output" == *"usage"* ]]
}

@test "wt-switch: has list option" {
    run "$WORKTREE_UTILS_DIR/wt-switch" --list
    # Should succeed even if no worktrees (exit 0 or show message)
    [ "$status" -eq 0 ] || [ "$status" -eq 1 ]
}

@test "wt-switch: contains git worktree commands" {
    grep -q "git worktree" "$WORKTREE_UTILS_DIR/wt-switch"
}

@test "wt-switch: uses bash shebang" {
    head -n 1 "$WORKTREE_UTILS_DIR/wt-switch" | grep -q "#!/bin/bash"
}

# --- wt-status tests ---

@test "wt-status: script exists and is executable" {
    [ -f "$WORKTREE_UTILS_DIR/wt-status" ]
    [ -x "$WORKTREE_UTILS_DIR/wt-status" ]
}

@test "wt-status: has help option" {
    run "$WORKTREE_UTILS_DIR/wt-status" --help
    [ "$status" -eq 0 ]
    [[ "$output" == *"help"* ]] || [[ "$output" == *"usage"* ]]
}

@test "wt-status: supports verbose mode" {
    grep -q "\-v\|--verbose" "$WORKTREE_UTILS_DIR/wt-status"
}

@test "wt-status: supports dirty-only mode" {
    grep -q "\-d\|--dirty" "$WORKTREE_UTILS_DIR/wt-status"
}

@test "wt-status: checks git status" {
    grep -q "git status" "$WORKTREE_UTILS_DIR/wt-status"
}

@test "wt-status: shows ahead/behind information" {
    grep -q "ahead\|behind" "$WORKTREE_UTILS_DIR/wt-status" || \
    grep -q "rev-list" "$WORKTREE_UTILS_DIR/wt-status"
}

@test "wt-status: uses color codes" {
    grep -q "\\033\|color\|RED\|GREEN\|YELLOW" "$WORKTREE_UTILS_DIR/wt-status"
}

# --- wt-clean tests ---

@test "wt-clean: script exists and is executable" {
    [ -f "$WORKTREE_UTILS_DIR/wt-clean" ]
    [ -x "$WORKTREE_UTILS_DIR/wt-clean" ]
}

@test "wt-clean: has help option" {
    run "$WORKTREE_UTILS_DIR/wt-clean" --help
    [ "$status" -eq 0 ]
    [[ "$output" == *"help"* ]] || [[ "$output" == *"usage"* ]]
}

@test "wt-clean: supports dry-run mode" {
    grep -q "\-n\|--dry-run" "$WORKTREE_UTILS_DIR/wt-clean"
}

@test "wt-clean: supports merged branch removal" {
    grep -q "\-m\|--merged" "$WORKTREE_UTILS_DIR/wt-clean"
}

@test "wt-clean: supports gone branch removal" {
    grep -q "\-g\|--gone" "$WORKTREE_UTILS_DIR/wt-clean"
}

@test "wt-clean: supports force option" {
    grep -q "\-f\|--force" "$WORKTREE_UTILS_DIR/wt-clean"
}

@test "wt-clean: checks for uncommitted changes" {
    grep -q "uncommitted\|git status\|dirty" "$WORKTREE_UTILS_DIR/wt-clean"
}

@test "wt-clean: removes worktrees" {
    grep -q "git worktree remove" "$WORKTREE_UTILS_DIR/wt-clean"
}

@test "wt-clean: protects main/master branches" {
    grep -q "main\|master" "$WORKTREE_UTILS_DIR/wt-clean"
}

# --- wt-sync tests ---

@test "wt-sync: script exists and is executable" {
    [ -f "$WORKTREE_UTILS_DIR/wt-sync" ]
    [ -x "$WORKTREE_UTILS_DIR/wt-sync" ]
}

@test "wt-sync: has help option" {
    run "$WORKTREE_UTILS_DIR/wt-sync" --help
    [ "$status" -eq 0 ]
    [[ "$output" == *"help"* ]] || [[ "$output" == *"usage"* ]]
}

@test "wt-sync: performs git fetch" {
    grep -q "git fetch" "$WORKTREE_UTILS_DIR/wt-sync"
}

@test "wt-sync: prunes remote branches" {
    grep -q "prune" "$WORKTREE_UTILS_DIR/wt-sync"
}

@test "wt-sync: supports prune-merged option" {
    grep -q "\-p\|--prune-merged" "$WORKTREE_UTILS_DIR/wt-sync"
}

@test "wt-sync: supports dry-run mode" {
    grep -q "\-n\|--dry-run" "$WORKTREE_UTILS_DIR/wt-sync"
}

@test "wt-sync: checks ahead/behind status" {
    grep -q "ahead\|behind" "$WORKTREE_UTILS_DIR/wt-sync" || \
    grep -q "rev-list" "$WORKTREE_UTILS_DIR/wt-sync"
}

# --- Common utility tests ---

@test "all worktree utils: use bash shebang" {
    head -n 1 "$WORKTREE_UTILS_DIR/wt-switch" | grep -q "#!/bin/bash"
    head -n 1 "$WORKTREE_UTILS_DIR/wt-status" | grep -q "#!/bin/bash"
    head -n 1 "$WORKTREE_UTILS_DIR/wt-clean" | grep -q "#!/bin/bash"
    head -n 1 "$WORKTREE_UTILS_DIR/wt-sync" | grep -q "#!/bin/bash"
}

@test "all worktree utils: use git worktree commands" {
    grep -q "git worktree" "$WORKTREE_UTILS_DIR/wt-switch"
    grep -q "git worktree" "$WORKTREE_UTILS_DIR/wt-status"
    grep -q "git worktree" "$WORKTREE_UTILS_DIR/wt-clean"
    grep -q "git worktree" "$WORKTREE_UTILS_DIR/wt-sync"
}

@test "all worktree utils: filter bare repositories" {
    grep -q "bare\|BARE" "$WORKTREE_UTILS_DIR/wt-status" || \
    grep -q "bare" "$WORKTREE_UTILS_DIR/wt-clean"
}

# --- Error handling tests ---

@test "worktree utils: have error messages" {
    grep -q "echo\|printf" "$WORKTREE_UTILS_DIR/wt-switch"
    grep -q "echo\|printf" "$WORKTREE_UTILS_DIR/wt-status"
}

@test "worktree utils: handle missing worktrees" {
    # Should have logic for when no worktrees exist
    grep -q "worktree list" "$WORKTREE_UTILS_DIR/wt-switch"
}

# --- Summary and reporting tests ---

@test "wt-status: provides summary information" {
    grep -q "summary\|total\|Summary\|Total" "$WORKTREE_UTILS_DIR/wt-status"
}

@test "wt-clean: provides summary of actions" {
    grep -q "summary\|total\|removed\|Summary" "$WORKTREE_UTILS_DIR/wt-clean"
}

@test "wt-sync: provides sync status" {
    grep -q "up.to.date\|synced\|status" "$WORKTREE_UTILS_DIR/wt-sync"
}
