"""
Plugin configuration management.

Manages plugin configuration loading, validation, and persistence.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigError(Exception):
    """Raised when configuration operations fail"""
    pass


class PluginConfig:
    """Manages configuration for a single plugin"""

    def __init__(self, plugin_name: str, config_data: Optional[Dict[str, Any]] = None):
        """
        Initialize plugin configuration.

        Args:
            plugin_name: Name of the plugin
            config_data: Configuration data
        """
        self.plugin_name = plugin_name
        self.config_data = config_data or {}
        self.schema: Optional[Dict[str, Any]] = None

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports nested keys with dots, e.g., 'database.host')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config_data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key (supports nested keys)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config_data

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def update(self, updates: Dict[str, Any]) -> None:
        """
        Update configuration with a dict of values.

        Args:
            updates: Dict of configuration updates
        """
        self._deep_update(self.config_data, updates)

    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Deep update of nested dictionaries"""
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value

    def validate(self, schema: Dict[str, Any]) -> bool:
        """
        Validate configuration against a JSON schema.

        Args:
            schema: JSON schema to validate against

        Returns:
            True if valid, False otherwise
        """
        self.schema = schema
        try:
            import jsonschema
            jsonschema.validate(instance=self.config_data, schema=schema)
            return True
        except ImportError:
            print("Warning: jsonschema not installed, skipping validation")
            return True
        except Exception as e:
            print(f"Configuration validation failed for {self.plugin_name}: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Get configuration as a dictionary.

        Returns:
            Configuration dict
        """
        return self.config_data.copy()


class ConfigManager:
    """Manages configurations for all plugins"""

    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration manager.

        Args:
            config_file: Path to main configuration file
        """
        self.config_file = config_file or Path("plugins/config.json")
        self.configs: Dict[str, PluginConfig] = {}
        self._load_configs()

    def _load_configs(self) -> None:
        """Load configurations from file"""
        if not self.config_file.exists():
            return

        try:
            with open(self.config_file, 'r') as f:
                all_configs = json.load(f)

            for plugin_name, config_data in all_configs.items():
                self.configs[plugin_name] = PluginConfig(plugin_name, config_data)

        except Exception as e:
            raise ConfigError(f"Failed to load config from {self.config_file}: {e}")

    def save_configs(self) -> None:
        """Save all configurations to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            all_configs = {
                name: config.to_dict()
                for name, config in self.configs.items()
            }

            with open(self.config_file, 'w') as f:
                json.dump(all_configs, f, indent=2)

        except Exception as e:
            raise ConfigError(f"Failed to save config to {self.config_file}: {e}")

    def get_config(self, plugin_name: str) -> PluginConfig:
        """
        Get configuration for a plugin.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin configuration
        """
        if plugin_name not in self.configs:
            self.configs[plugin_name] = PluginConfig(plugin_name)

        return self.configs[plugin_name]

    def set_config(self, plugin_name: str, config_data: Dict[str, Any]) -> None:
        """
        Set configuration for a plugin.

        Args:
            plugin_name: Name of the plugin
            config_data: Configuration data
        """
        self.configs[plugin_name] = PluginConfig(plugin_name, config_data)

    def update_config(self, plugin_name: str, updates: Dict[str, Any]) -> None:
        """
        Update configuration for a plugin.

        Args:
            plugin_name: Name of the plugin
            updates: Configuration updates
        """
        config = self.get_config(plugin_name)
        config.update(updates)

    def delete_config(self, plugin_name: str) -> None:
        """
        Delete configuration for a plugin.

        Args:
            plugin_name: Name of the plugin
        """
        if plugin_name in self.configs:
            del self.configs[plugin_name]

    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all plugin configurations.

        Returns:
            Dict of plugin configurations
        """
        return {
            name: config.to_dict()
            for name, config in self.configs.items()
        }

    def export_config(self, plugin_name: str, output_path: Path) -> None:
        """
        Export a plugin's configuration to a file.

        Args:
            plugin_name: Name of the plugin
            output_path: Path to output file
        """
        config = self.get_config(plugin_name)
        try:
            with open(output_path, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
        except Exception as e:
            raise ConfigError(f"Failed to export config for {plugin_name}: {e}")

    def import_config(self, plugin_name: str, input_path: Path) -> None:
        """
        Import a plugin's configuration from a file.

        Args:
            plugin_name: Name of the plugin
            input_path: Path to input file
        """
        try:
            with open(input_path, 'r') as f:
                config_data = json.load(f)

            self.set_config(plugin_name, config_data)

        except Exception as e:
            raise ConfigError(f"Failed to import config for {plugin_name}: {e}")


def create_default_config() -> Dict[str, Any]:
    """
    Create a default plugin configuration template.

    Returns:
        Default configuration dict
    """
    return {
        "enabled": True,
        "priority": 10,
        "settings": {}
    }
