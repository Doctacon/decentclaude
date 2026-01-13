# Worktree Utilities Reference

## Overview

The worktree utilities in `bin/worktree-utils/` provide enhanced management and coordination for git worktrees in Gas Town. They build on top of git's built-in worktree commands with Gas Town-specific features.

## Installation

Add the utilities to your PATH:

```bash
# Add to your shell rc (.bashrc, .zshrc, etc.)
export PATH="$HOME/gt/<project>/polecats/<name>/<project>/bin/worktree-utils:$PATH"

# Or create symlinks
ln -s ~/gt/<project>/bin/worktree-utils/* ~/bin/
```

## wt-status

### Synopsis

```bash
wt-status [--verbose] [--dirty-only] [--help]
```

### Description

Display status of all worktrees in the workspace with color-coded health indicators.

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--verbose` | `-v` | Show detailed git status for each worktree |
| `--dirty-only` | `-d` | Only show worktrees with uncommitted changes |
| `--help` | `-h` | Show help message |

### Output Fields

For each worktree, displays:
- **Name**: The worktree directory name
- **Branch**: Currently checked out branch
- **Status**: Color-coded status indicator
  - 🟢 **Green** (clean): No uncommitted changes, up to date
  - 🟡 **Yellow** (out of sync): Behind or ahead of origin
  - 🔴 **Red** (dirty): Has uncommitted changes
- **Path**: Full path to the worktree
- **Changes** (verbose mode): List of modified files

### Status Messages

| Message | Meaning |
|---------|---------|
| `clean` | No uncommitted changes, synchronized with remote |
| `dirty (N changes)` | N uncommitted changes (modified, staged, or untracked files) |
| `out of sync (↑X ↓Y)` | X commits ahead, Y commits behind remote |

### Examples

**Basic status check**:
```bash
$ wt-status
Worktree Status
Bare repo: /Users/you/gt/project/.repo.git

furiosa [polecat/furiosa-abc123] - dirty (3 changes)
  Path: /Users/you/gt/project/polecats/furiosa/project

nux [polecat/nux-xyz789] - clean
  Path: /Users/you/gt/project/polecats/nux/project

refinery [main] - out of sync (↑0 ↓2)
  Path: /Users/you/gt/project/refinery/rig

Summary
Total worktrees: 3
```

**Verbose mode**:
```bash
$ wt-status --verbose
...
furiosa [polecat/furiosa-abc123] - dirty (3 changes)
  Path: /Users/you/gt/project/polecats/furiosa/project
  Changes:
     M bin/worktree-utils/wt-status
    ?? docs/worktrees/UTILITIES.md
    ?? .git-hooks/post-checkout
```

**Only dirty worktrees**:
```bash
$ wt-status --dirty-only
Worktree Status
Bare repo: /Users/you/gt/project/.repo.git

furiosa [polecat/furiosa-abc123] - dirty (3 changes)
  Path: /Users/you/gt/project/polecats/furiosa/project

Summary
Total worktrees: 3
```

### Use Cases

- **Before switching contexts**: Check if you have uncommitted work
- **Daily standup**: Quick overview of work in progress
- **Debugging**: Find which worktree has changes you're looking for
- **CI/CD**: Validate clean state before deployment

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Not in a git repository |

---

## wt-switch

### Synopsis

```bash
wt-switch <worktree-name>
wt-switch --list
```

### Description

Quickly switch between worktrees by outputting a `cd` command. Designed to be used with `eval` or as an alias.

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--list` | `-l` | List available worktrees |
| `--help` | `-h` | Show help message |

### Arguments

- `<worktree-name>`: Name of the target worktree (directory name, not branch name)

### Output

Prints a `cd` command to stdout:
```bash
cd "/Users/you/gt/project/polecats/furiosa/project"
```

### Setup

**Recommended alias** (add to your shell rc):
```bash
alias wts='eval "$(wt-switch $@)"'
```

Then use as:
```bash
wts furiosa     # Instantly switch to furiosa worktree
wts refinery    # Switch to refinery
```

### Examples

**List worktrees**:
```bash
$ wt-switch --list
Available worktrees:
  furiosa
    Path: /Users/you/gt/project/polecats/furiosa/project
    Branch: polecat/furiosa-abc123
  nux
    Path: /Users/you/gt/project/polecats/nux/project
    Branch: polecat/nux-xyz789
  refinery
    Path: /Users/you/gt/project/refinery/rig
    Branch: main
```

