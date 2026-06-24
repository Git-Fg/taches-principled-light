---
name: evaluating-skills
description: "Load when evaluating an agent skill — writing evals, comparing with-skill vs baseline, grading outputs, or iterating. Use when the user says 'test this skill', 'benchmark', or 'improve it from the evals'. Do NOT use for authoring or pre-commit spec lint, and do NOT use for adversarial critique of non-skill artifacts."
when_to_use: |
  Use to measure whether a skill improves agent behavior via with-skill vs
  baseline behavioral comparison. Works across Claude Code, claude -p, Codex,
  kimi-code, and Reasonix. Trigger detection is behavioral, not load-event.
argument-hint: "[mode] [skill-path] [--runs N]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
license: MIT
---

# Evaluating Skills

Measure whether a skill makes an agent *behave better*. The unit of evidence is a behavioral comparison: two runs of the same prompt — one with the skill available, one without — captured as raw transcripts, then graded. This works on any agent CLI that emits a streaming transcript (Claude Code, `claude -p`, Codex, kimi-code, Reasonix all qualify).

This is the evaluation harness that `crafting-skills` (authoring) and `general-critic` (the critic contract) plug into. It owns the loop; they own the inputs and the judgement style.

## Decision Router

IF the user wants to know whether a skill is *good* / works / helps → **RUN** mode (the full pipeline)
IF the user already has two transcripts (with vs without) and wants them compared → **COMPARE** mode
IF the user wants to improve the skill's *description* so it triggers correctly → **OPTIMIZE** mode
IF unclear → **RUN** mode is the default; ask only if you cannot find the skill path

## Capability Probe (run first, every time)

Before any run, detect your own capabilities by reasoning about your tools. Mark each:

| Capability | How to detect | If absent |
|---|---|---|
| **Subagents** (Agent/subagent tool) | you have a tool that spawns an isolated agent | run inline, sequentially; less rigorous, still valid |
| **Bash / subprocess** | you can run shell commands | you cannot invoke the target CLI as a subprocess — **COMPARE** mode needs pre-captured transcripts instead |
| **JSONL capture** | the target CLI has a streaming/transcript flag (see `references/runtime-adapters.md`) | falls back to capturing stdout text; behavioral review is weaker |
| **Browser / display** | you can open HTML | review is a `report.md`, not an HTML viewer |
| **Parallel execution** | subagents + can launch many in one turn | run serially; raise `--runs` only if cost allows |

Write the probe result to the workspace as `capabilities.json` so later stages read it instead of re-probing. The probe decides which row of the adapter table each stage uses.

## The 8-Stage Loop

Adapted from Anthropic's `skill-creator`. Stages 1, 2, 5, 7 are runtime-agnostic; 3, 4, 6, 8 have adapter forms selected by the capability probe. Full schemas and per-runtime flags live in `references/`.

### Stage 1 — Capture intent

Decide whether this skill even needs evals. Skills with objectively verifiable outputs (file transforms, data extraction, fixed workflows) benefit. Skills with subjective outputs (writing style, art) are better evaluated qualitatively — say so and run **COMPARE** mode on 1 run each, not a benchmark. Confirm the skill path and the target runtime.

### Stage 2 — Write `evals.json`

Create `<workspace>/evals/evals.json` using the schema in `references/schemas.md`. Start with 2–3 realistic prompts (the kind a real user types — with file paths, context, typos), `expectations[]` left empty. You will fill expectations in stage 4 while runs are in flight. Use `assets/evals-template.json` as the skeleton.

### Stage 3 — Run with-skill + baseline (per eval, same turn)

For each eval, produce **two** transcripts of the same prompt:

- **with_skill**: the skill available to the target runtime.
- **without_skill** (baseline): the skill *not* available. For a new skill, baseline = no skill. For improving an existing skill, snapshot it first (`cp -r <skill> <workspace>/skill-snapshot/`) and baseline = the old version.

Capture each run as a normalized transcript (`with_skill.jsonl`, `without_skill.jsonl`) — see `references/runtime-adapters.md` for the two distinct capture paths (subprocess CLI vs interactive subagent). Capture timing (`total_tokens`, `duration_ms`) per run — it is not persisted elsewhere.

**Adapter:** if you have subagents + bash → spawn both runs in parallel this turn. If inline-only → run them sequentially yourself. If no bash/subprocess → the user must supply pre-captured transcripts (**COMPARE** mode).

Agent runs are stochastic; the per-run `delta` is the signal, the mean ± stddev over `--runs` runs is the noise floor. With `--runs 1` you get a single-pass comparison (no stddev, but a `material_difference` signal); with `--runs 3` you get a stable delta estimate at 3× the cost.

