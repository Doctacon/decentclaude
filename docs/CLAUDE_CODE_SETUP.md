# DecentClaude + Claude Code Integration

This guide shows you how to integrate DecentClaude with Claude Code using the Model Context Protocol (MCP).

## What You Get

Once integrated, Claude Code can directly use all DecentClaude tools:

- **BigQuery Tools**: Profile tables, explain queries, optimize SQL, validate syntax, trace lineage
- **dbt Tools**: Test models, compile queries, run models
- **AI Tools**: Generate code, review SQL, create documentation
- **Workflows**: Run data quality audits, schema migrations, query optimization

Claude Code will see these as native capabilities and can use them autonomously.

## Prerequisites

1. **Claude Desktop App** installed
   - Download: https://claude.ai/download
   - Version: 1.0.0 or later (with MCP support)

2. **Python 3.8+** installed
   ```bash
   python --version  # Should be 3.8 or higher
   ```

3. **DecentClaude repository** cloned
   ```bash
   git clone https://github.com/yourusername/decentclaude.git
   cd decentclaude
   ```

4. **Required credentials** (depending on which tools you want to use):
   - Google Cloud service account key (for BigQuery tools)
   - Anthropic API key (for AI tools)

## Installation

### 1. Install Python Dependencies

```bash
cd decentclaude
pip install -r requirements.txt
```

This installs:
- `mcp>=1.0.0` - Model Context Protocol server
- `click>=8.1.0` - CLI framework
- `google-cloud-bigquery>=3.0.0` - BigQuery client
- `anthropic>=0.39.0` - Anthropic API client

### 2. Make MCP Server Executable

```bash
chmod +x bin/mcp-server.py
```

### 3. Test the Server

Verify the MCP server starts correctly:

```bash
./bin/mcp-server.py
```

You should see:
```
Loaded 23 tools from registry
```

Press Ctrl+C to stop. If you see errors, check that:
- Python dependencies are installed
- Tool registry exists at `lib/tool_registry.json`

## Configuration

### 1. Set Up Environment Variables

Create a `.env` file using the wizard:

```bash
./bin/mayor config init
```

Or manually create `.env`:

```bash
cp .env.example .env
# Edit .env with your credentials
```

Required variables:
- `GOOGLE_CLOUD_PROJECT` - Your GCP project ID
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account JSON key
- `ANTHROPIC_API_KEY` - Your Anthropic API key (for AI tools)

### 2. Configure Claude Desktop

#### Option A: Using the Example Config (Recommended)

1. **Copy the example configuration**:
   ```bash
   cp claude_desktop_config.example.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **Edit the configuration**:
   ```bash
   # macOS
   open -e ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # Linux
   nano ~/.config/Claude/claude_desktop_config.json

   # Windows
   notepad %APPDATA%\Claude\claude_desktop_config.json
   ```

3. **Update the paths**:
   - Change `/absolute/path/to/decentclaude` to your actual path
   - Update environment variables with your credentials

#### Option B: Manual Configuration

Add DecentClaude to your existing `claude_desktop_config.json`:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Linux**: `~/.config/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "decentclaude": {
      "command": "/Users/yourname/decentclaude/bin/mcp-server.py",
      "env": {
        "GOOGLE_CLOUD_PROJECT": "your-gcp-project-id",
        "GOOGLE_APPLICATION_CREDENTIALS": "/Users/yourname/.config/gcloud/service-account-key.json",
        "ANTHROPIC_API_KEY": "sk-ant-your-api-key"
      }
    }
  }
}
```

**Important**: Use absolute paths, not relative paths or `~` shortcuts.

### 3. Restart Claude Desktop

Quit and restart the Claude Desktop app to load the MCP server.

## Verification

### Check Server Status

In Claude Desktop, open a new conversation and ask:

```
What MCP servers are connected?
```

You should see `decentclaude` in the list.

### Test a Tool

Try using a BigQuery tool:

```
Can you profile the table project.dataset.users?
```

Claude Code will use the `bq-profile` tool to analyze the table and return results.

### List Available Tools

```
What DecentClaude tools are available?
```

Claude Code will show all 23+ tools it can access.

## Available Tools

Once integrated, Claude Code can use:

### BigQuery (11 tools)
- `bq-profile` - Profile tables with quality scores
- `bq-explain` - Analyze query execution plans
- `bq-optimize` - Get query optimization suggestions
- `bq-validate` - Validate SQL syntax
- `bq-lineage` - Trace table dependencies
- `bq-query-cost` - Estimate query costs
- `bq-partition` - Analyze partitioning strategies
- `bq-cluster` - Recommend clustering columns
- `bq-compare` - Compare table schemas
- `bq-export` - Export tables to formats
- `bq-docs` - Generate table documentation

### dbt (5 tools)
- `dbt-test` - Run dbt tests
- `dbt-compile` - Compile dbt models
- `dbt-run` - Execute dbt models
- `dbt-docs` - Generate dbt docs
- `dbt-lineage` - Show dbt lineage

### AI (3 tools)
- `ai-generate` - Generate code with LLMs
- `ai-review` - Review SQL code
- `ai-docs` - Generate documentation

### Workflows (4 tools)
- `data-quality-audit` - Comprehensive DQ assessment
- `schema-migration` - Schema change analysis
- `query-optimization` - End-to-end query optimization
- `incident-response` - Data incident investigation

## Usage Examples

### Example 1: Profile a Table

**You ask Claude Code**:
```
Profile the analytics.events table and tell me if there are any quality issues
```

**Claude Code uses**:
- `bq-profile` tool with table `analytics.events`
- Receives structured JSON output with quality scores
- Analyzes results and reports findings to you

### Example 2: Optimize a Query

**You ask Claude Code**:
```
Can you optimize this query?

