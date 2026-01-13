# Claude Code Team Workflows

## Overview

This guide provides production-ready workflows for teams using Claude Code across different development scenarios. These workflows leverage MCP servers, skills, and automation to maximize productivity.

## PR Review Workflow

### Setup

Configure GitHub MCP server in `settings.json`:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your-token"
      }
    }
  }
}
```

### Workflow Steps

#### 1. Daily PR Review Queue

**Morning Routine**:
```
Review my daily PR queue:
1. List all open PRs where I'm a requested reviewer
2. Prioritize by:
   - CI/CD status (failing first)
   - Age (oldest first)
   - Size (small PRs first)
3. For each PR, show:
   - Title and description
   - Files changed count
   - CI/CD status
   - Comments count
4. Create a prioritized review list
```

**Expected Output**:
- Sorted list of PRs requiring review
- Quick status overview
- Estimated review time for each

#### 2. Comprehensive PR Review

**Standard Review**:
```
Review PR #456 in myorg/myrepo:

1. Analysis Phase:
   - Get PR details (title, description, author)
   - Check CI/CD status
   - Get full diff
   - Identify changed files by type (code, tests, config, docs)

2. Code Quality Review:
   - Check for code style violations
   - Identify potential bugs
   - Look for security issues
   - Verify error handling
   - Check for code duplication

3. Architecture Review:
   - Verify design patterns are followed
   - Check for proper separation of concerns
   - Identify architectural smells
   - Verify consistency with codebase

4. Testing Review:
   - Verify test coverage for new code
   - Check test quality
   - Ensure edge cases are tested
   - Verify integration tests if needed

5. Documentation Review:
   - Check if README updated
   - Verify inline comments
   - Check API documentation
   - Verify changelog updated

6. Submit Review:
   - If issues found: REQUEST_CHANGES with detailed comments
   - If minor issues: APPROVE with suggestions
   - If perfect: APPROVE with positive feedback
```

**Review Template**:
```markdown
## Summary
[Brief overview of changes]

## Code Quality
- [ ] Code follows project style guidelines
- [ ] No obvious bugs or logic errors
- [ ] Proper error handling
- [ ] No security vulnerabilities

## Architecture
- [ ] Design is sound
- [ ] Follows existing patterns
- [ ] No architectural anti-patterns

## Testing
- [ ] Adequate test coverage
- [ ] Tests are meaningful
- [ ] Edge cases covered

## Documentation
- [ ] Code is well-commented
- [ ] Documentation updated
- [ ] Changelog updated

## Recommendations
[Specific suggestions for improvement]

## Action Items
[Required changes if any]
```

#### 3. Quick Review (for small changes)

```
Quick review PR #789 in myorg/myrepo:

1. Get PR overview
2. Check if changes are < 100 lines
3. Review changed files
4. Run basic checks:
   - No obvious bugs
   - Tests included
   - CI passing
5. Approve if everything looks good
```

#### 4. Security-Focused Review

```
Security review PR #123 in myorg/myrepo:

1. Identify security-sensitive changes:
   - Authentication/authorization
   - Database queries
   - File operations
   - Network requests
   - Cryptography
   - User input handling

2. For each security-sensitive area:
   - Check for SQL injection
   - Verify XSS prevention
   - Check CSRF protection
   - Verify input validation
   - Check for secrets in code
   - Verify proper encryption

3. Check dependencies:
   - New dependencies added
   - Known vulnerabilities
   - License compatibility

4. Submit detailed security review
```

#### 5. Performance Review

```
Performance review PR #234 in myorg/myrepo:

1. Identify performance-critical changes:
   - Database queries
   - API calls
   - Loops over large datasets
   - File I/O
   - Caching logic

2. For database changes:
   - Check for N+1 queries
   - Verify indexes used
   - Check query complexity
   - Verify pagination

3. For API calls:
   - Check for sequential calls (should be parallel)
   - Verify timeouts set
   - Check retry logic
   - Verify rate limiting

4. For algorithms:
   - Analyze time complexity
   - Check space complexity
   - Suggest optimizations

5. Provide performance recommendations
```

### Automation Tips

**Create PR Review Hook**:

Create `/hooks/pr-review.sh`:
```bash
#!/bin/bash
# Run automated checks before review

PR_NUMBER=$1
REPO=$2

echo "Running automated PR checks..."

# Check PR size
FILES_CHANGED=$(gh pr view $PR_NUMBER --repo $REPO --json files --jq '.files | length')
if [ $FILES_CHANGED -gt 50 ]; then
    echo "⚠️  Large PR: $FILES_CHANGED files changed"
