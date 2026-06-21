# Rule Taxonomy

Classification of rule types by location, loading behavior, and orchestration strategy.

## Types

### Global Rules

**Location:** `CLAUDE.md` (project root)

**Loading:** Always loaded at session start. Affects every file in the project.

**Use when:** Rule applies universally across all file types, phases, and contexts.

**Examples:**
- Core operational principles ("explain before acting")
- Project-level conventions ("always run tests before committing")
- Tool preferences ("use ripgrep over grep")

**Orchestration action:** Keep lean. Move specifics to `.claude/rules/`. CLAUDE.md should state principles; rules should state specifics.

---

### Path-Scoped Rules

**Location:** `.claude/rules/<name>.md` with `paths:` frontmatter

**Loading:** Loaded only when a matching file is edited. Zero context cost until triggered.

**Use when:** Rule applies to specific file types, languages, or subsystems.

**Examples:**
- TypeScript conventions (paths: "**/*.ts")
- React patterns (paths: "**/*.{tsx,jsx}")
- Test file conventions (paths: "**/*.test.ts")

**Orchestration action:** Audit always-on rules for path-scoping opportunities. Adding `paths:` can reduce startup context significantly.

---

### Always-On Rules

**Location:** `.claude/rules/<name>.md` without `paths:`

**Loading:** Loaded at every session start, same as CLAUDE.md.

**Use when:** Rule is universal within this project but too specific for CLAUDE.md.

**Orchestration action:** Periodically audit for path-scoping opportunities. Group related always-on rules into single files to reduce file count.

---

### Domain Rules

**Location:** `.claude/rules/<domain>/` subdirectory

**Loading:** Recursive discovery — all `.md` files in the domain folder load.

**Use when:** Rule set for a specific project subsystem (auth, database, frontend, etc.)

**Orchestration action:** Create domain subdirectory when a project has more than 5 rules for one concern.

---

### Managed Rules

**Location:** System-level paths (e.g., `/etc/claude-code/`)

**Loading:** Enterprise-enforced, cannot be overridden by project-level rules.

**Orchestration action:** Read-only reference. Do not modify. Document the constraint in CLAUDE.md if relevant.

---

## Placement Decision Tree

```
Is the rule universal — applies to every file in every context?
  YES → CLAUDE.md (principle) or always-on rule (specific)
  NO  ↓
Does it apply to a specific file type or pattern?
  YES → Path-scoped rule (paths: "**/*.{ext}")
  NO  ↓
Does it belong to a specific project subsystem?
  YES → Domain rule (.claude/rules/<domain>/)
  NO  → Always-on rule with a descriptive name
```

## Priority Levels

| Priority | Meaning | Integration |
|----------|---------|-------------|
| **critical** | Correctness or security | Auto-integrate; notify user |
| **important** | Quality or efficiency | Integrate on approval |
| **nice-to-have** | Consistency or style | Queue for REVIEW mode |

## Deduplication

Before adding a rule, check:
1. Is this implied by an existing rule?
2. Does this contradict an existing rule?
3. Is this a special case that should merge with a general rule?

If same category + topic overlap: reinforce existing rule (add evidence) rather than creating duplicate.
