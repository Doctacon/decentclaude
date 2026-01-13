#!/usr/bin/env python3
"""
Team Metrics Dashboard Web Application

A Flask-based web dashboard for visualizing team metrics and analytics.

Usage:
    python scripts/metrics_dashboard.py [--port PORT] [--days DAYS] [--project-id PROJECT_ID]

Options:
    --port PORT           Port to run the dashboard (default: 5000)
    --days DAYS          Number of days of data to show (default: 30)
    --project-id ID      GCP project ID (uses default if not specified)
    --debug              Run in debug mode
"""

from flask import Flask, render_template, jsonify, request
from team_metrics import TeamMetricsCollector
import argparse
import os
from datetime import datetime

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Global collector instance
collector = None
default_days = 30


@app.route('/')
def index():
    """Render main dashboard page"""
    return render_template('metrics_dashboard.html')


@app.route('/api/metrics')
def get_metrics():
    """API endpoint to fetch metrics data

    Query parameters:
        days: Number of days to look back (default: from global config)
        categories: Comma-separated list of metric categories (default: all)
        team: Filter by team name (optional)
        project: Filter by project name (optional)
    """
    try:
        days = int(request.args.get('days', default_days))
        team = request.args.get('team')
        project = request.args.get('project')

        # Collect all metrics
        metrics = collector.collect_all_metrics(
            days=days,
            team_filter=team,
            project_filter=project
        )

        # Convert to JSON-serializable format
        output = {}
        for category, results in metrics.items():
            output[category] = [r.to_dict() for r in results]

        return jsonify(output)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/summary')
def get_summary():
    """API endpoint for dashboard summary statistics"""
    try:
        days = int(request.args.get('days', default_days))
        metrics = collector.collect_all_metrics(days=days)

        # Calculate summary stats
        summary = {
            'total_queries': 0,
            'total_cost': 0,
            'avg_success_rate': 0,
            'avg_test_coverage': 0,
            'avg_doc_coverage': 0,
            'active_users': 0,
            'last_updated': datetime.now().isoformat()
        }

        # Query performance
        if metrics.get('query_performance'):
            summary['total_queries'] = sum(
                r.value.get('query_count', 0)
                for r in metrics['query_performance']
            )

        # Costs
        if metrics.get('costs'):
            summary['total_cost'] = sum(
                r.value.get('cost_usd', 0)
                for r in metrics['costs']
            )

        # Pipeline success
        if metrics.get('pipeline_success'):
            success_rates = [
                r.value.get('success_rate', 0)
                for r in metrics['pipeline_success']
                if r.value.get('job_count', 0) > 0
            ]
            summary['avg_success_rate'] = (
                sum(success_rates) / len(success_rates)
                if success_rates else 0
            )

        # Test coverage
        if metrics.get('test_coverage'):
            coverage_values = [
                r.value.get('coverage_percentage', 0)
                for r in metrics['test_coverage']
            ]
            summary['avg_test_coverage'] = (
                sum(coverage_values) / len(coverage_values)
                if coverage_values else 0
            )

        # Documentation
        if metrics.get('documentation'):
            doc_values = [
                r.value.get('column_doc_percentage', 0)
                for r in metrics['documentation']
            ]
            summary['avg_doc_coverage'] = (
                sum(doc_values) / len(doc_values)
                if doc_values else 0
            )

        # Contributions
        if metrics.get('contributions'):
            summary['active_users'] = len(metrics['contributions'])

        return jsonify(summary)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def main():
    """CLI entry point"""
    global collector, default_days

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--port', type=int, default=5000, help='Port to run the dashboard')
    parser.add_argument('--days', type=int, default=30, help='Number of days of data to show')
    parser.add_argument('--project-id', type=str, help='GCP project ID')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')

    args = parser.parse_args()

    # Initialize global collector
    collector = TeamMetricsCollector(project_id=args.project_id)
    default_days = args.days

    print(f"Starting Team Metrics Dashboard on port {args.port}...")
    print(f"Open http://localhost:{args.port} in your browser")

    app.run(host='0.0.0.0', port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
