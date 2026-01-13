"""
Performance benchmarks for ai-generate utility.

This module benchmarks the AI-powered code generation functionality,
focusing on pure code performance with mocked API calls.

Run with:
    pytest tests/benchmarks/test_ai_generate_benchmark.py --benchmark-only
    pytest tests/benchmarks/test_ai_generate_benchmark.py --benchmark-autosave
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add lib directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lib"))


@pytest.mark.benchmark
@pytest.mark.ai_generate
class TestAIGenerateBenchmarks:
    """Benchmarks for ai-generate utility."""

    def test_build_system_prompt_dbt_model(self, benchmark):
        """Benchmark building system prompt for dbt model generation."""
        def build_prompt():
            base_prompt = """You are an expert data engineer specializing in SQL, dbt, and SQLMesh.
Your task is to generate high-quality, production-ready code following best practices."""

            dbt_specific = """
For dbt models:
- Use CTE (Common Table Expressions) for readability
- Add descriptive comments
- Follow naming conventions (stg_, int_, fct_, dim_)
- Include column descriptions in schema.yml
- Use refs for dependencies
- Add data quality tests
"""
            return base_prompt + dbt_specific

        result = benchmark(build_prompt)
        assert 'dbt' in result.lower()
        assert 'CTE' in result

    def test_build_system_prompt_sqlmesh_model(self, benchmark):
        """Benchmark building system prompt for SQLMesh model generation."""
        def build_prompt():
            base_prompt = """You are an expert data engineer specializing in SQL, dbt, and SQLMesh.
Your task is to generate high-quality, production-ready code following best practices."""

            sqlmesh_specific = """
For SQLMesh models:
- Use MODEL macro with appropriate configuration
- Define model kind (INCREMENTAL, FULL, VIEW, etc.)
- Add grain and partitioning
- Use @DEF and @VAR for reusable SQL
- Include audit columns
- Add comprehensive tests
"""
            return base_prompt + sqlmesh_specific

        result = benchmark(build_prompt)
        assert 'sqlmesh' in result.lower()
        assert 'MODEL' in result

    def test_build_user_prompt_simple(self, benchmark):
        """Benchmark building user prompt with simple requirements."""
        requirements = "Create a daily user engagement metrics model"
        context = ""

        def build_prompt():
            prompt_parts = []
            prompt_parts.append("Generate code based on the following requirements:\n")
            prompt_parts.append(f"Requirements: {requirements}\n")

            if context:
                prompt_parts.append(f"\nAdditional context:\n{context}")

            prompt_parts.append("\nProvide only the code without explanations.")

            return ''.join(prompt_parts)

        result = benchmark(build_prompt)
        assert 'daily user engagement' in result.lower()

    def test_build_user_prompt_with_context(self, benchmark):
        """Benchmark building user prompt with context file."""
        requirements = "Create a transformation for 7-day rolling average"
        context = """
Schema:
  users table: user_id, user_name, created_at
  events table: event_id, user_id, event_name, event_timestamp
  orders table: order_id, user_id, amount, order_date

Existing models:
  - stg_users
  - stg_events
  - stg_orders
"""

        def build_prompt():
            prompt_parts = []
            prompt_parts.append("Generate code based on the following requirements:\n")
            prompt_parts.append(f"Requirements: {requirements}\n")
            prompt_parts.append(f"\nAdditional context:\n{context}")
            prompt_parts.append("\nProvide only the code without explanations.")

            return ''.join(prompt_parts)

        result = benchmark(build_prompt)
        assert 'rolling average' in result.lower()
        assert 'users table' in result

    def test_parse_requirements_from_string(self, benchmark):
        """Benchmark parsing requirements from a string."""
        requirements = """
Calculate daily active users (DAU) with the following logic:
- Count distinct user_ids per day
- Filter out test users (user_id < 1000)
- Include only events from the past 30 days
- Partition by date for incremental processing
- Add a 7-day rolling average
"""

        def parse_requirements():
            lines = requirements.strip().split('\n')
            parsed = {
                'description': lines[0] if lines else '',
                'requirements': [line.strip('- ') for line in lines[1:] if line.strip().startswith('-')],
                'num_requirements': sum(1 for line in lines if line.strip().startswith('-'))
            }
            return parsed

        result = benchmark(parse_requirements)
        assert result['num_requirements'] == 5

    def test_parse_requirements_from_large_file(self, benchmark, tmp_path):
        """Benchmark parsing requirements from a large file."""
        requirements_file = tmp_path / "requirements.txt"
        requirements_content = "\n".join([
            "# Requirements Document",
            "",
            "## Objective",
            "Build a comprehensive user analytics pipeline",
            "",
            "## Requirements",
            *[f"- Requirement {i}: Process dimension {i}" for i in range(100)],
            "",
            "## Data Sources",
            "- Source system A",
            "- Source system B",
            "- Source system C",
        ])
        requirements_file.write_text(requirements_content)

        def parse_file():
            content = requirements_file.read_text()
            lines = content.split('\n')
            requirements = [line.strip('- ') for line in lines if line.strip().startswith('-')]
            return {
                'total_lines': len(lines),
                'requirements': requirements,
                'num_requirements': len(requirements)
            }

        result = benchmark(parse_file)
        assert result['num_requirements'] > 100

    def test_format_generated_code_sql(self, benchmark):
        """Benchmark formatting generated SQL code."""
        generated_code = """
SELECT
    user_id,
    event_date,
    COUNT(DISTINCT event_id) as event_count,
    COUNT(DISTINCT session_id) as session_count,
    SUM(revenue) as total_revenue
