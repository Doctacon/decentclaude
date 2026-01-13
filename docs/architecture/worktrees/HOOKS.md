# Git Hooks for Worktree Management

## Overview

The worktree-aware git hooks in `.git-hooks/` help maintain consistency and prevent common issues when working with multiple worktrees. They automatically validate operations, update state, and provide helpful warnings.

## Available Hooks

### post-checkout

**Triggers**: After `git checkout` or `git switch`

**Purpose**: Validates and tracks worktree state after branch changes.

**What it does**:
1. Checks if the newly checked out branch is already active in another worktree
2. Warns if there's a conflict
3. Updates the last checkout timestamp for the current worktree

**Example output**:
```
Warning: Branch 'feature-x' is also checked out in:
  /Users/you/gt/project/polecats/other/project

This can cause issues with git operations. Consider using a different branch.
```

**When it helps**:
- Prevents confusion when the same branch is checked out in multiple places
- Helps identify when you might be working on stale code
- Tracks worktree activity for debugging

**Override**: Not applicable (informational only)

### pre-commit

**Triggers**: Before `git commit`

**Purpose**: Prevents commits that could cause conflicts with other worktrees.

**What it does**:
1. Checks if the current branch is checked out in any other worktree
2. Blocks the commit if found (prevents inconsistent state)
3. Updates the last commit timestamp for the current worktree

**Example output**:
```
Error: Branch 'feature-x' is checked out in another worktree:
  /Users/you/gt/project/polecats/other/project

Committing on a branch that is checked out in multiple worktrees
can cause confusion and conflicts. Please switch one of them to a
different branch before committing.

To override this check, use: git commit --no-verify
```

**When it helps**:
- Prevents the confusing situation where you commit in one worktree but another has the old code checked out
- Ensures you don't accidentally create divergent histories
- Maintains consistency across the workspace

**Override**:
```bash
# Use --no-verify to skip the hook (not recommended)
git commit --no-verify -m "message"
```

### post-merge

**Triggers**: After `git merge` or `git pull`

**Purpose**: Notifies about impacts on other worktrees and tracks merge activity.

**What it does**:
1. Detects if main/master was merged
2. Lists other worktrees that might need syncing
3. Updates the last merge timestamp for the current worktree
4. Suggests running `wt-sync` to check other worktrees

**Example output**:
```
Merged from main. Other worktrees might also need to merge main.
Run 'wt-status' to check other worktrees.

Updated main branch. Consider syncing these worktrees:
  - furiosa:polecat/furiosa-abc123
  - nux:polecat/nux-xyz789

Run 'wt-sync' to check their status.
```

**When it helps**:
- Reminds you to update other worktrees after pulling main
- Prevents working on outdated code in other worktrees
- Helps coordinate work across multiple concurrent branches

**Override**: Not applicable (informational only)

## Installation

### Install for Current Worktree

Hooks installed in a specific worktree only affect that worktree:

```bash
cd ~/gt/project/polecats/furiosa/project
.git-hooks/install-hooks.sh --local
```

This installs hooks in `.git/hooks/` (worktree-specific).

### Install Globally for All Worktrees

Hooks installed in the bare repository affect all worktrees:

```bash
cd ~/gt/project/polecats/furiosa/project
.git-hooks/install-hooks.sh --global
```

This installs hooks in `.repo.git/hooks/` (shared by all worktrees).

**Recommendation**: Use `--global` for Gas Town to ensure all agents benefit from the hooks.

## Hook State Tracking

Hooks maintain state in `.repo.git/worktree-state/`:

```
.repo.git/
  worktree-state/
    furiosa.last_checkout    # Timestamp of last checkout
    furiosa.last_commit      # Timestamp of last commit
    furiosa.last_merge       # Timestamp of last merge
    nux.last_checkout
    nux.last_commit
    ...
```

This state is used for:
- Debugging worktree activity
- Identifying stale worktrees
- Understanding the timeline of operations

## Customization

### Disabling Specific Hooks

To disable a hook without removing it:

```bash
# Rename it so git doesn't recognize it
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled
```

### Temporarily Bypassing Hooks

For single operations:

