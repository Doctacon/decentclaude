# MCP Server Development Guide

## Overview

The Model Context Protocol (MCP) enables developers to build custom servers that extend Claude Code's capabilities. This guide covers everything from basic concepts to production deployment.

## MCP Architecture

### Core Concepts

1. **Protocol**: JSON-RPC 2.0 based communication
2. **Transport**: stdio, SSE, or WebSocket
3. **Server**: Exposes tools and resources
4. **Client**: Claude Code (or other MCP clients)
5. **Tools**: Functions Claude can invoke
6. **Resources**: Data Claude can access
7. **Prompts**: Reusable prompt templates

### Communication Flow

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│             │  JSON-  │              │  Tool   │              │
│ Claude Code │  RPC    │  MCP Server  │  Calls  │   External   │
│   (Client)  │ ◄──────►│              │ ◄──────►│   Services   │
│             │         │              │         │              │
└─────────────┘         └──────────────┘         └──────────────┘
```

### Message Types

1. **Request**: Client calls tool or requests resource
2. **Response**: Server returns result
3. **Notification**: One-way message (no response expected)
4. **Error**: Error response

## Getting Started

### Prerequisites

- Node.js 18+ or Python 3.10+
- Basic understanding of JSON-RPC
- Familiarity with async programming

### Choose Your Language

MCP servers can be built in any language that supports JSON-RPC. Official SDKs:

- **TypeScript/JavaScript**: `@modelcontextprotocol/sdk`
- **Python**: `mcp`

## Building Your First MCP Server

### TypeScript/Node.js Server

#### Installation

```bash
# Create new project
mkdir my-mcp-server
cd my-mcp-server
npm init -y

# Install MCP SDK
npm install @modelcontextprotocol/sdk

# Install TypeScript (if needed)
npm install -D typescript @types/node
npx tsc --init
```

#### Basic Server Structure

```typescript
// src/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// Create server instance
const server = new Server(
  {
    name: "my-custom-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "hello",
        description: "Say hello to someone",
        inputSchema: {
          type: "object",
          properties: {
            name: {
              type: "string",
              description: "Name of the person to greet",
            },
          },
          required: ["name"],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "hello") {
    const personName = args.name as string;
    return {
      content: [
        {
          type: "text",
          text: `Hello, ${personName}!`,
        },
      ],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP Server running on stdio");
}

main().catch(console.error);
```

#### Build and Run

```bash
# Add to package.json
{
  "name": "my-mcp-server",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "my-mcp-server": "./build/index.js"
  },
  "scripts": {
    "build": "tsc",
    "start": "node build/index.js"
  }
}

# Build
npm run build

# Test locally
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node build/index.js
```

### Python Server

#### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install MCP SDK
pip install mcp
```

#### Basic Server Structure

```python
# src/server.py
import asyncio
import json
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Create server instance
server = Server("my-custom-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="hello",
            description="Say hello to someone",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the person to greet",
                    },
                },
                "required": ["name"],
            },
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    if name == "hello":
        person_name = arguments["name"]
        return [
            TextContent(
                type="text",
                text=f"Hello, {person_name}!",
            )
        ]

    raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

if __name__ == "__main__":
    asyncio.run(main())
```

#### Run Python Server

```bash
python src/server.py
```

## Tool Development

### Tool Definition

Tools must include:
1. **name**: Unique identifier
2. **description**: What the tool does
3. **inputSchema**: JSON Schema for parameters

```typescript
{
  name: "calculate",
  description: "Perform mathematical calculations",
  inputSchema: {
    type: "object",
    properties: {
      operation: {
        type: "string",
        enum: ["add", "subtract", "multiply", "divide"],
        description: "Mathematical operation to perform",
      },
      a: {
        type: "number",
        description: "First operand",
      },
      b: {
        type: "number",
        description: "Second operand",
      },
    },
    required: ["operation", "a", "b"],
  },
}
```

### Input Validation

```typescript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "calculate") {
    // Validate inputs
    const { operation, a, b } = args;

    if (typeof a !== "number" || typeof b !== "number") {
      throw new Error("Operands must be numbers");
    }

    if (!["add", "subtract", "multiply", "divide"].includes(operation)) {
      throw new Error("Invalid operation");
    }

    if (operation === "divide" && b === 0) {
      throw new Error("Division by zero");
    }

    // Perform calculation
    let result: number;
    switch (operation) {
      case "add":
        result = a + b;
        break;
      case "subtract":
        result = a - b;
        break;
      case "multiply":
        result = a * b;
        break;
      case "divide":
        result = a / b;
        break;
    }

    return {
      content: [
        {
          type: "text",
          text: `Result: ${result}`,
        },
      ],
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});
```

### Error Handling

```typescript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    // Tool implementation
    const result = await performOperation(request.params);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(result),
        },
      ],
    };
  } catch (error) {
    // Return error as tool result
    return {
      content: [
        {
          type: "text",
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});
```

### Async Operations

```typescript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "fetch_data") {
    const url = args.url as string;

    try {
      // Async API call
      const response = await fetch(url);
      const data = await response.json();

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(data, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `Failed to fetch data: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
});
```

## Resources

### Resource Definition

Resources provide data that Claude can access:

```typescript
import {
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// List available resources
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: "config://app/settings",
        name: "Application Settings",
        description: "Current application configuration",
        mimeType: "application/json",
      },
      {
        uri: "file://logs/app.log",
        name: "Application Logs",
        description: "Recent application logs",
        mimeType: "text/plain",
      },
    ],
  };
});

