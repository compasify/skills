# Handoff Matrix

Routing logic for Step 5. Determines which skill receives the implementation task and what context to pass.

## Routing Table

| Intent | Target Skill | Mode | Extra Gate |
|--------|-------------|------|------------|
| Fix/Debug | `ck:fix` | default | none |
| Create/Add | `ck:cook` | default | none |
| Update/Modify | `ck:cook` | `--fast` | none |
| Refactor | `ck:cook` | `--fast` | none |
| Delete/Remove | `ck:cook` | default | Safety confirmation required |
| Quick trivial | Direct implementation | n/a | Only if `--quick` AND risk=Minimal |

## Context to Pass Per Skill

### `ck:fix`

Pass these fields from the assessment:
- **Root cause** (from research findings)
- **Affected files** (exact paths)
- **Reproduction path** (if identified during research)
- **Related tests** (so fix can verify against them)

### `ck:cook` (create/implement)

Pass these fields:
- **Research context** (patterns found, conventions, dependencies)
- **Suggested plan** (from fitness evaluation's architecture alignment notes)
- **Files to create/modify** (from impact assessment)
- **Concerns** (any yellow/red flags from the report)

### `ck:cook --fast` (update/refactor)

Pass these fields:
- **Impact analysis summary** (blast radius, breaking risk)
- **Affected files** (exact paths with dependency chain)
- **Existing patterns** (so refactor stays consistent)
- **Test coverage status** (which tests exist, which are missing)

## Handoff Prompt Format

Structure the handoff as a single activation prompt:

```
[Skill activation] [task summary]

**Precheck context:**
- Intent: [type]
- Risk: [level]
- Fitness: [score]/10
- Files: [list]
- [context fields per skill, from sections above]

**Concerns:** [list or "none"]
**User request:** [original user message]
```

### Example: Fix Handoff

```
ck:fix TypeError in UserProfile when avatar URL is null

**Precheck context:**
- Intent: fix
- Risk: Low
- Fitness: 9/10
- Files: UserProfile.tsx, useUserData.ts, Avatar.tsx
- Root cause: No null guard on `user.avatarUrl` before passing to Avatar component
- Related tests: UserProfile.test.tsx (missing null-avatar test path)

**Concerns:** Test coverage gap for null-avatar case
**User request:** "Fix the TypeError crash on the profile page when users don't have an avatar"
```

## Special Cases

### Delete/Remove — Extra Safety Gate

Before handing off delete intents, present an explicit confirmation via `AskUserQuestion`:

- Show exactly what will be deleted (files, database records, API endpoints)
- Show what depends on the deleted code (from dependency chain)
- Require user to pick: "Confirm deletion" or "Abort"

Only proceed to `ck:cook` after explicit confirmation. Never auto-proceed deletes, even with `--auto`.

### Multiple Intents in One Request

If the user's request spans multiple intents (e.g., "fix the bug and add a new feature"):

1. Split into separate precheck assessments
2. Present a combined report with per-intent sections
3. Hand off to the highest-priority intent first
4. Queue remaining intents as follow-up tasks

Priority order: Fix > Delete > Update > Create

## Direct Implementation (Skip Handoff)

Implement directly without routing to another skill ONLY when ALL conditions are met:

| Condition | Required Value |
|-----------|---------------|
| Mode | `--quick` |
| Risk level | Minimal |
| Fitness score | >= 9 |
| Files affected | 1 |
| Breaking risk | None |

Examples of qualifying changes:
- Fixing a typo in a string literal
- Updating a version number in config
- Adding a single CSS class
- Correcting a comment

If any condition fails, route to the appropriate skill. When in doubt, route.
