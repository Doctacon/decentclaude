# Code Review Comment Templates

> **Quick reference**: Copy-paste templates for common code review feedback

## Table of Contents

- [General Feedback](#general-feedback)
- [Code Quality](#code-quality)
- [Security](#security)
- [Performance](#performance)
- [Testing](#testing)
- [Data Engineering Specific](#data-engineering-specific)
- [Documentation](#documentation)
- [Git & Process](#git--process)
- [Positive Feedback](#positive-feedback)

## General Feedback

### Request Clarification
```markdown
❓ **Question**: Can you explain why [specific choice] was made here?

I'm trying to understand [what you're confused about] to better review this change.
```

### Suggest Alternative Approach
```markdown
💡 **Suggestion**: Consider [alternative approach]

This would [benefit/improvement] because [reason].

Would you be open to this approach?
```

### Flag as Blocking
```markdown
🚨 **Blocking**: [Issue description]

This must be addressed before merge because [reason].

Suggested fix: [specific recommendation]
```

### Flag as Non-Blocking
```markdown
💭 **Optional**: [Suggestion]

This is a nice-to-have improvement but not required for this PR.
Feel free to address in a follow-up or skip if you disagree.
```

## Code Quality

### Code Complexity
```markdown
🔍 **Complexity**: This function/block is doing too much

Consider breaking this into smaller, focused functions:
- [Function 1]: [responsibility]
- [Function 2]: [responsibility]

This will improve readability and testability.
```

### Naming Issues
```markdown
📝 **Naming**: The name `[current_name]` doesn't clearly convey its purpose

Consider renaming to `[suggested_name]` to better indicate that it [what it does].
```

### Magic Numbers
```markdown
🔢 **Magic Number**: Hard-coded value should be a named constant

Consider:
\`\`\`python
MAX_RETRY_ATTEMPTS = 3  # or appropriate name
DEFAULT_TIMEOUT_SECONDS = 30
\`\`\`

This improves readability and maintainability.
```

### Code Duplication
```markdown
♻️ **DRY Violation**: This logic is duplicated in [location]

Consider extracting to a shared function/utility to avoid duplication.

Reference: [link to other occurrence]
```

### Error Handling Missing
```markdown
⚠️ **Error Handling**: What happens if [error scenario]?

Consider adding error handling for:
- [Scenario 1]
- [Scenario 2]

Example:
\`\`\`python
try:
    # existing code
except SpecificException as e:
    # handle error appropriately
\`\`\`
```

### Overly Defensive Code
```markdown
🛡️ **Over-defensive**: This check seems unnecessary

Since [reason why it can't happen], we can safely remove this validation.
This simplifies the code without compromising safety.
```

## Security

### Secrets in Code
```markdown
🔒 **CRITICAL - Security**: Secrets/credentials detected

**This must be fixed before merge.**

Please:
1. Remove the secret from this file
2. Rotate the compromised credential
3. Use environment variables or secrets manager
4. Rewrite git history to remove from all commits

Reference: [link to secrets management docs]
```

### SQL Injection Risk
```markdown
🔒 **Security - SQL Injection**: User input not sanitized

This code is vulnerable to SQL injection. Use parameterized queries:

**Bad:**
\`\`\`python
query = f"SELECT * FROM users WHERE id = {user_id}"
\`\`\`

**Good:**
\`\`\`python
query = "SELECT * FROM users WHERE id = @user_id"
params = {"user_id": user_id}
\`\`\`
```

### Authentication/Authorization Missing
```markdown
🔒 **Security - Auth**: Missing authentication check

This endpoint/function should verify:
- User is authenticated
- User has permission to [action]

Add appropriate auth checks before proceeding with the operation.
```

### Input Validation Missing
```markdown
🔒 **Security - Input Validation**: User input not validated

Validate and sanitize this input to prevent:
- Injection attacks
- Malformed data
- Unexpected types

Example validation: [specific validation needed]
```

## Performance

### N+1 Query Problem
```markdown
⚡ **Performance - N+1 Queries**: This will make [N] database queries

For each item in [collection], this makes a separate query.
Consider using a join or batch query instead:

\`\`\`python
# Fetch all related data in one query
related_data = fetch_related_batch(item_ids)
\`\`\`

Impact: [N] queries → 1 query
```

### Inefficient BigQuery Query
```markdown
⚡ **Performance - BigQuery**: This query will scan the entire table

Issues:
- No partition filter on partitioned table
- `SELECT *` instead of specific columns
- Missing WHERE clause optimization

Estimated cost: [X] GB scanned

Suggested optimization:
\`\`\`sql
-- Add partition filter
WHERE DATE(timestamp_column) = CURRENT_DATE()
-- Select only needed columns
SELECT id, name, value
\`\`\`
```

### Missing Index
```markdown
⚡ **Performance - Indexing**: Consider adding an index

This query will perform a full table scan on [table].
Add an index on [column(s)] to improve performance.

Expected impact: [estimated improvement]
```

### Unnecessary Computation
```markdown
⚡ **Performance**: This computation could be cached/memoized

This [expensive operation] is called multiple times with the same inputs.
Consider caching the result or computing once.
```

## Testing

### Missing Tests
```markdown
🧪 **Testing**: Tests needed for this change

Please add tests covering:
- [ ] Happy path: [scenario]
- [ ] Edge case: [scenario]
- [ ] Error case: [scenario]

The current test coverage doesn't verify [specific behavior].
```

### Test Quality Issues
```markdown
🧪 **Test Quality**: This test doesn't adequately verify behavior

Issues:
- Doesn't test [critical behavior]
- Uses overly broad assertions
- Doesn't test edge cases

Suggested improvements:
- Assert specific values, not just "is not None"
- Add test for [edge case]
```

### Flaky Test
```markdown
🧪 **Flaky Test**: This test may be non-deterministic

Potential issues:
- Timing dependencies
- Random data without seed
- Shared state between tests

Consider: [specific fix]
```

### Missing Test Data Cleanup
```markdown
🧪 **Test Cleanup**: Test data should be cleaned up

This test creates [data] but doesn't clean it up.
Use fixtures or teardown to ensure clean state:

\`\`\`python
@pytest.fixture
def test_data():
    data = create_test_data()
    yield data
    cleanup_test_data(data)
\`\`\`
```

## Data Engineering Specific

### Missing Data Quality Tests
```markdown
📊 **Data Quality**: Add data quality tests

For this model, please add tests for:
- [ ] Unique key constraint
- [ ] Not-null check on critical columns
- [ ] Referential integrity
- [ ] Accepted values for categorical columns
- [ ] Freshness check

Reference: `data-testing-patterns.md`
```

### Schema Not Backward Compatible
```markdown
📊 **Breaking Change**: Schema change breaks backward compatibility

Removing/renaming `[column_name]` will break:
- [Downstream system 1]
- [Downstream system 2]

Please either:
1. Keep old column and add new one (deprecation period)
2. Coordinate with downstream teams on migration
3. Provide migration script

Migration plan needed before merge.
```

### Missing Partitioning
```markdown
📊 **BigQuery Optimization**: This table should be partitioned

This table will grow large and should be partitioned by [field].

Benefits:
- Reduced query costs
- Improved query performance
- Better data lifecycle management

\`\`\`sql
PARTITION BY DATE(timestamp_column)
\`\`\`
```

### Missing Cost Estimate
```markdown
📊 **Cost**: Query cost not estimated

Please run BigQuery dry run and provide:
- Estimated bytes scanned
- Estimated cost
- Expected frequency of query

Use: `bq query --dry_run < query.sql`
```

### Incremental Logic Issue
```markdown
📊 **Incremental Model**: Incremental logic may miss data

Issues with this incremental strategy:
- [Specific issue]

Consider:
- Full refresh for historical data
- More robust incremental filter
- Testing backfill scenario
```

### Missing Data Documentation
```markdown
📊 **Documentation**: Data model needs documentation

Please document:
- [ ] Business purpose of this model
- [ ] Column definitions
- [ ] Data lineage/sources
- [ ] Known limitations
- [ ] Example queries

Use template: `docs/templates/data-model.md`
```

## Documentation

### Missing Documentation
```markdown
📚 **Documentation**: Please add documentation for [component]

Users/developers will need to understand:
- What this does
- How to use it
- Any gotchas or limitations

Consider adding: [specific docs needed]
```

### Outdated Documentation
```markdown
📚 **Documentation**: Update documentation to match changes

These docs are now outdated:
- [Doc 1]: [what needs updating]
- [Doc 2]: [what needs updating]
```

### Unclear Comments
```markdown
📚 **Comment Clarity**: This comment doesn't add value

The comment "# Process data" doesn't explain *how* or *why*.
Either improve the comment or remove it if the code is self-explanatory.

Better: "# Deduplicate records using ROW_NUMBER to keep most recent version"
```

### Missing Example
```markdown
📚 **Examples**: Add usage example

This would be clearer with an example showing:
- [Example scenario 1]
- [Example scenario 2]

Example:
\`\`\`python
# Example usage
result = function_name(param1, param2)
\`\`\`
```

## Git & Process

### Commit Message Unclear
```markdown
📝 **Commit Message**: Commit message should be more descriptive

Current: "[current message]"
Better: "[suggested message]"

Good commit messages explain what and why, not just what.
```

### Unrelated Changes
```markdown
🎯 **Scope**: This change seems unrelated to the PR purpose

This PR is for [stated purpose], but this change [what it does].
Consider moving to a separate PR for clarity.
```

### Missing Issue/Bead Link
```markdown
🔗 **Tracking**: Link to related issue/bead

Please link to the bead or issue this addresses for traceability.

Format: `Addresses: bd-XXX` or link in description.
```

### Large PR
```markdown
📦 **PR Size**: This PR is quite large

Consider breaking into smaller PRs:
1. [Subset 1]
2. [Subset 2]
3. [Subset 3]

Smaller PRs are easier to review and safer to merge.
```

## Positive Feedback

### Good Pattern
```markdown
✅ **Nice Pattern**: Great use of [pattern/principle]

This is a good example of [what was done well].
[Why it's good / what others can learn from it]
```

### Good Test Coverage
```markdown
✅ **Great Testing**: Excellent test coverage

I particularly like:
- Edge case testing
- Clear test naming
- Good use of fixtures
```

### Good Documentation
```markdown
✅ **Clear Documentation**: The documentation is very helpful

This will make it easy for others to understand and use this feature.
```

### Clean Code
```markdown
✅ **Readable Code**: This code is very clear and maintainable

Easy to understand what's happening without needing comments.
Good variable names and logical structure.
```

### Good Error Handling
```markdown
✅ **Robust**: Excellent error handling

This handles edge cases gracefully and provides helpful error messages.
```

### Performance Optimization
```markdown
✅ **Performance**: Nice optimization

This improvement will [specific benefit].
Good catch!
```

### Learning Moment
```markdown
📖 **TIL**: I learned something from this!

I didn't know about [concept/approach]. Thanks for introducing this pattern!
```

## Template Usage Tips

1. **Customize the template** - Add specific details relevant to the code
2. **Be constructive** - Always explain the "why" behind feedback
3. **Provide examples** - Show what better code looks like
4. **Link to resources** - Reference docs, best practices, or examples
5. **Balance feedback** - Include positive comments, not just critiques
6. **Use appropriate severity** - 🚨 for blocking, 💡 for suggestions
7. **Be respectful** - Remember there's a person behind the code

## Emoji Guide

| Emoji | Meaning | Severity |
|-------|---------|----------|
| 🚨 | Critical/Blocking | High |
| 🔒 | Security Issue | High |
| 🐛 | Bug | High |
| ⚡ | Performance | Medium |
| 🧪 | Testing | Medium |
| 📊 | Data Quality | Medium |
| 🔍 | Code Quality | Medium |
| 📚 | Documentation | Low |
| 💡 | Suggestion | Low |
| ❓ | Question | - |
| ✅ | Positive | - |
| 📖 | Learning | - |

---

**Remember**: The best code reviews are collaborative, educational, and constructive. Use these templates as starting points, not rigid scripts.
