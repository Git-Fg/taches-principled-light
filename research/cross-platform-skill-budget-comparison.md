# Cross-Platform Skill Budget Comparison (May–Jun 2026)

This note captures the cross-platform comparison that the AGENTS.md → Marketplace Scaling → "Cross-platform behavior" subsection references. It is the audit trail for the actionable finding: **Codex is the binding constraint on absolute budget, but the mitigation strategy is similar to Claude Code** (Pattern 2 hub-and-sub-skill works on both, with different hub-count ceilings).

## Snapshot date

2026-06-24. Source versions: Claude Code v2.1.159+ (with the 2% budget added in subsequent releases), Cursor docs (current, ~v2.4), OpenAI Codex CLI docs (current snapshot, v0.137+ post May 2026), Microsoft Agent Framework (current docs), kimi-code v0.19.1 (released 2026-06-23).

## Correction history

This note supersedes the version committed in `1a39f71`. Three claims in the prior version were wrong (sourced from issue `openai/codex#24299` against v0.133.0, May 2026):

1. **Codex budget**: prior claim "5,440 chars hard budget (~2%)" was a model-specific calc by the issue author, not the spec. The official Codex skills docs state "8,000 characters when the context window is unknown" or 2% of the model's context window.
2. **Codex disable mechanism**: prior claim "no exclude config" was incorrect. The Codex docs document `[[skills.config]]` blocks in `~/.codex/config.toml` with `enabled = false` per skill. The mechanism is **less convenient than Claude Code's runtime `/skills` toggle** (config edit + restart vs immediate runtime toggle), but it exists.
3. **Codex warning visibility**: prior claim "truncation message documented only in the log file" was incomplete. The Codex docs state "Codex may omit some skills from the initial list and show a warning" — there IS a user-visible warning signal, in addition to the log file.
4. **Codex progressive disclosure**: prior claim "eager flat loading" was partially incorrect. The Codex docs state "Codex starts with each skill's name, description, and file path. Codex loads the full SKILL.md instructions only when it decides to use a skill." Bodies load on-demand; only descriptions + paths are in the budget pool.

The corrected understanding: Codex's UX is closer to Claude Code's than the issue suggested. Pattern 2 (hub-and-sub-skill) is viable on both. The differences are quantitative, not qualitative:

- Claude Code: ~16,000 chars (~80 hubs at ~200 chars each) before warning
- Codex: ~8,000 chars (~40 hubs at ~200 chars each) before omission warning
- Codex disable: config file + restart, not runtime toggle
- Codex selection: no documented recency + frequency protection (Codex docs do not mention frequency-based selection)

## Summary table (corrected)

| Runtime | Default budget | Truncation warning | Disable mechanism | Practical ceiling |
|---|---|---|---|---|
| Claude Code (current) | 2% (~16,000 chars at 200K) | Startup + /doctor + /context | /skills → disable (runtime toggle) | ~30–50 skills before warning; recency + frequency selection protects actively-used skills |
| Claude Code (pre-v2.1.129) | 1% (~8,000 chars) | Same signals (added later) | /skills → disable | ~15–25 skills |
| Cursor | None documented (path-scoped) | N/A | disable-model-invocation: true | Catalog size not the bottleneck |
| OpenAI Codex CLI | 8,000 chars (or 2% context) | Omission warning shown to user; per-skill log message in `~/.codex/log/codex-tui.log` | `[[skills.config]]` block in `~/.codex/config.toml` with `enabled = false` per skill; `allow_implicit_invocation = false` for explicit-only | ~20–25 skills before omission; progressive disclosure IS supported (bodies load on-demand) |
| Microsoft Agent Framework | ~100 tokens per skill advertise | N/A (library, not CLI) | FilteringSkillsSource programmatic | 2-level discovery depth |
| kimi-code | None documented | None documented | No per-skill disable; ships consolidation builtins | No formal budget |

## Critical finding (corrected): Codex is the binding constraint on absolute budget, not on pattern choice

The single most actionable finding from this cross-platform survey: **for marketplaces targeting both Claude Code and Codex, Codex's 8,000-char budget is the binding absolute constraint, but Pattern 2 (hub-and-sub-skill) is viable on both runtimes with the constraint applied as a hub-count ceiling, not a flat skill ceiling.**

Three Codex properties (CORRECTED from the prior version):

1. **Lower absolute description budget**: 8,000 chars (or 2% context) vs Claude Code's 16,000 chars (or 2% context, but counted in tokens × 4 chars/token). For descriptions only, Codex has ~50% of Claude Code's budget. So a 40-hub marketplace with ~200-char descriptions fits in Codex but only barely; Claude Code allows 80 hubs.

