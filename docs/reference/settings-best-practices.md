# Claude Code Settings Best Practices

## Overview

This guide provides comprehensive recommendations for configuring Claude Code through `settings.json`. Proper configuration maximizes productivity, security, and team collaboration.

## Settings File Structure

### Location

```bash
# Global settings (all projects)
~/.config/claude/settings.json

# Project-specific settings (override global)
/path/to/project/.claude/settings.json

# Team settings (shared via git)
/path/to/project/.claude/settings.team.json
```

### Basic Structure

```json
{
  "modelId": "claude-sonnet-4-5-20251029",
  "maxTokens": 8000,
  "temperature": 1.0,
  "mcpServers": {},
  "hooks": {},
  "skills": {},
  "customCommands": {},
  "allowedTools": [],
  "contextWindow": {
    "maxFiles": 50,
    "maxFileSize": 100000
  }
}
```

## Model Selection Guidelines

### Model Comparison

| Model | Use Case | Context Window | Speed | Cost |
|-------|----------|----------------|-------|------|
| Claude Opus 4.5 | Complex reasoning, architecture | 200K | Slower | Higher |
| Claude Sonnet 4.5 | Balanced performance (recommended) | 200K | Fast | Medium |
| Claude Haiku 3.5 | Simple tasks, fast iteration | 200K | Fastest | Lower |

### Recommended Configurations

**General Development** (Recommended):
```json
{
  "modelId": "claude-sonnet-4-5-20251029",
  "maxTokens": 8000,
  "temperature": 1.0
}
```

**Complex Architecture/Design**:
```json
{
  "modelId": "claude-opus-4-5-20251101",
  "maxTokens": 8000,
  "temperature": 1.0
}
```

**Fast Iteration/Simple Tasks**:
```json
{
  "modelId": "claude-haiku-3-5-20250128",
  "maxTokens": 4000,
  "temperature": 1.0
}
```

**Code Review**:
```json
{
  "modelId": "claude-sonnet-4-5-20251029",
  "maxTokens": 8000,
  "temperature": 0.7
}
```

### Temperature Settings

- **1.0** (Default): Balanced creativity and consistency
- **0.7-0.9**: More focused, consistent (code review, documentation)
- **1.0-1.2**: More creative (brainstorming, design)

## Context Window Optimization

### File Selection Strategy

```json
{
  "contextWindow": {
    "maxFiles": 50,
    "maxFileSize": 100000,
    "maxTotalSize": 1000000,
    "prioritize": [
      "recently_modified",
      "frequently_accessed",
      "small_files"
    ],
    "exclude": [
      "**/node_modules/**",
      "**/dist/**",
      "**/build/**",
      "**/.git/**",
      "**/coverage/**",
      "**/*.min.js",
      "**/*.map"
    ]
  }
}
```

### Smart Context Loading

```json
{
  "contextWindow": {
    "autoLoad": {
      "readme": true,
      "architecture": true,
      "recentChanges": true,
      "relatedFiles": true
    },
    "loadingStrategy": "lazy",
    "caching": {
      "enabled": true,
      "ttl": 3600
    }
  }
}
```

### Context Compression

```json
{
  "contextWindow": {
    "compression": {
      "enabled": true,
      "summarizeOldMessages": true,
      "summarizeThreshold": 50,
      "keepRecent": 10
    }
  }
}
```

## MCP Server Configuration

### Production Configuration

```json
{
  "mcpServers": {
    "github": {
      "command": "bash",
      "args": [
        "-c",
        "GITHUB_TOKEN=$(cat ~/.config/github/token) npx -y @modelcontextprotocol/server-github"
      ],
      "timeout": 30000,
      "retries": 3
    },
    "postgres-prod": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${POSTGRES_PROD_URL}"
      },
      "timeout": 10000
    },
    "datadog": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-datadog"],
      "env": {
        "DD_API_KEY": "${DD_API_KEY}",
        "DD_APP_KEY": "${DD_APP_KEY}",
        "DD_SITE": "datadoghq.com"
      }
    }
  }
}
```

