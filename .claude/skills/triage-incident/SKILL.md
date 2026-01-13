---
name: triage-incident
description: Incident response workflow for assessing severity, gathering symptoms, identifying impacted systems, forming hypotheses, testing fixes, and documenting timeline
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# Triage Incident Skill

Incident response workflow that guides you through assessing severity, gathering symptoms, identifying impacted systems, forming and testing hypotheses, implementing mitigations, and documenting the timeline.

## Workflow

### 1. Initial Assessment (0-5 minutes)

**Declare the incident**:
```bash
# Create incident channel
# Slack: /incident declare "Brief description"
# Or manually: #incident-YYYYMMDD-description

# Alert on-call
# PagerDuty, Opsgenie, or manual page
```

**Determine severity**:

**SEV1 - Critical**:
- Complete service outage
- Data loss or corruption
- Security breach
- Significant revenue impact
- Customer data exposed

**SEV2 - High**:
- Major feature degradation
- Significant user impact
- Intermittent outages
- Performance severely degraded

**SEV3 - Medium**:
- Minor feature issue
- Limited user impact
- Workaround available
- Non-critical service down

**SEV4 - Low**:
- Cosmetic issue
- Minimal user impact
- Enhancement request

**Initial notification template**:
```
SEV1: [Service] is down
Detected: 2024-01-15 10:30 UTC
Impact: All users unable to login
Investigating: @oncall-engineer
Status page: Updated
Channel: #incident-20240115-login-down
```

### 2. Gather Symptoms (5-15 minutes)

**What is broken?**
- Which service/feature is affected?
- What error messages are users seeing?
- When did it start?

**How many users affected?**
```bash
# Check error rates
curl "https://api.datadog.com/api/v1/query?query=sum:errors.count{*}" -H "DD-API-KEY: $DD_API_KEY"

# Check active users
SELECT COUNT(DISTINCT user_id) FROM sessions WHERE last_active > NOW() - INTERVAL '5 minutes';

# Check support tickets
# Check status page reports
```

**Is data at risk?**
- Data integrity intact?
- Backups available?
- Data exposure possible?

**System health check**:
```bash
# Service status
kubectl get pods -n production
systemctl status myapp

# Resource usage
top
df -h
free -m

# Network
netstat -an | grep LISTEN
curl https://api.example.com/health

# Database
psql -c "SELECT COUNT(*) FROM pg_stat_activity;"
SHOW PROCESSLIST;

# Logs
tail -f /var/log/app/error.log
kubectl logs -f deployment/myapp --tail=100
journalctl -u myapp -f

# Recent deployments
kubectl rollout history deployment/myapp
git log --oneline --since="2 hours ago"
```

### 3. Identify Impact (Concurrent with #2)

**Update status page**:
```
We are investigating reports of login failures.
We will provide an update within 15 minutes.
```

**Notify stakeholders**:
- Post in #incidents channel
- Email to stakeholders@company.com
- Update internal dashboard

**Document timeline**:
```
10:30 - First alert received
10:32 - SEV1 declared
10:33 - Status page updated
10:35 - Gathering symptoms
```

### 4. Form Hypothesis (10-20 minutes)

Based on symptoms, consider:

**Recent changes**:
```bash
# Recent deployments
git log --oneline --since="4 hours ago"

# Recent config changes
kubectl diff -f k8s/

# Recent database migrations
./manage.py showmigrations

# Recent infrastructure changes
terraform plan
```

**Common failure patterns**:

**Database issues**:
- Connection pool exhaustion
- Long-running queries
- Replication lag
- Disk space full

**Application issues**:
- Memory leak (OOM)
- Deadlock
- Exception in critical path
- External API failure

**Infrastructure issues**:
- Pod/instance crash
- Network partition
- DNS resolution failure
- SSL certificate expired

**External dependencies**:
- Third-party API down
- Payment processor issue
- CDN failure

**Check monitoring dashboards**:
```bash
# Open Grafana/Datadog dashboards
# Look for:
# - Error rate spikes
# - Latency increases
# - Resource exhaustion
# - Traffic anomalies
```

### 5. Test Hypothesis (15-30 minutes)

**Prioritize recovery over diagnosis**:
- Focus on mitigation first
- Root cause analysis can happen later
- Don't make it worse

