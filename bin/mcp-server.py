#!/usr/bin/env python3
"""
DecentClaude MCP Server

Exposes DecentClaude tools to Claude Code via Model Context Protocol.
Uses stdio transport for local integration with Claude desktop app.

Usage:
  mcp-server.py

Configuration in claude_desktop_config.json:
  {
    "mcpServers": {
      "decentclaude": {
        "command": "/path/to/decentclaude/bin/mcp-server.py",
        "env": {
          "GOOGLE_CLOUD_PROJECT": "your-project",
          "ANTHROPIC_API_KEY": "your-key"
        }
      }
    }
  }

References:
- MCP Specification: https://modelcontextprotocol.io/specification/2025-11-25
- Python SDK: https://github.com/modelcontextprotocol/python-sdk
"""

import sys
import os
from pathlib import Path

# Add lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Error: mcp library not installed", file=sys.stderr)
    print("Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)

from mcp_adapter import load_tools_from_registry, create_mcp_tool

# Initialize MCP server
mcp = FastMCP(
    "DecentClaude",
    website_url="https://github.com/yourusername/decentclaude",
)


def main():
    """Initialize and run MCP server"""

    # Load tool registry
    registry_path = Path(__file__).parent.parent / "lib" / "tool_registry.json"

    if not registry_path.exists():
        print(f"Error: Tool registry not found at {registry_path}", file=sys.stderr)
        sys.exit(1)

    # Load and register all tools
    tools = load_tools_from_registry(registry_path)

    for tool_def in tools:
        # Create MCP tool wrapper for each registry tool
        tool_func = create_mcp_tool(tool_def)

        # Register with MCP server
        # FastMCP will automatically extract docstring and type hints
        mcp.tool(name=tool_def['id'])(tool_func)

    print(f"Loaded {len(tools)} tools from registry", file=sys.stderr)

    # Run server with stdio transport
    mcp.run()


if __name__ == "__main__":
    main()
