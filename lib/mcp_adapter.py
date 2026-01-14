"""
MCP Adapter - Convert DecentClaude tools to MCP protocol

This module bridges the DecentClaude tool registry with the Model Context Protocol.
It loads tool definitions from the registry and creates MCP-compatible tool wrappers
that execute the actual utilities and return structured results.

Functions:
- load_tools_from_registry: Load tool definitions from JSON registry
- create_mcp_tool: Create MCP-compatible wrapper for a tool
- execute_tool: Execute a DecentClaude utility and capture output
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Callable
from functools import wraps


def load_tools_from_registry(registry_path: Path) -> List[Dict[str, Any]]:
    """Load tool definitions from the tool registry.

    Args:
        registry_path: Path to tool_registry.json

    Returns:
        List of tool definitions with metadata

    Example:
        tools = load_tools_from_registry(Path("lib/tool_registry.json"))
        # Returns: [{"id": "bq-profile", "name": "bq-profile", ...}, ...]
    """
    with open(registry_path) as f:
        registry = json.load(f)

    # Extract tools from registry
    # Filter to only tools that can be executed (have a command)
    tools = [
        tool for tool in registry.get("tools", [])
        if tool.get("command") and tool.get("category") != "kb"  # Exclude KB for now
    ]

    return tools


def execute_tool(tool_path: Path, args: List[str]) -> Dict[str, Any]:
    """Execute a DecentClaude utility and capture output.

    Args:
        tool_path: Path to the tool executable
        args: List of command-line arguments

    Returns:
        Dictionary with execution results:
        {
            "success": bool,
            "output": str,  # stdout
            "error": str,   # stderr if failed
            "exit_code": int
        }

    Example:
        result = execute_tool(
            Path("bin/data-utils/bq-profile"),
            ["project.dataset.table", "--format=json"]
        )
    """
    try:
        # Ensure tool is executable
        if not tool_path.exists():
            return {
                "success": False,
                "output": "",
                "error": f"Tool not found: {tool_path}",
                "exit_code": 1
            }

        # Execute tool
        proc = subprocess.run(
            [str(tool_path)] + args,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        return {
            "success": proc.returncode == 0,
            "output": proc.stdout,
            "error": proc.stderr if proc.returncode != 0 else "",
            "exit_code": proc.returncode
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": "",
            "error": "Tool execution timeout (5 minutes)",
            "exit_code": 124
        }
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": f"Execution error: {str(e)}",
            "exit_code": 1
        }


def build_args_from_params(tool_def: Dict[str, Any], **kwargs) -> List[str]:
    """Build command-line arguments from function parameters.

    Args:
        tool_def: Tool definition from registry
        **kwargs: Named parameters from MCP tool call

    Returns:
        List of command-line arguments

    Example:
        args = build_args_from_params(
            tool_def,
            table_id="project.dataset.users",
            format="json",
            detect_anomalies=True
        )
        # Returns: ["project.dataset.users", "--format=json", "--detect-anomalies"]
    """
    args = []
    inputs = tool_def.get("inputs", {})
    required = inputs.get("required", [])
    optional = inputs.get("optional", [])

    # Add required arguments (positional)
    for param in required:
        if param in kwargs:
            args.append(str(kwargs[param]))
        else:
            raise ValueError(f"Missing required parameter: {param}")

    # Add optional arguments (flags)
    for param in optional:
        if param in kwargs:
            value = kwargs[param]

            # Boolean flags
            if isinstance(value, bool):
                if value:
                    args.append(f"--{param}")
            # Value parameters
            else:
                args.append(f"--{param}={value}")

    return args


def create_mcp_tool(tool_def: Dict[str, Any]) -> Callable:
    """Create MCP-compatible tool wrapper for a registry tool.

    This creates a Python function that:
    1. Accepts parameters matching the tool's inputs
    2. Builds command-line arguments
    3. Executes the actual utility
    4. Returns structured output

    Args:
        tool_def: Tool definition from registry

    Returns:
        Callable function suitable for @mcp.tool() decoration

    Example:
        tool_func = create_mcp_tool({
            "id": "bq-profile",
            "command": "mayor bq profile",
            "description": "Profile a BigQuery table",
            "inputs": {"required": ["table_id"], "optional": ["format"]},
            "path": "bin/data-utils/bq-profile"
        })

        # Can now call:
        result = tool_func(table_id="project.dataset.users", format="json")
    """

    tool_id = tool_def["id"]
    description = tool_def.get("long_description") or tool_def.get("description")
    tool_path = Path(__file__).parent.parent / tool_def.get("path", "")
    inputs = tool_def.get("inputs", {})
    required_params = inputs.get("required", [])
    optional_params = inputs.get("optional", [])

    # Build function signature dynamically
    # Required params become required function args
    # Optional params become optional function args with defaults

    def tool_wrapper(**kwargs) -> str:
        """Dynamic tool wrapper - docstring set below"""

        try:
            # Build command-line arguments
            args = build_args_from_params(tool_def, **kwargs)

            # Execute tool
            result = execute_tool(tool_path, args)

            if result["success"]:
                # Return output (may be JSON, text, etc.)
                return result["output"]
            else:
                # Return error information
                return json.dumps({
                    "error": result["error"],
                    "exit_code": result["exit_code"]
                }, indent=2)

        except Exception as e:
            return json.dumps({
                "error": f"Tool execution failed: {str(e)}",
                "exit_code": 1
            }, indent=2)

    # Set docstring for MCP autodiscovery
    tool_wrapper.__doc__ = description

    # Set function name
    tool_wrapper.__name__ = tool_id.replace("-", "_")

    # Add parameter annotations for MCP
    # MCP will use these for parameter validation
    annotations = {}
    for param in required_params:
        annotations[param] = str

    for param in optional_params:
        # Optional params with defaults
        annotations[param] = str

    tool_wrapper.__annotations__ = annotations

    return tool_wrapper


def load_schemas(schemas_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Load all JSON schemas from schemas directory.

    Args:
        schemas_dir: Path to schemas directory

    Returns:
        Dictionary mapping schema ID to schema definition

    Example:
        schemas = load_schemas(Path("schemas/"))
        bq_profile_schema = schemas["bq-profile"]
    """
    schemas = {}

    if not schemas_dir.exists():
        return schemas

    for schema_file in schemas_dir.glob("*.json"):
        # Skip catalog.json
        if schema_file.name == "catalog.json":
            continue

        try:
            with open(schema_file) as f:
                schema = json.load(f)
                # Use filename (without .json) as schema ID
                schema_id = schema_file.stem
                schemas[schema_id] = schema
        except Exception as e:
            print(f"Warning: Failed to load schema {schema_file}: {e}", file=sys.stderr)

    return schemas
