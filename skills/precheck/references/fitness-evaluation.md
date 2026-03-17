# Fitness Evaluation — Step 3 Reference

Evaluate whether the requested change is appropriate, well-scoped, and aligned with the codebase. Produce a fitness score (1-10) that feeds the assessment report.

## Fitness Checklist

Answer each question yes/no. Each "no" reduces the fitness score.

### Architecture Alignment (weight: high)

- [ ] Does the change follow existing patterns in the affected area?
- [ ] Does it use the same libraries, abstractions, and conventions already present?
- [ ] Does it respect module boundaries and dependency direction?
- [ ] Would a maintainer recognize this as "belonging" in the codebase?

### Scope Definition (weight: high)

- [ ] Is the request specific enough to implement without guessing?
- [ ] Can the change be completed in a single focused session?
- [ ] Are acceptance criteria clear (or inferable from context)?
- [ ] Does the scope avoid mixing unrelated concerns?

### Alternative Approaches (weight: medium)

- [ ] Has the obvious simpler solution been considered?
- [ ] Is this the right layer/module for this change?
- [ ] Could an existing utility, hook, or helper solve this already?
- [ ] Does the approach avoid reinventing what the framework provides?

### Hidden Prerequisites (weight: medium)

- [ ] Are all dependencies available (packages, APIs, configs)?
- [ ] Do required migrations, schema changes, or env vars exist?
- [ ] Is the target code in a stable state (no pending refactors blocking this)?
- [ ] Are related features/modules this depends on already merged?

### Conflict Detection (weight: low)

- [ ] Does this conflict with changes merged in the last 7 days?
- [ ] Are other active branches touching the same files?
- [ ] Does this contradict any recently established patterns?

## Scoring Rubric

Count "no" answers, weigh by category, then map to the 1-10 scale.

| Score | Band | Criteria | Action |
|-------|------|----------|--------|
| 9-10 | Excellent | All checks pass. Clear scope, follows patterns, no conflicts. | Proceed. |
| 7-8 | Good | 1-2 minor "no" answers (low/medium weight). Concerns are addressable inline. | Proceed with notes. |
| 5-6 | Questionable | 3+ "no" answers OR any high-weight failure. Scope unclear or pattern mismatch. | Pause. Clarify with user before proceeding. |
| 3-4 | Poor | Multiple high-weight failures. Significant architectural mismatch or missing prerequisites. | Recommend modified approach. |
| 1-2 | Misaligned | Fundamentally wrong layer, pattern, or scope. Contradicts codebase direction. | Recommend complete rethink. |

### Score Calculation Logic

1. Start at 10.
2. Each high-weight "no" subtracts 2 points.
3. Each medium-weight "no" subtracts 1 point.
4. Each low-weight "no" subtracts 0.5 points.
5. Floor at 1. Round to nearest integer.

## Decision Logic

### When to Proceed (score >= 7)

Report the score, note any minor concerns, and hand off to implementation.

### When to Clarify (score 5-6)

Present specific "no" answers to the user. Ask targeted questions:
- "The codebase uses [pattern X] here, but this request implies [pattern Y]. Which approach?"
- "This depends on [prerequisite]. Is that already in place?"
- "The scope covers [A, B, C]. Can we narrow to [A] first?"

### When to Recommend Alternatives (score 3-4)

Don't just flag problems. Propose a concrete alternative:
- "Instead of [requested approach], consider [alternative] because [reason]."
- "Split this into [phase 1] and [phase 2] to reduce risk."
- "Move this logic to [correct module] to match existing patterns."

### When to Block (score 1-2)

State clearly why the request is misaligned. Provide:
- What the codebase expects vs what was requested.
- The minimum viable pivot that could work.
- Whether this needs a design discussion before any code.

## Common Fitness Failures

| Failure | Example | Typical Score |
|---------|---------|---------------|
| Wrong abstraction layer | Adding business logic in a UI component | 3-4 |
| Scope creep disguised as one task | "Add auth" that actually means auth + roles + permissions + UI | 4-5 |
| Pattern contradiction | Using REST in a codebase that's fully GraphQL | 2-3 |
| Missing prerequisite | Feature needs a DB migration that doesn't exist yet | 5-6 |
| Duplicate solution | Building a custom date picker when the design system has one | 6-7 |
| Stale assumption | Request based on old architecture that was refactored last sprint | 3-4 |
| Ambiguous scope | "Make it faster" with no metrics or target | 4-5 |

## Quick Mode Variant

When `--quick` is active, run a reduced checklist (architecture alignment only):

1. Does the change follow existing patterns? (yes/no)
2. Does it respect module boundaries? (yes/no)
3. Is the scope clear and single-purpose? (yes/no)

**Quick scoring:** All yes = 9. One no = 7. Two no = 5. All no = 3.

Skip alternative approach detection, hidden prerequisite discovery, and conflict detection. Note in the report that a quick evaluation was used.

## Integration with Report

Pass these values to the assessment report (Step 4):

- `fitness_score`: Integer 1-10
- `fitness_band`: Excellent / Good / Questionable / Poor / Misaligned
- `failed_checks`: List of specific "no" answers with category
- `alternatives`: Concrete alternative approaches (if score < 7)
- `blockers`: Hard blockers preventing implementation (if any)
- `evaluation_mode`: `deep` or `quick`
