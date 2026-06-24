# Background

## Question restatement

Two-part question on agent-skill marketplace routing at scale:

1. **Routing-quality degradation curve.** As the number of skills in a marketplace or per-session grows, how does per-skill trigger recall degrade? Is the relationship linear, knee-shaped, or sigmoidal? At what marketplace size does the design recommendation shift from "add skills" to "consolidate or shard"?

2. **Production marketplace implementations.** How do production agent-skill marketplaces (Claude Code Skills API at 8-per-request, Cursor, Codex, kimi-code, Microsoft Agent Framework) implement description-based routing under their respective context-budget and session-discovery constraints? What practical advice exists for marketplaces that want to scale beyond the 8-skill hard ceiling?

## Key terms and disambiguation

| Term | Meaning |
|---|---|
| **Routing** | The process of selecting which skill (or none) applies to a user request, given the skill's `description:` frontmatter. |
| **Progressive disclosure** | Anthropic's canonical pattern: only `description` (~100 tokens) is injected into the system prompt at every turn; full `body` is loaded on demand when the agent picks a skill. |
| **`skillListingBudgetFraction`** | Claude Code's hard-coded 1% of context window for the listing — `200K × 4 × 0.01 = 8,000 chars`. Default in v2.1.159; overridable via `SLASH_COMMAND_TOOL_CHAR_BUDGET`. |
| **Trigger recall** | Fraction of should-trigger queries where the agent actually picks the skill. Complemented by trigger rate on should-not queries (false-positive rate). |
| **Routing signal** | The information the agent uses to decide. SkillReducer's Stage 1 = description; SkillRouter's finding = full body text dominates attention (91.7% of cross-encoder attention). |
| **Sharding / consolidation** | Splitting one marketplace into N sub-marketplaces (e.g., per-project, per-cluster), or merging N skills into one. |
| **"8-skill hard ceiling"** | The user-named phrase. Not a literal Anthropic limit; the actual ceiling is the *character* budget, not a skill count. With 200-char descriptions (the recommended), the cap is ~40 skills; with 500-char descriptions, ~16 skills. |

## Top sources

