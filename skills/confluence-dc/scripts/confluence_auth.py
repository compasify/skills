"""
Confluence Data Center Authentication and Credential Discovery

Provides shared credential discovery for Confluence DC using PAT (Personal Access Token).
Discovers PAT and base URL from MCP config files across all AI IDEs.

Search priority:
1. Environment variables (CONFLUENCE_PAT / CONFLUENCE_API_TOKEN + CONFLUENCE_BASE_URL / CONFLUENCE_HOST)
2. OpenCode project-level MCP configs
3. OpenCode user-level MCP configs
4. Claude Desktop config
5. Claude Code config
6. Cursor MCP configs
7. Antigravity MCP configs
8. Windsurf / Codeium MCP configs
9. VS Code + Cline/Roo extensions
10. Generic ~/.mcp.json
11. .env file fallback (walk up directories)

Usage:
    from confluence_auth import get_confluence_client

    confluence = get_confluence_client()
    # Or with custom env file:
    confluence = get_confluence_client(env_file="/path/to/.env")
"""

import io
import os
import json
import re
import sys
from pathlib import Path
from typing import Optional, Dict, Tuple

# Fix Windows console encoding for Unicode (Vietnamese, emojis)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


ENV_FILE_VARIANTS = [".env", ".env.confluence", ".env.jira", ".env.atlassian"]

# Keys that indicate a PAT/token value in MCP env config
_TOKEN_KEYS = ["PAT", "TOKEN", "PERSONAL_ACCESS", "BEARER", "AUTH"]

# Keys that indicate a Confluence base URL in MCP env config
_URL_KEYS = ["BASE_URL", "HOST", "CONFLUENCE_URL", "URL", "API_BASE_PATH"]

# Keywords to identify Confluence-related MCP servers
_CONFLUENCE_SERVER_NAMES = ["confluence", "compasify-confluence-dc", "atlassian-confluence", "atlassian-dc"]
_CONFLUENCE_ARG_KEYWORDS = ["confluence", "@compasify/confluence-dc"]


def _resolve_env_ref(value: str) -> Optional[str]:
    """Resolve ${VAR} environment variable references in config values."""
    if not value:
        return value
    if value.startswith("${") and value.endswith("}"):
        var_name = value[2:-1]
        return os.environ.get(var_name)

    # Also handle embedded ${VAR} references
    def _replace(m):
        return os.environ.get(m.group(1), "")

    resolved = re.sub(r"\$\{([^}]+)}", _replace, value)
    return resolved if resolved else None


def _get_mcp_config_paths() -> list:
    """Return MCP config paths for all supported AI IDEs, in priority order."""
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
        # Claude Code (claude.ai/code) — dot-prefixed config
        home / ".claude" / ".mcp.json",
        home / ".claude" / "mcp.json",
        home / ".claude.json",
        # Cursor
        cwd / ".cursor" / "mcp.json",
        home / ".cursor" / "mcp.json",
        # Antigravity
        appdata / "Antigravity" / "mcp.json",
        appdata / "Antigravity" / "settings" / "mcp.json",
        # Windsurf (Codeium)
        home / ".windsurf" / "mcp.json",
        home / ".codeium" / "windsurf" / "mcp_config.json",
        # VS Code + Cline/Roo extensions
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


