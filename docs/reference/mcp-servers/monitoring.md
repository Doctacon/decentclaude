# Monitoring Integration MCP Servers Guide

## Overview

Monitoring and observability MCP servers enable Claude Code to interact with monitoring platforms like DataDog, New Relic, Prometheus, Grafana, and others. This integration allows for automated incident response, metrics analysis, and system health monitoring.

## DataDog MCP Server

### Installation

```bash
# Install via npm
npm install -g @modelcontextprotocol/server-datadog

# Or use npx
npx -y @modelcontextprotocol/server-datadog
```

### Prerequisites

- DataDog account
- API key and Application key
- Appropriate permissions

### Authentication Setup

1. **Create API and Application Keys**:
   - Go to DataDog: https://app.datadoghq.com/organization-settings/api-keys
   - Create API Key: Organization Settings > API Keys > New Key
   - Create Application Key: Organization Settings > Application Keys > New Key
   - Save both keys securely

2. **Store Keys Securely**:
   ```bash
   mkdir -p ~/.config/datadog
   echo "your-api-key" > ~/.config/datadog/api_key
   echo "your-app-key" > ~/.config/datadog/app_key
   chmod 600 ~/.config/datadog/*
   ```

### Configuration

**Claude Code Settings**:

```json
{
  "mcpServers": {
    "datadog": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-datadog"],
      "env": {
        "DD_API_KEY": "your-api-key",
        "DD_APP_KEY": "your-app-key",
        "DD_SITE": "datadoghq.com"
      }
    }
  }
}
```

**Secure Configuration**:

```json
{
  "mcpServers": {
    "datadog": {
      "command": "bash",
      "args": [
        "-c",
        "DD_API_KEY=$(cat ~/.config/datadog/api_key) DD_APP_KEY=$(cat ~/.config/datadog/app_key) npx -y @modelcontextprotocol/server-datadog"
      ],
      "env": {
        "DD_SITE": "datadoghq.com"
      }
    }
  }
}
```

**Regional Configuration**:

```json
{
  "env": {
    "DD_SITE": "datadoghq.eu"
  }
}
```

Common DD_SITE values:
- `datadoghq.com` (US1)
- `us3.datadoghq.com` (US3)
- `us5.datadoghq.com` (US5)
- `datadoghq.eu` (EU1)
- `ddog-gov.com` (US1-FED)

### Available Operations

#### Metrics Queries

**Query Timeseries Data**:

```
Get the average CPU usage for service:web over the last 1 hour
```

**Example queries**:
```
avg:system.cpu.user{env:production}
sum:aws.ec2.cpuutilization{*} by {availability-zone}
avg:trace.request.duration{service:api,env:prod}
rate(sum:redis.net.commands{*}.as_count())
```

**Metric Math**:
```
(avg:system.mem.used{*} / avg:system.mem.total{*}) * 100
```

**List Available Metrics**:

```
List all metrics with prefix "system.cpu"
```

**Get Metric Metadata**:

```
Show metadata for metric system.cpu.user
```

#### Monitors and Alerts

**List Monitors**:

```
List all monitors with state "Alert"
```

**Get Monitor Details**:

```
Show details for monitor ID 12345
```

**Create Monitor**:

```
Create a monitor:
Name: High CPU usage on production web servers
Query: avg(last_5m):avg:system.cpu.user{env:production,service:web} > 80
Type: metric alert
Message: CPU usage is above 80% on production web servers. Please investigate.
Tags: team:platform, severity:high
```

**Update Monitor**:

```
Update monitor 12345:
- Change threshold to 90
- Add tag: reviewed:true
- Update message
```

**Mute Monitor**:

```
Mute monitor 12345 for 2 hours with reason: "Planned maintenance"
```

**Unmute Monitor**:

```
Unmute monitor 12345
```

**Delete Monitor**:

```
Delete monitor 12345
```

#### Dashboards

**List Dashboards**:

```
List all dashboards
```

**Get Dashboard**:

```
Show dashboard "Production Overview"
```

**Create Dashboard**:

```
Create a dashboard:
Title: Service Health
Description: Overview of service health metrics
Widgets:
  - Timeseries: avg:system.cpu.user{service:api}
  - Query value: avg:system.mem.used{service:api}
  - Top list: top 10 services by error rate
```

**Update Dashboard**:

```
Update dashboard "Production Overview":
- Add widget for database connections
- Update title
```

#### Logs

**Search Logs**:

```
Search logs:
Query: service:api status:error
Time range: last 1 hour
Limit: 100
```

**Log Queries**:
```
# Error logs
status:error service:api

# By environment
env:production service:web

# By source
source:nginx

# Complex query
service:api status:(error OR warn) env:production -host:test*
```

**Get Log Context**:

