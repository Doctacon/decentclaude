"""
Mayor CLI implementation

Command structure:
- mayor bq <subcommand>      # BigQuery utilities
- mayor dbt <subcommand>     # dbt utilities
- mayor sqlmesh <subcommand> # SQLMesh utilities
- mayor ai <subcommand>      # AI utilities
- mayor kb <subcommand>      # Knowledge base
- mayor workflow <subcommand> # Workflow orchestration
- mayor skills <subcommand>  # Skills management
- mayor list                 # List all tools
- mayor search <query>       # Search tools by use case
- mayor info <tool>          # Tool information
"""

import click
import subprocess
import json
import sys
from pathlib import Path
from typing import List, Optional

# Paths
BIN_DIR = Path(__file__).parent.parent / "bin"
DATA_UTILS = BIN_DIR / "data-utils"
WORKFLOWS = BIN_DIR.parent / "workflows"
SKILLS = BIN_DIR.parent / ".claude" / "skills"


def run_utility(script_path: Path, args: List[str]) -> int:
    """Run a utility script with the given arguments"""
    try:
        result = subprocess.run(
            [str(script_path)] + args,
            check=False
        )
        return result.returncode
    except FileNotFoundError:
        click.echo(f"Error: Utility not found: {script_path}", err=True)
        return 1
    except Exception as e:
        click.echo(f"Error running utility: {e}", err=True)
        return 1


@click.group()
@click.version_option(version="0.1.0", prog_name="mayor")
def cli():
    """
    Mayor - DecentClaude unified command center

    The single entry point for all DecentClaude data engineering capabilities.

    \b
    Quick Start:
      mayor list                    # Discover all available tools
      mayor bq profile <table>      # Profile a BigQuery table
      mayor search "optimization"   # Find tools by use case

    \b
    Command Groups:
      bq         BigQuery utilities (11 tools)
      dbt        dbt utilities (5 tools)
      sqlmesh    SQLMesh utilities (4 tools)
      ai         AI-powered utilities (3 tools)
      kb         Knowledge base management
      workflow   Pre-built workflow orchestration
      skills     Claude Code Skills management

    \b
    Discovery:
      list       List all available tools
      search     Search tools by use case or description
      info       Get detailed information about a tool

    For detailed help on any command group:
      mayor <group> --help

    Examples:
      mayor bq profile project.dataset.table
      mayor dbt test-gen models/staging/
      mayor ai generate --spec "ETL for users table"
      mayor workflow run data-quality-audit table
    """
    pass


# ============================================================================
# BigQuery Command Group
# ============================================================================

@cli.group()
def bq():
    """BigQuery utilities (11 tools)

    Tools for BigQuery data analysis, optimization, and quality management.

    \b
    Available commands:
      profile        Generate comprehensive data profile
      explain        Analyze query execution plan
      optimize       Optimize query for cost and performance
      lineage        Discover table dependencies
      schema-diff    Compare schemas between tables
      table-compare  Compare data between tables
      partition-info Get partitioning details
      query-cost     Estimate query cost
      lint           Validate SQL and schemas
      validate       Validate table data quality
      list-tables    List tables in dataset

    Examples:
      mayor bq profile project.dataset.users --format=json
      mayor bq explain --file query.sql
      mayor bq optimize query.sql
      mayor bq lineage project.dataset.orders --direction=downstream
    """
    pass


@bq.command()
@click.argument('table_id')
@click.option('--format', type=click.Choice(['text', 'json', 'markdown', 'html']), default='text',
              help='Output format')
@click.option('--sample-size', type=int, default=10, help='Number of sample rows')
@click.option('--detect-anomalies', is_flag=True, help='Enable anomaly detection')
@click.option('--no-cache', is_flag=True, help='Disable metadata caching')
@click.option('--parallel', type=int, help='Number of parallel workers for batch profiling')
@click.option('--progress', is_flag=True, help='Show progress bar')
def profile(table_id, format, sample_size, detect_anomalies, no_cache, parallel, progress):
    """Generate comprehensive data profile for BigQuery table

    Analyzes table structure, statistics, data quality, and generates
    actionable recommendations.

    \b
    Outputs:
      - Table metadata (size, rows, partitioning)
      - Column-level statistics
      - Data quality score
      - Null percentages
      - Anomalies (if --detect-anomalies enabled)

    \b
    Examples:
      mayor bq profile project.dataset.users
      mayor bq profile table --format=json --detect-anomalies
      mayor bq profile table1 table2 table3 --parallel=3
    """
    args = [table_id, f'--format={format}', f'--sample-size={sample_size}']
    if detect_anomalies:
        args.append('--detect-anomalies')
    if no_cache:
        args.append('--no-cache')
    if parallel:
        args.extend(['--parallel', str(parallel)])
    if progress:
        args.append('--progress')

    sys.exit(run_utility(DATA_UTILS / "bq-profile", args))


