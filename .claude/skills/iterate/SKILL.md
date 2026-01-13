---
name: iterate
description: Iterative development workflow using Build → Test → Review → Refine cycles with automatic test execution and quality checks
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
  - Write
---

# Iterate Skill

Iterative development workflow that cycles through Build → Test → Review → Refine, perfect for Test-Driven Development (TDD) and rapid prototyping with quality gates.

## Workflow

### 1. Plan Iteration

- **Define goal**: What are you trying to achieve in this iteration?
- **Set scope**: Keep iterations small and focused (15-30 minutes)
- **Establish success criteria**: How will you know it works?
- **Identify tests**: What tests need to pass?

### 2. Build

- **Write minimal code**: Implement just enough to meet the iteration goal
- **Follow patterns**: Use existing patterns and conventions in the codebase
- **Keep it simple**: Don't over-engineer; iterate later if needed
- **Checkpoint**: Consider creating a git stash or WIP commit
  ```bash
  git add -A && git commit -m "WIP: <iteration-goal>"
  ```

### 3. Test

- **Run relevant tests**: Execute tests that cover your changes
  ```bash
  # Python
  pytest tests/test_module.py -v

  # JavaScript
  npm test -- --testPathPattern=module

  # Go
  go test ./pkg/module/... -v
  ```
- **Check coverage**: Ensure new code is tested
  ```bash
  # Python
  pytest --cov=module --cov-report=term-missing

  # JavaScript
  npm test -- --coverage

  # Go
  go test -coverprofile=coverage.out ./...
  ```
- **Fix failures**: If tests fail, debug and fix before continuing
- **Add missing tests**: Write tests for uncovered edge cases

### 4. Review

- **Code quality**: Check for code smells, complexity, duplication
- **Style compliance**: Run linters and formatters
  ```bash
  # Python
  black . && isort . && flake8

  # JavaScript
  npm run lint && npm run format

  # Go
  gofmt -w . && go vet ./...
  ```
- **Requirements validation**: Does the code meet the iteration goal?
- **Performance check**: Any obvious performance issues?
- **Security scan**: Any security concerns introduced?

### 5. Refine

- **Address review findings**: Fix quality issues, style violations
- **Optimize if needed**: Improve performance bottlenecks
- **Clean up**: Remove dead code, improve naming, add comments
- **Update documentation**: Reflect changes in README or inline docs

### 6. Checkpoint

- **Commit changes**: Create a clean commit with descriptive message
  ```bash
  git add -A
  git commit -m "feat: <what-you-built>

  - Specific change 1
  - Specific change 2

  Tests: <test-results>"
  ```
- **Tag if milestone**: Mark significant iterations
  ```bash
  git tag -a v0.1.0-alpha -m "Iteration checkpoint"
  ```
- **Push to remote** (optional): Share progress
  ```bash
  git push origin <branch>
  ```

### 7. Decide Next Step

- **Goal achieved?**
  - Yes: Move to next feature or iteration
  - Partially: Continue iterating on same goal
  - No: Reassess approach, maybe break down further
- **Feedback needed?**: Share with team for review
- **Break time?**: Take a break after 3-4 iterations

## TDD Mode

For Test-Driven Development, adjust the workflow:

1. **Write test first**: Write failing test that defines desired behavior
2. **Run test**: Verify it fails (red)
3. **Build**: Write minimal code to make test pass
4. **Run test**: Verify it passes (green)
5. **Refine**: Refactor while keeping tests green
6. **Checkpoint**: Commit the working code + test

## Quick Iteration Commands

```bash
# Full iteration cycle
./run-iteration.sh  # Custom script that runs tests + linters

# Python quick iteration
pytest && black . && isort .

# JavaScript quick iteration
npm test && npm run lint:fix

# Go quick iteration
go test ./... && gofmt -w . && go vet ./...
```

## Checkpointing Strategy

- **WIP commits**: Use for mid-iteration saves
  ```bash
  git commit -am "WIP: experimenting with approach X"
  ```
- **Squash before merge**: Clean up WIP commits before PR
  ```bash
  git rebase -i HEAD~5  # Interactive rebase to squash
  ```
- **Feature branches**: Use branches for larger features
  ```bash
  git checkout -b feature/new-capability
  ```

## Integration Points

- **CI/CD**: Push to trigger automated testing and validation
- **Code review**: Create draft PRs for early feedback
- **Issue tracking**: Update issue status after each iteration
- **Documentation**: Update docs incrementally, not all at end

## Tips for Effective Iteration

- **Keep iterations small**: Easier to debug and review
- **Test constantly**: Catch issues early when they're cheap to fix
- **Don't skip review**: Quality issues compound over iterations
- **Embrace refactoring**: Code quality should improve with each iteration
- **Use automation**: Automate tests, linting, formatting
- **Track velocity**: Note how long iterations take; optimize over time
- **Pair program**: Iterate with another developer for better quality

## Example Iteration Log

```
Iteration 1 (20 min):
  Goal: Add user authentication endpoint
  Built: POST /auth/login endpoint
  Tests: 5/5 passing, 85% coverage
  Review: ESLint warnings fixed
  Commit: abc123f

Iteration 2 (15 min):
  Goal: Add JWT token generation
  Built: Token generation and signing
  Tests: 8/8 passing, 90% coverage
  Review: Security review - use secure random
  Commit: def456a

Iteration 3 (25 min):
  Goal: Add token validation middleware
  Built: Middleware with error handling
  Tests: 12/12 passing, 92% coverage
  Review: Added documentation
  Commit: ghi789b
```

## Best Practices

- **Test after every build**: Don't accumulate untested code
- **Commit often**: Small commits are easier to revert if needed
- **Keep tests green**: Never commit failing tests
- **Review your own code**: Read your changes before committing
- **Update tests first**: When fixing bugs, add failing test then fix
- **Celebrate wins**: Acknowledge progress after each successful iteration
- **Learn from failures**: Document what didn't work and why
