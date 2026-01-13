# Observability Dashboard

A lightweight web dashboard for visualizing observability metrics, query performance, cost trends, errors, and system health.

## Features

### 1. Dashboard Home (`/`)
- **Real-time Statistics**: Total queries, average duration, total cost, error count
- **Performance Charts**: Query count and duration trends over 24 hours
- **Cost Tracking**: Hourly cost visualization
- **Error Monitoring**: Error rate tracking
- **System Health**: Component health status doughnut chart
- **Recent Activity**: Latest query executions with status indicators
- **Auto-refresh**: Updates every 30 seconds

### 2. Metrics Page (`/metrics`)
- **Query Execution Metrics**: Line chart of query count over time
- **Duration Distribution**: Bar chart of average query duration
- **Data Processing Volume**: Volume of data processed
- **Success vs Error Rate**: Success/error ratio visualization
- **Metrics Summary Table**: Current, average, peak, and total values
- **Configurable Time Range**: 1 hour, 6 hours, 24 hours, or 1 week

### 3. Queries Page (`/queries`)
- **Query History Table**: Detailed execution logs with:
  - Query ID and type (SELECT, INSERT, UPDATE, DELETE)
  - Execution status (success/error)
  - Duration in seconds
  - Rows returned
  - Bytes processed
  - Timestamp
- **CSV Export**: Export query data (functionality placeholder)
- **Auto-refresh**: Updates every 30 seconds

### 4. Costs Page (`/costs`)
- **Cost Statistics**:
  - Today's cost
  - Monthly cost
  - Average daily cost
  - Projected monthly cost
- **Budget Tracking**: Visual progress bar showing spend vs budget
- **Cost Trends Chart**: Line graph of cost over time
- **Cost by Query Type**: Breakdown by operation type
- **Data Processing Volume**: Bytes processed visualization
- **Cost Efficiency**: Cost per query metric
- **Configurable Periods**: Daily, weekly, or monthly views

### 5. Errors Page (`/errors`)
- **Error Statistics**:
  - Total errors in last 24 hours
  - Error rate percentage
  - Unique error types count
  - Time since last error
- **High Error Rate Alerts**: Visual alert when threshold exceeded
- **Error Trends Chart**: Error count over time
- **Errors by Type**: Bar chart breakdown
- **Recent Errors List**: Detailed error information with:
  - Error type and message
  - Timestamp
  - Context (operation, retry count)

### 6. Health Page (`/health`)
- **Overall System Status**: Health indicator (healthy/degraded/unhealthy)
- **Component Health Checks**:
  - BigQuery connectivity
  - Sentry error tracking
  - Prometheus metrics server
- **Check Details**: Duration and status for each component
- **Auto-refresh**: Real-time health monitoring

## Setup

### Prerequisites

```bash
pip install fastapi uvicorn
```

### Environment Variables

The dashboard reuses observability framework configuration:

```bash
# Dashboard Configuration
DASHBOARD_HOST=0.0.0.0         # Default: 0.0.0.0
DASHBOARD_PORT=8001            # Default: 8001

# Observability Framework (from observability/config.py)
LOG_LEVEL=INFO
METRICS_ENABLED=true
PROMETHEUS_PORT=8000
SENTRY_ENABLED=false
HEALTH_CHECK_ENABLED=true
```

### Running the Dashboard

#### Option 1: Direct Python

```bash
cd /Users/crlough/gt/decentclaude/mayor/rig
python -m observability.dashboard
```

#### Option 2: Custom Host/Port

```python
from observability.dashboard import run_server

run_server(host="127.0.0.1", port=8001)
```

#### Option 3: Environment Variables

```bash
export DASHBOARD_HOST=0.0.0.0
export DASHBOARD_PORT=8001
python -m observability.dashboard
```

## Usage

### Accessing the Dashboard

Once running, open your browser to:

```
http://localhost:8001/
```

### Navigation

Use the navigation bar at the top to switch between pages:
- **Dashboard**: Overview of all metrics
- **Metrics**: Detailed performance metrics
- **Queries**: Query execution history
- **Costs**: Cost trends and budget tracking
- **Errors**: Error monitoring and alerts
- **Health**: System health checks

### API Endpoints

The dashboard also provides JSON APIs:

```bash
# Get overall statistics
curl http://localhost:8001/api/stats

# Get recent metrics (last 24 hours)
curl http://localhost:8001/api/metrics/recent?hours=24

# Get recent queries
curl http://localhost:8001/api/queries/recent?limit=50

# Get cost trends
curl http://localhost:8001/api/costs/trends?period=daily

# Get recent errors
curl http://localhost:8001/api/errors/recent?limit=50

# Get health status
curl http://localhost:8001/api/health
```

## Integration with Observability Framework

The dashboard integrates with existing observability components:

### Metrics Collection
```python
from observability.metrics import get_metrics_collector

collector = get_metrics_collector()
# Dashboard reads from Prometheus metrics or Datadog
```

### Analytics
```python
from observability.analytics import get_analytics

analytics = get_analytics()
# Dashboard displays command execution statistics
```

### Error Tracking
```python
from observability.errors import get_error_tracker

tracker = get_error_tracker()
# Dashboard shows error trends and details
```

### Health Checks
```python
from observability.health import run_health_checks

health_status = run_health_checks()
# Dashboard displays component health
```

