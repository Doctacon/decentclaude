#!/bin/bash
# Quick start script for the Observability Dashboard

set -e

echo "Starting Observability Dashboard..."
echo ""

# Set default values if not provided
export DASHBOARD_HOST=${DASHBOARD_HOST:-0.0.0.0}
export DASHBOARD_PORT=${DASHBOARD_PORT:-8001}

echo "Configuration:"
echo "  Host: $DASHBOARD_HOST"
echo "  Port: $DASHBOARD_PORT"
echo ""

# Check if FastAPI is installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "Error: FastAPI is not installed."
    echo "Please install dependencies:"
    echo "  pip install -r observability/requirements.txt"
    exit 1
fi

# Check if uvicorn is installed
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "Error: Uvicorn is not installed."
    echo "Please install dependencies:"
    echo "  pip install -r observability/requirements.txt"
    exit 1
fi

echo "All dependencies are installed."
echo ""
echo "Dashboard will be available at:"
echo "  http://localhost:$DASHBOARD_PORT/"
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

# Run the dashboard
cd "$(dirname "$0")/.."
python3 -m observability.dashboard
