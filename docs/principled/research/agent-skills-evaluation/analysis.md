# Sub-Question Decomposition

| # | Sub-question | What we already know (from background.md) | What we still need | Source priority |
|---|---|---|---|---|
| 1 | What is the **canonical Anthropic 5-stage evaluation loop** and which stages are runtime-specific vs runtime-agnostic? | The SKILL.md describes Capture → Eval → Run → Grade → Iterate → Optimize-trigger. Stages 3 (Run uses `claude -p`) and 5 (Optimize uses `run_loop.py` + `claude -p`) depend on Claude Code; stages 1, 2, 4 are orchestration. | Verify by reading `references/schemas.md` and confirming what artifacts are runtime-portable vs not. | 1st |
| 2 | What does `evals.json` actually look like, and how should a generalistic skill surface it? | `evals.json` = `{skill_name, evals:[{id, prompt, expected_output, files[], expectations[]}]}`. Lives in `evals/evals.json` next to the skill. | Confirm the field set is closed, and whether `expectations` is required at this stage or added later. | 1st |
| 3 | What does a grade output (`grading.json`) look like, and what is the minimum the calling agent must produce? | Grader returns `{text, passed, evidence}` per expectation. The viewer depends on these exact field names. | Confirm the exact field names and any nesting. | 1st |
| 4 | What does `benchmark.json` look like, and can it be computed inline without `aggregate_benchmark.py`? | It has `pass_rate, time, tokens` per config with `mean ± stddev` and a delta. The skill-creator runs 3 iterations per query to get stddev. | Read the schema to know exact field requirements. | 1st |
| 5 | How does Anthropic detect "the skill was loaded" in a trigger test, and how do we replicate that without `claude -p`? | `run_eval.py` writes a `.claude/commands/<name>-skill-<uuid>.md` file and uses `--include-partial-messages` to detect `content_block_start` events for the skill. | Examine `run_eval.py` for the exact detection logic and identify the abstract pattern. | 1st |
| 6 | How does the description-optimizer loop generalize? Does the held-out-test approach need adaptation for non-Claude models? | `run_loop.py` does 60/40 train/test split, runs 3 trials per query, calls Claude to propose improvements, picks best by test score. | Check if the loop is model-agnostic (it likely is — Claude as editor is just one choice of editor LLM). | 2nd |
| 7 | What is the **generalistic grading pattern** that works without subagents? | The Anthropic grader is an Agent tool subagent. In headless mode, the orchestrator must grade inline — but it has the same tools (Read, Glob, Grep). The orchestrator becomes the grader. | Read the grader prompt to identify its inputs and outputs in abstract form. | 1st |
| 8 | How do existing taches-principled-light skills (crafting-skills, general-critic, reviewing-and-polishing) overlap with this methodology, and what stays unique? | crafting-skills teaches the eval-driven-development workflow in CREATE mode Step 2 + Step 6. general-critic is a reusable critic subagent. reviewing-and-polishing has REVIEW + CRITIQUE modes. | Map which concerns each covers and where gaps remain. | local |
| 9 | What **fallbacks** exist when the runtime cannot display HTML or spawn subprocesses? | Anthropic's `--static <path>` writes an HTML file the user opens themselves. For headless, the natural equivalent is to write a Markdown report. | Identify each runtime-specific dependency and pair it with a Markdown / JSON / inline equivalent. | 2nd |
| 10 | What is the **minimum viable evaluating-skills** that delivers ≥80% of the value at ≤20% of the complexity? | The 5-stage loop with stubs for subagent and subprocess calls. | Synthesize the smallest skill that preserves the loop's intent. | synthesis |

## Parallelism Map

- `parallel: true` — sub-questions 1, 2, 3, 4, 5, 6, 7 (they all require reading the same small set of files in `skill-creator`)
- `parallel: false` — sub-questions 8, 9, 10 (depend on the answer to the previous batch and require synthesis against local skill files)

## Risk Register

- **Risk:** The generalistic skill becomes a thin wrapper around "do whatever the runtime supports", which is useless.
  **Mitigation:** The skill teaches the *methodology contract* (what artifacts must exist after each stage: `evals.json` → `grading.json` → `benchmark.md`). Each runtime chooses how to fill them.
- **Risk:** Taches-principled-light users expect the marketplace to "just work" without picking a runtime mode. We can't ship both interactive and headless and pick at runtime without metadata.
  **Mitigation:** The skill reads the calling agent's own capabilities from context (does it have a `Bash` tool? a `WebFetch` tool? an `Agent` tool?) and adapts. No runtime-mode flag needed.
- **Risk:** Reusing Anthropic's schema names causes confusion when the marketplace adopts its own dialect later.
  **Mitigation:** Adopt Anthropic's schemas as-is. Schemas are public. Interop > local-flavor.