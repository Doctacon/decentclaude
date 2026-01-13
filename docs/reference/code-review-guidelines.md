# Code Review Guidelines

> **Purpose**: Ensure code quality, knowledge sharing, and maintain project standards through effective code reviews.

## Table of Contents

- [Review Principles](#review-principles)
- [Reviewer Responsibilities](#reviewer-responsibilities)
- [Author Responsibilities](#author-responsibilities)
- [Review Process](#review-process)
- [What to Look For](#what-to-look-for)
- [Comment Templates](#comment-templates)
- [Review Checklists](#review-checklists)
- [Approval Criteria](#approval-criteria)
- [Handling Disagreements](#handling-disagreements)

## Review Principles

### 1. Be Kind and Respectful
- Critique code, not people
- Assume positive intent
- Use "we" language ("we could improve this by...")
- Provide specific, actionable feedback

### 2. Focus on Impact
- Prioritize correctness, security, and maintainability
- Consider the cost/benefit of requested changes
- Distinguish between required changes and suggestions

### 3. Share Knowledge
- Explain the "why" behind feedback
- Link to documentation or examples
- Use reviews as teaching opportunities

### 4. Be Timely
- Review PRs within 1 business day
- Break large reviews into multiple sessions if needed
- Communicate if you can't review in time

## Reviewer Responsibilities

### Before Reviewing
- [ ] Understand the PR's purpose and context
- [ ] Review the PR description and linked issues/beads
- [ ] Check that CI/validation hooks have passed
- [ ] Ensure the PR is ready for review (not draft)

### During Review
- [ ] Review the code thoroughly
- [ ] Test locally if changes are significant
- [ ] Leave clear, actionable comments
- [ ] Approve, request changes, or leave comments as appropriate

### After Review
- [ ] Re-review when author addresses feedback
- [ ] Approve once all concerns are addressed
- [ ] Thank the author for their work

## Author Responsibilities

### Before Requesting Review
- [ ] Self-review your own code
- [ ] Ensure all validation hooks pass
- [ ] Fill out the PR template completely
- [ ] Add appropriate labels
- [ ] Link to related beads/issues
- [ ] Choose appropriate reviewers

### During Review
- [ ] Respond to all comments
- [ ] Ask questions if feedback is unclear
- [ ] Make requested changes or explain why you disagree
- [ ] Mark conversations as resolved when addressed
- [ ] Request re-review when ready

### After Approval
- [ ] Ensure branch is up to date with base branch
- [ ] Squash commits if appropriate
- [ ] Merge the PR
- [ ] Delete the branch after merge

## Review Process

### 1. Initial Review
```
PR Created → Automated Checks → Reviewer Assigned → Review Started
```

### 2. Review Depth Levels

**Light Review** (documentation, minor fixes)
- Read through changes
- Check for obvious issues
- Verify documentation accuracy

**Standard Review** (most changes)
- Understand the context and purpose
- Review code logic and structure
- Check tests and documentation
- Verify error handling

**Deep Review** (critical changes, complex features)
- Pull code and test locally
- Review related code and dependencies
- Check performance implications
- Verify security considerations
- Review downstream impacts

### 3. Review Timeline

| PR Size | Expected Review Time |
|---------|---------------------|
| Small (<100 lines) | 30 minutes |
| Medium (100-500 lines) | 1-2 hours |
| Large (500-1000 lines) | Half day |
| Extra Large (>1000 lines) | Consider splitting |

## What to Look For

### 1. Correctness
- [ ] Logic is correct and handles edge cases
- [ ] No obvious bugs or errors
- [ ] Error handling is appropriate
- [ ] Tests cover the changes

### 2. Security
- [ ] No secrets or credentials committed
- [ ] Input validation for user-supplied data
- [ ] No SQL injection vulnerabilities
- [ ] Proper authentication and authorization
- [ ] No XSS vulnerabilities

### 3. Performance
- [ ] No unnecessary database queries
- [ ] Efficient algorithms and data structures
- [ ] Proper use of indexes and caching
- [ ] BigQuery queries optimized (for SQL changes)
- [ ] No N+1 query problems

### 4. Data Quality (for data changes)
- [ ] Schema changes are backward compatible
- [ ] Data quality tests added
- [ ] Null handling is appropriate
- [ ] Partitioning and clustering used correctly
- [ ] Cost implications considered

### 5. Code Quality
- [ ] Code follows project conventions
- [ ] Code is readable and maintainable
- [ ] No unnecessary complexity
- [ ] DRY principle followed (but not over-abstracted)
- [ ] Meaningful variable and function names

### 6. Testing
- [ ] Tests exist and are meaningful
- [ ] Tests cover edge cases
- [ ] Tests are maintainable
- [ ] No flaky tests

### 7. Documentation
- [ ] Code is self-documenting or has comments where needed
- [ ] Public APIs are documented
- [ ] README updated if needed
- [ ] Data models documented
- [ ] Breaking changes documented

### 8. Git Hygiene
- [ ] Commit messages are clear and descriptive
- [ ] No merge commits (unless intentional)
- [ ] No commits with fixes for previous commits in same PR
- [ ] Branch is up to date with base

## Comment Templates

### Requesting Changes

**Critical Issue (blocking)**
```
🚨 **Critical**: [description of issue]

This needs to be fixed because [reason].

Suggested fix: [specific recommendation]
```

**Bug or Logic Error**
```
🐛 **Bug**: [description]

Expected: [what should happen]
Actual: [what currently happens]

Suggestion: [how to fix]
```

**Security Concern**
```
🔒 **Security**: [description of vulnerability]

Risk: [potential impact]

Fix: [specific recommendation]
```

**Performance Issue**
```
⚡ **Performance**: [description]

Impact: [estimated performance impact]

Suggestion: [optimization approach]
```

### Suggestions

**Optional Improvement**
```
💡 **Suggestion** (optional): [improvement idea]

This would improve [aspect] but is not blocking.
```

**Best Practice**
```
📚 **Best Practice**: [observation]

Consider [alternative approach] because [reason].

Reference: [link to documentation]
```

**Code Clarity**
```
🔍 **Clarity**: This could be clearer

Consider renaming `x` to `userAccountId` to better convey intent.
```

### Positive Feedback

**Good Pattern**
```
✅ **Nice**: [what was done well]

This is a great example of [pattern/principle].
```

**Learning Moment**
```
📖 **TIL**: [something learned from this PR]

I didn't know about [concept], this is helpful!
```

## Review Checklists

### General Review Checklist

- [ ] PR description clearly explains the changes
- [ ] Changes align with the stated purpose
- [ ] All automated checks pass
- [ ] No unrelated changes included
- [ ] Tests are added/updated appropriately
- [ ] Documentation is updated
- [ ] No secrets or sensitive data committed
- [ ] Code follows project conventions

### Data Model Review Checklist

- [ ] SQL syntax is valid
- [ ] BigQuery dry run successful
- [ ] Query cost is acceptable
- [ ] Schema changes are backward compatible (or migration plan exists)
- [ ] Data quality tests added
- [ ] Partitioning and clustering appropriate
- [ ] Downstream impacts identified and addressed
- [ ] Data model documentation updated
- [ ] Example queries provided and tested

### Pipeline Review Checklist

- [ ] Error handling is comprehensive
- [ ] Retry logic is appropriate
- [ ] Monitoring and alerting configured
- [ ] Idempotency considered
- [ ] Resource usage is reasonable
- [ ] Deployment plan is clear
- [ ] Rollback plan is documented
- [ ] Pipeline runbook created/updated
- [ ] Failure scenarios tested

### Python Code Review Checklist

- [ ] Type hints used appropriately
- [ ] Error handling is appropriate
- [ ] Logging is helpful and not excessive
- [ ] Dependencies are minimized
- [ ] Code is testable
- [ ] Tests are comprehensive
- [ ] No obvious performance issues
- [ ] Security best practices followed

## Approval Criteria

### When to Approve

Approve when:
- All blocking issues are resolved
- Code meets quality standards
- Tests are adequate
- Documentation is complete
- You're confident this won't cause problems

### When to Request Changes

Request changes when:
- Critical bugs exist
- Security vulnerabilities present
- Tests are missing or inadequate
- Breaking changes lack migration plan
- Code doesn't follow project standards

### When to Comment (without approval)

Comment without approval when:
- You have questions or suggestions
- You want to share knowledge
- Changes are optional improvements
- You're not the primary reviewer

## Handling Disagreements

### If You Disagree as a Reviewer

1. **Explain your reasoning** - Share why you believe a change is needed
2. **Provide examples** - Link to similar code or documentation
3. **Ask questions** - Seek to understand the author's perspective
4. **Escalate if needed** - Involve a senior engineer or architect

### If You Disagree as an Author

1. **Understand the feedback** - Ask clarifying questions
2. **Explain your approach** - Share your reasoning
3. **Be open to change** - Consider that feedback might be valid
4. **Propose alternatives** - Suggest different solutions
5. **Escalate if needed** - Involve a neutral third party

### Resolution Process

1. Discussion in PR comments
2. Synchronous discussion (call/chat) if comments aren't resolving it
3. Escalation to tech lead or architect
4. Document decision and reasoning

## Review Response Times

| Priority | Expected Response Time |
|----------|----------------------|
| Critical (P0) | Within 2 hours |
| High (P1) | Same day |
| Normal (P2) | Within 1 business day |
| Low (P3) | Within 2 business days |

## Review Metrics (Optional)

Track these metrics to improve review process:

- Time to first review
- Number of review cycles
- Time from PR creation to merge
- Number of comments per PR
- Issues found in review vs production

## Additional Resources

- [Best Practices Documentation](data-engineering-patterns.md)
- [Testing Patterns](data-testing-patterns.md)
- [Playbooks](playbooks.md)
- [Build Documentation Standards](BUILD.md)

## Review Anti-Patterns to Avoid

### As a Reviewer
- ❌ Nitpicking formatting (use automated tools)
- ❌ Requesting changes without explanation
- ❌ Reviewing code you don't understand
- ❌ Asking for rewrites of working code
- ❌ Being dismissive or condescending

### As an Author
- ❌ Taking feedback personally
- ❌ Arguing about every comment
- ❌ Ignoring feedback without discussion
- ❌ Requesting review before self-review
- ❌ Creating PRs that are too large

## Gas Town Specific Considerations

### Multi-Agent Environment
- PRs may be created by autonomous agents (polecats)
- Review with the same rigor as human-authored code
- Agent-generated code should follow same standards
- Use beads system for tracking related work

### Worktree Management
- Be aware of multi-worktree architecture
- Check for branch conflicts across worktrees
- Review git hooks are properly configured
- Consider impact on other active worktrees

### Claude Code Integration
- Validation hooks provide first-line checks
- Don't rely solely on hooks for review
- Hooks check syntax, not logic or design
- Manual review is still essential

---

**Remember**: The goal of code review is to improve code quality, share knowledge, and maintain project standards. Be thorough, be kind, and be constructive.