@bq.command()
@click.option('--file', type=click.Path(exists=True), help='SQL file to analyze')
@click.option('--query', help='SQL query string to analyze')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def explain(file, query, format):
    """Analyze BigQuery query execution plan

    Examines query structure, identifies bottlenecks, estimates costs,
    and provides optimization suggestions.

    \b
    Examples:
      mayor bq explain --file query.sql
      mayor bq explain --query "SELECT * FROM table" --format=json
    """
    args = [f'--format={format}']
    if file:
        args.extend(['--file', file])
    elif query:
        args.extend(['--query', query])
    else:
        click.echo("Error: Must provide either --file or --query", err=True)
        sys.exit(1)

    sys.exit(run_utility(DATA_UTILS / "bq-explain", args))


@bq.command()
@click.option('--file', type=click.Path(exists=True), help='SQL file to optimize')
@click.option('--query', help='SQL query string to optimize')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def optimize(file, query, format):
    """Optimize BigQuery query for cost and performance

    Automatically applies optimization techniques:
    - Add partition filters
    - Push down predicates
    - Suggest clustering columns
    - Estimate cost savings

    \b
    Examples:
      mayor bq optimize --file query.sql
      mayor bq optimize --query "SELECT * FROM table"
    """
    args = [f'--format={format}']
    if file:
        args.extend(['--file', file])
    elif query:
        args.extend(['--query', query])
    else:
        click.echo("Error: Must provide either --file or --query", err=True)
        sys.exit(1)

    sys.exit(run_utility(DATA_UTILS / "bq-optimize", args))


@bq.command()
@click.argument('table_id')
@click.option('--direction', type=click.Choice(['upstream', 'downstream', 'both']),
              default='both', help='Lineage direction to explore')
@click.option('--depth', type=int, default=1, help='Maximum depth to traverse')
@click.option('--format', type=click.Choice(['text', 'json', 'mermaid']), default='text')
def lineage(table_id, direction, depth, format):
    """Discover table dependencies and data lineage

    Maps upstream sources and downstream consumers for impact analysis
    and understanding data flow.

    \b
    Examples:
      mayor bq lineage project.dataset.users
      mayor bq lineage table --direction=downstream --depth=2
      mayor bq lineage table --format=mermaid > lineage.md
    """
    args = [
        table_id,
        f'--direction={direction}',
        f'--depth={depth}',
        f'--format={format}'
    ]
    sys.exit(run_utility(DATA_UTILS / "bq-lineage", args))


@bq.command(name='schema-diff')
@click.argument('table_a')
@click.argument('table_b')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def schema_diff(table_a, table_b, format):
    """Compare schemas between two tables

    Identifies differences in columns, types, and structure.
    Essential for safe schema migrations.

    \b
    Examples:
      mayor bq schema-diff dev.users prod.users
      mayor bq schema-diff table_v1 table_v2 --format=json
    """
    args = [table_a, table_b, f'--format={format}']
    sys.exit(run_utility(DATA_UTILS / "bq-schema-diff", args))


@bq.command(name='table-compare')
@click.argument('table_a')
@click.argument('table_b')
@click.option('--sample-size', type=int, default=1000, help='Rows to sample')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def table_compare(table_a, table_b, sample_size, format):
    """Compare data between two tables

    Samples and compares data to identify differences in content.

    \b
    Examples:
      mayor bq table-compare dev.users prod.users
      mayor bq table-compare old new --sample-size=5000
    """
    args = [table_a, table_b, f'--sample-size={sample_size}', f'--format={format}']
    sys.exit(run_utility(DATA_UTILS / "bq-table-compare", args))


@bq.command(name='query-cost')
@click.option('--file', type=click.Path(exists=True), help='SQL file to estimate')
@click.option('--query', help='SQL query string to estimate')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def query_cost(file, query, format):
    """Estimate BigQuery query cost before execution

    Dry-run analysis to prevent surprise bills.

    \b
    Examples:
      mayor bq query-cost --file query.sql
      mayor bq query-cost --query "SELECT * FROM table"
    """
    args = [f'--format={format}']
    if file:
        args.extend(['--file', file])
    elif query:
        args.extend(['--query', query])
    else:
        click.echo("Error: Must provide either --file or --query", err=True)
        sys.exit(1)

    sys.exit(run_utility(DATA_UTILS / "bq-query-cost", args))


