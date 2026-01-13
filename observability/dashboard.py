"""
Observability Dashboard Web Interface

FastAPI-based web dashboard for visualizing observability metrics, query performance,
cost trends, errors, and health status.
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

from .analytics import get_analytics
from .config import get_config
from .errors import get_error_tracker
from .health import run_health_checks
from .logger import get_logger
from .metrics import get_metrics_collector

logger = get_logger(__name__)

# Get the directory where this module is located
OBSERVABILITY_DIR = Path(__file__).parent
TEMPLATES_DIR = OBSERVABILITY_DIR / "templates"


# Pydantic models for API responses
class MetricData(BaseModel):
    """Model for metric data point."""
    timestamp: str
    value: float
    tags: Dict[str, str] = {}


class StatsResponse(BaseModel):
    """Model for statistics response."""
    total_queries: int
    total_errors: int
    total_cost_usd: float
    avg_query_duration_seconds: float
    health_status: str


# Initialize FastAPI app
app = FastAPI(
    title="Observability Dashboard",
    description="Real-time monitoring dashboard for DecentClaude observability metrics",
    version="1.0.0"
)


# Dashboard routes
@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Serve the main dashboard page."""
    template_path = TEMPLATES_DIR / "dashboard.html"
    with open(template_path) as f:
        return f.read()


@app.get("/metrics", response_class=HTMLResponse)
async def metrics_page():
    """Serve the metrics page."""
    template_path = TEMPLATES_DIR / "metrics.html"
    with open(template_path) as f:
        return f.read()


@app.get("/queries", response_class=HTMLResponse)
async def queries_page():
    """Serve the queries page."""
    template_path = TEMPLATES_DIR / "queries.html"
    with open(template_path) as f:
        return f.read()


@app.get("/costs", response_class=HTMLResponse)
async def costs_page():
    """Serve the costs page."""
    template_path = TEMPLATES_DIR / "costs.html"
    with open(template_path) as f:
        return f.read()


@app.get("/errors", response_class=HTMLResponse)
async def errors_page():
    """Serve the errors page."""
    template_path = TEMPLATES_DIR / "errors.html"
    with open(template_path) as f:
        return f.read()


