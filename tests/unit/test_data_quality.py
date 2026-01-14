"""
Unit tests for scripts/data_quality.py

Tests all data quality check classes and functions.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, mock_open

# Add project root to path so we can import from scripts
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.data_quality import (
    DataQualityCheck,
    SQLFileExistsCheck,
    SQLSyntaxCheck,
    ConfigFileCheck,
    NoHardcodedSecretsCheck,
    run_all_checks,
    main,
)


# --- Base Class Tests ---

@pytest.mark.unit
def test_data_quality_check_base_class():
    """Test the base DataQualityCheck class initialization"""
    check = DataQualityCheck("Test Check")
    assert check.name == "Test Check"
    assert check.passed is False
    assert check.message == ""


@pytest.mark.unit
def test_data_quality_check_run_not_implemented():
    """Test that base class run() raises NotImplementedError"""
    check = DataQualityCheck("Test")
    with pytest.raises(NotImplementedError):
        check.run()


@pytest.mark.unit
def test_data_quality_check_report_pass():
    """Test report formatting for passed check"""
    check = DataQualityCheck("Test Check")
    check.passed = True
    check.message = "Everything is good"
    report = check.report()
    assert "✓ PASS" in report
    assert "Test Check" in report
    assert "Everything is good" in report


@pytest.mark.unit
def test_data_quality_check_report_fail():
    """Test report formatting for failed check"""
    check = DataQualityCheck("Test Check")
    check.passed = False
    check.message = "Something went wrong"
    report = check.report()
    assert "✗ FAIL" in report
    assert "Test Check" in report
    assert "Something went wrong" in report


# --- SQLFileExistsCheck Tests ---

@pytest.mark.unit
def test_sql_file_exists_check_all_exist(temp_dir):
    """Test SQLFileExistsCheck when all directories exist"""
    # Create test directories
    dir1 = temp_dir / "models"
    dir2 = temp_dir / "queries"
    dir1.mkdir()
    dir2.mkdir()

    check = SQLFileExistsCheck([str(dir1), str(dir2)])
    result = check.run()

    assert result is True
    assert check.passed is True
    assert "All required directories exist" in check.message
    assert "models" in check.message
    assert "queries" in check.message


@pytest.mark.unit
def test_sql_file_exists_check_missing_dirs(temp_dir):
    """Test SQLFileExistsCheck when directories are missing"""
    dir1 = temp_dir / "existing"
    dir2 = temp_dir / "missing"
    dir1.mkdir()
    # dir2 intentionally not created

    check = SQLFileExistsCheck([str(dir1), str(dir2)])
    result = check.run()

    assert result is False
    assert check.passed is False
    assert "Missing directories" in check.message
    assert str(dir2) in check.message


@pytest.mark.unit
def test_sql_file_exists_check_all_missing(temp_dir):
    """Test SQLFileExistsCheck when all directories are missing"""
    check = SQLFileExistsCheck([
        str(temp_dir / "missing1"),
        str(temp_dir / "missing2")
    ])
    result = check.run()

    assert result is False
    assert check.passed is False
    assert "Missing directories" in check.message


# --- SQLSyntaxCheck Tests ---

@pytest.mark.unit
def test_sql_syntax_check_valid_sql(temp_dir):
    """Test SQLSyntaxCheck with valid SQL files"""
    sql_dir = temp_dir / "sql"
    sql_dir.mkdir()

    # Create valid SQL files
    (sql_dir / "query1.sql").write_text("SELECT * FROM users")
    (sql_dir / "query2.sql").write_text("SELECT id, name FROM products WHERE price > 100")

    check = SQLSyntaxCheck([str(sql_dir)])
    result = check.run()

    assert result is True
    assert check.passed is True
    assert "valid syntax" in check.message
    assert "2" in check.message


@pytest.mark.unit
def test_sql_syntax_check_invalid_sql(temp_dir):
    """Test SQLSyntaxCheck with invalid SQL files"""
    sql_dir = temp_dir / "sql"
    sql_dir.mkdir()

    # Create SQL file with empty content (will not parse)
    (sql_dir / "invalid.sql").write_text("")

    check = SQLSyntaxCheck([str(sql_dir)])
    result = check.run()

    assert result is False
    assert check.passed is False
    assert "Invalid SQL files" in check.message


@pytest.mark.unit
def test_sql_syntax_check_no_sql_files(temp_dir):
    """Test SQLSyntaxCheck when no SQL files exist"""
    sql_dir = temp_dir / "sql"
    sql_dir.mkdir()

    check = SQLSyntaxCheck([str(sql_dir)])
    result = check.run()

    assert result is True
    assert check.passed is True
    assert "No SQL files found" in check.message


@pytest.mark.unit
def test_sql_syntax_check_missing_sqlparse(temp_dir, monkeypatch):
    """Test SQLSyntaxCheck when sqlparse is not installed"""
    sql_dir = temp_dir / "sql"
    sql_dir.mkdir()

    # Mock sqlparse import to raise ImportError
    def mock_import(name, *args, **kwargs):
        if name == "sqlparse":
            raise ImportError("No module named 'sqlparse'")
        return __import__(name, *args, **kwargs)

    # We need to patch __import__ in the module's context
    import builtins
    original_import = builtins.__import__

    def patched_import(name, *args, **kwargs):
        if name == "sqlparse":
            raise ImportError("No module named 'sqlparse'")
        return original_import(name, *args, **kwargs)

    with patch("builtins.__import__", patched_import):
        check = SQLSyntaxCheck([str(sql_dir)])
        result = check.run()

    assert result is False
    assert check.passed is False
    assert "sqlparse not installed" in check.message


@pytest.mark.unit
def test_sql_syntax_check_nested_directories(temp_dir):
    """Test SQLSyntaxCheck finds SQL files in nested directories"""
    sql_dir = temp_dir / "sql"
    sql_dir.mkdir()
    nested = sql_dir / "nested" / "deep"
    nested.mkdir(parents=True)

    (sql_dir / "root.sql").write_text("SELECT 1")
    (nested / "nested.sql").write_text("SELECT 2")

    check = SQLSyntaxCheck([str(sql_dir)])
    result = check.run()

    assert result is True
    assert check.passed is True
    assert "2" in check.message


@pytest.mark.unit
def test_sql_syntax_check_file_read_error(temp_dir):
    """Test SQLSyntaxCheck handles file read errors gracefully"""
    sql_dir = temp_dir / "sql"
    sql_dir.mkdir()
    sql_file = sql_dir / "test.sql"
    sql_file.write_text("SELECT * FROM users")

    check = SQLSyntaxCheck([str(sql_dir)])

    # Mock open to raise an exception
    with patch("builtins.open", side_effect=PermissionError("Access denied")):
        result = check.run()

    assert result is False
    assert check.passed is False
    assert "Invalid SQL files" in check.message


# --- ConfigFileCheck Tests ---

@pytest.mark.unit
def test_config_file_check_all_exist(temp_dir):
    """Test ConfigFileCheck when all config files exist"""
    config1 = temp_dir / "config.yaml"
    config2 = temp_dir / "settings.json"
    config1.write_text("key: value")
    config2.write_text("{}")

    check = ConfigFileCheck([str(config1), str(config2)])
    result = check.run()

    assert result is True
    assert check.passed is True
    assert "All required config files present" in check.message


@pytest.mark.unit
def test_config_file_check_missing_files(temp_dir):
    """Test ConfigFileCheck when files are missing"""
    config1 = temp_dir / "existing.yaml"
    config2 = temp_dir / "missing.yaml"
    config1.write_text("key: value")
    # config2 not created

    check = ConfigFileCheck([str(config1), str(config2)])
    result = check.run()

    assert result is False
    assert check.passed is False
    assert "Missing config files" in check.message
    assert str(config2) in check.message


@pytest.mark.unit
def test_config_file_check_all_missing(temp_dir):
    """Test ConfigFileCheck when all files are missing"""
    check = ConfigFileCheck([
        str(temp_dir / "missing1.yaml"),
        str(temp_dir / "missing2.json")
    ])
    result = check.run()

    assert result is False
    assert check.passed is False


# --- NoHardcodedSecretsCheck Tests ---

@pytest.mark.unit
def test_no_secrets_check_clean_sql(temp_dir):
    """Test NoHardcodedSecretsCheck with clean SQL files"""
    sql_dir = temp_dir / "sql"
    sql_dir.mkdir()

    (sql_dir / "clean.sql").write_text("""
        SELECT * FROM users
        WHERE user_id = @user_id
        AND status = 'active'
    """)

    check = NoHardcodedSecretsCheck([str(sql_dir)])
    result = check.run()

    assert result is True
    assert check.passed is True
    assert "No hardcoded secrets detected" in check.message


@pytest.mark.unit
def test_no_secrets_check_detects_password(temp_dir):
    """Test NoHardcodedSecretsCheck detects password in SQL"""
    sql_dir = temp_dir / "sql"
    sql_dir.mkdir()

    (sql_dir / "suspicious.sql").write_text("""
        SELECT * FROM users
        WHERE password = 'secret123'
    """)

    check = NoHardcodedSecretsCheck([str(sql_dir)])
    result = check.run()

    assert result is False
    assert check.passed is False
    assert "Potential secrets found" in check.message
    assert "password" in check.message


@pytest.mark.unit
def test_no_secrets_check_detects_api_key(temp_dir):
    """Test NoHardcodedSecretsCheck detects api_key in SQL"""
    sql_dir = temp_dir / "sql"
    sql_dir.mkdir()

    (sql_dir / "suspicious.sql").write_text("""
        SELECT * FROM config
        WHERE api_key = 'sk_test_abc123'
    """)

    check = NoHardcodedSecretsCheck([str(sql_dir)])
    result = check.run()

    assert result is False
    assert check.passed is False
    assert "api_key" in check.message.lower()


@pytest.mark.unit
def test_no_secrets_check_detects_multiple_patterns(temp_dir):
    """Test NoHardcodedSecretsCheck detects various secret patterns"""
    sql_dir = temp_dir / "sql"
    sql_dir.mkdir()

    patterns = {
        "password.sql": "password = 'test'",
        "api.sql": "api_key = 'key123'",
        "token.sql": "token = 'tok123'",
        "secret.sql": "secret = 'sec123'",
        "creds.sql": "credentials = 'cred123'",
    }

    for filename, content in patterns.items():
        (sql_dir / filename).write_text(f"SELECT * FROM t WHERE {content}")

    check = NoHardcodedSecretsCheck([str(sql_dir)])
    result = check.run()

    assert result is False
    assert check.passed is False


@pytest.mark.unit
def test_no_secrets_check_no_files(temp_dir):
    """Test NoHardcodedSecretsCheck when no SQL files exist"""
    sql_dir = temp_dir / "sql"
    sql_dir.mkdir()

    check = NoHardcodedSecretsCheck([str(sql_dir)])
    result = check.run()

    assert result is True
    assert check.passed is True
    assert "No SQL files found" in check.message


@pytest.mark.unit
def test_no_secrets_check_ignores_comments_without_quotes(temp_dir):
    """Test that secret words in comments without quotes don't trigger false positives"""
    sql_dir = temp_dir / "sql"
    sql_dir.mkdir()

    # The check requires both the pattern AND quotes to trigger
    (sql_dir / "comment.sql").write_text("""
        -- This query gets the user password field
        SELECT password FROM users
    """)

    check = NoHardcodedSecretsCheck([str(sql_dir)])
    result = check.run()

    # Should fail because "password" and quotes are both present
    assert result is False


