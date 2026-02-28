#!/usr/bin/env python3
"""
Confluence Direct API Client - Fallback for large content that exceeds MCP tool limits.

Usage:
    python confluence_api.py discover-pat              # Find PAT from MCP configs
    python confluence_api.py create --space KEY --title "Title" --type blogpost --file content.html
    python confluence_api.py update --page-id ID --version N --file content.html [--title "New Title"]
    python confluence_api.py get --page-id ID           # Get page info (version, author, title)

Environment:
    CONFLUENCE_BASE_URL - Confluence base URL (default: from MCP config or must be provided)
    CONFLUENCE_PAT      - Personal Access Token (auto-discovered from MCP configs if not set)
"""

import argparse
import io
import json
import os
import re
import ssl
import sys
import urllib.request
import urllib.error
from pathlib import Path

# Fix Windows console encoding for Unicode (Vietnamese, emojis)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def get_platform_paths():
    """Return MCP config paths for all supported AI IDEs."""
    home = Path(os.environ.get("USERPROFILE", os.environ.get("HOME", "")))
    appdata = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
    cwd = Path.cwd()

    return [
        # OpenCode project-level
        cwd / ".opencode" / ".mcp.json",
        cwd / ".opencode" / "mcp.json",
        # OpenCode user-level
        home / ".opencode" / ".mcp.json",
        home / ".config" / "opencode" / "mcp.json",
        # Claude Desktop
        appdata / "Claude" / "claude_desktop_config.json",
        # Claude Code (claude.ai/code)
        home / ".claude" / "mcp.json",
        home / ".claude.json",
        # Cursor
        home / ".cursor" / "mcp.json",
        cwd / ".cursor" / "mcp.json",
        # Antigravity
        appdata / "Antigravity" / "mcp.json",
        appdata / "Antigravity" / "settings" / "mcp.json",
        # Windsurf (Codeium)
        home / ".windsurf" / "mcp.json",
        home / ".codeium" / "windsurf" / "mcp_config.json",
        # VS Code + Cline/Roo
        appdata
        / "Code"
        / "User"
        / "globalStorage"
        / "saoudrizwan.claude-dev"
        / "settings"
        / "cline_mcp_settings.json",
        appdata
        / "Code"
        / "User"
        / "globalStorage"
        / "rooveterinaryinc.roo-cline"
        / "settings"
        / "cline_mcp_settings.json",
        # Generic
        home / ".mcp.json",
    ]


def extract_confluence_config(config_data, config_path):
    """Extract Confluence PAT and base URL from an MCP config JSON."""
    pat = None
    base_url = None

    if isinstance(config_data, str):
        try:
            config_data = json.loads(config_data)
        except json.JSONDecodeError:
            return None, None

    # Navigate to mcpServers
    servers = config_data.get(
        "mcpServers", config_data.get("mcp", {}).get("servers", {})
    )
    if not servers:
        # Try top-level if it looks like a servers dict
        if any("command" in v for v in config_data.values() if isinstance(v, dict)):
            servers = config_data

    for name, server in servers.items():
        if not isinstance(server, dict):
            continue

        # Check if this is a Confluence-related server
        name_lower = name.lower()
        args_str = " ".join(str(a) for a in server.get("args", []))
        cmd = str(server.get("command", ""))

        is_confluence = any(
            kw in name_lower
            for kw in ["confluence", "atlassian-confluence", "atlassian-dc"]
        )
        is_confluence = is_confluence or any(
            kw in args_str.lower()
            for kw in ["confluence", "@compasify/confluence-dc"]
        )

        if not is_confluence:
            continue

        # Extract PAT from env
        env = server.get("env", {})
        for key, value in env.items():
            key_upper = key.upper()
            if any(
                k in key_upper
                for k in ["PAT", "TOKEN", "PERSONAL_ACCESS", "BEARER", "AUTH"]
            ):
                if value and not value.startswith("${"):
                    pat = value
                    break

        # Extract base URL from env or args
        for key, value in env.items():
            key_upper = key.upper()
            if any(
                k in key_upper for k in ["BASE_URL", "HOST", "CONFLUENCE_URL", "URL"]
            ):
                if value and not value.startswith("${"):
                    base_url = value
                    break

        # Try extracting URL from args
        if not base_url:
            for arg in server.get("args", []):
                if isinstance(arg, str) and (
                    "confluence" in arg.lower() or "atlassian" in arg.lower()
                ):
                    if arg.startswith("http"):
                        base_url = arg

        if pat:
            break

    return pat, base_url


