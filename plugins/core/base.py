"""
Base classes and interfaces for the plugin system.

This module defines the core plugin API that all plugins must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum


class PluginType(Enum):
    """Types of plugins supported by the system"""
    HOOK = "hook"                    # Custom Claude Code hooks
    VALIDATOR = "validator"          # Data validation plugins
    QUALITY_CHECK = "quality_check"  # Data quality check plugins
    CLI_UTILITY = "cli_utility"      # CLI utility plugins
    INTEGRATION = "integration"      # Third-party tool integrations
    CUSTOM = "custom"               # Custom plugin types


class PluginStatus(Enum):
    """Plugin lifecycle status"""
    UNLOADED = "unloaded"
    LOADING = "loading"
    LOADED = "loaded"
    ACTIVE = "active"
    FAILED = "failed"
    DISABLED = "disabled"


class PluginInterface(ABC):
    """
    Base interface that all plugins must implement.

    Plugins extend the functionality of DecentClaude by providing
    custom hooks, validators, quality checks, or integrations.
    """

    def __init__(self, manifest: Dict[str, Any]):
        """
        Initialize the plugin with its manifest.

        Args:
            manifest: Plugin manifest containing metadata and configuration
        """
        self.manifest = manifest
        self.status = PluginStatus.UNLOADED
        self.config: Dict[str, Any] = {}

    @property
    def name(self) -> str:
        """Get the plugin name"""
        return self.manifest.get("name", "unknown")

    @property
    def version(self) -> str:
        """Get the plugin version"""
        return self.manifest.get("version", "0.0.0")

    @property
    def plugin_type(self) -> PluginType:
        """Get the plugin type"""
        type_str = self.manifest.get("type", "custom")
        try:
            return PluginType(type_str)
        except ValueError:
            return PluginType.CUSTOM

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize the plugin with configuration.

        Args:
            config: Plugin-specific configuration

        Returns:
            True if initialization was successful, False otherwise
        """
        pass

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate that the plugin is properly configured and ready to use.

        Returns:
            True if validation passes, False otherwise
        """
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute the plugin's main functionality.

        Args:
            context: Execution context and parameters

        Returns:
            Plugin-specific result
        """
        pass

    def cleanup(self) -> None:
        """Clean up resources when plugin is unloaded"""
        pass

    def get_dependencies(self) -> List[str]:
        """
        Get list of plugin dependencies.

        Returns:
            List of plugin names this plugin depends on
        """
        return self.manifest.get("dependencies", [])

    def get_required_version(self) -> str:
        """
        Get the required DecentClaude version.

        Returns:
            Minimum DecentClaude version required (semver format)
        """
        return self.manifest.get("requires_version", "0.0.0")


class HookPlugin(PluginInterface):
    """
    Base class for hook plugins that extend Claude Code hooks.
    """

    @abstractmethod
    def get_hook_config(self) -> Dict[str, Any]:
        """
        Get the hook configuration for integration with Claude Code.

        Returns:
            Hook configuration dict compatible with .claude/settings.json
        """
        pass


class ValidatorPlugin(PluginInterface):
    """
    Base class for validator plugins that validate data or code.
    """

    @abstractmethod
    def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data.

        Args:
            input_data: Data to validate

        Returns:
            True if validation passes, False otherwise
        """
        pass

    @abstractmethod
    def get_validation_errors(self) -> List[str]:
        """
        Get validation errors from the last validation.

        Returns:
            List of validation error messages
        """
        pass


class QualityCheckPlugin(PluginInterface):
    """
    Base class for data quality check plugins.
    """

    def __init__(self, manifest: Dict[str, Any]):
        super().__init__(manifest)
        self.passed = False
        self.message = ""

    @abstractmethod
    def run_check(self) -> bool:
        """
        Run the quality check.

        Returns:
            True if check passes, False otherwise
        """
        pass

    def execute(self, context: Dict[str, Any]) -> bool:
        """Execute quality check"""
        return self.run_check()

    def get_report(self) -> str:
        """
        Get a formatted report of the check result.

        Returns:
            Formatted report string
        """
        status = "✓ PASS" if self.passed else "✗ FAIL"
        return f"{status}: {self.name}\n  {self.message}"


class IntegrationPlugin(PluginInterface):
    """
    Base class for third-party tool integration plugins.
    """

    @abstractmethod
    def connect(self) -> bool:
        """
        Establish connection to the external tool.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the external tool"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the external tool is available.

        Returns:
            True if tool is available, False otherwise
        """
        pass
