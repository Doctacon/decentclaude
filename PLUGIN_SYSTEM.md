# Plugin System Architecture

## Overview

The DecentClaude plugin system provides a comprehensive architecture for extending data engineering workflows through community-contributed plugins.

## Components

### Core Module (`plugins/core/`)

#### 1. Base Classes (`base.py`)
- `PluginInterface`: Base interface for all plugins
- `HookPlugin`: Hook extension plugins
- `ValidatorPlugin`: Data validation plugins
- `QualityCheckPlugin`: Quality check plugins
- `IntegrationPlugin`: Third-party integration plugins
- `PluginType`: Enumeration of plugin types
- `PluginStatus`: Plugin lifecycle states

#### 2. Manifest Management (`manifest.py`)
- `ManifestSchema`: Schema definition for plugin manifests
- `ManifestValidator`: Validates manifests against schema
- `ManifestLoader`: Loads manifests from JSON/YAML files
- `create_manifest_template()`: Creates manifest templates

#### 3. Version Compatibility (`version.py`)
- `SemanticVersion`: Semantic version parsing and comparison
- `VersionChecker`: Checks plugin compatibility with system version
- `parse_version_constraint()`: Parses version constraints

#### 4. Dependency Resolution (`dependencies.py`)
- `DependencyResolver`: Resolves plugin dependencies using topological sort
- `DependencyTree`: Visualizes dependency relationships
- `CircularDependencyError`: Raised on circular dependencies
- `MissingDependencyError`: Raised when dependencies are missing

#### 5. Plugin Loading (`loader.py`)
- `PluginDiscovery`: Discovers plugins in configured directories
- `PluginLoader`: Dynamically loads plugin classes
- `PluginManager`: Manages plugin lifecycle and orchestrates loading
- `PluginLoadError`: Raised when loading fails

#### 6. Configuration (`config.py`)
- `PluginConfig`: Manages configuration for a single plugin
- `ConfigManager`: Manages configurations for all plugins
- `ConfigError`: Raised on configuration errors
- `create_default_config()`: Creates default configuration template

## Features

### 1. Plugin Discovery
- Automatic discovery of plugins in `plugins/builtin/` and `plugins/external/`
- Manifest-based plugin metadata
- Support for JSON and YAML manifests

### 2. Standard API
- Well-defined base classes for each plugin type
- Consistent lifecycle methods: `initialize()`, `validate()`, `execute()`, `cleanup()`
- Type-safe plugin interfaces

### 3. Configuration Management
- JSON-based configuration files
- JSON Schema validation for plugin configs
- Nested configuration access with dot notation
- Config persistence and import/export

### 4. Dependency Resolution
- Automatic dependency ordering using topological sort
- Circular dependency detection
- Missing dependency validation
- Dependency tree visualization

### 5. Version Compatibility
- Semantic versioning (MAJOR.MINOR.PATCH)
- Compatibility checks between plugins and system
- Version constraint parsing
- Graceful handling of version mismatches

### 6. Plugin Management CLI
- List available plugins
- Show plugin details
- Enable/disable plugins
- Validate plugin manifests
- View dependency trees

## Plugin Types

### Hook Plugins
Extend Claude Code hooks with custom functionality.

**Use Cases:**
- Custom pre-commit hooks
- Specialized validation workflows
- Integration with external tools

### Validator Plugins
Validate data, SQL, or other inputs.

**Use Cases:**
- SQL syntax validation
- Schema validation
- Data type checking
- Custom business rule validation

### Quality Check Plugins
Run data quality checks.

**Use Cases:**
- Schema existence checks
- Data completeness checks
- Data consistency validation
- Custom quality metrics

### Integration Plugins
Integrate with third-party tools and services.

**Use Cases:**
- BigQuery integrations
- Snowflake connections
- Airflow DAG generation
- Custom tool integrations

## Architecture Decisions

### 1. Dynamic Loading
Plugins are loaded dynamically at runtime using Python's `importlib` to avoid requiring restarts.

### 2. Manifest-Based Discovery
Plugin metadata is defined in manifest files (JSON/YAML) separate from code, enabling validation before loading.

### 3. Dependency Graph
Plugins are loaded in dependency order determined by topological sort, ensuring dependencies are always loaded first.

### 4. Semantic Versioning
Strict semantic versioning ensures compatibility between plugins and the system, preventing version conflicts.

### 5. Configuration Separation
Plugin configuration is separated from code, allowing users to customize behavior without modifying plugin source.

