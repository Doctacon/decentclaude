#!/usr/bin/env python3
"""
analyze-legacy-usage.py - Analyze existing BigQuery usage patterns

This utility scans codebases for BigQuery usage (bq CLI, Python client, etc.)
and generates a comprehensive report for migration planning.

Usage:
  analyze-legacy-usage.py --scan-dir <dir> [--output-json <file>] [--output-report <file>]

Examples:
  analyze-legacy-usage.py --scan-dir scripts/
  analyze-legacy-usage.py --scan-dir scripts/ --scan-dir airflow/dags/ --output-report report.html
  analyze-legacy-usage.py --scan-dir . --type great-expectations --output ge-audit.json
"""

import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional
from datetime import datetime
from collections import defaultdict, Counter
import json


class UsagePattern:
    """Pattern for detecting specific usage types"""

    def __init__(self, name: str, pattern: str, description: str, category: str):
        self.name = name
        self.pattern = re.compile(pattern)
        self.description = description
        self.category = category

    def match(self, content: str) -> List[str]:
        """Find all matches in content"""
        return self.pattern.findall(content)


class LegacyUsageAnalyzer:
    """Analyzes legacy BigQuery usage patterns"""

    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.results = defaultdict(list)
        self.stats = Counter()

    def _initialize_patterns(self) -> List[UsagePattern]:
        """Initialize detection patterns"""
        return [
            # BQ CLI Commands
            UsagePattern(
                'bq_query',
                r'bq\s+query\s+',
                'bq query command',
                'bq_cli'
            ),
            UsagePattern(
                'bq_show',
                r'bq\s+show\s+',
                'bq show command (table metadata)',
                'bq_cli'
            ),
            UsagePattern(
                'bq_ls',
                r'bq\s+ls\s+',
                'bq ls command (list tables)',
                'bq_cli'
            ),
            UsagePattern(
                'bq_mk',
                r'bq\s+mk\s+',
                'bq mk command (create table)',
                'bq_cli'
            ),
            UsagePattern(
                'bq_load',
                r'bq\s+load\s+',
                'bq load command (load data)',
                'bq_cli'
            ),
            UsagePattern(
                'bq_extract',
                r'bq\s+extract\s+',
                'bq extract command (export data)',
                'bq_cli'
            ),
            UsagePattern(
                'bq_dry_run',
                r'bq\s+query\s+--dry[_-]run',
                'bq query with dry_run (cost estimation)',
                'bq_cli'
            ),

            # Python BigQuery Client
            UsagePattern(
                'bigquery_client',
                r'from\s+google\.cloud\s+import\s+bigquery|import\s+google\.cloud\.bigquery',
                'Python BigQuery client import',
                'python'
            ),
            UsagePattern(
                'bigquery_client_init',
                r'bigquery\.Client\(',
                'BigQuery Client initialization',
                'python'
            ),
            UsagePattern(
                'get_table',
                r'\.get_table\(',
                'client.get_table() call',
                'python'
            ),
            UsagePattern(
                'query_method',
                r'\.query\(',
                'client.query() call',
                'python'
            ),
            UsagePattern(
                'dry_run_config',
                r'dry_run\s*=\s*True',
                'QueryJobConfig with dry_run',
                'python'
            ),
            UsagePattern(
                'list_tables',
                r'\.list_tables\(',
                'client.list_tables() call',
                'python'
            ),

            # Great Expectations
            UsagePattern(
                'great_expectations_import',
                r'import\s+great_expectations|from\s+great_expectations',
                'Great Expectations import',
                'data_quality'
            ),
            UsagePattern(
                'ge_checkpoint',
                r'\.run_checkpoint\(',
                'Great Expectations checkpoint',
                'data_quality'
            ),
            UsagePattern(
                'ge_expectation',
                r'expect_column_',
                'Great Expectations expectation',
                'data_quality'
            ),

            # Custom Data Quality Patterns
            UsagePattern(
                'null_check',
                r'IS\s+NULL|COUNTIF\(.*IS\s+NULL\)',
                'NULL value check in SQL',
                'data_quality'
            ),
            UsagePattern(
                'uniqueness_check',
                r'COUNT\(DISTINCT|GROUP\s+BY.*HAVING\s+COUNT\(\*\)\s*>\s*1',
                'Uniqueness/duplicate check in SQL',
                'data_quality'
            ),
            UsagePattern(
                'row_count',
                r'SELECT\s+COUNT\(\*\)',
                'Row count query',
                'data_quality'
            ),

            # Schema Management
            UsagePattern(
                'schema_json',
                r'--schema\s+.*\.json|\.schema\s*=',
                'Schema JSON file reference',
                'schema'
            ),
            UsagePattern(
                'diff_schemas',
                r'diff\s+.*schema',
                'Schema comparison with diff',
                'schema'
            ),

            # Cost/Performance Patterns
            UsagePattern(
                'total_bytes_processed',
                r'total_bytes_processed',
                'Query cost calculation',
                'cost'
            ),
            UsagePattern(
                'cost_calculation',
                r'\$?\d+\.?\d*\s*/\s*TB|\*\s*5\.00',
                'Manual cost calculation',
                'cost'
            ),
        ]

    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze a single file for BigQuery usage"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            return {
                'file': str(file_path),
                'error': str(e),
                'matches': []
            }

        matches = []
        match_count = Counter()

        for pattern in self.patterns:
            pattern_matches = pattern.match(content)
            if pattern_matches:
                matches.append({
                    'name': pattern.name,
                    'description': pattern.description,
                    'category': pattern.category,
                    'count': len(pattern_matches),
                    'samples': pattern_matches[:3]  # First 3 samples
                })
                match_count[pattern.category] += len(pattern_matches)
                self.stats[pattern.name] += len(pattern_matches)

        return {
            'file': str(file_path),
            'matches': matches,
            'match_count': dict(match_count),
            'total_matches': sum(match_count.values())
        }

    def scan_directory(self, directory: Path, extensions: List[str]) -> None:
        """Scan directory for files and analyze them"""
        print(f"Scanning directory: {directory}")

        for ext in extensions:
            pattern = f"**/*{ext}"
            for file_path in directory.glob(pattern):
                if file_path.is_file():
                    result = self.analyze_file(file_path)
                    if result.get('total_matches', 0) > 0:
                        self.results[ext].append(result)

    def generate_summary(self) -> Dict:
        """Generate summary statistics"""
        all_files = [f for files in self.results.values() for f in files]

        # Count unique files
        files_with_matches = len(all_files)

        # Count by category
        category_counts = Counter()
        for file_result in all_files:
            for match in file_result.get('matches', []):
                category_counts[match['category']] += match['count']

        # Identify high-priority migrations
        migration_candidates = []
        for file_result in all_files:
            if file_result.get('total_matches', 0) >= 3:
                priority = self._calculate_priority(file_result)
                migration_candidates.append({
                    'file': file_result['file'],
                    'priority': priority,
                    'matches': file_result['total_matches'],
                    'categories': file_result.get('match_count', {}),
                    'suggested_utility': self._suggest_utility(file_result),
                    'complexity': self._estimate_complexity(file_result)
                })

        # Sort by priority
        migration_candidates.sort(key=lambda x: (
            {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}.get(x['priority'], 0),
            x['matches']
        ), reverse=True)

        return {
            'scan_date': datetime.now().isoformat(),
            'summary': {
                'total_files_scanned': sum(len(files) for files in self.results.values()),
                'files_with_bq_usage': files_with_matches,
                'total_matches': sum(self.stats.values()),
                'categories': dict(category_counts)
            },
            'pattern_stats': dict(self.stats.most_common()),
            'migration_candidates': migration_candidates[:20]  # Top 20
        }

    def _calculate_priority(self, file_result: Dict) -> str:
        """Calculate migration priority based on usage patterns"""
        match_count = file_result.get('total_matches', 0)
        categories = file_result.get('match_count', {})

        # High priority if:
        # - Many matches (>10)
        # - Has cost calculation patterns
        # - Has data quality checks
        # - Has dry_run patterns (easy to migrate to bq-query-cost)

        if match_count > 10:
            return 'HIGH'
        if 'cost' in categories or 'data_quality' in categories:
            return 'HIGH'
        if match_count > 5:
            return 'MEDIUM'
        return 'LOW'

    def _suggest_utility(self, file_result: Dict) -> str:
        """Suggest appropriate DecentClaude utility"""
        categories = file_result.get('match_count', {})

        suggestions = []

        if categories.get('cost', 0) > 0:
            suggestions.append('bq-query-cost')
        if categories.get('data_quality', 0) > 0:
            suggestions.append('bq-profile (with quality checks)')
        if categories.get('schema', 0) > 0:
            suggestions.append('bq-schema-diff')

        # Check specific patterns
        for match in file_result.get('matches', []):
            if match['name'] == 'bq_show':
                suggestions.append('bq-profile')
            elif match['name'] == 'bq_ls':
                suggestions.append('bq-explore')
            elif match['name'] in ['bq_dry_run', 'dry_run_config']:
                suggestions.append('bq-query-cost')

        # Deduplicate and return
        unique_suggestions = list(dict.fromkeys(suggestions))
        return ', '.join(unique_suggestions) if unique_suggestions else 'bq-profile'

    def _estimate_complexity(self, file_result: Dict) -> str:
        """Estimate migration complexity"""
        match_count = file_result.get('total_matches', 0)
        categories = len(file_result.get('match_count', {}))

        # Complex if:
        # - Many matches across multiple categories
        # - Great Expectations (requires mapping expectations)
        # - Custom cost calculations (needs validation)

        has_ge = any(m['name'].startswith('ge_') for m in file_result.get('matches', []))

        if has_ge or (match_count > 15 and categories > 2):
            return 'HIGH'
        if match_count > 8 or categories > 1:
            return 'MEDIUM'
        return 'LOW'

    def generate_html_report(self, summary: Dict, output_path: Path) -> None:
        """Generate HTML report"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Legacy BigQuery Usage Analysis</title>
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
            border-bottom: 3px solid #2196F3;
            padding-bottom: 10px;
        }}
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
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
            color: #2196F3;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .candidate {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 5px solid #FF9800;
        }}
        .candidate.priority-HIGH {{
            border-left-color: #f44336;
        }}
        .candidate.priority-MEDIUM {{
            border-left-color: #FF9800;
        }}
        .candidate.priority-LOW {{
            border-left-color: #4CAF50;
        }}
        .priority {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.9em;
            color: white;
        }}
        .priority-HIGH {{
            background-color: #f44336;
        }}
        .priority-MEDIUM {{
            background-color: #FF9800;
        }}
        .priority-LOW {{
            background-color: #4CAF50;
        }}
        .complexity {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.9em;
            margin-left: 10px;
        }}
        .complexity-HIGH {{
            background-color: #ffebee;
            color: #c62828;
        }}
        .complexity-MEDIUM {{
            background-color: #fff3e0;
            color: #e65100;
        }}
        .complexity-LOW {{
            background-color: #e8f5e9;
            color: #2e7d32;
        }}
        .utility {{
            background: #e3f2fd;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            color: #1565c0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
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
        tr:hover {{
            background-color: #f5f5f5;
        }}
    </style>
</head>
<body>
    <h1>Legacy BigQuery Usage Analysis</h1>

    <div class="summary">
        <h2>Executive Summary</h2>
        <p><strong>Report Generated:</strong> {summary['scan_date']}</p>

        <div class="stats">
            <div class="stat">
                <div class="stat-value">{summary['summary']['total_files_scanned']}</div>
                <div class="stat-label">Files Scanned</div>
            </div>
            <div class="stat">
                <div class="stat-value">{summary['summary']['files_with_bq_usage']}</div>
                <div class="stat-label">Files with BQ Usage</div>
            </div>
            <div class="stat">
                <div class="stat-value">{summary['summary']['total_matches']}</div>
                <div class="stat-label">Total Usage Patterns</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(summary['migration_candidates'])}</div>
                <div class="stat-label">Migration Candidates</div>
            </div>
        </div>

        <h3>Usage by Category</h3>
        <table>
            <tr>
                <th>Category</th>
                <th>Count</th>
                <th>Recommended Utility</th>
            </tr>
"""

        category_utility_map = {
            'bq_cli': 'Various (bq-profile, bq-query-cost, etc.)',
            'python': 'bq-profile, bq_cache library',
            'data_quality': 'bq-profile with quality checks',
            'schema': 'bq-schema-diff',
            'cost': 'bq-query-cost, bq-cost-report'
        }

        for category, count in summary['summary']['categories'].items():
            utility = category_utility_map.get(category, 'See documentation')
            html += f"""
            <tr>
                <td>{category}</td>
                <td>{count}</td>
                <td>{utility}</td>
            </tr>
"""

        html += """
        </table>
    </div>

    <h2>Top Migration Candidates</h2>
    <p>Files prioritized by impact and ease of migration</p>
"""

        for candidate in summary['migration_candidates']:
            html += f"""
    <div class="candidate priority-{candidate['priority']}">
        <h3>{candidate['file']}</h3>
        <div>
            <span class="priority priority-{candidate['priority']}">{candidate['priority']} PRIORITY</span>
            <span class="complexity complexity-{candidate['complexity']}">{candidate['complexity']} COMPLEXITY</span>
        </div>

        <p><strong>Matches:</strong> {candidate['matches']} BigQuery usage patterns</p>

        <p><strong>Categories:</strong>
"""
            for cat, count in candidate['categories'].items():
                html += f"<span style='margin-right:10px'>{cat}: {count}</span>"

            html += f"""
        </p>

        <div class="utility">
            <strong>Suggested Utility:</strong> {candidate['suggested_utility']}
        </div>

        <p><strong>Migration Steps:</strong></p>
        <ol>
"""
            # Generate migration steps based on patterns
            if 'cost' in candidate['categories']:
                html += "<li>Replace cost calculations with <code>bq-query-cost</code></li>\n"
            if 'data_quality' in candidate['categories']:
                html += "<li>Replace quality checks with <code>bq-profile</code></li>\n"
            if 'bq_cli' in candidate['categories']:
                html += "<li>Replace bq CLI commands with corresponding utilities</li>\n"
            html += "<li>Test output parity</li>\n"
            html += "<li>Update CI/CD pipelines</li>\n"
            html += "<li>Archive legacy script</li>\n"

            html += """
        </ol>
    </div>
"""

        html += """
    <h2>Pattern Statistics</h2>
    <table>
        <tr>
            <th>Pattern</th>
            <th>Occurrences</th>
        </tr>
"""

        for pattern, count in sorted(summary['pattern_stats'].items(), key=lambda x: x[1], reverse=True)[:15]:
            html += f"""
        <tr>
            <td>{pattern}</td>
            <td>{count}</td>
        </tr>
"""

        html += """
    </table>

    <h2>Next Steps</h2>
    <ol>
        <li>Review top migration candidates</li>
        <li>Prioritize based on team capacity and impact</li>
        <li>Use <code>convert-bq-script.py</code> for automated conversion</li>
        <li>Create migration timeline with <code>migration-report.py</code></li>
        <li>Begin with Phase 1 (read-only operations)</li>
    </ol>

    <p><em>For detailed migration guidance, see docs/guides/MIGRATION.md</em></p>
</body>
</html>
"""

        with open(output_path, 'w') as f:
            f.write(html)

        print(f"HTML report generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze existing BigQuery usage patterns for migration planning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--scan-dir',
        action='append',
        dest='scan_dirs',
        required=True,
        help='Directory to scan (can specify multiple times)'
    )

    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.py', '.sh', '.bash', '.sql'],
        help='File extensions to scan (default: .py .sh .bash .sql)'
    )

    parser.add_argument(
        '--output-json',
        help='Output JSON file for programmatic processing'
    )

    parser.add_argument(
        '--output-report',
        help='Output HTML report file'
    )

    parser.add_argument(
        '--type',
        choices=['all', 'bq-cli', 'python', 'great-expectations'],
        default='all',
        help='Type of usage to analyze'
    )

    args = parser.parse_args()

    analyzer = LegacyUsageAnalyzer()

    # Scan all directories
    for scan_dir in args.scan_dirs:
        path = Path(scan_dir)
        if not path.exists():
            print(f"Warning: Directory not found: {scan_dir}", file=sys.stderr)
            continue
        analyzer.scan_directory(path, args.extensions)

    # Generate summary
    summary = analyzer.generate_summary()

    # Output JSON
    if args.output_json:
        json_path = Path(args.output_json)
        with open(json_path, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"JSON output saved: {json_path}")

    # Output HTML report
    if args.output_report:
        report_path = Path(args.output_report)
        analyzer.generate_html_report(summary, report_path)

    # Print summary to console
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    print(f"Files scanned: {summary['summary']['total_files_scanned']}")
    print(f"Files with BQ usage: {summary['summary']['files_with_bq_usage']}")
    print(f"Total usage patterns: {summary['summary']['total_matches']}")
    print(f"\nTop migration candidates: {len(summary['migration_candidates'])}")

    for i, candidate in enumerate(summary['migration_candidates'][:5], 1):
        print(f"\n{i}. {candidate['file']}")
        print(f"   Priority: {candidate['priority']} | Complexity: {candidate['complexity']}")
        print(f"   Suggested: {candidate['suggested_utility']}")


if __name__ == '__main__':
    main()
