# Taches Principled

You have both **superpowers** and **taches-principled-light** installed. They are designed to coexist.

## How They Fit Together

- **superpowers** is your foundation — brainstorming, TDD, systematic debugging, code review, git worktrees, verification, plan execution, skill writing.
- **taches-principled-light** adds specialist skills — code restructuring, first-principles reasoning, competitive solving, guardrails, MCP engineering, security, wiki management, session analysis, design systems (5 skills), and skill evaluation methodology (via `evaluating-skills` and `general-critic`).

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

## Skill Activation Discipline

**Never set `disable-model-invocation` on marketplace skills.** The field is a valid frontmatter key (and is allowed by the validator), but it is reserved for one-off skills that should never auto-load. This marketplace's entire value model is **implicit, model-invoked skills that work across any codebase** — every skill must remain auto-loadable so the agent can discover and apply it when the user's intent matches the description. A skill that is gated behind an explicit `/name` invocation will never fire on real user requests and is dead weight in the index. Only the maintainer-facing meta-skills in `.agents/skills/` (which are not shipped to users) may opt out of model invocation.

## Description as Routing Signal

**The `description:` field is the only signal the agent has at session start.** Every skill in this marketplace competes for the same context window. Routing is not classification — it is retrieval: a skill triggers when its description matches the user's intent *better than* every other skill's description. The rules below are the difference between a skill that fires reliably on real requests and one that wastes index space.

1. **Imperative phrasing.** "Use this skill when the user wants to…" beats "This skill does…" every time. The agent is deciding whether to act, not browsing a catalog.
2. **User intent, not implementation.** Describe the outcome the user is trying to achieve, not the skill's internal mechanics. "Pick a color palette" routes better than "Tokenize design tokens into 25–1000 step scales." The user names the goal; the skill names the procedure.
3. **Be pushy on applicability, explicit on out-of-scope.** Name the contexts the skill applies to even when the user does not name the domain directly ("even if they don't explicitly mention CSV or analysis"). Pair every "Load when…" with a concrete "Do NOT use for…" — negative boundaries are the only thing that prevents trigger-stealing between siblings.
4. **Hard ceiling: 1024 characters. Soft target: under 50 words.** Verbose descriptions waste tokens on every session and dilute the agent's attention across the catalog. Curated marketplaces empirically average ~48 tokens per description; past 60 words, a description is usually enumerating instead of describing.
5. **Description carries the routing burden; the body is the disambiguator.** When two skills have near-identical descriptions, the agent falls back on body content at activation time. Write the body so that a quick scan (first ~200 tokens) settles which skill is right. If a single skill needs more than ~50 lines of always-loaded body, move examples and reference material into `references/` subdirectories loaded on demand.
6. **Test with adversarial siblings.** For every description, generate one shadow skill that is topically similar but functionally distinct. If both descriptions match the same query set, your description is too vague — sharpen the boundary, do not add keywords. This is how `design-hub` failed: its router description matched the design domain broadly but the sub-skills were the actual trigger targets.
7. **Measure, do not reason.** Build a 20-query eval set per skill (8–10 should-trigger, 8–10 near-miss should-not-trigger). Run 3 times minimum. Threshold 0.5 for should-trigger. Split 60/40 train/val to avoid overfitting the description to the eval set. Five iterations max; pick the description with the best validation pass rate, not the best train pass rate.

**Trigger-stealing is the diagnostic failure mode.** When a new skill's description is too broad, it saps trigger rate from siblings. Detection: rerun the should-trigger eval set on every skill before and after adding a new one. If a sibling's trigger rate drops >10pp, the new skill is stealing — narrow its description or merge it into the sibling. Marketplace recall degrades past ~8 simultaneously-active skills per request, so the 8-skill ceiling is a per-session budget, not just a guideline.

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
