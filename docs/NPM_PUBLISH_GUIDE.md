# NPM Publishing Guide

Guide for publishing individual skills as npm packages.

## Prerequisites

- Node.js 18+
- npm account (`npm login`)
- Publish access to the `@compasify` scope (if using scoped packages)

## Package Structure

Each skill that you want to publish to npm needs its own `package.json`:

```
skills/confluence-dc/
├── package.json        # npm manifest
├── SKILL.md
├── scripts/
├── references/
└── LICENSE.txt
```

### Example `package.json`

```json
{
  "name": "@compasify/skill-confluence-dc",
  "version": "1.0.0",
  "description": "AI agent skill for Confluence Data Center with MCP integration",
  "main": "SKILL.md",
  "files": [
    "SKILL.md",
    "scripts/**/*",
    "references/**/*",
    "LICENSE.txt"
  ],
  "keywords": [
    "agent-skill",
    "claude-code",
    "opencode",
    "confluence",
    "atlassian",
    "mcp"
  ],
  "author": "Compasify <hien.bt@htsc.vn>",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/compasify/skills.git",
    "directory": "skills/confluence-dc"
  },
  "homepage": "https://github.com/compasify/skills/tree/main/skills/confluence-dc"
}
```

## Publishing Steps

### 1. Create npm org (one-time)

```bash
# Create the @compasify scope on npmjs.com
npm login
npm org create compasify
```

### 2. Add package.json to the skill

```bash
cd skills/confluence-dc
# Create package.json (see example above)
```

### 3. Publish

```bash
cd skills/confluence-dc
npm publish --access public
```

### 4. Update marketplace.json

After publishing to npm, you can add an npm source to the marketplace:

```json
{
  "name": "confluence-dc",
  "source": {
    "source": "npm",
    "package": "@compasify/skill-confluence-dc",
    "version": "^1.0.0"
  },
  "description": "Confluence DC skill with MCP integration"
}
```

## Versioning

Follow semver:
- **Patch** (1.0.x): Bug fixes, typo corrections in SKILL.md
- **Minor** (1.x.0): New features, new references, script improvements
- **Major** (x.0.0): Breaking changes to skill behavior or API

## Publishing Checklist

- [ ] `package.json` has correct `name`, `version`, `description`
- [ ] `files` array includes all necessary files
- [ ] `SKILL.md` frontmatter is valid
- [ ] Scripts work correctly (`python scripts/confluence_api.py --help`)
- [ ] `npm pack` produces expected tarball contents
- [ ] `npm publish --dry-run` succeeds
- [ ] Version is bumped from previous release

## Installing from npm

Users can install published skills:

```bash
# Via Claude Code marketplace (if npm source is configured)
/plugin install confluence-dc@compasify-skills

# Via npm directly
npm install @compasify/skill-confluence-dc
# Then copy SKILL.md to your skills directory
```