SELECT * FROM large_table
WHERE date > '2024-01-01'
```

**Claude Code uses**:
- `bq-optimize` tool with your SQL
- Receives optimization suggestions
- Shows you improved query with explanations

### Example 3: Run Data Quality Audit

**You ask Claude Code**:
```
Run a data quality audit on the analytics dataset
```

**Claude Code uses**:
- `data-quality-audit` workflow
- Profiles all tables in dataset
- Generates comprehensive quality report

## Troubleshooting

### MCP Server Not Showing Up

**Symptoms**: Claude Code doesn't list `decentclaude` as a connected server

**Solutions**:

1. **Check configuration file location**:
   ```bash
   # macOS
   ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # Linux
   ls -la ~/.config/Claude/claude_desktop_config.json
   ```

2. **Verify JSON syntax**:
   ```bash
   # Use jq to validate
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq .
   ```

3. **Check absolute paths**:
   - Command must be absolute path (not `./bin/mcp-server.py`)
   - Environment variables must use absolute paths

4. **Restart Claude Desktop completely**:
   - Quit app (Cmd+Q on macOS)
   - Wait 5 seconds
   - Reopen

### Tools Execute But Fail

**Symptoms**: Tool calls return errors instead of results

**Solutions**:

1. **Verify environment variables**:
   ```bash
   # Test manually
   export GOOGLE_CLOUD_PROJECT=your-project
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
   ./bin/mcp-server.py
   ```

2. **Check service account permissions**:
   - Service account needs BigQuery Data Viewer role
   - Service account needs BigQuery Job User role

3. **Test tool directly**:
   ```bash
   # Try running tool outside MCP
   ./bin/mayor bq profile project.dataset.table
   ```

### Slow Tool Responses

**Symptoms**: Tools take a long time to respond

**Solutions**:

1. **Enable caching**:
   ```json
   "env": {
     "CACHE_DIR": "~/.cache/decentclaude",
     "CACHE_TTL": "3600"
   }
   ```

2. **Use smaller sample sizes**:
   - Tools like `bq-profile` support `--sample-size` parameter
   - MCP server uses reasonable defaults

3. **Check network latency**:
   - BigQuery tools require network access to GCP
   - VPN or firewall may slow requests

### Debugging

Enable debug logging:

```json
{
  "mcpServers": {
    "decentclaude": {
      "command": "/path/to/bin/mcp-server.py",
      "env": {
        "LOG_LEVEL": "DEBUG",
        "MCP_DEBUG": "true"
      }
    }
  }
}
```

View MCP server logs:
- **macOS**: `~/Library/Logs/Claude/mcp-server-decentclaude.log`
- **Linux**: `~/.local/share/Claude/logs/mcp-server-decentclaude.log`

## Security Considerations

### API Keys

- **Never commit `claude_desktop_config.json` with real credentials**
- Use environment variables when possible
- Rotate API keys regularly

### Service Account Permissions

Use principle of least privilege:

```bash
# BigQuery read-only access
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/bigquery.dataViewer"

# Job execution only
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/bigquery.jobUser"
```

### Data Access

- MCP server runs locally (stdio transport)
- No data sent to external servers (except GCP/Anthropic APIs)
- Claude Code sees tool outputs but doesn't store them permanently

## Advanced Configuration

### Multiple Projects

Configure multiple GCP projects:

```json
{
  "mcpServers": {
    "decentclaude-prod": {
      "command": "/path/to/bin/mcp-server.py",
      "env": {
        "GOOGLE_CLOUD_PROJECT": "prod-project",
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/prod-key.json"
      }
    },
    "decentclaude-dev": {
      "command": "/path/to/bin/mcp-server.py",
      "env": {
        "GOOGLE_CLOUD_PROJECT": "dev-project",
        "GOOGLE_APPLICATION_CREDENTIALS": "/path/to/dev-key.json"
      }
    }
  }
}
```

### Custom Tool Paths

Override tool locations:

```json
"env": {
  "DECENTCLAUDE_HOME": "/custom/path/to/decentclaude"
}
```

## Getting Help

- **Documentation**: `./bin/mayor --help`
- **Tool-specific help**: `./bin/mayor bq profile --help`
- **Issues**: https://github.com/yourusername/decentclaude/issues
- **MCP Spec**: https://modelcontextprotocol.io/specification/2025-11-25

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/specification/2025-11-25)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Claude Code Documentation](https://claude.ai/code)
- [Tool Registry](../lib/tool_registry.json)
- [JSON Schemas](../schemas/)
