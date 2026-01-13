---
name: refactor
description: Systematic refactoring workflow to improve code quality while preserving behavior through incremental changes with test verification
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
  - Write
---

# Refactor Skill

Systematic refactoring workflow that improves code quality while preserving behavior. Supports extract method, rename, move, simplify, and other refactoring patterns.

## Workflow

### 1. Identify Code Smells

Common signs that refactoring is needed:

- **Long methods/functions**: More than 30-50 lines
- **Large classes**: Too many responsibilities
- **Duplicated code**: Same logic in multiple places
- **Long parameter lists**: More than 3-4 parameters
- **Complex conditionals**: Nested if/else, hard to understand
- **Dead code**: Unused variables, functions, imports
- **Magic numbers**: Unexplained constants
- **Poor naming**: Unclear variable/function names
- **Feature envy**: Method uses another class more than its own
- **Data clumps**: Same group of variables passed together
- **Primitive obsession**: Using primitives instead of small objects
- **Comments**: Explaining what code does (code should be self-explanatory)

### 2. Plan Refactoring

- **Set clear goal**: What specific improvement are you making?
- **Assess risk**: How much of the codebase is affected?
- **Check test coverage**: Ensure existing tests cover the code
- **Define success**: How will you know the refactoring succeeded?
- **Break it down**: Plan incremental steps
- **Estimate time**: Keep refactoring sessions focused (30-60 min)

### 3. Preserve Tests

CRITICAL: Before refactoring, ensure tests exist and pass.

```bash
# Run full test suite
npm test || pytest || go test ./...

# Check coverage of code to be refactored
npm test -- --coverage --testPathPattern=module
pytest --cov=module tests/
go test -cover ./pkg/module/...
```

**If tests don't exist**: Write characterization tests first
- Document current behavior (even if wrong)
- These tests ensure behavior doesn't change during refactoring
- Can update tests after refactoring if behavior should change

### 4. Make Incremental Changes

**Key principle**: One refactoring at a time, with tests passing after each step.

#### Common Refactoring Patterns

##### Extract Method/Function

**Before**:
```python
def process_order(order):
    # Calculate total
    total = 0
    for item in order.items:
        total += item.price * item.quantity
        if item.discount:
            total -= item.discount

    # Apply tax
    tax_rate = 0.08
    tax = total * tax_rate
    total += tax

    # Save order
    order.total = total
    order.save()
```

**After**:
```python
def process_order(order):
    total = calculate_order_total(order.items)
    total_with_tax = apply_tax(total)
    save_order(order, total_with_tax)

def calculate_order_total(items):
    total = 0
    for item in items:
        total += item.price * item.quantity
        if item.discount:
            total -= item.discount
    return total

def apply_tax(amount, rate=0.08):
    return amount * (1 + rate)

def save_order(order, total):
    order.total = total
    order.save()
```

##### Rename

**Before**:
```javascript
function calc(a, b) {
    return a * b * 0.08;
}
```

**After**:
```javascript
function calculateSalesTax(price, quantity) {
    const TAX_RATE = 0.08;
    const subtotal = price * quantity;
    return subtotal * TAX_RATE;
}
```

**Steps**:
1. Use IDE refactoring tools when possible
2. Or manually: Find all usages, rename systematically
3. Update related documentation/comments
4. Run tests after renaming

##### Extract Variable/Constant

**Before**:
```go
if user.age >= 18 && user.age <= 65 && user.income > 50000 {
    // eligible
}
```

**After**:
```go
const (
    MIN_AGE = 18
    MAX_AGE = 65
    MIN_INCOME = 50000
)

isAgeEligible := user.age >= MIN_AGE && user.age <= MAX_AGE
isIncomeEligible := user.income > MIN_INCOME

if isAgeEligible && isIncomeEligible {
    // eligible
}
```

##### Simplify Conditional

**Before**:
```python
if user is not None:
    if user.is_active:
        if user.has_permission('admin'):
            return True
return False
```

**After**:
```python
return (user is not None and
        user.is_active and
        user.has_permission('admin'))
```

##### Replace Magic Number

**Before**:
```javascript
setTimeout(retryConnection, 5000);
```

**After**:
```javascript
const RETRY_DELAY_MS = 5000; // 5 seconds
setTimeout(retryConnection, RETRY_DELAY_MS);
```

##### Extract Class

**Before**:
```python
class Order:
    def __init__(self):
        self.items = []
        self.customer_name = ""
        self.customer_email = ""
        self.customer_address = ""
        self.shipping_method = ""
        self.shipping_cost = 0
```

**After**:
```python
class Customer:
    def __init__(self, name, email, address):
        self.name = name
        self.email = email
        self.address = address

class Shipping:
    def __init__(self, method, cost):
        self.method = method
        self.cost = cost

class Order:
    def __init__(self):
        self.items = []
        self.customer = None
        self.shipping = None
```

##### Consolidate Duplicate Code

**Before**:
```javascript
function getUserAdmin(id) {
    const user = db.users.findOne({id});
    if (!user) throw new Error('User not found');
    if (!user.isAdmin) throw new Error('Not admin');
    return user;
}

function getUserModerator(id) {
    const user = db.users.findOne({id});
    if (!user) throw new Error('User not found');
    if (!user.isModerator) throw new Error('Not moderator');
    return user;
}
```

