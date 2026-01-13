---
name: review-code
description: Comprehensive code review workflow checking correctness, performance, security, style, tests, and documentation with severity levels
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# Review Code Skill

Comprehensive code review workflow that systematically checks correctness, performance, security, style, tests, and documentation. Generates review comments in GitHub/GitLab format.

## Workflow

### 1. Understand Context

- **Read PR/MR description**: What is being changed and why?
- **Check linked issues**: Understand the problem being solved
- **Review commit messages**: Trace the development history
- **Identify affected systems**: What parts of the codebase are impacted?

### 2. Review Checklist

#### A. Correctness

- **Logic errors**: Does the code do what it's supposed to?
- **Edge cases**: Are boundary conditions handled?
- **Error handling**: Are errors caught and handled appropriately?
- **Null/undefined checks**: Are nullable values checked?
- **Type safety**: Are types used correctly?
- **Business logic**: Does it match requirements and specifications?

#### B. Performance

- **Algorithmic complexity**: Are algorithms efficient? (O(n) vs O(n²))
- **Database queries**: N+1 queries? Missing indexes? Inefficient joins?
- **Caching**: Should results be cached?
- **Resource usage**: Memory leaks? File handles closed? Connections pooled?
- **Lazy loading**: Are expensive operations deferred when possible?
- **Batch operations**: Can multiple operations be batched?

#### C. Security

- **SQL injection**: Are queries parameterized?
- **XSS vulnerabilities**: Is user input sanitized?
- **CSRF protection**: Are state-changing operations protected?
- **Authentication**: Is auth required where needed?
- **Authorization**: Are permissions checked correctly?
- **Secrets management**: No hardcoded credentials?
- **Input validation**: Is user input validated and sanitized?
- **Dependencies**: Any known vulnerabilities in dependencies?

#### D. Style & Maintainability

