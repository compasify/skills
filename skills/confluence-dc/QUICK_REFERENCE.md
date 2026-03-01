# Confluence Skill Quick Reference (Data Center)

## Common Tasks

### Search Confluence
```
"Find all pages about authentication in the DEV space"
"Search for API documentation created this month"
```

### Create Page
```
"Create a Confluence page from this Markdown in the DEV space"
"Create a page titled 'API Guide' under 'Documentation' parent"
```

### Create Blogpost
```
"Create a Confluence blogpost from this Markdown in the DEV space"
"Write a blogpost titled 'Release Notes v2.0' in DEV space"
```

### Update Page
```
"Update the 'Getting Started' page with this content"
"Find and update the authentication guide"
```

### Convert Formats
```
"Convert this Wiki Markup to Markdown"
"Convert this Markdown to Confluence format"
```

### Handle Diagrams
```
"Convert this Markdown with Mermaid diagrams to a Confluence page"
"Render these Mermaid diagrams and upload to Confluence"
```

## Format Conversion Cheat Sheet

| Element | Markdown | Wiki Markup |
|---------|----------|-------------|
| H1 | `# Heading` | `h1. Heading` |
| Bold | `**text**` | `*text*` |
| Italic | `*text*` | `_text*` |
| Code | `` `code` `` | `{{code}}` |
| Link | `[text](url)` | `[text|url]` |
| Image | `![alt](url)` | `!url!` |
| Bullet | `- item` | `* item` |
| Number | `1. item` | `# item` |

## CQL Search Quick Examples

```cql
# Find in space
space = "DEV"

# Find by title
title ~ "authentication"

# Find by content
text ~ "REST API"

# Created this month
created >= startOfMonth()

# My pages
creator = currentUser()

# With labels
label IN ("api", "docs")

# Complex
space = "DEV" AND
type = page AND
created >= startOfYear() AND
label = "api"
```

## Python Scripts

```bash
# Convert Markdown -> Wiki
python scripts/convert_markdown_to_wiki.py input.md output.wiki

# Render Mermaid diagram
python scripts/render_mermaid.py diagram.mmd output.png

# Upload as page (default)
python scripts/upload_confluence_v2.py document.md --id PAGE_ID

# Upload as blogpost
python scripts/upload_confluence_v2.py document.md --space ARCP --type blogpost
```

## Available MCP Tools

- `confluence_getContent` - Get content by ID
- `confluence_searchContent` - Search with CQL
- `confluence_createContent` - Create page/blogpost
- `confluence_updateContent` - Update content (requires version number)
- `confluence_searchSpace` - Search spaces
- `confluence_deletePage` - Delete page
- `confluence_getPageChildren` - Get child pages
- `confluence_getLabels` - Get labels
- `confluence_addLabel` - Add label
- `confluence_getComments` - Get comments (read-only)

## File Locations

- **Main documentation**: `~/.claude/skills/confluence-dc/SKILL.md`
- **Wiki Markup guide**: `~/.claude/skills/confluence-dc/references/wiki_markup_guide.md`
- **Conversion guide**: `~/.claude/skills/confluence-dc/references/conversion_guide.md`
- **Scripts**: `~/.claude/skills/confluence-dc/scripts/`
- **Examples**: `~/.claude/skills/confluence-dc/examples/`

## Common Workflows

### 1. Create from Markdown
1. Write Markdown with Mermaid diagrams
2. Claude extracts and renders diagrams
3. Converts Markdown to Wiki Markup
4. Uploads diagrams as attachments
5. Creates Confluence page

### 2. Search and Update
1. Search for page with CQL
2. Get current content
3. Make changes
4. Update page with version comment (increment version number)

## Tips

- Use labels consistently for organization
- Keep diagram source files (.mmd) in Git
- Review conversions for edge cases
- Use parent pages for proper hierarchy
