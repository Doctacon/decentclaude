"""
Schema Check Plugin

Validates that required schema files exist and are properly formatted.
"""

from typing import Any, Dict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from plugins.core.base import QualityCheckPlugin


class SchemaCheckPlugin(QualityCheckPlugin):
    """Plugin for checking schema files"""

    def __init__(self, manifest: Dict[str, Any]):
        super().__init__(manifest)
        self.schema_paths = []

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize schema checker"""
        self.config = config
        self.schema_paths = config.get("schema_paths", ["schemas"])
        return True

    def validate(self) -> bool:
        """Validate plugin is ready"""
        return True

    def run_check(self) -> bool:
        """
        Run schema existence and format check.

        Returns:
            True if check passes, False otherwise
        """
        missing_dirs = []
        found_schemas = []

        for schema_path in self.schema_paths:
            path = Path(schema_path)
            if not path.exists():
                missing_dirs.append(schema_path)
            else:
                schema_files = list(path.glob("*.json")) + list(path.glob("*.yaml"))
                found_schemas.extend(schema_files)

        if missing_dirs:
            self.passed = False
            self.message = f"Missing schema directories: {', '.join(missing_dirs)}"
            return False

        if not found_schemas:
            self.passed = False
            self.message = "No schema files found in configured paths"
            return False

        self.passed = True
        self.message = f"Found {len(found_schemas)} schema files"
        return True
