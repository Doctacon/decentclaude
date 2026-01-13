# Git Worktree Utilities for Gas Town

A comprehensive toolkit for managing multiple git worktrees in Gas Town's multi-agent environment.

## Quick Start

### Installation

1. **Add utilities to PATH**:
   ```bash
   export PATH="$PWD/bin/worktree-utils:$PATH"
   ```

2. **Install git hooks** (recommended):
   ```bash
   .git-hooks/install-hooks.sh --global
   ```

3. **Add shell alias** (optional but recommended):
   ```bash
   alias wts='eval "$(wt-switch $@)"'
   ```

### Basic Usage

```bash
# Check status of all worktrees
wt-status

# Switch to a different worktree
wts refinery

# Sync all worktrees with remote
wt-sync

# Clean up merged branches
wt-clean --merged
```

## What's Included

### Utilities (`bin/worktree-utils/`)

- **wt-status**: View status of all worktrees with color-coded health indicators
- **wt-switch**: Quickly switch between worktrees
- **wt-sync**: Fetch updates and synchronize all worktrees
- **wt-clean**: Remove stale or merged worktrees

### Git Hooks (`.git-hooks/`)

- **post-checkout**: Warns about same branch in multiple worktrees
- **pre-commit**: Prevents commits on branches checked out elsewhere
- **post-merge**: Notifies about impacts on other worktrees
- **install-hooks.sh**: Hook installation script

### Documentation (`docs/worktrees/`)

- **[WORKTREES.md](./WORKTREES.md)**: Complete worktree workflow guide
- **[HOOKS.md](./HOOKS.md)**: Git hooks reference
- **[UTILITIES.md](./UTILITIES.md)**: Detailed utility documentation

## Common Workflows

### Daily Workflow

```bash
# Start of day: check status
wt-status

# Sync with remote
wt-sync

# Switch to a worktree
wts furiosa

# Work...

# End of day: check what changed
wt-status --dirty-only
```

### After Merging PRs

```bash
# Sync and remove merged branches
wt-sync --prune-merged

# Or separately
wt-clean --merged
```

### Finding What You Changed

```bash
# See which worktrees have uncommitted work
wt-status --dirty-only

# See detailed changes
wt-status --verbose
```

## Why Worktrees?

In Gas Town, multiple agents work simultaneously on different features. Traditional git workflows would require:
- Multiple clones (wastes space)
- Constant branch switching (loses context)
- Stashing changes (error-prone)

With worktrees:
- Each agent has its own directory ✓
- All work in parallel ✓
- Shared git history ✓
- Instant context switching ✓

## Architecture

```
~/gt/<project>/
├── .repo.git/              # Bare repository (shared)
├── polecats/
│   ├── furiosa/<project>/  # Polecat worktree
│   ├── nux/<project>/      # Polecat worktree
│   └── slit/<project>/     # Polecat worktree
├── refinery/
│   └── rig/                # Refinery worktree (usually main)
└── witness/
    └── <project>/          # Witness worktree
```

Each worktree:
- Has its own working directory
- Has its own checked out branch
- Shares the same commit history
- Can work independently

## Integration with Gas Town

### GT Commands

```bash
# Create cross-rig worktree
gt worktree beads

# List cross-rig worktrees
gt worktree list

# Remove cross-rig worktree
gt worktree remove beads
```

### Polecat Workflow

1. Polecat spawns in dedicated worktree
2. Works on feature branch
3. Hooks prevent conflicts with other polecats
4. Submits work to merge queue
5. Worktree cleaned up after merge

### Coordination

- **wt-status**: Monitor all active work
- **wt-sync**: Keep everyone up to date
- **Hooks**: Prevent conflicts automatically
- **wt-clean**: Automated cleanup

## Troubleshooting

### Can't check out branch

**Error**: "Branch is already checked out"

**Solution**: Use `wt-status` to find which worktree has it, then either switch that worktree or work there.

### Changes disappeared

**Cause**: Changes are local to each worktree

**Solution**: Check other worktrees with `wt-status --dirty-only`

### Stale worktrees

**Symptom**: `git worktree list` shows missing directories

**Solution**: `wt-clean` or `git worktree prune`

## Learn More

- **[WORKTREES.md](./WORKTREES.md)**: Comprehensive workflow guide
- **[UTILITIES.md](./UTILITIES.md)**: Complete utility reference
- **[HOOKS.md](./HOOKS.md)**: Hook documentation
- [Git Worktree Docs](https://git-scm.com/docs/git-worktree)

## Examples

### Check Status

```bash
$ wt-status
Worktree Status
Bare repo: /Users/you/gt/project/.repo.git

furiosa [polecat/furiosa-abc] - dirty (3 changes)
  Path: /Users/you/gt/project/polecats/furiosa/project

nux [polecat/nux-xyz] - clean
  Path: /Users/you/gt/project/polecats/nux/project

refinery [main] - out of sync (↑0 ↓2)
  Path: /Users/you/gt/project/refinery/rig

Summary
Total worktrees: 3
```

### Switch Worktrees

```bash
$ wts refinery
$ pwd
/Users/you/gt/project/refinery/rig
```

### Clean Up

```bash
$ wt-clean --merged
Cleaning worktrees...

[3/3] Checking worktrees
  ✗ feature-123 - merged into main (removing)

Summary
  Removed: 1 worktrees
```

## Contributing

When adding new utilities:

1. Add script to `bin/worktree-utils/`
2. Make executable: `chmod +x bin/worktree-utils/your-script`
3. Follow existing patterns for options and output
4. Document in `UTILITIES.md`
5. Add tests

When modifying hooks:

1. Edit in `.git-hooks/`
2. Test thoroughly (hooks can block operations)
3. Document in `HOOKS.md`
4. Reinstall: `.git-hooks/install-hooks.sh --global`

## Support

For issues or questions:
- Check the docs in `docs/worktrees/`
- Run utilities with `--help`
- Review git worktree docs: `man git-worktree`
