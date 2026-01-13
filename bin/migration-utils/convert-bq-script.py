#!/usr/bin/env python3
"""
convert-bq-script.py - Convert legacy bq CLI scripts to DecentClaude utilities

This utility analyzes legacy shell scripts that use the `bq` CLI and suggests
equivalent DecentClaude utilities. It can also automatically convert simple
scripts to use the new utilities.

Usage:
  convert-bq-script.py --input <script> [--output <script>] [--suggest-utility]

Examples:
  convert-bq-script.py --input legacy_profiler.sh --suggest-utility
  convert-bq-script.py --input legacy_profiler.sh --output migrated_profiler.sh
  convert-bq-script.py --input scripts/ --scan-all --report conversion-report.html
"""

import sys
import re
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json

class BQCommandPattern:
    """Pattern for detecting and converting bq CLI commands"""

    def __init__(self, pattern: str, utility: str, description: str, converter=None):
        self.pattern = re.compile(pattern)
        self.utility = utility
        self.description = description
        self.converter = converter or self._default_converter

    def _default_converter(self, match: re.Match) -> str:
        """Default converter - just suggests the utility"""
        return f"# TODO: Replace with {self.utility}"

    def match(self, line: str) -> Optional[re.Match]:
        """Check if line matches this pattern"""
        return self.pattern.search(line)


