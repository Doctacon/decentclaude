---
name: update-deps
description: Dependency update workflow checking outdated deps, identifying breaking changes, generating upgrade plans, updating files, and running tests
allowed-tools:
  - Read
  - Grep
  - Bash
  - Edit
---

# Update Deps Skill

Systematic dependency update workflow for npm, pip, go modules, and other package managers. Identifies outdated dependencies, breaking changes, security vulnerabilities, and automates safe updates.

## Workflow

### 1. Check Outdated Dependencies

```bash
# npm/yarn
npm outdated
yarn outdated

# Python/pip
pip list --outdated
pip-audit  # Security vulnerabilities

# Go
go list -u -m all

# Ruby
bundle outdated

# Rust
cargo outdated
```

### 2. Identify Breaking Changes

**Check changelogs and release notes**:
```bash
# For each outdated package
npm view package-name versions --json
npm view package-name@latest
# Read CHANGELOG.md or GitHub releases
```

**Semver guidelines**:
- **Patch (1.0.x)**: Bug fixes, safe to update
- **Minor (1.x.0)**: New features, backward compatible
- **Major (x.0.0)**: Breaking changes, requires code changes

### 3. Update Strategy

**Patch updates** (safest):
```bash
npm update  # Updates to latest patch/minor within semver range
```

**Minor updates**:
```bash
# Update specific package to latest minor
npm install package-name@^2.3.0
```

**Major updates** (risky, test thoroughly):
```bash
# Update to specific major version
npm install package-name@3.0.0
```

### 4. Update Lock Files

```bash
# npm
npm install
rm package-lock.json && npm install  # Regenerate if needed

# Yarn
yarn install

# Python
pip freeze > requirements.txt

# Go
go mod tidy
```

### 5. Run Tests

```bash
npm test
pytest
go test ./...

# If tests fail, investigate and fix or rollback
```

### 6. Check for Deprecation Warnings

```bash
npm run build 2>&1 | grep -i "deprecat"
```

## Security Updates

**Check for vulnerabilities**:
```bash
npm audit
npm audit fix  # Auto-fix non-breaking
npm audit fix --force  # Fix with breaking changes (careful!)

pip-audit
safety check

# Go
govulncheck ./...
```

**Subscribe to security advisories**:
- GitHub Dependabot
- Snyk
- WhiteSource

## Best Practices

- Update dependencies regularly (monthly)
- Read changelogs before updating
- Update one dependency at a time (easier to debug)
- Test thoroughly after updates
- Use lock files for reproducible builds
- Automate with Renovate or Dependabot
