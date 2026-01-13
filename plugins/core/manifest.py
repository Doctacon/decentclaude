"""
Plugin manifest schema and validation.

Plugin manifests are JSON or YAML files that describe a plugin's metadata,
dependencies, and configuration requirements.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import re


class ManifestSchema:
    """Schema definition for plugin manifests"""

    REQUIRED_FIELDS = ["name", "version", "type", "entry_point"]
    OPTIONAL_FIELDS = [
        "description",
        "author",
        "license",
        "homepage",
        "dependencies",
        "requires_version",
        "config_schema",
        "tags"
    ]

    VALID_TYPES = ["hook", "validator", "quality_check", "cli_utility", "integration", "custom"]


class ManifestValidator:
    """Validates plugin manifests against the schema"""

    def __init__(self):
        self.errors: List[str] = []

    def validate(self, manifest: Dict[str, Any]) -> bool:
        """
        Validate a plugin manifest.

        Args:
            manifest: Plugin manifest dict

        Returns:
            True if valid, False otherwise
        """
        self.errors = []

        self._validate_required_fields(manifest)
        self._validate_name(manifest.get("name"))
        self._validate_version(manifest.get("version"))
        self._validate_type(manifest.get("type"))
        self._validate_entry_point(manifest.get("entry_point"))
        self._validate_dependencies(manifest.get("dependencies", []))
        self._validate_requires_version(manifest.get("requires_version", "0.0.0"))

        return len(self.errors) == 0

    def _validate_required_fields(self, manifest: Dict[str, Any]) -> None:
        """Validate that all required fields are present"""
        for field in ManifestSchema.REQUIRED_FIELDS:
            if field not in manifest:
                self.errors.append(f"Missing required field: {field}")

    def _validate_name(self, name: Optional[str]) -> None:
        """Validate plugin name"""
        if not name:
            return

        if not re.match(r"^[a-z0-9_-]+$", name):
            self.errors.append(
                f"Invalid plugin name '{name}'. Must contain only lowercase letters, "
                "numbers, hyphens, and underscores"
            )

    def _validate_version(self, version: Optional[str]) -> None:
        """Validate semantic version"""
        if not version:
            return

        semver_pattern = r"^\d+\.\d+\.\d+(-[a-z0-9.-]+)?(\+[a-z0-9.-]+)?$"
        if not re.match(semver_pattern, version, re.IGNORECASE):
            self.errors.append(
                f"Invalid version '{version}'. Must follow semantic versioning (e.g., 1.0.0)"
            )

    def _validate_type(self, plugin_type: Optional[str]) -> None:
        """Validate plugin type"""
        if not plugin_type:
            return

        if plugin_type not in ManifestSchema.VALID_TYPES:
            self.errors.append(
                f"Invalid plugin type '{plugin_type}'. "
                f"Must be one of: {', '.join(ManifestSchema.VALID_TYPES)}"
            )

    def _validate_entry_point(self, entry_point: Optional[str]) -> None:
        """Validate entry point"""
        if not entry_point:
            return

        if not re.match(r"^[a-zA-Z0-9_.:]+$", entry_point):
            self.errors.append(
                f"Invalid entry_point '{entry_point}'. "
                "Must be a valid Python module path (e.g., 'module.ClassName')"
            )

    def _validate_dependencies(self, dependencies: List[str]) -> None:
        """Validate dependencies list"""
        if not isinstance(dependencies, list):
            self.errors.append("Dependencies must be a list")
            return

        for dep in dependencies:
            if not isinstance(dep, str):
                self.errors.append(f"Invalid dependency: {dep}. Must be a string")

    def _validate_requires_version(self, version: Optional[str]) -> None:
        """Validate required DecentClaude version"""
        if not version:
            return

        semver_pattern = r"^\d+\.\d+\.\d+$"
        if not re.match(semver_pattern, version):
            self.errors.append(
                f"Invalid requires_version '{version}'. Must be semantic version (e.g., 1.0.0)"
            )

    def get_errors(self) -> List[str]:
        """Get validation errors"""
        return self.errors


class ManifestLoader:
    """Loads and parses plugin manifests"""

    @staticmethod
    def load_from_file(manifest_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load manifest from a file.

        Args:
            manifest_path: Path to manifest file (JSON or YAML)

        Returns:
            Parsed manifest dict or None if loading fails
        """
        if not manifest_path.exists():
            return None

        try:
            with open(manifest_path, 'r') as f:
                if manifest_path.suffix == '.json':
                    return json.load(f)
                elif manifest_path.suffix in ['.yml', '.yaml']:
                    try:
                        import yaml
                        return yaml.safe_load(f)
                    except ImportError:
                        print("YAML support requires PyYAML: pip install pyyaml")
                        return None
                else:
                    return None
        except Exception as e:
            print(f"Error loading manifest from {manifest_path}: {e}")
            return None

    @staticmethod
    def load_from_dict(manifest_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load manifest from a dictionary.

        Args:
            manifest_dict: Manifest as a dictionary

        Returns:
            Manifest dict
        """
        return manifest_dict


def create_manifest_template(
    name: str,
    version: str,
    plugin_type: str,
    entry_point: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a manifest template with common fields.

    Args:
        name: Plugin name
        version: Plugin version
        plugin_type: Plugin type
        entry_point: Python entry point (e.g., 'module.ClassName')
        **kwargs: Additional optional fields

    Returns:
        Manifest dict
    """
    manifest = {
        "name": name,
        "version": version,
        "type": plugin_type,
        "entry_point": entry_point,
        "description": kwargs.get("description", ""),
        "author": kwargs.get("author", ""),
        "license": kwargs.get("license", "MIT"),
        "dependencies": kwargs.get("dependencies", []),
        "requires_version": kwargs.get("requires_version", "0.1.0"),
        "tags": kwargs.get("tags", [])
    }

    return manifest
