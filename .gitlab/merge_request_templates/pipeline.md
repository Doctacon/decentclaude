## Pipeline/Workflow Changes

<!-- What pipeline or workflow is being added or modified? -->

## Purpose

<!-- What is the business purpose of this pipeline? -->

## Pipeline Details

### Type
- [ ] Data ingestion
- [ ] Transformation pipeline
- [ ] Export/sync pipeline
- [ ] Orchestration workflow
- [ ] Scheduled job
- [ ] Event-driven pipeline

### Components
<!-- List the key components -->
- **Source(s)**:
- **Destination(s)**:
- **Transformations**:
- **Dependencies**:

### Schedule/Trigger
<!-- When does this pipeline run? -->
- **Schedule**: (e.g., daily at 2 AM, hourly, etc.)
- **Trigger**: (e.g., file arrival, API event, manual)
- **Timeout**: Expected runtime and timeout settings

## Changes Made

<!-- List the specific changes -->
-
-
-

## Data Flow

<!-- Describe the data flow through the pipeline -->
1.
2.
3.

## Error Handling

- [ ] Retry logic implemented
- [ ] Error notifications configured
- [ ] Dead letter queue/error handling
- [ ] Circuit breaker pattern (if applicable)
- [ ] Graceful degradation strategy

### Failure Scenarios
<!-- How does the pipeline handle failures? -->
-
-

## Monitoring & Observability

- [ ] Logging implemented
- [ ] Metrics/monitoring configured
- [ ] Alerting rules defined
- [ ] SLOs/SLAs defined
- [ ] Dashboard created/updated

### Key Metrics
<!-- What metrics will be tracked? -->
-
-

## Testing

- [ ] Unit tests for individual components
- [ ] Integration tests for full pipeline
- [ ] Dry run completed successfully
- [ ] Tested with sample data
- [ ] Tested failure scenarios
- [ ] Performance tested with expected load

### Test Results
<!-- Summarize test results -->
-

## Performance & Cost

- [ ] Resource requirements estimated
- [ ] Cost impact assessed
- [ ] Performance optimizations applied
- [ ] Scaling strategy defined

### Estimates
- **Expected runtime**:
- **Resource usage** (CPU/memory):
- **Cost estimate** (if applicable):
- **Data volume processed**:

## Impact Assessment

- [ ] Dependencies identified
- [ ] Downstream systems notified
- [ ] Breaking changes: Yes/No
- [ ] Requires coordination with other teams

### Dependencies
<!-- List upstream and downstream dependencies -->
- **Upstream**:
- **Downstream**:

## Documentation

- [ ] Pipeline runbook created/updated (use `pipeline-runbook.md` template)
- [ ] Troubleshooting guide updated
- [ ] Architecture diagram created/updated
- [ ] Playbook updated with operational procedures
- [ ] CLAUDE.md updated with new patterns

## Deployment Plan

### Prerequisites
<!-- What needs to be in place before deployment? -->
-
-

### Deployment Steps
1.
2.
3.

### Validation Steps
<!-- How to verify successful deployment -->
1.
2.

### Rollback Plan
<!-- How to rollback if needed -->
-

## Operational Readiness

- [ ] Runbook complete and tested
- [ ] On-call team trained
- [ ] Monitoring and alerting verified
- [ ] Incident response plan documented
- [ ] Backup and recovery tested

## Checklist

- [ ] Follows pipeline best practices (see `playbooks.md`)
- [ ] All validation hooks pass
- [ ] No secrets or sensitive data committed
- [ ] Reviewed own code before requesting review
- [ ] Idempotency verified
- [ ] Proper error handling and logging
- [ ] Configuration externalized (no hardcoded values)

## Related Work

<!-- Link to related beads, pipelines, or design docs -->
- Related bead:
- Related pipelines:
- Design doc:

## Additional Context

<!-- Pipeline diagrams, example outputs, logs, etc. -->
