"""
SQL Validator Plugin

Validates SQL syntax using sqlparse.
"""

from typing import Any, Dict, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from plugins.core.base import ValidatorPlugin


class SQLValidatorPlugin(ValidatorPlugin):
    """Plugin for validating SQL syntax"""

    def __init__(self, manifest: Dict[str, Any]):
        super().__init__(manifest)
        self.validation_errors: List[str] = []
        self.sqlparse = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the SQL validator"""
        self.config = config

        try:
            import sqlparse
            self.sqlparse = sqlparse
            return True
        except ImportError:
            self.validation_errors.append(
                "sqlparse not installed. Install with: pip install sqlparse"
            )
            return False

    def validate(self) -> bool:
        """Validate plugin is ready"""
        return self.sqlparse is not None

    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute SQL validation"""
        sql = context.get("sql", "")
        return self.validate_input(sql)

    def validate_input(self, input_data: Any) -> bool:
        """
        Validate SQL syntax.

        Args:
            input_data: SQL string to validate

        Returns:
            True if SQL is valid, False otherwise
        """
        self.validation_errors = []

        if not isinstance(input_data, str):
            self.validation_errors.append("Input must be a string")
            return False

        if not input_data.strip():
            self.validation_errors.append("SQL string is empty")
            return False

        try:
            parsed = self.sqlparse.parse(input_data)
            if not parsed:
                self.validation_errors.append("Failed to parse SQL")
                return False

            return True

        except Exception as e:
            self.validation_errors.append(f"SQL parsing error: {str(e)}")
            return False

    def get_validation_errors(self) -> List[str]:
        """Get validation errors"""
        return self.validation_errors