## Architecture

### Technology Stack
- **Backend**: FastAPI (async Python web framework)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Charts**: Chart.js 4.4.0 (loaded from CDN)
- **No Database**: Currently uses mock data; can be extended to read from:
  - Prometheus metrics server
  - Time-series database (InfluxDB, TimescaleDB)
  - BigQuery for historical analytics

### File Structure
```
observability/
├── dashboard.py              # Main FastAPI application
├── templates/                # HTML templates
│   ├── dashboard.html       # Main dashboard page
│   ├── metrics.html         # Metrics page
│   ├── queries.html         # Queries page
│   ├── costs.html           # Costs page
│   └── errors.html          # Errors page
└── dashboard_README.md      # This file
```

### Design Patterns
- **Single Page Applications**: Each page is self-contained with inline JavaScript
- **RESTful API**: Clean JSON endpoints following REST principles
- **Responsive Design**: Works on desktop and mobile devices
- **Auto-refresh**: Real-time updates without page reload
- **Minimal Dependencies**: Uses CDN for Chart.js, no build step required

## Extending the Dashboard

### Adding Real Data Sources

Currently, the dashboard uses mock data. To integrate real data:

#### 1. Connect to Prometheus

```python
from prometheus_client import REGISTRY

@app.get("/api/metrics/prometheus")
async def get_prometheus_metrics():
    metrics = {}
    for metric in REGISTRY.collect():
        metrics[metric.name] = metric.samples
    return metrics
```

#### 2. Query BigQuery for Historical Data

```python
from google.cloud import bigquery

@app.get("/api/queries/history")
async def get_query_history(limit: int = 100):
    client = bigquery.Client()
    query = """
        SELECT *
        FROM `project.dataset.query_logs`
        ORDER BY timestamp DESC
        LIMIT @limit
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("limit", "INT64", limit)
        ]
    )
    results = client.query(query, job_config=job_config)
    return [dict(row) for row in results]
```

#### 3. Add WebSocket Support for Real-time Updates

```python
from fastapi import WebSocket

@app.websocket("/ws/metrics")
async def metrics_websocket(websocket: WebSocket):
    await websocket.accept()
    while True:
        metrics = await get_current_metrics()
        await websocket.send_json(metrics)
        await asyncio.sleep(5)
```

### Custom Health Checks

```python
from observability.health import HealthCheck, HealthCheckResult, HealthStatus

class CustomHealthCheck(HealthCheck):
    def __init__(self):
        super().__init__("custom_service", timeout_seconds=5.0)

    def check(self) -> HealthCheckResult:
        # Your custom health check logic
        return HealthCheckResult(
            name=self.name,
            status=HealthStatus.HEALTHY,
            message="Service is running"
        )

# Register in dashboard.py
from observability.health import register_health_check
register_health_check(CustomHealthCheck())
```

### Adding New Pages

1. Create HTML template in `templates/` directory
2. Add route in `dashboard.py`:

```python
@app.get("/my-page", response_class=HTMLResponse)
async def my_page():
    with open("templates/my-page.html") as f:
        return f.read()
```

3. Add API endpoint for data:

```python
@app.get("/api/my-data")
async def get_my_data():
    return {"data": "value"}
```

## Deployment

### Development
```bash
# Run with auto-reload
uvicorn observability.dashboard:app --reload --port 8001
```

### Production

#### Using Gunicorn + Uvicorn Workers
```bash
pip install gunicorn
gunicorn observability.dashboard:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8001
```

#### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY observability/ observability/

CMD ["uvicorn", "observability.dashboard:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### Using Systemd Service
```ini
[Unit]
Description=Observability Dashboard
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/rig
Environment="DASHBOARD_PORT=8001"
ExecStart=/usr/bin/python3 -m observability.dashboard
Restart=always

[Install]
WantedBy=multi-user.target
```

## Security Considerations

- **No Authentication**: Currently open to all users on the network
- **Production Recommendations**:
  - Add authentication (JWT, OAuth, API keys)
  - Use HTTPS/TLS
  - Implement rate limiting
  - Add CORS configuration for API endpoints
  - Sanitize all inputs
  - Use environment-specific configurations

## Performance

- **Lightweight**: Minimal dependencies, no database required
- **Fast**: Async FastAPI with efficient JSON serialization
- **Scalable**: Stateless design, can run multiple instances
- **Low Resource**: ~50MB memory footprint

## Troubleshooting

### Dashboard won't start
```bash
# Check if port is already in use
lsof -i :8001

# Try a different port
DASHBOARD_PORT=8002 python -m observability.dashboard
```

### Charts not loading
- Ensure internet connection (Chart.js loads from CDN)
- Check browser console for JavaScript errors
- Verify API endpoints return valid JSON

### No data showing
- Check that observability framework is initialized
- Verify Prometheus metrics server is running
- Check logs for API endpoint errors

## Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] User authentication and authorization
- [ ] Persistent storage for metrics history
- [ ] Alerting configuration UI
- [ ] Custom dashboard layouts
- [ ] Export functionality (CSV, PDF)
- [ ] Advanced filtering and search
- [ ] Integration with Grafana/Kibana
- [ ] Mobile app version
- [ ] Slack/email notifications

## License

Part of the DecentClaude observability framework.