def _extract_confluence_config(config_data) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract Confluence PAT and base URL from an MCP config dict/string.

    Returns:
        (pat, base_url) tuple, either or both may be None
    """
    if isinstance(config_data, str):
        try:
            config_data = json.loads(config_data)
        except json.JSONDecodeError:
            return None, None

    if not isinstance(config_data, dict):
        return None, None

    pat = None
    base_url = None

    # Navigate to mcpServers (support both flat and nested structures)
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

        is_confluence = any(kw in name_lower for kw in _CONFLUENCE_SERVER_NAMES)
        is_confluence = is_confluence or any(
            kw in args_str.lower() for kw in _CONFLUENCE_ARG_KEYWORDS
        )

        if not is_confluence:
            continue

        # Extract PAT from env section
        env = server.get("env", {})
        for key, value in env.items():
            key_upper = key.upper()
            if any(k in key_upper for k in _TOKEN_KEYS):
                resolved = _resolve_env_ref(value) if value else None
                if resolved:
                    pat = resolved
                    break

        # Extract base URL from env section
        for key, value in env.items():
            key_upper = key.upper()
            if any(k in key_upper for k in _URL_KEYS):
                resolved = _resolve_env_ref(value) if value else None
                if resolved:
                    base_url = resolved
                    break

        # Try extracting URL from args as fallback
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


def _discover_from_mcp_configs() -> Tuple[Optional[str], Optional[str]]:
    """
    Search all known MCP config locations for Confluence PAT and base URL.

    Returns:
        (pat, base_url) tuple
    """
    paths = _get_mcp_config_paths()
    for config_path in paths:
        try:
            if config_path.exists():
                content = config_path.read_text(encoding="utf-8")
                pat, base_url = _extract_confluence_config(content)
                if pat:
                    return pat, base_url
        except (PermissionError, OSError):
            continue
    return None, None


def _check_env_vars() -> Optional[Dict[str, str]]:
    """Check if required DC environment variables are set (PAT + URL)."""
    pat = os.getenv("CONFLUENCE_PAT") or os.getenv("CONFLUENCE_API_TOKEN")
    url = (
        os.getenv("CONFLUENCE_BASE_URL")
        or os.getenv("CONFLUENCE_HOST")
        or os.getenv("CONFLUENCE_URL")
    )

    if pat and url:
        return {"url": url, "token": pat}
    if pat:
        # PAT found but no URL — still return so caller can attempt MCP URL discovery
        return {"url": url, "token": pat}
    return None


def _find_env_file_in_directory(directory: Path) -> Optional[Path]:
    """Find first matching .env variant in a directory."""
    for env_variant in ENV_FILE_VARIANTS:
        env_path = directory / env_variant
        if env_path.exists() and env_path.is_file():
            return env_path
    return None


def _walk_up_for_env_file(start_dir: Optional[Path] = None) -> Optional[Path]:
    """Walk up directory tree to find .env file."""
    if start_dir is None:
        start_dir = Path.cwd()

    current = start_dir.resolve()
    root = Path(current.anchor)

    while current != root:
        env_file = _find_env_file_in_directory(current)
        if env_file:
            return env_file

        parent = current.parent
        if parent == current:
            break
        current = parent

    return None


def _load_env_and_check(env_path: Path) -> Optional[Dict[str, str]]:
    """Load a .env file and check for DC credentials."""
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path)
    except ImportError:
        # Fallback: manually parse KEY=VALUE lines
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value:
                        os.environ.setdefault(key, value)
        except (OSError, UnicodeDecodeError):
            return None
    return _check_env_vars()


def _normalize_url(url: Optional[str]) -> Optional[str]:
    """Normalize URL: ensure https:// prefix, strip trailing slash."""
    if not url:
        return None
    url = url.rstrip("/")
    if not url.startswith("http"):
        url = f"https://{url}"
    return url


