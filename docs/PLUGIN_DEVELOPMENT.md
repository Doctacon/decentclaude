# Plugin Development Guide

DecentClaude provides a powerful plugin system that enables community extensions for data engineering workflows, quality checks, validators, and integrations.

## Table of Contents

- [Overview](#overview)
- [Plugin Types](#plugin-types)
- [Getting Started](#getting-started)
- [Plugin Structure](#plugin-structure)
- [Creating a Plugin](#creating-a-plugin)
- [Plugin Manifest](#plugin-manifest)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Version Compatibility](#version-compatibility)
- [Testing](#testing)
- [Publishing](#publishing)

## Overview

The plugin system provides:

- **Plugin Discovery**: Automatic discovery of plugins in configured directories
- **Standard API**: Well-defined base classes for different plugin types
- **Configuration Management**: JSON-based configuration with schema validation
- **Dependency Resolution**: Automatic dependency ordering and loading
- **Version Compatibility**: Semantic versioning with compatibility checks
- **CLI Management**: Command-line tools for plugin management

## Plugin Types

DecentClaude supports several plugin types:

### 1. Hook Plugins
Extend Claude Code hooks with custom functionality.

```python
from plugins.core import HookPlugin

class MyHookPlugin(HookPlugin):
    def get_hook_config(self) -> Dict[str, Any]:
        return {
            "my-custom-hook": {
                "command": "python scripts/my_hook.py",
                "description": "My custom hook"
            }
        }
```

### 2. Validator Plugins
Validate data, SQL, or other inputs.

```python
from plugins.core import ValidatorPlugin

class MyValidatorPlugin(ValidatorPlugin):
    def validate_input(self, input_data: Any) -> bool:
        # Validation logic
        return True

    def get_validation_errors(self) -> List[str]:
        return self.errors
```

### 3. Quality Check Plugins
Run data quality checks.

```python
from plugins.core import QualityCheckPlugin

class MyQualityCheckPlugin(QualityCheckPlugin):
    def run_check(self) -> bool:
        # Quality check logic
        self.passed = True
        self.message = "Check passed"
        return self.passed
```

### 4. Integration Plugins
Integrate with third-party tools.

```python
from plugins.core import IntegrationPlugin

class MyIntegrationPlugin(IntegrationPlugin):
    def connect(self) -> bool:
        # Connection logic
        return True

    def disconnect(self) -> None:
        pass

    def is_available(self) -> bool:
        return True
```

## Getting Started

### Directory Structure

Create your plugin in one of these locations:

- `plugins/builtin/` - For builtin plugins (shipped with DecentClaude)
- `plugins/external/` - For third-party community plugins

```
plugins/
├── builtin/
│   └── my_plugin/
│       ├── __init__.py
│       ├── plugin.json
│       └── README.md
└── external/
    └── community_plugin/
        ├── __init__.py
        ├── plugin.json
        └── README.md
```

## Plugin Structure

Each plugin must have:

1. **Plugin directory**: Named after your plugin (e.g., `my_plugin/`)
2. **Entry point**: Python file with plugin class (usually `__init__.py`)
3. **Manifest**: `plugin.json` or `plugin.yaml` with metadata

Minimal structure:

```
my_plugin/
├── __init__.py      # Plugin implementation
└── plugin.json      # Plugin manifest
```

## Creating a Plugin

### Step 1: Create Plugin Directory

```bash
mkdir -p plugins/external/my_validator
cd plugins/external/my_validator
```

### Step 2: Implement Plugin Class

Create `__init__.py`:

```python
"""
My Validator Plugin

Description of what your plugin does.
"""

from typing import Any, Dict, List
import sys
from pathlib import Path

# Add core module to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.base import ValidatorPlugin


class MyValidatorPlugin(ValidatorPlugin):
    """Custom validator plugin"""

    def __init__(self, manifest: Dict[str, Any]):
        super().__init__(manifest)
        self.errors = []

    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with configuration.

        Args:
            config: Plugin configuration dict

        Returns:
            True if initialization successful
        """
        self.config = config
        # Initialization logic here
        return True

    def validate(self) -> bool:
        """
        Validate plugin is ready to use.

        Returns:
            True if plugin is valid
        """
        # Validation logic here
        return True

    def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute the plugin's main functionality.

        Args:
            context: Execution context

        Returns:
            Plugin result
        """
        data = context.get("data")
        return self.validate_input(data)

    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data.

        Args:
            input_data: Data to validate

        Returns:
            True if valid
        """
        self.errors = []

        # Your validation logic here
        if not input_data:
            self.errors.append("Input data is empty")
            return False

        return True

    def get_validation_errors(self) -> List[str]:
        """Get validation errors"""
        return self.errors
```

### Step 3: Create Plugin Manifest

Create `plugin.json`:

```json
{
  "name": "my_validator",
  "version": "1.0.0",
  "type": "validator",
  "entry_point": "__init__.MyValidatorPlugin",
  "description": "My custom validator plugin",
  "author": "Your Name",
  "license": "MIT",
  "homepage": "https://github.com/yourname/my_validator",
  "dependencies": [],
  "requires_version": "1.0.0",
  "tags": ["validation", "custom"],
  "config_schema": {
    "type": "object",
    "properties": {
      "strict_mode": {
        "type": "boolean",
        "description": "Enable strict validation",
        "default": false
      }
    }
  }
}
```

## Plugin Manifest

The manifest file describes your plugin's metadata and requirements.

### Required Fields

- `name`: Unique plugin identifier (lowercase, hyphens/underscores only)
- `version`: Semantic version (e.g., "1.0.0")
- `type`: Plugin type (hook, validator, quality_check, cli_utility, integration, custom)
- `entry_point`: Python class path (e.g., "module.ClassName")

### Optional Fields

- `description`: Brief description of the plugin
- `author`: Plugin author name
- `license`: License identifier (e.g., "MIT")
- `homepage`: Plugin homepage URL
- `dependencies`: List of plugin dependencies
- `requires_version`: Minimum DecentClaude version
- `tags`: List of tags for categorization
- `config_schema`: JSON schema for configuration validation

### Example Manifest

```json
{
  "name": "bigquery_profiler",
  "version": "2.1.0",
  "type": "integration",
  "entry_point": "profiler.BigQueryProfiler",
  "description": "Profiles BigQuery tables and generates statistics",
  "author": "Data Team",
  "license": "Apache-2.0",
  "homepage": "https://github.com/company/bq-profiler",
  "dependencies": ["sql_validator"],
  "requires_version": "1.0.0",
  "tags": ["bigquery", "profiling", "statistics"],
  "config_schema": {
    "type": "object",
    "properties": {
      "project_id": {
        "type": "string",
        "description": "GCP project ID"
      },
      "sample_size": {
        "type": "integer",
        "description": "Number of rows to sample",
        "default": 1000
      }
    },
    "required": ["project_id"]
  }
}
```

## Configuration

### Plugin Configuration

Plugins are configured in `plugins/config.json`:

```json
{
  "my_validator": {
    "enabled": true,
    "priority": 10,
    "settings": {
      "strict_mode": true,
      "custom_option": "value"
    }
  }
}
```

### Accessing Configuration

In your plugin:

```python
def initialize(self, config: Dict[str, Any]) -> bool:
    self.config = config
    strict_mode = config.get("strict_mode", False)
    return True
```

### Configuration Schema

Define a JSON schema in your manifest to validate configuration:

```json
{
  "config_schema": {
    "type": "object",
    "properties": {
      "api_key": {
        "type": "string",
        "description": "API key for service"
      },
      "timeout": {
        "type": "integer",
        "minimum": 1,
        "maximum": 300,
        "default": 30
      }
    },
    "required": ["api_key"]
  }
}
```

## Dependencies

### Declaring Dependencies

List plugin dependencies in your manifest:

```json
{
  "dependencies": ["sql_validator", "schema_check"]
}
```

### Dependency Resolution

The plugin system automatically:

1. Validates all dependencies are available
2. Resolves load order using topological sort
3. Loads dependencies before dependent plugins
4. Detects circular dependencies

### Example with Dependencies

```json
{
  "name": "advanced_validator",
  "dependencies": ["sql_validator"],
  "requires_version": "1.0.0"
}
```

The system ensures `sql_validator` loads before `advanced_validator`.

## Version Compatibility

### Semantic Versioning

Plugins use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Compatibility Rules

Plugins are compatible with DecentClaude if:

1. Major version matches
2. Plugin version >= required version

Examples:

```
Plugin requires 1.2.0
System version 1.3.0 ✓ Compatible
System version 1.1.0 ✗ Incompatible
System version 2.0.0 ✗ Incompatible (major mismatch)
```

### Version Constraints

```json
{
  "requires_version": "1.2.0"
}
```

## Testing

### Unit Testing

Create tests for your plugin:

```python
import unittest
from my_plugin import MyValidatorPlugin

class TestMyValidator(unittest.TestCase):
    def setUp(self):
        manifest = {
            "name": "test",
            "version": "1.0.0",
            "type": "validator",
            "entry_point": "test.TestPlugin"
        }
        self.plugin = MyValidatorPlugin(manifest)
        self.plugin.initialize({})

    def test_validation(self):
        result = self.plugin.validate_input("test data")
        self.assertTrue(result)
```

### Validation

Validate your plugin before publishing:

```bash
bin/plugin-manager validate plugins/external/my_plugin
```

## Publishing

### Checklist

Before publishing your plugin:

- [ ] Plugin manifest is valid
- [ ] All required fields are present
- [ ] Version follows semantic versioning
- [ ] Dependencies are correctly declared
- [ ] Configuration schema is defined
- [ ] Plugin passes validation
- [ ] Documentation is complete
- [ ] Tests are passing

### Distribution

1. **GitHub Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial plugin version"
   git tag v1.0.0
   git push origin main --tags
   ```

2. **Installation Instructions**
   ```bash
   # Clone into external plugins directory
   cd plugins/external
   git clone https://github.com/yourname/my_plugin.git
   ```

3. **Enable Plugin**
   ```bash
   bin/plugin-manager enable my_plugin
   ```

## Plugin Management CLI

### List Plugins

```bash
bin/plugin-manager list
```

### Show Plugin Info

```bash
bin/plugin-manager info sql_validator
```

### Enable/Disable

```bash
bin/plugin-manager enable my_plugin
bin/plugin-manager disable my_plugin
```

### Validate Plugin

```bash
bin/plugin-manager validate plugins/external/my_plugin
```

### Show Dependencies

```bash
bin/plugin-manager deps advanced_validator
```

### Dependency Tree

```bash
bin/plugin-manager tree
```

## Examples

See builtin plugins for examples:

- `plugins/builtin/sql_validator/` - SQL validation
- `plugins/builtin/schema_check/` - Schema checking

## API Reference

### Base Classes

- `PluginInterface` - Base interface for all plugins
- `HookPlugin` - Hook extensions
- `ValidatorPlugin` - Data validation
- `QualityCheckPlugin` - Quality checks
- `IntegrationPlugin` - Third-party integrations

### Core Modules

- `plugins.core.base` - Base classes
- `plugins.core.manifest` - Manifest handling
- `plugins.core.loader` - Plugin loading
- `plugins.core.config` - Configuration
- `plugins.core.dependencies` - Dependency resolution
- `plugins.core.version` - Version checking

## Best Practices

1. **Single Responsibility**: Each plugin should do one thing well
2. **Clear Naming**: Use descriptive, lowercase names with hyphens
3. **Documentation**: Include docstrings and README
4. **Error Handling**: Provide clear error messages
5. **Configuration**: Make plugins configurable
6. **Testing**: Write comprehensive tests
7. **Versioning**: Follow semantic versioning strictly
8. **Dependencies**: Minimize dependencies when possible

## Troubleshooting

### Plugin Not Loading

1. Check manifest is valid: `bin/plugin-manager validate <path>`
2. Verify entry point exists
3. Check dependencies are available
4. Review version compatibility

### Import Errors

Ensure you add the core module to path:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.base import PluginInterface
```

### Configuration Issues

1. Verify config schema is valid JSON Schema
2. Check config file exists: `plugins/config.json`
3. Validate config against schema

## Support

For issues or questions:

- Check existing builtin plugins for examples
- Review plugin architecture in `plugins/core/`
- Open an issue on GitHub

## License

Plugin system is available under MIT license.
