---
name: add-tests
description: Test addition workflow that analyzes coverage, identifies untested paths, generates test cases, and validates tests pass
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
  - Write
---

# Add Tests Skill

Comprehensive test addition workflow that analyzes code coverage, identifies untested paths, generates test cases (unit, integration, e2e), and validates tests pass.

## Workflow

### 1. Analyze Current Coverage

**Run coverage analysis**:

```bash
# Python (pytest)
pytest --cov=module --cov-report=html --cov-report=term-missing
open htmlcov/index.html

# JavaScript (Jest)
npm test -- --coverage
open coverage/lcov-report/index.html

# Go
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html
open coverage.html
```

**Identify gaps**:
- Which files have low coverage (<80%)?
- Which functions/methods are untested?
- Which branches (if/else) are untested?
- Which edge cases are missing?

### 2. Prioritize Test Coverage

Focus on:
1. **Critical paths**: Core business logic, security-sensitive code
2. **Bug-prone areas**: Code that has had bugs before
3. **Complex logic**: Conditional branches, loops, error handling
4. **Public APIs**: Functions/methods called by other modules
5. **Recently changed code**: New features, bug fixes

Lower priority:
- Trivial getters/setters
- Generated code
- Third-party library wrappers (test integration, not library itself)

### 3. Identify Test Types Needed

#### Unit Tests
- Test individual functions/methods in isolation
- Mock external dependencies
- Fast execution (milliseconds)
- High coverage of logic paths

#### Integration Tests
- Test multiple components together
- Real dependencies (database, APIs) or realistic fakes
- Medium execution time (seconds)
- Validate component interactions

#### End-to-End Tests
- Test complete user workflows
- Real environment or production-like staging
- Slow execution (minutes)
- Validate system behavior

**Rule of thumb**: Test pyramid
- 70% unit tests
- 20% integration tests
- 10% e2e tests

### 4. Analyze Code for Test Cases

For each untested function/method:

**Identify inputs**:
- Parameters
- Instance variables
- Global state
- External dependencies (database, API, file system)

**Identify outputs**:
- Return values
- Side effects (database writes, file changes, API calls)
- Exceptions/errors

**Identify test scenarios**:
- **Happy path**: Normal, expected input
- **Edge cases**: Boundary values (0, -1, max int, empty string)
- **Error cases**: Invalid input, missing data, exceptions
- **State variations**: Different pre-conditions

### 5. Write Test Cases

#### Test Structure (AAA Pattern)

```python
def test_calculate_discount():
    # Arrange: Set up test data and dependencies
    product = Product(price=100)
    discount_rate = 0.2

    # Act: Execute the code under test
    result = calculate_discount(product, discount_rate)

    # Assert: Verify the expected outcome
    assert result == 20
```

#### Unit Test Example (Python - pytest)

```python
# tests/test_calculator.py
import pytest
from calculator import Calculator

class TestCalculator:
    def test_add_positive_numbers(self):
        calc = Calculator()
        result = calc.add(2, 3)
        assert result == 5

    def test_add_negative_numbers(self):
        calc = Calculator()
        result = calc.add(-2, -3)
        assert result == -5

    def test_add_zero(self):
        calc = Calculator()
        result = calc.add(5, 0)
        assert result == 5

    def test_divide_by_zero_raises_error(self):
        calc = Calculator()
        with pytest.raises(ZeroDivisionError):
            calc.divide(10, 0)

    @pytest.mark.parametrize("a,b,expected", [
        (1, 1, 2),
        (0, 0, 0),
        (-1, 1, 0),
        (100, 200, 300),
    ])
    def test_add_multiple_cases(self, a, b, expected):
        calc = Calculator()
        assert calc.add(a, b) == expected
```

#### Unit Test Example (JavaScript - Jest)