**Test hypotheses from most to least likely**:

#### Hypothesis: Recent deployment caused issue

**Test**:
```bash
# Check deployment timing
kubectl rollout history deployment/myapp

# Compare error rate before/after deployment
# (in monitoring dashboard)
```

**Mitigate**:
```bash
# Rollback to previous version
kubectl rollout undo deployment/myapp

# Verify rollback
kubectl rollout status deployment/myapp

# Monitor error rates
```

#### Hypothesis: Database connection pool exhausted

**Test**:
```bash
# Check active connections
psql -c "SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active';"

# Check max connections
psql -c "SHOW max_connections;"
```

**Mitigate**:
```bash
# Quick fix: Restart app to reset connections
kubectl rollout restart deployment/myapp

# Or increase pool size
kubectl set env deployment/myapp DB_POOL_SIZE=50

# Long-term: Fix connection leaks
```

#### Hypothesis: Memory leak causing OOM

**Test**:
```bash
# Check memory usage
kubectl top pods
free -h
```

**Mitigate**:
```bash
# Restart pods with OOM
kubectl delete pod <pod-name>

# Scale horizontally
kubectl scale deployment myapp --replicas=5

# Add memory limits
kubectl set resources deployment myapp --limits=memory=2Gi
```

#### Hypothesis: External API down

**Test**:
```bash
# Check API health
curl https://api.external.com/health
curl https://status.external.com

# Check logs for API errors
grep "api.external.com" /var/log/app/error.log
```

**Mitigate**:
```bash
# Enable circuit breaker
# Switch to degraded mode
# Use cached data
# Show maintenance message
```

### 6. Implement Mitigation (20-45 minutes)

**Common mitigation strategies**:

**Rollback**:
```bash
# Application rollback
kubectl rollout undo deployment/myapp
git revert <commit-hash> && git push

# Database migration rollback
./manage.py migrate app 0042_previous_migration

# Infrastructure rollback
terraform apply -target=resource.name
```

**Horizontal scaling**:
```bash
# Scale up
kubectl scale deployment myapp --replicas=10
aws autoscaling set-desired-capacity --auto-scaling-group-name myapp --desired-capacity 10
```

**Restart services**:
```bash
kubectl rollout restart deployment/myapp
systemctl restart myapp
sudo service myapp restart
```

**Enable maintenance mode**:
```bash
# Put up maintenance page
kubectl apply -f k8s/maintenance-mode.yaml

# Redirect traffic
# Update load balancer rules
```

**Database fixes**:
```bash
# Kill long-running queries
SELECT pg_cancel_backend(pid) FROM pg_stat_activity WHERE state = 'active' AND query_start < NOW() - INTERVAL '5 minutes';

# Clear cache
FLUSHDB  # Redis

# Optimize slow query
CREATE INDEX idx_user_email ON users(email);
```

**Feature flag**:
```bash
# Disable problematic feature
curl -X POST https://api.example.com/flags/new-feature -d '{"enabled": false}'
```

### 7. Verify Mitigation (45-60 minutes)

**Check metrics**:
```bash
# Error rate returned to normal?
# Latency back to baseline?
# User reports stopped?
# Support ticket rate decreased?
```

**Test key user flows**:
```bash
# Login
curl -X POST https://api.example.com/auth/login -d '{"email":"test@example.com","password":"test"}'

# Critical transactions
# Run smoke tests
./run-smoke-tests.sh
```

**Update stakeholders**:
```
Issue has been mitigated. Services are operational.
We are monitoring closely.
Post-mortem will follow within 48 hours.
```

**Update status page**:
```
Resolved: Login issues have been fixed.
All services are operational.
```

### 8. Monitor and Stabilize (60+ minutes)

**Continue monitoring**:
- Watch dashboards for 30-60 minutes
- Ensure issue doesn't recur
- Be ready to re-engage

**Close incident**:
```
INCIDENT RESOLVED
SEV1: Login service down
Duration: 45 minutes
Impact: All users unable to login
Root cause: Database connection pool exhaustion
Mitigation: Increased pool size, restarted app servers
Status: Monitoring for 1 hour before full closure
```

**Begin post-mortem**:
- Schedule post-mortem meeting within 48 hours
- Assign action items
- Document lessons learned