def get_confluence_credentials(env_file: Optional[str] = None) -> Dict[str, str]:
    """
    Discover Confluence DC credentials using fallback chain.

    Args:
        env_file: Optional path to specific .env file (overrides discovery)

    Returns:
        Dict with 'url' and 'token' keys (DC PAT auth, no username)

    Raises:
        ValueError: If no valid credentials found

    Priority order:
        1. Explicit env_file parameter
        2. Environment variables (CONFLUENCE_PAT + CONFLUENCE_BASE_URL)
        3. MCP config files (all AI IDEs)
        4. .env files in current directory
        5. .env files in parent directories
        6. .env files in home directory
    """

    # Priority 1: Explicit env_file parameter
    if env_file:
        env_path = Path(env_file)
        if not env_path.exists():
            raise ValueError(f"Specified env file not found: {env_file}")

        creds = _load_env_and_check(env_path)
        if creds and creds.get("token"):
            creds["url"] = _normalize_url(creds.get("url"))
            if creds["url"]:
                return creds
        raise ValueError(
            f"Env file {env_file} does not contain required DC credentials "
            f"(CONFLUENCE_PAT/CONFLUENCE_API_TOKEN + CONFLUENCE_BASE_URL/CONFLUENCE_HOST)"
        )

    # Priority 2: Environment variables (already set)
    creds = _check_env_vars()
    if creds and creds.get("token") and creds.get("url"):
        creds["url"] = _normalize_url(creds["url"])
        return creds

    # Priority 3: MCP config files (all AI IDEs)
    mcp_pat, mcp_url = _discover_from_mcp_configs()
    if mcp_pat:
        # Merge: env vars may have partial info (e.g. URL but no PAT)
        url = _normalize_url(
            mcp_url
            or (creds.get("url") if creds else None)
            or os.getenv("CONFLUENCE_BASE_URL")
            or os.getenv("CONFLUENCE_HOST")
            or os.getenv("CONFLUENCE_URL")
        )
        if url:
            return {"url": url, "token": mcp_pat}

    # Priority 4: .env files in current directory
    env_file_path = _find_env_file_in_directory(Path.cwd())
    if env_file_path:
        dotenv_creds = _load_env_and_check(env_file_path)
        if dotenv_creds and dotenv_creds.get("token") and dotenv_creds.get("url"):
            dotenv_creds["url"] = _normalize_url(dotenv_creds["url"])
            return dotenv_creds

    # Priority 5: Walk up parent directories
    env_file_path = _walk_up_for_env_file()
    if env_file_path:
        dotenv_creds = _load_env_and_check(env_file_path)
        if dotenv_creds and dotenv_creds.get("token") and dotenv_creds.get("url"):
            dotenv_creds["url"] = _normalize_url(dotenv_creds["url"])
            return dotenv_creds

    # Priority 6: Home directory .env files
    for env_variant in ENV_FILE_VARIANTS:
        home_env = Path.home() / env_variant
        if home_env.exists():
            dotenv_creds = _load_env_and_check(home_env)
            if dotenv_creds and dotenv_creds.get("token") and dotenv_creds.get("url"):
                dotenv_creds["url"] = _normalize_url(dotenv_creds["url"])
                return dotenv_creds

    # No credentials found — give clear DC-specific error
    raise ValueError(
        "No Confluence Data Center credentials found.\n"
        "Set environment variables or configure MCP:\n"
        "  - CONFLUENCE_PAT (or CONFLUENCE_API_TOKEN) = your Personal Access Token\n"
        "  - CONFLUENCE_BASE_URL (or CONFLUENCE_HOST) = your Confluence DC base URL\n"
        "Or create a .env file with these variables.\n"
        "Or configure a Confluence MCP server in your AI IDE's mcp.json."
    )


def get_confluence_client(env_file: Optional[str] = None, **overrides):
    """
    Get authenticated Confluence Data Center client.

    Args:
        env_file: Optional path to .env file
        **overrides: Optional credential overrides (url, token)

    Returns:
        atlassian.Confluence client instance (DC mode, PAT auth)

    Raises:
        ValueError: If credentials not found
        ImportError: If atlassian-python-api not installed
    """
    try:
        from atlassian import Confluence
    except ImportError:
        raise ImportError(
            "atlassian-python-api not installed. "
            "Install with: pip install atlassian-python-api"
        )

    # Get credentials
    creds = get_confluence_credentials(env_file)

    # Apply overrides
    url = overrides.get("url", creds["url"])
    pat = overrides.get("token", creds["token"])

    # Normalize URL
    url = _normalize_url(url)

    # DC auth: token= parameter with cloud=False
    return Confluence(url=url, token=pat, cloud=False)


if __name__ == "__main__":
    """Test credential discovery for Confluence Data Center."""

    try:
        creds = get_confluence_credentials()
        print("Credentials found:")
        print(f"  URL:   {creds['url']}")
        token = creds["token"]
        preview = f"{token[:8]}...{token[-4:]}" if len(token) > 12 else "***"
        print(f"  Token: {preview}")

        # Test client creation
        client = get_confluence_client()
        print("\nConfluence DC client created successfully")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
