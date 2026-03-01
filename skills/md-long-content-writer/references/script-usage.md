# write_markdown.py — Script Usage Guide

## Overview

Fallback script for writing large Markdown files when agent tool calls fail.
Cross-platform (Windows, macOS, Linux). No external dependencies.



## Installation

No installation needed. Uses Python 3.6+ standard library only.

## Usage Patterns

### Pattern 1: Content File (RECOMMENDED for large content)

Write content to a temp file first, then call script:

```bash
# Step 1: Agent writes content to temp file using edit/write tool
# (temp file is small enough for tool calls to succeed)

# Step 2: Script merges temp file into target
python scripts/write_markdown.py output.md --content-file temp_content.txt

# Step 3: Append more content
python scripts/write_markdown.py output.md --content-file section2.txt --append

# Step 4: Clean up temp file
rm temp_content.txt section2.txt
```

### Pattern 2: Stdin Pipe

```bash
# Pipe content from another command
cat section.md | python scripts/write_markdown.py output.md --stdin --append
```

### Pattern 3: Inline (small content only)

```bash
# Quick header or small section
python scripts/write_markdown.py output.md --inline "# Title\n\nFirst paragraph."
```

### Pattern 4: Verify

```bash
# Check file integrity after writing
python scripts/write_markdown.py output.md --verify

# Output:
# VERIFY OK: output.md
#   Lines: 425
#   Characters: 18234
#   Size: 17.8 KB
#   Encoding: UTF-8
#   Headings (11):
#     # Title
#     ## Section 1
#     ...
```

### Pattern 5: Dry Run

```bash
# Preview without writing
python scripts/write_markdown.py output.md --content-file content.txt --dry-run
```

## Arguments Reference

| Argument | Required | Description |
|----------|----------|-------------|
| `filepath` | Yes | Target file path |
| `--content-file FILE` | One of three | Read content from file |
| `--stdin` | One of three | Read content from stdin |
| `--inline TEXT` | One of three | Inline content string |
| `--append` | No | Append instead of overwrite |
| `--dry-run` | No | Preview without writing |
| `--verify` | No | Verify file after write |
| `--ensure-newline` | No | Ensure trailing newline (default: true) |

## Chunked Writing Workflow

For very large files (500+ lines), combine script with chunking:

```bash
# Chunk 1: Header + sections 1-3
python scripts/write_markdown.py article.md --content-file chunk1.txt

# Chunk 2: Sections 4-6
python scripts/write_markdown.py article.md --content-file chunk2.txt --append

# Chunk 3: Sections 7-9 + references
python scripts/write_markdown.py article.md --content-file chunk3.txt --append

# Verify final result
python scripts/write_markdown.py article.md --verify
```

## Error Codes

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | Error (file not found, encoding error, missing input) |

## Platform Notes

- **Windows**: Handles UTF-8 stdin correctly (wraps sys.stdin with UTF-8 codec)
- **macOS/Linux**: UTF-8 is default, no special handling needed
- **Newlines**: Uses `newline=""` to preserve platform-native line endings