fi

# Check CI status
CI_STATUS=$(gh pr view $PR_NUMBER --repo $REPO --json statusCheckRollup --jq '.statusCheckRollup[].conclusion')
if echo "$CI_STATUS" | grep -q "FAILURE"; then
    echo "❌ CI checks failing"
fi

# Check conflicts
MERGEABLE=$(gh pr view $PR_NUMBER --repo $REPO --json mergeable --jq '.mergeable')
if [ "$MERGEABLE" = "CONFLICTING" ]; then
    echo "⚠️  PR has merge conflicts"
fi
```

**Configure in settings.json**:
```json
{
  "hooks": {
    "beforeReview": "/hooks/pr-review.sh {pr_number} {repo}"
  }
}
```

## Incident Response Workflow

### Setup

Configure monitoring MCP servers:

```json
{
  "mcpServers": {
    "datadog": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-datadog"],
      "env": {
        "DD_API_KEY": "your-api-key",
        "DD_APP_KEY": "your-app-key"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your-token"
      }
    }
  }
}
```

### Workflow Steps

#### 1. Incident Detection

```
Check for active incidents:

1. DataDog:
   - List all monitors in "Alert" state
   - Get recent error logs (last 30 minutes)
   - Check for anomalies in key metrics

2. Application:
   - Check error rate (last 15 minutes)
   - Check request latency p95, p99
   - Check service health endpoints

3. If incident detected:
   - Categorize severity (P1/P2/P3)
   - Create incident summary
   - Proceed to investigation
```

#### 2. Incident Investigation

```
Investigate incident: High Error Rate on API

1. Gather Context:
   - Get error rate timeline (last 2 hours)
   - Get sample error logs (last 100)
   - Identify affected services
   - Check recent deployments
   - Check infrastructure changes

2. Analyze Errors:
   - Group errors by type
   - Identify error patterns
   - Find common stack traces
   - Check affected endpoints

3. Check Dependencies:
   - Database health and latency
   - External API availability
   - Redis/cache status
   - Message queue status

4. Timeline:
   - When did errors start?
   - What changed around that time?
   - Any correlating events?

5. Generate Investigation Report:
   - Root cause hypothesis
   - Evidence supporting hypothesis
   - Affected components
   - Recommended actions
```

#### 3. Incident Response

```
Respond to incident: Database Connection Pool Exhausted

1. Immediate Actions:
   - Assess impact (users affected, services down)
   - Notify stakeholders
   - Create incident channel

2. Mitigation:
   - Identify quick fixes
   - Scale resources if needed
   - Apply temporary workarounds
   - Monitor mitigation effectiveness

3. Fix Implementation:
   - Identify root cause fix
   - Create emergency branch
   - Implement fix
   - Test fix locally
   - Deploy to staging
   - Verify fix works

4. Deployment:
   - Create emergency PR
   - Fast-track review
   - Deploy to production
   - Monitor metrics

5. Verification:
   - Confirm error rate decreased
   - Verify latency normalized
   - Check affected services recovered
   - Monitor for 30 minutes
```

#### 4. Post-Incident Analysis

```
Post-incident analysis for: API Outage on 2024-01-15

1. Incident Summary:
   - What happened?
   - When did it happen?
   - How long did it last?
   - What was the impact?

2. Timeline:
   - Detailed chronology
   - When was it detected?
   - When was it mitigated?
   - When was it resolved?

3. Root Cause:
   - What was the root cause?
   - Why did it happen?
   - Why wasn't it caught earlier?

4. Resolution:
   - How was it fixed?
   - Who was involved?
   - What worked well?
   - What didn't work well?

5. Action Items:
   - Prevent recurrence
   - Improve detection
   - Improve response
   - Update runbooks
   - Improve monitoring
   - Update alerts

6. Create Post-Mortem Document:
   - Save to docs/post-mortems/
   - Share with team
   - Track action items
```

### Incident Response Checklist

```markdown
## Incident Response Checklist

### Detection (0-5 minutes)
- [ ] Incident confirmed
- [ ] Severity assessed
- [ ] Incident channel created
- [ ] On-call notified

### Investigation (5-15 minutes)
- [ ] Error logs collected
- [ ] Metrics analyzed
- [ ] Recent changes identified
- [ ] Dependencies checked
- [ ] Root cause hypothesis formed

### Mitigation (15-30 minutes)
- [ ] Quick fix identified
- [ ] Stakeholders notified
- [ ] Mitigation deployed
- [ ] Effectiveness verified

