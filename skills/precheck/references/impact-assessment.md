# Impact Assessment Framework

Score each dimension 1-5. Combine scores to classify overall risk.

## Dimension Scoring Rubrics

### 1. Blast Radius

| Score | Criteria |
|-------|----------|
| 1 | Single file, no dependents |
| 2 | 2-3 files in same module |
| 3 | 4-10 files, crosses 1 module boundary |
| 4 | 10-25 files, crosses multiple modules |
| 5 | 25+ files or touches shared core (utils, types, config) |

Count both direct and transitive dependents. A change to a shared type file scores higher than a leaf component.

### 2. Breaking Risk

| Score | Criteria |
|-------|----------|
| 1 | Internal-only change, no public API touched |
| 2 | Public API unchanged, behavior subtly different |
| 3 | API signature change with backward compatibility |
| 4 | Breaking API change, consumers must update |
| 5 | Breaking change to external/published API or contract |

Check: function signatures, type exports, event names, route paths, env vars, config keys.

### 3. Data Integrity

| Score | Criteria |
|-------|----------|
| 1 | No data read/write involved |
| 2 | Reads data, no writes |
| 3 | Writes data with existing validation |
| 4 | Schema migration, state shape change, or new write path |
| 5 | Destructive migration, cross-system data sync, or no rollback path |

Flag any change touching database schemas, cache keys, localStorage shapes, or serialization formats.

### 4. Performance

| Score | Criteria |
|-------|----------|
| 1 | No runtime impact |
| 2 | Negligible impact (< 5% regression plausible) |
| 3 | Adds computation in hot path or increases bundle by 10-50KB |
| 4 | New network calls, heavy computation, or bundle increase > 50KB |
| 5 | O(n) → O(n²) change, unbounded queries, or memory leak potential |

Consider: loop complexity, async waterfalls, re-render cascades, lazy-load boundaries.

### 5. Security

| Score | Criteria |
|-------|----------|
| 1 | No auth, input, or secret handling |
| 2 | Touches input handling with existing sanitization |
| 3 | New user input path or modified auth check |
| 4 | Changes auth flow, adds secret handling, or modifies CORS/CSP |
| 5 | Touches auth bypass logic, crypto, token generation, or admin routes |

Check OWASP Top 10 relevance: injection, broken auth, sensitive data exposure, XXE, broken access control.

## Overall Risk Classification

Sum all 5 dimension scores (range: 5-25). Apply the highest single-dimension score as a floor.

| Sum | Classification | Floor Override |
|-----|---------------|----------------|
| 5-7 | **Minimal** | Any dim = 4 → Low minimum |
| 8-11 | **Low** | Any dim = 4 → Medium minimum |
| 12-16 | **Medium** | Any dim = 5 → High minimum |
| 17-20 | **High** | Two dims ≥ 4 → High minimum |
| 21-25 | **Critical** | Any dim = 5 + sum ≥ 17 → Critical |

The floor override prevents a dangerous single dimension from hiding behind low averages.

## Red Flags (Automatic Escalation)

These conditions override the scoring formula. Escalate to **Critical** immediately:

| Red Flag | Why |
|----------|-----|
| No tests exist for affected code | No safety net for regression |
| Change touches auth/permission logic | Security-critical path |
| Destructive DB migration without rollback | Irreversible data loss risk |
| Modifies shared types used by 10+ consumers | Cascade failure potential |
| Removes or weakens input validation | Injection attack surface |
| Changes crypto, token, or secret handling | Requires security review |

## Intent-Specific Considerations

| Intent | Key Adjustments |
|--------|----------------|
| **Fix/Debug** | Blast radius often underestimated (root cause spans modules). Score breaking risk on behavioral change, not line count. Data corruption bugs → data integrity ≥ 4. |
| **Create/Add** | Blast radius typically low, but score integration seams. Focus breaking risk where new code connects to existing code. Score perf based on hot path vs. cold path. |
| **Update/Refactor** | Highest average blast radius. Map full dependency chain. Breaking risk = behavior change, not structural change. Renames/moves → score by consumer count. |
| **Delete/Remove** | Score data integrity ≥ 3 unless proven no data refs. Check dynamic references (string imports, config routing). Grep-verify "unused" code for indirect usage. |

## Example Assessments

### Fixing a typo in a UI label

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Blast radius | 1 | Single component file |
| Breaking risk | 1 | No API change |
| Data integrity | 1 | Display only |
| Performance | 1 | No runtime change |
| Security | 1 | No input/auth involved |
| **Total** | **5** | **Minimal** |

### Adding a new API endpoint

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Blast radius | 2 | Route file + controller + service |
| Breaking risk | 1 | New endpoint, nothing breaks |
| Data integrity | 3 | Writes to database |
| Performance | 2 | New query, indexed |
| Security | 3 | New input path, needs validation |
| **Total** | **11** | **Low** — no floor override triggered |

### Refactoring shared auth middleware

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Blast radius | 5 | Every authenticated route affected |
| Breaking risk | 4 | Middleware signature changing |
| Data integrity | 2 | Session reads, no writes |
| Performance | 2 | Same complexity |
| Security | 5 | Core auth path |
| **Total** | **18** | **Critical** — red flag: auth logic, dim=5 |
