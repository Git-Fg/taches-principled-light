---
name: marketplace-health
description: >
  Load when auditing the marketplace as a whole — convention compliance,
  manifest consistency, license coverage, cross-reference integrity, and
  docs-reflect-state checks across all skills and the 4 plugin manifests.
  Use when the user says 'is the marketplace healthy', 'audit the marketplace',
  'pre-release health check', 'check for drift', or 'sweep before cutting
  a version'. Do NOT use for single-skill lint (use marketplace-validator) or
  for release cutting itself (use releasing-marketplace).
when_to_use: |
  Use before any release cut, on request as a periodic sweep, and after
  ingesting a new skill. The output is a single Markdown report at
  docs/principled/marketplace-health/<date>.md.
argument-hint: "[--date YYYY-MM-DD] [--no-fail]"
allowed-tools: Read, Bash, Glob, Grep
---

# Marketplace Health

The pre-release sweep. Aggregates `marketplace-validator` output with manifest consistency, license coverage, cross-reference integrity, and docs-reflect-state checks. Single Markdown report; deterministic; <5s on the full 31-skill catalog.

## Decision Router

IF the user wants a single-skill lint → `marketplace-validator` (faster, more focused)
IF the user wants the full sweep → `python .agents/skills/marketplace-health/scripts/health.py`
IF the user wants CI-friendly output → add `--no-fail` (always exit 0) for advisory
IF the user wants the report at a custom path → add `--output <path>`
IF unclear → run the full sweep with defaults

## What it checks

| Check | What it does | Pass criterion |
|---|---|---|
| **Validator** | Runs `marketplace-validator` over all skills | 0 failures (warnings allowed) |
| **Manifest consistency** | Compares version + description across all 4 plugin manifests | All at the same version |
| **License coverage** | Scans every `SKILL.md` frontmatter for `license:` field | Every skill has one |
| **Cross-reference integrity** | Resolves every `references/X.md` and `scripts/X.py` citation in skill files | All resolve to real paths |
| **Skill count** | Counts `SKILL.md` files recursively | Reported; no pass/fail (caller decides) |
| **Docs reflect state** | Compares README's "26 skills" claim to actual count | Numbers match |

### Cross-reference checks: opt-out convention

Documentation files that *quote* reference paths as teaching examples (e.g., the `crafting-skills` reference file that shows "WRONG: read `references/patterns.md`" vs. "RIGHT: read `references/patterns.md` BEFORE proceeding") can opt out of citation checks with an HTML comment at the top of the file:

```html
<!-- check-citations-skip: this file's body quotes `references/patterns.md` as teaching examples for the WRONG/RIGHT citation rule. The cited path is a string inside the example, not a navigation pointer. -->
```

The opt-out covers the whole file. Use sparingly. Lines with inline backticks and lines inside fenced code blocks are also skipped by default — no opt-out needed for those.

## Usage

```bash
# Full sweep, default output path
python .agents/skills/marketplace-health/scripts/health.py

# Pre-release gate (CI)
python .agents/skills/marketplace-health/scripts/health.py --no-fail

# Custom date
python .agents/skills/marketplace-health/scripts/health.py --date 2026-06-22

# Custom output
python .agents/skills/marketplace-health/scripts/health.py --output /tmp/health.md
```

**Exit codes:**
- `0` — no hard failures (warnings allowed)
- `1` — at least one hard failure (manifest diverge, broken cross-ref, doc state mismatch)

**Output:** `docs/principled/marketplace-health/<YYYY-MM-DD>.md` by default. The file is committed to the repo as the audit trail.

## Reuse

- **`marketplace-validator`** is a *component* of this health sweep. The validator handles per-skill frontmatter + body checks; this skill adds the marketplace-level concerns (manifests, license, cross-refs, doc state).
- **`releasing-marketplace`** calls this skill as its pre-release gate.
- **`crafting-skills` OPTIMIZE mode** for any routing-fix recommendations surfaced here.

## Contrast

- `marketplace-validator` — per-skill lint, fast, machine-readable, foundation tool.
- `marketplace-health` — pre-release audit, broader scope, slower (runs the validator + 5 other checks), Markdown report.
- `releasing-marketplace` — orchestrator that uses this skill's report as one input.
- `crafting-skills` OPTIMIZE — fixes the issues these audits surface.

## When NOT to load

- Single-skill lint → `marketplace-validator`.
- Release cutting → `releasing-marketplace` (which calls this skill internally).
- Authoring or modifying a skill → `crafting-skills` CREATE/OPTIMIZE.
- Evaluating whether a skill materially changes behavior → `evaluating-skills`.