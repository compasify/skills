# API Fallback for Large Content

When MCP tool calls fail due to content exceeding ~8-10K character parameter limits, use the direct API script.

## Symptoms of MCP Tool Size Limit

- JSON Parse error: `Expected '}'` — content truncated mid-JSON
- Repeated failures on `createContent` or `updateContent` with large HTML
- Content appears cut off or incomplete on the Confluence page

## Fallback Workflow

### 1. Prepare HTML Content

Write the HTML content to a file:
```bash
# From markdown
npx marked input.md -o output.html

# Post-processing for Confluence storage format
# - Remove <h1> tag (title is set separately via API)
# - Self-close <hr/> tags
# - Remove BOM character if present
```

### 2. Discover PAT Token

```bash
python skills/confluence/scripts/confluence_api.py discover-pat
```

Output:
```json
{
  "found": true,
  "source": ".opencode/.mcp.json",
  "pat_preview": "MzkwMzA3...egJI",
  "pat": "full-token-here",
  "base_url": "https://confluence.example.com"
}
```

If PAT not found, ask user to provide it or point to config file.

### 3. Get Current Page Info (for updates)

```bash
python skills/confluence/scripts/confluence_api.py get \
  --page-id 47486114 \
  --base-url https://confluence.example.com
```

Output includes version number and author — needed for safety checks.

### 4a. Create New Content

```bash
python skills/confluence/scripts/confluence_api.py create \
  --space HTSC \
  --title "Page Title" \
  --type blogpost \
  --file output.html \
  --base-url https://confluence.example.com
```

### 4b. Update Existing Content

```bash
python skills/confluence/scripts/confluence_api.py update \
  --page-id 47486114 \
  --version 0 \
  --file output.html \
  --base-url https://confluence.example.com
```

Version `0` = auto-increment from current version.

### 5. Clean Up

Remove temporary HTML files after successful publish.

## Size Guidelines

| Content Size | Approach |
|-------------|----------|
| < 8K chars | MCP tool `confluence_createContent` / `confluence_updateContent` |
| 8K - 100K chars | Direct API via `confluence_api.py` |
| > 100K chars | Split into parent + child pages |

## Error Handling

| HTTP Status | Meaning | Action |
|-------------|---------|--------|
| 200/201 | Success | Content published |
| 401 | Auth failed | PAT expired or invalid |
| 403 | Forbidden | User lacks permission for this space/page |
| 404 | Not found | Page ID doesn't exist |
| 409 | Version conflict | Someone else updated the page; re-fetch version |
| 413 | Payload too large | Split into child pages |

## Safety Reminders

- Always `get` page info before `update` to check author and version
- Never update without confirming version (prevents overwriting concurrent edits)
- If author ≠ current user, confirm with user before proceeding
- Never delete via this script — deletion requires explicit user confirmation through MCP tool
