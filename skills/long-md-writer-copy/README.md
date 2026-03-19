# Long Markdown Writer — Copy-Paste Fallback

When all automated write methods fail (tool calls, chunking, API server, scripts), this skill instructs the AI agent to create an empty target file and print the full content in a `txt` code block for manual copy-paste.

## Problem

Sometimes every automated write method fails — tool payload limits, encoding issues, no Python available, no server. The content exists in the agent's context but can't reach the disk. This skill provides the simplest possible fallback: show the content, let the user copy it.

## How It Works

1. **Create** an empty file at the target path
2. **Print** the full content inside a `txt` code block (no rendering, clean copy)
3. **Instruct** the user to copy-paste into the file

## Installation

### skills.sh (Recommended)

```bash
npx skills add compasify/skills --skill long-md-writer-copy
```

### Manual Copy

```bash
# OpenCode
cp -r skills/long-md-writer-copy .opencode/skills/

# Claude Code
cp -r skills/long-md-writer-copy ~/.claude/skills/

# Cursor
cp -r skills/long-md-writer-copy ~/.cursor/skills/
```

## Requirements

None. This skill uses no scripts or dependencies.

## File Structure

```
long-md-writer-copy/
├── SKILL.md     # Core instructions for the AI agent
└── README.md    # This file
```

## License

MIT License — see repository [LICENSE](../../LICENSE) for details.

## Author

**Compasify** — [github.com/compasify](https://github.com/compasify)
