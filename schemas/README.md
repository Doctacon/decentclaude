# DecentClaude Tool Output Schemas

This directory contains JSON Schema definitions for all DecentClaude tool outputs.

## Overview

All schemas use **JSON Schema Draft 2020-12** format and define the structure of tool outputs in machine-readable format. These schemas enable:

- **MCP Server Integration**: Claude Code can understand tool outputs via Model Context Protocol
- **Validation**: Programmatic validation of tool output correctness
- **Documentation**: Self-documenting APIs with typed outputs
- **AI Integration**: LLMs can parse structured outputs reliably

## Available Schemas

### BigQuery Tools

| Schema | Tool | Description |
|--------|------|-------------|
| `bq-profile.json` | `mayor bq profile` | Comprehensive table profiling results with statistics, quality scores, and anomaly detection |
| `bq-explain.json` | `mayor bq explain` | Query execution plan analysis with bottlenecks and optimization suggestions |
| `bq-optimize.json` | `mayor bq optimize` | Automated query optimization recommendations with before/after comparisons |
| `bq-validate.json` | `mayor bq validate` | SQL syntax and semantic validation with error locations and suggestions |
| `bq-lineage.json` | `mayor bq lineage` | Table dependency graphs with upstream/downstream tracking and column-level lineage |

### Workflows

| Schema | Workflow | Description |
|--------|----------|-------------|
| `data-quality-audit.json` | `mayor workflow run data-quality-audit` | Multi-dimensional DQ assessment across datasets |
| `schema-migration.json` | `mayor workflow run schema-migration` | Schema change analysis with migration plans and rollback strategies |

### AI Tools

| Schema | Tool | Description |
|--------|------|-------------|
| `ai-generate.json` | `mayor ai generate` | LLM-powered code generation with alternatives, explanations, and test cases |

### dbt Tools

| Schema | Tool | Description |
|--------|------|-------------|
| `dbt-test.json` | `mayor dbt test` | dbt test execution results with pass/fail details and remediation suggestions |

## Schema Structure

Each schema follows this general structure:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://decentclaude.com/schemas/<tool-name>.json",
  "title": "Human-readable title",
  "description": "Schema description",
  "type": "object",
  "required": ["field1", "field2"],
  "properties": {
    "field1": {
      "type": "string",
      "description": "Field description"
    },
    ...
  }
}
```

## Using Schemas

### Validation

Validate tool output against schema using Python:

```python
import json
import jsonschema

# Load schema
with open('schemas/bq-profile.json') as f:
    schema = json.load(f)

# Load tool output
with open('output.json') as f:
    data = json.load(f)

# Validate
jsonschema.validate(data, schema)
```

### MCP Server

The MCP server automatically loads these schemas to expose tools to Claude Code:

```python
from lib.mcp_adapter import load_schemas

schemas = load_schemas('schemas/')
# Schemas used to define tool outputs in MCP protocol
```

### Documentation Generation

Generate API documentation from schemas:

```bash
mayor docs generate-api --schemas schemas/
```

## Schema Guidelines

When creating new schemas:

1. **Use Draft 2020-12**: Always specify `"$schema": "https://json-schema.org/draft/2020-12/schema"`
2. **Include $id**: Use format `https://decentclaude.com/schemas/<tool-name>.json`
3. **Require Core Fields**: Mark essential fields as required
4. **Describe Everything**: Add descriptions for all properties
5. **Use Enums**: For fixed sets of values (e.g., severity levels)
6. **Include Examples**: Add example values where helpful
7. **Nest Logically**: Group related fields in nested objects
8. **Version Carefully**: Schema changes should be backwards-compatible when possible

## Common Patterns

### Metadata Block

Most schemas include a metadata block for operational info:

```json
"metadata": {
  "type": "object",
  "properties": {
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "execution_time_seconds": {
      "type": "number"
    },
    "version": {
      "type": "string"
    }
  }
}
```

### Error Reporting

Tools that can fail use standardized error structures:

```json
"errors": {
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "type": {"type": "string"},
      "message": {"type": "string"},
      "severity": {
        "type": "string",
        "enum": ["low", "medium", "high", "critical"]
      }
    }
  }
}
```

### Quality Scores

Quality-related tools use 0-100 scale consistently:

```json
"quality_score": {
  "type": "number",
  "minimum": 0,
  "maximum": 100,
  "description": "Quality score (0-100)"
}
```

## Testing Schemas

Run schema validation tests:

```bash
# Validate all schemas are valid JSON Schema
mayor test schemas

# Test schemas against sample outputs
mayor test schemas --with-examples
```

## Contributing

When adding new tools:

1. Create schema in `schemas/<tool-name>.json`
2. Update `catalog.json` with new schema entry
3. Update this README with schema documentation
4. Add to MCP server tool registry
5. Include example output in tests

## References

- [JSON Schema Specification](https://json-schema.org/draft/2020-12/json-schema-core.html)
- [Understanding JSON Schema](https://json-schema.org/understanding-json-schema/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Tool Registry](../lib/tool_registry.json)
