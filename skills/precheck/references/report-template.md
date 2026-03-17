# Assessment Report Template

Structure for the Step 4 assessment report. Two formats: full (default) and condensed (--quick).

## Full Report Format

```
## Precheck Assessment Report

**Intent:** [fix|create|update|delete] — [one-line summary]
**Timestamp:** [ISO 8601]
**Scope:** [module/feature area]
**Mode:** [--deep|--quick|--auto]

### Research Findings

- **Files affected:** [list with paths]
- **Dependencies found:** [N] modules depend on this code
- **Existing patterns:** [conventions observed in the area]
- **Related tests:** [list or "none found"]
- **Recent changes:** [last N commits touching this area]

### Impact Assessment

| Dimension        | Level    | Justification                        |
|------------------|----------|--------------------------------------|
| Blast radius     | [level]  | [N files across M modules]           |
| Breaking risk    | [level]  | [why it might/won't break things]    |
| Data integrity   | [level]  | [data flow concerns or "N/A"]        |
| Performance      | [level]  | [perf implications or "negligible"]  |
| Security         | [level]  | [security surface or "none"]         |

**Overall risk:** [Critical|High|Medium|Low|Minimal]

### Fitness Evaluation

**Score:** [N]/10
- Architecture alignment: [yes/no — why]
- Simpler alternative exists: [yes/no — what]
- Hidden prerequisites: [list or "none"]
- Conflicts with recent changes: [yes/no — details]
- Scope clarity: [well-defined|ambiguous|unclear]

### Concerns & Blockers

- 🔴 **Blocker:** [description] (if any)
- 🟡 **Concern:** [description] (if any)
- 🟢 No blockers identified (if clean)

### Alternative Approaches

1. **[Alternative name]** — [brief description, trade-offs]
2. **[Alternative name]** — [brief description, trade-offs]
3. *(none identified)* — if current approach is optimal

### Recommendation

**[Proceed | Proceed with caution | Reconsider approach | Block]**

Rationale: [1-2 sentences explaining the verdict]
```

## Condensed Report Format (--quick)

Use when `--quick` flag is active. Three to five lines max.

```
**Precheck (quick):** [intent] — [summary]
**Risk:** [level] | **Fitness:** [N]/10 | **Files:** [N]
**Recommendation:** [verdict] — [one-line rationale]
```

## Full Example Report

```
## Precheck Assessment Report

**Intent:** fix — TypeError in UserProfile component when avatar URL is null
**Timestamp:** 2026-03-17T10:42:00+07:00
**Scope:** src/components/UserProfile
**Mode:** --deep

### Research Findings

- **Files affected:** `UserProfile.tsx`, `useUserData.ts`, `Avatar.tsx`
- **Dependencies found:** 4 modules import UserProfile
- **Existing patterns:** Null checks use optional chaining (`?.`) throughout the codebase
- **Related tests:** `UserProfile.test.tsx` exists, covers 3 of 5 render paths
- **Recent changes:** Last modified 12 days ago (commit `a3f91bc` — added avatar upload)

### Impact Assessment

| Dimension        | Level   | Justification                              |
|------------------|---------|--------------------------------------------|
| Blast radius     | Low     | 3 files, 1 component tree                  |
| Breaking risk    | Low     | Fix adds null guard, no API change          |
| Data integrity   | Minimal | Read-only display, no writes                |
| Performance      | Minimal | Single conditional check, negligible cost   |
| Security         | Minimal | No auth/data exposure surface               |

**Overall risk:** Low

### Fitness Evaluation

**Score:** 9/10
- Architecture alignment: yes — follows existing optional chaining pattern
- Simpler alternative exists: no — this is the simplest fix
- Hidden prerequisites: none
- Conflicts with recent changes: no
- Scope clarity: well-defined

### Concerns & Blockers

- 🟡 **Concern:** Test coverage misses the null-avatar path. Add a test case.
- 🟢 No blockers identified

### Alternative Approaches

1. **Default avatar fallback** — Set a default URL in `useUserData.ts` instead of guarding in the component. Trade-off: changes data layer for a display concern.
2. *(Current approach is simpler and more localized)*

### Recommendation

**Proceed**

Rationale: Low risk, high fitness. The fix follows existing patterns and touches minimal code. Suggest adding a test for the null-avatar case during implementation.
```

## Recommendation Decision Rules

| Risk Level | Fitness Score | Verdict              |
|------------|---------------|----------------------|
| Minimal    | >= 8          | Proceed              |
| Low        | >= 7          | Proceed              |
| Low        | < 7           | Proceed with caution |
| Medium     | >= 7          | Proceed with caution |
| Medium     | < 7           | Reconsider approach  |
| High       | any           | Reconsider approach  |
| Critical   | any           | Block                |
