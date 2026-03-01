#!/usr/bin/env python3
"""
Lightweight Confluence page downloader.

Downloads a single Confluence Data Center page by pageId and converts to Markdown.
Uses only Python stdlib + html2text (pip install html2text).

Credential discovery is delegated to confluence_auth.get_confluence_credentials().

Usage:
    python download_long_page.py PAGE_ID [--output-dir DIR]

Examples:
    python download_long_page.py 47486114
    python download_long_page.py 47486114 --output-dir ./docs
"""

from __future__ import annotations

import argparse
import json
import re
import ssl
import sys
import urllib.request
from pathlib import Path

# ---------------------------------------------------------------------------
# Import shared credential discovery
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

try:
    from confluence_auth import get_confluence_credentials
except ImportError:
    print(
        "ERROR: confluence_auth.py not found in the same directory.\n"
        "Make sure this script lives alongside confluence_auth.py.",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    import html2text
except ImportError:
    print(
        "ERROR: html2text is not installed.\nInstall it with:  pip install html2text",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Confluence REST API fetch
# ---------------------------------------------------------------------------


def _fetch_page(base_url: str, token: str, page_id: str) -> dict:
    """Fetch page JSON from Confluence REST API."""
    url = f"{base_url}/rest/api/content/{page_id}?expand=body.storage,version,space"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")

    # Allow self-signed certs (common in enterprise DC)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        print(f"HTTP {exc.code}: {exc.reason}\n{body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as exc:
        print(f"Connection error: {exc.reason}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# HTML → Markdown conversion + post-processing
# ---------------------------------------------------------------------------


def _html_to_markdown(html_content: str) -> str:
    """Convert Confluence storage-format HTML to clean Markdown."""
    h = html2text.HTML2Text()
    h.body_width = 0  # No line wrapping
    h.unicode_snob = True
    h.protect_links = True
    h.wrap_links = False
    h.wrap_list_items = False
    h.single_line_break = False

    md = h.handle(html_content)

    # Post-process common html2text artifacts from Confluence HTML
    # Fix escaped heading numbers:  "## 1\. Title" → "## 1. Title"
    md = re.sub(r"^(#{1,6}\s+\d+)\\(\.\s)", r"\1\2", md, flags=re.MULTILINE)

    # Fix false horizontal rules:  "* * *" → "---"
    md = re.sub(r"^\*\s*\*\s*\*\s*$", "---", md, flags=re.MULTILINE)

    # Fix angle-bracket links:  [text](<url>) → [text](url)
    md = re.sub(r"\[([^\]]+)\]\(<([^>]+)>\)", r"[\1](\2)", md)

    # Collapse 3+ blank lines → 2
    md = re.sub(r"\n{3,}", "\n\n", md)

    return md.strip() + "\n"


def _slugify(title: str) -> str:
    """Convert page title to a filesystem-safe filename."""
    slug = re.sub(r"[^\w\s-]", "", title).strip()
    slug = re.sub(r"[\s_]+", "_", slug)
    return slug


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Download a Confluence page to Markdown (lightweight)."
    )
    parser.add_argument("page_id", help="Confluence page ID")
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--output-file",
        default=None,
        help="Output filename (default: auto-generated from page title)",
    )
    args = parser.parse_args()

    # --- Credentials ---
    try:
        creds = get_confluence_credentials()
    except ValueError as exc:
        print(f"Credential error: {exc}", file=sys.stderr)
        sys.exit(1)

    base_url = creds["url"]
    token = creds["token"]

    # --- Fetch page ---
    print(f"Fetching page {args.page_id} from {base_url} ...")
    data = _fetch_page(base_url, token, args.page_id)

    title = data.get("title", f"page_{args.page_id}")
    space_key = data.get("space", {}).get("key", "UNKNOWN")
    version = data.get("version", {}).get("number", 1)
    html_body = data.get("body", {}).get("storage", {}).get("value", "")

    if not html_body:
        print("WARNING: Page body is empty.", file=sys.stderr)

    # --- Convert ---
    md_content = _html_to_markdown(html_body)

    # --- Add metadata header ---
    header = (
        f"---\n"
        f'title: "{title}"\n'
        f"confluence_page_id: {args.page_id}\n"
        f"space_key: {space_key}\n"
        f"version: {version}\n"
        f"source: Confluence Data Center\n"
        f"---\n\n"
        f"# {title}\n\n"
    )
    full_content = header + md_content

    # --- Write file ---
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.output_file:
        filename = args.output_file
    else:
        filename = _slugify(title) + ".md"

    output_path = output_dir / filename
    output_path.write_text(full_content, encoding="utf-8")

    print(f"✓ Saved: {output_path}  ({len(full_content):,} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
