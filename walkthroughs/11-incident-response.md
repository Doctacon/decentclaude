# Walkthrough: Responding to an Incident

## Overview

This walkthrough provides a structured approach to handling production data incidents, from initial triage through resolution and post-mortem.

## Prerequisites

- Access to production systems
- Understanding of your data pipelines
- Familiarity with monitoring tools
- Authority to make production changes (if needed)

## Time Estimate

Varies (15 minutes to several hours depending on severity)

## Incident Severity Levels

Before starting, classify the incident:

- **P0 (Critical)**: Data loss, security breach, complete outage
- **P1 (High)**: Incorrect data affecting decisions, partial outage
- **P2 (Medium)**: Delayed data, degraded performance
- **P3 (Low)**: Minor issues, cosmetic problems

## Steps

### Phase 1: Initial Response (First 5 minutes)

#### 1. Acknowledge the Incident

```bash
# Log the incident
echo "Incident detected at $(date)" > incident_$(date +%Y%m%d_%H%M%S).log

# Set incident start time
INCIDENT_START=$(date +%s)
```

#### 2. Quick Assessment

Answer these questions:

- **What's broken?** (specific table, dashboard, pipeline)
- **When did it break?** (timestamp)
- **Who's affected?** (users, teams, systems)
- **What's the impact?** (business decisions, reports, downstream systems)

Document answers:
```bash
cat >> incident_*.log << EOF
What: [Description]
When: [Timestamp]
Who: [Affected parties]
Impact: [Business impact]
EOF
```

#### 3. Notify Stakeholders

For P0/P1, immediately notify:
- Your team lead
- Affected teams
- On-call engineer

```bash
# Example notification
# Adapt to your communication tool
slack_notify "🚨 P1 Incident: [Brief description]. Investigating."
```

### Phase 2: Investigation (15-30 minutes)

#### 4. Check Recent Changes

```bash
# What was deployed recently?
git log --oneline --since="24 hours ago"

# Check dbt run history (if using dbt Cloud)
# or local run logs

# Check Airflow/Composer DAG runs
# gcloud composer environments run ENV_NAME list_dags
```

#### 5. Examine the Data

```bash
# Check row counts
bq query --use_legacy_sql=false "
  SELECT COUNT(*) as current_count
  FROM \`project.dataset.affected_table\`
  WHERE _PARTITIONDATE = CURRENT_DATE()
"

# Compare to historical
bq query --use_legacy_sql=false "
  SELECT
    _PARTITIONDATE as date,
    COUNT(*) as row_count
  FROM \`project.dataset.affected_table\`
  WHERE _PARTITIONDATE >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
  GROUP BY 1
  ORDER BY 1 DESC
"

# Check for nulls in critical columns
bq query --use_legacy_sql=false "
  SELECT
    COUNTIF(critical_column IS NULL) as null_count,
    COUNT(*) as total_count
  FROM \`project.dataset.affected_table\`
  WHERE _PARTITIONDATE = CURRENT_DATE()
"
```

#### 6. Check Dependencies

```bash
# View upstream tables
bin/data-utils/bq-lineage project.dataset.affected_table

# Check if upstream data is healthy
# Verify source data quality
```

#### 7. Review Logs

```bash
# dbt logs
cat logs/dbt.log | grep ERROR

# BigQuery job errors
bq ls -j --max_results=20 | grep FAILED

# Airflow task logs (if applicable)
```

### Phase 3: Containment (Immediate)

#### 8. Stop the Bleeding

Depending on the issue:

**Option A: Revert recent changes**
```bash
# Revert the problematic commit
git revert <commit-hash>
git push

# Re-run the pipeline
dbt run --select model_name
```

**Option B: Pause affected pipelines**
```bash
# Stop Airflow DAG (if applicable)
# airflow dags pause dag_id

# Or pause dbt Cloud job
```

**Option C: Use last known good data**
```bash
# Point downstream to previous day's partition
# Update views/dependencies temporarily
```

#### 9. Isolate the Problem

```bash
# Test the fix in development first
dbt run --select model_name --target dev

# Validate the fix
dbt test --select model_name --target dev

# Check data quality
python scripts/checks/validate_model.py
```

### Phase 4: Resolution

#### 10. Implement the Fix

```bash
# For code issues
git add fixed_files
git commit -m "Fix: [Brief description of fix]

Root cause: [What caused the issue]
Solution: [What was changed]
Tested: [How it was validated]

Resolves incident: incident_$(date +%Y%m%d)"

git push
```

#### 11. Backfill if Needed

```bash
# Backfill affected dates
dbt run --select model_name --vars '{"start_date": "2024-01-01", "end_date": "2024-01-05"}'

# Or use BigQuery to backfill
bq query --use_legacy_sql=false < backfill_query.sql
```

#### 12. Verify Resolution

```bash
# Run comprehensive tests
dbt test --select model_name+

# Data quality checks
python scripts/run_all_quality_checks.sh

# Spot check the data
bq query --use_legacy_sql=false "
  SELECT * FROM \`project.dataset.affected_table\`
  WHERE _PARTITIONDATE = CURRENT_DATE()
  LIMIT 100
"
```