## Directory Structure

```
plugins/
├── core/                      # Plugin system core
│   ├── __init__.py           # Core module exports
│   ├── base.py               # Base classes and interfaces
│   ├── manifest.py           # Manifest handling
│   ├── version.py            # Version compatibility
│   ├── dependencies.py       # Dependency resolution
│   ├── loader.py             # Plugin loading
│   └── config.py             # Configuration management
├── builtin/                  # Built-in plugins
│   ├── sql_validator/
│   │   ├── __init__.py
│   │   └── plugin.json
│   └── schema_check/
│       ├── __init__.py
│       └── plugin.json
├── external/                 # Third-party plugins
└── config.json              # Plugin configurations
```

## Built-in Plugins

### 1. SQL Validator
- **Type**: Validator
- **Purpose**: Validates SQL syntax using sqlparse
- **Dependencies**: None
- **Configuration**: `strict_mode` (boolean)

### 2. Schema Check
- **Type**: Quality Check
- **Purpose**: Checks for existence of schema files
- **Dependencies**: None
- **Configuration**: `schema_paths` (array of strings)

## Usage Examples

### Programmatic Usage

```python
from plugins.core import PluginManager

# Initialize plugin manager
manager = PluginManager(
    [Path("plugins/builtin"), Path("plugins/external")],
    system_version="1.0.0"
)

# Discover and load all plugins
manager.discover_plugins()
manager.load_all_plugins()

# Get a specific plugin
validator = manager.get_plugin("sql_validator")

# Execute plugin
result = validator.execute({"sql": "SELECT * FROM users"})
```

### CLI Usage

```bash
# List all plugins
bin/plugin-manager list

# Show plugin info
bin/plugin-manager info sql_validator

# Validate a plugin
bin/plugin-manager validate plugins/external/my_plugin

# View dependencies
bin/plugin-manager tree
```

## Development Workflow

1. **Create Plugin Directory**
   ```bash
   mkdir -p plugins/external/my_plugin
   ```

2. **Implement Plugin Class**
   ```python
   from plugins.core.base import ValidatorPlugin

   class MyValidator(ValidatorPlugin):
       def initialize(self, config): ...
       def validate(self): ...
       def execute(self, context): ...
       def validate_input(self, input_data): ...
       def get_validation_errors(self): ...
   ```

3. **Create Manifest**
   ```json
   {
     "name": "my_validator",
     "version": "1.0.0",
     "type": "validator",
     "entry_point": "__init__.MyValidator"
   }
   ```

4. **Test Plugin**
   ```bash
   bin/plugin-manager validate plugins/external/my_plugin
   ```

5. **Enable Plugin**
   ```bash
   bin/plugin-manager enable my_validator
   ```

## Extension Points

The plugin system can be extended with:

1. **New Plugin Types**: Add new `PluginInterface` subclasses
2. **Custom Loaders**: Implement alternative loading strategies
3. **Additional Validators**: Create new manifest validators
4. **Config Formats**: Support additional configuration formats
5. **Discovery Methods**: Implement alternative discovery mechanisms

## Performance Considerations

1. **Lazy Loading**: Plugins are loaded only when requested
2. **Caching**: Loaded modules are cached to avoid re-parsing
3. **Minimal Dependencies**: Core system has minimal dependencies
4. **Dependency Ordering**: Efficient topological sort for load order

## Security Considerations

1. **Manifest Validation**: All manifests validated before loading
2. **Version Checking**: Compatibility verified before initialization
3. **Sandboxing**: Plugins run in controlled environment (future enhancement)
4. **Permission Model**: Plugin capabilities defined in manifest (future enhancement)

## Future Enhancements

1. **Hot Reloading**: Reload plugins without restart
2. **Plugin Marketplace**: Central repository for community plugins
3. **Async Support**: Async plugin execution
4. **Event System**: Plugin communication via events
5. **Permission Model**: Fine-grained plugin permissions
6. **Sandboxing**: Isolated plugin execution environments
7. **Plugin Testing Framework**: Automated testing utilities
8. **Plugin Templates**: Scaffolding for quick plugin creation

## Documentation

- [Plugin Development Guide](docs/PLUGIN_DEVELOPMENT.md) - Complete guide to creating plugins
- [README](README.md) - Main project documentation
- [Examples](examples/plugin_usage.py) - Programmatic usage examples

## License

Plugin system is available under MIT license.