@app.get("/health", response_class=HTMLResponse)
async def health_page():
    """Serve the health checks page."""
    try:
        health_data = run_health_checks()

        # Generate simple HTML for health status
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Health Checks - Observability Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        header {{
            background: #2c3e50;
            color: white;
            padding: 20px 0;
            margin-bottom: 30px;
        }}
        h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        .nav {{
            display: flex;
            gap: 15px;
            margin-top: 15px;
        }}
        .nav a {{
            color: white;
            text-decoration: none;
            padding: 8px 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
        }}
        .nav a:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}
        .status-card {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }}
        .status-badge {{
            display: inline-block;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 1.2em;
            font-weight: bold;
        }}
        .status-badge.healthy {{
            background: #d5f4e6;
            color: #27ae60;
        }}
        .status-badge.degraded {{
            background: #fef5e7;
            color: #f39c12;
        }}
        .status-badge.unhealthy {{
            background: #fadbd8;
            color: #c0392b;
        }}
        .checks-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .check-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .check-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .check-name {{
            font-size: 1.2em;
            font-weight: bold;
        }}
        .check-status {{
            padding: 5px 10px;
            border-radius: 12px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .check-status.healthy {{
            background: #d5f4e6;
            color: #27ae60;
        }}
        .check-status.degraded {{
            background: #fef5e7;
            color: #f39c12;
        }}
        .check-status.unhealthy {{
            background: #fadbd8;
            color: #c0392b;
        }}
        .check-message {{
            color: #555;
            margin-bottom: 10px;
        }}
        .check-details {{
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        .timestamp {{
            text-align: center;
            color: #7f8c8d;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>Health Checks</h1>
            <p>System component health status</p>
            <div class="nav">
                <a href="/">Dashboard</a>
                <a href="/metrics">Metrics</a>
                <a href="/queries">Queries</a>
                <a href="/costs">Costs</a>
                <a href="/errors">Errors</a>
                <a href="/health">Health</a>
            </div>
        </div>
    </header>

    <div class="container">
        <div class="status-card">
            <h2>Overall Status</h2>
            <div class="status-badge {health_data['status'].lower()}">
                {health_data['status'].upper()}
            </div>
        </div>

        <div class="checks-grid">
"""

        for check_name, check_result in health_data['checks'].items():
            html += f"""
            <div class="check-card">
                <div class="check-header">
                    <div class="check-name">{check_name.upper()}</div>
                    <div class="check-status {check_result['status'].lower()}">
                        {check_result['status'].upper()}
                    </div>
                </div>
                <div class="check-message">{check_result['message']}</div>
                <div class="check-details">
                    Duration: {check_result['duration_seconds']:.3f}s
                </div>
            </div>
"""

        html += f"""
        </div>

        <div class="timestamp">
            Last updated: {health_data['timestamp']}
        </div>
    </div>
</body>
</html>
"""
        return html

    except Exception as e:
        logger.error(f"Error loading health page: {str(e)}")
        return f"<html><body><h1>Error loading health checks</h1><p>{str(e)}</p></body></html>"


# API endpoints
@app.get("/api/stats")
async def get_stats():
    """Get overall statistics."""
    try:
        # In a real implementation, these would come from a metrics store
        # For now, return mock data
        return {
            "total_queries": 1250,
            "total_errors": 15,
            "total_cost_usd": 42.50,
            "avg_query_duration_seconds": 1.234,
            "health_status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics/recent")
async def get_recent_metrics(hours: int = 24):
    """Get recent metrics data."""
    try:
        # Mock data for demonstration
        # In production, this would query from metrics store
        now = datetime.utcnow()
        data_points = []

        for i in range(hours):
            timestamp = now - timedelta(hours=hours - i)
            data_points.append({
                "timestamp": timestamp.isoformat(),
                "query_count": 50 + (i * 2),
                "avg_duration": 1.2 + (i * 0.05),
                "error_count": 1 if i % 5 == 0 else 0,
                "cost_usd": 1.5 + (i * 0.1)
            })

        return {
            "data": data_points,
            "period_hours": hours
        }
    except Exception as e:
        logger.error(f"Error getting recent metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/queries/recent")
async def get_recent_queries(limit: int = 50):
    """Get recent query executions."""
    try:
        # Mock data
        queries = []
        query_types = ["SELECT", "INSERT", "UPDATE", "DELETE"]

        for i in range(limit):
            queries.append({
                "id": i + 1,
                "query_type": query_types[i % len(query_types)],
                "duration_seconds": round(0.5 + (i * 0.1), 3),
                "bytes_processed": 1024 * (i + 1) * 100,
                "rows_returned": (i + 1) * 10,
                "timestamp": (datetime.utcnow() - timedelta(minutes=i)).isoformat(),
                "status": "success" if i % 10 != 0 else "error"
            })

        return {
            "queries": queries,
            "total": len(queries)
        }
    except Exception as e:
        logger.error(f"Error getting recent queries: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/costs/trends")
async def get_cost_trends(period: str = "daily"):
    """Get cost trends over time."""
    try:
        # Mock data
        trends = []
        days = 30 if period == "daily" else 12

        for i in range(days):
            if period == "daily":
                date = (datetime.utcnow() - timedelta(days=days - i)).strftime("%Y-%m-%d")
            else:
                date = f"Month {i + 1}"

            trends.append({
                "period": date,
                "cost_usd": round(10.0 + (i * 2.5), 2),
                "queries": 100 + (i * 10),
                "bytes_processed": 1024 * 1024 * (i + 1) * 100
            })

        return {
            "trends": trends,
            "period": period
        }
    except Exception as e:
        logger.error(f"Error getting cost trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/errors/recent")
async def get_recent_errors(limit: int = 50):
    """Get recent errors."""
    try:
        # Mock data
        errors = []
        error_types = ["QueryError", "ConnectionError", "TimeoutError", "ValidationError"]

        for i in range(min(limit, 20)):
            errors.append({
                "id": i + 1,
                "error_type": error_types[i % len(error_types)],
                "message": f"Sample error message {i + 1}",
                "timestamp": (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                "context": {
                    "operation": "query_execution",
                    "retry_count": i % 3
                }
            })

        return {
            "errors": errors,
            "total": len(errors)
        }
    except Exception as e:
        logger.error(f"Error getting recent errors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def get_health_status():
    """Get system health status."""
    try:
        return run_health_checks()
    except Exception as e:
        logger.error(f"Error getting health status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def run_server(
    host: Optional[str] = None,
    port: Optional[int] = None,
):
    """
    Run the dashboard web server.

    Args:
        host: Host to bind to (default: from config or 0.0.0.0)
        port: Port to listen on (default: from config or 8001)
    """
    import os

    config = get_config()

    # Get host and port from environment or parameters
    dashboard_host = host or os.getenv("DASHBOARD_HOST", "0.0.0.0")
    dashboard_port = port or int(os.getenv("DASHBOARD_PORT", "8001"))

    logger.info(
        "Starting observability dashboard",
        host=dashboard_host,
        port=dashboard_port,
        environment=config.environment
    )

    uvicorn.run(app, host=dashboard_host, port=dashboard_port)


if __name__ == "__main__":
    run_server()