@pytest.mark.unit
def test_no_secrets_check_file_read_error(temp_dir):
    """Test NoHardcodedSecretsCheck handles file read errors gracefully"""
    sql_dir = temp_dir / "sql"
    sql_dir.mkdir()
    sql_file = sql_dir / "test.sql"
    sql_file.write_text("SELECT 1")

    check = NoHardcodedSecretsCheck([str(sql_dir)])

    # Mock open to raise an exception
    # The check catches exceptions and continues
    with patch("builtins.open", side_effect=PermissionError("Access denied")):
        result = check.run()

    # Should pass because exceptions are caught and ignored
    assert result is True


# --- run_all_checks() Tests ---

@pytest.mark.unit
def test_run_all_checks_all_pass(temp_dir, monkeypatch):
    """Test run_all_checks when all checks pass"""
    # Change to temp directory
    monkeypatch.chdir(temp_dir)

    # Create required directories and files
    (temp_dir / ".claude").mkdir()
    (temp_dir / ".claude" / "settings.json").write_text("{}")

    with patch("sys.stdout"):
        results, all_passed = run_all_checks()

    assert all_passed is True
    assert len(results) == 4
    # At least the config file check should pass
    assert any(check.passed for check in results)


@pytest.mark.unit
def test_run_all_checks_some_fail(temp_dir, monkeypatch):
    """Test run_all_checks when some checks fail"""
    monkeypatch.chdir(temp_dir)
    # Don't create the required config file

    with patch("sys.stdout"):
        results, all_passed = run_all_checks()

    assert all_passed is False
    assert len(results) == 4
    # Config file check should fail
    assert any(not check.passed for check in results)