# ============================================================================
# dbt Command Group
# ============================================================================

@cli.group()
def dbt():
    """dbt utilities (5 tools)

    Tools for dbt project development and optimization.

    \b
    Available commands:
      test-gen       Generate dbt tests for models
      doc-gen        Generate documentation for models
      analyze        Analyze dbt project structure
      optimize       Optimize dbt models
      validate       Validate dbt project configuration

    Examples:
      mayor dbt test-gen models/staging/
      mayor dbt doc-gen models/marts/customers.sql
    """
    pass


@dbt.command(name='test-gen')
@click.argument('path', type=click.Path(exists=True))
@click.option('--format', type=click.Choice(['text', 'yaml']), default='yaml')
def dbt_test_gen(path, format):
    """Generate dbt tests for models

    Automatically creates test configurations based on model structure.

    \b
    Examples:
      mayor dbt test-gen models/staging/
      mayor dbt test-gen models/staging/stg_users.sql
    """
    args = [path, f'--format={format}']
    sys.exit(run_utility(DATA_UTILS / "dbt-test-gen", args))


# ============================================================================
# AI Command Group
# ============================================================================

@cli.group()
def ai():
    """AI-powered utilities (3 tools)

    Tools leveraging LLMs for code generation and analysis.

    \b
    Available commands:
      generate       Generate SQL/dbt code from specifications
      review         AI code review for data pipelines
      docs           Generate documentation from code

    Examples:
      mayor ai generate --spec "ETL for users table"
      mayor ai review models/staging/
    """
    pass


@ai.command()
@click.option('--spec', required=True, help='Specification for code generation')
@click.option('--format', type=click.Choice(['sql', 'dbt', 'python']), default='sql')
@click.option('--output', type=click.Path(), help='Output file path')
def generate(spec, format, output):
    """Generate SQL/dbt code from natural language specifications

    Uses LLMs to convert specifications into production-ready code.

    \b
    Examples:
      mayor ai generate --spec "ETL for users table with deduplication"
      mayor ai generate --spec "dbt model joining users and orders" --format=dbt
    """
    args = ['--spec', spec, f'--format={format}']
    if output:
        args.extend(['--output', output])

    sys.exit(run_utility(DATA_UTILS / "ai-generate", args))


# ============================================================================
# Knowledge Base Command Group
# ============================================================================

@cli.group()
def kb():
    """Knowledge base management

    Store and retrieve tribal knowledge, patterns, and solutions.

    \b
    Available commands:
      add            Add knowledge to base
      search         Search knowledge base
      list           List all knowledge entries
      show           Show specific entry

    Examples:
      mayor kb search "partition filter error"
      mayor kb add solution --title "..." --content "..."
    """
    pass


@kb.command()
@click.argument('query')
@click.option('--type', type=click.Choice(['solution', 'pattern', 'all']), default='all')
@click.option('--limit', type=int, default=5, help='Maximum results to return')
def search(query, type, limit):
    """Search knowledge base for solutions and patterns

    \b
    Examples:
      mayor kb search "data quality"
      mayor kb search "optimization" --type=pattern
    """
    args = ['search', query, f'--type={type}', f'--limit={limit}']
    sys.exit(run_utility(BIN_DIR / "kb", args))


# ============================================================================
# Workflow Command Group
# ============================================================================

@cli.group()
def workflow():
    """Workflow orchestration

    Pre-built workflows combining multiple tools.

    \b
    Available workflows:
      data-quality-audit    Comprehensive DQ assessment
      schema-migration      Safe schema changes
      incident-response     Incident triage and response
      query-optimization    Systematic query improvement

    Examples:
      mayor workflow run data-quality-audit <table>
      mayor workflow list
    """
    pass


@workflow.command()
def list():
    """List all available workflows"""
    if not WORKFLOWS.exists():
        click.echo("No workflows directory found", err=True)
        sys.exit(1)

    click.echo("Available workflows:\n")
    for workflow_file in sorted(WORKFLOWS.glob("*")):
        if workflow_file.is_file() and workflow_file.name != "README.md":
            click.echo(f"  {workflow_file.name}")

    click.echo(f"\nRun with: mayor workflow run <name> [args]")
    click.echo(f"See {WORKFLOWS}/README.md for detailed documentation")


