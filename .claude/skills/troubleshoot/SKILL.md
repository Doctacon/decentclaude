---
name: troubleshoot
description: Systematic debugging workflow for reproducing issues, gathering context, forming hypotheses, and iterating to resolution
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Edit
  - Write
---

# Troubleshoot Skill

Systematic debugging workflow that guides you through reproducing issues, gathering context, forming hypotheses, testing them, and iterating to resolution.

## Workflow

### 1. Reproduce the Issue

- **Gather initial report**: What's the error? When does it happen? Steps to reproduce?
- **Attempt reproduction**: Try to reproduce the issue yourself
- **Document conditions**: Note environment, input data, configuration that triggers the issue
- **Verify consistency**: Can you reproduce it reliably?

### 2. Gather Context

- **Error messages**: Collect full stack traces and error logs
- **System logs**: Check application logs, system logs, service logs
- **Recent changes**: Review git history for recent commits that might be related
  ```bash
  git log --oneline --since="7 days ago" -- <affected-files>
  ```
- **Configuration**: Check relevant config files, environment variables
- **Dependencies**: Verify versions of relevant libraries and services
- **System state**: Check resource usage (CPU, memory, disk, network)

### 3. Form Hypothesis

- **Analyze symptoms**: What are the observable behaviors?
- **Identify suspects**: Based on stack traces and logs, what components are involved?
- **Consider causes**: What could cause this behavior?
  - Logic errors
  - Race conditions
  - Resource exhaustion
  - External service failures
  - Configuration issues
  - Data quality issues
- **Prioritize**: Rank hypotheses by likelihood

### 4. Test Hypothesis

- **Design test**: How can you verify or disprove this hypothesis?
- **Add instrumentation**: Add logging, debugging statements, or breakpoints
- **Run test**: Execute and observe results
- **Collect evidence**: Document what you learned

### 5. Iterate

- **Hypothesis confirmed?**
  - Yes: Proceed to implement fix
  - No: Return to step 3 with new information
- **Keep notes**: Document what you've tried and learned
- **Avoid rabbit holes**: Set time limits for each hypothesis test
- **Ask for help**: If stuck, prepare a clear summary of what you've tried

### 6. Implement Fix

- **Make minimal change**: Fix the root cause, not just symptoms
- **Add tests**: Create test case that reproduces the original issue
- **Verify fix**: Confirm the issue is resolved
- **Check for side effects**: Ensure fix doesn't break other functionality
- **Update documentation**: Document the issue and fix if needed

### 7. Generate Report

Create a debugging report with:
- **Issue description**: What was the problem?
- **Root cause**: What caused it?
- **Investigation steps**: What did you try?
- **Solution**: How was it fixed?
- **Prevention**: How to avoid this in the future?

## Integration Points

- **Error tracking**: Check Sentry, Rollbar, or similar services for error context
- **Logs**: Use centralized logging (e.g., CloudWatch, Datadog, ELK stack)
- **Git history**: Use `git log`, `git blame`, `git bisect` to identify when issue was introduced
- **Monitoring**: Check metrics and dashboards for anomalies
- **Incident response**: If this is a production incident, coordinate with incident-response utilities

## Tips

- **Divide and conquer**: Isolate the problem to the smallest possible scope
- **Scientific method**: Treat debugging as experimentation
- **One change at a time**: Don't make multiple changes simultaneously
- **Take breaks**: Fresh perspective often helps
- **Document everything**: Your future self will thank you
- **Check the obvious**: Sometimes it's a typo or config error
- **Rubber duck**: Explaining the problem often reveals the solution

## Example Usage

```
User: "The API is returning 500 errors intermittently"

1. Reproduce: Call the API endpoint multiple times, observe pattern
2. Gather context:
   - Check API logs for stack traces
   - Review recent deployments
   - Check database connection pool status
3. Form hypothesis: "Database connection pool exhaustion"
4. Test: Add logging for pool metrics, monitor during load
5. Iterate: If confirmed, increase pool size or fix connection leaks
6. Fix: Update connection pool configuration, add connection leak detection
7. Report: Document root cause and prevention measures
```

## Best Practices

- Start with what changed recently
- Check logs before assuming code issues
- Verify assumptions (e.g., "this should never be null")
- Use binary search to narrow down problem location
- Leverage git bisect for regressions
- Don't guess randomly; form testable hypotheses
- Keep a debugging journal for complex issues