// Read resource content
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (uri === "config://app/settings") {
    const config = {
      debug: true,
      port: 3000,
      database: "postgresql://localhost/app",
    };

    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify(config, null, 2),
        },
      ],
    };
  }

  if (uri === "file://logs/app.log") {
    const logs = await readFile("./logs/app.log", "utf-8");

    return {
      contents: [
        {
          uri,
          mimeType: "text/plain",
          text: logs,
        },
      ],
    };
  }

  throw new Error(`Unknown resource: ${uri}`);
});
```

### Dynamic Resources

```typescript
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  // Parse URI
  const match = uri.match(/^db:\/\/([^/]+)\/(.+)$/);
  if (match) {
    const [, database, table] = match;

    // Query database
    const rows = await queryDatabase(database, table);

    return {
      contents: [
        {
          uri,
          mimeType: "application/json",
          text: JSON.stringify(rows, null, 2),
        },
      ],
    };
  }

  throw new Error(`Invalid resource URI: ${uri}`);
});
```

## Prompts

### Prompt Templates

```typescript
import {
  ListPromptsRequestSchema,
  GetPromptRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// List available prompts
server.setRequestHandler(ListPromptsRequestSchema, async () => {
  return {
    prompts: [
      {
        name: "code_review",
        description: "Generate a code review for a pull request",
        arguments: [
          {
            name: "pr_number",
            description: "Pull request number",
            required: true,
          },
          {
            name: "repository",
            description: "Repository name",
            required: true,
          },
        ],
      },
    ],
  };
});

// Get prompt content
server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "code_review") {
    const { pr_number, repository } = args;

    return {
      messages: [
        {
          role: "user",
          content: {
            type: "text",
            text: `Please review pull request #${pr_number} in ${repository}:

1. Check code quality and style
2. Identify potential bugs
3. Suggest improvements
4. Verify test coverage
5. Check documentation

Provide a detailed review with specific recommendations.`,
          },
        },
      ],
    };
  }

  throw new Error(`Unknown prompt: ${name}`);
});
```

## Advanced Patterns

### Authentication

```typescript
import { AuthenticationRequestSchema } from "@modelcontextprotocol/sdk/types.js";

