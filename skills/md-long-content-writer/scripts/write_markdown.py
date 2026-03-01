#!/usr/bin/env python3
"""
Reliable large Markdown file writer with append/overwrite modes.

Handles UTF-8 content safely on all platforms (Windows, macOS, Linux).
Designed as a fallback when AI agent tool calls fail for large content.

Usage:
    # Write content from a temp file (RECOMMENDED for large content)
    python write_markdown.py output.md --content-file content.txt

    # Append content from a temp file
    python write_markdown.py output.md --content-file content.txt --append

    # Write content from stdin
    echo "# Hello" | python write_markdown.py output.md --stdin

    # Append content from stdin
    echo "## New Section" | python write_markdown.py output.md --stdin --append

    # Write inline content (small content only)
    python write_markdown.py output.md --inline "# Title\n\nParagraph here"

    # Dry run (show what would happen)
    python write_markdown.py output.md --content-file content.txt --dry-run

    # Verify file after writing
    python write_markdown.py output.md --verify
"""

import argparse
import sys
import os
from pathlib import Path

# Fix Windows console encoding for Unicode output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def count_lines(filepath: Path) -> int:
    """Count lines in a file."""
    if not filepath.exists():
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def read_content_source(args) -> str:
    """Read content from the specified source."""
    if args.content_file:
        content_path = Path(args.content_file)
        if not content_path.exists():
            print(
                f"ERROR: Content file not found: {args.content_file}", file=sys.stderr
            )
            sys.exit(1)
        with open(content_path, "r", encoding="utf-8") as f:
            return f.read()
    elif args.stdin:
        if sys.stdin.isatty():
            print("ERROR: --stdin specified but no input piped", file=sys.stderr)
            sys.exit(1)
        # Force UTF-8 on Windows
        if sys.platform == "win32":
            import io

            sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")
        return sys.stdin.read()
    elif args.inline:
        # Unescape \n in inline content
        return args.inline.replace("\\n", "\n")
    else:
        print(
            "ERROR: Must specify --content-file, --stdin, or --inline", file=sys.stderr
        )
        sys.exit(1)


def verify_file(filepath: Path) -> None:
    """Verify file exists, is readable, and report stats."""
    if not filepath.exists():
        print(f"VERIFY FAILED: File does not exist: {filepath}")
        sys.exit(1)

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError as e:
        print(f"VERIFY FAILED: Encoding error: {e}")
        sys.exit(1)

    lines = content.split("\n")
    line_count = len(lines)
    char_count = len(content)
    size_kb = filepath.stat().st_size / 1024

    # Extract headings for structure overview
    headings = [l for l in lines if l.startswith("#")]

    print(f"VERIFY OK: {filepath}")
    print(f"  Lines: {line_count}")
    print(f"  Characters: {char_count}")
    print(f"  Size: {size_kb:.1f} KB")
    print(f"  Encoding: UTF-8")
    if headings:
        print(f"  Headings ({len(headings)}):")
        for h in headings[:15]:  # Show first 15 headings
            print(f"    {h}")
        if len(headings) > 15:
            print(f"    ... and {len(headings) - 15} more")


def main():
    parser = argparse.ArgumentParser(
        description="Reliable large Markdown file writer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("filepath", help="Target Markdown file path")
    parser.add_argument("--content-file", help="Read content from this file")
    parser.add_argument("--stdin", action="store_true", help="Read content from stdin")
    parser.add_argument("--inline", help="Inline content string (small content only)")
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append to existing file instead of overwriting",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would happen without writing"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify file after writing (or just verify existing)",
    )
    parser.add_argument(
        "--ensure-newline",
        action="store_true",
        default=True,
        help="Ensure file ends with newline (default: true)",
    )

    args = parser.parse_args()
    filepath = Path(args.filepath)

    # Verify-only mode
    if args.verify and not (args.content_file or args.stdin or args.inline):
        verify_file(filepath)
        return

    # Read content
    content = read_content_source(args)

    if not content.strip():
        print("WARNING: Content is empty or whitespace-only", file=sys.stderr)

    # Ensure trailing newline
    if args.ensure_newline and content and not content.endswith("\n"):
        content += "\n"

    # Dry run
    if args.dry_run:
        mode = "APPEND" if args.append else "WRITE"
        content_lines = content.count("\n")
        existing_lines = count_lines(filepath) if filepath.exists() else 0
        print(f"DRY RUN: {mode} to {filepath}")
        print(f"  Content: {content_lines} lines, {len(content)} chars")
        if args.append and filepath.exists():
            print(f"  Existing: {existing_lines} lines")
            print(f"  Result: ~{existing_lines + content_lines} lines")
        print(f"  First 3 lines:")
        for line in content.split("\n")[:3]:
            print(f"    | {line}")
        return

    # Ensure parent directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Write or append
    mode = "a" if args.append else "w"
    existing_lines = count_lines(filepath) if args.append and filepath.exists() else 0

    # If appending, ensure existing file ends with newline
    if args.append and filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            existing = f.read()
            if existing and not existing.endswith("\n"):
                content = "\n" + content

    with open(filepath, mode, encoding="utf-8", newline="") as f:
        f.write(content)

    new_total = count_lines(filepath)
    action = "Appended to" if args.append else "Wrote"
    print(f"OK: {action} {filepath}")
    print(f"  Total lines: {new_total}")
    if args.append:
        print(f"  Added: ~{new_total - existing_lines} lines")
    print(f"  Size: {filepath.stat().st_size / 1024:.1f} KB")

    # Auto-verify if requested
    if args.verify:
        print()
        verify_file(filepath)


if __name__ == "__main__":
    main()
