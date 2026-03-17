# Long Markdown Writer API Skill

Write large Markdown files reliably via a local HTTP API server. When AI agent tool calls fail on large content, start the server, POST content to it, then stop.

## Problem

AI coding agents frequently fail when writing large Markdown files through their built-in tools — JSON parse errors, payload limits, Unicode corruption. This skill provides an HTTP API bypass: content goes through a local server that writes directly to disk.

## How It Works

1. **Start** the Python HTTP server (zero dependencies, stdlib only)
2. **POST** content to `http://localhost:9111/write` with `{path, content}`
3. **Stop** the server when done

## Installation

### skills.sh (Recommended)

```bash
npx skills add compasify/skills --skill long-md-writer-api
```

### Manual Copy

```bash
# OpenCode (project-level)
cp -r skills/long-md-writer-api .opencode/skills/

# Claude Code
cp -r skills/long-md-writer-api ~/.claude/skills/

# Cursor
cp -r skills/long-md-writer-api ~/.cursor/skills/
```

## Requirements

- Python 3.6+ (stdlib only, no pip install needed)

## File Structure

```
long-md-writer-api/
├── SKILL.md                       # Core instructions for the AI agent
├── README.md                      # This file
└── scripts/
    └── md_writer_server.py        # HTTP server (Python stdlib)
```

## Quick Start

```bash
# Start server
python scripts/md_writer_server.py &

# Write a file
curl -X POST http://localhost:9111/write \
  -H "Content-Type: application/json" \
  -d '{"path": "doc.md", "content": "# Hello World\n\nThis works!"}'

# Append to file
curl -X POST http://localhost:9111/append \
  -H "Content-Type: application/json" \
  -d '{"path": "doc.md", "content": "\n## Section 2\n\nMore content."}'

# Stop server
curl -X POST http://localhost:9111/stop
```

## API Endpoints

| Endpoint | Method | Body | Description |
|----------|--------|------|-------------|
| `/write` | POST | `{"path": "...", "content": "..."}` | Write/overwrite file |
| `/append` | POST | `{"path": "...", "content": "..."}` | Append to file |
| `/health` | GET | — | Health check |
| `/stop` | POST | — | Shut down server |

## License

MIT License — see repository [LICENSE](../../LICENSE) for details.

## Author

**Compasify** — [github.com/compasify](https://github.com/compasify)
