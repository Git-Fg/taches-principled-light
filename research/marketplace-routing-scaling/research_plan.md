# Research Plan

## Phase A — Parallel sub-questions (4 concurrent explore subagents)

### Agent 1 — Q3: Claude Code skill routing budget (parallel)
- Read Anthropic docs at https://docs.claude.com (skills section) and https://codewithmukesh.com/blog/skills-claude-code/
- Confirm the `skillListingBudgetFraction = 0.01` → 8,000-char cap.
- Document the 4 truncation modes (fits / priority / truncate / names-only) and their thresholds.
- Confirm `SLASH_COMMAND_TOOL_CHAR_BUDGET`, `skillListingMaxDescChars`, `maxSkillDescriptionChars` knobs.
- Find any literal "N skills per request" limit (the user's "8-per-request" claim).

### Agent 2 — Q4: Cursor skill discovery + budget (parallel)
- Read Cursor's skills docs and Agentic Thinking's "How Cursor Finds Skills".
- Document Cursor's directory scan + agent-decides pattern.
- Find any per-session budget / cap on skills.
- Capture how Cursor handles 50+ skills (does it shard, limit, or trust the model?).

### Agent 3 — Q5: Codex + kimi-code + MAF (parallel)
- Codex: confirm "plugins not skills" framing; find any count limit.
- kimi-code: `--skills-dir`, any budget cap.
- Microsoft Agent Framework: confirm `AgentSkillsProvider` 2-level depth; `load_skill` / `read_skill_resource` tools; budget behavior.

### Agent 4 — Q7: The "8-per-request" claim (parallel)
- Search Anthropic docs, GitHub issues, forum posts for any literal "8 skills per request" or "8 skills per turn" limit.
- Distinguish: is 8 a hard count, or is it derived from the 8K-char budget at ~1K chars/skill?
- Find the origin of the claim if it exists.

## Phase B — Sequential sub-questions (single agent)

### Q1 — Curve shape
- SkillReducer 55,315-skill corpus: any breakdown by marketplace size?
- SkillRouter 80K-skill benchmark: any per-N accuracy plot?
- arXiv 2605 SoK survey: any aggregated scaling data?

### Q2 — Knee location
- Anthropic bug #64606 "20+ custom skills per project" — the empirical collapse point.
- promptspace.in "around 7-8 skills" — practitioner floor.
- Microsoft 2-level discovery depth — the architectural ceiling.
- tachyon-beep "5+ plugins" — practical ceiling for slash-command workaround.
- Cross-reference to converge on a recommended max.

### Q6 — Scaling patterns
- SkillReducer: 48% description compression → what marketplace size does that unlock?
- SkillRouter: 1.2B reranker → production-grade? Latency?
- Skill Hub: 14-tool facade → adoption? Tradeoffs?
- Slash-command workaround (tachyon-beep) → manual overhead?
- Synthesis: decision tree for "add skills vs shard vs external route."

## Deliverables

Each Phase A subagent returns a markdown section (≤ 300 words) with:
- A "Verified findings" sub-list of facts with `[source: title](url)` inline citations.
- An "Unverified" sub-list of facts I could not confirm.

After all subagents return, the orchestrator:
1. Merges Phase A findings into `document.md`.
2. Runs Phase B (Q1, Q2, Q6 sequentially).
3. Writes the `Synthesis` section tying everything together.
4. Writes `## Open questions`.

Then proceeds to step 5 (`final.md`).