- **Code style**: Follows project conventions?
- **Naming**: Are names clear and consistent?
- **Function size**: Are functions focused and reasonably sized?
- **Duplication**: Is code DRY (Don't Repeat Yourself)?
- **Comments**: Are complex sections explained? No outdated comments?
- **Magic numbers**: Are constants named and explained?
- **Complexity**: Are complex sections simplified where possible?

#### E. Tests

- **Test coverage**: Are new/changed lines covered?
- **Test quality**: Do tests actually validate behavior?
- **Edge cases tested**: Are boundary conditions tested?
- **Error cases tested**: Are error paths tested?
- **Test naming**: Are test names descriptive?
- **Test independence**: Can tests run in any order?
- **Flaky tests**: Are tests deterministic?

#### F. Documentation

- **README updated**: If public API changed, is README updated?
- **API docs**: Are public functions/classes documented?
- **Inline comments**: Are complex sections explained?
- **Migration guides**: If breaking changes, is migration documented?
- **Changelog**: Is CHANGELOG.md updated?

### 3. Generate Review Comments

Use this format for comments:

```markdown
### [SEVERITY] Category: Issue Title

**File**: `path/to/file.py` (Line X-Y)

**Issue**: Brief description of the problem

**Impact**: What could go wrong?

**Suggestion**:
```language
// Proposed fix or improvement
```

**Reasoning**: Why this change is recommended

**Priority**: High/Medium/Low
```

### 4. Severity Levels

- **CRITICAL**: Security vulnerabilities, data loss risks, production-breaking bugs
- **HIGH**: Correctness issues, performance problems, important missing tests
- **MEDIUM**: Code quality issues, minor bugs, missing documentation
- **LOW**: Style nitpicks, suggestions for improvement, optional refactoring

### 5. Review Modes

#### Quick Review (5-10 min)
- Focus on CRITICAL and HIGH issues only
- Automated checks (linting, tests, security scans)
- Obvious logic errors

#### Standard Review (15-30 min)
- All severity levels
- Full checklist coverage
- Constructive feedback

#### Deep Review (30+ min)
- Architecture analysis
- Performance profiling
- Security threat modeling
- Comprehensive testing review

### 6. Automated Checks

Run these before manual review:

```bash
# Linting
eslint . || pylint . || golangci-lint run

# Tests
npm test || pytest || go test ./...

# Coverage
npm test -- --coverage || pytest --cov || go test -cover ./...

# Security scanning
npm audit || safety check || gosec ./...

# Dependency check
npm outdated || pip list --outdated || go list -u -m all
```

### 7. Review Template

```markdown
## Review Summary

**Overall Assessment**: APPROVE / REQUEST_CHANGES / COMMENT

**Strengths**:
- What was done well

**Concerns**:
- Major issues that need addressing

**Suggestions**:
- Optional improvements

---

## Detailed Feedback

### Critical Issues
(None found / List critical issues)

### High Priority
(None found / List high priority issues)

### Medium Priority
(None found / List medium priority issues)

### Low Priority / Suggestions
(None found / List suggestions)

---

## Testing

- [ ] Tests pass locally
- [ ] Coverage is adequate
- [ ] Edge cases covered
- [ ] Error cases tested

## Security

- [ ] No secrets in code
- [ ] Input validation present
- [ ] Auth/authz checks correct
- [ ] Dependencies scanned

## Documentation

- [ ] README updated if needed
- [ ] API docs updated
- [ ] Complex code commented
- [ ] CHANGELOG updated
```

## GitHub/GitLab Comment Format

```markdown
<!-- Review comment for specific line -->
**[HIGH] Performance: N+1 Query**

This loop executes a database query for each item, causing an N+1 problem.

**Suggestion**:
```python
# Instead of:
for item in items:
    item.user = User.query.get(item.user_id)

# Use:
user_ids = [item.user_id for item in items]
users = User.query.filter(User.id.in_(user_ids)).all()
user_map = {user.id: user for user in users}
for item in items:
    item.user = user_map[item.user_id]
```

**Impact**: Can cause significant performance degradation with large datasets.
```

## Integration Points

- **CI/CD**: Ensure CI checks pass before review
- **Static analysis**: Use tools like SonarQube, CodeClimate
- **Security scanners**: Snyk, Dependabot, OWASP dependency check
- **Code coverage**: Codecov, Coveralls
- **Style checkers**: Prettier, Black, gofmt

## Tips for Reviewers

- **Be constructive**: Suggest improvements, don't just criticize
- **Explain why**: Help the author learn, don't just point out issues
- **Praise good work**: Acknowledge clever solutions and good practices
- **Ask questions**: If unclear, ask for clarification
- **Be timely**: Review within 24 hours when possible
- **Use automation**: Let tools catch style/formatting issues
- **Focus on impact**: Prioritize issues that matter most
- **Consider context**: Understand constraints and trade-offs

## Tips for Authors

- **Self-review first**: Review your own code before requesting review
- **Keep PRs small**: Easier to review, faster to merge
- **Write good descriptions**: Explain what and why
- **Respond to feedback**: Address comments, don't argue defensively
- **Test thoroughly**: Don't rely on reviewers to find bugs
- **Update based on feedback**: Make requested changes promptly

## Example Review

```markdown
## Review of PR #123: Add user profile feature

**Overall Assessment**: REQUEST_CHANGES

**Strengths**:
- Clean implementation of profile UI
- Good test coverage (92%)
- Well-documented API endpoints

**Concerns**:
- Security issue with profile image upload
- Missing validation on bio field

---

### [CRITICAL] Security: Unrestricted File Upload

**File**: `api/profile.py` (Line 45-52)

**Issue**: File upload doesn't validate file type or size

**Impact**: Could allow malicious file uploads (executable files, XXE attacks)

**Suggestion**:
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/profile/image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return error('No file provided')

    file = request.files['file']
    if not allowed_file(file.filename):
        return error('Invalid file type')

    if len(file.read()) > MAX_FILE_SIZE:
        return error('File too large')
    file.seek(0)  # Reset file pointer

    # ... rest of upload logic
```

**Priority**: CRITICAL - Must fix before merge

---

### [HIGH] Validation: Missing Input Sanitization

**File**: `api/profile.py` (Line 67)

**Issue**: Bio field allows unlimited length and isn't sanitized

**Suggestion**: Add length limit and HTML escaping

**Priority**: HIGH
```

## Best Practices

- Review in short sessions (max 60 min) to maintain focus
- Use checklists to ensure consistency
- Review code, not the person
- Assume good intent
- Provide actionable feedback
- Balance thoroughness with velocity
- Learn from reviews you receive
- Update review guidelines based on learnings
