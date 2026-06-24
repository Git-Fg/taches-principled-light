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

**Trigger-stealing is the diagnostic failure mode.** When a new skill's description is too broad, it saps trigger rate from siblings. Detection: rerun the should-trigger eval set on every skill before and after adding a new one. If a sibling's trigger rate drops >10pp, the new skill is stealing — narrow its description or merge it into the sibling.

## Marketplace Scaling

> **Version anchor.** All Claude Code budgets and warnings below are documented against **Claude Code v2.1.105+** (the release that introduced `skillListingBudgetFraction` as a user-tunable setting). For pre-v2.1.105 Claude Code, the legacy implicit 2% scaling formula from v2.1.32 applies — see the "Claude Code (legacy)" row in the cross-platform table below. Both rows document their own defaults; nothing in this section silently assumes the v2.1.105+ 1% default for an unversioned client.

Routing quality degrades as the catalog grows. The constraint is **character-based, not count-based**. Claude Code's `skillListingBudgetFraction` defaults to **0.01 of context (≈2,000 tokens / ≈8,000 chars at 200K context, per `code.claude.com/docs/en/settings` and claudefa.st's v2.1.129 binary extraction)**. The current 1% default was set when the setting was made explicit; the v2.1.32 CHANGELOG line "Skill character budget now scales with context window (2% of context)" was the prior *implicit* scaling formula, not the current default. Per-skill listing cost is **75–150 tokens** including the XML wrapper, name, location, and frontmatter overhead (was ~50 tokens in prior research, which measured only name + description; the current methodology counts the full listing entry — claudefa.st, May 2026). At the current 1% default on a 200K context window, ~15–25 skills trigger the warning; at 1M context, ~75–125. The budget scales linearly with description length and the `skillListingBudgetFraction` setting. (`skillListingBudgetFraction` and `skillListingMaxDescChars` are user-tunable overrides; `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var takes precedence.)

**Truncation is NOT silent.** Anthropic emits three user-visible signals when the budget is exceeded:

- **Startup warning** at session start: `"Skill listing will be truncated"` with the percentage vs budget (`X%/Y% of context`).
- **`/doctor` command**: full breakdown of which skills were dropped, accessible on demand.
- **`/context`** at session start: shows a `Skills:` line with the percentage of context currently consumed.

The selection logic for which skills survive is **recency + frequency** (most-invoked survives, least-invoked drops) — Claude Code tracks usage and ranks descriptions by frequency, not by position in the catalog. This means a marketplace with 80 skills where 30 are heavily used may behave correctly even though the listing exceeds the budget; the warning fires but the actively-used skills keep their full descriptions.

| Catalog size | Symptom | Action |
|---|---|---|
| 5–15 skills | Practitioners first observe wrong-pick symptoms; descriptions start competing for attention. The "around 7–8 skills, things get weird" community observation lands here (PromptSpace 2026), not at the marketplace ceiling. | Run the shadow-skill check (AGENTS.md rule 6) before adding more; tighten near-miss boundaries. |
| <50 skills | Progressive disclosure works as designed for sessions that load a handful of skills. Below the current 1% budget warning threshold (~15–25 skills at 200K context; ~75–125 at 1M). | Continue adding; run the trigger-eval harness on each new description. |
| 25–50 skills | At the current 1% default budget, sessions with 25+ skills start firing the startup warning at 200K context. The warning is visible but the actively-used skills keep their descriptions (recency + frequency selection). New or rarely-used skills may go names-only. | Tighten descriptions toward the 50-word soft target; disable rarely-used skills (`/skills` → disable) instead of deleting them — disabled skills don't count against the budget (claudefa.st). |
| 50–100 skills | Beyond the recency + frequency protection (per claudefa.st's observation; the empirical hit rate at this size is not yet studied in peer-reviewed literature): even actively-used skills may start losing descriptions, depending on usage distribution. | Consolidation is mandatory — split the catalog into thematic hubs (the 14 sub-skills-per-hub figure below is the Skill Hub estimate: 14 tools × ~14 skills ≈ 200). |
| 100–200 skills | Cross-cluster trigger rate degrades even for power users with raised budgets (`skillListingBudgetFraction: 0.05`). | Pattern 2 (tool-facade hub, next section) becomes appropriate toward the upper end of this range. |
| 200–500 skills | Tool-facade hub fragmentation: each cluster still has to fit its own description budget. | Pattern 2 in full: collapse the catalog behind ~14 router tools, each loading its own ~14-skill cluster on demand. |
| 500–1,000 skills | Even a well-built hub starts to fragment attention. | Pattern 3 (external retrieval, semantic-index tier). |
| >1,000 skills | Attention quality degrades continuously even with full body access — the agent starts making wrong picks on hand-eye-distinguishable cases. The curve does not plateau before catastrophic failure. | Pattern 3 (external retrieval, trained-reranker tier) is required. |

**Three scaling patterns** that cover 50–80,000 skills without restructuring the skill format itself:

1. **In-place tightening** (≤100 skills): keep the flat catalog, run SkillReducer-style compression to shorten descriptions ~48%, doubling the per-budget cap. Discipline cost: every addition must be re-evaluated. Source: SkillReducer arXiv:2603.29919.
2. **Tool-facade hub** (~200–500 skills): collapse the catalog behind ~14 router tools; each tool loads its own cluster of ~14 sub-skills on demand (Skill Hub's 14-tool registry exposing 200 skills). Engineering cost: a registry layer + a routing policy per hub. Source: Skill Hub.
3. **External retrieval** (≥500 skills): keep descriptions as a corpus, retrieve top-K at session start.
   - **Semantic index** (~500–5,000 skills): embed all descriptions, return top-K by similarity. Cheapest per-query cost.
   - **Trained reranker** (~5,000–80,000 skills): two-stage retrieve-and-rerank with a 1.2B-param model (SkillRouter). Cost: an extra model call per turn. SkillRouter reports a 31–44pp Hit@1 drop if you remove the full body from candidates, so the corpus alone is not enough.

When the marketplace crosses 50 skills, choose which pattern fits before adding more — adding past the knee without a scaling plan turns description-tuning into a treadmill.

### Cross-platform behavior

The thresholds and warnings above are Claude-Code-specific. Other agentskills.io-compatible runtimes implement the same progressive-disclosure pattern but diverge sharply on budget, warnings, and disable mechanisms. If the marketplace ships to multiple runtimes, the lowest-common-denominator constraint applies:

| Runtime | Default budget | Truncation warning | Disable mechanism | Practical ceiling (default settings) |
|---|---|---|---|---|
| **Claude Code** (v2.1.105+) | **1% of context** (≈2,000 tokens / ≈8,000 chars at 200K; scales to 10,000 tokens at 1M) — default `0.01` introduced with the setting in v2.1.105 per `code.claude.com/docs/en/settings`; claudefa.st's v2.1.129 binary extraction first publicly documented the knob | Startup warning + `/doctor` breakdown + `/context` percentage line | `/skills` → disable per-skill; disabled skills don't count against the budget | ~15–25 skills before warning at 200K (~75–125 at 1M); recency + frequency selection protects actively-used skills past that |
| **Claude Code** (v2.1.32–v2.1.104; implicit 2% scaling pre-setting) | **2% of context** (implicit scaling formula, no user-tunable setting) — per v2.1.32 CHANGELOG entry "Skill character budget now scales with context window (2% of context)" | Same signals (added in subsequent releases) | `/skills` → disable (when added) | ~30–50 skills before warning at 200K |
| **Cursor** | No documented character budget; skills without `paths:` or nested-directory scoping are surfaced globally; skills with `paths:` or nested-directory location are scoped per-query | N/A (no catalog-wide budget) | `disable-model-invocation: true` per skill; or omit the skill from the catalog directory entirely | Catalog size not the bottleneck; per-query relevance is |
| **OpenAI Codex CLI** (current docs, v0.142+ post June 2026) | **2% of context, with an 8,000-character fallback when the context window is unknown** (per Codex skills docs — the 8,000-char figure is the floor, not the operative number; at 200K context, 2% = ≈4,000 chars, *less* than the fallback); issue `openai/codex#24299` reported 5,440 chars against v0.133.0 — model-specific calc, not the spec | "Codex may omit some skills from the initial list and **show a warning**" (Codex docs); per-skill log evidence is at `~/.codex/log/codex-tui.log` per issue #24299 from v0.133.0, not re-confirmed in current docs | `[[skills.config]]` block in `~/.codex/config.toml` with `enabled = false` per skill (user-side, config-file edit + restart); skill authors can set `policy.allow_implicit_invocation = false` in the skill's `agents/openai.yaml` for explicit-only invocation | **~20–25 skills before omission warning** at the 8,000-char fallback budget; **progressive disclosure IS supported** — full SKILL.md loads only when the skill is invoked, so bodies don't count against the budget (only descriptions + paths do) |
| **Microsoft Agent Framework** | ~100 tokens per skill in the advertise block (provider-controlled, per research note) | N/A (library, not CLI) | `FilteringSkillsSource` programmatic filter, applied at agent construction | Provider-controlled; 2-level discovery depth caps the natural directory walk |
| **kimi-code** | No documented character budget | None documented | No per-skill disable; ships `sub-skill.review` / `sub-skill.consolidate` builtins (introduced v0.11.0 / 2026-06-05, default-on since v0.12.0 / 2026-06-09) to consolidate the catalog at the source rather than suppress individual skills | Ships consolidation primitives but no formal budget — the scaling problem is acknowledged but not yet formalized |

**Practical implication for cross-runtime marketplaces.** If the marketplace targets both Claude Code and Codex, Codex is the binding constraint on absolute budget (~8,000-char fallback vs Claude Code's ~8,000 chars at 200K context — both roughly 1–2% of context, but Codex counts chars while Claude Code counts tokens × 4 chars/token). However, both runtimes now support **progressive disclosure** (full SKILL.md bodies load on-demand, not eagerly), so **Pattern 2 (tool-facade hub) IS viable on both** if hubs are modeled as top-level skills with the Skill tool. The difference is one of degree:

- Claude Code: hub description budget = ≈8,000 chars at 200K ÷ ~200 chars/hub description = **~40 hubs** before warning fires. Recency + frequency selection further protects actively-used hubs. At 1M context the budget grows to ~40,000 chars ≈ ~200 hubs.
- Codex: hub description budget = 8,000 chars ÷ ~200 chars/hub description = ~40 hubs before omission warning fires.

So for a marketplace targeting both, the binding constraint is the **hub count** (≤40 for both runtimes at 200K context; Claude Code becomes more permissive at 1M context). Codex's `[[skills.config]]` config-file disable mechanism works but is **less convenient than Claude Code's runtime `/skills` toggle** (config edit + restart vs immediate).

Pattern 1 (in-place tightening, keep flat catalog ≤ 20 skills) remains the simplest cross-runtime strategy, but is no longer the *only* viable strategy on Codex. Pattern 2 (hub-and-sub-skill, where hubs are top-level skills and sub-skills are loaded via the Skill tool) works on both runtimes with the hub-count constraint above.

**Research audit trail.** The current section's facts about Claude Code's budget system evolved significantly between May and June 2026 (default lowered from implicit 2% scaling to explicit 1% via `skillListingBudgetFraction`; truncation is no longer silent; selection is recency + frequency). The audit trail is at `research/claude-code-skill-budget-evolution.md`. The error was in the AGENTS.md integration layer that misread the v2.1.32 CHANGELOG line as a default change rather than the prior implicit scaling formula; the upstream `research/marketplace-routing-scaling/final.md` was already correct at 1% / 8,000 chars. The cross-platform comparison above is itself research-tracked at `research/cross-platform-skill-budget-comparison.md` (May–Jun 2026).

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