2. **Config-file disable mechanism (not runtime)**: `[[skills.config]]` with `enabled = false` per skill. Less convenient than Claude Code's runtime `/skills` toggle, but functional. Cross-runtime marketplaces will need a CI/automation layer that writes both `~/.claude/settings.json` (or equivalent) AND `~/.codex/config.toml` to keep disable lists in sync.

3. **Progressive disclosure IS supported**: full SKILL.md bodies load only when the skill is invoked. Only descriptions + paths count against the budget. This means Pattern 2 (hub routers as top-level skills, sub-skills loaded via Skill tool) works on Codex — the hub descriptions count against the budget, but sub-skill bodies are on-demand.

## Implication for Pattern selection (corrected)

### Pattern 1 (In-place tightening, ≤100 skills)

- **Claude Code**: works. SkillReducer compression extends the budget by ~48%.
- **Cursor**: irrelevant; no catalog-wide budget.
- **Codex**: works. Keep the flat catalog ≤ 20 skills for safety. Beyond that, prefer Pattern 2.
- **Microsoft Agent Framework**: applicable at the `FilteringSkillsSource` level.
- **kimi-code**: applicable if the marketplace owner commits to running `sub-skill.consolidate`.

### Pattern 2 (Tool-facade hub, hub-count varies by runtime)

The hub-count ceiling differs by runtime (assuming ~200 chars per hub description):

- **Claude Code**: ~80 hubs before warning (16,000 / 200); with recency + frequency protection, actively-used hubs survive past that.
- **Codex**: ~40 hubs before omission warning (8,000 / 200). No documented frequency-based selection.
- **Cursor**: irrelevant; per-query relevance.
- **Microsoft Agent Framework**: works via `AggregatingSkillsSource` + `FilteringSkillsSource`.
- **kimi-code**: ships the `sub-skill` builtin (v0.11.0+, default-on since v0.12.0).

So for cross-runtime marketplaces, the binding Pattern 2 hub count is **≤40 (Codex)**.

### Pattern 3 (External retrieval, ≥500 skills)

- **Claude Code**: works (SkillRouter, etc.).
- **Cursor**: irrelevant.
- **Codex**: applicable if hub count exceeds 40; the external retrieval layer replaces the in-process hub router.
- **Microsoft Agent Framework**: works via custom context providers.
- **kimi-code**: not yet formalized.

## Cross-platform marketplace strategy (corrected)

For marketplaces that ship to multiple runtimes, the practical decision tree is:

1. **If Codex is in scope**: bound hub count at ≤40 (Pattern 2 ceiling). The disable mechanism requires a sync layer between Claude Code settings and Codex config.toml.
2. **If Claude Code + MAF + kimi-code are in scope but not Codex**: Claude Code is the binding constraint (~80 hubs).
3. **If Cursor is in scope**: Cursor is not a constraint; per-query `paths:` scoping handles relevance.
4. **kimi-code**: ships consolidation primitives; commit to running `sub-skill.consolidate` periodically.

## Open questions (updated)

1. **Codex selection logic**: does Codex have any analog to Claude Code's recency + frequency protection? The docs do not mention it, but absence-of-evidence. If Codex selection is purely positional or based on a fixed priority list, the safety margin for actively-used hubs may be lower than Claude Code's.
2. **MAF cumulative advertise budget**: the `~100 tokens` figure is per-skill; what's the cumulative limit?
3. **Cursor global-skill budget**: skills without `paths:` are surfaced globally — does this consume system prompt at startup?
4. **kimi-code flat catalog ceiling**: consolidation builtin acknowledges the problem but no formal budget.

## Sources

- Codex skills docs (current): https://developers.openai.com/codex/skills
- Codex changelog: https://developers.openai.com/codex/changelog
- Codex issue #24299 (May 2026, v0.133.0 snapshot — partially superseded): https://github.com/openai/codex/issues/24299
- Cursor skills docs: https://cursor.com/docs/skills
- Microsoft Agent Framework skills docs: https://learn.microsoft.com/en-us/agent-framework/agents/skills
- kimi-code changelog v0.7–v0.19.1: https://moonshotai.github.io/kimi-code/en/release-notes/changelog.html
- AGENTS.md → Marketplace Scaling (the source of truth for Claude Code budget facts)
- research/claude-code-skill-budget-evolution.md (the prior research note covering Claude Code's evolution)