### Stage 4 — Grade (behavioral review)

This is the core innovation over Anthropic's load-event model. Read `references/behavioral-review.md` for the full contract. In short:

Spawn a reviewer subagent (or switch hats and do it inline) that takes both transcripts + the skill's `SKILL.md` + the eval `expectations[]`, and:

1. Reads both transcripts end-to-end.
2. Self-edits each JSONL (or writes an overlay) annotating where behavior aligned with / deviated from the skill's explicit guidance.
3. Scores both runs on a fixed rubric — *followed-step-ordering, used-skill-patterns, output-completeness, output-quality, tool-discipline*.
4. Emits `behavioral_comparison.json` per eval: per-dimension `with_skill` / `without_skill` / `delta` / evidence quotes, plus `material_difference: bool`.

Fill the eval's `expectations[]` now (from the deviation annotations) if they were empty. Reuse the `general-critic` HIGH/MEDIUM/LOW contract for the verdict; if ambiguous, loop until the comparison is decisive.

### Stage 5 — Aggregate

Compute `benchmark.json` (schema in `references/schemas.md`): per-configuration `pass_rate / time / tokens` as `mean ± stddev` + `delta`. Meaningful stddev needs ≥3 runs per configuration (`--runs`, default 3) — this is the same ≥3-run floor as **AGENTS.md → Description as Routing Signal → rule 7**, do not loosen it.

If you have a Python interpreter, the portable aggregator handles this deterministically:

```bash
python scripts/aggregate_benchmark.py <workspace>/iteration-N --skill-name <name> --runs 3
```

It reads the `behavioral_comparison.json` files from each `eval-<id>/` subdirectory, writes `benchmark.json` (Anthropic-schema-compatible) and `benchmark.md` (human-readable), and emits auto-derived analyst notes (e.g. "skill may not be moving the needle" when the pass_rate delta is small). No subprocess — runs anywhere Python runs.

If Python is unavailable, compute inline with bash or by hand for small N. The math is `mean(values)`, `stdev(values)`, `min(values)`, `max(values)`, and `mean_with − mean_without` per metric.

### Stage 6 — Review

Present results to the user. **Adapter:** if display available → `generate_review.py --static report.html` (no server) or an inline HTML. If not → write `report.md` with per-eval outputs + the behavioral scores + the benchmark table, and present it inline. Collect the user's feedback and save to `feedback.json`.

### Stage 7 — Iterate

Rewrite the skill from the feedback + deviation annotations. Four principles (from Anthropic): *generalize* (don't overfit to the few examples), *keep the prompt lean* (remove what isn't pulling weight), *explain the why* (not rigid MUSTs), *look for repeated work* (if every run reinvented a helper, bundle it into `scripts/`). Then loop back to Stage 3 in `<workspace>/iteration-N+1/`.

### Stage 8 — Optimize the description (optional)

Only after the body is settled. Measure whether the skill's `description` causes correct triggering — but **behaviorally**, not via load-events. See **OPTIMIZE** mode below.

---

## COMPARE Mode

You already have `with_skill.jsonl` and `without_skill.jsonl` (user-supplied, or from a prior RUN). Skip to Stage 4. Write the annotated transcripts and `behavioral_comparison.json` to `<workspace>/`. This is the right mode when the runtime can't be driven as a subprocess (e.g. an IDE-resident agent) but its transcripts are available.

## OPTIMIZE Mode

Improve the skill's `description` frontmatter for correct triggering. The numeric floors below come from **AGENTS.md → Description as Routing Signal → rule 7** (≥3 runs per query, 0.5 threshold, 60/40 train/val stratified) and from the **trigger-stealing paragraph** that follows rule 7 (>10pp sibling-trigger-rate drop is a regression) — do not loosen them.

### TRIGGER-EVAL PRE-STEP (scriptable, preferred)

Before iterating the description, scaffold a 20-query trigger-eval set (8–10 should-trigger, 8–10 should-not, weighted to *near-misses* not obvious negatives), split 60/40 train/val, and score it:

```bash
python scripts/trigger_eval.py init --out /tmp/queries.json --skill-name <name>
# Fill in `query` for every entry, preserving should_trigger.
python scripts/trigger_eval.py split /tmp/queries.json /tmp/train.json /tmp/val.json --seed 42
# Run each query ≥3 times against the agent, capture the transcript, then:
python scripts/trigger_eval.py detect <transcript.jsonl> <name> --runtime {claude,codex,kimi,reasonix,cursor}
# Append {"query_id": N, "run_number": K, "triggered": bool} to results.jsonl
# Train run (iterate the description using these failures):
python scripts/trigger_eval.py score /tmp/train.json /tmp/results.jsonl --threshold 0.5 --out-json /tmp/train-report.json --out-md /tmp/train-report.md
# Validation run (score best description on held-out val set):
python scripts/trigger_eval.py score /tmp/val.json /tmp/results.jsonl --threshold 0.5 --out-json /tmp/val-report.json --out-md /tmp/val-report.md
```