**After**:
```javascript
function getUserWithRole(id, role, roleName) {
    const user = db.users.findOne({id});
    if (!user) throw new Error('User not found');
    if (!user[role]) throw new Error(`Not ${roleName}`);
    return user;
}

function getUserAdmin(id) {
    return getUserWithRole(id, 'isAdmin', 'admin');
}

function getUserModerator(id) {
    return getUserWithRole(id, 'isModerator', 'moderator');
}
```

##### Remove Dead Code

```bash
# Find unused imports (Python)
autoflake --remove-all-unused-imports --in-place file.py

# Find unused variables (JavaScript)
eslint --rule 'no-unused-vars: error'

# Find unused functions (manual)
grep -r "function_name" . --exclude-dir=node_modules
```

### 5. Verify Behavior Unchanged

After EACH refactoring step:

```bash
# Run tests
npm test || pytest || go test ./...

# Run specific tests for refactored code
npm test -- --testPathPattern=module
pytest tests/test_module.py
go test ./pkg/module/...

# Check test coverage hasn't decreased
npm test -- --coverage
pytest --cov --cov-report=term-missing
go test -cover ./...

# Manual verification if needed
# - Run application locally
# - Test key user flows
# - Check logs for errors
```

**If tests fail**:
1. DON'T proceed to next refactoring
2. Debug and fix the issue
3. If stuck, revert the change
4. Reconsider the approach

### 6. Commit Incremental Changes

```bash
# Commit after each successful refactoring
git add -A
git commit -m "refactor: Extract calculate_total method

- Moved calculation logic to separate function
- Improved readability and testability
- All tests passing"
```

Benefits of incremental commits:
- Easy to review
- Easy to revert if issues arise
- Clear history of changes
- Safer for code review

### 7. Update Documentation

- **Inline comments**: Remove comments that explain what code does (if self-explanatory now)
- **API docs**: Update if public interfaces changed
- **README**: Update examples if refactoring affects usage
- **Architecture docs**: Update if structure changed significantly

### 8. Final Verification

```bash
# Full test suite
npm test || pytest || go test ./...

# Linting
npm run lint || flake8 || golangci-lint run

# Type checking (if applicable)
npm run type-check || mypy . || go vet ./...

# Build/compile
npm run build || python setup.py build || go build ./...

# Integration tests
npm run test:integration || pytest tests/integration/
```

## Refactoring Strategies

### The Strangler Fig Pattern

For large-scale refactoring:
1. Create new implementation alongside old
2. Gradually route traffic to new implementation
3. Eventually remove old implementation

### Branch by Abstraction

1. Create abstraction layer
2. Implement new version behind abstraction
3. Switch to new version
4. Remove old version and abstraction

### Parallel Change (Expand-Contract)

1. **Expand**: Add new interface without removing old
2. **Migrate**: Update callers to use new interface
3. **Contract**: Remove old interface

## Tools & Automation

### IDE Refactoring Tools

- **VS Code**: F2 for rename, Extract method/variable
- **IntelliJ/PyCharm**: Ctrl+Alt+Shift+T for refactoring menu
- **Vim**: Use plugins like vim-refactor

### Automated Refactoring

```bash
# JavaScript/TypeScript
npx jscodeshift -t transform.js src/

# Python
python -m rope.refactor.rename old_name new_name file.py

# Go
gofmt -r 'old -> new' -w .
```

### Linters with Auto-fix

```bash
# JavaScript
eslint --fix .

# Python
autopep8 --in-place --recursive .
black .

# Go
gofmt -w .
```

## Anti-Patterns to Avoid

- **Refactoring without tests**: High risk of breaking things
- **Big bang refactoring**: Change everything at once
- **Refactoring during feature development**: Mix refactoring and new features
- **Premature optimization**: Refactor for readability first, performance second
- **Over-engineering**: Keep it simple
- **Ignoring code review**: Get feedback on refactoring plans

## Best Practices

- **Test before, during, and after**: Cannot stress this enough
- **One refactoring at a time**: Don't mix multiple refactoring patterns
- **Commit frequently**: Small, focused commits
- **Use automation**: Let tools handle mechanical refactoring
- **Pair program**: Two sets of eyes reduce risk
- **Time-box sessions**: Refactoring can be endless; set limits
- **Prioritize high-value refactoring**: Focus on code that changes frequently
- **Boy Scout Rule**: Leave code better than you found it

## When NOT to Refactor

- Code is about to be deleted
- Deadline is imminent and refactoring isn't critical
- Tests don't exist and can't be written
- Refactoring would require changing public API with breaking changes
- The "improvement" is subjective and minor

## Example Refactoring Session

```
Session Goal: Refactor user authentication module
Time Budget: 60 minutes

Step 1 (5 min): Run tests, verify all pass (20/20 ✓)
Step 2 (10 min): Extract password hashing to separate function
  - Commit: "refactor: Extract hash_password function"
  - Tests: 20/20 ✓
Step 3 (10 min): Extract token generation to separate function
  - Commit: "refactor: Extract generate_token function"
  - Tests: 20/20 ✓
Step 4 (15 min): Rename vague variable names (u -> user, t -> token)
  - Commit: "refactor: Improve variable naming"
  - Tests: 20/20 ✓
Step 5 (10 min): Extract validation to separate module
  - Commit: "refactor: Extract validation to auth.validation"
  - Tests: 20/20 ✓
Step 6 (10 min): Update documentation and add examples
  - Commit: "docs: Update auth module documentation"

Total: 60 minutes, 5 refactoring commits, all tests green ✓
```