### 9. Document Timeline

**Incident timeline template**:

```markdown
# Incident Post-Mortem: Login Service Outage

**Date**: 2024-01-15
**Severity**: SEV1
**Duration**: 45 minutes (10:30-11:15 UTC)
**Impact**: 100% of users unable to login

## Timeline

**10:30** - First alert: High error rate on /auth/login
**10:32** - SEV1 declared by @oncall-engineer
**10:33** - Incident channel created: #incident-20240115-login
**10:35** - Status page updated
**10:40** - Initial investigation: Recent deployment suspected
**10:45** - Rollback attempted, no improvement
**10:50** - Database investigation: Connection pool at 100%
**10:55** - Hypothesis: Connection pool exhaustion
**11:00** - Mitigation: Increased pool size from 20 to 50
**11:02** - Restarted application servers
**11:05** - Error rate dropping
**11:10** - Services fully operational
**11:15** - Incident resolved, monitoring continues

## Impact

- **Users affected**: ~10,000 (100% of active users)
- **Duration**: 45 minutes
- **Revenue impact**: Estimated $5,000 in lost transactions
- **Support tickets**: 47 tickets filed

## Root Cause

Database connection pool was configured for 20 connections.
A sudden spike in traffic (2x normal) exhausted the pool.
Requests waiting for connections timed out, causing login failures.

## Contributing Factors

1. Connection pool too small for peak traffic
2. No connection timeout or retry logic
3. Monitoring didn't alert on pool saturation
4. Load testing hadn't simulated this traffic level

## Mitigation

**Immediate**:
- Increased connection pool to 50
- Restarted app servers to reset connections

**Temporary**:
- Monitoring pool usage every 5 minutes

## Resolution

**Permanent fixes**:
1. Set connection pool to 100 (accommodates 3x traffic)
2. Add connection timeout and retry logic
3. Add alert on pool saturation >80%
4. Implement connection leak detection
5. Add load testing for 3x traffic scenarios

## Action Items

- [ ] @dev-team: Implement connection pooling improvements (Due: 2024-01-20)
- [ ] @devops: Add pool saturation alerts (Due: 2024-01-17)
- [ ] @qa: Update load testing scenarios (Due: 2024-01-22)
- [ ] @oncall: Update incident runbook with this scenario (Due: 2024-01-18)

## Lessons Learned

**What went well**:
- Quick detection (2 minutes)
- Clear communication in incident channel
- Effective hypothesis testing
- Fast mitigation once cause identified

**What could be improved**:
- Earlier identification of DB as issue (spent 15 min on rollback)
- Better monitoring of DB metrics
- Load testing should have caught this
- Connection pool should have been sized better initially

## Prevention

- Implement auto-scaling for connection pools
- Add comprehensive DB monitoring
- Regular capacity planning reviews
- Improve load testing coverage
```

## Incident Response Best Practices

### Communication

- **Frequent updates**: Every 15-30 minutes during active incident
- **Clear status**: What's broken, what we're doing, when next update
- **Single source of truth**: Use incident channel, not DMs
- **External communication**: Update status page, notify customers

### Team Coordination

- **Incident Commander**: One person coordinates
- **Roles**: Assign investigation, communication, mitigation leads
- **No heroes**: Don't work alone, collaborate
- **Shift changes**: If incident >4 hours, rotate responders

### Decision Making

- **Bias to action**: Make informed decisions quickly
- **Reversible decisions**: Prefer changes that can be undone
- **Document decisions**: Why did we do X instead of Y?
- **Avoid analysis paralysis**: Perfect is enemy of good

### After the Incident

- **Blameless post-mortem**: Focus on systems, not people
- **Action items**: Specific, assigned, with due dates
- **Share learnings**: Post-mortem to entire engineering team
- **Follow up**: Track action items to completion

## Tools and Resources

### Monitoring
- Datadog, New Relic, Grafana
- Sentry, Rollbar (error tracking)
- PagerDuty, Opsgenie (alerting)

### Communication
- Slack, Microsoft Teams
- Status page (StatusPage.io, Atlassian Statuspage)
- Incident.io, FireHydrant (incident management)

### Runbooks
- Maintain runbooks for common issues
- Practice incident response (game days)
- Keep contact lists updated
- Document escalation paths
