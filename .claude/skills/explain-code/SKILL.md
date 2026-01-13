---
name: explain-code
description: Code explanation workflow analyzing complex code, generating plain-English explanations, creating documentation, and identifying patterns
allowed-tools:
  - Read
  - Grep
  - Glob
---

# Explain Code Skill

Code explanation workflow for analyzing complex algorithms, design patterns, and unfamiliar codebases. Generates clear explanations, documentation, and identifies improvement opportunities.

## Workflow

### 1. Read and Understand Context

**Gather information**:
- What does this code do at a high level?
- Where is it called from?
- What are the inputs and outputs?
- What's the broader system context?

```bash
# Find usages
grep -r "function_name" --include="*.py"

# Find callers
grep -r "import.*module" --include="*.py"
```

### 2. Analyze Code Structure

**Break down into sections**:
1. Imports and dependencies
2. Constants and configuration
3. Helper functions
4. Main logic
5. Error handling
6. Return values

### 3. Generate Explanation

**Explanation template**:

```markdown
## What This Code Does

[One-sentence summary]

## How It Works

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Key Concepts

- **Concept 1**: Explanation
- **Concept 2**: Explanation

## Example

[Show example usage with inputs and outputs]

## Edge Cases

- [Edge case 1]
- [Edge case 2]

## Potential Issues

- [Issue 1]
- [Issue 2]
```

### 4. Identify Patterns

Common patterns to recognize:
- **Factory Pattern**: Creates objects without specifying exact class
- **Singleton**: Ensures only one instance exists
- **Observer**: Pub/sub pattern for events
- **Decorator**: Adds behavior to objects dynamically
- **Strategy**: Selects algorithm at runtime
- **Repository**: Abstracts data access

### 5. Suggest Improvements

Look for:
- Code smells (long functions, deep nesting)
- Missing error handling
- Performance bottlenecks
- Security vulnerabilities
- Missing tests
- Poor naming

## Example Explanation

**Complex code**:
```python
def f(x, y, z):
    return [i for i in range(x) if i % y == 0 and i % z != 0]
```

**Explanation**:
```markdown
## What This Code Does

Returns a list of numbers from 0 to x-1 that are divisible by y but not divisible by z.

## How It Works

1. Generates numbers from 0 to x-1 using range()
2. Filters numbers divisible by y (remainder is 0)
3. Excludes numbers divisible by z (remainder is not 0)
4. Returns resulting list

## Example

```python
f(20, 3, 6)  # Returns [3, 9, 15]
# 3: divisible by 3, not by 6
# 9: divisible by 3, not by 6
# 15: divisible by 3, not by 6
# (6, 12, 18 are excluded because divisible by both)
```

## Suggested Improvements

```python
def find_numbers_divisible_by_y_not_z(max_num, divisor_y, divisor_z):
    """
    Find numbers divisible by y but not z.

    Args:
        max_num: Upper bound (exclusive)
        divisor_y: Numbers must be divisible by this
        divisor_z: Numbers must NOT be divisible by this

    Returns:
        List of numbers matching criteria
    """
    return [
        num for num in range(max_num)
        if num % divisor_y == 0 and num % divisor_z != 0
    ]
```

## Best Practices

- Explain **why**, not just **what**
- Use analogies for complex concepts
- Provide concrete examples
- Highlight edge cases
- Identify potential issues
- Suggest improvements