**Switch to a worktree**:
```bash
# Without alias (prints command)
$ wt-switch furiosa
cd "/Users/you/gt/project/polecats/furiosa/project"

# With eval (actually switches)
$ eval "$(wt-switch furiosa)"
$ pwd
/Users/you/gt/project/polecats/furiosa/project

# With alias (recommended)
$ wts furiosa
$ pwd
/Users/you/gt/project/polecats/furiosa/project
```

**Error handling**:
```bash
$ wts nonexistent
Error: Worktree 'nonexistent' not found

Available worktrees:
  furiosa
  nux
  refinery
```

### Use Cases

- **Context switching**: Jump between polecats or roles
- **Quick navigation**: Faster than `cd` with tab completion
- **Scripts**: Use in automation to switch contexts
- **Pair programming**: Quickly move to partner's worktree

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (worktree found) |
| 1 | Worktree not found or invalid arguments |

---

## wt-sync

### Synopsis

```bash
wt-sync [--prune-merged] [--dry-run]
```

### Description

Synchronize all worktrees by fetching from remote and checking their status. Optionally removes worktrees for merged branches.

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--prune-merged` | `-p` | Remove worktrees for branches merged into main |
| `--dry-run` | `-n` | Show what would be done without doing it |
| `--help` | `-h` | Show help message |

### Process

1. **Fetch**: Fetch all updates from remote and prune deleted branches
2. **Check**: Analyze each worktree for issues
3. **Prune** (if `--prune-merged`): Remove worktrees for merged branches
4. **Report**: Summarize findings and actions

### Examples

**Basic sync**:
```bash
$ wt-sync
Syncing worktrees...

[1/3] Fetching from remote
  ✓ Fetch complete

[2/3] Checking worktree status
  ⚠ furiosa - has uncommitted changes
  ✓ nux - up to date
  ⚠ refinery - behind origin by 2 commits

[3/3] Summary
  Worktrees needing attention:
    - furiosa (uncommitted changes)
    - refinery (behind by 2)

Sync complete
```

**With auto-prune**:
```bash
$ wt-sync --prune-merged
Syncing worktrees...

[1/3] Fetching from remote
  ✓ Fetch complete

[2/3] Checking worktree status
  ✓ feature-123 - branch merged into main
    Removing worktree...
  ✓ nux - up to date

[3/3] Summary
  All worktrees are in sync

Sync complete
```

**Dry run**:
```bash
$ wt-sync --prune-merged --dry-run
Syncing worktrees...

[1/3] Fetching from remote
  (dry-run) Would run: git fetch --all --prune

[2/3] Checking worktree status
  ✓ feature-123 - branch merged into main
    (dry-run) Would remove worktree

[3/3] Summary
  Worktrees needing attention:
    (none)

Sync complete
```

### Use Cases

- **After pulling main**: Sync all worktrees after updating main
- **Daily workflow**: Start each day with a sync
- **Cleanup**: Regular maintenance to remove merged branches
- **Team coordination**: Before starting work, ensure everything is up to date

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |

---

## wt-clean

### Synopsis

```bash
wt-clean [--merged] [--gone] [--dry-run] [--force]
```

### Description

Clean up stale or unnecessary worktrees by removing those for merged or deleted branches.

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--merged` | `-m` | Remove worktrees for branches merged into main |
| `--gone` | `-g` | Remove worktrees for branches deleted from remote |
| `--dry-run` | `-n` | Show what would be removed without removing |
| `--force` | `-f` | Force removal even with uncommitted changes |
| `--help` | `-h` | Show help message |

### Behavior

- **No options**: Runs in scan mode (dry-run with both merged and gone checks)
- **With options**: Performs actual removal based on specified criteria
- **Safety**: Refuses to remove worktrees with uncommitted changes unless `--force`

### Process

1. **Prune**: Remove metadata for missing worktree directories
2. **Fetch**: Update remote information
3. **Check**: Identify worktrees meeting removal criteria
4. **Remove**: Delete qualifying worktrees (unless dry-run)

### Examples

