# Git Worktree Management in Gas Town

## Overview

Gas Town uses git worktrees extensively to enable parallel work across multiple agents and contexts. Each polecat, the refinery, and other roles operate in their own worktree, allowing them to work on different branches simultaneously without interfering with each other.

## What Are Git Worktrees?

Git worktrees allow you to have multiple working directories attached to the same repository. Instead of using `git clone` multiple times or constantly switching branches with `git checkout`, you can have multiple directories, each with a different branch checked out.

### Traditional Git Workflow
```
~/project/           # Only one working directory
  git checkout feature-1
  # work on feature-1
  git checkout feature-2
  # work on feature-2 (feature-1 changes gone from working dir)
```

### Worktree Workflow
```
~/gt/project/.repo.git/              # Bare repo (no working directory)
~/gt/project/main/                   # Worktree with main branch
~/gt/project/polecats/alice/         # Worktree with feature-1 branch
~/gt/project/polecats/bob/           # Worktree with feature-2 branch
```

## Gas Town Worktree Structure

In Gas Town, the typical structure is:

```
~/gt/
  <project>/
    .repo.git/                       # Bare repository
    polecats/
      <polecat-name>/
        <project>/                   # Polecat worktree
    refinery/
      rig/                          # Refinery worktree (usually on main)
    witness/
      <project>/                    # Witness worktree
    mayor/
      rig/                          # Mayor worktree
```

Each worktree is a fully functional git repository with its own:
- Working directory with files
- Branch checked out
- `.git` file (pointer to the bare repo)
- Local uncommitted changes

They all share:
- The same commit history
- The same remote configuration
- The same tags and branches

## Worktree Commands

### Built-in Git Commands

```bash
# List all worktrees
git worktree list

# Add a new worktree
git worktree add <path> <branch>

# Remove a worktree
git worktree remove <path>

# Clean up stale worktree metadata
git worktree prune
```

### Gas Town Worktree Utilities

Gas Town provides enhanced utilities in `bin/worktree-utils/`:

#### `wt-status` - View worktree status

Shows the status of all worktrees in the workspace.

```bash
# Basic status
wt-status

# Verbose mode with detailed changes
wt-status --verbose

# Show only worktrees with uncommitted changes
wt-status --dirty-only
```

Output example:
```
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

#### `wt-switch` - Quick switch between worktrees

Quickly switch your shell to a different worktree.

```bash
# List available worktrees
wt-switch --list

# Switch to a worktree (prints cd command)
wt-switch furiosa

# Use with eval to actually switch
eval "$(wt-switch furiosa)"

# Add this alias to your shell for convenience
alias wts='eval "$(wt-switch $@)"'

# Then use it like:
wts refinery
```

#### `wt-sync` - Sync and coordinate worktrees

Fetch updates, check status, and optionally prune merged worktrees.

```bash
# Basic sync (fetch and status check)
wt-sync

# Sync and remove worktrees for merged branches
wt-sync --prune-merged

# Dry run to see what would be done
wt-sync --dry-run
```

#### `wt-clean` - Clean up stale worktrees

Identify and remove worktrees that are no longer needed.

```bash
# Scan for stale worktrees (no changes made)
wt-clean

# Remove worktrees for branches merged into main
wt-clean --merged

# Remove worktrees for branches deleted from remote
wt-clean --gone

# Dry run to see what would be removed
wt-clean --merged --dry-run

# Force removal even with uncommitted changes
wt-clean --merged --force
```

### Gas Town GT Commands

GT also provides worktree management:

```bash
# Create a cross-rig worktree
gt worktree <rig>

# List cross-rig worktrees
gt worktree list

# Remove a cross-rig worktree
gt worktree remove <rig>
```

## Common Workflows

### Working in Multiple Worktrees

1. Check status of all worktrees:
   ```bash
   wt-status
   ```

2. Switch to a different worktree:
   ```bash
   wts furiosa
   ```

3. Sync all worktrees after pulling main:
   ```bash
   cd ~/gt/project/refinery/rig
   git pull origin main
   wt-sync
   ```

### Cleaning Up After Merges

When branches are merged into main, their worktrees should be cleaned up:

```bash
# See what would be removed
wt-clean --merged --dry-run

# Actually remove them
wt-clean --merged

# Or use wt-sync with auto-prune
wt-sync --prune-merged
```

### Cross-Rig Work

When you need to work on another rig's codebase while maintaining your identity:

```bash
# From a crew workspace
gt worktree beads

# This creates ~/gt/beads/crew/<your-rig>-<your-name>/
# You maintain your BD_ACTOR and GT_ROLE identity
```

### Checking for Conflicts

Before committing on a branch, ensure it's not checked out elsewhere:

```bash
git worktree list | grep "mybranch"
```

The pre-commit hook will also prevent commits if the branch is checked out in multiple worktrees.

## Best Practices

1. **One branch per worktree**: Avoid checking out the same branch in multiple worktrees. The pre-commit hook will prevent this, but it's good to be aware.

2. **Regular syncing**: Run `wt-sync` regularly to keep all worktrees up to date.

3. **Clean up merged branches**: Use `wt-clean --merged` after merging to remove stale worktrees.

4. **Check status before switching**: Always run `wt-status` to see if you have uncommitted changes before switching contexts.

5. **Use hooks**: Install the worktree hooks (see HOOKS.md) to get automatic validation and warnings.

6. **Fetch before checking**: The worktrees share the same repository, so a `git fetch` in one affects all of them. Fetch from one place before checking status in another.

## Common Issues and Solutions

### Issue: "Branch is checked out in another worktree"

**Problem**: Git prevents you from checking out a branch that's already checked out elsewhere.

**Solution**:
1. Check which worktree has it: `git worktree list`
2. Either switch the other worktree to a different branch, or remove it
3. Or work in the existing worktree for that branch

### Issue: "Changes disappeared after switching worktrees"

**Problem**: Uncommitted changes are local to each worktree.

**Solution**:
1. Commit your changes before switching, or
2. Use `git stash` to save them temporarily
3. Remember that each worktree has its own working directory

### Issue: "Stale worktree metadata"

**Problem**: Git thinks a worktree exists but the directory is gone.

**Solution**:
```bash
git worktree prune
# or
wt-clean
```

### Issue: "Can't remove worktree with uncommitted changes"

**Problem**: Git protects you from losing work.

**Solution**:
```bash
# Either commit the changes first
cd <worktree>
git commit -am "Save work"

# Or force remove (loses uncommitted changes)
git worktree remove --force <worktree>
# or
wt-clean --merged --force
```

## Performance Considerations

1. **Disk space**: Each worktree needs its own working directory. A 100MB codebase with 5 worktrees uses ~500MB for working directories (plus the shared .repo.git).

2. **Fetch operations**: Since all worktrees share the repository, fetch operations affect all of them simultaneously. This is actually more efficient than separate clones.

3. **Checkout speed**: Switching between worktrees (cd) is instant, much faster than `git checkout`.

## See Also

- [HOOKS.md](./HOOKS.md) - Git hooks for worktree-aware operations
- [UTILITIES.md](./UTILITIES.md) - Detailed utility reference
- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