### Resolution (30-60 minutes)
- [ ] Permanent fix implemented
- [ ] Tests added
- [ ] PR created and reviewed
- [ ] Fix deployed
- [ ] Metrics confirmed normal

### Post-Incident (1-24 hours)
- [ ] Post-mortem scheduled
- [ ] Timeline documented
- [ ] Root cause documented
- [ ] Action items created
- [ ] Runbooks updated
```

## Feature Development Workflow

### Workflow Steps

#### 1. Feature Planning

```
Plan feature: User Authentication

1. Requirements Analysis:
   - Review feature requirements
   - Identify technical dependencies
   - Check existing related code
   - Identify potential conflicts

2. Architecture Design:
   - Design component structure
   - Define data models
   - Plan API endpoints
   - Identify integration points

3. Task Breakdown:
   - Break into subtasks
   - Estimate effort
   - Identify blockers
   - Create GitHub issues

4. Create Feature Branch:
   - Branch from main
   - Name: feature/user-authentication
```

#### 2. Implementation

```
Implement feature: User Authentication

1. Setup:
   - Create feature branch
   - Update dependencies
   - Setup test environment

2. Implement Core Logic:
   - Create auth models
   - Implement login/logout
   - Add session management
   - Implement password hashing

3. Add Tests:
   - Unit tests for auth logic
   - Integration tests for endpoints
   - Security tests
   - Edge case tests

4. Add Documentation:
   - Update API docs
   - Add code comments
   - Update README
   - Add usage examples

5. Local Testing:
   - Run all tests
   - Manual testing
   - Security review
   - Performance check
```

#### 3. Code Review Preparation

```
Prepare feature for review: User Authentication

1. Self-Review:
   - Review all changes
   - Check for debug code
   - Verify no secrets committed
   - Check code style

2. Pre-PR Checklist:
   - All tests passing
   - No linting errors
   - Documentation updated
   - Changelog updated
   - Branch up to date with main

3. Create PR:
   - Write detailed description
   - Link related issues
   - Add screenshots if UI changes
   - Request reviewers
   - Add labels
```

#### 4. Address Review Feedback

```
Address feedback on PR #456:

1. Review Comments:
   - Read all comments
   - Categorize (must-fix, suggestions, questions)
   - Prioritize changes

2. Make Changes:
   - Fix required issues
   - Implement suggestions if agreed
   - Answer questions
   - Update tests if needed

3. Update PR:
   - Push changes
   - Reply to comments
   - Re-request review if needed
```

## Code Migration Workflow

### Large-Scale Refactoring

```
Migrate from legacy API to new API:

1. Analysis Phase:
   - Find all usages of legacy API
   - Document current behavior
   - Identify edge cases
   - Plan migration strategy

2. Create Migration Plan:
   - Prioritize components
   - Define rollback strategy
   - Plan feature flags
   - Identify risks

3. Implement Migration:
   - Create abstraction layer
   - Migrate one component at a time
   - Add feature flags
   - Test thoroughly

4. Gradual Rollout:
   - Deploy with feature flag off
   - Enable for 1% traffic
   - Monitor metrics
   - Gradually increase to 100%
   - Remove old code

5. Cleanup:
   - Remove feature flags
   - Delete legacy code
   - Update documentation
```

### Database Migration

```
Migrate database schema:

1. Planning:
   - Design new schema
   - Plan data transformation
   - Identify dependencies
   - Plan downtime (if needed)

2. Create Migration:
   - Write migration scripts
   - Add rollback scripts
   - Test on staging
   - Backup production data

3. Execute Migration:
   - Take backup
   - Run migration
   - Verify data integrity
   - Test application

4. Rollback Plan:
   - Document rollback steps
   - Test rollback on staging
   - Keep ready during migration
```

## Documentation Workflow

### Workflow Steps

#### 1. API Documentation

```
Document API endpoints:

1. For each endpoint:
   - HTTP method and path
   - Description
   - Request parameters
   - Request body schema
   - Response schema
   - Error codes
   - Examples
   - Authentication requirements

2. Generate OpenAPI spec:
   - Create openapi.yaml
   - Validate spec
   - Generate interactive docs
   - Publish to docs site
```

#### 2. Code Documentation

```
Document codebase:

1. Module Documentation:
   - Purpose and responsibility
   - Public API
   - Usage examples
   - Dependencies

2. Function Documentation:
   - Purpose
   - Parameters
   - Return value
   - Exceptions
   - Examples