def discover_pat():
    """Search all known MCP config locations for Confluence PAT."""
    # 1. Check environment variable first
    env_pat = os.environ.get("CONFLUENCE_PAT")
    if env_pat:
        print(
            json.dumps(
                {
                    "found": True,
                    "source": "environment variable CONFLUENCE_PAT",
                    "pat_preview": f"{env_pat[:8]}...{env_pat[-4:]}",
                    "pat": env_pat,
                    "base_url": os.environ.get("CONFLUENCE_BASE_URL"),
                }
            )
        )
        return env_pat, os.environ.get("CONFLUENCE_BASE_URL")

    # 2. Search MCP config files
    paths = get_platform_paths()
    for config_path in paths:
        try:
            if config_path.exists():
                content = config_path.read_text(encoding="utf-8")
                pat, base_url = extract_confluence_config(content, str(config_path))
                if pat:
                    print(
                        json.dumps(
                            {
                                "found": True,
                                "source": str(config_path),
                                "pat_preview": f"{pat[:8]}...{pat[-4:]}",
                                "pat": pat,
                                "base_url": base_url,
                            }
                        )
                    )
                    return pat, base_url
        except (PermissionError, OSError) as e:
            continue

    # 3. Not found
    searched = [str(p) for p in paths if p.exists()]
    not_found = [str(p) for p in paths if not p.exists()]
    print(
        json.dumps(
            {
                "found": False,
                "searched_existing": searched,
                "not_found_paths": not_found[:5],
                "hint": "Set CONFLUENCE_PAT environment variable or provide PAT manually",
            }
        )
    )
    return None, None


