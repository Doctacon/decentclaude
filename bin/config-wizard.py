#!/usr/bin/env python3
"""
DecentClaude Configuration Wizard

Interactive setup tool for creating .env configuration file.
Guides users through required and optional settings with validation.

Usage:
  ./bin/config-wizard.py
  mayor config init
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List

# Colors for terminal output
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color


def print_header(text: str):
    """Print colored section header"""
    print(f"\n{BLUE}{'='*70}{NC}")
    print(f"{BLUE}{text}{NC}")
    print(f"{BLUE}{'='*70}{NC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{GREEN}✓ {text}{NC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{YELLOW}⚠ {text}{NC}")


def print_error(text: str):
    """Print error message"""
    print(f"{RED}✗ {text}{NC}")


def prompt(question: str, default: Optional[str] = None, required: bool = False) -> str:
    """Prompt user for input with optional default"""
    if default:
        prompt_text = f"{question} [{default}]: "
    else:
        prompt_text = f"{question}: "

    while True:
        value = input(prompt_text).strip()

        if not value and default:
            return default

        if not value and required:
            print_error("This field is required. Please provide a value.")
            continue

        return value


def prompt_yes_no(question: str, default: bool = False) -> bool:
    """Prompt user for yes/no answer"""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{question} [{default_str}]: ").strip().lower()

    if not response:
        return default

    return response in ('y', 'yes')


def validate_path(path: str) -> bool:
    """Validate that a file path exists"""
    return Path(path).expanduser().exists()


def validate_project_id(project_id: str) -> bool:
    """Validate Google Cloud project ID format"""
    if not project_id:
        return False
    # Project IDs must be 6-30 characters, lowercase letters, digits, hyphens
    import re
    return bool(re.match(r'^[a-z][a-z0-9-]{4,28}[a-z0-9]$', project_id))


def test_bigquery_connection(project_id: str, credentials_path: str) -> bool:
    """Test BigQuery connection with provided credentials"""
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        os.environ['GOOGLE_CLOUD_PROJECT'] = project_id

        from google.cloud import bigquery
        client = bigquery.Client(project=project_id)

        # Try a simple query
        query = "SELECT 1 as test"
        client.query(query).result()

        return True
    except ImportError:
        print_warning("google-cloud-bigquery not installed. Skipping connection test.")
        print_warning("Install with: pip install google-cloud-bigquery")
        return True  # Don't fail if library not installed
    except Exception as e:
        print_error(f"Connection test failed: {e}")
        return False


def main():
    """Main wizard flow"""
    print_header("DecentClaude Configuration Wizard")
    print("This wizard will help you create a .env configuration file.")
    print("Press Ctrl+C at any time to cancel.\n")

    # Check if .env already exists
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        print_warning(f".env file already exists at: {env_file}")
        if not prompt_yes_no("Overwrite existing .env file?", default=False):
            print("Cancelled. Existing .env file preserved.")
            sys.exit(0)

    config: Dict[str, str] = {}

    # ========================================================================
    # BigQuery Configuration
    # ========================================================================
    print_header("1. BigQuery Configuration (Required for bq-* tools)")

    use_bigquery = prompt_yes_no("Do you want to use BigQuery utilities?", default=True)

    if use_bigquery:
        # Project ID
        while True:
            project_id = prompt(
                "Google Cloud Project ID",
                required=True
            )

            if validate_project_id(project_id):
                config['GOOGLE_CLOUD_PROJECT'] = project_id
                break
            else:
                print_error("Invalid project ID format. Must be 6-30 characters, lowercase, digits, hyphens.")

        # Dataset
        dataset = prompt(
            "Default BigQuery dataset (optional)",
            default="analytics"
        )
        if dataset:
            config['GOOGLE_DATASET'] = dataset

        # Service account credentials
        print("\nService Account Credentials:")
        print("  Create at: https://cloud.google.com/iam/docs/creating-managing-service-account-keys")

        while True:
            creds_path = prompt(
                "Path to service account JSON key file",
                required=True
            )

            expanded_path = str(Path(creds_path).expanduser())

            if validate_path(expanded_path):
                config['GOOGLE_APPLICATION_CREDENTIALS'] = expanded_path

                # Test connection
                if prompt_yes_no("Test BigQuery connection?", default=True):
                    print("Testing connection...")
                    if test_bigquery_connection(project_id, expanded_path):
                        print_success("BigQuery connection successful!")
                    else:
                        if not prompt_yes_no("Connection failed. Continue anyway?", default=False):
                            continue
                break
            else:
                print_error(f"File not found: {expanded_path}")

    # ========================================================================
    # AI Integration
    # ========================================================================
    print_header("2. AI Integration (Required for ai-* tools)")

    use_ai = prompt_yes_no("Do you want to use AI-powered utilities?", default=True)

    if use_ai:
        print("\nAnthrop Claude API:")
        print("  Get key at: https://console.anthropic.com/")

        anthropic_key = prompt(
            "Anthropic API key (starts with 'sk-ant-')",
            required=False
        )
        if anthropic_key:
            config['ANTHROPIC_API_KEY'] = anthropic_key

        if prompt_yes_no("Also use OpenAI models?", default=False):
            print("\nOpenAI API:")
            print("  Get key at: https://platform.openai.com/api-keys")

            openai_key = prompt(
                "OpenAI API key (starts with 'sk-')",
                required=False
            )
            if openai_key:
                config['OPENAI_API_KEY'] = openai_key

    # ========================================================================
    # Observability
    # ========================================================================
    print_header("3. Observability (Optional)")

    enable_obs = prompt_yes_no("Enable observability (metrics, logging)?", default=False)

    if enable_obs:
        config['METRICS_ENABLED'] = 'true'

        # Log format
        log_format = prompt(
            "Log format (text or json)",
            default="text"
        )
        config['LOG_FORMAT'] = log_format

        # Log level
        log_level = prompt(
            "Log level (DEBUG, INFO, WARNING, ERROR)",
            default="INFO"
        )
        config['LOG_LEVEL'] = log_level

        # External services
        if prompt_yes_no("Integrate with Datadog?", default=False):
            dd_key = prompt("Datadog API key", required=False)
            if dd_key:
                config['DATADOG_API_KEY'] = dd_key

        if prompt_yes_no("Integrate with Sentry?", default=False):
            sentry_dsn = prompt("Sentry DSN", required=False)
            if sentry_dsn:
                config['SENTRY_DSN'] = sentry_dsn

    # ========================================================================
    # Cache Configuration
    # ========================================================================
    print_header("4. Cache Configuration (Optional)")

    use_cache = prompt_yes_no("Enable metadata caching? (Recommended)", default=True)

    if use_cache:
        cache_dir = prompt(
            "Cache directory",
            default="~/.cache/decentclaude"
        )
        config['CACHE_DIR'] = cache_dir

        cache_ttl = prompt(
            "Cache TTL in seconds",
            default="3600"
        )
        config['CACHE_TTL'] = cache_ttl

    # ========================================================================
    # Knowledge Base
    # ========================================================================
    print_header("5. Knowledge Base (Optional)")

    if prompt_yes_no("Configure knowledge base?", default=False):
        kb_dir = prompt(
            "Knowledge base directory",
            default="~/.decentclaude/kb"
        )
        config['KB_DIR'] = kb_dir

    # ========================================================================
    # Workflow Defaults
    # ========================================================================
    print_header("6. Workflow Defaults (Optional)")

    if prompt_yes_no("Set workflow defaults?", default=False):
        workflow_dir = prompt(
            "Workflow output directory",
            default="./workflow-outputs"
        )
        config['WORKFLOW_OUTPUT_DIR'] = workflow_dir

        dq_threshold = prompt(
            "Data quality threshold (percentage)",
            default="80"
        )
        config['DATA_QUALITY_THRESHOLD'] = dq_threshold

        cost_threshold = prompt(
            "Query cost threshold (USD)",
            default="1.00"
        )
        config['QUERY_COST_THRESHOLD'] = cost_threshold

    # ========================================================================
    # Write .env file
    # ========================================================================
    print_header("7. Writing Configuration")

    print(f"\nConfiguration summary:")
    print(f"  Settings configured: {len(config)}")
    print(f"  Output file: {env_file}")

    if not prompt_yes_no("\nWrite configuration to .env file?", default=True):
        print("Cancelled. No changes made.")
        sys.exit(0)

    try:
        with open(env_file, 'w') as f:
            f.write("# DecentClaude Environment Configuration\n")
            f.write(f"# Generated by config-wizard on {os.popen('date').read().strip()}\n")
            f.write("# Edit this file or re-run wizard: mayor config init\n\n")

            # Write in logical groups
            if any(k.startswith('GOOGLE') for k in config):
                f.write("# BigQuery Configuration\n")
                for key in ['GOOGLE_CLOUD_PROJECT', 'GOOGLE_DATASET', 'GOOGLE_APPLICATION_CREDENTIALS']:
                    if key in config:
                        f.write(f"{key}={config[key]}\n")
                f.write("\n")

            if any('ANTHROPIC' in k or 'OPENAI' in k for k in config):
                f.write("# AI Integration\n")
                for key in ['ANTHROPIC_API_KEY', 'OPENAI_API_KEY']:
                    if key in config:
                        f.write(f"{key}={config[key]}\n")
                f.write("\n")

            if any('METRICS' in k or 'LOG' in k or 'DATADOG' in k or 'SENTRY' in k for k in config):
                f.write("# Observability\n")
                for key in ['METRICS_ENABLED', 'LOG_FORMAT', 'LOG_LEVEL', 'DATADOG_API_KEY', 'SENTRY_DSN']:
                    if key in config:
                        f.write(f"{key}={config[key]}\n")
                f.write("\n")

            if 'CACHE_DIR' in config or 'CACHE_TTL' in config:
                f.write("# Cache\n")
                for key in ['CACHE_DIR', 'CACHE_TTL']:
                    if key in config:
                        f.write(f"{key}={config[key]}\n")
                f.write("\n")

            if 'KB_DIR' in config:
                f.write("# Knowledge Base\n")
                f.write(f"KB_DIR={config['KB_DIR']}\n\n")

            if 'WORKFLOW_OUTPUT_DIR' in config:
                f.write("# Workflow Defaults\n")
                for key in ['WORKFLOW_OUTPUT_DIR', 'DATA_QUALITY_THRESHOLD', 'QUERY_COST_THRESHOLD']:
                    if key in config:
                        f.write(f"{key}={config[key]}\n")
                f.write("\n")

        print_success(f"Configuration written to: {env_file}")

        # Next steps
        print_header("Next Steps")
        print("1. Review and edit .env file if needed")
        print("2. Load configuration: source .env  (or restart shell)")
        print("3. Verify setup: mayor config validate")
        print("4. Start using DecentClaude: mayor list")
        print(f"\n{GREEN}Setup complete!{NC}\n")

    except Exception as e:
        print_error(f"Failed to write .env file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Cancelled by user.{NC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