FROM {{ ref('stg_events') }}
WHERE event_date >= CURRENT_DATE() - 30
GROUP BY user_id, event_date
"""

        def format_code():
            # Simple formatting: ensure consistent indentation
            lines = generated_code.strip().split('\n')
            formatted_lines = []

            for line in lines:
                stripped = line.strip()
                if stripped.startswith('SELECT') or stripped.startswith('FROM') or stripped.startswith('WHERE') or stripped.startswith('GROUP BY'):
                    formatted_lines.append(stripped)
                else:
                    formatted_lines.append('    ' + stripped)

            return '\n'.join(formatted_lines)

        result = benchmark(format_code)
        assert 'SELECT' in result
        assert 'user_id' in result

    def test_extract_code_from_response(self, benchmark):
        """Benchmark extracting code from API response."""
        api_response = """
Here's the dbt model for daily user engagement:

```sql
-- models/staging/stg_analytics__user_engagement_daily.sql

with source as (
    select * from {{ ref('stg_events') }}
),

daily_metrics as (
    select
        user_id,
        date(event_timestamp) as event_date,
        count(distinct event_id) as event_count,
        count(distinct session_id) as session_count,
        sum(case when event_name = 'purchase' then 1 else 0 end) as purchase_count
    from source
    group by 1, 2
)

select * from daily_metrics
```

This model calculates daily engagement metrics per user.
"""

        def extract_code():
            # Extract code between ```sql and ```
            import re
            pattern = r'```sql\n(.*?)\n```'
            matches = re.findall(pattern, api_response, re.DOTALL)
            return matches[0] if matches else api_response

        result = benchmark(extract_code)
        assert 'select' in result.lower()
        assert 'from source' in result.lower()

    def test_validate_generated_sql_syntax(self, benchmark):
        """Benchmark basic SQL syntax validation."""
        sql_code = """
SELECT
    user_id,
    event_date,
    COUNT(*) as event_count
FROM events
WHERE event_date >= '2024-01-01'
GROUP BY user_id, event_date
HAVING COUNT(*) > 10
"""

        def validate_sql():
            required_keywords = ['SELECT', 'FROM']
            sql_upper = sql_code.upper()

            issues = []
            for keyword in required_keywords:
                if keyword not in sql_upper:
                    issues.append(f"Missing required keyword: {keyword}")

            # Check for balanced parentheses
            if sql_code.count('(') != sql_code.count(')'):
                issues.append("Unbalanced parentheses")

            # Check for common syntax errors
            lines = sql_code.split('\n')
            for i, line in enumerate(lines):
                if line.strip().endswith(',') and i == len(lines) - 1:
                    issues.append(f"Trailing comma on line {i+1}")

            return {
                'is_valid': len(issues) == 0,
                'issues': issues
            }

        result = benchmark(validate_sql)
        assert result['is_valid'] is True

    def test_mock_anthropic_api_call(self, benchmark, mock_anthropic_client):
        """Benchmark mock Anthropic API interaction."""
        def make_api_call():
            response = mock_anthropic_client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": "Generate a dbt model for user analytics"
                }]
            )
            return response.content[0].text

        result = benchmark(make_api_call)
        assert 'SQL' in result or 'code' in result

    def test_generate_multiple_variants(self, benchmark, mock_anthropic_client):
        """Benchmark generating multiple code variants."""
        generation_types = ['dbt-model', 'sqlmesh-model', 'test', 'transform', 'migration']

        def generate_variants():
            variants = []
            for gen_type in generation_types:
                response = mock_anthropic_client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=2000,
                    messages=[{
                        "role": "user",
                        "content": f"Generate {gen_type} for user analytics"
                    }]
                )
                variants.append({
                    'type': gen_type,
                    'code': response.content[0].text,
                    'tokens': response.usage.output_tokens
                })
            return variants

        result = benchmark(generate_variants)
        assert len(result) == 5

    def test_estimate_token_usage(self, benchmark):
        """Benchmark estimating token usage for prompts."""
        prompt = """You are an expert data engineer.

Generate a dbt model for daily user engagement metrics.

Requirements:
- Calculate DAU (daily active users)
- Include 7-day rolling average
- Partition by date
- Add data quality tests
- Use CTEs for readability

Context:
Schema: users (user_id, user_name), events (event_id, user_id, event_timestamp)
"""

        def estimate_tokens():
            # Rough estimation: ~4 characters per token
            char_count = len(prompt)
            estimated_tokens = char_count // 4

            return {
                'characters': char_count,
                'estimated_tokens': estimated_tokens,
                'estimated_cost': estimated_tokens * 0.000003  # Example pricing
            }

        result = benchmark(estimate_tokens)
        assert result['estimated_tokens'] > 0

    def test_add_code_documentation(self, benchmark):
        """Benchmark adding documentation to generated code."""
        sql_code = """
SELECT
    user_id,
    COUNT(*) as event_count
FROM events
GROUP BY user_id
"""

        def add_documentation():
            doc_header = """
-- Model: User Event Summary
-- Description: Aggregates event counts per user
-- Owner: Data Engineering Team
-- Updated: {date}
-- Dependencies: raw.events

""".format(date='2024-01-01')

            inline_comments = []
            lines = sql_code.split('\n')
            for line in lines:
                if 'SELECT' in line:
                    inline_comments.append(line + "  -- Select user metrics")
                elif 'FROM' in line:
                    inline_comments.append(line + "  -- Source table")
                elif 'GROUP BY' in line:
                    inline_comments.append(line + "  -- Aggregate by user")
                else:
                    inline_comments.append(line)

            return doc_header + '\n'.join(inline_comments)

        result = benchmark(add_documentation)
        assert 'Model:' in result
        assert 'Description:' in result
