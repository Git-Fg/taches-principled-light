# Iteration 3 Design — Assertion-Based Skill Grading

## Why iteration-3

Iteration 1 and iteration 2 use **read-counting** as the behavioral signal: how many marketplace SKILL.md files did the agent consult? This is a *necessary but not sufficient* signal. An agent can read the right skill and still fail to apply it. Conversely, a strong model can produce a correct answer without reading any skill.

The Tessl framework ([arxiv 2606.17819v1](https://arxiv.org/html/2606.17819v1), June 2026) and Anthropic's `skill-creator` (4 modes: Create / Eval / Improve / Benchmark, March 2026) both grade on **task completion** via custom rubrics, not on consultation. The Tessl paper showed that **instruction-following** is the discriminating metric: "Kimi K2.6, MiniMax 2.7, Qwen3-Coder-Next, and Gemini 3.1 Flash Lite all cluster around 57–60 — roughly 25–30 points below the frontier." By contrast, **goal-completion** "close to saturation, frequently exceeding 90%" for almost all models except the Nemotron family — so the wide spread is on instruction-following, not goal-completion.

This document specifies the iteration-3 design that adopts the assertion-based pattern.

## Reuse, don't re-invent

The marketplace already ships an 8-stage eval loop in `skills/evaluating-skills/` that implements this design. Specifically:

- **`skills/evaluating-skills/SKILL.md`** — the 8-stage loop (Capture intent → Write `evals.json` → Run with+without → Grade → Aggregate → Review → Iterate → Optimize). Iteration-3 maps directly onto stages 2–5.
- **`skills/evaluating-skills/references/behavioral-review.md`** — the reviewer contract. Defines the 5-dimension rubric (`followed-step-ordering`, `used-skill-patterns`, `output-completeness`, `output-quality`, `tool-discipline`) with adaptive dimensions per skill type (Workflow / Reference / Content generation / Methodology). Defines the `material_difference` threshold: ≥2 points on ≥2 dimensions OR ≥1.5 on the mean. Defines the `verdict: AMBIGUOUS` band for the case where scores are too close to call.
- **`skills/evaluating-skills/references/schemas.md`** — `evals.json` and `behavioral_comparison.json` schemas.
- **`skills/evaluating-skills/scripts/aggregate_benchmark.py`** — deterministic `benchmark.json` + `benchmark.md` writer. Reusable as-is.

What iteration-3 adds on top:

1. **Per-eval `assertions[]`** (the only big content blocker) — 18 evals × 3-4 assertions each, hand-authored.
2. **`grader.py`** — a thin Python harness that, for each `(eval, config)` pair, spawns a `claude --print` reviewer subagent with the behavioral-review contract, the eval's assertions, the transcript path, and the SKILL.md context. The reviewer agent emits `behavioral_comparison.json` per Anthropic's grading schema (`expectations[]` with `text`/`passed`/`evidence` fields).
3. **`run_iteration_3.py`** — orchestrator. Mirrors `run_iteration_2.py` structure but invokes `grader.py` per eval after capturing both transcripts.

The marketplace has not shipped `grader.py` yet (the 8-stage loop in `evaluating-skills` is a process spec, not an implementation). Implementing it is the iter-3 code work.

## Per-eval structure

Each eval becomes a JSON file with three required fields and a list of assertions:

```json
{
  "eval_id": "craft-create",
  "expected_skill": "crafting-skills",
  "utterance": "create a new agent skill for parsing PDFs",
  "assertions": [
    {"id": "loaded_skill_md", "type": "consultation",
     "text": "the agent should read crafting-skills/SKILL.md (or invoke the Skill tool on crafting-skills)"},
    {"id": "applied_routing_pattern", "type": "compliance",
     "text": "the agent should follow the Compendium's 'Load when… / Use when… / Do NOT use for…' structure for the new skill's frontmatter"},
    {"id": "decision_router_top", "type": "structure",
     "text": "the new SKILL.md body should start with a Decision Router section"},
    {"id": "no_recipe_overfit", "type": "quality",
     "text": "the new skill should not be a verbatim recipe copy of an existing skill (e.g., should not just say 'follow the PDF parsing tutorial')"}
  ]
}
```

Each assertion is one of:
- `consultation` (did the agent read/invoke the right skill?)
- `compliance` (did the agent follow the skill's specific guidance?)
- `structure` (does the output have the right structural form?)
- `quality` (qualitative judgment — typically requires LLM-as-judge)

## The 4 sub-agents

Per Anthropic's [skill-creator pattern](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) (executor / grader / comparator / analyzer, March 2026), iteration-3 uses 4 sub-agents. Anthropic ships reference implementations for each (`agents/grader.md`, `agents/comparator.md`, `agents/analyzer.md`) which we're adapting to Python `subprocess` runs of `claude --print`:

### 1. Executor

Runs the with-skill and without-skill configurations identically to iteration-2 (Claude Code CLI, `--output-format stream-json`). Anthropic's pattern recommends spawning **both runs in the same turn** (parallel) — we don't have that luxury in this Python harness, but iter-2's per-eval serial execution is acceptable. Per-eval timeout raised to 300s (from 180s) to allow the agent to complete more thorough work.

### 2. Grader

For each `(eval, config)` pair, grades the final response against the eval's `assertions[]`. Each assertion is graded PASS / FAIL with a one-line justification. The grader is itself an LLM call (Claude, with the eval's assertions + the response text + the eval's expected_skill + the relevant SKILL.md).

Grading output schema (per Anthropic's `references/schemas.md`):

```json
{
  "expectations": [
    {"text": "...", "passed": true, "evidence": "..."},
    {"text": "...", "passed": false, "evidence": "..."}
  ]
}
```

**Use `text` / `passed` / `evidence` — NOT `name` / `met` / `details`.** The exact field names matter for downstream tooling (the viewer depends on them).

For the `consultation` assertions, the grader can use a deterministic check on the transcript (was the right SKILL.md read?). For the others, the grader uses LLM-as-judge.

### 3. Comparator

For each eval, computes (per Anthropic's blind-A/B pattern: "give two outputs to an independent agent without telling it which is which"):
- `with_skill_pass_rate` = (assertions PASS in with-skill run) / total assertions
- `without_skill_pass_rate` = (assertions PASS in without-skill run) / total assertions
- `delta` = with − without

And classifies each eval as one of:
- `skill_lifts_quality` (delta > 0.2, with-skill substantially better)
- `skill_neutral` (|delta| ≤ 0.1, similar)
- `skill_hurts` (delta < -0.2, with-skill worse)
- `inconclusive` (transcript truncated, sample too small, etc.)

### 4. Analyzer

Aggregates across all evals. Computes:
- **Overall skill lift** = mean delta across all evals
- **Per-assertion-type pass rate** (consultation vs compliance vs structure vs quality)
- **Per-skill utility score** (this is what the Tessl paper calls the headline metric)
- **Failure pattern clustering** (which assertions fail most often?)
- **Recommended description edits** (for any eval where delta < 0)

Per Anthropic's pattern, also surface patterns the aggregate stats might hide: assertions that always pass regardless of skill (non-discriminating), high-variance evals (possibly flaky), and time/token tradeoffs.

## See also

- `methodology-note-routing-vs-validator.md` — the same instruction-following vs goal-completion distinction in the context of the validator's `\b\w+\b` count vs the routing test's content-word filter.

## Required infrastructure changes

Iteration-3 needs:

0. **Widen the SKILL.md read filter** (fix for the iter-2 metric bug). The
   current `run_iteration_2.py:170` filter only matches reads under
   `REPO / "skills"` and misses reads of `.agents/skills/*/SKILL.md`. The
   `.agents/skills/` folder contains 4 marketplace skills:
   `marketplace-health`, `marketplace-validator`, `ingesting-skills`,
   `releasing-marketplace`. The iter-3 filter should accept both:
   ```python
   MARKETPLACE_SKILL_DIRS = [REPO / "skills", REPO / ".agents/skills"]
   ```
   See `iteration-2/METRIC-BUG-NOTE.md` for the audit-2 case study that
   surfaced this bug (the with-skill agent went off on a tangent reading
   eval infrastructure files and produced a wrong answer; the metric
   reported `material_difference: false` for both runs).

1. **An `assertions.json` per eval** (or a `assertions[]` field added to `evals.json`). 18 evals × ~3-4 assertions each = 54-72 hand-authored assertions. This is the biggest blocker — it's content work, not tooling.

2. **An LLM-as-judge runner** that takes `(assertion, transcript, response_text, skill_context)` → `(pass, justification)`. The grader is best implemented as another subprocess `claude --print` call with a tightly-scoped prompt.

3. **An assertion schema** that supports PASS / FAIL / NOT_APPLICABLE (e.g., a `consultation` assertion against a skill that the model didn't load is NOT_APPLICABLE, not FAIL). NOT_APPLICABLE is excluded from the pass-rate denominator.

4. **A better signal baseline.** The Tessl paper noted that "When the pass rates are identical, make your test cases harder." Several of our 18 utterances are easy enough that the model can answer them without any skill. For iteration-3, the eval set should be rebalanced toward harder, more specific tasks where the skill actually changes the answer.

## Failure modes iteration-3 should catch that iteration-2 cannot

| Failure mode | Caught by iteration-2? | Caught by iteration-3? |
|--------------|:----------------------:|:----------------------:|
| Agent reads the skill but doesn't apply it | No (shows as +1 read) | Yes (compliance assertion FAIL) |
| Agent produces the right answer by coincidence (no skill needed) | No (passes as no_difference) | Yes (consultation assertion NOT_APPLICABLE if no skill read, or skill_lifts_quality=0) |
| Agent produces a structurally wrong output despite reading the skill | No | Yes (structure assertion FAIL) |
| Agent consults a wrong skill (false positive routing) | No (counts as +1 read) | Yes (consultation assertion FAIL on expected_skill) |
| Agent over-applies the skill (recipe overfit) | No | Yes (quality assertion FAIL) |

## Effort estimate

| Step | Effort | Notes |
|------|--------|-------|
| Author 18 `assertions[]` sets | 4-6 hours | This is the bottleneck; mostly content work |
| Implement `grader.py` (LLM-as-judge) | 2 hours | Reuse the with/without-skill runner |
| Implement `comparator.py` | 1 hour | Pure computation |
| Implement `analyzer.py` | 1 hour | Aggregation + report |
| Run iteration-3 | ~3 hours (18 evals × 2 configs × 4 sub-agents × 60s each) | The grader calls add 18 × 2 × 2 = 72 extra LLM calls |
| **Total** | **~1 working day** | Realistic estimate |

## When to run iteration-3

Not now. Iteration-2 (this batch) proves the harness scales and gives a coarse behavioral baseline. Iteration-3 is the "real" eval but requires content authoring that doesn't benefit from being rushed. Run it in a dedicated session with the assertions draft pre-prepared.

## Open question

The Tessl paper measured both instruction-following and goal-completion but found that goal-completion saturates for almost all models. So in practice, **instruction-following is the only metric that varies across model tiers on this kind of task.** Should iteration-3 therefore weight instruction-following rubrics (e.g., "the agent followed the Compendium's prescribed frontmatter structure") heavily, and treat goal-completion rubrics as a sanity check (i.e., they should saturate to 100% — anything less is a real bug)? My take: yes for skills whose value is in workflow encoding (crafting-skills, plan-lifecycle, security), where the discriminator is whether the agent followed the right process. For skills whose value is in knowledge encoding (web-search, rust, engineering-mcp), the goal-completion rubric is the better primary metric. Different skills, different metrics, but within any single skill, pick one and stick to it. Defer to a per-skill decision when iteration-3 actually runs.
