#!/usr/bin/env bash
# Test script for shell completion functionality
# This script verifies that completion is properly installed and working

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

# Counters
TESTS_PASSED=0
TESTS_FAILED=0

print_header() {
    echo -e "\n${BLUE}===========================================================${RESET}"
    echo -e "${BLUE}$1${RESET}"
    echo -e "${BLUE}===========================================================${RESET}\n"
}

print_test() {
    echo -e "${YELLOW}Testing:${RESET} $1"
}

print_pass() {
    echo -e "${GREEN}✓ PASS:${RESET} $1"
    ((TESTS_PASSED++))
}

print_fail() {
    echo -e "${RED}✗ FAIL:${RESET} $1"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${BLUE}Info:${RESET} $1"
}

# Detect shell
SHELL_NAME="$(basename "$SHELL")"

print_header "Shell Completion Test Suite"
echo "Shell: $SHELL_NAME"
echo "User: $USER"
echo "Home: $HOME"
echo

# Test 1: Check shell type
print_header "Test 1: Shell Detection"
print_test "Detecting shell type"

case "$SHELL_NAME" in
    bash|sh)
        print_pass "Bash shell detected"
        SHELL_TYPE="bash"
        ;;
    zsh)
        print_pass "Zsh shell detected"
        SHELL_TYPE="zsh"
        ;;
    *)
        print_fail "Unsupported shell: $SHELL_NAME"
        SHELL_TYPE="unknown"
        ;;
esac

# Test 2: Check completion files exist
print_header "Test 2: Completion Files"

if [[ "$SHELL_TYPE" == "bash" ]]; then
    print_test "Checking for bash completion file"

    if [[ -f "$HOME/.bash_completion.d/bq-utils" ]]; then
        print_pass "User completion file exists: ~/.bash_completion.d/bq-utils"
    elif [[ -f /etc/bash_completion.d/bq-utils ]]; then
        print_pass "System completion file exists: /etc/bash_completion.d/bq-utils"
    else
        print_fail "No bash completion file found"
        print_info "Run: ./install-completions.sh --bash"
    fi

    print_test "Checking if completion is sourced"
    if [[ -f "$HOME/.bashrc" ]] && grep -q "bq-utils" "$HOME/.bashrc"; then
        print_pass "Completion is sourced in ~/.bashrc"
    elif [[ -f "$HOME/.bash_profile" ]] && grep -q "bq-utils" "$HOME/.bash_profile"; then
        print_pass "Completion is sourced in ~/.bash_profile"
    else
        print_fail "Completion not sourced in shell RC file"
        print_info "Add source line to ~/.bashrc or ~/.bash_profile"
    fi

elif [[ "$SHELL_TYPE" == "zsh" ]]; then
    print_test "Checking for zsh completion file"

    if [[ -f "$HOME/.zsh/completion/_bq-utils" ]]; then
        print_pass "User completion file exists: ~/.zsh/completion/_bq-utils"
    elif [[ -f /usr/local/share/zsh/site-functions/_bq-utils ]]; then
        print_pass "System completion file exists: /usr/local/share/zsh/site-functions/_bq-utils"
    else
        print_fail "No zsh completion file found"
        print_info "Run: ./install-completions.sh --zsh"
    fi

    print_test "Checking fpath configuration"
    if echo "$fpath" | grep -q "completion" 2>/dev/null; then
        print_pass "Completion directory is in fpath"
    else
        print_fail "Completion directory not in fpath"
        print_info "Add to ~/.zshrc: fpath=(~/.zsh/completion \$fpath)"
    fi
fi

# Test 3: Check completion functions loaded
print_header "Test 3: Completion Functions"

if [[ "$SHELL_TYPE" == "bash" ]]; then
    print_test "Checking if _bq_complete function exists"
    if type _bq_complete &>/dev/null; then
        print_pass "Completion function loaded"
    else
        print_fail "Completion function not loaded"
        print_info "Reload shell: exec \$SHELL"
    fi

    print_test "Checking if completion is registered for bq-profile"
    if complete -p bq-profile 2>/dev/null | grep -q "_bq_complete"; then
        print_pass "Completion registered for bq-profile"
    else
        print_fail "Completion not registered for bq-profile"
        print_info "Source the completion file or reload shell"
    fi

elif [[ "$SHELL_TYPE" == "zsh" ]]; then
    print_test "Checking if compinit is loaded"
    if whence compinit &>/dev/null; then
        print_pass "compinit is available"
    else
        print_fail "compinit not loaded"
        print_info "Add to ~/.zshrc: autoload -Uz compinit; compinit"
    fi

    print_test "Checking if _bq_utils function exists"
    if whence _bq_utils &>/dev/null; then
        print_pass "Completion function loaded"
    else
        print_fail "Completion function not loaded"
        print_info "Reload shell: exec \$SHELL"
    fi
