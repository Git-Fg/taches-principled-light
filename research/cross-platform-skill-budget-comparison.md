# Cross-Platform Skill Budget Comparison (May–Jun 2026)

This note captures the cross-platform comparison that the AGENTS.md → Marketplace Scaling → "Cross-platform behavior" subsection references. It is the audit trail for the actionable finding: **Codex is the binding constraint for cross-runtime marketplaces**, not Claude Code.

## Snapshot date

2026-06-24. Source versions: Claude Code v2.1.159+ (with the 2% budget added in subsequent releases), Cursor docs (current, ~v2.4), OpenAI Codex CLI v0.133.0 (released May 2026), Microsoft Agent Framework (current docs), kimi-code v0.19.1 (released 2026-06-23).

## Summary table

| Runtime | Default budget | Truncation warning | Disable mechanism | Practical ceiling |
|---|---|---|---|---|
| Claude Code (current) | 2% (~16,000 chars at 200K) | Startup + /doctor + /context | /skills → disable | ~30–50 skills before warning |
| Claude Code (pre-v2.1.129) | 1% (~8,000 chars) | Same signals (added later) | /skills → disable | ~15–25 skills |
| Cursor | None documented (path-scoped) | N/A | disable-model-invocation: true | Catalog size not the bottleneck |
| OpenAI Codex CLI | 5,440 chars (~2%) | Not observed in v0.133.0 (only log file) | No exclude config | ~20 skills before mass truncation |
| Microsoft Agent Framework | ~100 tokens per skill advertise | N/A (library, not CLI) | FilteringSkillsSource programmatic | 2-level discovery depth |
| kimi-code | None documented | None documented | No per-skill disable; ships consolidation builtins | No formal budget |

## Critical finding: Codex is the binding constraint

The single most actionable finding from this cross-platform survey: **for marketplaces targeting both Claude Code and Codex, Codex's 20-skill ceiling is the binding constraint, not Claude Code's 30-50 skill ceiling.**

Three Codex-specific properties make it the binding constraint:

1. **Lower absolute ceiling**: 5,440 chars at ~232 chars/skill description = ~23 skills before the budget kicks in (vs Claude Code's 16,000 chars ÷ ~450 chars = ~35 skills). The Codex issue reports 103 of 119 descriptions truncated at 119 skills, which is 86% mass truncation at less than 2× the budget.

2. **No disable mechanism**: Unlike Claude Code's `/skills` → disable, Codex has no per-skill or per-directory exclude config. `~/.codex/skills/.system/` skills (imagegen, plugin-creator, skill-creator, skill-installer, openai-docs) auto-restore on every launch and cannot be permanently removed. So the "disable rarely-used skills" advice that works on Claude Code does not apply.

3. **Eager multi-directory loading**: Codex scans `~/.codex/skills/`, `~/.codex/skills/.system/`, and `~/.agents/skills/` with no filter. All discovered skills are unconditionally added to the budget pool. This means a 14-router hub with 196 sub-skills still produces 210 loaded skills, with 196 descriptions truncated to ~46 chars each — effectively undiscoverable.

## Implication for Pattern selection

The three scaling patterns from AGENTS.md → Marketplace Scaling are tested against each platform:

### Pattern 1 (In-place tightening, ≤100 skills)

- **Claude Code**: works. SkillReducer compression extends the budget by ~48%.
- **Cursor**: irrelevant; no catalog-wide budget.
- **Codex**: the **only viable strategy** if the marketplace ships to Codex. Keep the flat catalog ≤ 20 skills. Any Pattern 2/3 work on Codex requires verifying sub-skill support, which is not documented.
- **Microsoft Agent Framework**: applicable at the `FilteringSkillsSource` level.
- **kimi-code**: applicable if the marketplace owner commits to running `sub-skill.consolidate`.

### Pattern 2 (Tool-facade hub, ~200-500 skills)

- **Claude Code**: works (the design target).
- **Cursor**: irrelevant; per-query relevance is the model.
- **Codex**: **not yet verified** whether the agentskills.io spec supports on-demand sub-skill loading. The Codex issue shows flat eager loading; if this is structural, Pattern 2 does not help on Codex at any size.
- **Microsoft Agent Framework**: works via `AggregatingSkillsSource` + `FilteringSkillsSource` composition.
- **kimi-code**: the `sub-skill` builtin bundle (v0.11.0+, default-on since v0.12.0) is a primitive for this exact pattern.

### Pattern 3 (External retrieval, ≥500 skills)

- **Claude Code**: works (SkillRouter, etc.).
- **Cursor**: irrelevant; per-query model.
- **Codex**: not applicable at any size given the 20-skill ceiling.
- **Microsoft Agent Framework**: works via custom context providers.
- **kimi-code**: not yet formalized.

## Cross-platform marketplace strategy

For marketplaces that ship to multiple runtimes, the practical decision tree is:

1. **If Codex is in scope**: bound the catalog at ~20 skills (Pattern 1 only). Sub-skills, hubs, and external retrieval do not help if Codex loads eagerly.
2. **If Claude Code + MAF + kimi-code are in scope but not Codex**: Claude Code is the binding constraint. Pattern 1 ≤ 100, Pattern 2 at 200-500, Pattern 3 at 500+.
3. **If Cursor is in scope**: Cursor is not a constraint; per-query `paths:` scoping handles relevance. The marketplace can scale freely on Cursor.
4. **kimi-code**: ships the consolidation primitives; if the marketplace owner commits to running `sub-skill.consolidate` periodically, the catalog can grow beyond the kimi-code soft limits. No hard budget to enforce.

## Open questions

1. **Does Codex support sub-skill discovery on demand?** The issue text shows flat eager loading; need to verify against the Codex loader spec.
2. **What happens on MAF when the advertise block exceeds the per-skill budget?** The `~100 tokens` figure is the per-skill cost; the cumulative limit is undocumented in the public MAF docs.
3. **Does Cursor's `paths:` glob have a budget cost at the catalog level?** Path-scoped skills are per-query relevant, but global skills (without `paths:`) still consume system prompt at startup.
4. **kimi-code's flat catalog ceiling**: the v0.11.0 consolidation builtin acknowledges a scaling problem but no formal budget is documented. What's the practical ceiling in practice?

## Sources

- Codex issue: https://github.com/openai/codex/issues/24299 (May 2026)
- Cursor skills docs: https://cursor.com/docs/skills
- Microsoft Agent Framework skills docs: https://learn.microsoft.com/en-us/agent-framework/agents/skills
- kimi-code changelog v0.7–v0.19.1: https://moonshotai.github.io/kimi-code/en/release-notes/changelog.html
- AGENTS.md → Marketplace Scaling (the source of truth for Claude Code budget facts)
- research/claude-code-skill-budget-evolution.md (the prior research note covering Claude Code's evolution)