# API Fallback for Large Content

When MCP tool calls fail due to content exceeding parameter limits (typically ~10-20KB), use the direct REST API scripts.

## Symptoms of MCP Tool Size Limit

- JSON Parse error: `Expected '}'` — content truncated mid-JSON
- Repeated failures on `confluence_createContent` or `confluence_updateContent` with large HTML
- Content appears cut off or incomplete on the Confluence page
- Error message indicating request entity too large

## Decision Matrix

| Content Size | Approach | Best Script/Tool |
|-------------|----------|-----------------|
| < 10KB | MCP Tools | `confluence_createContent` / `confluence_updateContent` |
| 10KB - 500KB | Direct API | `scripts/confluence_api.py` |
| Includes Images | Direct API | `scripts/upload_confluence_v2.py` |
| > 500KB | Split Pages | Split into parent + child pages |

## Fallback Workflow

### 1. Prepare HTML Content

Write your content to an HTML file first. If starting from markdown:

```bash
# Convert markdown to HTML
npx marked input.md -o output.html

# Post-processing requirements:
# - Remove <h1> tags (title is handled by API)
# - Ensure <hr/> and <img/> tags are self-closed
# - Remove BOM characters
```

### 2. Discover PAT Token

Use the utility script to find your Personal Access Token:

```bash
python scripts/confluence_api.py discover-pat
```

### 3. Choose the Right Script

#### Option A: Basic Content (Text/HTML only)
Use `scripts/confluence_api.py` for standard page updates.

**Create New Page:**
```bash
python scripts/confluence_api.py create \
  --space HTSC \
  --title "My Large Page" \
  --file output.html \
  --base-url https://confluence.example.com
```

**Update Existing Page:**
```bash
python scripts/confluence_api.py update \
  --page-id 12345678 \
  --version 0 \
  --file output.html \
  --base-url https://confluence.example.com
```
*Note: version `0` auto-increments from the current version.*

#### Option B: Enhanced Content (Images/Attachments)
Use `scripts/upload_confluence_v2.py` if you need to upload local images referenced in your HTML.

```bash
python scripts/upload_confluence_v2.py \
  --page-id 12345678 \
  --html-file output.html \
  --base-url https://confluence.example.com
```

### 4. Verify and Clean Up

1. Check the Confluence page in your browser.
2. Verify all images/formatting rendered correctly.
3. Delete temporary HTML files: `rm output.html`.

## Error Handling

| HTTP Status | Meaning | Action |
|-------------|---------|--------|
| 401 | Unauthorized | PAT expired or invalid; check `.opencode/.mcp.json` |
| 403 | Forbidden | Check space permissions for your user |
| 404 | Not Found | Verify Page ID or Space Key |
| 409 | Conflict | Version mismatch; fetch current version with `get` command |
| 413 | Payload Too Large | Split content into multiple sub-pages |

## Safety Reminders

- Always run `python scripts/confluence_api.py get --page-id <ID>` before updating to check the current version and author.
- Confirm with the user before overwriting a page last edited by someone else.
- Never use these scripts for mass deletion; use MCP tools for single-item removal with confirmation.