If `trigger_rate_should.mean ≥ 0.5` AND `trigger_rate_should_not.mean ≤ 0.5` on the **validation** set, the description is fine — skip the iteration loop and run the body-iteration loop (next section) instead. Otherwise, iterate the description, re-score the train set to surface new failures, and re-validate on the val set. Cap at 5 iterations. The train/val split is mandatory — picking best by train score overfits to the train queries. See `references/trigger-eval-guide.md` for the full methodology, `assets/trigger-queries-template.json` for the skeleton, and `assets/shadow-skill-scaffold.md` for adversarial-shadow testing.

### Body-iteration loop (behavioral)

Reuse the trigger-eval queries scaffolded in the TRIGGER-EVAL PRE-STEP above (do not re-author them). If the PRE-STEP was skipped because the runtime lacks transcript capture, scaffold an equivalent set inline (≈10 should-trigger, ≈10 should-not, weighted to *near-misses* not obvious negatives — see `references/behavioral-review.md` §trigger-evals). Then:

1. For each query, run with-skill-available vs not, capture both transcripts.
2. The reviewer subagent judges, per query: did the with-skill run behave as the skill intends, and did the without-skill run not? (Behavioral, not load-event.)
3. Split 60/40 train/test (stratified by `should_trigger`). Use the train failures to propose description improvements via your editor LLM; re-evaluate on both; pick best by **held-out test** score (avoids overfitting). Cap at 5 iterations.

If the runtime can't be driven as a subprocess or can't capture transcripts, **skip OPTIMIZE** — matching Anthropic's own Claude.ai guidance. Trigger quality then relies on `crafting-skills` OPTIMIZE mode + `skill-self-testing.md`'s grep-based check.

### Sibling-stealing regression check

When adding or modifying any skill in the catalog, run a `stealing` regression check on the before/after trigger-rate reports of every sibling in the same thematic cluster (per the **trigger-stealing paragraph** in AGENTS.md → Description as Routing Signal, which follows rule 7):

```bash
python scripts/trigger_eval.py stealing before.json after.json --threshold 0.10
```

A >10pp drop in any sibling's `trigger_rate_should.mean` is a routing regression — the new or changed description is stealing signal. Narrow the new description, or merge the skills per `crafting-skills` Compendium Rule 2 (tightly-coupled-cluster exception). Do not raise the threshold to hide the alert; the threshold is a discipline, not a knob.

---

## Workspace layout

```
<workspace>/                          # default: docs/principled/skill-evals/<skill-name>/
├── capabilities.json                 # stage 0 probe result
├── evals/
│   └── evals.json                    # stage 2
├── iteration-N/
│   ├── eval-<name>/
│   │   ├── with_skill.jsonl          # stage 3 (annotated in stage 4)
│   │   ├── without_skill.jsonl
│   │   ├── timing.json
│   │   └── behavioral_comparison.json# stage 4
│   ├── benchmark.json                # stage 5
│   ├── benchmark.md
│   └── feedback.json                 # stage 6
└── skill-snapshot/                   # baseline for improvement runs
```

## Reuse, don't duplicate

- **`crafting-skills`** owns CREATE/OPTIMIZE routing and the 14-rule compendium. This skill adopts Anthropic's `evals.json` schema and defers intent-capture + pre-commit validation there.
- **`crafting-skills` reference: `skill-self-testing.md`** owns the YAML/threshold/trigger-grep pre-commit checks. Run them before declaring a skill shipped. (The reference lives in the sibling skill's `references/` directory; reference by name, not by path, per the marketplace convention.)
- **`general-critic`** owns the HIGH/MEDIUM/LOW critic contract and the "loop until PASS" loop. Use it as the inline grader/reviewer.

## Contrast with nearby skills

- `crafting-skills` — authors the skill; this evaluates it.
- `general-critic` — generic artifact critic; this is the skill-specific harness with schemas + behavioral comparison.
- `reviewing-and-polishing` — reviews code/PRs/prose; this reviews *skills* via runtime transcripts.
- `solving-competitively` — multi-candidate judging; this is with-vs-without-single-skill, not a tournament.

## When NOT to load

- Authoring a skill from scratch → `crafting-skills`.
- The skill has purely subjective output and the user just wants a vibe check → run inline once, don't benchmark.
- No transcript of any kind is available and the runtime can't be driven → there is nothing to evaluate; say so.