class BQScriptConverter:
    """Converts legacy bq CLI scripts to DecentClaude utilities"""

    def __init__(self):
        self.patterns = self._initialize_patterns()
        self.stats = {
            'total_lines': 0,
            'bq_commands': 0,
            'converted': 0,
            'suggestions': 0
        }

    def _initialize_patterns(self) -> List[BQCommandPattern]:
        """Initialize detection patterns for common bq commands"""
        return [
            # bq query with dry_run for cost estimation
            BQCommandPattern(
                r'bq\s+query\s+--dry[_-]run',
                'bq-query-cost',
                'Cost estimation with dry_run',
                self._convert_cost_estimation
            ),

            # bq query for execution
            BQCommandPattern(
                r'bq\s+query\s+(?!--dry[_-]run)',
                'bq-explain + bq query',
                'Query execution (consider adding bq-explain first)',
                self._convert_query_execution
            ),

            # bq show for table info
            BQCommandPattern(
                r'bq\s+show\s+(?!--schema)',
                'bq-profile',
                'Table metadata and profiling',
                self._convert_show_table
            ),

            # bq show --schema
            BQCommandPattern(
                r'bq\s+show\s+--schema',
                'bq-profile --format=json | jq .schema',
                'Schema inspection',
                self._convert_show_schema
            ),

            # bq ls for listing tables
            BQCommandPattern(
                r'bq\s+ls',
                'bq-explore',
                'Interactive dataset exploration',
                self._convert_ls
            ),

            # Manual schema comparison
            BQCommandPattern(
                r'diff\s+.*schema.*\.json',
                'bq-schema-diff',
                'Schema comparison',
                self._convert_schema_diff
            ),
        ]

    def _convert_cost_estimation(self, match: re.Match) -> str:
        """Convert bq query --dry_run to bq-query-cost"""
        original = match.group(0)

        # Try to extract query
        # Common patterns: bq query --dry_run "SELECT ..." or --dry_run < file.sql
        if '"' in original or "'" in original:
            return f"# Use bq-query-cost with inline query\n{original.replace('bq query --dry_run', 'bq-query-cost --query')}"
        else:
            return f"# Use bq-query-cost with file\n{original.replace('bq query --dry_run', 'bq-query-cost --file')}"

    def _convert_query_execution(self, match: re.Match) -> str:
        """Convert bq query to bq-explain + bq query"""
        original = match.group(0)
        return f"""# Consider explaining query first for optimization
# bq-explain --query "..." --dry-run
{original}"""

    def _convert_show_table(self, match: re.Match) -> str:
        """Convert bq show to bq-profile"""
        original = match.group(0)
        # Extract table ID (simple heuristic)
        parts = original.split()
        table_id = parts[-1] if parts else "TABLE_ID"
        return f"bq-profile {table_id}"

    def _convert_show_schema(self, match: re.Match) -> str:
        """Convert bq show --schema to bq-profile"""
        original = match.group(0)
        parts = original.split()
        table_id = parts[-1] if parts else "TABLE_ID"
        return f"bq-profile {table_id} --format=json | jq .schema"

    def _convert_ls(self, match: re.Match) -> str:
        """Convert bq ls to bq-explore"""
        return "# Use bq-explore for interactive exploration\nbq-explore"

    def _convert_schema_diff(self, match: re.Match) -> str:
        """Convert diff schema files to bq-schema-diff"""
        original = match.group(0)
        # Try to extract table IDs from filenames
        # Pattern: diff dev_table_schema.json prod_table_schema.json
        # Extract table names if possible
        return f"# {original}\n# Use bq-schema-diff instead:\n# bq-schema-diff project-dev.dataset.table project-prod.dataset.table"

    def analyze_script(self, script_path: Path) -> Dict:
        """Analyze a script and detect conversion opportunities"""
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")

        with open(script_path, 'r') as f:
            lines = f.readlines()

        self.stats['total_lines'] = len(lines)

        matches = []
        for line_num, line in enumerate(lines, 1):
            for pattern in self.patterns:
                match = pattern.match(line)
                if match:
                    matches.append({
                        'line_num': line_num,
                        'original': line.strip(),
                        'pattern': pattern.description,
                        'suggested_utility': pattern.utility,
                        'converted': pattern.converter(match)
                    })
                    self.stats['bq_commands'] += 1

        return {
            'script': str(script_path),
            'total_lines': self.stats['total_lines'],
            'matches': matches,
            'conversion_rate': len(matches) / max(self.stats['bq_commands'], 1)
        }

    def convert_script(self, input_path: Path, output_path: Path, suggest_only: bool = False) -> None:
        """Convert a script to use DecentClaude utilities"""
        if not input_path.exists():
            raise FileNotFoundError(f"Input script not found: {input_path}")

        with open(input_path, 'r') as f:
            lines = f.readlines()

        converted_lines = []
        conversion_count = 0

        # Add migration header
        converted_lines.append("#!/bin/bash\n")
        converted_lines.append(f"# Migrated to use DecentClaude utilities\n")
        converted_lines.append(f"# Original: {input_path}\n")
        converted_lines.append(f"# Migration date: {datetime.now().strftime('%Y-%m-%d')}\n")
        converted_lines.append("\n")

        # Skip original shebang and comments
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                start_idx = i
                break

        # Process each line
        for line_num, line in enumerate(lines[start_idx:], start_idx + 1):
            converted = False

            # Check each pattern
            for pattern in self.patterns:
                match = pattern.match(line)
                if match:
                    if suggest_only:
                        # Add suggestion as comment
                        converted_lines.append(f"# Suggestion: Use {pattern.utility}\n")
                        converted_lines.append(f"# {pattern.description}\n")
                        converted_lines.append(line)
                        self.stats['suggestions'] += 1
                    else:
                        # Convert the line
                        converted_line = pattern.converter(match)
                        converted_lines.append(f"{converted_line}\n")
                        conversion_count += 1
                        self.stats['converted'] += 1
                    converted = True
                    break

            if not converted:
                # Keep line as-is
                converted_lines.append(line)

        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.writelines(converted_lines)

        # Make executable
        output_path.chmod(0o755)

        print(f"Converted {input_path} -> {output_path}")
        print(f"  Lines processed: {len(lines)}")
        print(f"  Conversions: {conversion_count}")
        if suggest_only:
            print(f"  Suggestions: {self.stats['suggestions']}")

    def scan_directory(self, directory: Path, extensions: List[str] = ['.sh', '.bash']) -> List[Dict]:
        """Scan directory for scripts and analyze them"""
        results = []

        for ext in extensions:
            for script_path in directory.rglob(f"*{ext}"):
                try:
                    analysis = self.analyze_script(script_path)
                    if analysis['matches']:
                        results.append(analysis)
                except Exception as e:
                    print(f"Error analyzing {script_path}: {e}", file=sys.stderr)

        return results

    def generate_report(self, results: List[Dict], output_path: Path) -> None:
        """Generate HTML report of conversion opportunities"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>BQ CLI to DecentClaude Migration Report</title>
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
        .summary {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .script {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .script h3 {{
            margin-top: 0;
            color: #2196F3;
        }}
        .match {{
            background: #f9f9f9;
            padding: 10px;
            margin: 10px 0;
            border-left: 4px solid #FF9800;
            border-radius: 4px;
        }}
        .original {{
            font-family: 'Courier New', monospace;
            background: #263238;
            color: #aed581;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
        }}
        .converted {{
            font-family: 'Courier New', monospace;
            background: #1e1e1e;
            color: #4fc3f7;
            padding: 10px;
            border-radius: 4px;
            margin-top: 5px;
            overflow-x: auto;
        }}
        .utility {{
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.9em;
            margin: 5px 0;
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
            color: #4CAF50;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <h1>BQ CLI to DecentClaude Migration Report</h1>

    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Scripts Analyzed:</strong> {len(results)}</p>

        <div class="stats">
            <div class="stat">
                <div class="stat-value">{sum(len(r['matches']) for r in results)}</div>
                <div class="stat-label">Total Conversion Opportunities</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(results)}</div>
                <div class="stat-label">Scripts with bq Commands</div>
            </div>
            <div class="stat">
                <div class="stat-value">{sum(r['total_lines'] for r in results)}</div>
                <div class="stat-label">Total Lines Analyzed</div>
            </div>
        </div>
    </div>

    <h2>Conversion Opportunities by Script</h2>
"""

        for result in sorted(results, key=lambda r: len(r['matches']), reverse=True):
            html += f"""
    <div class="script">
        <h3>{result['script']}</h3>
        <p><strong>Total Lines:</strong> {result['total_lines']} |
           <strong>Matches:</strong> {len(result['matches'])}</p>
"""
            for match in result['matches']:
                html += f"""
        <div class="match">
            <p><strong>Line {match['line_num']}:</strong> {match['pattern']}</p>
            <div class="utility">Suggested: {match['suggested_utility']}</div>
            <div class="original">{match['original']}</div>
            <div class="converted">{match['converted']}</div>
        </div>
"""
            html += "    </div>\n"

        html += """
</body>
</html>
"""

        with open(output_path, 'w') as f:
            f.write(html)

        print(f"Report generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert legacy bq CLI scripts to DecentClaude utilities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--input',
        required=True,
        help='Input script or directory to analyze'
    )

    parser.add_argument(
        '--output',
        help='Output script path (for single file conversion)'
    )

    parser.add_argument(
        '--suggest-utility',
        action='store_true',
        help='Only suggest utilities without converting (adds comments)'
    )

    parser.add_argument(
        '--scan-all',
        action='store_true',
        help='Scan all scripts in directory'
    )

    parser.add_argument(
        '--report',
        help='Generate HTML report of conversion opportunities'
    )

    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.sh', '.bash'],
        help='File extensions to scan (default: .sh .bash)'
    )

    args = parser.parse_args()

    converter = BQScriptConverter()
    input_path = Path(args.input)

    if args.scan_all or input_path.is_dir():
        # Scan directory
        print(f"Scanning directory: {input_path}")
        results = converter.scan_directory(input_path, args.extensions)

        if args.report:
            report_path = Path(args.report)
            converter.generate_report(results, report_path)
        else:
            # Print summary
            print(f"\nFound {len(results)} scripts with bq commands:")
            for result in sorted(results, key=lambda r: len(r['matches']), reverse=True):
                print(f"\n{result['script']}:")
                print(f"  Total lines: {result['total_lines']}")
                print(f"  Matches: {len(result['matches'])}")
                for match in result['matches'][:3]:  # Show first 3
                    print(f"    Line {match['line_num']}: {match['pattern']}")
                    print(f"      -> {match['suggested_utility']}")
                if len(result['matches']) > 3:
                    print(f"    ... and {len(result['matches']) - 3} more")

    else:
        # Convert single file
        if not args.output:
            # Generate output filename
            stem = input_path.stem
            suffix = input_path.suffix
            output_path = input_path.parent / f"{stem}_migrated{suffix}"
        else:
            output_path = Path(args.output)

        converter.convert_script(input_path, output_path, args.suggest_utility)


if __name__ == '__main__':
    main()