@workflow.command()
@click.argument('name')
@click.argument('args', nargs=-1)
def run(name, args):
    """Run a workflow by name

    \b
    Examples:
      mayor workflow run data-quality-audit project.dataset.table 85
      mayor workflow run schema-migration dev.users prod.users
    """
    workflow_path = WORKFLOWS / name
    if not workflow_path.exists():
        click.echo(f"Error: Workflow '{name}' not found", err=True)
        click.echo(f"\nAvailable workflows:")
        for wf in sorted(WORKFLOWS.glob("*")):
            if wf.is_file() and wf.name != "README.md":
                click.echo(f"  {wf.name}")
        sys.exit(1)

    sys.exit(run_utility(workflow_path, list(args)))


# ============================================================================
# Skills Command Group
# ============================================================================

@cli.group()
def skills():
    """Claude Code Skills management

    Manage and discover Claude Code Skills for data engineering workflows.

    \b
    Available commands:
      list           List all available Skills
      info           Get detailed information about a Skill
      search         Search Skills by use case

    Examples:
      mayor skills list
      mayor skills info sql-optimizer
      mayor skills search "data quality"
    """
    pass


@skills.command()
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def list(format):
    """List all available Claude Code Skills"""
    if not SKILLS.exists():
        click.echo("No skills directory found", err=True)
        sys.exit(1)

    skill_dirs = [d for d in SKILLS.iterdir() if d.is_dir() and not d.name.startswith('.')]

    if format == 'json':
        skills_data = []
        for skill_dir in sorted(skill_dirs):
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                skills_data.append({
                    "name": skill_dir.name,
                    "path": str(skill_file)
                })
        click.echo(json.dumps(skills_data, indent=2))
    else:
        click.echo(f"Available Claude Code Skills ({len(skill_dirs)}):\n")
        for skill_dir in sorted(skill_dirs):
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                # Try to extract description from frontmatter
                try:
                    with open(skill_file) as f:
                        content = f.read()
                        if 'description:' in content:
                            desc_line = [l for l in content.split('\n') if 'description:' in l][0]
                            desc = desc_line.split('description:')[1].strip()
                            click.echo(f"  {skill_dir.name:<30} {desc}")
                        else:
                            click.echo(f"  {skill_dir.name}")
                except:
                    click.echo(f"  {skill_dir.name}")

        click.echo(f"\nUse in Claude Code: /{click.format_filename('{skill-name}')}")
        click.echo(f"Get info: mayor skills info <skill-name>")


@skills.command()
@click.argument('skill_name')
def info(skill_name):
    """Get detailed information about a Skill

    \b
    Examples:
      mayor skills info sql-optimizer
      mayor skills info data-lineage-doc
    """
    skill_dir = SKILLS / skill_name
    skill_file = skill_dir / "SKILL.md"

    if not skill_file.exists():
        click.echo(f"Error: Skill '{skill_name}' not found", err=True)
        sys.exit(1)

    with open(skill_file) as f:
        click.echo(f.read())


# ============================================================================
# Discovery Commands
# ============================================================================

@cli.command()
@click.option('--category', help='Filter by category (bq, dbt, ai, etc.)')
@click.option('--format', type=click.Choice(['text', 'json']), default='text')
def list(category, format):
    """List all available tools

    Shows comprehensive catalog of all 23+ DecentClaude utilities.

    \b
    Examples:
      mayor list
      mayor list --category=bq
      mayor list --format=json
    """
    # This will be enhanced with tool registry in next phase
    tools = {
        "bq": ["profile", "explain", "optimize", "lineage", "schema-diff",
               "table-compare", "partition-info", "query-cost", "lint",
               "validate", "list-tables"],
        "dbt": ["test-gen", "doc-gen", "analyze", "optimize", "validate"],
        "sqlmesh": ["plan", "run", "test", "audit"],
        "ai": ["generate", "review", "docs"],
    }

    if format == 'json':
        if category:
            output = {category: tools.get(category, [])}
        else:
            output = tools
        click.echo(json.dumps(output, indent=2))
    else:
        if category:
            if category in tools:
                click.echo(f"{category.upper()} tools ({len(tools[category])}):\n")
                for tool in tools[category]:
                    click.echo(f"  mayor {category} {tool}")
            else:
                click.echo(f"Unknown category: {category}", err=True)
                click.echo(f"Available categories: {', '.join(tools.keys())}")
                sys.exit(1)
        else:
            total = sum(len(t) for t in tools.values())
            click.echo(f"DecentClaude Tools ({total} total):\n")
            for cat, tool_list in tools.items():
                click.echo(f"{cat.upper()} ({len(tool_list)} tools):")
                for tool in tool_list:
                    click.echo(f"  mayor {cat} {tool}")
                click.echo()

        click.echo("For detailed help: mayor <category> <tool> --help")
        click.echo("Search by use case: mayor search <query>")