// Handle authentication
server.setRequestHandler(AuthenticationRequestSchema, async (request) => {
  const { token } = request.params;

  // Verify token
  const isValid = await verifyToken(token);

  if (!isValid) {
    throw new Error("Invalid authentication token");
  }

  return {
    authenticated: true,
  };
});

// Check authentication in tool handlers
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // Verify request is authenticated
  if (!request.context?.authenticated) {
    throw new Error("Authentication required");
  }

  // Handle tool call
  // ...
});
```

### Caching

```typescript
import { LRUCache } from "lru-cache";

const cache = new LRUCache<string, any>({
  max: 100,
  ttl: 1000 * 60 * 5, // 5 minutes
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "fetch_data") {
    const url = args.url as string;

    // Check cache
    const cached = cache.get(url);
    if (cached) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(cached),
          },
        ],
      };
    }

    // Fetch data
    const response = await fetch(url);
    const data = await response.json();

    // Store in cache
    cache.set(url, data);

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(data),
        },
      ],
    };
  }
});
```

### Rate Limiting

```typescript
import { RateLimiter } from "limiter";

const limiter = new RateLimiter({
  tokensPerInterval: 10,
  interval: "minute",
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // Check rate limit
  const hasToken = await limiter.removeTokens(1);
  if (!hasToken) {
    throw new Error("Rate limit exceeded. Please try again later.");
  }

  // Handle tool call
  // ...
});
```

### Logging

```typescript
import { createLogger } from "winston";

const logger = createLogger({
  level: "info",
  format: combine(timestamp(), json()),
  transports: [
    new transports.File({ filename: "error.log", level: "error" }),
    new transports.File({ filename: "combined.log" }),
  ],
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  logger.info("Tool called", {
    tool: name,
    arguments: args,
  });

  try {
    const result = await handleTool(name, args);

    logger.info("Tool succeeded", {
      tool: name,
    });

    return result;
  } catch (error) {
    logger.error("Tool failed", {
      tool: name,
      error: error.message,
      stack: error.stack,
    });

    throw error;
  }
});
```

## Testing

### Unit Tests

```typescript
import { describe, it, expect } from "vitest";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { CallToolRequestSchema } from "@modelcontextprotocol/sdk/types.js";

describe("MCP Server", () => {
  it("should handle hello tool", async () => {
    const server = createServer();

    const request = {
      jsonrpc: "2.0" as const,
      id: 1,
      method: "tools/call",
      params: {
        name: "hello",
        arguments: {
          name: "World",
        },
      },
    };

    const response = await server.handleRequest(request);

    expect(response.content[0].text).toBe("Hello, World!");
  });

  it("should handle invalid tool", async () => {
    const server = createServer();

    const request = {
      jsonrpc: "2.0" as const,
      id: 1,
      method: "tools/call",
      params: {
        name: "invalid",
        arguments: {},
      },
    };

    await expect(
      server.handleRequest(request)
    ).rejects.toThrow("Unknown tool: invalid");
  });
});
```

### Integration Tests

```typescript
import { spawn } from "child_process";
import { it, expect } from "vitest";

it("should start server and respond to requests", async () => {
  // Start server
  const serverProcess = spawn("node", ["build/index.js"]);

  // Send request
  const request = JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "tools/list",
  }) + "\n";

  serverProcess.stdin.write(request);

  // Read response
  const response = await new Promise((resolve) => {
    serverProcess.stdout.once("data", (data) => {
      resolve(JSON.parse(data.toString()));
    });
  });

  expect(response.result.tools).toBeDefined();
  expect(response.result.tools.length).toBeGreaterThan(0);

  // Cleanup
  serverProcess.kill();
});
```

## Deployment

### Package for Distribution

#### npm Package

```json
{
  "name": "@myorg/mcp-server-custom",
  "version": "1.0.0",
  "description": "Custom MCP server",
  "type": "module",
  "bin": {
    "mcp-server-custom": "./build/index.js"
  },
  "files": [
    "build/"
  ],
  "scripts": {
    "build": "tsc",
    "prepublishOnly": "npm run build"
  },
  "keywords": ["mcp", "model-context-protocol"],
  "author": "Your Name",
  "license": "MIT"
}
```

Publish:
```bash
npm publish
```

#### Python Package

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="mcp-server-custom",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "mcp>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "mcp-server-custom=server:main",
        ],
    },
    author="Your Name",
    description="Custom MCP server",
    keywords=["mcp", "model-context-protocol"],
    python_requires=">=3.10",
)
```