| # | Title | URL | Author / Org | Date | One-line takeaway |
|---|---|---|---|---|---|
| 1 | SkillReducer: Optimizing LLM Agent Skills for Token Efficiency | https://arxiv.org/abs/2603.29919 | Y Gao et al. | 2026-03-31 | Empirical study of 55,315 wild skills. 26.4% lack routing descriptions, 60% of body is non-actionable. Less-is-more: compressing descriptions by 48% *improves* quality by 2.8%. |
| 2 | SkillRouter: Skill Routing for LLM Agents at Scale | https://arxiv.org/html/2603.22455v2 | Zheng et al. (Alibaba) | 2026-03-30 | Benchmark of ~80K skills, 75 expert queries. Removing skill body causes 31-44pp drop in routing accuracy. 91.7% of cross-encoder attention on body. |
| 3 | Skill description budget silently truncates routing information | https://github.com/anthropics/claude-code/issues/64606 | Anthropic bug | 2026-06-02 | Binary analysis of Claude Code v2.1.159: `skillListingBudgetFraction=0.01` → 8,000-char cap. 25 skills × 490 chars = 12,274 chars → silent truncation. |
| 4 | SkillOrchestra: Skill Transfer in Agent Routing | https://www.emergentmind.com/papers/2602.19672 | Multi-institution | 2026-02-23 | Skill Handbook Pareto-frontier routing; +22.5 absolute accuracy, 700x cost reduction over RL routers. Less-fragmented skill sets perform better. |
| 5 | Microsoft Agent Framework: Agent Skills | https://learn.microsoft.com/en-us/agent-framework/agents/skills | Microsoft | 2026-05-20 | `AgentSkillsProvider` scans **2 levels deep** for `SKILL.md`. Injects names+descriptions into system prompt; exposes `load_skill` and `read_skill_resource` tools. |
| 6 | Give Your Agents Domain Expertise with Agent Skills in Microsoft Agent Framework | https://devblogs.microsoft.com/agent-framework/give-your-agents-domain-expertise-with-agent-skills-in-microsoft-agent-framework/ | Microsoft devblog | 2026-04-13 | Walks through .NET + Python integration. Discovery depth is hard-coded at 2 levels. |
| 7 | Dynamic Context Discovery for Production Coding Agents | https://www.zenml.io/llmops-database/dynamic-context-discovery-for-production-coding-agents | ZenML (Cursor) | 2026-01 (blog) | Cursor's "dynamic context discovery": 5 techniques; MCP tool selection cut 46.9% tokens. Skills = one of the layers. |
| 8 | Smart Routing: Let AI Pick the Right Skill for Every Task | https://www.promptspace.in/blog/smart-routing-let-ai-pick-right-skill | PromptSpace | 2026-05-25 | Practitioner anecdote: "Around skill seven or eight, things get weird." Routing is description-driven + request-shape-driven + competitive. |
| 9 | Skills in Claude Code — Reusable Prompts and Workflows | https://codewithmukesh.com/blog/skills-claude-code/ | Mukesh | 2026-05-23 | Skill Budget = 1% of context by default. `SLASH_COMMAND_TOOL_CHAR_BUDGET` and `skillListingBudgetFraction` are the override knobs. |
| 10 | Skill Hub: On-Demand AI Skill Routing for LLM Context Optimization | https://mcpmarket.com/server/skill-hub-1 | mcpmarket | 2026 | 200 local skills exposed as **14 lightweight tool definitions** to the LLM. Demonstrates the on-demand routing pattern. |
| 11 | tachyon-beep/skillpacks | https://github.com/tachyon-beep/skillpacks | tachyon-beep | 2025-10-28 | "Router skills are comprehensive guides that exceeded the context budget for automatic skill discovery." 200+ skills across 38 packs; uses slash commands for routers. |
| 12 | Harnessing Agent Skills: Architectural Patterns and a Reference Architecture | https://arxiv.org/list/cs/new (new listing 2026-06-23) | arXiv new | 2026-06-23 | New survey paper citing "trigger rate" as a primary success metric for skill mediation. |
| 13 | How Cursor Finds Skills | https://agenticthinking.ai/blog/skill-discovery/ | Agentic Thinking | 2026-01-27 | Cursor discovery flow: scan directories → present skills to agent → agent matches via description. Description is "single most important part of your skill." |
| 14 | Feature request: coordinator.domains frontmatter for tag-match routing | https://github.com/anthropics/skills/issues/1091 | Agent Upskill | 2026-05-04 | Two-layer routing: deterministic tag-match (confidence 1.0) + Sonnet classifier fallback (threshold 0.6). |

## Open threads (still to investigate)

- **Curve shape (linear vs knee vs sigmoidal).** None of the sources I've read so far plot a fitted curve. SkillRouter's 31-44pp drop and the Claude Code bug show the *collapse point* but not the slope. The Microsoft 2-level cap and the promptspace.in "around 7-8 skills" anecdote suggest a **knee**, not a sigmoidal S-curve, but no quantitative model.
- **The actual Claude Code "8-per-request" rule.** The user mentions it. I haven't found a Claude Code source documenting this exactly. The empirical evidence points to a *character* budget, not a count, but the user's "8-per-request" framing is worth verifying.
- **Codex / kimi-code routing implementations.** Less documented than Claude Code / Cursor / Microsoft. Worth a targeted search.
- **Quantitative scaling experiments.** SkillReducer's 55,315-skill corpus is the largest I've seen but doesn't plot per-skill-count vs accuracy. The closest is the 200-skill Stratified Sample.
- **Production-grade routing alternatives for scaling beyond 8.** Skill Hub (14 tools → 200 skills) and SkillRouter (1.2B reranker) are the leading patterns. Worth verifying their real-world adoption.

## Next: direction judgment (see judgment.md)