### Development Configuration

```json
{
  "mcpServers": {
    "postgres-dev": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_HOST": "localhost",
        "POSTGRES_PORT": "5432",
        "POSTGRES_USER": "dev",
        "POSTGRES_PASSWORD": "dev",
        "POSTGRES_DATABASE": "dev_db"
      }
    },
    "sqlite-local": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sqlite", "./dev.db"]
    }
  }
}
```

### Environment-Specific Servers

```json
{
  "mcpServers": {
    "database": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${DATABASE_URL}"
      }
    }
  },
  "environments": {
    "development": {
      "DATABASE_URL": "postgresql://localhost:5432/dev_db"
    },
    "staging": {
      "DATABASE_URL": "postgresql://staging-host:5432/staging_db"
    },
    "production": {
      "DATABASE_URL": "${PROD_DATABASE_URL}"
    }
  }
}
```

## Hook Configuration

### Essential Hooks

```json
{
  "hooks": {
    "sessionStart": "./hooks/session-start.sh",
    "sessionEnd": "./hooks/session-end.sh",
    "beforeCommit": "./hooks/pre-commit.sh",
    "afterCommit": "./hooks/post-commit.sh",
    "onError": "./hooks/error-handler.sh"
  }
}
```

### Session Hooks

**Session Start Hook** (`hooks/session-start.sh`):
```bash
#!/bin/bash

echo "=== Session Starting ==="
echo "Project: $(basename $(pwd))"
echo "Branch: $(git branch --show-current)"
echo ""

# Load project context
if [ -f .claude/context.md ]; then
    cat .claude/context.md
fi

# Check environment
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
fi

# Pull latest changes
git fetch origin

# Show recent activity
echo ""
echo "=== Recent Commits ==="
git log --oneline -5

echo ""
echo "=== Modified Files ==="
git status --short
```

**Session End Hook** (`hooks/session-end.sh`):
```bash
#!/bin/bash

echo "=== Session Ending ==="

# Save session summary
DATE=$(date +%Y-%m-%d-%H-%M)
mkdir -p .claude/sessions

cat > ".claude/sessions/${DATE}.md" <<EOF
# Session: $DATE

## Changes
$(git diff --stat)

## Modified Files
$(git status --short)

## New Files
$(git ls-files --others --exclude-standard)

## Session Duration
[Manual entry needed]

## Summary
[Claude will fill this in]
EOF

echo "Session summary saved to .claude/sessions/${DATE}.md"

# Update context
./hooks/update-context.sh 2>/dev/null || true

# Run tests
if [ -f package.json ]; then
    npm test 2>/dev/null || echo "Tests not run"
fi
```

### Git Hooks

**Pre-Commit Hook** (`hooks/pre-commit.sh`):
```bash
#!/bin/bash

echo "Running pre-commit checks..."

# Check for secrets
if git diff --cached | grep -i -E '(api[_-]?key|password|secret|token).*=.*[a-zA-Z0-9]{20,}'; then
    echo "❌ Possible secret detected in commit"
    echo "Please remove secrets before committing"
    exit 1
fi

# Check for debug code
if git diff --cached | grep -E '(console\.log|debugger|pdb\.set_trace)'; then
    echo "⚠️  Debug code detected"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Run linter
if [ -f package.json ]; then
    npm run lint 2>/dev/null || echo "Linting skipped"
fi

# Run tests
if [ -f package.json ]; then
    npm test 2>/dev/null || echo "Tests skipped"
fi

echo "✓ Pre-commit checks passed"
```

### Error Hooks

