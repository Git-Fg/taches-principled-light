# Taches Principled

You have both **superpowers** and **taches-principled-light** installed. They are designed to coexist.

## How They Fit Together

- **superpowers** is your foundation — brainstorming, TDD, systematic debugging, code review, git worktrees, verification, plan execution, skill writing.
- **taches-principled-light** adds specialist skills — code restructuring, first-principles reasoning, competitive solving, guardrails, MCP engineering, security, wiki management, session analysis, design systems (via `design-hub`), and skill evaluation methodology (via `evaluating-skills` and `general-critic`).

## When Both Cover a Topic

Each taches skill has a CONTRAST section. When a topic overlaps with superpowers, the skill redirects explicitly. Examples:

- Want Red-Green-Refactor TDD? → superpowers' `test-driven-development` (taches' `test-orchestration` handles strategy and repair only)
- Want to brainstorm a vague idea into a design? → superpowers' `brainstorming` (taches' `generating-ideas` generates alternatives only)
- Want root-cause debugging? → superpowers' `systematic-debugging`
- Want per-task subagent execution? → superpowers' `subagent-driven-development` (taches' `solving-competitively` does competitive generation)
- Want collaborative skill creation? → superpowers' `writing-skills` (taches' `crafting-skills` creates and optimizes agent skills)
- Want to evaluate whether a skill actually improves behavior? → taches' `evaluating-skills` (8-stage loop with behavioral JSONL review; works across Claude Code, `claude -p`, Codex, kimi-code, Reasonix)
- Want to run a multi-stage research pipeline? → taches' `deep-research` (5 stages writing to `docs/principled/research/<slug>/`)

**The pattern: superpowers for fundamentals, taches-principled-light for depth.**

## Skill Discovery

All taches skills use a uniform description pattern for fast routing:

- **Load when…** — the primary trigger describing user intent
- **Use when…** — concrete trigger phrases the user might say
- **Do NOT use for…** — negative boundary; if your task matches this, skip the skill

When scanning the skill index at startup, match user intent against the trigger phrases
first; the NOT clauses define hard exclusion boundaries between sibling skills.

## Subagent Convention

All skills use platform-agnostic phrasing. Never name a specific tool.

### Explorer (read-only)

```
spawn a subagent explorer with the prompt:
  "<task>"
  Read-only. Return findings as a bounded summary.
```

Use for: codebase mapping, external research, wiki search, verification reads.

### Generalist (edit access)

```
spawn a subagent generalist with the prompt:
  "<task>"
  You have edit access. Implement, verify, return what you changed.
```

Use for: implementation, review, judgment, auditing, fixes.

## Adding a Skill

1. Create `skills/<name>/SKILL.md` with frontmatter + body.
2. Follow `crafting-skills` CREATE mode for authoring new skills; use OPTIMIZE mode for routing improvements.
3. No other files to touch.

## Marketplace Maintenance (.agents/skills/)

Four local meta-marketplace skills live in `.agents/skills/` for maintaining the marketplace itself. They are not shipped to users — they are internal tooling for maintainers.

| Skill | Purpose | Command |
|-------|---------|---------|
| `marketplace-validator` | Lint SKILL.md frontmatter + body against the convention spec | `python3 .agents/skills/marketplace-validator/scripts/validate.py skills/` |
| `marketplace-health` | Pre-release sweep: validator + manifest + license + cross-refs + docs | `python3 .agents/skills/marketplace-health/scripts/health.py` |
| `ingesting-skills` | 9-step porting workflow for adding external skills | `python3 .agents/skills/ingesting-skills/scripts/inventory_source.py <source>` |
| `releasing-marketplace` | 7-step approval-gated release orchestrator | (workflow, no script) |

Run `marketplace-health` before any release cut. It catches cross-reference bugs, license gaps, and stale doc claims that the per-skill validator misses.

## Pre-commit Safety Floor

A pre-commit hook at `.pre-commit-config.yaml` enforces the spec's risky-string scrub rules (`docs/principled/specs/2026-06-23-eval-cleanup-design.md` L145-162) on every commit. The hook lives at `scripts/check-risky-strings.py`. CI runs the same script as a backstop on every push to `main` (see `.github/workflows/marketplace-health.yml`).

One-time setup:

```bash
python3 -m pip install --user pre-commit
pre-commit install
```

Verify on demand:

```bash
pre-commit run --all-files
```

Bypass sparingly with `git commit --no-verify`. The hook only enforces high-signal patterns (specific model IDs, private IPs, error formats) — the broader vendor-name sweep lives in the spec, not the hook, to avoid false positives on legitimate tool-name references.

## Project Closure Convention

For this project, the durable closure marker for a completed work cycle is **CHANGELOG entry + release tag + `grading_summary.json`**. The plan-lifecycle `SUMMARY.md` is optional unless a specific skill explicitly requires it. For archive bundles, `STATUS.md` pointing to the release tag + CHANGELOG entry is an acceptable alternative to `SUMMARY.md` (precedent: `docs/principled/attic/2026-06-22-marketplace-routing-v0.0.6/STATUS.md`).

Rationale: marketplace release cycles use CHANGELOG entries + release tags (e.g., commit `bd04ae0` + `v0.0.6` tag) as the durable summary. `SUMMARY.md` was designed for multi-phase feature delivery, not marketplace release cycles. Codified from `docs/principled/memory/learnings.md` entry titled `[PROCESS] [conf 4] plan-archive workflow needs adaptation for CHANGELOG-as-summary projects`.
