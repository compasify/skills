# Compasify Skills

A curated collection of enterprise AI agent skills for Atlassian, DevOps, and productivity workflows.

## About

This repository contains reusable agent skills built by [Compasify](https://github.com/compasify). Each skill is self-contained in its own folder with a `SKILL.md` file containing instructions and metadata that AI agents use to perform specialized tasks.

Skills work with any AI coding assistant that supports the [Agent Skills](https://agentskills.io) standard:
- **Claude Code** (plugin marketplace)
- **OpenCode**
- **Cursor**
- **Windsurf**
- **Antigravity**
- **VS Code + Cline/Roo**

## Available Skills

| Skill | Description |
|-------|-------------|
| [confluence-dc](./skills/confluence-dc/) | Manage Confluence Data Center pages/blogs with safety guards, MCP integration, and API fallback *(synced from [compasify/confluence-skill](https://github.com/compasify/confluence-skill))* |
| [long-md-writer-api](./skills/long-md-writer-api/) | Write large Markdown files via local HTTP API server (Python stdlib, 0 deps) |
| [md-long-content-writer](./skills/md-long-content-writer/) | Write large Markdown files (100+ lines) reliably with chunked appends and fallback scripts |
| [precheck](./skills/precheck/) | Mandatory pre-change assessment — research codebase, assess impact, evaluate fitness before any code change |

## Cloning

```bash
git clone https://github.com/compasify/skills.git
```

> **For maintainers:** Some skills are managed via `git subtree`. See [Contributing](#contributing) for sync commands.

## Installation

### skills.sh (Recommended)

Install via the [skills.sh](https://skills.sh) CLI — works with Claude Code, Cursor, OpenCode, Windsurf, Cline/Roo, AMP, Codex, and [more](https://skills.sh):

```bash
# Install confluence-dc from this monorepo
npx skills add compasify/skills --skill confluence-dc

# Or install from the standalone repo
npx skills add compasify/confluence-skill

# Install to a specific agent only
npx skills add compasify/skills --skill confluence-dc -a claude-code

# Install globally (user-level, all projects)
npx skills add compasify/skills --skill confluence-dc -g
```

### Claude Code Plugin Marketplace

```
/plugin marketplace add compasify/skills
/plugin install confluence-dc@compasify-skills
```

### Manual Copy

Clone this repo and copy the skill folder to your agent's skills directory:

```bash
# OpenCode (project-level)
cp -r skills/confluence-dc .opencode/skills/

# OpenCode (user-level, all projects)
cp -r skills/confluence-dc ~/.config/opencode/skills/

# Claude Code
cp -r skills/confluence-dc ~/.claude/skills/

# Cursor
cp -r skills/confluence-dc ~/.cursor/skills/

# Universal (.agents/ convention)
cp -r skills/confluence-dc ~/.agents/skills/
```

## Creating a New Skill

Use the [template](./template/SKILL.md) as a starting point:

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it.
---

# My Skill Name

[Instructions here]
```

Each skill folder can contain:

```
my-skill/
├── SKILL.md          # Required: instructions + metadata
├── scripts/          # Optional: executable code
├── references/       # Optional: documentation
├── LICENSE.txt       # License for this skill
└── assets/           # Optional: templates, resources
```

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a skill in `skills/your-skill-name/`
3. Include a `SKILL.md` with proper frontmatter
4. Submit a pull request

### Subtree-Managed Skills

Some skills (e.g. `confluence-dc`) are synced from standalone repos via `git subtree`.

```bash
# Pull latest changes from upstream
git subtree pull --prefix=skills/confluence-dc https://github.com/compasify/confluence-skill.git main --squash

# Push local changes back to upstream
git subtree push --prefix=skills/confluence-dc https://github.com/compasify/confluence-skill.git main
```

## License

MIT License — see [LICENSE](LICENSE) for details.

Individual skills may have their own license terms noted in their `LICENSE.txt` files.

## Author

**Compasify** — [github.com/compasify](https://github.com/compasify)

Maintained by Bùi Thế Hiển ([@nickhien](https://github.com/nickhien))