**Error Handler** (`hooks/error-handler.sh`):
```bash
#!/bin/bash

ERROR_MSG="$1"
ERROR_CODE="$2"
ERROR_CONTEXT="$3"

DATE=$(date +%Y-%m-%d-%H-%M-%S)
ERROR_LOG=".claude/errors/${DATE}.log"

mkdir -p .claude/errors

# Save error details
cat > "$ERROR_LOG" <<EOF
# Error Report: $DATE

## Error
Code: $ERROR_CODE
Message: $ERROR_MSG

## Context
$ERROR_CONTEXT

## Environment
$(env | grep -v PASSWORD | grep -v SECRET | grep -v TOKEN)

## Git State
Branch: $(git branch --show-current)
Commit: $(git rev-parse HEAD)

Status:
$(git status)

Recent commits:
$(git log --oneline -5)

## System Info
OS: $(uname -s)
Shell: $SHELL
PWD: $(pwd)
EOF

echo "Error logged to: $ERROR_LOG"

# Notify team (optional)
if [ -n "$SLACK_WEBHOOK" ]; then
    curl -X POST "$SLACK_WEBHOOK" \
        -H 'Content-Type: application/json' \
        -d "{\"text\":\"Claude Code Error: $ERROR_MSG\"}" \
        2>/dev/null || true
fi
```

## Custom Commands

### Productivity Commands

```json
{
  "customCommands": {
    "review": {
      "description": "Review current changes",
      "command": "git diff HEAD",
      "prompt": "Review these changes and provide feedback"
    },
    "test-current": {
      "description": "Test current file",
      "command": "npm test -- ${currentFile}",
      "prompt": "Run tests for the current file and analyze results"
    },
    "analyze-deps": {
      "description": "Analyze dependencies",
      "command": "npm audit && npm outdated",
      "prompt": "Analyze dependency audit and outdated packages, recommend updates"
    },
    "db-schema": {
      "description": "Show database schema",
      "command": "psql $DATABASE_URL -c '\\dt' && psql $DATABASE_URL -c '\\d+'",
      "prompt": "Analyze the database schema and suggest improvements"
    }
  }
}
```

### Project Commands

```json
{
  "customCommands": {
    "build-check": {
      "description": "Build and check for errors",
      "command": "npm run build 2>&1",
      "prompt": "Analyze build output and fix any errors"
    },
    "coverage": {
      "description": "Check test coverage",
      "command": "npm run test:coverage",
      "prompt": "Analyze test coverage and suggest areas needing more tests"
    },
    "perf-check": {
      "description": "Check performance",
      "command": "./scripts/performance-check.sh",
      "prompt": "Analyze performance metrics and suggest optimizations"
    }
  }
}
```

## Skill and Subagent Organization

### Skill Structure

```
.claude/
├── skills/
│   ├── code-review/
│   │   ├── skill.json
│   │   ├── templates/
│   │   │   ├── security-review.md
│   │   │   ├── performance-review.md
│   │   │   └── general-review.md
│   │   └── checklist.md
│   ├── testing/
│   │   ├── skill.json
│   │   ├── templates/
│   │   │   ├── unit-test.md
│   │   │   ├── integration-test.md
│   │   │   └── e2e-test.md
│   │   └── coverage-goals.md
│   └── documentation/
│       ├── skill.json
│       ├── templates/
│       │   ├── api-doc.md
│       │   ├── readme.md
│       │   └── architecture.md
│       └── style-guide.md
```

### Skill Configuration

```json
{
  "skills": {
    "code-review": {
      "path": ".claude/skills/code-review",
      "description": "Comprehensive code review",
      "triggers": ["review", "/review"],
      "templates": [
        "security-review",
        "performance-review",
        "general-review"
      ]
    },
    "testing": {
      "path": ".claude/skills/testing",
      "description": "Generate and run tests",
      "triggers": ["test", "/test"],
      "config": {
        "coverageThreshold": 80,
        "testFramework": "jest"
      }
    },
    "refactor": {
      "path": ".claude/skills/refactor",
      "description": "Refactoring assistance",
      "triggers": ["refactor", "/refactor"],
      "config": {
        "preserveTests": true,
        "updateDocs": true
      }
    }
  }
}
```