### Phase 5: Communication

#### 13. Update Stakeholders

```bash
# Calculate incident duration
INCIDENT_END=$(date +%s)
DURATION=$(( ($INCIDENT_END - $INCIDENT_START) / 60 ))

# Send resolution notice
slack_notify "✅ Incident resolved. Duration: ${DURATION} minutes.
Root cause: [Brief explanation]
Status: All systems operational"
```

#### 14. Document the Incident

Create an incident report:

```bash
cat > incident_report_$(date +%Y%m%d).md << EOF
# Incident Report: [Title]

**Date**: $(date)
**Severity**: P[0-3]
**Duration**: ${DURATION} minutes
**Responder**: [Your name]

## Summary
[One paragraph summary]

## Timeline
- [HH:MM] Incident detected
- [HH:MM] Investigation began
- [HH:MM] Root cause identified
- [HH:MM] Fix implemented
- [HH:MM] Verified resolved

## Root Cause
[Detailed explanation of what caused the issue]

## Impact
- Affected tables: [list]
- Affected users: [list]
- Business impact: [description]

## Resolution
[What was done to fix it]

## Prevention
[How to prevent this in the future]

## Action Items
- [ ] Add monitoring for [specific metric]
- [ ] Improve test coverage for [area]
- [ ] Update documentation for [process]
- [ ] Conduct post-mortem meeting

## Lessons Learned
[Key takeaways]
EOF
```

### Phase 6: Post-Mortem (Within 48 hours)

#### 15. Schedule Post-Mortem

Organize a blameless post-mortem:

**Attendees**:
- Incident responder
- Affected teams
- System owners

**Agenda**:
1. Timeline review
2. Root cause analysis
3. What went well
4. What could be improved
5. Action items

#### 16. Implement Preventive Measures

Based on the post-mortem:

```bash
# Add monitoring
# Create alert for similar issues

# Improve tests
cat > tests/regression/test_incident_$(date +%Y%m%d).sql << EOF
-- Regression test to prevent recurrence of incident
SELECT ...
FROM {{ ref('affected_model') }}
WHERE [condition that should never happen again]
EOF

# Update documentation
# Add to playbooks/troubleshooting guides
```

## Validation

Confirm the incident is fully resolved:

- [ ] Data is correct
- [ ] All tests passing
- [ ] Downstream systems healthy
- [ ] Stakeholders notified
- [ ] Incident documented
- [ ] Prevention measures identified

## Common Incident Patterns

### Pattern: Data Freshness Issue

**Symptoms**: Data not updating, stale timestamps

**Investigation**:
```bash
# Check when data was last updated
bq query --use_legacy_sql=false "
  SELECT MAX(updated_at) as last_update
  FROM \`project.dataset.table\`
"

# Check pipeline runs
# Review scheduler logs
```

**Resolution**: Fix pipeline scheduling or source data delays

### Pattern: Schema Change Breaking Pipeline

**Symptoms**: Pipeline failures, missing columns

**Investigation**:
```bash
# Compare schemas
bin/data-utils/bq-schema-diff \
  project.dataset.table@YESTERDAY \
  project.dataset.table@TODAY
```

**Resolution**: Update models to handle schema changes

### Pattern: Data Quality Degradation

**Symptoms**: Tests failing, anomalous values

**Investigation**:
```bash
# Run data quality checks
python scripts/data_quality.py

# Check for anomalies
bq query --use_legacy_sql=false "
  SELECT
    column_name,
    COUNT(DISTINCT column_name) as distinct_values,
    COUNTIF(column_name IS NULL) as null_count
  FROM \`project.dataset.table\`
  WHERE _PARTITIONDATE = CURRENT_DATE()
"
```

**Resolution**: Fix data quality at source or add validation

## Troubleshooting

### Can't identify root cause?

Use the "5 Whys" technique:
1. Why did the data fail? → Tests failed
2. Why did tests fail? → Null values appeared
3. Why did nulls appear? → Source data changed
4. Why did source data change? → Upstream team deployed
5. Why weren't we notified? → No communication process

### Fix isn't working?

- Double-check you're testing the right thing
- Verify the fix is actually deployed
- Check if there are multiple issues
- Consider rolling back and re-assessing

### Incident keeps recurring?

- Root cause analysis incomplete
- Prevention measures not implemented
- Similar issues in other areas
- Need broader architectural fix

## Best Practices Checklist

- [ ] Incident classified by severity
- [ ] Stakeholders notified promptly
- [ ] Investigation systematic and documented
- [ ] Fix tested before production deploy
- [ ] Impact fully assessed
- [ ] Comprehensive incident report created
- [ ] Post-mortem scheduled
- [ ] Prevention measures implemented

## Related Resources

- [Playbooks - Incident Response Procedures](../playbooks.md#incident-response)
- [Troubleshooting Guide](../docs/templates/troubleshooting-guide.md)
- [Data Quality Checks](06-custom-quality-checks.md)

## Emergency Contacts

```bash
# Add your team's contacts
Team Lead: [contact]
On-call Engineer: [contact]
DevOps: [contact]
```
