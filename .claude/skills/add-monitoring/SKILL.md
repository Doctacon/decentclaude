---
name: add-monitoring
description: Observability workflow adding logging, metrics, tracing, and alerts with dashboard generation for Datadog/Prometheus integration
allowed-tools:
  - Read
  - Grep
  - Bash
  - Edit
  - Write
---

# Add Monitoring Skill

Comprehensive observability workflow for adding logging, metrics, distributed tracing, and alerts to applications. Integrates with Datadog, Prometheus, Grafana, and ELK stack.

## The Three Pillars of Observability

1. **Logs**: Discrete events (errors, warnings, info)
2. **Metrics**: Numeric measurements over time (latency, throughput, error rate)
3. **Traces**: Request flows through distributed systems

## Workflow

### 1. Identify What to Monitor

**Golden Signals** (Google SRE):
- **Latency**: How long requests take
- **Traffic**: How many requests
- **Errors**: Rate of failed requests
- **Saturation**: How full is the system (CPU, memory, disk)

**RED Method** (for services):
- **Rate**: Requests per second
- **Errors**: Failed requests
- **Duration**: Time per request

**USE Method** (for resources):
- **Utilization**: % time resource is busy
- **Saturation**: Queue depth
- **Errors**: Error count

### 2. Add Structured Logging

**Python logging setup**:
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        if record.exc_info:
            log_obj['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(handler)

# Usage
logger.info("User logged in", extra={'user_id': 123, 'ip': '1.2.3.4'})
logger.error("Payment failed", extra={'order_id': 456, 'amount': 99.99})
```

**JavaScript/Node.js logging**:
```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'app.log' })
  ]
});

// Usage
logger.info('User logged in', { userId: 123, ip: '1.2.3.4' });
logger.error('Payment failed', { orderId: 456, amount: 99.99 });
```

### 3. Add Metrics

**Python with Prometheus**:
```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Define metrics
requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
active_users = Gauge('active_users_total', 'Number of active users')

# Instrument code
@request_duration.labels(method='GET', endpoint='/api/users').time()
def get_users():
    requests_total.labels(method='GET', endpoint='/api/users', status='200').inc()
    # Your code
    return users

# Expose metrics endpoint
start_http_server(8000)  # Metrics at http://localhost:8000/metrics
```

**Node.js with Prometheus**:
```javascript
const client = require('prom-client');

// Create metrics
const httpRequestsTotal = new client.Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'endpoint', 'status']
});

const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration',
  labelNames: ['method', 'endpoint']
});

// Middleware to track requests
app.use((req, res, next) => {
  const end = httpRequestDuration.startTimer({ method: req.method, endpoint: req.path });

  res.on('finish', () => {
    httpRequestsTotal.inc({ method: req.method, endpoint: req.path, status: res.statusCode });
    end();
  });

  next();
});

// Expose metrics
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', client.register.contentType);
  res.end(await client.register.metrics());
});
```

### 4. Add Distributed Tracing

**Python with OpenTelemetry**:
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Setup
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(agent_host_name='localhost', agent_port=6831)
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

tracer = trace.get_tracer(__name__)

# Instrument code
with tracer.start_as_current_span("process_order") as span:
    span.set_attribute("order.id", order_id)
    span.set_attribute("user.id", user_id)

    # Call other services (automatically traced)
    check_inventory()
    process_payment()
    send_confirmation()
```

### 5. Set Up Alerts

**Prometheus alert rules**:
```yaml
groups:
  - name: application_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"

      # High latency
      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "p95 latency is {{ $value }}s"

      # Service down
      - alert: ServiceDown
        expr: up{job="myapp"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Service is down"
```

**Datadog monitors**:
```python
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.model.monitor import Monitor

configuration = Configuration()
with ApiClient(configuration) as api_client:
    api_instance = MonitorsApi(api_client)

    monitor = Monitor(
        type="metric alert",
        query="avg(last_5m):avg:myapp.error_rate{*} > 0.05",
        name="High Error Rate",
        message="Error rate exceeded 5% @slack-ops",
        options={
            "thresholds": {"critical": 0.05, "warning": 0.03},
            "notify_no_data": True,
            "no_data_timeframe": 10
        }
    )

    api_instance.create_monitor(body=monitor)
```

### 6. Create Dashboards

**Grafana dashboard JSON**:
```json
{
  "dashboard": {
    "title": "Application Overview",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ],
        "type": "graph"
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "Errors"
          }
        ],
        "type": "graph"
      },
      {
        "title": "p95 Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, http_request_duration_seconds_bucket)",
            "legendFormat": "p95"
          }
        ],
        "type": "graph"
      }
    ]
  }
}
```

### 7. Monitor Critical Paths

Identify and instrument critical user flows:

```python
# Example: Order checkout flow
@tracer.start_as_current_span("checkout_flow")
def checkout(cart_id, payment_info):
    logger.info("Checkout started", extra={'cart_id': cart_id})

    with tracer.start_as_current_span("validate_cart"):
        cart = validate_cart(cart_id)

    with tracer.start_as_current_span("process_payment"):
        payment = process_payment(payment_info)

    with tracer.start_as_current_span("create_order"):
        order = create_order(cart, payment)

    checkout_success.inc()
    logger.info("Checkout completed", extra={'order_id': order.id})

    return order
```

## Monitoring Stack Examples

### Datadog Integration
```python
from ddtrace import tracer, patch_all
import datadog

patch_all()  # Auto-instrument Flask, requests, etc.

# Initialize Datadog
datadog.initialize(api_key='your_key', app_key='your_app_key')

# Custom metrics
datadog.statsd.increment('orders.completed')
datadog.statsd.gauge('inventory.stock', 100)
datadog.statsd.histogram('order.value', 99.99)
```

### Prometheus + Grafana
```bash
# docker-compose.yml
version: '3'
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - 9090:9090

  grafana:
    image: grafana/grafana
    ports:
      - 3000:3000
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

### ELK Stack (Elasticsearch, Logstash, Kibana)
```yaml
# docker-compose.yml
version: '3'
services:
  elasticsearch:
    image: elasticsearch:8.0.0
    environment:
      - discovery.type=single-node
    ports:
      - 9200:9200

  logstash:
    image: logstash:8.0.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - 5000:5000

  kibana:
    image: kibana:8.0.0
    ports:
      - 5601:5601
```

## Best Practices

- **Start with high-level metrics** (golden signals)
- **Use structured logging** (JSON format)
- **Add correlation IDs** to trace requests across services
- **Set SLOs** (Service Level Objectives) and alert on SLI (Indicators)
- **Don't over-monitor**: Too many alerts = alert fatigue
- **Monitor what matters**: User-facing issues, not every metric
- **Test alerts**: Ensure they fire when they should
- **Document runbooks**: What to do when alert fires