Publish:
```bash
python -m build
twine upload dist/*
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY build/ ./build/

USER node

ENTRYPOINT ["node", "build/index.js"]
```

Build and run:
```bash
docker build -t mcp-server-custom .
docker run -i mcp-server-custom
```

### Configuration in Claude Code

After publishing, users configure in `settings.json`:

```json
{
  "mcpServers": {
    "custom": {
      "command": "npx",
      "args": ["-y", "@myorg/mcp-server-custom"],
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

## Best Practices

### Security

1. **Validate All Inputs**: Never trust client data
2. **Use Environment Variables**: For secrets
3. **Implement Rate Limiting**: Prevent abuse
4. **Sanitize Outputs**: Prevent injection attacks
5. **Use HTTPS**: For network transports
6. **Implement Authentication**: When appropriate

### Performance

1. **Use Async Operations**: Don't block
2. **Implement Caching**: When appropriate
3. **Limit Result Sizes**: Prevent memory issues
4. **Use Streaming**: For large responses
5. **Monitor Resource Usage**: Set limits

### Reliability

1. **Handle Errors Gracefully**: Always catch exceptions
2. **Implement Retries**: For transient failures
3. **Add Timeouts**: Prevent hanging operations
4. **Log Everything**: For debugging
5. **Monitor Health**: Implement health checks

### User Experience

1. **Clear Tool Descriptions**: Help Claude understand
2. **Comprehensive Input Schemas**: Document parameters
3. **Helpful Error Messages**: Guide users
4. **Consistent Naming**: Use conventions
5. **Provide Examples**: In documentation

## Example: Complete MCP Server

Here's a complete example combining everything:

```typescript
// src/index.ts
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { LRUCache } from "lru-cache";
import winston from "winston";

// Setup logger
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || "info",
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: "error.log", level: "error" }),
    new winston.transports.File({ filename: "combined.log" }),
  ],
});

// Setup cache
const cache = new LRUCache<string, any>({
  max: 100,
  ttl: 1000 * 60 * 5,
});

// Create server
const server = new Server(
  {
    name: "example-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

// List tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "fetch_url",
        description: "Fetch content from a URL",
        inputSchema: {
          type: "object",
          properties: {
            url: {
              type: "string",
              description: "URL to fetch",
            },
          },
          required: ["url"],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  logger.info("Tool called", { tool: name, arguments: args });

  try {
    if (name === "fetch_url") {
      const url = args.url as string;

      // Check cache
      const cached = cache.get(url);
      if (cached) {
        logger.info("Cache hit", { url });
        return {
          content: [{ type: "text", text: cached }],
        };
      }

      // Fetch URL
      const response = await fetch(url);
      const text = await response.text();

      // Cache result
      cache.set(url, text);

      logger.info("Tool succeeded", { tool: name });

      return {
        content: [{ type: "text", text }],
      };
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error) {
    logger.error("Tool failed", {
      tool: name,
      error: error.message,
    });

    return {
      content: [
        {
          type: "text",
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  logger.info("MCP Server started");
}

main().catch((error) => {
  logger.error("Server failed to start", { error: error.message });
  process.exit(1);
});
```

## Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [MCP SDK Documentation](https://github.com/modelcontextprotocol/sdk)
- [Example Servers](https://github.com/modelcontextprotocol/servers)
- [JSON-RPC 2.0 Spec](https://www.jsonrpc.org/specification)
- [JSON Schema](https://json-schema.org/)