```
Get logs around log ID abc123 with 5 minutes before and after
```

**Aggregate Logs**:

```
Count logs by status for service:api in the last 24 hours
```

#### Events

**List Events**:

```
List events from the last 24 hours with tag "deployment"
```

**Create Event**:

```
Create an event:
Title: Deployment to production
Text: Deployed version v1.2.3 to production
Tags: deployment, service:api, env:production
```

**Get Event Details**:

```
Show event ID 12345
```

#### Service Catalog

**List Services**:

```
List all services
```

**Get Service Details**:

```
Show details for service "api"
```

**Service Dependencies**:

```
Show dependencies for service "api"
```

#### Hosts

**List Hosts**:

```
List all hosts with tag env:production
```

**Get Host Details**:

```
Show details for host web-01.example.com
```

**Host Metrics**:

```
Get CPU and memory metrics for host web-01.example.com
```

#### APM (Application Performance Monitoring)

**List Services**:

```
List all APM services
```

**Get Service Performance**:

```
Show performance metrics for service:api over the last 1 hour
```

**Trace Search**:

```
Search traces:
Service: api
Resource: GET /users
Duration: > 1s
Time range: last 1 hour
```

**Get Trace Details**:

```
Show trace ID abc123def456
```

#### Synthetics

**List Synthetic Tests**:

```
List all synthetic tests
```

**Get Test Results**:

```
Show results for synthetic test "API Health Check"
```

**Get Test Details**:

```
Show details for synthetic test ID 12345
```

### DataDog Best Practices

#### Metric Naming

1. **Use Consistent Prefixes**:
   ```
   service.api.request.count
   service.api.request.duration
   service.api.error.count
   ```

2. **Include Units**: In metric names or metadata
   ```
   database.connections.count
   database.query.duration.ms
   memory.usage.bytes
   ```

3. **Use Tags Effectively**:
   ```
   env:production
   service:api
   version:v1.2.3
   team:platform
   ```

#### Query Optimization

1. **Use Time Aggregation**:
   ```
   avg(last_5m):avg:system.cpu.user{*}
   sum(last_1h):sum:http.requests{*}.as_count()
   ```

2. **Filter with Tags**:
   ```
   avg:system.cpu.user{env:production,service:web}
   ```

3. **Group By Tags**:
   ```
   avg:system.cpu.user{*} by {host}
   avg:http.requests{*} by {service,env}
   ```

#### Alert Configuration

1. **Clear Alert Messages**:
   ```
   Alert: High Error Rate on {{service.name}}

   Error rate is {{value}}% (threshold: {{threshold}}%)

   Environment: {{env.name}}
   Service: {{service.name}}

   Runbook: https://wiki.example.com/runbooks/high-error-rate
   Dashboard: https://app.datadoghq.com/dashboard/abc123

   @slack-platform-alerts @pagerduty-oncall
   ```

2. **Use Alert Recovery**:
   ```
   Recovery: Error rate back to normal on {{service.name}}

   Error rate is now {{value}}% (was {{last_triggered_at}})
   ```

3. **Alert Tags**:
   ```
   team:platform
   severity:high
   service:api
   alert-type:error-rate
   ```

## Prometheus MCP Server

### Installation

```bash
# Install via npm
npm install -g @modelcontextprotocol/server-prometheus

# Or use npx
npx -y @modelcontextprotocol/server-prometheus
```