def make_request(method, url, headers, body=None):
    """Make HTTPS request with SSL handling for self-signed certs."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    data = body.encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            response_data = resp.read().decode("utf-8")
            return resp.status, response_data
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        return e.code, error_body


def get_page_info(base_url, pat, page_id):
    """Get page info including version, author, title."""
    url = f"{base_url}/rest/api/content/{page_id}?expand=version,history.createdBy"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/json",
    }
    status, data = make_request("GET", url, headers)
    if status == 200:
        result = json.loads(data)
        info = {
            "id": result["id"],
            "title": result["title"],
            "type": result["type"],
            "version": result["version"]["number"],
            "author": result.get("history", {})
            .get("createdBy", {})
            .get("displayName", "unknown"),
            "author_username": result.get("history", {})
            .get("createdBy", {})
            .get("username", "unknown"),
            "url": f"{base_url}/pages/viewpage.action?pageId={page_id}",
        }
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return info
    else:
        print(
            json.dumps(
                {"error": f"HTTP {status}", "details": data[:500]}, ensure_ascii=False
            )
        )
        sys.exit(1)


def create_content(
    base_url, pat, space_key, title, content_type, html_file, parent_id=None
):
    """Create new page or blogpost."""
    html_content = Path(html_file).read_text(encoding="utf-8").lstrip("\ufeff")

    body = {
        "type": content_type,
        "title": title,
        "space": {"key": space_key},
        "body": {"storage": {"value": html_content, "representation": "storage"}},
    }
    if parent_id:
        body["ancestors"] = [{"id": parent_id}]

    url = f"{base_url}/rest/api/content"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    status, data = make_request(
        "POST", url, headers, json.dumps(body, ensure_ascii=False)
    )
    if status in (200, 201):
        result = json.loads(data)
        print(
            json.dumps(
                {
                    "success": True,
                    "id": result["id"],
                    "title": result["title"],
                    "version": result["version"]["number"],
                    "url": f"{base_url}/pages/viewpage.action?pageId={result['id']}",
                    "content_length": len(html_content),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(
            json.dumps(
                {"success": False, "status": status, "error": data[:1000]},
                ensure_ascii=False,
            )
        )
        sys.exit(1)


def update_content(base_url, pat, page_id, version, html_file, title=None):
    """Update existing page or blogpost."""
    html_content = Path(html_file).read_text(encoding="utf-8").lstrip("\ufeff")

    # Get current page info for type and title
    info_url = f"{base_url}/rest/api/content/{page_id}?expand=version"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    status, data = make_request("GET", info_url, headers)
    if status != 200:
        print(
            json.dumps({"success": False, "error": f"Cannot fetch page: HTTP {status}"})
        )
        sys.exit(1)

    current = json.loads(data)
    current_version = current["version"]["number"]

    if version <= current_version:
        version = current_version + 1

    body = {
        "version": {"number": version},
        "title": title or current["title"],
        "type": current["type"],
        "body": {"storage": {"value": html_content, "representation": "storage"}},
    }

    url = f"{base_url}/rest/api/content/{page_id}"
    status, data = make_request(
        "PUT", url, headers, json.dumps(body, ensure_ascii=False)
    )
    if status == 200:
        result = json.loads(data)
        print(
            json.dumps(
                {
                    "success": True,
                    "id": result["id"],
                    "title": result["title"],
                    "version": result["version"]["number"],
                    "url": f"{base_url}/pages/viewpage.action?pageId={result['id']}",
                    "content_length": len(html_content),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(
            json.dumps(
                {"success": False, "status": status, "error": data[:1000]},
                ensure_ascii=False,
            )
        )
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Confluence Direct API Client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # discover-pat
    subparsers.add_parser("discover-pat", help="Find PAT from MCP configs")

    # get
    get_parser = subparsers.add_parser("get", help="Get page info")
    get_parser.add_argument("--page-id", required=True)
    get_parser.add_argument("--base-url", default=os.environ.get("CONFLUENCE_BASE_URL"))
    get_parser.add_argument("--pat", default=os.environ.get("CONFLUENCE_PAT"))

    # create
    create_parser = subparsers.add_parser("create", help="Create content")
    create_parser.add_argument("--space", required=True, help="Space key")
    create_parser.add_argument("--title", required=True)
    create_parser.add_argument("--type", default="page", choices=["page", "blogpost"])
    create_parser.add_argument("--file", required=True, help="HTML file path")
    create_parser.add_argument("--parent-id", default=None)
    create_parser.add_argument(
        "--base-url", default=os.environ.get("CONFLUENCE_BASE_URL")
    )
    create_parser.add_argument("--pat", default=os.environ.get("CONFLUENCE_PAT"))

    # update
    update_parser = subparsers.add_parser("update", help="Update content")
    update_parser.add_argument("--page-id", required=True)
    update_parser.add_argument(
        "--version", type=int, default=0, help="Version number (auto-increments if 0)"
    )
    update_parser.add_argument("--file", required=True, help="HTML file path")
    update_parser.add_argument("--title", default=None)
    update_parser.add_argument(
        "--base-url", default=os.environ.get("CONFLUENCE_BASE_URL")
    )
    update_parser.add_argument("--pat", default=os.environ.get("CONFLUENCE_PAT"))

    args = parser.parse_args()

    if args.command == "discover-pat":
        pat, base_url = discover_pat()
        sys.exit(0 if pat else 1)

    # For other commands, resolve PAT and base_url
    pat = getattr(args, "pat", None)
    base_url = getattr(args, "base_url", None)

    if not pat:
        discovered_pat, discovered_url = discover_pat()
        pat = discovered_pat
        if not base_url:
            base_url = discovered_url

    if not pat:
        print(
            json.dumps({"error": "No PAT found. Set CONFLUENCE_PAT or provide --pat"})
        )
        sys.exit(1)

    if not base_url:
        print(
            json.dumps(
                {"error": "No base URL. Set CONFLUENCE_BASE_URL or provide --base-url"}
            )
        )
        sys.exit(1)

    # Normalize base URL
    base_url = base_url.rstrip("/")
    if not base_url.startswith("http"):
        base_url = f"https://{base_url}"

    if args.command == "get":
        get_page_info(base_url, pat, args.page_id)
    elif args.command == "create":
        create_content(
            base_url, pat, args.space, args.title, args.type, args.file, args.parent_id
        )
    elif args.command == "update":
        update_content(base_url, pat, args.page_id, args.version, args.file, args.title)


if __name__ == "__main__":
    main()
