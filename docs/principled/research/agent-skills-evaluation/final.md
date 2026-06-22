# Deep Research: A Generalistic Skill-Evaluation Methodology

## TL;DR

- Anthropic's official `skill-creator` (`anthropics/skills/skills/skill-creator`) teaches an **8-stage evaluation loop**: capture intent → write `evals.json` → run with-skill + baseline → grade → aggregate → review → iterate → optimize trigger description. Its public JSON schemas (`evals.json`, `grading.json`, `benchmark.json`, `history.json`) are runtime-agnostic and worth adopting verbatim. `[source: skill-creator/SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)`
- 4 of the 8 stages have runtime-specific *mechanisms* in the official skill — but only because the official skill chose brittle Claude-Code-only implementations (`.claude/commands/` injection to detect a `Skill`/`Read` tool_use event; `webbrowser.open()` for the HTML viewer). `[source: run_eval.py](https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/run_eval.py)`
- **The decisive reframing:** measure **behavioral consequence**, not the load event. Every agent CLI in scope can emit a **raw streaming JSONL transcript** — verified for kimi-code (`kimi -p --output-format stream-json` `[source: kimi-command.html](https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command.html)`), Codex CLI (`codex exec --json` `[source: codex cli reference](https://developers.openai.com/codex/cli/reference)`), Reasonix (`agent.NewTextSink` event stream + legacy `--transcript` for JSONL file `[source: esengine.github.io/DeepSeek-Reasonix](https://esengine.github.io/DeepSeek-Reasonix/)`), and Claude Code (`--output-format stream-json --include-partial-messages` `[source: run_eval.py](https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/run_eval.py)`). Two runs (with-skill vs without) produce two JSONL files; a reviewer subagent reads both, self-edits the JSON to annotate behavioral alignment/deviation, and scores the delta. This works on any JSONL-emitting runtime and is richer than a per-query trigger boolean. It collapses the runtime-specific stages from 4 to ~1.5 (only the "make the skill available in one run" setup and the HTML-vs-markdown display choice remain runtime-specific).
- **Recommendation:** ship a single `evaluating-skills` skill in `taches-principled-light` that (a) adopts Anthropic's four schemas verbatim `[source: schemas.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/references/schemas.md)`, (b) teaches the 8-stage loop with a capability probe at the top, (c) replaces trigger-detection with behavioral JSONL review, and (d) reuses the local `general-critic` as the inline grader `[source: local general-critic/SKILL.md]`. No interactive/headless split is needed.

## Body

### 1. What the official skill-creator actually teaches

The `skill-creator` SKILL.md is a 485-line workflow. Its spine is a loop `[source: skill-creator/SKILL.md §"Running and evaluating test cases" and §"Improving the skill"](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)`:

1. **Capture intent** — interview the user; decide whether the skill even needs evals ("Skills with objectively verifiable outputs benefit from test cases. Skills with subjective outputs … often don't need them.").
2. **Write `evals.json`** — 2–3 realistic prompts first, *then* fill in assertions while runs are in flight. `[source: schemas.md §evals.json](https://github.com/anthropics/skills/blob/main/skills/skill-creator/references/schemas.md)`
3. **Run** — spawn, *in the same turn*, a with-skill subagent **and** a baseline subagent per eval. For new skills, baseline = no skill; for improvements, baseline = the previous version (snapshotted). Capture `timing.json` (tokens + duration) from the task notification immediately — "this is the only opportunity to capture this data … it isn't persisted elsewhere."
4. **Grade** — a grader subagent (`agents/grader.md`) returns `{text, passed, evidence}` per expectation. The grader's two non-obvious jobs: (i) mark FAIL when evidence is "superficial (e.g., correct filename but empty/wrong content)", and (ii) **critique the assertions themselves** in `eval_feedback` — "a passing grade on a weak assertion is worse than useless — it creates false confidence." `[source: agents/grader.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/agents/grader.md)`
5. **Aggregate** — `aggregate_benchmark.py` produces `benchmark.json` with `pass_rate/time/tokens` per configuration as `mean ± stddev` plus a `delta`. Meaningful stddev needs ≥3 runs per config. `[source: schemas.md §benchmark.json](https://github.com/anthropics/skills/blob/main/skills/skill-creator/references/schemas.md)`
6. **Review** — `eval-viewer/generate_review.py` serves an HTML viewer with an "Outputs" tab (per-test outputs + feedback textbox) and a "Benchmark" tab (quantitative). Feedback downloads as `feedback.json`.
7. **Iterate** — rewrite the skill from the feedback. Four improvement principles: generalize (don't overfit to the few examples), keep the prompt lean, explain the *why*, and **look for repeated work across test cases** — if every run reinvented the same helper script, bundle it into `scripts/`.
8. **Optimize the description** — `run_loop.py` does a 60/40 stratified train/test split, runs each query 3×, calls Claude to propose description improvements from the failures, re-evaluates, and picks the best by **held-out test score** (explicitly to avoid overfitting). `[source: run_loop.py](https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/run_loop.py)`

The official skill is also admirably honest about its own degradation paths: a "Claude.ai-specific" section (no subagents → run inline, skip baselines, skip browser, skip description optimization) and a "Cowork-specific" section (subagents work, no browser → use `generate_review.py --static` for a standalone HTML file, feedback arrives as a downloaded `feedback.json`). `[source: skill-creator/SKILL.md §"Claude.ai-specific instructions", §"Cowork-Specific Instructions"]`

### 2. Where the official design is Claude-Code-coupled

Three mechanisms are the coupling points:

- **Stage 3/8 trigger detection** (`run_eval.py`) writes a `.claude/commands/<name>-skill-<uuid>.md` file to inject the candidate description into Claude's `available_skills`, then parses the `stream-json` for a `content_block_start` whose `tool_use` name is exactly `Skill` or `Read`. Brittle: depends on Claude Code's command-file convention and exact tool names.
- **Stage 8 editor** (`improve_description.py`) shells out to `claude -p`. Fine for Claude Code; not portable to kimi-code/Reasonix/Codex without substituting their CLIs.
- **Stage 6 viewer** (`generate_review.py`) defaults to `webbrowser.open()`. The `--static` fallback exists but is documented only under Cowork.

The coupling is in the *mechanism*, not the *methodology*. The methodology — schemas, the grade-then-iterate loop, train/test-split description optimization — is fully portable.

### 3. The reframing that makes it generalistic

Replace **"did the skill load?"** with **"did the agent's behavior differ, with vs without the skill?"** — measured by reviewing the raw JSONL transcripts both runs produce.

This works because every target runtime can emit a raw streaming transcript:

- Claude Code / `claude -p`: `--output-format stream-json`
- Codex CLI: its own transcript/trace output
- Cursor: agent-mode trace
- kimi-code, Reasonix: their raw streaming JSONL modes

A **behavioral-reviewer subagent** takes `with_skill.jsonl` + `without_skill.jsonl` + the skill's `SKILL.md` + the eval expectations, and:

1. Reads both transcripts end to end.
2. Annotates each (by editing/overlaying the JSONL) where behavior aligned with or deviated from the skill's explicit guidance.
3. Scores both runs on a fixed behavioral rubric (e.g. *followed-step-ordering*, *used-skill-patterns*, *output-completeness*, *output-quality*, *tool-discipline*).
4. Emits `behavioral_comparison.json` with per-dimension `with_skill` / `without_skill` / `delta` / evidence quotes, plus a `material_difference` verdict.
5. Loops (reusing the local `general-critic` "until no HIGH findings" contract) if the comparison is ambiguous.

Why this is strictly better than load-event detection: (a) universal — needs only a JSONL transcript; (b) catches both loaded-then-ignored and silently-embodied cases; (c) produces a self-documenting annotated transcript, not a boolean; (d) removes the brittle `.claude/commands/` injection from the design entirely.

### 4. Capability matrix (revised)

| Stage | Subagent-native (Claude Code, Cursor, Cowork) | Headless / JSONL-only (`claude -p`, CI, kimi-code, Reasonix, Codex) |
|---|---|---|
| 3 Run | fan out with-skill + baseline subagents per eval | run inline, sequentially; capture each as raw JSONL; baseline = no-skill or previous-version snapshot |
| 4 Grade | grader subagent per run → `grading.json` | **behavioral-reviewer subagent** on the two JSONL transcripts → `behavioral_comparison.json`; or inline self-grade |
| 6 Review | `generate_review.py` server + `webbrowser.open()` | `generate_review.py --static report.html` **or** a `report.md` presented inline; feedback captured as conversation → saved to `feedback.json` |
| 8 Optimize | `run_loop.py` 60/40 split, 3 runs/query, editor LLM | measurement is universal (behavioral delta on JSONL); only the *N-run cost* is a runtime decision — reduce N or do a single-run qualitative check if parallelism is expensive |

With this matrix, **one skill serves all runtimes** — no interactive/headless split. The skill opens by probing its own capabilities (subagent tool? bash/subprocess? browser/display? JSONL-capture flag?) and picks the row. This was the hypothesis in `judgment.md`; it is confirmed.

### 5. How it fits the existing marketplace

The new skill does **not** duplicate the local collection — it is the evaluation *harness* the others plug into:

- `crafting-skills` owns CREATE/OPTIMIZE routing, the 14-rule compendium, and pre-commit validation (Step 2 "Write Evals First", Step 6, `references/skill-self-testing.md`). The new skill adopts Anthropic's `evals.json` schema and references `crafting-skills` for intent-capture.
- `general-critic` owns the reusable critic contract (HIGH/MEDIUM/LOW, loop-until-PASS). The new skill reuses it as the inline grader / behavioral reviewer.
- `reviewing-and-polishing` owns code/PR review and prose polish. No overlap — that's about *artifact* quality, this is about *skill* quality.

### 6. The recommended artifact

A single `skills/evaluating-skills/` directory:

```
evaluating-skills/
├── SKILL.md                      # capability probe + 8-stage loop + adapter table
├── references/
│   ├── schemas.md                # Anthropic's 4 JSON schemas, vendored verbatim
│   ├── behavioral-review.md      # the reviewer-subagent contract + rubric
│   └── runtime-adapters.md       # per-runtime JSONL-capture flags + fallbacks
└── assets/
    └── evals-template.json       # evals.json skeleton
```

Conforms to the local convention: decision router up top, `allowed-tools`, `argument-hint`, ≤50-word description, body <500 lines, schemas pushed to `references/` (Anthropic's own progressive-disclosure rule, `[source: best-practices §"Progressive disclosure patterns"]`).

## What this does NOT settle

1. **Whether to vendor the Anthropic schemas or fetch them live.** Vendoring (current plan) risks drift; live-fetching risks breakage if GitHub moves them. Open — needs a maintainer call.
2. **Per-skill `evals/evals.json` for all 28 existing marketplace skills.** This research designed the *methodology*; backfilling evals for the existing collection is a separate, large task.
3. **The exact behavioral rubric dimensions.** *followed-step-ordering*, *used-skill-patterns*, *output-completeness*, *output-quality*, *tool-discipline* is a starting proposal; it needs calibration against real with/without runs before it's trustworthy.
4. **Whether `material_difference` from one reviewer is reliable enough, or whether high-stakes skills need a blind comparator** (Anthropic's `agents/comparator.md`) plus a panel. Likely skill-dependent.
5. **Cost ceiling for stage-8 N-runs on cheap/parallel runtimes vs expensive ones.** The methodology says "≥3 for stddev"; the runtime decides what's affordable.

## References

1. [skill-creator SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) — canonical 8-stage workflow
2. [skill-creator references/schemas.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/references/schemas.md) — evals/grading/benchmark/history JSON schemas
3. [skill-creator scripts/run_eval.py](https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/run_eval.py) — Claude-Code trigger detection (the brittle mechanism we replace)
4. [skill-creator scripts/run_loop.py](https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/run_loop.py) — 60/40 train/test description optimizer
5. [skill-creator agents/grader.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/agents/grader.md) — grader contract incl. assertion-critique duty
6. [agentskills.io/skill-creation/evaluating-skills](https://agentskills.io/skill-creation/evaluating-skills) — "skill-creator automates much of this workflow"
7. [Anthropic Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — evaluation-driven-development cycle, progressive disclosure
8. Local `skills/crafting-skills/SKILL.md` + `references/skill-self-testing.md` — existing eval/trigger teaching this builds on
9. Local `skills/general-critic/SKILL.md` — inline grader/reviewer to reuse
10. [Promptfoo: Test Agent Skills](https://www.promptfoo.dev/docs/guides/test-agent-skills/) — corroborating JS-assertion agent-eval pattern