```javascript
// tests/calculator.test.js
import { Calculator } from '../src/calculator';

describe('Calculator', () => {
  let calculator;

  beforeEach(() => {
    calculator = new Calculator();
  });

  describe('add', () => {
    it('should add two positive numbers', () => {
      expect(calculator.add(2, 3)).toBe(5);
    });

    it('should add negative numbers', () => {
      expect(calculator.add(-2, -3)).toBe(-5);
    });

    it('should handle zero', () => {
      expect(calculator.add(5, 0)).toBe(5);
    });
  });

  describe('divide', () => {
    it('should divide numbers', () => {
      expect(calculator.divide(10, 2)).toBe(5);
    });

    it('should throw error on division by zero', () => {
      expect(() => calculator.divide(10, 0)).toThrow('Division by zero');
    });
  });
});
```

#### Unit Test Example (Go)

```go
// calculator_test.go
package calculator

import "testing"

func TestAdd(t *testing.T) {
    tests := []struct {
        name string
        a, b int
        want int
    }{
        {"positive numbers", 2, 3, 5},
        {"negative numbers", -2, -3, -5},
        {"with zero", 5, 0, 5},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := Add(tt.a, tt.b)
            if got != tt.want {
                t.Errorf("Add(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.want)
            }
        })
    }
}

func TestDivideByZero(t *testing.T) {
    _, err := Divide(10, 0)
    if err == nil {
        t.Error("Expected error for division by zero, got nil")
    }
}
```

#### Integration Test Example (Python)

```python
# tests/integration/test_user_service.py
import pytest
from app import create_app, db
from app.models import User
from app.services import UserService

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def user_service(app):
    return UserService()

def test_create_user_saves_to_database(app, user_service):
    # Arrange
    user_data = {
        'email': 'test@example.com',
        'password': 'secure_password'
    }

    # Act
    user = user_service.create_user(**user_data)

    # Assert
    saved_user = User.query.filter_by(email=user_data['email']).first()
    assert saved_user is not None
    assert saved_user.email == user_data['email']
    assert saved_user.check_password(user_data['password'])
```

#### E2E Test Example (JavaScript - Playwright)

```javascript
// tests/e2e/login.spec.js
import { test, expect } from '@playwright/test';

test('user can log in successfully', async ({ page }) => {
  // Navigate to login page
  await page.goto('/login');

  // Fill in credentials
  await page.fill('input[name="email"]', 'user@example.com');
  await page.fill('input[name="password"]', 'password123');

  // Click login button
  await page.click('button[type="submit"]');

  // Verify redirect to dashboard
  await expect(page).toHaveURL('/dashboard');

  // Verify user name is displayed
  await expect(page.locator('.user-name')).toContainText('John Doe');
});
```

### 6. Mock External Dependencies

#### Python (unittest.mock)

```python
from unittest.mock import Mock, patch
import pytest

def test_send_notification_calls_email_service():
    # Mock the email service
    mock_email = Mock()

    # Test the notification function
    send_notification(mock_email, 'user@example.com', 'Hello')

    # Verify email service was called correctly
    mock_email.send.assert_called_once_with(
        to='user@example.com',
        message='Hello'
    )

@patch('app.services.requests.get')
def test_fetch_user_data(mock_get):
    # Mock API response
    mock_get.return_value.json.return_value = {'id': 1, 'name': 'Alice'}

    # Call function
    user = fetch_user_data(1)

    # Verify
    assert user['name'] == 'Alice'
    mock_get.assert_called_with('https://api.example.com/users/1')
```

#### JavaScript (Jest)

```javascript
import { sendNotification } from '../src/notifications';
import { emailService } from '../src/services/email';

jest.mock('../src/services/email');

test('sendNotification calls email service', () => {
  sendNotification('user@example.com', 'Hello');

  expect(emailService.send).toHaveBeenCalledWith(
    'user@example.com',
    'Hello'
  );
});
```

### 7. Test Edge Cases

**Common edge cases to test**:

- **Boundary values**: 0, -1, MAX_INT, MIN_INT, empty string, null
- **Empty collections**: [], {}, null, undefined
- **Large inputs**: Very long strings, large arrays, deep nesting
- **Special characters**: Unicode, SQL special chars, HTML/XML chars
- **Concurrent access**: Race conditions, thread safety
- **Network issues**: Timeouts, connection failures, retries
- **File system**: Permissions, disk full, missing files
- **Date/time**: Timezones, DST, leap years, epoch boundaries

### 8. Validate Tests Pass

