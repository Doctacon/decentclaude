#!/usr/bin/env python3
"""
migration-report.py - Generate comprehensive migration assessment and progress reports

This utility generates detailed reports for migration planning and tracking,
including effort estimates, cost savings projections, and progress metrics.

Usage:
  migration-report.py --mode=assessment [--output-report <file>]
  migration-report.py --mode=progress --baseline <file> [--output-report <file>]

Examples:
  # Initial assessment
  migration-report.py --mode=assessment --output-report migration-assessment.html

  # Track progress (run weekly)
  migration-report.py --mode=progress --baseline migration-baseline.json --output-report week-2-progress.html
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from collections import defaultdict


class MigrationReporter:
    """Generate migration assessment and progress reports"""

    def __init__(self):
        self.phases = self._define_phases()
        self.metrics = {}

    def _define_phases(self) -> List[Dict]:
        """Define migration phases"""
        return [
            {
                'name': 'Phase 1: Read-Only Operations',
                'duration': '2 weeks',
                'effort': 'LOW',
                'risk': 'LOW',
                'activities': [
                    'Install utilities on dev machines',
                    'Team training (1-hour workshop)',
                    'Parallel run of profiling tools',
                    'Output validation and comparison',
                    'Knowledge base setup'
                ],
                'success_criteria': [
                    'All team members trained',
                    'Utilities running in parallel for 1 week',
                    'No output discrepancies',
                    'Team satisfaction >80%'
                ],
                'deliverables': [
                    'Installed utilities',
                    'Training materials',
                    'Validation reports',
                    'Team feedback'
                ]
            },
            {
                'name': 'Phase 2: Quality Checks and Monitoring',
                'duration': '2 weeks',
                'effort': 'MEDIUM',
                'risk': 'LOW',
                'activities': [
                    'Map existing quality checks to utilities',
                    'Create validation scripts',
                    'Integrate with CI/CD',
                    'Set up alerting',
                    'Parallel run quality checks'
                ],
                'success_criteria': [
                    '80% of quality checks migrated',
                    'CI/CD integration complete',
                    'Check runtime reduced >50%',
                    'No false positives'
                ],
                'deliverables': [
                    'Validation scripts',
                    'CI/CD configuration',
                    'Alert configurations',
                    'Quality metrics'
                ]
            },
            {
                'name': 'Phase 3: Full CI/CD Integration',
                'duration': '2 weeks',
                'effort': 'MEDIUM',
                'risk': 'MEDIUM',
                'activities': [
                    'Add cost gates to PR checks',
                    'Schema diff in deployment',
                    'Scheduled profiling setup',
                    'Observability dashboard',
                    'Documentation automation'
                ],
                'success_criteria': [
                    'All workflows migrated',
                    'Cost gates active',
                    'Schema validation working',
                    'Zero migration incidents'
                ],
                'deliverables': [
                    'Updated CI/CD pipelines',
                    'Cost monitoring',
                    'Schema validation',
                    'Dashboards'
                ]
            },
            {
                'name': 'Phase 4: Decommission Legacy Tools',
                'duration': '2 weeks',
                'effort': 'LOW',
                'risk': 'LOW',
                'activities': [
                    'Verify complete migration',
                    'Archive legacy scripts',
                    'Update documentation',
                    'Migration retrospective',
                    'Success measurement'
                ],
                'success_criteria': [
                    'Legacy usage at 0%',
                    'All docs updated',
                    'Cost savings validated',
                    'Retrospective complete'
                ],
                'deliverables': [
                    'Archived scripts',
                    'Updated documentation',
                    'Retrospective report',
                    'Success metrics'
                ]
            }
        ]

    def generate_assessment(self, analysis_file: Optional[Path] = None) -> Dict:
        """Generate initial migration assessment"""
        assessment = {
            'assessment_date': datetime.now().isoformat(),
            'timeline': {
                'total_duration': '8 weeks',
                'start_date': datetime.now().isoformat(),
                'end_date': (datetime.now() + timedelta(weeks=8)).isoformat()
            },
            'phases': self.phases,
            'effort_estimate': {
                'total_hours': 160,
                'by_role': {
                    'Data Engineer': 100,
                    'DevOps Engineer': 40,
                    'Data Analyst': 20
                }
            },
            'cost_savings': {
                'monthly_savings': {
                    'query_costs': 125,  # $125/month
                    'api_costs': 50,     # $50/month
                    'engineering_time': 320  # 20 hours * $16/hour
                },
                'annual_savings': 5940,  # (125 + 50 + 320) * 12
                'roi_months': 1.3  # 160 hours * $50/hour / 5940 annual
            },
            'risks': [
                {
                    'risk': 'Team resistance to change',
                    'probability': 'MEDIUM',
                    'impact': 'MEDIUM',
                    'mitigation': 'Hands-on training, clear benefits communication, incremental adoption'
                },
                {
                    'risk': 'Output parity issues',
                    'probability': 'LOW',
                    'impact': 'HIGH',
                    'mitigation': 'Parallel run period, automated validation, rollback plan'
                },
                {
                    'risk': 'CI/CD integration breaks',
                    'probability': 'LOW',
                    'impact': 'MEDIUM',
                    'mitigation': 'Test in staging first, gradual rollout, monitoring'
                }
            ],
            'success_metrics': {
                'api_calls_reduction': '60%',
                'query_cost_reduction': '25%',
                'quality_check_speedup': '70%',
                'documentation_freshness': '< 24 hours',
                'team_satisfaction': '> 80%'
            }
        }

        # If analysis file provided, incorporate its data
        if analysis_file and analysis_file.exists():
            with open(analysis_file, 'r') as f:
                analysis = json.load(f)

            # Update estimates based on analysis
            candidates = analysis.get('migration_candidates', [])
            if candidates:
                # Adjust effort based on number of high-priority candidates
                high_priority = sum(1 for c in candidates if c.get('priority') == 'HIGH')
                assessment['effort_estimate']['total_hours'] += high_priority * 4

                # Update timeline if needed
                if high_priority > 20:
                    assessment['timeline']['total_duration'] = '10 weeks'
                    assessment['timeline']['end_date'] = (datetime.now() + timedelta(weeks=10)).isoformat()

        return assessment

    def generate_progress_report(self, baseline_file: Path, current_metrics: Optional[Dict] = None) -> Dict:
        """Generate progress report against baseline"""
        if not baseline_file.exists():
            raise FileNotFoundError(f"Baseline file not found: {baseline_file}")

        with open(baseline_file, 'r') as f:
            baseline = json.load(f)

        # If current metrics not provided, collect them
        if not current_metrics:
            current_metrics = self._collect_current_metrics()

        # Calculate progress
        progress = {
            'report_date': datetime.now().isoformat(),
            'baseline_date': baseline.get('date', 'Unknown'),
            'metrics_comparison': self._compare_metrics(baseline, current_metrics),
            'phase_completion': self._estimate_phase_completion(current_metrics),
            'recommendations': self._generate_recommendations(baseline, current_metrics)
        }

        return progress

    def _collect_current_metrics(self) -> Dict:
        """Collect current metrics (placeholder - would integrate with actual systems)"""
        # In production, this would query actual systems
        # For now, return placeholder data
        return {
            'date': datetime.now().isoformat(),
            'legacy_scripts': 25,  # Down from baseline
            'utility_usage': 180,  # Up from 0
            'monthly_query_costs': 375,  # Down from baseline
            'api_calls_per_day': 180,  # Down from baseline
            'profile_time_seconds': 8,  # Down from baseline
            'quality_check_time_minutes': 15  # Down from baseline
        }

    def _compare_metrics(self, baseline: Dict, current: Dict) -> Dict:
        """Compare current metrics against baseline"""
        comparisons = {}

        metrics_to_compare = [
            ('legacy_scripts', 'fewer is better'),
            ('monthly_query_costs', 'fewer is better'),
            ('api_calls_per_day', 'fewer is better'),
            ('profile_time_seconds', 'fewer is better')
        ]

        for metric, direction in metrics_to_compare:
            if metric in baseline and metric in current:
                baseline_val = baseline[metric]
                current_val = current[metric]

                if baseline_val == 0:
                    change_pct = 0
                else:
                    change_pct = ((current_val - baseline_val) / baseline_val) * 100

                # Determine if change is good
                if direction == 'fewer is better':
                    is_improvement = change_pct < 0
                else:
                    is_improvement = change_pct > 0

                comparisons[metric] = {
                    'baseline': baseline_val,
                    'current': current_val,
                    'change_percent': round(change_pct, 1),
                    'is_improvement': is_improvement,
                    'status': 'on_track' if is_improvement else 'needs_attention'
                }

        return comparisons

    def _estimate_phase_completion(self, current_metrics: Dict) -> List[Dict]:
        """Estimate completion percentage for each phase"""
        # Simplified estimation based on metrics
        # In production, this would track actual checklist items

        utility_usage = current_metrics.get('utility_usage', 0)
        legacy_scripts = current_metrics.get('legacy_scripts', 100)

        # Rough estimation
        migration_percent = (utility_usage / max(utility_usage + legacy_scripts, 1)) * 100

        phase_completion = []
        for i, phase in enumerate(self.phases):
            if migration_percent > 75:
                completion = 100 if i < 4 else 80
            elif migration_percent > 50:
                completion = 100 if i < 3 else 60 if i == 2 else 40
            elif migration_percent > 25:
                completion = 100 if i < 2 else 70 if i == 1 else 30
            else:
                completion = 80 if i == 0 else 20 if i == 1 else 0

            phase_completion.append({
                'phase': phase['name'],
                'completion_percent': completion,
                'status': 'complete' if completion == 100 else 'in_progress' if completion > 0 else 'not_started'
            })

        return phase_completion

    def _generate_recommendations(self, baseline: Dict, current: Dict) -> List[str]:
        """Generate recommendations based on progress"""
        recommendations = []

        # Check if legacy usage is decreasing
        if current.get('legacy_scripts', 0) >= baseline.get('legacy_scripts', 0):
            recommendations.append(
                "Legacy script usage not decreasing. Review team adoption and provide additional training."
            )

        # Check if costs are improving
        if current.get('monthly_query_costs', 0) >= baseline.get('monthly_query_costs', 0):
            recommendations.append(
                "Query costs not improving. Ensure bq-optimize recommendations are being implemented."
            )

        # Check API call reduction
        baseline_api = baseline.get('api_calls_per_day', 0)
        current_api = current.get('api_calls_per_day', 0)
        if baseline_api > 0 and current_api > baseline_api * 0.6:
            recommendations.append(
                "API calls not reducing as expected. Verify metadata caching is enabled in utilities."
            )

        if not recommendations:
            recommendations.append(
                "Migration on track! Continue with current pace and monitor metrics weekly."
            )

        return recommendations

    def generate_html_assessment(self, assessment: Dict, output_path: Path) -> None:
        """Generate HTML assessment report"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Migration Assessment Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .section {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .timeline {{
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
            padding: 20px;
            background: linear-gradient(to right, #e3f2fd, #bbdefb);
            border-radius: 8px;
        }}
        .timeline-item {{
            text-align: center;
        }}
        .timeline-label {{
            font-weight: bold;
            color: #1565c0;
        }}
        .phase {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 5px solid #2196F3;
        }}
        .phase h3 {{
            margin-top: 0;
            color: #1976d2;
        }}
        .effort-LOW {{ border-left-color: #4CAF50; }}
        .effort-MEDIUM {{ border-left-color: #FF9800; }}
        .effort-HIGH {{ border-left-color: #f44336; }}
        .risk-LOW {{ background-color: #e8f5e9; }}
        .risk-MEDIUM {{ background-color: #fff3e0; }}
        .risk-HIGH {{ background-color: #ffebee; }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .stat {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
            font-size: 0.9em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #2196F3;
            color: white;
        }}
        .checklist {{
            list-style: none;
            padding: 0;
        }}
        .checklist li {{
            padding: 8px;
            margin: 5px 0;
            background: #f5f5f5;
            border-radius: 4px;
        }}
        .checklist li:before {{
            content: "☐ ";
            font-size: 1.2em;
            margin-right: 8px;
        }}
    </style>
</head>
<body>
    <h1>Migration Assessment: Legacy Tools to DecentClaude</h1>

    <div class="section">
        <h2>Executive Summary</h2>
        <p><strong>Assessment Date:</strong> {assessment['assessment_date'][:10]}</p>

        <div class="timeline">
            <div class="timeline-item">
                <div class="timeline-label">Duration</div>
                <div>{assessment['timeline']['total_duration']}</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-label">Effort</div>
                <div>{assessment['effort_estimate']['total_hours']} hours</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-label">ROI</div>
                <div>{assessment['cost_savings']['roi_months']:.1f} months</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-label">Annual Savings</div>
                <div>${assessment['cost_savings']['annual_savings']:,.0f}</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Cost Savings Projection</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">${assessment['cost_savings']['monthly_savings']['query_costs']}</div>
                <div class="stat-label">Query Cost Savings/Month</div>
            </div>
            <div class="stat">
                <div class="stat-value">${assessment['cost_savings']['monthly_savings']['api_costs']}</div>
                <div class="stat-label">API Cost Savings/Month</div>
            </div>
            <div class="stat">
                <div class="stat-value">${assessment['cost_savings']['monthly_savings']['engineering_time']}</div>
                <div class="stat-label">Time Savings/Month</div>
            </div>
            <div class="stat">
                <div class="stat-value">${assessment['cost_savings']['annual_savings']:,.0f}</div>
                <div class="stat-label">Total Annual Savings</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Migration Phases</h2>
"""

        for i, phase in enumerate(assessment['phases'], 1):
            html += f"""
        <div class="phase effort-{phase['effort']}">
            <h3>{i}. {phase['name']}</h3>
            <p><strong>Duration:</strong> {phase['duration']} |
               <strong>Effort:</strong> {phase['effort']} |
               <strong>Risk:</strong> {phase['risk']}</p>

            <h4>Activities</h4>
            <ul>
"""
            for activity in phase['activities']:
                html += f"                <li>{activity}</li>\n"

            html += f"""
            </ul>

            <h4>Success Criteria</h4>
            <ul class="checklist">
"""
            for criterion in phase['success_criteria']:
                html += f"                <li>{criterion}</li>\n"

            html += """
            </ul>
        </div>
"""

        html += """
    </div>

    <div class="section">
        <h2>Risk Assessment</h2>
        <table>
            <tr>
                <th>Risk</th>
                <th>Probability</th>
                <th>Impact</th>
                <th>Mitigation</th>
            </tr>
"""

        for risk in assessment['risks']:
            html += f"""
            <tr>
                <td>{risk['risk']}</td>
                <td><span class="risk-{risk['probability']}">{risk['probability']}</span></td>
                <td><span class="risk-{risk['impact']}">{risk['impact']}</span></td>
                <td>{risk['mitigation']}</td>
            </tr>
"""

        html += """
        </table>
    </div>

    <div class="section">
        <h2>Success Metrics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Target</th>
            </tr>
"""

        for metric, target in assessment['success_metrics'].items():
            html += f"""
            <tr>
                <td>{metric.replace('_', ' ').title()}</td>
                <td>{target}</td>
            </tr>
"""

        html += """
        </table>
    </div>

    <div class="section">
        <h2>Team Training Requirements</h2>
        <ul>
            <li><strong>1-hour workshop:</strong> DecentClaude utilities overview</li>
            <li><strong>Hands-on session:</strong> Migrating first script</li>
            <li><strong>Office hours:</strong> Daily for first 2 weeks</li>
            <li><strong>Documentation:</strong> Command aliases, migration guide</li>
        </ul>
    </div>

    <div class="section">
        <h2>Next Steps</h2>
        <ol>
            <li>Review assessment with team and stakeholders</li>
            <li>Get approval and resource allocation</li>
            <li>Schedule Phase 1 kickoff</li>
            <li>Set up baseline metrics tracking</li>
            <li>Begin with read-only operations</li>
        </ol>
    </div>

    <p><em>For detailed migration steps, see docs/guides/MIGRATION.md</em></p>
</body>
</html>
"""

        with open(output_path, 'w') as f:
            f.write(html)

        print(f"Assessment report generated: {output_path}")

    def generate_html_progress(self, progress: Dict, output_path: Path) -> None:
        """Generate HTML progress report"""
        # Similar to assessment but focused on progress tracking
        # Implementation similar to above but with progress-specific content
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Migration Progress Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        .section {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-comparison {{ margin: 15px 0; padding: 15px; background: #f9f9f9; border-radius: 4px; }}
        .improvement {{ color: #4CAF50; font-weight: bold; }}
        .needs-attention {{ color: #f44336; font-weight: bold; }}
        .progress-bar {{ background: #e0e0e0; border-radius: 4px; height: 24px; margin: 10px 0; position: relative; }}
        .progress-fill {{ background: #4CAF50; height: 100%; border-radius: 4px; transition: width 0.3s; }}
        .progress-text {{ position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Migration Progress Report</h1>

    <div class="section">
        <h2>Progress Summary</h2>
        <p><strong>Report Date:</strong> {progress['report_date'][:10]}</p>
        <p><strong>Baseline Date:</strong> {progress['baseline_date'][:10]}</p>

        <h3>Metrics Comparison</h3>
"""

        for metric, comparison in progress['metrics_comparison'].items():
            status_class = 'improvement' if comparison['is_improvement'] else 'needs-attention'
            change_symbol = '↓' if comparison['change_percent'] < 0 else '↑'

            html += f"""
        <div class="metric-comparison">
            <strong>{metric.replace('_', ' ').title()}</strong><br>
            Baseline: {comparison['baseline']} → Current: {comparison['current']}
            <span class="{status_class}">
                {change_symbol} {abs(comparison['change_percent']):.1f}%
            </span>
        </div>
"""

        html += """
        <h3>Phase Completion</h3>
"""

        for phase in progress['phase_completion']:
            html += f"""
        <div>
            <strong>{phase['phase']}</strong>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {phase['completion_percent']}%"></div>
                <div class="progress-text">{phase['completion_percent']}%</div>
            </div>
        </div>
"""

        html += """
    </div>

    <div class="section">
        <h2>Recommendations</h2>
        <ul>
"""

        for rec in progress['recommendations']:
            html += f"            <li>{rec}</li>\n"

        html += """
        </ul>
    </div>
</body>
</html>
"""

        with open(output_path, 'w') as f:
            f.write(html)

        print(f"Progress report generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate migration assessment and progress reports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--mode',
        required=True,
        choices=['assessment', 'progress'],
        help='Report mode: assessment (initial) or progress (tracking)'
    )

    parser.add_argument(
        '--baseline',
        type=Path,
        help='Baseline metrics file (required for progress mode)'
    )

    parser.add_argument(
        '--analysis',
        type=Path,
        help='Analysis file from analyze-legacy-usage.py (optional for assessment)'
    )

    parser.add_argument(
        '--output-report',
        type=Path,
        default=Path('migration-report.html'),
        help='Output HTML report file'
    )

    parser.add_argument(
        '--output-json',
        type=Path,
        help='Also output JSON for programmatic processing'
    )

    args = parser.parse_args()

    reporter = MigrationReporter()

    if args.mode == 'assessment':
        # Generate assessment
        assessment = reporter.generate_assessment(args.analysis)

        if args.output_json:
            with open(args.output_json, 'w') as f:
                json.dump(assessment, f, indent=2)
            print(f"JSON output saved: {args.output_json}")

        reporter.generate_html_assessment(assessment, args.output_report)

    elif args.mode == 'progress':
        if not args.baseline:
            parser.error("--baseline is required for progress mode")

        # Generate progress report
        progress = reporter.generate_progress_report(args.baseline)

        if args.output_json:
            with open(args.output_json, 'w') as f:
                json.dump(progress, f, indent=2)
            print(f"JSON output saved: {args.output_json}")

        reporter.generate_html_progress(progress, args.output_report)


if __name__ == '__main__':
    main()
