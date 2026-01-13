#!/usr/bin/env python3
"""
Example: Using the Plugin System

Demonstrates how to use the DecentClaude plugin system programmatically.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from plugins.core import PluginManager, ConfigManager


def example_basic_usage():
    """Basic plugin discovery and loading"""
    print("=" * 60)
    print("Example 1: Basic Plugin Usage")
    print("=" * 60)

    plugin_dirs = [
        Path(__file__).parent.parent / "plugins" / "builtin",
        Path(__file__).parent.parent / "plugins" / "external"
    ]

    manager = PluginManager(plugin_dirs, system_version="1.0.0")

    print("\nDiscovering plugins...")
    plugins = manager.discover_plugins()

    for plugin_info in plugins:
        manifest = plugin_info["manifest"]
        print(f"  Found: {manifest['name']} v{manifest['version']} ({manifest['type']})")

    print("\nLoading all plugins...")
    try:
        manager.load_all_plugins()
        print(f"  Loaded {len(manager.loaded_plugins)} plugins")
    except Exception as e:
        print(f"  Error: {e}")


def example_with_configuration():
    """Using plugins with custom configuration"""
    print("\n" + "=" * 60)
    print("Example 2: Plugins with Configuration")
    print("=" * 60)

    plugin_dirs = [Path(__file__).parent.parent / "plugins" / "builtin"]

    manager = PluginManager(plugin_dirs, system_version="1.0.0")

    configs = {
        "sql_validator": {
            "enabled": True,
            "strict_mode": True
        },
        "schema_check": {
            "enabled": True,
            "schema_paths": ["schemas", "models"]
        }
    }

    print("\nLoading plugins with custom config...")
    manager.load_all_plugins(configs)

    for name, plugin in manager.loaded_plugins.items():
        print(f"  {name}: {plugin.status.value}")


def example_using_validator():
    """Using a validator plugin"""
    print("\n" + "=" * 60)
    print("Example 3: Using SQL Validator Plugin")
    print("=" * 60)

    plugin_dirs = [Path(__file__).parent.parent / "plugins" / "builtin"]

    manager = PluginManager(plugin_dirs, system_version="1.0.0")
    manager.load_plugin("sql_validator")

    validator = manager.get_plugin("sql_validator")

    test_cases = [
        ("SELECT * FROM users", True),
        ("SELECT * FROM", False),
        ("", False),
    ]

    print("\nValidating SQL queries:")
    for sql, expected in test_cases:
        result = validator.execute({"sql": sql})
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{sql[:30]}...' -> {result}")


def example_using_quality_check():
    """Using a quality check plugin"""
    print("\n" + "=" * 60)
    print("Example 4: Using Quality Check Plugin")
    print("=" * 60)

    plugin_dirs = [Path(__file__).parent.parent / "plugins" / "builtin"]

    manager = PluginManager(plugin_dirs, system_version="1.0.0")

    config = {"schema_paths": ["schemas"]}
    manager.load_plugin("schema_check", config)

    check = manager.get_plugin("schema_check")

    print("\nRunning schema check...")
    result = check.run_check()

    print(f"  Result: {'PASS' if result else 'FAIL'}")
    print(f"  Message: {check.message}")
    print(f"\nFormatted Report:")
    print(f"  {check.get_report()}")


def example_dependency_resolution():
    """Demonstrating dependency resolution"""
    print("\n" + "=" * 60)
    print("Example 5: Dependency Resolution")
    print("=" * 60)

    from plugins.core import DependencyResolver, DependencyTree

    resolver = DependencyResolver()

    resolver.add_plugin("sql_validator", [])
    resolver.add_plugin("schema_check", [])
    resolver.add_plugin("advanced_check", ["sql_validator", "schema_check"])

    print("\nPlugin dependencies:")
    print("  sql_validator: []")
    print("  schema_check: []")
    print("  advanced_check: ['sql_validator', 'schema_check']")

    print("\nResolving load order...")
    load_order = resolver.resolve()
    print(f"  Load order: {' -> '.join(load_order)}")

    print("\nDependency tree:")
    tree = DependencyTree(resolver)
    print(tree.get_full_tree())


def example_version_compatibility():
    """Demonstrating version compatibility checking"""
    print("\n" + "=" * 60)
    print("Example 6: Version Compatibility")
    print("=" * 60)

    from plugins.core import VersionChecker, SemanticVersion

    checker = VersionChecker(system_version="1.2.0")

    test_cases = [
        ("plugin_a", "1.0.0"),
        ("plugin_b", "1.2.0"),
        ("plugin_c", "1.5.0"),
        ("plugin_d", "2.0.0"),
    ]

    print("\nChecking plugin compatibility (system version: 1.2.0):")
    for plugin_name, required_version in test_cases:
        is_compatible, message = checker.check_plugin_compatibility(
            plugin_name, required_version
        )
        status = "✓" if is_compatible else "✗"
        print(f"  {status} {plugin_name} requires {required_version}")


def example_configuration_management():
    """Demonstrating configuration management"""
    print("\n" + "=" * 60)
    print("Example 7: Configuration Management")
    print("=" * 60)

    from plugins.core import ConfigManager

    config_file = Path("/tmp/plugin_config.json")

    manager = ConfigManager(config_file)

    print("\nSetting plugin configurations...")
    manager.set_config("my_plugin", {
        "enabled": True,
        "api_key": "test-key",
        "settings": {
            "timeout": 30,
            "retries": 3
        }
    })

    manager.save_configs()
    print(f"  Saved config to {config_file}")

    config = manager.get_config("my_plugin")
    print(f"\nRetrieving nested config value:")
    print(f"  timeout = {config.get('settings.timeout')}")
    print(f"  retries = {config.get('settings.retries')}")

    manager.update_config("my_plugin", {
        "settings": {
            "timeout": 60
        }
    })

    print(f"\nAfter update:")
    print(f"  timeout = {config.get('settings.timeout')}")


def main():
    """Run all examples"""
    examples = [
        example_basic_usage,
        example_with_configuration,
        example_using_validator,
        example_using_quality_check,
        example_dependency_resolution,
        example_version_compatibility,
        example_configuration_management,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in example: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("Examples Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