```bash
# Skip pre-commit hook
git commit --no-verify -m "message"

# Skip all hooks for a rebase
git rebase --no-verify main
```

### Adjusting Hook Behavior

Edit the hooks in `.git-hooks/` to customize:

1. Change warning thresholds
2. Add additional checks
3. Integrate with other tools
4. Send notifications

Then reinstall:

```bash
.git-hooks/install-hooks.sh --global
```

## Hook Interaction with Gas Town

### Polecat Workflow

Polecats benefit most from these hooks because they:
1. Work on isolated branches
2. Need to coordinate with the refinery
3. Should never have the same branch in multiple worktrees

The hooks automatically prevent common mistakes in this workflow.

### Refinery Workflow

The refinery typically works on `main` and merge queue branches. The hooks:
1. Warn when other worktrees need updating after main changes
2. Prevent commits on branches that are being worked on elsewhere
3. Track merge activity for audit purposes

### Cross-Rig Work

When using `gt worktree <rig>` for cross-rig work:
1. Hooks still apply in the created worktree
2. State tracking helps identify when to sync
3. Pre-commit hook prevents conflicts with the main rig's worktrees

## Troubleshooting

### Hook Not Running

**Check hook is installed**:
```bash
ls -la .git/hooks/
# or for global
ls -la $(git rev-parse --git-common-dir)/hooks/
```

**Check hook is executable**:
```bash
chmod +x .git/hooks/pre-commit
```

**Check hook syntax**:
```bash
bash -n .git/hooks/pre-commit
```

### False Positives

**pre-commit blocks but shouldn't**:
1. Verify the branch really isn't checked out elsewhere:
   ```bash
   git worktree list | grep "your-branch"
   ```
2. If it's a false positive (stale metadata):
   ```bash
   git worktree prune
   ```
3. Last resort - bypass with `--no-verify`

### Hook Errors

**Hook fails with permission error**:
```bash
chmod +x .git-hooks/install-hooks.sh
.git-hooks/install-hooks.sh --global
```

**Hook fails with "command not found"**:
- Ensure the hook's shebang is correct (`#!/usr/bin/env bash`)
- Check that `bash` is available: `which bash`

## Best Practices

1. **Install globally**: Use `--global` to ensure all worktrees benefit.

2. **Don't bypass unless necessary**: The `--no-verify` flag should be rare. If you're using it often, investigate why.

3. **Check warnings**: When hooks warn you, take the time to understand why. They're trying to prevent real problems.

4. **Update hooks**: When the `.git-hooks/` directory is updated (via git pull), reinstall:
   ```bash
   .git-hooks/install-hooks.sh --global
   ```

5. **Monitor state**: Occasionally check `.repo.git/worktree-state/` to understand worktree activity.

6. **Coordinate with team**: If multiple people work in the same Gas Town installation, ensure everyone has the hooks installed.

## Advanced: Writing Custom Hooks

Want to add your own worktree-aware logic? Here's the pattern:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Get current worktree info
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
CURRENT_WORKTREE=$(git rev-parse --show-toplevel)

# Iterate over all worktrees
while IFS= read -r line; do
    if [[ $line =~ ^worktree[[:space:]]+(.*) ]]; then
        WORKTREE_PATH="${BASH_REMATCH[1]}"

        # Skip current and bare
        if [[ "$WORKTREE_PATH" == "$CURRENT_WORKTREE" ]] || \
           [[ $WORKTREE_PATH == *".repo.git"* ]]; then
            continue
        fi

        # Get branch
        read -r branch_line
        if [[ $branch_line =~ branch[[:space:]]+refs/heads/(.*) ]]; then
            BRANCH="${BASH_REMATCH[1]}"

            # Your logic here
            if [[ "$BRANCH" == "$CURRENT_BRANCH" ]]; then
                echo "Found same branch in $WORKTREE_PATH"
            fi
        fi
    fi
done < <(git worktree list --porcelain)
```

## See Also

- [WORKTREES.md](./WORKTREES.md) - Worktree workflow guide
- [UTILITIES.md](./UTILITIES.md) - Utility reference
- [Git Hooks Documentation](https://git-scm.com/docs/githooks)
