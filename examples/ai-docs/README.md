# AI-Docs Examples

This directory contains examples of auto-generated documentation using the `ai-docs` tool.

## What is ai-docs?

`ai-docs` is an automated documentation generator for BigQuery models and tables. It can:

- Generate model descriptions from SQL files (dbt/SQLMesh)
- Create column-level documentation
- Build data dictionaries
- Generate ERD diagrams (Mermaid format)
- Write operational runbooks
- Auto-update docs on file changes (watch mode)

## Quick Start

### Generate documentation for a SQL model

```bash
bin/data-utils/ai-docs examples/sql/dbt_model_example.sql
```

### Generate a data dictionary for a BigQuery table

```bash
bin/data-utils/ai-docs project.dataset.table --type=dictionary
```

### Generate all documentation types

```bash
bin/data-utils/ai-docs examples/sql/dbt_model_example.sql --type=all --output=docs/
```

### Watch mode (auto-regenerate on changes)

```bash
bin/data-utils/ai-docs models/staging/stg_orders.sql --watch
```

## Documentation Types

### Model Documentation

Extracts configuration, dependencies, and structure from SQL models.

**Example:**
```bash
bin/data-utils/ai-docs examples/sql/dbt_model_example.sql
```

**Output includes:**
- Model configuration (materialization, partitioning, clustering)
- Dependencies (sources, refs)
- CTEs and their purposes
- Table metadata (for BigQuery tables)
- Lineage information

### Data Dictionary

Generates comprehensive column-level documentation for BigQuery tables.

**Example:**
```bash
bin/data-utils/ai-docs project.dataset.orders --type=dictionary
```

**Output includes:**
- Table description
- Column names, types, and modes
- Column descriptions
- Sample values

### ERD Diagram

Generates Entity-Relationship Diagrams in Mermaid format.

**Example:**
```bash
bin/data-utils/ai-docs project.dataset.orders --type=erd
```

**Output:** Mermaid diagram showing table relationships

### Runbook

Generates operational runbooks for data pipelines.

**Example:**
```bash
bin/data-utils/ai-docs project.dataset.orders --type=runbook
```

**Output includes:**
- Overview and ownership
- Schedule and dependencies
- Monitoring and data quality checks
- Troubleshooting guide
- Maintenance procedures

## Output Formats

### Markdown (default)

```bash
bin/data-utils/ai-docs examples/sql/dbt_model_example.sql
```

### JSON

```bash
bin/data-utils/ai-docs examples/sql/dbt_model_example.sql --format=json
```

### YAML

```bash
bin/data-utils/ai-docs examples/sql/dbt_model_example.sql --format=yaml
```

## Examples in this Directory

- `dbt_model_docs.md` - Auto-generated documentation for a dbt model
- `data_dictionary_example.md` - Auto-generated data dictionary
- `erd_example.md` - Auto-generated ERD diagram
- `runbook_example.md` - Auto-generated runbook

## Integration with CI/CD

You can integrate `ai-docs` into your CI/CD pipeline to automatically update documentation on code changes.

**Example GitHub Action:**

```yaml
name: Update Documentation

on:
  push:
    paths:
      - 'models/**/*.sql'

jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install google-cloud-bigquery pyyaml

      - name: Generate documentation
        run: |
          bin/data-utils/ai-docs models/ --recursive --type=all --output=docs/

      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add docs/
          git commit -m "Auto-update documentation" || exit 0
          git push
```

## Requirements

- Python 3.7+
- `google-cloud-bigquery` (for BigQuery integration)
- `pyyaml` (for YAML output format)

Install dependencies:

```bash
pip install google-cloud-bigquery pyyaml
```

## Tips

1. **Use watch mode during development** to see documentation updates in real-time as you modify SQL models.

2. **Generate all types** when creating comprehensive documentation for a new model.

3. **Use JSON format** when integrating with other tools or scripts.

4. **Combine with templates** to customize the documentation structure.

5. **Integrate with Git hooks** to enforce documentation updates before commits.
