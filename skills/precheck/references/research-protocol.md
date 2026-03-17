# Research Protocol

Parallel codebase research patterns for Step 1 of the precheck workflow. Launch multiple `Explore` agents to scout the codebase before any code change.

## Parallel Exploration Strategy

Launch 3 `Explore` agents simultaneously, each targeting a different research dimension:

```
Task("Explore", "Find all files related to [feature/module]. List file paths, exports, and key functions.", "Scout files")
Task("Explore", "Find all imports/usages of [target]. Trace the dependency chain: who calls it, who depends on it.", "Scout deps")
Task("Explore", "Find test files, config files, and recent git commits touching [area]. Note patterns and conventions.", "Scout context")
```

Wait for all 3 to complete before proceeding to Step 2.

## Research Goals by Intent

| Intent | Agent 1: Files | Agent 2: Dependencies | Agent 3: Context |
|--------|---------------|----------------------|-----------------|
| **Fix** | Error source files, stack trace locations, related modules | Call chain to/from broken code, shared state | Failing tests, recent commits in area, similar past fixes |
| **Create** | Existing similar features, directory conventions, base classes | Modules the new code must integrate with | Naming patterns, test patterns, config conventions |
| **Update** | Target files + all files sharing the interface | Consumers of the changed API/interface | Test coverage of target, breaking change history |
| **Delete** | Target files + all references | Full reverse-dependency tree (critical) | Tests that will break, configs referencing target |

## Agent Prompt Templates

### Fix/Debug
```
Agent 1: "Find files related to [error/symptom]. Check error messages, stack traces, log outputs. List all files that could produce this behavior."
Agent 2: "Trace the call chain for [function/module]. Who calls it? What data flows through it? What shared state does it touch?"
Agent 3: "Find tests covering [area], recent git log for [files] (last 20 commits), and any TODO/FIXME/HACK comments nearby."
```

### Create/Add
```
Agent 1: "Find existing [similar feature type] implementations. What directory structure, naming conventions, and base patterns do they follow?"
Agent 2: "Map the integration points for [new feature]. What existing modules, APIs, or services must it connect to? List their interfaces."
Agent 3: "Find test patterns for [similar features]. Check for shared test utilities, fixtures, mocks. Note the test file naming convention."
```

### Update/Modify
```
Agent 1: "Find all files containing [target interface/function/type]. Include type definitions, implementations, and re-exports."
Agent 2: "Find every consumer of [target]. Search for imports, function calls, type references. Flag any that depend on the current behavior."
Agent 3: "Check git log for [target files] — last 30 commits. Find related tests. Note any version constraints or deprecation warnings."
```

### Delete/Remove
```
Agent 1: "Find ALL references to [target] across the entire codebase. Include imports, string references, config entries, documentation links."
Agent 2: "Build the full reverse-dependency tree for [target]. What breaks if this disappears? Check transitive dependencies too."
Agent 3: "Find tests that import or reference [target]. Check CI configs, build scripts, and deployment manifests for references."
```

## Research Checklist

Every research pass must cover these items. Mark each as found or confirmed absent:

| Category | Items to Discover | Priority |
|----------|------------------|----------|
| **Files** | Direct target files, related modules, shared utilities | Required |
| **Dependencies** | Import chain (in), usage chain (out), shared state | Required |
| **Patterns** | Naming conventions, directory structure, code style in area | Required |
| **Tests** | Existing test files, coverage gaps, test utilities used | Required |
| **Git history** | Recent commits (last 20), related PRs, blame for key lines | Recommended |
| **Config** | Build configs, env vars, feature flags affecting target | If applicable |
| **Docs** | README, inline docs, API docs referencing target | If applicable |

## Research Output Format

Synthesize all agent findings into this structure:

```markdown
## Research Report

**Intent:** [fix|create|update|delete] — [one-line summary]
**Scope:** [N] files directly affected, [M] dependencies found

### Affected Files
- `path/to/file.ts` — [role: source of bug | integration point | test]
- `path/to/other.ts` — [role]

### Dependency Map
- **Upstream** (calls into target): [list callers]
- **Downstream** (target calls): [list callees]
- **Shared state**: [list shared modules/stores/configs]

### Patterns Observed
- Naming: [convention found]
- Structure: [directory pattern]
- Testing: [test pattern, framework, utilities]

### Git Context
- Last modified: [date, author, commit msg]
- Recent activity: [high|medium|low] — [N] commits in last 30 days
- Related changes: [any relevant recent PRs or refactors]

### Gaps & Unknowns
- [anything agents couldn't find or that needs clarification]
```

## Quick Mode (--quick)

Single `Explore` agent with a combined prompt. Reduced scope for trivial changes:

```
Task("Explore", "Quick scan for [target]: list affected files, direct imports/exports, and any test files. Skip git history and deep dependency tracing.", "Quick scout")
```

Quick mode skips: git history analysis, transitive dependencies, pattern deep-dive, documentation scan. Still produces the Research Report but with fewer sections filled.

## Resource Limits

- Max 3 parallel `Explore` agents (system resources)
- Keep each prompt under 200 words to avoid context bloat
- If agents return overlapping results, deduplicate before reporting
- Total research phase target: under 60 seconds for `--deep`, under 20 seconds for `--quick`
