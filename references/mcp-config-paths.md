# MCP Config Paths for PAT Discovery

Confluence PAT tokens are stored in MCP server configurations across AI IDEs.

## Discovery Order (Priority)

### 1. Environment Variable (Highest Priority)
```
CONFLUENCE_API_TOKEN=<token>
CONFLUENCE_PAT=<token>
CONFLUENCE_BASE_URL=https://confluence.example.com
CONFLUENCE_HOST=https://confluence.example.com
```

### 2. OpenCode (Project-Level)
```
Windows/Linux/Mac:
  ./.opencode/.mcp.json
  ./.opencode/mcp.json
```

### 3. OpenCode (User-Level)
```
Windows:  %USERPROFILE%\.opencode\.mcp.json
Linux:    ~/.opencode/.mcp.json
Mac:      ~/.config/opencode/mcp.json
```

### 4. Claude Desktop
```
Windows:  %APPDATA%\Claude\claude_desktop_config.json
Mac:      ~/Library/Application Support/Claude/claude_desktop_config.json
Linux:    ~/.config/Claude/claude_desktop_config.json
```

### 5. Claude Code
```
All:      ~/.claude/mcp.json
Alt:      ~/.claude.json
```

### 6. Cursor
```
Project:  ./.cursor/mcp.json
User:     ~/.cursor/mcp.json
```

### 7. Antigravity
```
Windows:  %APPDATA%\Antigravity\mcp.json
          %APPDATA%\Antigravity\settings\mcp.json
```

### 8. Windsurf (Codeium)
```
Windows:  %USERPROFILE%\.windsurf\mcp.json
          %USERPROFILE%\.codeium\windsurf\mcp_config.json
Mac:      ~/.windsurf/mcp.json
```

### 9. VS Code + Cline/Roo Extensions
```
Windows:  %APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
          %APPDATA%\Code\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json
```

## Config JSON Structure

### Standard MCP Config
```json
{
  "mcpServers": {
    "compasify-confluence-dc": {
      "command": "npx",
      "args": ["-y", "@compasify/confluence-dc"],
      "env": {
        "CONFLUENCE_BASE_URL": "https://confluence.example.com",
        "CONFLUENCE_API_TOKEN": "your-personal-access-token",
        "CONFLUENCE_PAT": "your-personal-access-token"
      }
    }
  }
}
```

### Claude Desktop Config
```json
{
  "mcpServers": {
    "confluence": {
      "command": "npx",
      "args": ["-y", "@compasify/confluence-dc"],
      "env": {
        "CONFLUENCE_HOST": "https://confluence.example.com",
        "CONFLUENCE_API_TOKEN": "token-here"
      }
    }
  }
}
```

### Cline/Roo Config
```json
{
  "mcpServers": {
    "confluence": {
      "command": "npx",
      "args": ["-y", "@compasify/confluence-dc"],
      "env": {
        "CONFLUENCE_BASE_URL": "https://confluence.example.com",
        "CONFLUENCE_PAT": "token-here"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## PAT Extraction Logic

The script searches for keys containing: `PAT`, `TOKEN`, `PERSONAL_ACCESS`, `BEARER`, `AUTH` in the `env` section of Confluence-related MCP server entries. Server name/args must contain `confluence` or `atlassian`.
