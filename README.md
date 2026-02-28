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
| [confluence-dc](./skills/confluence-dc/) | Manage Confluence Data Center pages/blogs with safety guards, MCP integration, and API fallback *(submodule → [compasify/confluence-skill](https://github.com/compasify/confluence-skill))* |

## Cloning

This repo uses **git submodules** for some skills. Clone with:

```bash
git clone --recurse-submodules https://github.com/compasify/skills.git
```

Or if already cloned:

```bash
git submodule update --init --recursive
```

## Installation
### Claude Code (Recommended)

Register this repository as a plugin marketplace:

```
/plugin marketplace add compasify/skills
```

Install the skill:

```
/plugin install confluence-dc@compasify-skills
```

### OpenCode

Copy the skill to your OpenCode skills directory:

```bash
# Project-level
cp -r skills/confluence-dc .opencode/skills/

# Or user-level (all projects)
cp -r skills/confluence-dc ~/.config/opencode/skills/
```

### Manual (Any Agent)

Copy the desired skill folder to your agent's skills directory:

```bash
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

## License

MIT License — see [LICENSE](LICENSE) for details.

Individual skills may have their own license terms noted in their `LICENSE.txt` files.

## Author

**Compasify** — [github.com/compasify](https://github.com/compasify)

Maintained by Bùi Thế Hiển ([@nickhien](https://github.com/nickhien))