@cli.command()
@click.argument('query')
def search(query):
    """Search tools by use case or description

    Finds tools matching your search query across all categories.

    \b
    Examples:
      mayor search "data quality"
      mayor search "optimization"
      mayor search "cost"
    """
    # This will be enhanced with tool registry in next phase
    # For now, simple keyword matching
    query_lower = query.lower()

    matches = []
    if "quality" in query_lower or "profile" in query_lower:
        matches.append("mayor bq profile - Generate comprehensive data profile")
        matches.append("mayor workflow run data-quality-audit - DQ assessment")

    if "optim" in query_lower or "performance" in query_lower:
        matches.append("mayor bq optimize - Optimize query for cost and performance")
        matches.append("mayor bq explain - Analyze query execution plan")
        matches.append("mayor workflow run query-optimization - Systematic query improvement")

    if "cost" in query_lower:
        matches.append("mayor bq query-cost - Estimate query cost before execution")
        matches.append("mayor bq optimize - Optimize query to reduce costs")

    if "lineage" in query_lower or "depend" in query_lower:
        matches.append("mayor bq lineage - Discover table dependencies")

    if "schema" in query_lower or "migrat" in query_lower:
        matches.append("mayor bq schema-diff - Compare schemas between tables")
        matches.append("mayor workflow run schema-migration - Safe schema changes")

    if "test" in query_lower:
        matches.append("mayor dbt test-gen - Generate dbt tests for models")

    if "incident" in query_lower or "debug" in query_lower:
        matches.append("mayor workflow run incident-response - Incident triage and response")

    if matches:
        click.echo(f"Tools matching '{query}':\n")
        for match in matches:
            click.echo(f"  {match}")
        click.echo(f"\nFor detailed help: mayor <command> --help")
    else:
        click.echo(f"No tools found matching '{query}'")
        click.echo(f"\nTry: mayor list (to see all tools)")
        click.echo(f"Or: mayor search <different query>")


@cli.command()
@click.argument('tool_name')
def info(tool_name):
    """Get detailed information about a tool

    Shows comprehensive documentation including usage, examples,
    output schema, related skills, and observability.

    \b
    Examples:
      mayor info bq-profile
      mayor info bq-optimize
    """
    # This will be enhanced with tool registry in next phase
    tool_docs = {
        "bq-profile": """
Tool: bq-profile
Category: BigQuery
Description: Generate comprehensive data profile for BigQuery tables

Usage:
  mayor bq profile <table_id> [options]

Options:
  --format=text|json|markdown|html   Output format (default: text)
  --sample-size=N                    Sample rows (default: 10)
  --detect-anomalies                 Enable anomaly detection
  --no-cache                         Disable metadata caching
  --parallel=N                       Parallel workers for batch
  --progress                         Show progress bar

Examples:
  mayor bq profile project.dataset.users
  mayor bq profile table --format=json --detect-anomalies
  mayor bq profile table1 table2 table3 --parallel=3

Output Schema:
  See: schemas/bq-profile.json

Related Skills:
  - data-lineage-doc (Document data lineage)
  - schema-doc-generator (Generate schema docs)

Observability:
  Tracks: bytes processed, execution time, cache hit rate
        """,
        "bq-optimize": """
Tool: bq-optimize
Category: BigQuery
Description: Optimize BigQuery queries for cost and performance

Usage:
  mayor bq optimize --file=<path> | --query=<sql>

Options:
  --file=PATH       SQL file to optimize
  --query=SQL       SQL query string
  --format=text|json Output format

Examples:
  mayor bq optimize --file query.sql
  mayor bq optimize --query "SELECT * FROM table"

Optimizations Applied:
  - Add partition filters
  - Push down predicates
  - Suggest clustering columns
  - Estimate cost savings

Related Workflows:
  - query-optimization (Systematic query improvement)

Related Skills:
  - sql-optimizer (Comprehensive SQL optimization)
        """
    }

    if tool_name in tool_docs:
        click.echo(tool_docs[tool_name].strip())
    else:
        click.echo(f"Tool documentation not yet available for: {tool_name}")
        click.echo(f"\nTry: mayor <category> {tool_name} --help")
        click.echo(f"Or: mayor list (to see all tools)")


if __name__ == "__main__":
    cli()
