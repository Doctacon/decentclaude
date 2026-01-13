"""
DecentClaude Plugin System Core

Provides plugin architecture for extensibility including:
- Plugin discovery and loading
- Standard plugin API
- Configuration management
- Dependency resolution
- Version compatibility
"""

from .base import (
    PluginInterface,
    PluginType,
    PluginStatus,
    HookPlugin,
    ValidatorPlugin,
    QualityCheckPlugin,
    IntegrationPlugin
)

from .manifest import (
    ManifestSchema,
    ManifestValidator,
    ManifestLoader,
    create_manifest_template
)

from .version import (
    SemanticVersion,
    VersionChecker,
    parse_version_constraint
)

from .dependencies import (
    DependencyResolver,
    DependencyTree,
    DependencyError,
    CircularDependencyError,
    MissingDependencyError
)

from .loader import (
    PluginDiscovery,
    PluginLoader,
    PluginManager,
    PluginLoadError
)

from .config import (
    PluginConfig,
    ConfigManager,
    ConfigError,
    create_default_config
)

__all__ = [
    # Base classes
    "PluginInterface",
    "PluginType",
    "PluginStatus",
    "HookPlugin",
    "ValidatorPlugin",
    "QualityCheckPlugin",
    "IntegrationPlugin",

    # Manifest
    "ManifestSchema",
    "ManifestValidator",
    "ManifestLoader",
    "create_manifest_template",

    # Version
    "SemanticVersion",
    "VersionChecker",
    "parse_version_constraint",

    # Dependencies
    "DependencyResolver",
    "DependencyTree",
    "DependencyError",
    "CircularDependencyError",
    "MissingDependencyError",

    # Loader
    "PluginDiscovery",
    "PluginLoader",
    "PluginManager",
    "PluginLoadError",

    # Config
    "PluginConfig",
    "ConfigManager",
    "ConfigError",
    "create_default_config",
]

__version__ = "1.0.0"
