"""
Plugin discovery and loading.

Discovers plugins from configured directories and loads them dynamically.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
import json

from .base import PluginInterface, PluginStatus
from .manifest import ManifestLoader, ManifestValidator
from .version import VersionChecker
from .dependencies import DependencyResolver, DependencyError


class PluginLoadError(Exception):
    """Raised when plugin loading fails"""
    pass


class PluginDiscovery:
    """Discovers plugins in configured directories"""

    def __init__(self, search_paths: List[Path]):
        """
        Initialize plugin discovery.

        Args:
            search_paths: List of directories to search for plugins
        """
        self.search_paths = search_paths

    def discover(self) -> List[Dict[str, Any]]:
        """
        Discover all plugins in search paths.

        Returns:
            List of discovered plugin manifests with metadata
        """
        discovered = []

        for search_path in self.search_paths:
            if not search_path.exists():
                continue

            for plugin_dir in search_path.iterdir():
                if not plugin_dir.is_dir():
                    continue

                plugin_info = self._load_plugin_info(plugin_dir)
                if plugin_info:
                    discovered.append(plugin_info)

        return discovered

    def _load_plugin_info(self, plugin_dir: Path) -> Optional[Dict[str, Any]]:
        """
        Load plugin information from a directory.

        Args:
            plugin_dir: Path to plugin directory

        Returns:
            Plugin info dict or None if invalid
        """
        manifest_files = ["plugin.json", "plugin.yaml", "plugin.yml"]
        manifest_path = None

        for manifest_file in manifest_files:
            path = plugin_dir / manifest_file
            if path.exists():
                manifest_path = path
                break

        if not manifest_path:
            return None

        manifest = ManifestLoader.load_from_file(manifest_path)
        if not manifest:
            return None

        validator = ManifestValidator()
        if not validator.validate(manifest):
            print(f"Invalid manifest in {plugin_dir}: {validator.get_errors()}")
            return None

        return {
            "manifest": manifest,
            "directory": plugin_dir,
            "manifest_path": manifest_path
        }


class PluginLoader:
    """Loads and instantiates plugins"""

    def __init__(self, version_checker: VersionChecker):
        """
        Initialize plugin loader.

        Args:
            version_checker: Version compatibility checker
        """
        self.version_checker = version_checker
        self.loaded_modules: Dict[str, Any] = {}

    def load_plugin(
        self,
        plugin_info: Dict[str, Any],
        config: Dict[str, Any]
    ) -> PluginInterface:
        """
        Load and instantiate a plugin.

        Args:
            plugin_info: Plugin information from discovery
            config: Plugin configuration

        Returns:
            Instantiated plugin

        Raises:
            PluginLoadError: If loading fails
        """
        manifest = plugin_info["manifest"]
        plugin_dir = plugin_info["directory"]

        is_compatible, message = self.version_checker.check_plugin_compatibility(
            manifest["name"],
            manifest.get("requires_version", "0.0.0")
        )

        if not is_compatible:
            raise PluginLoadError(message)

        entry_point = manifest["entry_point"]
        plugin_class = self._load_plugin_class(entry_point, plugin_dir)

        try:
            plugin_instance = plugin_class(manifest)
            plugin_instance.status = PluginStatus.LOADING

            if not plugin_instance.initialize(config):
                raise PluginLoadError(f"Plugin {manifest['name']} initialization failed")

            if not plugin_instance.validate():
                raise PluginLoadError(f"Plugin {manifest['name']} validation failed")

            plugin_instance.status = PluginStatus.LOADED
            return plugin_instance

        except Exception as e:
            raise PluginLoadError(f"Failed to load plugin {manifest['name']}: {e}")

    def _load_plugin_class(self, entry_point: str, plugin_dir: Path) -> Type[PluginInterface]:
        """
        Dynamically load a plugin class.

        Args:
            entry_point: Module path to plugin class (e.g., 'module.ClassName')
            plugin_dir: Plugin directory

        Returns:
            Plugin class

        Raises:
            PluginLoadError: If class cannot be loaded
        """
        try:
            parts = entry_point.rsplit('.', 1)
            if len(parts) != 2:
                raise PluginLoadError(f"Invalid entry_point format: {entry_point}")

            module_path, class_name = parts

            # Create a unique module name based on plugin directory
            unique_module_name = f"plugin_{plugin_dir.name}_{module_path}"

            if unique_module_name not in self.loaded_modules:
                # Handle __init__ modules
                if module_path == "__init__":
                    module_file = plugin_dir / "__init__.py"
                else:
                    module_file = plugin_dir / f"{module_path.replace('.', '/')}.py"
                    if not module_file.exists():
                        module_file = plugin_dir / f"{module_path.split('.')[0]}.py"

                if not module_file.exists():
                    raise PluginLoadError(f"Module file not found: {module_file}")

                spec = importlib.util.spec_from_file_location(unique_module_name, module_file)
                if spec is None or spec.loader is None:
                    raise PluginLoadError(f"Failed to load module spec: {unique_module_name}")

                module = importlib.util.module_from_spec(spec)
                sys.modules[unique_module_name] = module
                spec.loader.exec_module(module)
                self.loaded_modules[unique_module_name] = module
            else:
                module = self.loaded_modules[unique_module_name]

            plugin_class = getattr(module, class_name)

            if not issubclass(plugin_class, PluginInterface):
                raise PluginLoadError(
                    f"{class_name} must inherit from PluginInterface"
                )

            return plugin_class

        except PluginLoadError:
            raise
        except Exception as e:
            raise PluginLoadError(f"Failed to load plugin class {entry_point}: {e}")


class PluginManager:
    """Manages plugin lifecycle and dependencies"""

    def __init__(
        self,
        search_paths: List[Path],
        system_version: str = "1.0.0"
    ):
        """
        Initialize plugin manager.

        Args:
            search_paths: Directories to search for plugins
            system_version: Current system version
        """
        self.search_paths = search_paths
        self.version_checker = VersionChecker(system_version)
        self.discovery = PluginDiscovery(search_paths)
        self.loader = PluginLoader(self.version_checker)
        self.dependency_resolver = DependencyResolver()

        self.discovered_plugins: List[Dict[str, Any]] = []
        self.loaded_plugins: Dict[str, PluginInterface] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}

    def discover_plugins(self) -> List[Dict[str, Any]]:
        """
        Discover all available plugins.

        Returns:
            List of discovered plugin info
        """
        self.discovered_plugins = self.discovery.discover()
        return self.discovered_plugins

    def load_all_plugins(self, configs: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        """
        Load all discovered plugins in dependency order.

        Args:
            configs: Optional plugin configurations keyed by plugin name

        Raises:
            PluginLoadError: If loading fails
            DependencyError: If dependency resolution fails
        """
        if configs:
            self.plugin_configs = configs

        if not self.discovered_plugins:
            self.discover_plugins()

        for plugin_info in self.discovered_plugins:
            manifest = plugin_info["manifest"]
            self.dependency_resolver.add_plugin(
                manifest["name"],
                manifest.get("dependencies", [])
            )

        try:
            load_order = self.dependency_resolver.resolve()
        except DependencyError as e:
            raise PluginLoadError(f"Dependency resolution failed: {e}")

        for plugin_name in load_order:
            plugin_info = next(
                (p for p in self.discovered_plugins if p["manifest"]["name"] == plugin_name),
                None
            )

            if not plugin_info:
                continue

            config = self.plugin_configs.get(plugin_name, {})
            plugin = self.loader.load_plugin(plugin_info, config)
            self.loaded_plugins[plugin_name] = plugin

    def load_plugin(self, plugin_name: str, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Load a specific plugin.

        Args:
            plugin_name: Name of the plugin to load
            config: Optional plugin configuration

        Raises:
            PluginLoadError: If loading fails
        """
        if plugin_name in self.loaded_plugins:
            return

        if not self.discovered_plugins:
            self.discover_plugins()

        plugin_info = next(
            (p for p in self.discovered_plugins if p["manifest"]["name"] == plugin_name),
            None
        )

        if not plugin_info:
            raise PluginLoadError(f"Plugin not found: {plugin_name}")

        deps = plugin_info["manifest"].get("dependencies", [])
        for dep in deps:
            if dep not in self.loaded_plugins:
                self.load_plugin(dep)

        plugin_config = config or self.plugin_configs.get(plugin_name, {})
        plugin = self.loader.load_plugin(plugin_info, plugin_config)
        self.loaded_plugins[plugin_name] = plugin

    def unload_plugin(self, plugin_name: str) -> None:
        """
        Unload a plugin.

        Args:
            plugin_name: Name of the plugin to unload

        Raises:
            PluginLoadError: If plugin cannot be unloaded
        """
        if plugin_name not in self.loaded_plugins:
            return

        if not self.dependency_resolver.can_unload(plugin_name):
            dependents = self.dependency_resolver.get_dependents(plugin_name)
            raise PluginLoadError(
                f"Cannot unload {plugin_name}: required by {', '.join(dependents)}"
            )

        plugin = self.loaded_plugins[plugin_name]
        plugin.cleanup()
        plugin.status = PluginStatus.UNLOADED
        del self.loaded_plugins[plugin_name]

    def get_plugin(self, plugin_name: str) -> Optional[PluginInterface]:
        """
        Get a loaded plugin by name.

        Args:
            plugin_name: Name of the plugin

        Returns:
            Plugin instance or None if not loaded
        """
        return self.loaded_plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type: str) -> List[PluginInterface]:
        """
        Get all loaded plugins of a specific type.

        Args:
            plugin_type: Plugin type to filter by

        Returns:
            List of plugins matching the type
        """
        return [
            p for p in self.loaded_plugins.values()
            if p.plugin_type.value == plugin_type
        ]

    def reload_plugin(self, plugin_name: str) -> None:
        """
        Reload a plugin.

        Args:
            plugin_name: Name of the plugin to reload
        """
        config = self.plugin_configs.get(plugin_name)
        self.unload_plugin(plugin_name)
        self.load_plugin(plugin_name, config)
