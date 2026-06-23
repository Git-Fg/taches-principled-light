# Iteration 1 — Marketplace Routing Behavioral Eval (single-eval pilot)

## Scope

This iteration-1 is a **pilot** with a single eval (the rest of the 18 evals from `evals/evals.json` are queued for iteration-N+1). The purpose: prove the behavioral-eval harness works end-to-end on the kimi-code marketplace before scaling to all 18 utterances × 2 configurations.

## Eval selected

**craft-create** — utterance "create a new agent skill for parsing PDFs", expected skill `crafting-skills`. Picked because the routing_test.py token-overlap test reports it as a clear win (4 vs runner-up 3), so we should see a behavioral signal.

## Configuration

- **Runtime:** Claude Code CLI (`/Users/felix/.local/bin/claude`) — chosen because kimi's `-p` mode refuses `--yolo`/`--auto` permission flags (verified empirically). Claude accepts `--dangerously-skip-permissions` with `--print`.
- **Capture:** `--output-format stream-json` (newline-delimited JSON events: `system`, `user`, `assistant`, `tool_use`, `tool_result`).
- **With-skill dir:** `<repo>/skills/` (31 marketplace skills auto-discovered by Claude).
- **Without-skill dir:** `/tmp/empty-skills/` (empty `.claude/` and `.agents/` subdirs — Claude discovers zero skills).
- **Timeout:** 90s for with-skill (hit limit, transcript truncated at 94 events); 120s for without-skill (completed cleanly, 62 events).

## Behavioral signal

| Metric | With skills | Without skills | Delta |
|---|---|---|---|
| Total events | 94 (truncated) | 62 | +32 |
| `Skill` tool invocations | `[superpowers:writing-skills, superpowers:brainstorming]` | `[superpowers:writing-skills, superpowers:brainstorming]` | 0 |
| `Read` calls on any SKILL.md | 3 | 0 | +3 |
| `Read` calls on marketplace SKILL.md | 3 (crafting-skills, pdf-design-guide, deep-research) | 0 | **+3** |
| Final response text length | 758 chars | 1278 chars | -520 |

## Verdict

**Material difference observed.** With-skill run READ three marketplace SKILL.md files to inform its approach: `crafting-skills/SKILL.md` (the expected primary skill), `design-hub/pdf-design-guide/SKILL.md` (a sibling — agent searched for `**/pdf*` and read it), and `deep-research/SKILL.md` (a sibling consulted for the "long-form answer with citations" pattern in the user's framing). Without-skill run read zero SKILL.md files and relied entirely on its own base reasoning + superpowers meta-skills.

Both runs invoked the same `superpowers:writing-skills` and `superpowers:brainstorming` skills first — that's system-level routing via superpowers. The marketplace `crafting-skills` is consulted via file reads rather than the `Skill` tool invocation, which is consistent with how marketplaces loaded via `.claude-plugin/marketplace.json` work: they're discovered at session start but not registered as invokable skills unless explicitly enabled.

## Limitations & next steps

1. **Timeout truncation:** the with-skill run hit the 90s timeout at 94 events. The agent was still exploring. A real eval should give 180-300s budget.
2. **N=1:** only 1 of 18 evals run. Need to scale to all 18 for the benchmark.
3. **Single runtime:** only Claude Code tested. Codex, Cursor, Kimi Code behavior may differ (each has its own skill-discovery mechanics).
4. **Behavioral proxy:** `SKILL.md` reads are a proxy for "skill was consulted." A real eval should also grade whether the agent APPLIED the skill's guidance, not just read it.
5. **Permission handling:** `--dangerously-skip-permissions` is appropriate for sandboxes/evals but should NOT be used in production.

## Stage status (from `evaluating-skills` skill)

| Stage | Status |
|---|---|
| 1 — Capture intent | ✅ — this doc |
| 2 — Write `evals.json` | ✅ — `../evals/evals.json` (18 evals defined; this iteration runs 1) |
| 3 — Run with-skill + baseline | ✅ — `with_skill_claude.jsonl`, `without_skill_claude.jsonl` |
| 4 — Grade (behavioral review) | ✅ — `behavioral_comparison.json` |
| 5 — Aggregate | ⏳ — single eval, no aggregate yet |
| 6 — Review | ✅ — this doc |
| 7 — Iterate | ⏳ — deferred until N=18 reached |
| 8 — Optimize description | ⏳ — depends on having a per-skill scope |
