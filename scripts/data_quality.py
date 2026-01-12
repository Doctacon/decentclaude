#!/usr/bin/env python3
"""
Example Data Quality Check Script

This script demonstrates how to implement custom data quality checks
that can be triggered by the data-quality-check Claude Code hook.

Customize this script for your project's specific data quality requirements.
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple


class DataQualityCheck:
    """Base class for data quality checks"""

    def __init__(self, name: str):
        self.name = name
        self.passed = False
        self.message = ""

    def run(self) -> bool:
        """Run the check. Override in subclasses."""
        raise NotImplementedError

    def report(self) -> str:
        """Return a formatted report of the check result"""
        status = "✓ PASS" if self.passed else "✗ FAIL"
        return f"{status}: {self.name}\n  {self.message}"


class SQLFileExistsCheck(DataQualityCheck):
    """Check that SQL files exist in expected locations"""

    def __init__(self, required_dirs: List[str]):
        super().__init__("SQL Files Exist")
        self.required_dirs = required_dirs

    def run(self) -> bool:
        missing_dirs = []
        for dir_path in self.required_dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)

        if missing_dirs:
            self.message = f"Missing directories: {', '.join(missing_dirs)}"
            self.passed = False
        else:
            self.message = f"All required directories exist: {', '.join(self.required_dirs)}"
            self.passed = True

        return self.passed


class SQLSyntaxCheck(DataQualityCheck):
    """Validate SQL syntax in all SQL files"""

    def __init__(self, sql_dirs: List[str]):
        super().__init__("SQL Syntax Validation")
        self.sql_dirs = sql_dirs

    def run(self) -> bool:
        try:
            import sqlparse
        except ImportError:
            self.message = "sqlparse not installed. Install with: pip install sqlparse"
            self.passed = False
            return False

        sql_files = []
        for sql_dir in self.sql_dirs:
            if Path(sql_dir).exists():
                sql_files.extend(Path(sql_dir).rglob("*.sql"))

        if not sql_files:
            self.message = "No SQL files found to validate"
            self.passed = True
            return True

        invalid_files = []
        for sql_file in sql_files:
            try:
                with open(sql_file, 'r') as f:
                    content = f.read()
                parsed = sqlparse.parse(content)
                if not parsed:
                    invalid_files.append(str(sql_file))
            except Exception as e:
                invalid_files.append(f"{sql_file} ({str(e)})")

        if invalid_files:
            self.message = f"Invalid SQL files: {', '.join(invalid_files)}"
            self.passed = False
        else:
            self.message = f"All {len(sql_files)} SQL files have valid syntax"
            self.passed = True

        return self.passed


class ConfigFileCheck(DataQualityCheck):
    """Check that required configuration files exist"""

    def __init__(self, required_files: List[str]):
        super().__init__("Configuration Files")
        self.required_files = required_files

    def run(self) -> bool:
        missing_files = []
        for file_path in self.required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            self.message = f"Missing config files: {', '.join(missing_files)}"
            self.passed = False
        else:
            self.message = f"All required config files present: {', '.join(self.required_files)}"
            self.passed = True

        return self.passed


class NoHardcodedSecretsCheck(DataQualityCheck):
    """Check that SQL files don't contain hardcoded secrets"""

    def __init__(self, sql_dirs: List[str]):
        super().__init__("No Hardcoded Secrets")
        self.sql_dirs = sql_dirs
        self.secret_patterns = [
            "password",
            "api_key",
            "secret",
            "token",
            "credentials"
        ]

    def run(self) -> bool:
        sql_files = []
        for sql_dir in self.sql_dirs:
            if Path(sql_dir).exists():
                sql_files.extend(Path(sql_dir).rglob("*.sql"))

        if not sql_files:
            self.message = "No SQL files found to check"
            self.passed = True
            return True

        suspicious_files = []
        for sql_file in sql_files:
            try:
                with open(sql_file, 'r') as f:
                    content = f.read().lower()
                for pattern in self.secret_patterns:
                    if pattern in content and "'" in content:
                        suspicious_files.append(f"{sql_file} (contains '{pattern}')")
                        break
            except Exception:
                pass

        if suspicious_files:
            self.message = f"Potential secrets found in: {', '.join(suspicious_files)}"
            self.passed = False
        else:
            self.message = f"No hardcoded secrets detected in {len(sql_files)} files"
            self.passed = True

        return self.passed


def run_all_checks() -> Tuple[List[DataQualityCheck], bool]:
    """Run all configured data quality checks"""

    # Configure checks for your project
    checks = [
        # Check for SQL directories (customize as needed)
        SQLFileExistsCheck(["models", "queries", "sql"]),

        # Validate SQL syntax
        SQLSyntaxCheck(["models", "queries", "sql"]),

        # Check for configuration files (customize as needed)
        ConfigFileCheck([".claude/settings.json"]),

        # Check for hardcoded secrets
        NoHardcodedSecretsCheck(["models", "queries", "sql"]),
    ]

    all_passed = True
    results = []

    print("=" * 60)
    print("Running Data Quality Checks")
    print("=" * 60)

    for check in checks:
        try:
            check.run()
            results.append(check)
            if not check.passed:
                all_passed = False
        except Exception as e:
            check.message = f"Error running check: {str(e)}"
            check.passed = False
            results.append(check)
            all_passed = False

    return results, all_passed


def main():
    """Main entry point"""
    results, all_passed = run_all_checks()

    print()
    for result in results:
        print(result.report())

    print()
    print("=" * 60)
    if all_passed:
        print("✓ All data quality checks passed")
        print("=" * 60)
        sys.exit(0)
    else:
        print("✗ Some data quality checks failed")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