### Subagent Configuration

```json
{
  "subagents": {
    "frontend": {
      "model": "claude-sonnet-4-5-20251029",
      "specialization": "React/TypeScript frontend",
      "context": [
        "src/frontend/**",
        "docs/frontend/**"
      ],
      "skills": ["testing", "code-review"],
      "tools": ["github", "npm"]
    },
    "backend": {
      "model": "claude-sonnet-4-5-20251029",
      "specialization": "Node.js/Express backend",
      "context": [
        "src/backend/**",
        "docs/backend/**"
      ],
      "skills": ["testing", "code-review", "database"],
      "tools": ["github", "postgres", "datadog"]
    },
    "devops": {
      "model": "claude-opus-4-5-20251101",
      "specialization": "Infrastructure and deployment",
      "context": [
        "infrastructure/**",
        ".github/**",
        "docker/**"
      ],
      "skills": ["deployment", "monitoring"],
      "tools": ["github", "datadog", "aws"]
    }
  }
}
```

## Security Best Practices

### Secure Credential Storage

**DO NOT** store credentials in settings.json:
```json
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_TOKEN": "ghp_actualtoken123"
      }
    }
  }
}
```

**DO** use environment variables or files:
```json
{
  "mcpServers": {
    "github": {
      "command": "bash",
      "args": [
        "-c",
        "GITHUB_TOKEN=$(cat ~/.config/github/token) npx -y @modelcontextprotocol/server-github"
      ]
    }
  }
}
```

### .gitignore Configuration

```bash
# .gitignore

# Never commit settings with secrets
settings.json

# Commit team settings (no secrets)
!.claude/settings.team.json

# Session data
.claude/sessions/
.claude/errors/
.claude/checkpoints/

# Credentials
.config/
*.token
*.key
*.pem
.env
.env.*
!.env.example
```

### Secrets Management

Use a secrets manager:

```bash
# .claude/load-secrets.sh
#!/bin/bash

# Load from environment
export GITHUB_TOKEN="${GITHUB_TOKEN:-$(cat ~/.config/github/token 2>/dev/null)}"
export DATABASE_URL="${DATABASE_URL:-$(cat ~/.config/db/url 2>/dev/null)}"
export DD_API_KEY="${DD_API_KEY:-$(cat ~/.config/datadog/api_key 2>/dev/null)}"

# Or use a secrets manager
if command -v aws &> /dev/null; then
    export GITHUB_TOKEN=$(aws secretsmanager get-secret-value --secret-id github-token --query SecretString --output text)
fi
```

## Team Settings

### Shared Team Configuration