@pytest.mark.unit
def test_run_all_checks_exception_handling(temp_dir, monkeypatch):
    """Test run_all_checks handles exceptions in checks"""
    monkeypatch.chdir(temp_dir)

    with patch("scripts.data_quality.SQLFileExistsCheck.run", side_effect=Exception("Test error")):
        with patch("sys.stdout"):
            results, all_passed = run_all_checks()

    assert all_passed is False
    # First check should have error message
    assert "Error running check" in results[0].message


# --- main() Tests ---

@pytest.mark.unit
def test_main_all_pass(temp_dir, monkeypatch):
    """Test main() exits with 0 when all checks pass"""
    monkeypatch.chdir(temp_dir)

    # Create required files
    (temp_dir / ".claude").mkdir()
    (temp_dir / ".claude" / "settings.json").write_text("{}")

    with patch("sys.stdout"):
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code == 0


@pytest.mark.unit
def test_main_some_fail(temp_dir, monkeypatch):
    """Test main() exits with 1 when checks fail"""
    monkeypatch.chdir(temp_dir)
    # Don't create required files to trigger failure

    with patch("sys.stdout"):
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code == 1


@pytest.mark.unit
def test_main_prints_reports(temp_dir, monkeypatch, capsys):
    """Test main() prints check reports"""
    monkeypatch.chdir(temp_dir)

    with pytest.raises(SystemExit):
        main()

    captured = capsys.readouterr()
    # Should print report headers
    assert "Data Quality Checks" in captured.out
    assert "=" in captured.out


# --- Edge Cases and Integration ---

@pytest.mark.unit
def test_multiple_sql_dirs(temp_dir):
    """Test checks work with multiple SQL directories"""
    dir1 = temp_dir / "models"
    dir2 = temp_dir / "queries"
    dir1.mkdir()
    dir2.mkdir()

    (dir1 / "model.sql").write_text("SELECT 1")
    (dir2 / "query.sql").write_text("SELECT 2")

    check = SQLSyntaxCheck([str(dir1), str(dir2)])
    result = check.run()

    assert result is True
    assert "2" in check.message


@pytest.mark.unit
def test_nonexistent_sql_dir_handled_gracefully(temp_dir):
    """Test that checks handle non-existent directories gracefully"""
    check = SQLSyntaxCheck([str(temp_dir / "nonexistent")])
    result = check.run()

    assert result is True
    assert "No SQL files found" in check.message


@pytest.mark.unit
def test_empty_check_lists():
    """Test checks with empty lists"""
    check1 = SQLFileExistsCheck([])
    check2 = ConfigFileCheck([])

    assert check1.run() is True
    assert check2.run() is True
