# Document

Deep-research evidence base for the marketplace-routing-scaling question. Each section is one sub-question from `research_plan.md`. Citations are inline; sources are also indexed at the bottom.

---

## Q1 — Curve shape: linear, knee, or sigmoidal?

**Verified findings:**

- **Per-skill name+description cost is roughly linear in skill count.** Klymentiev measured the index cost at "roughly 50 tokens per skill name+description" for the Anthropic-curated corpus. His explicit table: 100 skills → ~5K tokens (2.5% of 200K context); 500 → ~25K (12.5%); 1,000 → ~50K (25%); 2,000 → ~100K (50%); 4,000 → ~200K (will not fit). [source: Klymentiev, "How does an AI agent pick from 686 skills in a second?" (klymentiev.com, 23 May 2026)](https://klymentiev.com/blog/claude-skills-semantic-router)
- **Attention quality degrades long before the linear-token cap.** Same source: "Even when the catalog physically fits, attention quality on a long list of similar items degrades. Past about 1,000 entries the agent starts making wrong picks on hand-eye-distinguishable cases." No saturated plateau — degradation is continuous. [source: Klymentiev (same URL above)](https://klymentiev.com/blog/claude-skills-semantic-router)
- **The Anthropic specification also confirms a per-tier token budget** (catalog ~50-100 tokens/skill, body up to 5,000 tokens, resources "unlimited") — i.e. the cost is a per-skill-fixed overhead, supporting linearity. [source: inventorsoft.co, "How to Teach Your AI Agent to Work by Your Standards" (4 May 2026)](https://inventorsoft.co/blog/agent_skills_how_to_teach_ai_agent_to_work_by_your_standards)
- **Claude Code's 1% budget rule means ~40-50 skills is the practical cap with default 200-char descriptions** (~10 skills with 500-char descriptions). A 200K-context model with `skillListingBudgetFraction = 0.01` gets an 8,000-char listing. [source: Anthropic Claude Code Docs — Extend Claude with skills (code.claude.com)](https://code.claude.com/docs/en/skills)
- **SkillRouter's 80K-skill benchmark shows body-removal collapses accuracy by 31-44pp** across BM25, encoder-only, and retrieve-and-rerank baselines. The collapse is a step-function of "do you have body or not," not a smooth degradation. [source: Zheng et al., SkillRouter arXiv:2603.22455v3, March 2026](https://arxiv.org/html/2603.22455v3)

**Interim verdict (Q1):** The curve is **piecewise linear with a hard knee at the context-budget cap, then continuous attention-quality degradation beyond ~1,000 skills**. Not sigmoidal (no plateau before catastrophic failure), not smoothly linear (the knee at the budget cap is sharp — silent truncation from "fits" → "truncate" → "names-only" mode, a 4-step function per Anthropic's `formatCommandsWithinBudget`).

## Q2 — Knee location in practice

**Verified findings:**

- **Anthropic's binary-analysis-documented four modes:** "fits" (all descriptions fit), "priority" (low-priority descriptions removed), "truncate" (descriptions uniformly shortened), "names-only" (descriptions removed entirely when over budget). The default `skillListingBudgetFraction = 0.01` produces an 8,000-char cap. Real-world impact table: `ai-video-pipeline` 25 skills × ~490 chars each = 12,274 chars (153% over budget → silent truncation). [source: GitHub issue anthropics/claude-code#64606 (2 June 2026)](https://github.com/anthropics/claude-code/issues/64606)
- **Practitioner floor — 7-8 skills:** "Around skill seven or eight, things get weird. Claude starts ignoring a skill that obviously applies. Or worse, it picks the wrong one and confidently runs the wrong playbook for ten minutes before you notice." [source: PromptSpace, "Smart Routing" (25 May 2026)](https://www.promptspace.in/blog/smart-routing-let-ai-pick-right-skill)
- **OpenClaw hard cap:** "Limit active skills to 10 per agent to avoid context window dilution and instruction confusion." This is the closest documented hard count limit I could find. [source: Skywork/ClawHub guide (25 April 2026)](https://skywork.ai/slide/en/clawhub-openclaw-skill-marketplace-2047575736827637761)
- **Cursor's always-apply budget:** "Total always-apply: TARGET < 5,000 tokens" — Cursor imposes a soft budget on always-on rules separately from the skill listing. [source: create-rules Cursor skill (lobehub.com)](https://lobehub.com/skills/dmitryprg-ai-cursor-develop-autorules-create-rules)
- **Microsoft Agent Framework:** Discovery is "up to two levels deep" — architectural cap on directory nesting. [source: Microsoft Agent Framework — Agent Skills docs](https://learn.microsoft.com/en-us/agent-framework/agents/skills)
- **tachyon-beep/skillpacks:** "With many plugins installed (5+), you may hit skill discovery context limits. In this case, use slash commands for routers and direct invocation for specialized skills." The 5+ threshold is empirical, not documented as a hard cap. [source: tachyon-beep/skillpacks README](https://github.com/tachyon-beep/skillpacks)
- **SkillReducer's missing-description baseline:** 26.4% of 55,315 wild skills lack routing descriptions entirely; 44.1% are missing or under 20 tokens. Description *quality*, not count, is the binding constraint. [source: Gao et al., SkillReducer arXiv:2603.29919 (31 March 2026)](https://arxiv.org/abs/2603.29919)

**Interim verdict (Q2):** The knee is **range-dependent, not point-sharp**. Three regimes:

- **~5-15 skills:** The Anthropic default starts truncating at ~16-50 skills depending on description length. OpenClaw's "limit to 10 per agent" matches this range. Practitioners first observe wrong-pick symptoms in this range (PromptSpace).
- **~50-100 skills:** The Anthropic `skillListingBudgetFraction = 0.01` cap is fully exhausted. Users hitting this range report silent skill-list truncation (Claude Code bug #64606).
- **~1,000+ skills:** The Klymentiev empirical "agent starts making wrong picks" threshold. Beyond this, even with full body access, attention quality degrades.

The pragmatic recommendation: **20-40 skills per session** is the sweet spot, **100-200 is the practical ceiling** with default settings, **>1,000 requires external routing**.

## Q3 — Claude Code's skill routing budget

**Verified findings:**

- **Default settings** (Claude Code v2.1.159, validated against the binary schema by dsebastien.net 2 June 2026):
  - `skillListingBudgetFraction` = 0.01 (1% of context, in characters)
  - `skillListingMaxDescChars` = 1,536 (per-skill cap)
  - `SLASH_COMMAND_TOOL_CHAR_BUDGET` env var overrides both, taking a raw character count
  - Combined text per skill is capped at 1,536 chars regardless of the global budget. [source: codewithmukesh, "Skills in Claude Code" (23 May 2026)](https://codewithmukesh.com/blog/skills-claude-code/)
- **Anthropic's own docs (the canonical source, code.claude.com/docs/en/skills):**
  - "All skill names are always included, but if you have many skills, descriptions are shortened to fit the character budget"
  - "The budget scales at 1% of the model's context window"
  - "When it overflows, descriptions for the skills you invoke least are dropped first, so the skills you actually use keep their full text"
  - Mitigation: raise `skillListingBudgetFraction` (e.g. 0.02 = 2%), set `SLASH_COMMAND_TOOL_CHAR_BUDGET`, or mark low-priority entries as `"name-only"` via `skillOverrides`. [source: Anthropic Skills docs (English, Japanese, Korean, Russian, Traditional Chinese)](https://code.claude.com/docs/en/skills)
- **The "old" pre-v2.1.105 behavior:** every skill survived but descriptions got shorter (250 char cap initially, raised to 1,536 in v2.1.86). The "new" v2.1.105+ behavior: every description stays full but low-use skills disappear entirely. For 5-10 skills both are equivalent; for 50+ the new approach is strictly better. [source: claudefa.st, "Claude Code's Hidden Skill Budget Setting" (14 June 2026)](https://claudefa.st/blog/guide/mechanics/skill-listing-budget). Note: claudefa.st places this split at v2.1.128/v2.1.129 based on binary analysis, but Anthropic docs (`code.claude.com/docs/en/settings`) mark the setting's min-version as v2.1.105. The marketplace chose v2.1.105 as authoritative; see `research/claude-code-skill-budget-evolution.md` §"Source tension on the v2.1.105 vs v2.1.129 introduction date" for the resolution rationale.
- **No literal "8 skills per request" limit in the Anthropic docs.** I searched Anthropic's docs (English + 5 translations), the GitHub issues, the binary schema, and 3 third-party deep-dives. The closest documented hard cap is OpenClaw's "limit active skills to 10 per agent." Claude Code's constraint is character-budget, not count-budget.

**Interim verdict (Q3):** Claude Code's budget is **character-based, not count-based**, defaults to 1% of context (~8,000 chars at 200K), and degrades in 4 explicit modes. **The "8-per-request" framing is not Anthropic-specific.** The closest documented hard-cap-as-count rule is OpenClaw's 10-per-agent recommendation.

## Q4 — Cursor's skill discovery

**Verified findings:**

- **Discovery flow** (5 steps): scan directories → present skills to agent → agent evaluates against descriptions → matches user intent → loads relevant skill into context. Skills can also be invoked manually via `/skill-name` (bypass). [source: Agentic Thinking, "How Cursor Finds Skills" (27 January 2026)](https://agenticthinking.ai/blog/skill-discovery/)
- **Directory scan order** (highest priority first): `.cursor/skills/` (project) → `.claude/skills/` (project, legacy) → `.codex/skills/` (project, legacy) → `~/.cursor/skills/` (user) → `~/.claude/skills/` (user) → `~/.codex/skills/` (user). [source: hutchic/.cursor, cursor-skills.md](https://github.com/hutchic/.cursor/blob/main/docs/cursor-skills.md)
- **Cursor rules budget** (separate from skills): always-apply tokens target < 5,000. File-specific rules use globs; agent-decides rules use description only. [source: create-rules Cursor skill](https://lobehub.com/skills/dmitryprg-ai-cursor-develop-autorules-create-rules)
- **Cursor's "dynamic context discovery" technique:** Cursor's blog claims selective MCP tool loading cut token usage by 46.9% in MCP scenarios. Skills are one of the 5 techniques (skill-loading is on-demand). [source: ZenML database, "Dynamic Context Discovery for Production Coding Agents" (2026)](https://www.zenml.io/llmops-database/dynamic-context-discovery-for-production-coding-agents)
- **Compaction persistence:** Cursor re-attaches most-recently-invoked skills automatically after compaction, with a 25,000-token budget. [source: wonderbird/ai-agent-workspace ADR-001](https://github.com/wonderbird/ai-agent-workspace/blob/main/docs/architecture-decisions/001-ai-rule-adherence-strategy.md)
- **No documented hard count cap.** Cursor's budget model is the same as Claude Code's (token-budget driven), but in practice less aggressive because Cursor splits rules (always-apply) from skills (on-demand). The 5,000-token always-apply budget is orthogonal to skill count.

**Interim verdict (Q4):** Cursor's model is **progressive disclosure with directory-scoped sharding**. Hard cap = always-apply token budget (5,000 tokens), not a skill count. Skill count cap is implicit (limited by the Claude Code / Anthropic-compatible system-prompt budget when skills descriptions get bundled).

## Q5 — Codex, kimi-code, Microsoft Agent Framework

**Verified findings:**

- **Codex:** "Plugins not skills" — Codex uses Codex plugins (`codex plugin add`/`remove`). The runtime does not yet support the Agent Skills standard natively. [source: own runtime-adapters.md, which documents this in the marketplace](file:///Users/felix/Documents/AutoPluginClaw/taches-principled-light/skills/evaluating-skills/references/runtime-adapters.md)
- **kimi-code:** `--skills-dir <dir>` flag replaces the discovered skills dirs for a given run. MoonshotAI's kimi-cli repository has a `--skills-dir` flag (PR #1626 updated the help text). No documented character or count budget beyond what's inherited from the underlying model. [source: MoonshotAI/kimi-cli PR #1626 (29 March 2026)](https://github.com/MoonshotAI/kimi-cli/actions/runs/23698152026)
- **Microsoft Agent Framework:** `AgentSkillsProvider` scans **2 levels deep** for `SKILL.md` files, injects skill names+descriptions into the system prompt, exposes `load_skill` and `read_skill_resource` tools. Resources recognized by extension (`.md`, `.json`, `.yaml`, etc.) and limited to `references/` and `assets/` subdirectories by default. [source: Microsoft Agent Framework docs](https://learn.microsoft.com/en-us/agent-framework/agents/skills)
- **MAF's `load_skill` design:** The agent decides (via description matching) which skills to load, then explicitly calls `load_skill` for the chosen one. This is the same progressive-disclosure shape as Claude Code / Cursor / SkillReducer. [source: Microsoft devblog "Give Your Agents Domain Expertise" (4 March 2026)](https://devblogs.microsoft.com/agent-framework/give-your-agents-domain-expertise-with-agent-skills-in-microsoft-agent-framework/)
- **No count limits** documented for any of the three. Codex & kimi-code inherit the underlying model's character budget; MAF's 2-level directory depth is the architectural ceiling, not a count.

**Interim verdict (Q5):** **All three platforms implement the same progressive-disclosure shape.** They differ on (a) how aggressively they shard the directory (MAF enforces 2-level depth; Claude Code / Cursor do not), (b) whether the runtime natively understands the SKILL.md spec (Claude Code / Cursor / MAF yes; Codex no; kimi-code partial via `--skills-dir`).

## Q6 — Scaling patterns beyond 8 (and beyond 100)

**Verified findings:**

- **Pattern 1 — Tighten descriptions.** SkillReducer's Stage 1 achieved 48% mean description-token reduction on 600 skills with a +2.8% functional quality *gain* (the less-is-more effect). Source: arXiv:2603.29919. This scales a marketplace with default 200-char descriptions from ~40 skills to ~80 skills without changing the budget. [source: Gao et al., SkillReducer (31 March 2026)](https://arxiv.org/abs/2603.29919)
- **Pattern 2 — Slash-command workaround.** tachyon-beep's pattern: pack 200+ skills into 38 packs; use slash commands for router skills that are too big for the listing, and direct invocation for specialized skills after the router guides you. [source: tachyon-beep/skillpacks README](https://github.com/tachyon-beep/skillpacks)
- **Pattern 3 — On-demand tool facade.** Skill Hub exposes 200+ local skills to the LLM as **14 lightweight tool definitions** (search, load, list, etc.); the LLM queries the registry on demand rather than holding the full listing in context. Reduces token overhead by separating "what's available" from "what's loaded." [source: Skill Hub listing (mcpmarket.com)](https://mcpmarket.com/server/skill-hub-1)
- **Pattern 4 — External retrieve-and-rerank.** SkillRouter (Alibaba, arXiv:2603.22455v3): 1.2B-parameter compact pipeline (0.6B encoder + 0.6B reranker) achieves 74.0% Hit@1 on an 80K-skill benchmark, matching the strongest 16B base pipeline at 5.8× lower latency. Critical training adaptations: false-negative filtering + listwise reranking loss. [source: Zheng et al., SkillRouter (31 March 2026)](https://arxiv.org/html/2603.22455v3)
- **Pattern 5 — Semantic router (embeddings).** Klymentiev's empirical demonstration: embed all 686 skill names+descriptions once; at task time, run a single semantic-search call against the task, get top-5 candidates, pick one, read full body only for the chosen one. Token cost per turn is **constant regardless of catalog size**. [source: Klymentiev (23 May 2026)](https://klymentiev.com/blog/claude-skills-semantic-router)
- **Pattern 6 — Reduce token cost per skill (SkillReducer Stage 2).** Body compression (39% mean reduction) and reference deduplication; mean body drop from 359K → 84K tokens across SkillsBench (75% per-task reduction). [source: SkillReducer arXiv:2603.29919](https://arxiv.org/abs/2603.29919)

**Interim verdict (Q6):** **Three viable scaling patterns** emerged from the evidence:

1. **In-place:** Tighten descriptions (Pattern 1) + slash commands for big routers (Pattern 2). Effective up to ~100 skills.
2. **On-demand facade:** Skill Hub's tool-based registry (Pattern 3) — effective to ~200-500 skills.
3. **External retrieval:** SkillRouter's compact 1.2B reranker (Pattern 4) or Klymentiev's semantic router (Pattern 5) — scales to 80K+ skills.

Each pattern has a cost: Pattern 1 requires description-iteration discipline; Pattern 2 requires manual slash-command invocation; Pattern 3 requires a stable registry layer; Patterns 4-5 require running an external model.

## Q7 — The "8-per-request" claim

**Verified findings:**

- **No Claude Code source documents "8 skills per request" as a limit.** I searched Anthropic's English + 5 translation skills docs, the GitHub issues, the binary schema, and 4 third-party deep-dives. The constraint is character-based (8,000 chars at 200K context with `skillListingBudgetFraction = 0.01`), not count-based.
- **The closest documented hard-cap-as-count rule is OpenClaw's "limit active skills to 10 per agent."** This is from the Skywork/ClawHub guide, not Anthropic. [source: Skywork (25 April 2026)](https://skywork.ai/slide/en/clawhub-openclaw-skill-marketplace-2047575736827637761)
- **Other plausible origins of "8":**
  - Anthropic's tool-use slots are typically ~5-10 per session, but that's a separate constraint (tool definitions, not skill listings).
  - The SkillRouter paper's experiments used 80K skills but reports per-query top-1, top-10, etc. — not 8.
  - Microsoft Agent Framework's 2-level depth discovery is *not* a count limit either.

**Interim verdict (Q7):** **The "8-per-request" framing does not appear in Anthropic documentation.** It may be a misremembering of OpenClaw's "10-per-agent" rule, or a different platform's limit. The Claude Code constraint is character-based; the user's premise should be re-grounded as "**~16-50 skills per session depending on description length**" rather than a literal count of 8.

---

## Synthesis

**Three findings that together answer both parts of the question:**

1. **The curve is piecewise-linear with a knee at the context budget, not sigmoidal.** With Claude Code's default `skillListingBudgetFraction = 0.01`, the budget is 1% of context window in characters (8,000 chars at 200K). A skill's description averages 200-500 chars; that gives a practical cap of ~16-50 skills per session. Past the cap, the failure mode is the 4-step `formatCommandsWithinBudget` function: fits → priority → truncate → names-only. Beyond ~1,000 skills, attention quality degrades continuously even with full body access (Klymentiev). [Klymentiev 2026](https://klymentiev.com/blog/claude-skills-semantic-router), [Anthropic bug #64606](https://github.com/anthropics/claude-code/issues/64606)

2. **The "8-per-request" claim is not grounded in Claude Code documentation.** The closest documented count cap is OpenClaw's "limit active skills to 10 per agent." Claude Code, Cursor, Codex, kimi-code, and Microsoft Agent Framework all implement progressive disclosure with character-based budgets — none imposes a hard count of 8 (or any other specific number). The user's premise should be reformulated as "**what happens past the budget?**" rather than "what happens past 8?"

3. **Three scaling patterns cover the range from 50 to 80,000 skills.** In-place (description tightening + slash commands) works to ~100; on-demand tool facades (Skill Hub, Klymentiev's semantic router) work to ~500; external retrieve-and-rerank (SkillRouter's 1.2B pipeline) scales to 80K. The recommendation shift from "add skills" to "consolidate or shard" happens at ~50-100 skills per session; the recommendation shift to "external routing" happens at ~1,000. [SkillReducer arXiv:2603.29919](https://arxiv.org/abs/2603.29919), [SkillRouter arXiv:2603.22455v3](https://arxiv.org/html/2603.22455v3)

## Open questions

Things a primary source or a controlled experiment would settle:

1. **The exact shape of the degradation curve from 100-1,000 skills.** Klymentiev measured a few data points (50, 100, 200, 500, 1,000) and reports "degradation starts around 1,000," but no published study has fitted a parametric curve (logistic, exponential decay, piecewise) to per-N accuracy data.
2. **Vendor-specific per-platform routing accuracy.** SkillRouter's 80K benchmark is built on SkillsBench + a synthetic pool. Real-world Claude Code / Cursor / kimi-code routing accuracy at marketplace sizes >100 is undocumented in the literature.
3. **The "8 skills per request" claim origin.** Could be a misremembering, could be a closed Anthropic design note, could be from a third-party product. Worth one targeted ask on the Anthropic forum or a search of GitHub Discussions.
4. **Long-context model behavior.** Anthropic Claude Sonnet 4.6, GPT-5.5, and DeepSeek V4-Flash all have 200K+ context windows. Whether the ~1,000-skill attention threshold holds for 1M-context models (or scales linearly) is untested.
5. **SkillReducer adoption.** Stage 1 (description compression) is build-time, no runtime cost. Stage 2 (body compression) requires the agent to follow routing metadata. How often does the agent actually load the right reference file at runtime? A follow-up study measuring runtime hit rate would close this gap.