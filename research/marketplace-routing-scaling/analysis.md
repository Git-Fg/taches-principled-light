# Analysis

## Sub-questions (decomposed from judgment.md)

| # | Sub-question | Already know | Still need | Queries | Source priority |
|---|---|---|---|---|---|
| 1 | What is the empirical shape of the per-skill trigger recall vs marketplace size curve? | SkillRouter's 31-44pp drop on body removal; Claude Code 8K-char cap; promptspace.in "around 7-8" anecdote. None of these *plot* a curve. | Quantitative scaling data points (e.g., SkillReducer 198-stratified wild sample, Microsoft 2-level depth finding, SkillRouter benchmark). | "trigger recall" "skills marketplace size" scaling study, "N skills" "Hit@1" curve plot | SkillRouter, SkillReducer, the arXiv 2605 survey |
| 2 | Where does the marketplace size knee sit in practice, and what evidence locates it? | Anthropic's bug report (20+ skills per project hits cap); Microsoft 2-level depth; promptspace.in's 7-8. No consensus number. | Direct empirical curves or more anecdotes clustering around a range. | "5 skills" "10 skills" "20 skills" marketplace degradation, marketplace size limit LLM routing | SkillRouter benchmark, SkillsBench, Anthropic docs |
| 3 | How does Claude Code's Skills API implement the 8,000-char budget, the 4 truncation modes, and the override knobs? | Bug #64606 documents `skillListingBudgetFraction=0.01`, `formatCommandsWithinBudget`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`. | Official Anthropic docs on the budget knobs (vs the binary-analysis-derived knowledge); what triggers "names-only" mode. | site:docs.claude.com skill description budget, SLASH_COMMAND_TOOL_CHAR_BUDGET, skillListingBudgetFraction | Anthropic docs, codewithmukesh |
| 4 | How does Cursor implement skill discovery and routing? What is its budget behavior? | Skills discovery flow scans `.cursor/skills/` + `~/.claude/skills/`; agent decides; "agent decides" section; description is the only signal. | Cursor's specific budget settings (if any) and skill count cap; how they handle 50+ skills. | Cursor skills budget, cursor skills directory listing token | Cursor docs, Agentic Thinking blog |
| 5 | How does Codex / kimi-code / Microsoft Agent Framework implement description routing? | Microsoft has `AgentSkillsProvider` with 2-level depth, `load_skill` and `read_skill_resource` tools. Codex is "plugins not skills" per our own runtime-adapters.md. kimi-code has `--skills-dir`. | Specific character/count budgets and discovery depth limits. | kimi-code skills directory budget, Codex plugin skills description routing, AgentSkillsProvider 2-level depth | MAF docs, Codex docs, kimi-code docs |
| 6 | What scaling patterns exist beyond 8 skills? | SkillReducer's 48% description compression; SkillRouter's 1.2B reranker; Skill Hub's 14-tool facade; tachyon-beep's slash-command workaround. | Real-world adoption evidence; tradeoff matrix; whether these tools are used in production at >100 skills. | scaling beyond 8 skills, on-demand skill routing production, skill hub tool facade | Skill Hub, SkillRouter, SkillReducer, arXiv 2605 SoK |
| 7 | The "8-per-request" claim — is it literally true, or is the user misremembering? | I've found no source confirming 8 specifically. The Claude Code cap is character-based. | Confirm whether Claude Code has a hard count limit in addition to the character budget. | claude code 8 skills per request limit, claude code skills count limit per turn | Anthropic docs, GitHub issues |

## Parallel vs sequential

- **Parallel (independent, can run concurrently):** Sub-questions 3, 4, 5 (each platform implementation), and sub-question 7 (the "8-per-request" claim).
- **Sequential (each depends on the previous):** Sub-questions 1 and 2 (the curve shape and knee location) build on each other; sub-question 6 depends on sub-questions 1-2 establishing the problem before evaluating solutions.

So I'll run:
- Phase A (parallel): Q3, Q4, Q5, Q7 via 4 concurrent explore subagents.
- Phase B (sequential, single agent): Q1, Q2, Q6 in series.

Each subagent gets the full context, the specific sub-question, the source-priority list, and the expected output shape (a markdown section with citations).

## Output expectations

`document.md` will have:
- One `## <sub-question>` section per sub-question.
- Each section ends with a 1-sentence interim verdict.
- Final section `## Synthesis` with cross-cutting answer.
- Final section `## Open questions` for things primary sources would settle.

`final.md` will follow the deep-research quality bar:
- TL;DR with 3-6 bullets, each cited.
- Body with H2 per angle, paragraphs with `[source: title](url)` citations.
- "What this does NOT settle" section.
- References section ordered by first mention.
- No paragraph > 6 lines.