**Scan mode (default)**:
```bash
$ wt-clean
Running in scan mode (no changes will be made)
Use --merged or --gone to actually remove worktrees

Cleaning worktrees...

[1/3] Pruning missing worktrees
  No missing worktrees found

[2/3] Fetching latest from remote
  (dry-run) Would run: git fetch --all --prune

[3/3] Checking worktrees
  ⊘ feature-123 - merged into main (would remove)
  ⊘ hotfix-456 - branch deleted from remote (would remove)

Summary
  Would remove: 2 worktrees
  Would skip: 0 worktrees (uncommitted changes)

To actually remove these worktrees, run:
  wt-clean --merged
  wt-clean --gone
```

**Remove merged branches**:
```bash
$ wt-clean --merged
Cleaning worktrees...

[1/3] Pruning missing worktrees
  ✓ Prune complete

[2/3] Fetching latest from remote
  ✓ Fetch complete

[3/3] Checking worktrees
  ✗ feature-123 - merged into main (removing)

Summary
  Removed: 1 worktrees
  Skipped: 0 worktrees (uncommitted changes)
```

**Remove deleted branches**:
```bash
$ wt-clean --gone
Cleaning worktrees...

[3/3] Checking worktrees
  ✗ hotfix-456 - branch deleted from remote (removing)

Summary
  Removed: 1 worktrees
  Skipped: 0 worktrees (uncommitted changes)
```

**Force removal with uncommitted changes**:
```bash
$ wt-clean --merged
...
  ⊘ feature-789 - merged into main (skipped: has uncommitted changes)
    Use --force to remove anyway

$ wt-clean --merged --force
...
  ✗ feature-789 - merged into main (removing)
```

**Combined cleanup**:
```bash
# Remove both merged and gone in one command
$ wt-clean --merged --gone
```

### Use Cases

- **Post-merge cleanup**: After merging PRs, remove old worktrees
- **Storage management**: Free up disk space from old branches
- **Workspace hygiene**: Keep worktree list clean and relevant
- **Automated maintenance**: Run periodically in scripts

### Safety Features

1. **Dry-run by default**: When run without options, shows what would happen
2. **Protects uncommitted work**: Refuses to remove unless `--force`
3. **Never removes main**: Automatically skips main/master branches
4. **Confirmation**: Clear output shows what's being removed

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |

---

## Integration with Gas Town

### With GT Commands

The utilities work seamlessly with `gt` commands:

```bash
# GT creates worktrees
gt worktree beads

# Utilities manage them
wt-status
wt-sync
wts beads
```

### With Git Commands

The utilities complement git's built-in commands:

```bash
# Git lists worktrees
git worktree list

# Utilities provide enhanced views
wt-status --verbose

# Git adds worktrees
git worktree add ../new-worktree feature-branch

# Utilities clean them up
wt-clean --merged
```

### In Shell Scripts

Example automation:

```bash
#!/bin/bash
# Daily worktree maintenance

echo "Syncing worktrees..."
wt-sync --prune-merged

echo "Checking for stale worktrees..."
wt-clean --gone --dry-run

echo "Current status:"
wt-status --dirty-only
```

## Tips and Tricks

### Quick Status Check Alias

```bash
alias wts-status='wt-status --dirty-only'
```

Shows only worktrees that need attention.

### Jump to Dirty Worktree

```bash
# Get first dirty worktree and switch to it
dirty=$(wt-status --dirty-only | grep -A1 "dirty" | head -1 | awk '{print $1}')
if [ -n "$dirty" ]; then
    wts "$dirty"
fi
```

### Pre-Handoff Check

Before handing off or ending work:

```bash
wt-status && echo "All clean!" || echo "You have uncommitted work"
```

### Auto-Sync on Main

Add to your shell rc:

```bash
# After pulling main, auto-sync other worktrees
gpull() {
    git pull "$@" && wt-sync
}
```

## Troubleshooting

### "Not in a git repository"

**Cause**: Running outside a git worktree.

**Solution**: Navigate to a worktree first.

### "Worktree not found"

**Cause**: Typo in worktree name or worktree doesn't exist.

**Solution**: Run `wt-switch --list` to see available names.

### Utilities not in PATH

**Cause**: `bin/worktree-utils/` not in your PATH.

**Solution**: Add to your shell rc or use full path.

## See Also

- [WORKTREES.md](./WORKTREES.md) - Worktree workflow guide
- [HOOKS.md](./HOOKS.md) - Git hooks documentation
- [git-worktree(1)](https://git-scm.com/docs/git-worktree) - Git worktree documentation
