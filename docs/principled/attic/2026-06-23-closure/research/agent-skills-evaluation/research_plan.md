# Research Plan

Same as analysis.md's sub-question table, plus an executable task list for step 4. Each step references the source file already cached under `/tmp/skill-creator-*.md` and `/tmp/skill-creator-*.py` (fetched during planning) or the local marketplace files.

## Execution Task List

### Batch A — parallel (read official skill-creator files)

- [ ] A1. Read `references/schemas.md` fully → extract exact field names for `evals.json`, `grading.json`, `benchmark.json`, `history.json`.
- [ ] A2. Read `agents/grader.md` fully → extract the grader's input contract and output schema; note its "critique the assertions themselves" behavior.
- [ ] A3. Read `agents/comparator.md` + `agents/analyzer.md` → extract blind-comparison contract (for completeness, not for port).
- [ ] A4. Read `scripts/run_eval.py` → extract the exact trigger-detection logic (`.claude/commands/` injection, stream-json content-block-start parsing).
- [ ] A5. Read `scripts/run_loop.py` + `improve_description.py` → extract the description-optimizer loop's parameters (train/test split, trial count, iteration cap).
- [ ] A6. Read `scripts/aggregate_benchmark.py` → extract how pass_rate + stddev + delta are computed.
- [ ] A7. Re-read SKILL.md sections "Running and evaluating test cases" + "Improving the skill" + "Description Optimization" + "Claude.ai-specific" + "Cowork-specific" → extract the runtime-specific assumptions and the explicit fallbacks Anthropic already documents.

### Batch B — parallel (read local marketplace files)

- [ ] B1. Read `crafting-skills/SKILL.md` fully → extract its Step 2 (Write Evals First) and Step 6 (Validate Before Shipping); note its eval schema vs Anthropic's.
- [ ] B2. Read `crafting-skills/references/skill-self-testing.md` → extract its pre-commit checklist; compare with Anthropic's grading.
- [ ] B3. Read `general-critic/SKILL.md` (just added) → extract its critic-loop contract for reuse as the inline grader.
- [ ] B4. Read `reviewing-and-polishing/SKILL.md` REVIEW + CRITIQUE modes → identify overlap and carve out the unique scope.

### Batch C — sequential (synthesis)

- [ ] C1. Build the **runtime-capability matrix**: for each of {Claude Code interactive, Claude Code `claude -p`, Codex CLI, Cursor, Reasonix, kimi-code, generic CI}, enumerate which capabilities exist (subagents, browser, subprocess, MCP tools) and which don't.
- [ ] C2. Build the **adapter table**: for each pipeline stage, give the interactive-native form AND the headless fallback form.
- [ ] C3. Decide whether to ship one skill or two (test the hypothesis in judgment.md).
- [ ] C4. Draft `evaluating-skills/SKILL.md` matching the local convention (decision router, allowed-tools, argument-hint, ≤50-word description, body <500 lines, references/ for schemas and adapters).
- [ ] C5. Validate the draft against (a) Anthropic spec, (b) Anthropic best practices, (c) local `crafting-skills` compendium.

### Batch D — final

- [ ] D1. Write `final.md` with TL;DR, body per angle, "what this does NOT settle", references.