fi

# Test 4: Check prerequisites for table completion
print_header "Test 4: Prerequisites for Table ID Completion"

print_test "Checking for 'bq' command"
if command -v bq &>/dev/null; then
    print_pass "bq command found: $(which bq)"
else
    print_fail "bq command not found"
    print_info "Install Google Cloud SDK: https://cloud.google.com/sdk/docs/install"
fi

print_test "Checking for 'jq' command"
if command -v jq &>/dev/null; then
    print_pass "jq command found: $(which jq)"
else
    print_fail "jq command not found"
    print_info "Install jq: brew install jq (macOS) or apt-get install jq (Linux)"
fi

print_test "Checking for 'gcloud' command"
if command -v gcloud &>/dev/null; then
    print_pass "gcloud command found: $(which gcloud)"
else
    print_fail "gcloud command not found (optional but recommended)"
fi

print_test "Checking GCP project configuration"
PROJECT="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project 2>/dev/null || echo '')}"
if [[ -n "$PROJECT" ]]; then
    print_pass "GCP project configured: $PROJECT"
else
    print_fail "No GCP project configured"
    print_info "Set project: gcloud config set project PROJECT_ID"
    print_info "Or export GOOGLE_CLOUD_PROJECT=PROJECT_ID"
fi

# Test 5: Check cache
print_header "Test 5: Completion Cache"

CACHE_FILE="$HOME/.cache/bq-completion-cache"

print_test "Checking cache directory"
if [[ -d "$HOME/.cache" ]]; then
    print_pass "Cache directory exists: ~/.cache"
else
    print_fail "Cache directory missing"
    print_info "Create it: mkdir -p ~/.cache"
fi

print_test "Checking cache file"
if [[ -f "$CACHE_FILE" ]]; then
    print_pass "Cache file exists: $CACHE_FILE"

    CACHE_AGE=$(($(date +%s) - $(stat -f %m "$CACHE_FILE" 2>/dev/null || stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0)))
    print_info "Cache age: ${CACHE_AGE}s (TTL: 3600s)"

    LINE_COUNT=$(wc -l < "$CACHE_FILE" | tr -d ' ')
    print_info "Cached tables: $LINE_COUNT"

    if [[ $LINE_COUNT -gt 0 ]]; then
        print_info "Sample entries:"
        head -n 3 "$CACHE_FILE" | while read -r line; do
            echo "    $line"
        done
    fi
else
    print_fail "Cache file not found"
    print_info "It will be created on first use"
fi

# Test 6: Test utilities exist
print_header "Test 6: Utility Commands"

UTILITIES=(
    "bq-profile"
    "bq-explain"
    "bq-explore"
    "bq-lineage"
)

print_test "Checking if utilities are in PATH"
FOUND_COUNT=0
for util in "${UTILITIES[@]}"; do
    if command -v "$util" &>/dev/null; then
        ((FOUND_COUNT++))
    fi
done

if [[ $FOUND_COUNT -eq ${#UTILITIES[@]} ]]; then
    print_pass "All test utilities found in PATH ($FOUND_COUNT/${#UTILITIES[@]})"
elif [[ $FOUND_COUNT -gt 0 ]]; then
    print_pass "Some utilities found in PATH ($FOUND_COUNT/${#UTILITIES[@]})"
    print_info "Missing utilities won't have completion available"
else
    print_fail "No utilities found in PATH"
    print_info "Add rig/bin/data-utils to your PATH"
fi

# Summary
print_header "Test Summary"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
PASS_RATE=0
if [[ $TOTAL_TESTS -gt 0 ]]; then
    PASS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))
fi

echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$TESTS_PASSED${RESET}"
echo -e "Failed: ${RED}$TESTS_FAILED${RESET}"
echo "Pass Rate: ${PASS_RATE}%"
echo

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}✓ All tests passed! Shell completion is properly configured.${RESET}"
    echo
    echo "Try these commands to test completion:"
    echo "  bq-profile --<TAB>"
    echo "  bq-explain --format=<TAB>"
    echo "  bq-lineage <TAB>"
    exit 0
else
    echo -e "${YELLOW}⚠ Some tests failed. Review the output above for recommendations.${RESET}"
    echo
    echo "Common fixes:"
    echo "  1. Reload shell: exec \$SHELL"
    echo "  2. Reinstall: ./install-completions.sh"
    echo "  3. Install prerequisites: brew install jq (or apt-get install jq)"
    echo "  4. Set GCP project: gcloud config set project PROJECT_ID"
    exit 1
fi
