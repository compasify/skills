# Precheck — Mandatory Pre-Change Assessment Skill

A skill that forces AI agents to research the codebase, assess impact, and evaluate fitness **before touching any code**. No implementation happens until the assessment report is reviewed and approved.

## Problem

AI coding agents often jump straight to implementation without understanding:
- How the change affects existing code
- Whether the approach aligns with the codebase architecture
- What dependencies and side effects exist
- Whether there's a better alternative

This leads to broken builds, unintended regressions, and architectural drift.

## How It Works

The skill enforces a **5-step mandatory gate** before any code change:

```
[Parse Intent] → [Research Codebase] → [Assess Impact] → [Evaluate Fitness] → [Report] → [Handoff]
```

1. **Research** — Parallel exploration of affected files, dependencies, patterns, tests, and git history
2. **Impact Assessment** — Blast radius, breaking risk, data/perf/security analysis with risk classification
3. **Fitness Evaluation** — Architecture alignment, alternative detection, prerequisite discovery, scope check
4. **Report** — Structured assessment presented to the user with a clear recommendation
5. **Handoff** — Route to the appropriate implementation skill (`ck:fix`, `ck:cook`, etc.) with full context

## Installation

### skills.sh (Recommended)

```bash
npx skills add compasify/skills --skill precheck
```

### Manual Copy

```bash
# OpenCode (project-level)
cp -r skills/precheck .opencode/skills/

# OpenCode (user-level, all projects)
cp -r skills/precheck ~/.config/opencode/skills/

# Claude Code
cp -r skills/precheck ~/.claude/skills/

# Cursor
cp -r skills/precheck ~/.cursor/skills/

# Universal (.agents/ convention)
cp -r skills/precheck ~/.agents/skills/
```

## Usage

The skill auto-activates when the agent detects a code change request, or invoke manually:

```
/precheck "Add user authentication to the API"
/precheck "Fix the login timeout bug" --quick
/precheck "Refactor database layer to use connection pooling" --deep
```

### Modes

| Mode | Research Depth | Impact Depth | User Review | Use Case |
|------|---------------|--------------|-------------|----------|
| `--deep` (default) | Parallel agents | Full 5-dimension | Always | Complex or risky changes |
| `--quick` | Single agent | Blast radius + breaking only | Always | Trivial, well-scoped changes |
| `--auto` | Parallel agents | Full 5-dimension | Only if risk > Low | Trusted, low-risk changes |

## File Structure

```
precheck/
├── SKILL.md                          # Core instructions (<120 lines)
├── README.md                         # This file
└── references/
    ├── research-protocol.md          # Parallel codebase research patterns
    ├── impact-assessment.md          # Impact analysis framework (5 dimensions)
    ├── fitness-evaluation.md         # Feasibility and appropriateness criteria
    ├── report-template.md            # Assessment report structure + example
    └── handoff-matrix.md             # Skill routing after assessment
```

## Requirements

- No external dependencies
- Works with any AI coding assistant supporting the Agent Skills standard
- Recommended companion skills: `ck:fix`, `ck:cook` (for post-assessment handoff)

## When This Skill Activates

The skill auto-activates when the agent encounters:
- Requests to fix, create, update, refactor, or delete code
- Any prompt implying code changes
- Manual invocation with `/precheck`

## License

MIT License — see repository [LICENSE](../../LICENSE) for details.

## Author

**Compasify** — [github.com/compasify](https://github.com/compasify)