### Configuration

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-prometheus"],
      "env": {
        "PROMETHEUS_URL": "http://localhost:9090"
      }
    }
  }
}
```

**With Authentication**:

```json
{
  "mcpServers": {
    "prometheus": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-prometheus"],
      "env": {
        "PROMETHEUS_URL": "https://prometheus.example.com",
        "PROMETHEUS_AUTH_TOKEN": "bearer-token",
        "PROMETHEUS_BASIC_AUTH": "username:password"
      }
    }
  }
}
```

### Available Operations

#### Query Metrics

**Instant Query**:

```
Query prometheus: rate(http_requests_total[5m])
```

**Range Query**:

```
Query prometheus over last 1 hour with 30s step:
rate(http_requests_total{job="api"}[5m])
```

**PromQL Examples**:

```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m]) /
rate(http_requests_total[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Memory usage
process_resident_memory_bytes / 1024 / 1024

# CPU usage
rate(process_cpu_seconds_total[5m]) * 100

# Aggregations
sum(rate(http_requests_total[5m])) by (job)
avg(node_cpu_seconds_total) by (mode)
topk(5, sum(rate(http_requests_total[5m])) by (handler))
```

#### Metadata

**List Metrics**:

```
List all prometheus metrics
```

**Get Metric Metadata**:

```
Show metadata for http_requests_total
```

**List Labels**:

```
List all label names
```

**Get Label Values**:

```
Get values for label "job"
```

#### Targets and Service Discovery

**List Targets**:

```
Show all prometheus targets
```

**Get Target Health**:

```
Check health of all targets
```

#### Alerts

**List Active Alerts**:

```
Show all active prometheus alerts
```

**Get Alert Rules**:

```
List all alert rules
```

### Prometheus Best Practices

#### Metric Design

1. **Use Counter for Cumulative Values**:
   ```promql
   http_requests_total
   errors_total
   bytes_sent_total
   ```

2. **Use Gauge for Current State**:
   ```promql
   memory_usage_bytes
   cpu_temperature
   active_connections
   ```

3. **Use Histogram for Distributions**:
   ```promql
   http_request_duration_seconds
   response_size_bytes
   ```

4. **Use Summary for Quantiles**:
   ```promql
   api_request_duration_seconds
   ```

#### Query Performance

1. **Use Recording Rules**:
   ```yaml
   # prometheus.yml
   groups:
     - name: example
       interval: 30s
       rules:
         - record: job:http_requests:rate5m
           expr: rate(http_requests_total[5m])
   ```

2. **Limit Cardinality**:
   ```promql
   # Good: Low cardinality labels
   http_requests_total{method="GET", status="200"}

   # Bad: High cardinality labels (user_id, session_id, etc.)
   # Don't do this:
   http_requests_total{user_id="12345"}
   ```

3. **Use Appropriate Time Ranges**:
   ```promql
   # Match rate window to query interval
   rate(http_requests_total[5m])  # Good for 5m intervals
   rate(http_requests_total[1m])  # Good for real-time
   ```

## Grafana MCP Server

### Installation

```bash
# Install via npm
npm install -g @modelcontextprotocol/server-grafana

# Or use npx
npx -y @modelcontextprotocol/server-grafana
```

### Configuration

```json
{
  "mcpServers": {
    "grafana": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-grafana"],
      "env": {
        "GRAFANA_URL": "http://localhost:3000",
        "GRAFANA_API_KEY": "your-api-key"
      }
    }
  }
}
```

**With Basic Auth**:

```json
{
  "mcpServers": {
    "grafana": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-grafana"],
      "env": {
        "GRAFANA_URL": "https://grafana.example.com",
        "GRAFANA_USER": "admin",
        "GRAFANA_PASSWORD": "password"
      }
    }
  }
}
```

### Available Operations

#### Dashboards

**List Dashboards**:

```
List all grafana dashboards
```

**Get Dashboard**:

```
Show dashboard "System Overview"
```

**Create Dashboard**:

```
Create a grafana dashboard:
Title: API Performance
Panels:
  - Request Rate (graph)
  - Error Rate (graph)
  - Latency P95 (graph)
  - Active Connections (stat)
```

**Update Dashboard**:

```
Update dashboard "API Performance":
- Add new panel for database connections
- Update time range to last 6 hours
```

**Delete Dashboard**:

```
Delete dashboard "Old Dashboard"
```

**Export Dashboard**:

```
Export dashboard "System Overview" to JSON
```

**Import Dashboard**:

```
Import dashboard from JSON
```

#### Data Sources

**List Data Sources**:

```
List all grafana data sources
```

**Add Data Source**:

```
Add prometheus data source:
Name: Prometheus Production
URL: http://prometheus:9090
Type: prometheus
Access: proxy
```

**Test Data Source**:

```
Test data source "Prometheus Production"
```

#### Alerts

**List Alert Rules**:

```
List all grafana alert rules
```

**Get Alert State**:

```
Check state of alert "High CPU"
```

**Create Alert Rule**:

```
Create alert rule:
Name: High Memory Usage
Condition: avg(memory_usage) > 80
For: 5m
Annotations:
  summary: Memory usage above 80%
  description: Current value: {{ $value }}%
```

#### Annotations

**List Annotations**:

```
List annotations for the last 24 hours
```

**Create Annotation**:

```
Create annotation:
Text: Deployment v1.2.3
Tags: deployment, production
Time: now
```

#### Organizations and Users

**List Organizations**:

```
List all grafana organizations
```

**List Users**:

```
List all grafana users
```

**Add User**:

```
Add user to grafana:
Login: john.doe
Email: john@example.com
Role: Viewer
```

## New Relic MCP Server

### Configuration

```json
{
  "mcpServers": {
    "newrelic": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-newrelic"],
      "env": {
        "NEW_RELIC_API_KEY": "your-api-key",
        "NEW_RELIC_ACCOUNT_ID": "your-account-id"
      }
    }
  }
}
```

### Available Operations

#### NRQL Queries

**Query Data**:

```
Run New Relic query:
SELECT average(duration) FROM Transaction
WHERE appName = 'API'
SINCE 1 hour ago
FACET name
```

**Example NRQL Queries**:

```sql
-- Average response time
SELECT average(duration)
FROM Transaction
WHERE appName = 'Production API'
SINCE 1 hour ago