3. Generate Docs:
   - Run doc generator
   - Review output
   - Publish to doc site
```

#### 3. Runbook Creation

```
Create runbook for: Production Deployment

1. Prerequisites:
   - Required access
   - Tools needed
   - Pre-deployment checklist

2. Step-by-Step Guide:
   - Numbered steps
   - Commands to run
   - Expected output
   - Verification steps

3. Troubleshooting:
   - Common issues
   - How to diagnose
   - How to fix
   - When to escalate

4. Rollback Procedure:
   - When to rollback
   - How to rollback
   - Verification
   - Notification
```

## Testing Workflow

### Workflow Steps

#### 1. Test Planning

```
Plan tests for feature: User Authentication

1. Identify Test Scenarios:
   - Happy path
   - Edge cases
   - Error cases
   - Security scenarios
   - Performance scenarios

2. Define Test Levels:
   - Unit tests (business logic)
   - Integration tests (API endpoints)
   - E2E tests (user flows)
   - Security tests
   - Load tests

3. Setup Test Environment:
   - Test database
   - Mock external services
   - Test data
```

#### 2. Test Implementation

```
Implement tests for User Authentication:

1. Unit Tests:
   - Password hashing
   - Token generation
   - Session management
   - Input validation

2. Integration Tests:
   - POST /login
   - POST /logout
   - GET /profile (authenticated)
   - Token refresh

3. E2E Tests:
   - Complete login flow
   - Session persistence
   - Logout flow

4. Security Tests:
   - SQL injection attempts
   - XSS attempts
   - Brute force protection
   - Session hijacking

5. Run Tests:
   - Execute test suite
   - Check coverage
   - Fix failing tests
```

#### 3. Test Automation

```
Setup CI/CD testing:

1. Configure GitHub Actions:
   - Run tests on every PR
   - Run tests on push to main
   - Block merge if tests fail

2. Add Test Reports:
   - Coverage reports
   - Test results
   - Performance metrics

3. Setup Nightly Tests:
   - Full test suite
   - Load tests
   - Security scans
```

## Collaboration Patterns

### Pair Programming with Claude

```
Pair programming session: Implement payment processing

1. Planning:
   - Discuss approach with Claude
   - Design data structures
   - Identify edge cases

2. Implementation:
   - Claude writes initial code
   - Developer reviews and refines
   - Iterate until satisfied

3. Testing:
   - Claude generates tests
   - Developer adds scenarios
   - Run and verify

4. Review:
   - Discuss code quality
   - Identify improvements
   - Document decisions
```

### Code Review with Claude

```
Pre-review with Claude before requesting human review:

1. Self-Review:
   - Ask Claude to review changes
   - Get feedback on code quality
   - Identify potential issues

2. Fix Issues:
   - Address Claude's feedback
   - Improve code based on suggestions
   - Add missing tests

3. Request Human Review:
   - Code is higher quality
   - Fewer back-and-forth cycles
   - Faster approval
```

### Knowledge Transfer

```
Document tribal knowledge with Claude:

1. Identify undocumented areas
2. Interview team members (or extract from Slack/docs)
3. Claude structures knowledge
4. Create comprehensive docs
5. Review and publish
```

## Best Practices

### General Principles

1. **Consistency**: Use the same workflow across the team
2. **Automation**: Automate repetitive tasks
3. **Documentation**: Document everything
4. **Quality**: Never compromise on quality
5. **Communication**: Keep team informed

### Workflow Optimization

1. **Measure**: Track time spent on each workflow
2. **Identify Bottlenecks**: Find slow steps
3. **Optimize**: Improve or automate bottlenecks
4. **Iterate**: Continuously improve workflows

### Team Coordination

1. **Standup Integration**: Share Claude Code achievements
2. **Sprint Planning**: Use Claude for estimation
3. **Retrospectives**: Discuss workflow improvements
4. **Knowledge Sharing**: Document learnings

### Quality Gates

1. **PR Quality**:
   - All tests pass
   - No linting errors
   - Coverage maintained
   - Documentation updated

2. **Code Quality**:
   - Follows style guide
   - No code smells
   - Proper error handling
   - Security reviewed

3. **Deployment Quality**:
   - Staging tested
   - Rollback plan ready
   - Monitoring configured
   - Team notified

## Resources

- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Git Best Practices](https://www.git-tower.com/learn/git/ebook/en/command-line/appendix/best-practices)
- [Code Review Best Practices](https://google.github.io/eng-practices/review/)
- [Incident Response Best Practices](https://www.atlassian.com/incident-management/handbook/incident-response)
