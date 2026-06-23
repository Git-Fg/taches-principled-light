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

Each eval becomes a JSON file with three required fields and a list of assertions. Adopt the [Tessl framework rubric schema](https://arxiv.org/abs/2606.17819) ([huggingface dataset](https://huggingface.co/datasets/tesslio/task-evals-for-skills)) as the canonical format, simplified for our 18 marketplace evals:

```json
{
  "eval_id": "craft-create",
  "expected_skill": "crafting-skills",
  "utterance": "create a new agent skill for parsing PDFs",
  "assertions": [
    {"id": "consulted_crafting_skills", "type": "consultation",
     "text": "the agent should read crafting-skills/SKILL.md (or invoke the Skill tool on crafting-skills)",
     "category": "instruction_following", "points": 20},
    {"id": "applied_routing_pattern", "type": "compliance",
     "text": "the agent should follow the Compendium's 'Load when… / Use when… / Do NOT use for…' structure for the new skill's frontmatter",
     "category": "instruction_following", "points": 25},
    {"id": "decision_router_top", "type": "structure",
     "text": "the new SKILL.md body should start with a Decision Router section",
     "category": "instruction_following", "points": 20},
    {"id": "no_recipe_overfit", "type": "quality",
     "text": "the new skill should not be a verbatim recipe copy of an existing skill (e.g., should not just say 'follow the PDF parsing tutorial')",
     "category": "goal_completion", "points": 15},
    {"id": "produced_valid_skill", "type": "structure",
     "text": "the output file parses as a valid SKILL.md with name + description + license frontmatter",
     "category": "goal_completion", "points": 20}
  ]
}
```

Tessl rules (apply directly to our schema):

- **`points` sum to 100 per category** — `instruction_following` and `goal_completion` are scored independently, each on a 0–100 scale.
- **Each assertion is one of 4 types** — `consultation` (did the agent read/invoke the right skill?), `compliance` (did the agent follow the skill's specific guidance?), `structure` (does the output have the right structural form?), `quality` (qualitative judgment — typically requires LLM-as-judge).
- **`category` is one of `instruction_following` or `goal_completion`** — Tessl's two-axis split. Per Tessl Table 4, `instruction_following` is the discriminating metric for skill lift (5.5–22 point delta with skill vs without); `goal_completion` saturates near 90% for almost all models.
- **Assertions are hidden from the solver agent** and used only by the judge agent.

### Per-category guidance (from Tessl + Anthropic)

| Category | What it measures | When to use |
|---|---|---|
| `instruction_following` | Did the agent follow the preferences encoded in the skill? Library choices, structural conventions, naming rules, prohibited patterns, required steps. (Tessl verbatim.) | When the skill encodes a specific opinionated workflow or convention. |
| `goal_completion` | Did the solution produce the requested outputs and is the final artifact correct? (Tessl verbatim.) | When the skill encodes knowledge or capabilities unavailable to the base agent. |

For each assertion type:
- `consultation` (did the agent read/invoke the right skill?) — deterministic check on the transcript (was the right SKILL.md read?). Often a 20-pt "gating" assertion.
- `compliance` (did the agent follow the skill's specific guidance?) — check transcript evidence + output for adherence to specific patterns.
- `structure` (does the output have the right structural form?) — check output artifact's structure (frontmatter, required sections).
- `quality` (qualitative judgment) — LLM-as-judge for taste / style / completeness.

## The 4 sub-agents

Per Anthropic's [skill-creator pattern](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) (executor / grader / comparator / analyzer, March 2026), iteration-3 uses 4 sub-agents. Anthropic ships reference implementations for each (`agents/grader.md`, `agents/comparator.md`, `agents/analyzer.md`) which we're adapting to Python `subprocess` runs of `claude --print`:

### 1. Executor

Runs the with-skill and without-skill configurations identically to iteration-2 (Claude Code CLI, `--output-format stream-json`). Anthropic's pattern recommends spawning **both runs in the same turn** (parallel) — we don't have that luxury in this Python harness, but iter-2's per-eval serial execution is acceptable. Per-eval timeout raised to 300s (from 180s) to allow the agent to complete more thorough work.

### 2. Grader

For each `(eval, config)` pair, grades the final response against the eval's `assertions[]`. Each assertion is graded PASS / FAIL with a one-line justification. The grader is itself an LLM call. **Per Tessl's methodology, use a fixed strong model for the judge across all experiments** (they use Sonnet 4.6; we use Haiku since that's our iteration-2/3 target — same chain ensures consistent scoring).

The judge receives:
- The eval's `assertions[]` (text + points + category + type)
- The transcript JSONL (`with_skill.jsonl` or `without_skill.jsonl`)
- The relevant `SKILL.md` (for the `compliance` assertions)

Grading output schema (per Anthropic's `references/schemas.md`):

```json
{
  "expectations": [
    {"text": "...", "passed": true, "evidence": "...", "points_awarded": 20}
  ],
  "summary": {
    "instruction_following_score": 75.0,
    "goal_completion_score": 90.0,
    "overall_score": 82.5,
    "passed": 4, "failed": 1, "total": 5
  }
}
```

**Use `text` / `passed` / `evidence` / `points_awarded` — NOT `name` / `met` / `details`.** The exact field names matter for downstream tooling.

For the `consultation` assertions, the grader can use a deterministic check on the transcript (was the right SKILL.md read?). For the others, the grader uses LLM-as-judge.

### 3. Comparator

For each eval, computes (per Tessl's with-skill vs without-skill methodology and Anthropic's blind-A/B pattern: "give two outputs to an independent agent without telling it which is which"):

- `with_skill_instruction_following_score` (0–100)
- `without_skill_instruction_following_score` (0–100)
- `with_skill_goal_completion_score` (0–100)
- `without_skill_goal_completion_score` (0–100)
- `instruction_following_delta` = with − without
- `goal_completion_delta` = with − without
- `overall_delta` = weighted average delta (Tessl uses equal weighting; we may choose instruction-following-heavy for workflow-encoding skills)

And classifies each eval as one of:
- `skill_lifts_quality` (overall_delta > 5 points per Tessl Table 4 norms; with-skill substantially better)
- `skill_neutral` (|overall_delta| ≤ 5 points, similar)
- `skill_hurts` (overall_delta < -5 points, with-skill worse)
- `skill_redundant` (instruction_following_delta ≈ 0; the model already captures the skill's behavior — per Tessl "Implications for skill authors": "the skill can be removed")
- `inconclusive` (transcript truncated, sample too small, etc.)

Per Tessl Table 4 (with-skill vs without-skill on real skills across 19 models), the typical delta is **5.5–22 points** on the overall score, driven primarily by `instruction_following`. `goal_completion` deltas are smaller and saturate near 90% for frontier models.

### 4. Analyzer

Aggregates across all evals. Computes:
- **Overall skill lift** = mean `overall_delta` across all evals (Tessl reports this as the headline metric)
- **Per-category skill lift** = mean `instruction_following_delta` and `goal_completion_delta` separately
- **Per-skill utility score** (Tessl's term) — mean overall delta for each expected_skill
- **Per-eval verdict distribution** (skill_lifts_quality / skill_neutral / skill_hurts / skill_redundant / inconclusive)
- **Failure pattern clustering** (which assertion `text` patterns fail most often?)
- **Recommended description edits** (for any eval where delta < 0)

Per Tessl Table 5, the uplift varies dramatically by skill domain:
- **Media & File Processing: +38.1** (highest — skills encode strict workflows)
- **Security & Compliance: +30.3**
- **Testing, QA & Code Quality: +16.7** (lowest — skills describe principles not procedures)
- **API Development & Integration: +25.9**

Heuristic from Tessl: "when knowledge can be captured as a workflow, it is a strong candidate for a skill." Marketplace skills that fit this pattern (pdf-design-guide, releasing-marketplace, ingesting-skills, marketplace-validator, marketplace-health, security) should expect **+20–35 point uplift** in iter-3. Methodology-heavy skills (crafting-skills, evaluating-skills, general-critic) may show smaller uplift because they encode principles rather than procedures.

Per Anthropic's pattern, also surface patterns the aggregate stats might hide: assertions that always pass regardless of skill (non-discriminating), high-variance evals (possibly flaky), and time/token tradeoffs.

### Haiku 4.5 baseline reference (Tessl Table 4)

Per Tessl's published benchmark:

| Condition | IF score | GC score | Overall | Cost |
|---|---|---|---|---|
| Haiku 4.5 without skill | 43.6 | 85.3 | 64.4 | $0.08/scenario |
| Haiku 4.5 with skill | 75.3 | 93.0 | 84.1 | $0.11/scenario |
| **Δ** | **+31.7** | **+7.7** | **+19.7** | **+37%** |

Our iter-2/3 also targets Haiku 4.5. If our marketplace skills are well-constructed, we should expect similar instruction-following lift (+20 to +30 points) when an agent consults the right skill vs doesn't.

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

## Grader type selection (Anthropic methodology)

Per [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), three grader types — choose the right one per assertion:

| Type | Methods | When to use |
|---|---|---|
| **Code-based** | string match, binary tests, static analysis, outcome verification, tool-call verification, transcript analysis | When the assertion is deterministic (consultation, structure, tool-use). Fast, cheap, reproducible. |
| **Model-based** | rubric-based scoring, natural-language assertions, pairwise comparison, reference-based evaluation, multi-judge consensus | When the assertion is open-ended (compliance, quality). Flexible but non-deterministic. |
| **Human graders** | SME review, crowdsourced judgment, A/B testing, inter-annotator agreement | Calibration only. Reserve for subjective/ambiguous tasks. |

For each task, scoring is **weighted** (combined scores hit a threshold), **binary** (all must pass), or **hybrid**. Tessl uses weighted (per-category 0–100 sums); our iter-3 follows the same.

### Per-assertion grader recommendation

| Assertion `type` | Recommended grader | Why |
|---|---|---|
| `consultation` | code-based | Deterministic: was `SKILL.md` read? Was the Skill tool invoked? |
| `structure` | code-based | Deterministic: does the output have the right frontmatter keys, section ordering, etc. |
| `compliance` | model-based | Judgment call: did the agent follow the skill's specific guidance? |
| `quality` | model-based | Open-ended judgment: was the output tasteful, complete, non-overfit? |

For model-based graders, Anthropic recommends:

- **Give the LLM a way out** — instruction to return `"Unknown"` when uncertain.
- **Grade each dimension with an isolated LLM-as-judge** rather than one grader per dimension.
- **Calibrate LLM judges with human experts** before trusting the score.

## Canonical eval task format (Anthropic YAML)

Per Anthropic's example, the canonical eval task schema (adapted for our 18 marketplace evals):

```yaml
task:
  id: craft-create
  desc: |
    Create a new agent skill for parsing PDFs.
  graders:
    - type: deterministic_tests   # consultation: did agent read crafting-skills/SKILL.md?
      transcript_checks:
        - read_file: skills/crafting-skills/SKILL.md
    - type: llm_rubric            # compliance: did agent follow the Compendium?
      rubric: prompts/crafting-skill-quality.md
      assertions:
        - "Description starts with 'Load when…'"
        - "Description has Do NOT use for X clause"
        - "Body has Decision Router section"
    - type: state_check           # goal_completion: is the output a valid SKILL.md?
      expect:
        - file_exists: skills/pdf-parser/SKILL.md
        - frontmatter_keys: [name, description, license]
  tracked_metrics:
    - type: transcript
      metrics: [n_turns, n_toolcalls, n_total_tokens]
    - type: latency
      metrics: [time_to_first_token, time_to_last_token]
```

Our 18-eval set's JSON form follows this structure (with `assertions[]` flat list + `points` + `category` from Tessl). The YAML form is for human authoring; JSON is for the harness.

## Anti-patterns to avoid

Anthropic's "Demystifying evals" lists specific anti-patterns that have bitten even sophisticated teams:

1. **Don't check tool-call order as success.** "There is a common instinct to check that agents followed very specific steps like a sequence of tool calls in the right order. We've found this approach too rigid and results in overly brittle tests, as agents regularly find valid approaches that eval designers didn't anticipate. So as not to unnecessarily punish creativity, it's often better to grade what the agent produced, not the path it took."
   - **Exception for iter-3**: `consultation` assertions *do* check the path (was the skill read?). Justified because: (a) we want to measure skill *reach* — without a consultation check, a skill that's never consulted gets 100% goal_completion (since goal-completion saturates); (b) consultation is a yes/no fact, not a sequence.

2. **0% pass rate across many trials = broken task.** "With frontier models, a 0% pass rate across many trials (i.e. 0% pass@100) is most often a signal of a broken task, not an incapable agent, and a sign to double-check your task specification and graders. For each task, it's useful to create a reference solution: a known working output that passes all graders."
   - **For iter-3**: each of our 18 assertions needs a reference solution. Anthropic + Tessl agree.

3. **Build partial credit in.** "For tasks with multiple components, build in partial credit. A support agent that correctly identifies the problem and verifies the customer but fails to process a refund is meaningfully better than one that fails immediately."
   - **For iter-3**: Tessl's per-category 0–100 scoring already gives partial credit; we don't need to add it.

4. **Watch for eval saturation.** "An eval at 100% tracks regressions but provides no signal for improvement. Eval saturation occurs when an agent passes all of the solvable tasks, leaving no room for improvement."
   - **For iter-3**: if iter-3 returns 100% on a category across all 18 evals, the category has saturated. Harder tasks are needed.

5. **Read the transcripts.** "You won't know if your graders are working well unless you read the transcripts and grades from many trials... Failures should seem fair: it's clear what the agent got wrong and why."
   - **For iter-3**: step 4 (review) of the iter-2 loop should always include reading 5–10 transcripts of failed evals.

6. **20–50 tasks is a great start.** "We see teams delay building evals because they think they need hundreds of tasks. In reality, 20–50 simple tasks drawn from real failures is a great start."
   - **For iter-3**: our 18 evals is at the lower end of Anthropic's recommended range; if iter-3 surfaces interesting patterns, we should grow to 30–50.

## Eval author guidance

From Anthropic's roadmap, applied to our 18 marketplace evals:

- **Step 0**: Start now — don't wait for the perfect suite. (We're starting with 18; iterate.)
- **Step 1**: Start with what you already test manually. The `evals.json` set is hand-authored from prior routing-test failures (the 7W/0T/3L baseline at 904e11e). ✓
- **Step 2**: Write unambiguous tasks with reference solutions. For each of our 18 evals, author a known-good response that passes all assertions. (Blocker for iter-3.)
- **Step 3**: Build balanced problem sets. Our set has 10 marketplace-category + 8 local-meta + 1 critic + 5 research/etc — needs review for class balance.
- **Step 4**: Build a robust eval harness with a stable environment. We use `/tmp/empty-claude-project` as the baseline for without-skill runs (no repo state leaks); with-skill runs use the marketplace repo.
- **Step 5**: Design graders thoughtfully. (See table above.)
- **Step 6**: Check the transcripts. (Run after iter-3.)
- **Step 7**: Monitor for capability eval saturation. (Run after iter-3.)
- **Step 8**: Keep evaluation suites healthy. (Long-term; out of iter-3 scope.)