-- Error rate
SELECT percentage(count(*), WHERE error IS true)
FROM Transaction
WHERE appName = 'Production API'
SINCE 1 day ago
TIMESERIES

-- Throughput
SELECT rate(count(*), 1 minute)
FROM Transaction
WHERE appName = 'Production API'
SINCE 1 hour ago
TIMESERIES

-- Top slow transactions
SELECT average(duration)
FROM Transaction
WHERE appName = 'Production API'
SINCE 1 hour ago
FACET name
LIMIT 10
```

#### Applications

**List Applications**:

```
List all New Relic applications
```

**Get Application Details**:

```
Show details for application "Production API"
```

**Application Health**:

```
Check health status for application "Production API"
```

#### Infrastructure

**List Hosts**:

```
List all infrastructure hosts
```

**Host Metrics**:

```
Get metrics for host "web-01"
```

## Common Monitoring Workflows

### Incident Investigation

```
1. Check current alerts in DataDog
2. For each critical alert:
   - Get alert details
   - Query related metrics
   - Check logs for errors
   - Get trace samples
3. Identify root cause
4. Create incident event
5. Document findings
```

### Performance Analysis

```
1. Query request rate over last 24 hours
2. Query error rate over last 24 hours
3. Query p95 latency over last 24 hours
4. Compare with previous week
5. Identify anomalies
6. Generate performance report
```

### Capacity Planning

```
1. Get historical CPU usage (30 days)
2. Get historical memory usage (30 days)
3. Get historical request rate (30 days)
4. Calculate growth trends
5. Predict future resource needs
6. Generate capacity report
```

### SLO Monitoring

```
1. Define SLO: 99.9% availability
2. Query actual uptime
3. Calculate error budget
4. If error budget low:
   - Alert team
   - Freeze deployments
   - Focus on reliability
5. Generate SLO report
```

### Deployment Validation

```
Before deployment:
1. Check current error rates
2. Check current latencies
3. Create deployment event

After deployment:
1. Monitor error rates (15 min)
2. Monitor latencies (15 min)
3. Compare with pre-deployment
4. If degradation:
   - Trigger rollback
5. Create validation report
```

## Integration Patterns

### Multi-Platform Monitoring

Combine multiple monitoring sources:

```json
{
  "mcpServers": {
    "datadog": { ... },
    "prometheus": { ... },
    "grafana": { ... }
  }
}
```

Usage:
```
Compare metrics from DataDog and Prometheus:
1. Query error rate from DataDog
2. Query error rate from Prometheus
3. Identify discrepancies
4. Generate comparison report
```

### Automated Remediation

```
When high error rate alert triggers:
1. Get recent error logs
2. Identify error patterns
3. Check if known issue
4. If known:
   - Execute automated fix
   - Document action
5. If unknown:
   - Create incident
   - Alert on-call engineer
   - Collect diagnostics
```

### Alerting Integration

```
Configure alert routing:
1. Critical alerts -> PagerDuty
2. High alerts -> Slack + email
3. Medium alerts -> Slack
4. Low alerts -> Email only

Alert enrichment:
1. Add runbook links
2. Add dashboard links
3. Add recent changes
4. Add similar past incidents
```

## Troubleshooting

### Authentication Issues

**DataDog**:
```bash
# Verify API keys
curl -X GET "https://api.datadoghq.com/api/v1/validate" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}"
```

**Prometheus**:
```bash
# Test connection
curl http://localhost:9090/api/v1/status/config
```

**Grafana**:
```bash
# Test API key
curl -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
  http://localhost:3000/api/org
```

### Query Issues

**DataDog Query Timeout**:
- Reduce time range
- Use aggregation
- Limit tag cardinality

**Prometheus Query Too Large**:
- Use recording rules
- Increase query timeout
- Optimize PromQL

### Data Quality

**Missing Data**:
- Check agent/exporter health
- Verify network connectivity
- Check retention policies
- Verify tag filters

**Inconsistent Data**:
- Check time synchronization
- Verify aggregation methods
- Compare sampling rates
- Check for data gaps

## Resources

- [DataDog API Documentation](https://docs.datadoghq.com/api/)
- [Prometheus Query Documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana HTTP API](https://grafana.com/docs/grafana/latest/developers/http_api/)
- [New Relic NRQL Reference](https://docs.newrelic.com/docs/query-your-data/nrql-new-relic-query-language/)
- [PromQL Cheat Sheet](https://promlabs.com/promql-cheat-sheet/)
- [DataDog Metrics Guide](https://docs.datadoghq.com/metrics/)
