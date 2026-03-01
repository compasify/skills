# Long Markdown Content Writer Skill

A skill that teaches AI agents how to write large Markdown files (100+ lines) reliably by chunking content and falling back to scripts when tool calls fail.

## Problem

AI coding agents (OpenCode, Claude Code, Cursor, etc.) frequently fail when writing large Markdown files:

- **`write` tool**: JSON parse errors on large content with Unicode
- **`edit` tool**: Works well in chunks but stale line hashes cause failures
- **Bash heredocs**: Corrupt Unicode/Vietnamese characters on Windows
- **Single large writes**: Tool call timeouts or payload size limits

This skill provides a systematic fallback strategy and a Python script for guaranteed reliable writes.

## How It Works

The skill teaches a 3-level fallback chain:

1. **`edit` tool** (chunked append, ~80-100 lines per call) — fastest, most integrated
2. **`write` tool** (full file rewrite) — when edit hashes get stale
3. **Python script** (`write_markdown.py`) — guaranteed reliability for any size

## Installation

### skills.sh (Recommended)

```bash
npx skills add compasify/skills --skill md-long-content-writer
```

### Manual Copy

```bash
# OpenCode (project-level)
cp -r skills/md-long-content-writer .opencode/skills/

# OpenCode (user-level, all projects)
cp -r skills/md-long-content-writer ~/.config/opencode/skills/

# Claude Code
cp -r skills/md-long-content-writer ~/.claude/skills/

# Cursor
cp -r skills/md-long-content-writer ~/.cursor/skills/
```

## Requirements

- Python 3.6+ (for fallback script)
- No external dependencies

## File Structure

```
md-long-content-writer/
├── SKILL.md                    # Core instructions for the AI agent
├── README.md                   # This file
├── scripts/
│   └── write_markdown.py       # Fallback script for reliable large writes
└── references/
    └── script-usage.md         # Detailed script documentation
```

## Script Quick Start

```bash
# Write content from a file
python scripts/write_markdown.py output.md --content-file content.txt

# Append more content
python scripts/write_markdown.py output.md --content-file section2.txt --append

# Verify result
python scripts/write_markdown.py output.md --verify
```

## When This Skill Activates

The skill auto-activates when the agent encounters:
- Writing articles, blog posts, or long documentation
- Tool call failures during large content writes
- Requests to "write long markdown" or "create document"
- Content exceeding 100+ lines

## License

MIT License — see repository [LICENSE](../../LICENSE) for details.

## Author

**Compasify** — [github.com/compasify](https://github.com/compasify)
