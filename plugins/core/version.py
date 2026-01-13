"""
Version compatibility checking for plugins.

Implements semantic versioning (semver) comparison and compatibility checks.
"""

import re
from typing import Tuple, Optional


class SemanticVersion:
    """Represents a semantic version (major.minor.patch)"""

    def __init__(self, version_string: str):
        """
        Parse a semantic version string.

        Args:
            version_string: Version in format "major.minor.patch" or "major.minor.patch-prerelease"
        """
        self.original = version_string
        self.major = 0
        self.minor = 0
        self.patch = 0
        self.prerelease = ""
        self.metadata = ""

        self._parse(version_string)

    def _parse(self, version_string: str) -> None:
        """Parse version string into components"""
        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-z0-9.-]+))?(?:\+([a-z0-9.-]+))?$"
        match = re.match(pattern, version_string, re.IGNORECASE)

        if not match:
            raise ValueError(f"Invalid semantic version: {version_string}")

        self.major = int(match.group(1))
        self.minor = int(match.group(2))
        self.patch = int(match.group(3))
        self.prerelease = match.group(4) or ""
        self.metadata = match.group(5) or ""

    def __str__(self) -> str:
        """String representation"""
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.metadata:
            version += f"+{self.metadata}"
        return version

    def __repr__(self) -> str:
        return f"SemanticVersion('{self}')"

    def __eq__(self, other: object) -> bool:
        """Check equality (ignoring metadata)"""
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
        )

    def __lt__(self, other: "SemanticVersion") -> bool:
        """Check if this version is less than another"""
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch

        if not self.prerelease and other.prerelease:
            return False
        if self.prerelease and not other.prerelease:
            return True
        if self.prerelease and other.prerelease:
            return self.prerelease < other.prerelease

        return False

    def __le__(self, other: "SemanticVersion") -> bool:
        """Check if this version is less than or equal to another"""
        return self < other or self == other

    def __gt__(self, other: "SemanticVersion") -> bool:
        """Check if this version is greater than another"""
        return not self <= other

    def __ge__(self, other: "SemanticVersion") -> bool:
        """Check if this version is greater than or equal to another"""
        return not self < other

    def is_compatible_with(self, required_version: "SemanticVersion") -> bool:
        """
        Check if this version is compatible with a required version.

        Compatibility rules:
        - Major version must match
        - This version must be >= required version

        Args:
            required_version: Required version to check against

        Returns:
            True if compatible, False otherwise
        """
        if self.major != required_version.major:
            return False

        return self >= required_version


class VersionChecker:
    """Checks version compatibility between plugins and the system"""

    def __init__(self, system_version: str = "1.0.0"):
        """
        Initialize version checker.

        Args:
            system_version: Current DecentClaude system version
        """
        self.system_version = SemanticVersion(system_version)

    def check_plugin_compatibility(
        self,
        plugin_name: str,
        required_version: str
    ) -> Tuple[bool, str]:
        """
        Check if a plugin is compatible with the current system version.

        Args:
            plugin_name: Name of the plugin
            required_version: Minimum required system version

        Returns:
            Tuple of (is_compatible, message)
        """
        try:
            required = SemanticVersion(required_version)
        except ValueError as e:
            return False, f"Invalid version format for {plugin_name}: {e}"

        if self.system_version.is_compatible_with(required):
            return True, f"Plugin {plugin_name} is compatible (requires {required}, have {self.system_version})"
        else:
            return False, (
                f"Plugin {plugin_name} requires version {required} or higher "
                f"(current version: {self.system_version})"
            )

    def check_dependency_compatibility(
        self,
        plugin_version: str,
        dependency_version: str
    ) -> bool:
        """
        Check if two plugin versions are compatible.

        Args:
            plugin_version: Version of the plugin
            dependency_version: Version of the dependency

        Returns:
            True if compatible, False otherwise
        """
        try:
            plugin_ver = SemanticVersion(plugin_version)
            dep_ver = SemanticVersion(dependency_version)
            return plugin_ver.is_compatible_with(dep_ver)
        except ValueError:
            return False

    def get_latest_compatible(
        self,
        available_versions: list[str],
        min_version: Optional[str] = None
    ) -> Optional[str]:
        """
        Get the latest compatible version from a list.

        Args:
            available_versions: List of available version strings
            min_version: Minimum required version (optional)

        Returns:
            Latest compatible version or None
        """
        try:
            semver_list = [SemanticVersion(v) for v in available_versions]
            semver_list.sort(reverse=True)

            if min_version:
                min_ver = SemanticVersion(min_version)
                semver_list = [v for v in semver_list if v >= min_ver]

            return str(semver_list[0]) if semver_list else None
        except (ValueError, IndexError):
            return None


def parse_version_constraint(constraint: str) -> Tuple[str, str]:
    """
    Parse a version constraint like ">=1.0.0" or "~1.2.0".

    Args:
        constraint: Version constraint string

    Returns:
        Tuple of (operator, version)
    """
    operators = [">=", "<=", ">", "<", "==", "~", "^"]
    for op in operators:
        if constraint.startswith(op):
            version = constraint[len(op):].strip()
            return op, version

    return "==", constraint