```bash
# Run new tests
pytest tests/test_module.py -v
npm test -- tests/module.test.js
go test ./pkg/module/... -v

# Run full test suite (ensure no regressions)
pytest
npm test
go test ./...

# Verify coverage improved
pytest --cov=module --cov-report=term-missing
npm test -- --coverage
go test -cover ./...
```

**Green tests required before proceeding**:
- All new tests pass
- All existing tests still pass
- Coverage increased (or at minimum maintained)

### 9. Commit Tests

```bash
git add tests/
git commit -m "test: Add tests for user authentication

- Add unit tests for password hashing
- Add integration tests for login flow
- Add edge case tests for invalid inputs
- Coverage increased from 65% to 92%"
```

## Test Quality Guidelines

### Good Test Characteristics

- **Fast**: Unit tests run in milliseconds
- **Isolated**: No dependencies on other tests
- **Repeatable**: Same result every time
- **Self-validating**: Pass/fail is clear, no manual verification
- **Timely**: Written close to when code is written

### Bad Test Smells

- **Slow tests**: Taking seconds for unit tests
- **Flaky tests**: Sometimes pass, sometimes fail
- **Brittle tests**: Break when unrelated code changes
- **Unclear tests**: Hard to understand what's being tested
- **Testing implementation**: Testing how code works vs what it does

### Test Naming Conventions

**Good names describe behavior**:

```python
# Good
def test_login_with_invalid_password_returns_error():
def test_cart_total_includes_tax():
def test_empty_cart_checkout_raises_exception():

# Bad
def test_login():
def test_calculate():
def test_case_1():
```

## Testing Patterns

### Parameterized Tests

**Python**:
```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("WORLD", "WORLD"),
    ("", ""),
    ("123", "123"),
])
def test_to_uppercase(input, expected):
    assert to_uppercase(input) == expected
```

**JavaScript**:
```javascript
test.each([
  ['hello', 'HELLO'],
  ['WORLD', 'WORLD'],
  ['', ''],
  ['123', '123'],
])('toUppercase(%s) returns %s', (input, expected) => {
  expect(toUppercase(input)).toBe(expected);
});
```

### Fixtures and Setup

**Python**:
```python
@pytest.fixture
def database():
    db = Database(':memory:')
    db.create_tables()
    yield db
    db.close()

def test_user_creation(database):
    user = database.create_user('alice')
    assert user.name == 'alice'
```

**JavaScript**:
```javascript
describe('Database', () => {
  let db;

  beforeEach(() => {
    db = new Database(':memory:');
    db.createTables();
  });

  afterEach(() => {
    db.close();
  });

  it('creates user', () => {
    const user = db.createUser('alice');
    expect(user.name).toBe('alice');
  });
});
```

### Test Doubles

- **Mock**: Verifies interactions (method called with args)
- **Stub**: Returns predefined values
- **Fake**: Simplified working implementation
- **Spy**: Records interactions for later verification

## Tools & Frameworks

### Python
- **pytest**: Primary testing framework
- **unittest**: Built-in testing framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking utilities
- **hypothesis**: Property-based testing

### JavaScript
- **Jest**: All-in-one testing framework
- **Mocha**: Test runner
- **Chai**: Assertion library
- **Sinon**: Mocking/stubbing
- **Playwright/Cypress**: E2E testing

### Go
- **testing**: Built-in testing package
- **testify**: Assertions and mocks
- **gomock**: Mock generation
- **httptest**: HTTP testing utilities

## Best Practices

- **Write tests first (TDD)**: Define behavior before implementation
- **Test behavior, not implementation**: Don't test private methods
- **One assertion per test** (when reasonable): Makes failures clear
- **Use descriptive test names**: Test name should explain scenario
- **Keep tests simple**: Tests should be easier than code under test
- **Don't test framework code**: Trust that libraries work
- **Avoid test interdependence**: Tests should run in any order
- **Update tests when requirements change**: Keep tests in sync

## Common Pitfalls

- Testing getters/setters (low value)
- Overmocking (tests become coupled to implementation)
- Not testing error cases
- Flaky tests (random failures)
- Slow tests (reduces productivity)
- Too many integration tests (test pyramid inverted)
- Ignoring failing tests (maintain test hygiene)
