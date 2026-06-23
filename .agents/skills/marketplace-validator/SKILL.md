---
name: marketplace-validator
description: "Load when linting the full marketplace for spec compliance — schema, name format, description length, body size, stale refs, hardcoded tool names. Use for 'lint the marketplace', 'check all skills', 'pre-release lint'. Do NOT use for single-skill pre-commit checks, aggregated audit, or authoring."
---

# Marketplace Validator

Lint the marketplace for spec compliance and local-convention drift. Built on a Python stdlib script (no dependencies) that runs in <1s on the full 31-skill catalog.

## Scope router (decide FIRST)

Identify the scope before reading further. Wrong scope = wrong workflow. The iter-3 behavioral eval (June 2026, N=2) showed this skill **polarizes by scope**: it lifts +45pp on full-marketplace utterances but hurts -20pp on single-skill pre-commit utterances.

| Scope | Utterance shape | Workflow |
|---|---|---|
| **Full marketplace lint** | "lint the marketplace", "validate all skills", "run the pre-release lint", "check the catalog" | `python scripts/validate.py skills/` — no path, default settings. |
| **Single-skill lint** | "lint this skill", "check this skill's frontmatter" | `python scripts/validate.py skills/<name>/` — pass the path. |
| **Pre-commit quick check** | "is this skill valid before I commit", "will this skill pass the linter" | Use `crafting-skills` OPTIMIZE mode or read the SKILL.md and check the 5 most common failure modes inline. This skill's full output is overkill. |
| **CI / pre-commit hook** | (programmatic) | `python scripts/validate.py skills/<name>/ --json --strict` — exit code 1 = fail. |
| **Unclear** | "is this skill valid" | Run on the single skill path, default settings. |

**Default for ambiguous single-skill utterances**: route to `crafting-skills` instead of running this skill's full validator. The full validator is designed for marketplace-wide lint, not single-skill pre-commit checks.

## Decision Router

IF the user wants to check a single skill → pass the path: `python scripts/validate.py skills/<name>`
IF the user wants to check the whole marketplace → no path: `python scripts/validate.py skills/`
IF the user wants machine-readable output (CI, pre-commit) → add `--json`
IF the user wants warnings to fail the build → add `--strict`
IF unclear → run on the whole marketplace, default settings

## What it checks

### Canonical spec (from `agentskills.io` and Anthropic's `skill-creator/scripts/quick_validate.py`)

- **Frontmatter schema.** Only `{name, description, license, allowed-tools, metadata, compatibility}` are spec-allowed. **The local convention is intentionally a superset** — `when_to_use`, `argument-hint`, `context`, `agent`, etc. are local extensions; the validator flags them as *warnings* (not failures) so a maintainer can confirm intent, not a typo.
- **Required fields.** `name` and `description` must be present.
- **Name format.** kebab-case, ≤64 chars, no leading/trailing/double hyphens, no XML, no reserved words (`anthropic-`, `claude-`).
- **Name matches directory.** `name: foo` must live in `foo/SKILL.md`.
- **Description length.** ≤1024 chars, no `<` or `>` characters.
- **Compatibility length.** ≤500 chars if present.
- **Body length.** ≤500 lines (warning, not failure — soft cap per Anthropic best-practices).

### Local convention (from `crafting-skills/references/best-practices-compendium.md`)

- **Description starts with "Load when…"** (compendium rule 1).
- **Description ≤50 words** (compendium rule 3; soft target).
- **Description has "Do NOT use for"** negative trigger clause (compendium rule 2; only checked for descriptions ≥15 words).
- **No stale platform references anywhere in the skill files**: `kimi-code edition`, `disableModelInvocation` (CamelCase form), `$ARGUMENTS`, `type: prompt`, `whenToUse:` (CamelCase form).
- **No hardcoded tool names** (`the Agent tool`, `the Write tool`, etc.) — must use platform-agnostic phrasing per AGENTS.md.

### Routing signal quality

The validator's structural checks catch most defects, but they can't measure *routing quality* — whether an LLM actually picks the right skill from a natural-language prompt. For that, use the routing test:

```bash
python .agents/skills/marketplace-validator/scripts/routing_test.py
```

The test scores every SKILL.md's description against 10 utterances (covering the 4 local meta-skills + 6 adjacent marketplace skills) using content-word overlap. Target: **≥7/10 clear wins** (top match strictly greater than runner-up). Ties and losses indicate description overlap with adjacent skills — add a distinguishing trigger phrase or sharpen the negative trigger. See `references/evaluating-local-skills.md` for the full self-eval protocol.

### Known false positives

- `references/best-practices-compendium.md` (in `crafting-skills`) contains the literal strings `the Agent tool`, `the Write tool`, `the Bash tool` inside a translation table that *teaches* the bad pattern. The validator flags them as warnings; they are teaching examples, not actual hardcoded tool names. Manual review: ignore.
- This SKILL.md itself documents the patterns inside backticks (`` ` ``) so the linter's code-block stripper ignores them. **Convention:** when documenting patterns the linter flags, use backticks. Plain double-quoted strings still trigger the check.

## Usage

```bash
# Lint the whole marketplace
python .agents/skills/marketplace-validator/scripts/validate.py skills/

# Lint one skill
python .agents/skills/marketplace-validator/scripts/validate.py skills/evaluating-skills

# CI / pre-commit
python .agents/skills/marketplace-validator/scripts/validate.py skills/ --strict

# Machine-readable
python .agents/skills/marketplace-validator/scripts/validate.py skills/ --json
```

**Exit codes:**
- `0` — no failures
- `1` — at least one failure (or warning, if `--strict`)

## Reuse

- **`crafting-skills` OPTIMIZE mode** — for any routing-fix recommendations the validator surfaces. The validator *detects*; `crafting-skills` *fixes*.
- **`marketplace-health` skill** — for the broader pre-release audit (manifest consistency, license coverage, cross-reference integrity). The validator is one component of the health sweep.

## Contrast

- `marketplace-validator` — spec + local-convention checks, per-skill output, machine-readable. Foundation tool.
- `marketplace-health` — broader pre-release audit; aggregates validator output plus manifest checks, license coverage, stale-ref scans. Read-only report.
- `crafting-skills` OPTIMIZE — fixes the routing issues the validator surfaces.
- `releasing-marketplace` — orchestrates the release including a validator run in the pre-release gate.

## When NOT to load

- The user wants to write or edit a skill → `crafting-skills` CREATE/OPTIMIZE.
- The user wants to evaluate a skill's behavioral quality → `evaluating-skills` (this marketplace ships 8-stage skill evaluation with behavioral JSONL review).
- The user wants the *broader* marketplace audit (manifests, license, cross-refs) → `marketplace-health`.
- The user wants a release cut → `releasing-marketplace` (which calls this validator internally).
- The user asks "is this skill valid before I commit" → `crafting-skills` OPTIMIZE mode is the right tool; this skill's full marketplace lint is overkill for a pre-commit check.

## Behavioral evidence (iter-3 N=2, June 2026)

The full marketplace lint reliably **lifts** +45pp on `lint-1` ("lint the marketplace and check the frontmatter") but **hurts** -20pp on `lint-2` ("is this skill valid before I commit"). Same skill, similar utterances, opposite effects. The scope router above is the fix — it routes pre-commit utterances to `crafting-skills` before this skill's full validator runs.
