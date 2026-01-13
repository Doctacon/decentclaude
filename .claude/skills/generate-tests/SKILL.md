---
name: generate-tests
description: Test generation workflow analyzing code, identifying edge cases, and generating comprehensive test suites with TDD and retrofit modes
allowed-tools:
  - Read
  - Grep
  - Write
  - Bash
---

# Generate Tests Skill

Automated test generation workflow that analyzes code structure, identifies edge cases, and creates comprehensive test suites including unit, integration, and property-based tests.

## Workflow

### 1. Analyze Code

**Identify testable units**:
- Public functions/methods
- Class constructors
- API endpoints
- Business logic

**Map inputs and outputs**:
- Parameters (types, constraints)
- Return values
- Side effects (DB writes, API calls)
- Exceptions

### 2. Generate Test Cases

**Test categories**:
1. **Happy path**: Normal, expected inputs
2. **Edge cases**: Boundary values (0, -1, null, empty)
3. **Error cases**: Invalid inputs, exceptions
4. **State variations**: Different object states

**Example analysis**:
```python
def calculate_discount(price: float, discount_rate: float) -> float:
    if price < 0:
        raise ValueError("Price cannot be negative")
    if not 0 <= discount_rate <= 1:
        raise ValueError("Discount rate must be between 0 and 1")
    return price * (1 - discount_rate)
```

**Generated tests**:
```python
import pytest

def test_calculate_discount_normal():
    assert calculate_discount(100, 0.2) == 80.0

def test_calculate_discount_zero_discount():
    assert calculate_discount(100, 0) == 100.0

def test_calculate_discount_full_discount():
    assert calculate_discount(100, 1) == 0.0

def test_calculate_discount_negative_price_raises_error():
    with pytest.raises(ValueError, match="Price cannot be negative"):
        calculate_discount(-10, 0.2)

def test_calculate_discount_invalid_rate_too_low():
    with pytest.raises(ValueError, match="must be between 0 and 1"):
        calculate_discount(100, -0.1)

def test_calculate_discount_invalid_rate_too_high():
    with pytest.raises(ValueError, match="must be between 0 and 1"):
        calculate_discount(100, 1.5)
```

### 3. Property-Based Testing

**Using Hypothesis (Python)**:
```python
from hypothesis import given, strategies as st

@given(
    price=st.floats(min_value=0, max_value=10000),
    discount_rate=st.floats(min_value=0, max_value=1)
)
def test_discount_never_negative(price, discount_rate):
    result = calculate_discount(price, discount_rate)
    assert result >= 0

@given(
    price=st.floats(min_value=0, max_value=10000),
    discount_rate=st.floats(min_value=0, max_value=1)
)
def test_discount_never_exceeds_price(price, discount_rate):
    result = calculate_discount(price, discount_rate)
    assert result <= price
```

## TDD Mode

**Test-first workflow**:
1. Write failing test
2. Write minimal code to pass
3. Refactor
4. Repeat

**Example**:
```python
# Step 1: Write test
def test_user_can_be_created():
    user = User(email="test@example.com", name="Test")
    assert user.email == "test@example.com"
    assert user.name == "Test"

# Step 2: Implement
class User:
    def __init__(self, email, name):
        self.email = email
        self.name = name

# Step 3: Test passes, add more tests
```

## Best Practices

- Test behavior, not implementation
- One assertion per test (when reasonable)
- Use descriptive test names
- Arrange-Act-Assert pattern
- Mock external dependencies
- Test edge cases thoroughly