```json
{
  "version": "1.0.0",
  "team": "platform",
  "project": "ecommerce-api",

  "modelId": "claude-sonnet-4-5-20251029",
  "maxTokens": 8000,

  "contextWindow": {
    "exclude": [
      "**/node_modules/**",
      "**/dist/**",
      "**/.next/**",
      "**/coverage/**"
    ]
  },

  "hooks": {
    "sessionStart": "./hooks/session-start.sh",
    "beforeCommit": "./hooks/pre-commit.sh"
  },

  "skills": {
    "code-review": {
      "path": ".claude/skills/code-review"
    }
  },

  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

### Personal Overrides

```json
{
  "extends": ".claude/settings.team.json",

  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_TOKEN": "${MY_GITHUB_TOKEN}"
      }
    },
    "postgres-local": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://localhost:5432/mydb"
      }
    }
  }
}
```

## Performance Optimization

### Response Time Optimization

```json
{
  "performance": {
    "caching": {
      "enabled": true,
      "ttl": 3600,
      "maxSize": 100
    },
    "parallelRequests": true,
    "requestTimeout": 30000,
    "retries": {
      "enabled": true,
      "maxRetries": 3,
      "backoff": "exponential"
    }
  }
}
```

### Resource Limits

```json
{
  "limits": {
    "maxConcurrentRequests": 5,
    "maxFileSize": 1000000,
    "maxContextSize": 180000,
    "requestTimeout": 60000,
    "toolTimeout": 30000
  }
}
```

## Monitoring and Logging

### Logging Configuration

```json
{
  "logging": {
    "level": "info",
    "file": ".claude/logs/claude.log",
    "maxSize": 10485760,
    "maxFiles": 5,
    "console": true,
    "structured": true,
    "includeContext": true
  }
}
```

### Metrics Collection

```json
{
  "metrics": {
    "enabled": true,
    "collectors": [
      "response_time",
      "token_usage",
      "tool_calls",
      "error_rate"
    ],
    "export": {
      "type": "datadog",
      "interval": 60000
    }
  }
}
```

## Example Configurations

### Minimal Configuration

```json
{
  "modelId": "claude-sonnet-4-5-20251029",
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"]
    }
  }
}
```

### Full-Featured Configuration

```json
{
  "version": "1.0.0",
  "modelId": "claude-sonnet-4-5-20251029",
  "maxTokens": 8000,
  "temperature": 1.0,

  "contextWindow": {
    "maxFiles": 50,
    "maxFileSize": 100000,
    "prioritize": ["recently_modified", "frequently_accessed"],
    "exclude": [
      "**/node_modules/**",
      "**/dist/**",
      "**/.git/**"
    ],
    "compression": {
      "enabled": true,
      "summarizeThreshold": 50
    }
  },

  "mcpServers": {
    "github": {
      "command": "bash",
      "args": ["-c", "GITHUB_TOKEN=$(cat ~/.config/github/token) npx -y @modelcontextprotocol/server-github"],
      "timeout": 30000
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "${DATABASE_URL}"
      }
    },
    "datadog": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-datadog"],
      "env": {
        "DD_API_KEY": "${DD_API_KEY}",
        "DD_APP_KEY": "${DD_APP_KEY}"
      }
    }
  },

  "hooks": {
    "sessionStart": "./hooks/session-start.sh",
    "sessionEnd": "./hooks/session-end.sh",
    "beforeCommit": "./hooks/pre-commit.sh",
    "onError": "./hooks/error-handler.sh"
  },

  "skills": {
    "code-review": {
      "path": ".claude/skills/code-review",
      "triggers": ["review", "/review"]
    },
    "testing": {
      "path": ".claude/skills/testing",
      "triggers": ["test", "/test"]
    }
  },

  "customCommands": {
    "review": {
      "command": "git diff HEAD",
      "prompt": "Review these changes"
    },
    "test-current": {
      "command": "npm test -- ${currentFile}",
      "prompt": "Run and analyze tests"
    }
  },

  "performance": {
    "caching": {
      "enabled": true,
      "ttl": 3600
    },
    "parallelRequests": true
  },

  "logging": {
    "level": "info",
    "file": ".claude/logs/claude.log"
  }
}
```

## Migration Guide

### Upgrading Settings

When updating settings format:

```bash
# Backup current settings
cp settings.json settings.json.backup

# Validate new settings
claude validate-settings settings.json

# Test with dry-run
claude --dry-run --settings settings.json

# Apply new settings
cp settings.new.json settings.json
```

### Version Compatibility

```json
{
  "version": "1.0.0",
  "minClaudeVersion": "1.5.0",
  "deprecatedFeatures": [
    {
      "feature": "oldHookFormat",
      "deprecatedIn": "1.4.0",
      "removedIn": "2.0.0",
      "migration": "Use new hook format in hooks/ directory"
    }
  ]
}
```

## Resources

- [Claude Code Documentation](https://docs.claude.com/claude-code)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Settings Schema](https://github.com/anthropics/claude-code/schema/settings.json)
- [Example Configurations](https://github.com/anthropics/claude-code/examples)
