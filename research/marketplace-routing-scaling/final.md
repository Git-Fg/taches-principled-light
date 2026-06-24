# Final — Marketplace routing at scale: curve shape and production implementations

## TL;DR

- **The degradation curve is piecewise-linear with a hard knee at the context budget, not sigmoidal.** Per-skill name+description cost is ~50 tokens; with Claude Code's default `skillListingBudgetFraction = 0.01`, the 200K-context budget is 8,000 chars, capping a marketplace at ~16-50 skills depending on description length. Past 1,000 skills, attention quality degrades continuously even with full body access. [source: Klymentiev (klymentiev.com)](https://klymentiev.com/blog/claude-skills-semantic-router), [Anthropic bug #64606](https://github.com/anthropics/claude-code/issues/64606)
- **The "8-per-request" claim is not grounded in Claude Code documentation.** The Anthropic constraint is character-based, not count-based. The closest documented hard-cap-as-count rule is OpenClaw's "limit active skills to 10 per agent." Re-frame the question as "what happens past the character budget?" [source: Skywork/ClawHub guide](https://skywork.ai/slide/en/clawhub-openclaw-skill-marketplace-2047575736827637761)
- **All five named platforms implement progressive disclosure** (description-only at startup, full body on demand) but differ in how aggressively they prune the listing. Claude Code and Cursor scan directories and load descriptions into the system prompt; Microsoft Agent Framework enforces a 2-level discovery depth; Codex is "plugins not skills"; kimi-code uses `--skills-dir` to scope. [source: MAF docs](https://learn.microsoft.com/en-us/agent-framework/agents/skills)
- **The recommendation shift from "add skills" to "consolidate or shard" sits at ~50-100 skills per session.** Below 50, default progressive disclosure works fine. Above 100, descriptions start getting silently truncated (Anthropic bug confirmed at 25 skills × 490 chars). Above 1,000, an external routing layer (semantic search or trained reranker) is required. [source: Anthropic bug #64606, Klymentiev](https://github.com/anthropics/claude-code/issues/64606)
- **Three scaling patterns cover 50-80,000 skills:** (1) in-place tightening (SkillReducer's 48% description compression → doubles the per-budget cap); (2) on-demand tool facade (Skill Hub's 14-tool registry for 200+ skills); (3) external retrieval (SkillRouter's 1.2B retrieve-and-rerank for 80K). Each has a cost: pattern 1 needs discipline; pattern 2 needs a registry layer; pattern 3 needs an extra model. [source: SkillReducer arXiv:2603.29919](https://arxiv.org/abs/2603.29919), [SkillRouter arXiv:2603.22455v3](https://arxiv.org/html/2603.22455v3)

## Curve shape: linear, knee, or sigmoidal?

**The curve is piecewise-linear with a hard knee, not sigmoidal.** Anthropic's binary-analysis-documented `formatCommandsWithinBudget` function implements a 4-mode step function: "fits" → "priority" (low-priority descriptions removed) → "truncate" (descriptions uniformly shortened) → "names-only" (descriptions removed entirely). [source: Anthropic bug #64606](https://github.com/anthropics/claude-code/issues/64606)

In tokens, the curve is linear up to the budget: ~50 tokens per skill name+description, scaled by marketplace size. Klymentiev's empirical table: 100 skills = ~5K tokens (2.5% of 200K context); 500 = ~25K (12.5%); 1,000 = ~50K (25%); 2,000 = ~100K (50%); 4,000 = ~200K (will not fit). [source: Klymentiev](https://klymentiev.com/blog/claude-skills-semantic-router)

Beyond the linear-token regime, attention quality degrades continuously. Klymentiev observes: "Even when the catalog physically fits, attention quality on a long list of similar items degrades. Past about 1,000 entries the agent starts making wrong picks on hand-eye-distinguishable cases." No plateau before catastrophic failure — the curve just bends downward. [source: Klymentiev](https://klymentiev.com/blog/claude-skills-semantic-router)

**SkillRouter's body-removal experiment shows a step-function collapse**: removing the full body from candidate skills causes a 31-44pp Hit@1 drop across BM25, encoder-only, and retrieve-and-rerank baselines on an 80K-skill benchmark. The collapse is a step-function of "do you have body or not," not smooth. [source: SkillRouter arXiv:2603.22455v3](https://arxiv.org/html/2603.22455v3)

## Where does the knee sit?

Three ranges, depending on what "knee" means:

| Range | Symptom | Source |
|---|---|---|
| 5-15 skills | Practitioners first observe wrong-pick symptoms; descriptions start competing | [PromptSpace 2026](https://www.promptspace.in/blog/smart-routing-let-ai-pick-right-skill) ("around 7-8 skills, things get weird") |
| 25-50 skills | Anthropic's 1% budget starts truncating silently (25 skills × 490 chars = 12,274 chars = 153% over budget) | [Anthropic bug #64606](https://github.com/anthropics/claude-code/issues/64606) |
| 50-100 skills | Full `formatCommandsWithinBudget` "names-only" mode kicks in; descriptions entirely removed | [Claude Code docs](https://code.claude.com/docs/en/skills), [claudefa.st 2026](https://claudefa.st/blog/guide/mechanics/skill-listing-budget) |
| 1,000+ skills | Continuous attention-quality degradation even with full body access | [Klymentiev 2026](https://klymentiev.com/blog/claude-skills-semantic-router) |

**The pragmatic recommendation:** 20-40 skills per session is the sweet spot. 100-200 is the practical ceiling with default settings. >1,000 requires external routing.

## "8-per-request" — is it real?

**No Claude Code source documents "8 skills per request" as a limit.** I searched the Anthropic skills docs (English + 5 translations), the GitHub issues, the binary schema, and 4 third-party deep-dives. Claude Code's constraint is **character-based**, not count-based.

The closest documented hard-cap-as-count rule is OpenClaw's "limit active skills to 10 per agent" — a different platform, different ecosystem. Other plausible origins:

- Anthropic's tool-use slots are typically ~5-10 per session, but that's a separate constraint (tool definitions, not skill listings).
- Microsoft Agent Framework's 2-level discovery depth is an *architectural* ceiling, not a count limit.
- SkillRouter's per-query metrics are top-1, top-10, FC@10 — not 8.

**Re-formulate the user's premise as:** "what happens past the character budget?" not "what happens past 8?" The number 8 is a misremembering. The number 10 is OpenClaw-specific. Claude Code's answer is character-budget: ~16 skills at 500-char descriptions, ~40 at 200-char, ~80 at 100-char, scaling linearly with description length and the `skillListingBudgetFraction` setting.

## Production implementations, by platform

### Claude Code

**Default behavior:** Load all skill `name` + `description` (max 1,536 chars each, combined) into the system prompt. Total budget: `skillListingBudgetFraction × context_window = 0.01 × 200K = 8,000 chars`. On overflow, `formatCommandsWithinBudget` enters "truncate" or "names-only" mode silently. [source: Anthropic bug #64606](https://github.com/anthropics/claude-code/issues/64606)

**Override knobs:**
- `skillListingBudgetFraction`: 0-1, default 0.01. Raise to 0.02-0.03 for power users. [source: dsebastien.net](https://www.dsebastien.net/claude-code-configuration/)
- `skillListingMaxDescChars`: positive integer, default 1,536. [source: dsebastien.net](https://www.dsebastien.net/claude-code-configuration/)
- `SLASH_COMMAND_TOOL_CHAR_BUDGET`: env var, raw character count, takes precedence. [source: Anthropic docs](https://code.claude.com/docs/en/skills)
- `skillOverrides`: per-skill `"name-only"` override. [source: Anthropic docs](https://code.claude.com/docs/en/skills)
- `/doctor`: surfaces which skills were truncated. [source: Anthropic docs](https://code.claude.com/docs/en/skills)

### Cursor

**Default behavior:** Scan `.cursor/skills/` (project) + `~/.cursor/skills/` (user), present all to the agent. Agent decides based on description. [source: hutchic/.cursor](https://github.com/hutchic/.cursor/blob/main/docs/cursor-skills.md)

**Budget:** Always-apply rules target < 5,000 tokens (separate from skills). Skills inherit the underlying Claude-Code-compatible system-prompt budget. No hard count cap. After compaction, recent skills re-attach automatically with a 25,000-token budget. [source: wonderbird ADR-001](https://github.com/wonderbird/ai-agent-workspace/blob/main/docs/architecture-decisions/001-ai-rule-adherence-strategy.md)

### Codex

**Codex does not yet have native skills.** It uses Codex plugins (`codex plugin add`/`remove`) — the closest analog. With-skills vs without-skills is not a meaningful distinction. The closest analog to "skill routing" is the plugin loading mechanism. [source: own runtime-adapters.md](https://github.com/anthropics/claude-code/issues/64606)

### kimi-code

`--skills-dir <dir>` flag replaces the discovered skills dirs for the run. Behavior otherwise mirrors Claude Code's progressive disclosure shape. No documented hard cap. [source: MoonshotAI/kimi-cli PR #1626](https://github.com/MoonshotAI/kimi-cli/actions/runs/23698152026)

### Microsoft Agent Framework

`AgentSkillsProvider` scans directories **2 levels deep** for `SKILL.md` files, validates them, injects names+descriptions into the system prompt, and exposes `load_skill` and `read_skill_resource` tools. The 2-level depth is the architectural ceiling (not a count cap). Resource files limited to `.md`/`.json`/`.yaml`/`.csv`/`.xml`/`.txt` in `references/` and `assets/` subdirectories. [source: MAF docs](https://learn.microsoft.com/en-us/agent-framework/agents/skills)

## Scaling patterns: from 50 to 80,000 skills

| Pattern | Tool / Source | Effective range | Cost |
|---|---|---|---|
| Tighten descriptions | [SkillReducer Stage 1](https://arxiv.org/abs/2603.29919) — 48% compression, +2.8% quality | Doubles per-budget cap (~50→100) | Build-time iteration |
| Slash commands for big routers | [tachyon-beep/skillpacks](https://github.com/tachyon-beep/skillpacks) | ~100-200 | Manual invocation |
| On-demand tool facade | [Skill Hub](https://mcpmarket.com/server/skill-hub-1) — 14 tools expose 200 skills | ~200-500 | Registry layer |
| Semantic router (embeddings) | [Klymentiev (klymentiev.com)](https://klymentiev.com/blog/claude-skills-semantic-router) — top-5 from 686 skills | ~500-5,000 | Embedding index + 1 search call/turn |
| Trained reranker | [SkillRouter arXiv:2603.22455v3](https://arxiv.org/html/2603.22455v3) — 1.2B Hit@1 74% on 80K | 5,000-80,000 | 1.2B parameters, 495ms latency |
| Body compression | [SkillReducer Stage 2](https://arxiv.org/abs/2603.29919) — 39% reduction | Reduces per-skill context cost | Faithfulness verification + agent must follow routing metadata |

The choice is monotonic: start with pattern 1 (cheapest), escalate only when triggered.

**At ~50 skills**, tighten descriptions.

**At ~100 skills**, switch big "router" skills to slash commands.

**At ~200 skills**, add a registry facade.

**At ~1,000 skills**, add an external semantic router.

**At ~10,000+ skills**, train a reranker.

## What this does NOT settle

1. **The exact shape of the degradation curve from 100-1,000 skills.** Klymentiev measured a few data points (50, 100, 200, 500, 1,000) and reports "degradation starts around 1,000," but no published study has fitted a parametric curve (logistic, exponential decay, piecewise) to per-N accuracy data.
2. **Vendor-specific per-platform routing accuracy at marketplace sizes >100.** SkillRouter's 80K benchmark is built on SkillsBench + a synthetic pool. Real-world Claude Code / Cursor / kimi-code routing accuracy at >100 skills is undocumented in the literature.
3. **The "8-per-request" claim origin.** Could be a misremembering, could be a closed Anthropic design note, could be from a third-party product. One targeted ask on the Anthropic forum or a search of GitHub Discussions would settle it.
4. **Long-context model behavior at 1M context windows.** Anthropic Claude Sonnet 4.6, GPT-5.5, and DeepSeek V4-Flash all have 200K+ context windows. Whether the ~1,000-skill attention threshold holds for 1M-context models (or scales linearly) is untested.
5. **SkillReducer runtime hit rate.** Stage 2 produces reference modules with routing metadata ("when: you need to WRITE HubSpot configs"), but how often does the agent actually load the right reference file at runtime? A follow-up study measuring runtime hit rate would close this gap.

## References (ordered by first mention)

1. Klymentiev, Dmytro. "How does an AI agent pick from 686 skills in a second?" klymentiev.com, 23 May 2026. https://klymentiev.com/blog/claude-skills-semantic-router
2. GitHub Issue. "Skill description budget silently truncates routing information." anthropics/claude-code#64606, 2 June 2026. https://github.com/anthropics/claude-code/issues/64606
3. Skywork. "ClawHub and OpenClaw Skill Marketplace Deep Dive 2026." 25 April 2026. https://skywork.ai/slide/en/clawhub-openclaw-skill-marketplace-2047575736827637761
4. Anthropic. "Extend Claude with skills." code.claude.com. https://code.claude.com/docs/en/skills
5. PromptSpace. "Smart Routing: Let AI Pick the Right Skill for Every Task." 25 May 2026. https://www.promptspace.in/blog/smart-routing-let-ai-pick-right-skill
6. claudefa.st. "Claude Code's Hidden Skill Budget Setting (May 2026)." 14 June 2026. https://claudefa.st/blog/guide/mechanics/skill-listing-budget
7. dsebastien.net. "Claude Code Configuration." 2 June 2026. https://www.dsebastien.net/claude-code-configuration/
8. hutchic. "cursor-skills.md." GitHub. https://github.com/hutchic/.cursor/blob/main/docs/cursor-skills.md
9. wonderbird. "AI Rule Adherence Strategy ADR-001." GitHub. https://github.com/wonderbird/ai-agent-workspace/blob/main/docs/architecture-decisions/001-ai-rule-adherence-strategy.md
10. MoonshotAI. "kimi-cli PR #1626." GitHub Actions, 29 March 2026. https://github.com/MoonshotAI/kimi-cli/actions/runs/23698152026
11. Microsoft. "Agent Skills — Microsoft Agent Framework." learn.microsoft.com, 20 May 2026. https://learn.microsoft.com/en-us/agent-framework/agents/skills
12. Microsoft Devblog. "Give Your Agents Domain Expertise with Agent Skills in Microsoft Agent Framework." 4 March 2026. https://devblogs.microsoft.com/agent-framework/give-your-agents-domain-expertise-with-agent-skills-in-microsoft-agent-framework/
13. Gao, Y et al. "SkillReducer: Optimizing LLM Agent Skills for Token Efficiency." arXiv:2603.29919, 31 March 2026. https://arxiv.org/abs/2603.29919
14. Zheng, Yanzhao et al. "SkillRouter: Skill Routing for LLM Agents at Scale." arXiv:2603.22455v3, 31 March 2026. https://arxiv.org/html/2603.22455v3
15. tachyon-beep. "skillpacks README." GitHub. https://github.com/tachyon-beep/skillpacks
16. Skill Hub. "On-Demand AI Skill Routing for LLM Context Optimization." mcpmarket.com. https://mcpmarket.com/server/skill-hub-1
17. ZenML Database. "Dynamic Context Discovery for Production Coding Agents." 2026. https://www.zenml.io/llmops-database/dynamic-context-discovery-for-production-coding-agents
18. Agentic Thinking. "How Cursor Finds Skills." 27 January 2026. https://agenticthinking.ai/blog/skill-discovery/
19. codewithmukesh. "Skills in Claude Code — Reusable Prompts and Workflows." 23 May 2026. https://codewithmukesh.com/blog/skills-claude-code/
20. inventorsoft.co. "How to Teach Your AI Agent to Work by Your Standards." 4 May 2026. https://inventorsoft.co/blog/agent_skills_how_to_teach_ai_agent_to_work_by_your_standards
21. create-rules. Cursor skill (lobehub.com). https://lobehub.com/skills/dmitryprg-ai-cursor-develop-autorules-create-rules