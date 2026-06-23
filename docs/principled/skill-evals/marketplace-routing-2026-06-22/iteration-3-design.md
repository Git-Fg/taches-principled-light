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
     "category": "instruction_following", "points": 30},
    {"id": "applied_routing_pattern", "type": "compliance",
     "text": "the agent should follow the Compendium's 'Load when… / Use when… / Do NOT use for…' structure for the new skill's frontmatter",
     "category": "instruction_following", "points": 40},
    {"id": "decision_router_top", "type": "structure",
     "text": "the new SKILL.md body should start with a Decision Router section",
     "category": "instruction_following", "points": 30},
    {"id": "no_recipe_overfit", "type": "quality",
     "text": "the new skill should not be a verbatim recipe copy of an existing skill (e.g., should not just say 'follow the PDF parsing tutorial')",
     "category": "goal_completion", "points": 40},
    {"id": "produced_valid_skill", "type": "structure",
     "text": "the output file parses as a valid SKILL.md with name + description + license frontmatter",
     "category": "goal_completion", "points": 60}
  ]
}
```

Note: `instruction_following` assertions sum to 30 + 40 + 30 = **100**. `goal_completion` assertions sum to 40 + 60 = **100**. Each category is independently scored on 0–100. The author must size each category's assertions to sum to exactly 100.

Tessl rules (apply directly to our schema):

- **`points` sum to 100 per category** — `instruction_following` and `goal_completion` are scored independently, each on a 0–100 scale.
- **Each assertion is one of 4 types** — `consultation` (did the agent read/invoke the right skill?), `compliance` (did the agent follow the skill's specific guidance?), `structure` (does the output have the right structural form?), `quality` (qualitative judgment — typically requires LLM-as-judge).
- **`category` is one of `instruction_following` or `goal_completion`** — Tessl's two-axis split. Per Tessl Table 4, `instruction_following` is the discriminating metric for skill lift (5.5–22 point delta on the overall score, driven primarily by IF); `goal_completion` saturates near 90% for almost all models.
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

For each `(eval, config)` pair, grades the final response against the eval's `assertions[]`. Each assertion is graded PASS / FAIL with a one-line justification. The grader is itself an LLM call. **Judge model choice**: Tessl uses Sonnet 4.6 as the fixed judge across all experiments (rationale: a strong frontier model gives the most reliable grades). We deliberately deviate to **Haiku 4.5** (same chain as the solver, per project convention to target the VPS port-3456 proxy) — this is a *trade-off*, not an optimization:

- **Lower grading quality** vs Sonnet 4.6 (smaller model, less nuanced on `compliance`/`quality`).
- **Self-grading bias**: Haiku judging Haiku's own solver output. The bias is roughly symmetric between with-skill and without-skill runs (same judge), so the *delta* signal should be more reliable than the absolute scores. But absolute scores may be inflated.
- **Cost**: ~10× cheaper than Sonnet 4.6 at 60 grader calls/eval.

**Mitigation**: run a calibration subset of 5-10 evals with both Haiku and Sonnet 4.5 judges before the full iter-3 run. If the deltas agree within ±5 points, proceed with Haiku; if not, switch to Sonnet.

The judge receives:

- The eval's `assertions[]` (text + points + category + type)
- The transcript JSONL (`with_skill.jsonl` or `without_skill.jsonl`)
- The relevant `SKILL.md` (for the `compliance` assertions)

Grading output schema (per Anthropic's `references/schemas.md`):

```json
{
  "expectations": [
    {"text": "...", "passed": true, "evidence": "...", "points_awarded": 30}
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

For the `consultation` assertions, the grader is **not** needed — those checks are code-based (parse the transcript for `Read` events on the expected skill path, check `Skill` tool invocations). Only `compliance` and `quality` use the LLM judge. `structure` assertions on tool calls use `compare_args` from the schema (also code-based, see below).

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

| Condition | IF score | GC score | Overall (50/50 avg) | Cost |
|---|---|---|---|---|
| Haiku 4.5 without skill | 43.6 | 85.3 | 64.4 | $0.08/scenario |
| Haiku 4.5 with skill | 75.3 | 93.0 | 84.1 | $0.11/scenario |
| **Δ IF** | **+31.7** | — | — | — |
| **Δ GC** | — | **+7.7** | — | — |
| **Δ Overall** | — | — | **+19.7** | **+37%** |

The `Δ` rows are derived (one per column, not aggregated). The "+19.7 overall" matches Tessl's "Skill Δ" headline because the overall score is computed as a 50/50 weighted average of IF and GC: `0.5 × 75.3 + 0.5 × 93.0 = 84.15 ≈ 84.1` and `0.5 × 43.6 + 0.5 × 85.3 = 64.45 ≈ 64.4`. The lift is driven primarily by IF (+31.7) — Tessl's central finding for the Haiku tier.

Our iter-2/3 also targets Haiku 4.5. If our marketplace skills are well-constructed, we should expect similar IF lift (**+25 to +32 points**) when an agent consults the right skill vs doesn't.

## EvaluationCriteria schema (synthesized from tau-bench + Anthropic + Tessl)

The cleanest published schema for structured task evaluation is Sierra's `tau2-bench` `EvaluationCriteria` Pydantic model. It defines 5 components per task, each with a `RewardType` that gates the final score:

| tau-bench field | Maps to iter-3 assertion type | Grader |
|---|---|---|
| `actions[]` (reference tool-call trajectory) | `consultation` (was the skill read?) + `structure` (was the right tool called?) | Code-based; `compare_args[]` lets us check only specific args, ignore others |
| `env_assertions[]` (DB state checks) | `goal_completion` `structure` assertions on the output artifact | Code-based |
| `communicate_info[]` (substring-match in agent msgs) | `compliance` substring checks (lightweight) | Code-based |
| `nl_assertions[]` (LLM-judged NL criteria) | `compliance` + `quality` (model-based) | Model-based |
| `reward_basis[]` (which components gate the score) | **NEW**: per-task `reward_basis` field | Configurable |

### Adapted iter-3 EvaluationCriteria schema

```python
class Assertion(BaseModel):
    id: str
    text: str
    type: Literal["consultation", "compliance", "structure", "quality"]
    category: Literal["instruction_following", "goal_completion"]
    points: int  # within category, sums to 100
    grader: Literal["code", "model"]
    compare_args: Optional[list[str]] = None  # like tau-bench Action.compare_args

class EvaluationCriteria(BaseModel):
    assertions: list[Assertion]
    reward_basis: list[Literal["instruction_following", "goal_completion"]] = [
        "instruction_following", "goal_completion"
    ]
```

### Reward combination: weighted average across categories (Tessl-style)

Tau-bench computes the final reward as a **product** of per-category rewards, where each category is either 1.0 (all assertions pass) or 0.0 (any assertion fails). This is stricter than Tessl's additive approach but matches Anthropic's "the agent either solved the task or didn't" framing.

Iter-3 will follow **Tessl's approach** (verified against Table 4 numerics: `0.5 × 75.3 + 0.5 × 93.0 = 84.15 ≈ 84.1` overall):

- **Within category**: Tessl-style partial credit. Each assertion has a `points` value; `points_awarded` is summed per category and divided by the category total (100) to get a 0-100 category score. 4/5 assertions in `instruction_following` summing to 80 pts → IF score = 80.
- **Across categories**: Weighted average. With default equal weights (`weight["instruction_following"] = 1.0`, `weight["goal_completion"] = 1.0`), the overall score is the simple average: `0.5 × IF + 0.5 × GC`. Per-eval `reward_basis` can omit a category (set its weight to 0) to gate it out — omitted categories are still computed as diagnostics but do not affect the overall score.

Final score formula:

```python
score = 100 * sum(category_avg[c] * weight[c] for c in reward_basis) \
            / sum(weight[c] for c in reward_basis)
```

With default `weight = {"instruction_following": 1.0, "goal_completion": 1.0}` and `reward_basis = ["instruction_following", "goal_completion"]`, this simplifies to `0.5 × IF + 0.5 × GC` — verified to reproduce Tessl Table 4's overall score exactly.

**Why weighted average, not tau-bench's product**: a product treats any category failure as zero, which discards partial-credit signal. For skill efficacy research, we want to know "how much did consulting the skill help?" — a weighted average preserves that signal even when one category fails. For example, an eval where IF=100, GC=60 (full skill compliance, partial goal completion) gets score=80 with averaging vs score=0 with product. The former is more useful for deciding whether to keep the skill.

### `compare_args` pattern (specification match, not verbatim)

Tau-bench's `Action.compare_with_tool_call` only checks the args in `compare_args[]`, ignoring others. Iter-3 adopts this for `structure` assertions on tool calls: a skill that says "call `release_marketplace(version='0.0.2')`" can be checked with `compare_args=['version']` — the agent's exact tool name spelling or other args don't matter. This is the "grade the outcome, not the path" principle from Anthropic applied to specific-arg inspection.

### LLM-as-judge prompt (synthesized from tau-bench + Anthropic)

The grader LLM gets a tightly-scoped system prompt (adapted from `evaluator_nl_assertions.py`). Only `compliance` and `quality` assertions are LLM-judged; `consultation` and `structure` are code-based and bypass this prompt.

```
TASK
- You will be given a list of compliance/quality assertions, a transcript
  of the agent's run, and the relevant skill's SKILL.md.
- Your job is to evaluate whether the agent satisfies each assertion.
- Grade each assertion individually.

FORMAT
- Your response should be a JSON object with the following fields:
- For each assertion, return: {"text": ..., "passed": true|false,
  "evidence": "...", "points_awarded": 0|N}
- A summary: {"instruction_following_score": 0-100,
  "goal_completion_score": 0-100}

If you cannot determine whether an assertion was satisfied from the
transcript and final response, return "passed": false and explain why
in "evidence". Per Anthropic's recommendation, you may also return
"unknown": true if the evidence is genuinely ambiguous — this is
treated as a FAIL for scoring purposes but is flagged in the report
for human review.
```

The model is fixed (Haiku 4.5, same chain as the solver) per Tessl's "fixed judge" methodology. Note the trade-offs documented in the Grader section above (smaller model + self-grading bias vs cost savings).

## SkillsBench: the canonical reference for skill evaluation

[SkillsBench](https://skillsbench.ai) (paper arXiv [2602.12670](https://arxiv.org/abs/2602.12670), v1.2, June 2026) is the first published benchmark measuring how well AI agents use skills. It is **direct prior art** for iter-3 and we should treat its task-package format, verifier design, and lift numbers as the canonical reference.

### Headline numbers (SkillsBench v1.1, 87 tasks, 8 domains)

- **Aggregate lift**: 33.9% → 50.5% with curated skills (+16.6 pp; +25.5% normalized gain)
- **Per-config range**: +4.1 to +25.7 pp across 18 model-harness configs
- **Haiku 4.5 Claude Code**: 8.8% → 30.1% with skills (Δ +21.3 pp; +23.4% normalized)

This is our target configuration. If our 18 marketplace evals are well-calibrated, we should expect similar lift when an agent consults the right skill vs doesn't. Lift below +10 pp would be a red flag — either the skills are too weak, or the evals are too easy.

### SkillsBench task package format (BenchFlow v1.2 native `task.md`)

```text
tasks/<task-id>/
├── task.md                  # YAML frontmatter + human-written prompt
├── environment/
│   ├── Dockerfile           # pinned deps, frozen inputs
│   ├── <bundled inputs>
│   └── skills/
│       └── <skill-name>/    # the skill under test
│           ├── SKILL.md
│           ├── references/
│           └── scripts/
├── oracle/
│   └── solve.sh             # held-out reference (computes, not hardcodes)
└── verifier/
    ├── test.sh              # runs pytest, writes 0/1 to /logs/verifier/reward.txt
    └── test_outputs.py      # outcome-based assertions
```

`task.md` frontmatter (from `CONTRIBUTING.md`):

```yaml
---
schema_version: '1.3'
metadata:
  author_name: ...
  difficulty: medium
  difficulty_explanation: ...
  category: office-white-collar        # one of 8 controlled categories
  subcategory: spreadsheet-analysis
  category_confidence: high
  task_type: [analysis, calculation]   # YAML list
  modality: [spreadsheet]
  interface: [terminal, python]
  skill_type: [domain-procedure]
  tags: [revenue-report, excel-formulas]
verifier:
  type: test-script
  timeout_sec: 900.0
agent:
  timeout_sec: 900.0
environment:
  network_mode: no-network
  build_timeout_sec: 600.0
  os: linux
  cpus: 1
  memory_mb: 4096
  storage_mb: 10240
---
```

### Verifier design (SkillsBench)

`verifier/test.sh`:

```bash
#!/bin/bash
mkdir -p /logs/verifier
uvx --with pytest==8.4.1 --with openpyxl==3.1.5 \
  pytest /verifier/test_outputs.py -rA -v > /logs/verifier/output.txt 2>&1
RC=$?
cat /logs/verifier/output.txt
if [ $RC -eq 0 ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi
exit 0
```

`verifier/test_outputs.py` — pytest functions, outcome-based (file exists, format valid, numerical correctness). **Anti-cheat**: agent cannot read `/tests` or `/solution` during execution.

**For iter-3**, our assertions map naturally to this verifier pattern:

| iter-3 assertion | SkillsBench verifier equivalent |
|---|---|
| `consultation` (skill was read) | `test.sh` reads `~/.claude/skills/<name>/` after agent run; checks SKILL.md read timestamp |
| `structure` (output has right form) | pytest `test_file_exists()`, `test_frontmatter_keys()` |
| `compliance` (followed skill guidance) | model-based grader (SkillsBench does NOT do this — they only check outcomes) |
| `quality` (qualitative judgment) | model-based grader (NOT in SkillsBench) |

SkillsBench is **strictly outcome-based** (deterministic verifiers, no LLM judge). Our iter-3 is broader — we add the LLM judge layer for `compliance` and `quality`. This is a deliberate extension: SkillsBench measures "did the task get done correctly?"; we additionally measure "did the agent consult + follow the skill?" Both signals are valuable for our domain (skill efficacy research).

### Task Quality Rubric (SkillsBench `.agents/skills/task-review/`)

From SkillsBench's task-review skill — what makes a task good:

1. **Authenticity**: real scenario, real data, human-authored prompt and oracle.
2. **Skill quality**: accurate, reusable, useful beyond one task.
3. **Verification**: deterministic, outcome-based, anti-cheat aware.
4. **Instructions**: concise, fair, no skill hints.
5. **Environment**: reproducible Docker image, pinned deps, no leaked skills.

Specific anti-patterns (SkillsBench rejects PRs that have these):

- **Tests that check which tools were used instead of what was produced** — BAD
- **Task-specific skills that only solve one instance** — BAD
- **Hardcoded expected values without independent derivation** — BAD
- **Synthetic toy data when realistic data exists** — BAD
- **AI-generated prompts or oracle logic** — BAD

**For iter-3**: our `compliance` and `quality` assertions (which use LLM-as-judge) should be designed with these anti-patterns in mind. The LLM judge should focus on **outcome quality** (does the artifact satisfy the user request?) rather than **process compliance** (did the agent literally call the named tool?). The `compare_args` pattern (tau-bench) helps with this.

### Key SkillsBench findings relevant to iter-3

1. **Focused skills (≤3 modules) outperform larger bundles.** Our design-hub with 5 sub-skills is in the "borderline" zone; we should monitor whether the hub routing + subskills combo outperforms a flat skill with all 5 modules.
2. **Smaller models with skills can match larger models without them.** On SkillsBench, Haiku 4.5 with skills ≈ Sonnet 4.5 without skills on several domains. This validates the value of skills as model-level leverage.
3. **8 controlled categories** (office-white-collar, software-eng, scientific, infrastructure, multimodal, research, finance, robotics). Our existing evals are already classified; no retrofit needed.
4. **3 trials per task** for confidence intervals. Our iter-3 should consider this — current iter-2/3 design is single-trial per (eval, config), which gives noisier lift estimates.

### Comparison: iter-3 vs SkillsBench

| Dimension | SkillsBench | iter-3 |
|---|---|---|
| Domain | Cross-domain (8 categories, 87 tasks) | Marketplace routing (1 category, 18 tasks) |
| Verifier | Pure deterministic pytest (outcome only) | Hybrid: code + model-based (outcome + compliance + quality) |
| Judge model | None (deterministic) | Fixed Haiku 4.5 |
| Trials per task | 3 | 1 |
| Lift signal | Binary pass/fail | Per-assertion points summing to 100 |
| Anti-cheat | No `/tests`/`/solution` access | N/A (single-agent, isolated) |
| Task difficulty | Tuned for SOTA <50% | Tuned for skill lift signal >5 pp |

We borrow SkillsBench's **task-package format** and **verifier architecture** but extend with **model-based graders** for the compliance + quality dimensions that deterministic tests can't capture.

## Anthropic "Complete Guide" skill testing methodology

Per [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) (Anthropic, January 2026), skill testing covers **three areas** that map directly onto our iter-3 assertion taxonomy:

| Anthropic testing area | iter-3 assertion type | Method |
|---|---|---|
| **Triggering tests** (does the skill load at the right times?) | `consultation` (was the right skill read/invoked?) | Code-based: parse transcript for `Read`/`Skill` events on the expected skill path |
| **Functional tests** (does the skill produce correct outputs?) | `structure` + `compliance` (does output follow skill guidance?) | Hybrid: code-based for structure; model-based for compliance |
| **Performance comparison** (does the skill improve results vs baseline?) | The with-skill vs without-skill A/B comparison (Tessl delta) | Statistical: pass-rate delta + per-category score delta |

**Pro Tip from the guide**: *"We've found that the most effective skill creators iterate on a single challenging task until Claude succeeds, then extract the winning approach into a skill. This leverages Claude's in-context learning and provides faster signal than broad testing."*

**For iter-3**: this argues for *paired eval authoring* — for each marketplace skill, find a single real failure mode the skill is designed to prevent, then write the assertion set around that specific failure. Don't try to cover all possible failure modes at once. A focused eval that catches the dominant failure mode is more valuable than a broad eval that catches no failures.

### Three skill categories (Anthropic)

The guide classifies skills into 3 categories, useful for understanding what our marketplace skills encode:

1. **Document & Asset Creation**: deterministic output formatting (frontend-design, docx, pptx, xlsx). **SkillsBench lift: high** — these are workflow-encoded.
2. **Workflow Automation**: multi-step processes (skill-creator). **SkillsBench lift: high** — procedural knowledge the model lacks.
3. **MCP Enhancement**: workflow guidance on top of MCP tools (sentry-code-review). **SkillsBench lift: medium** — depends on tool stability.

Our marketplace spans all 3:
- Category 1: `pdf-design-guide`, `design-hub` subskills (palette/typography/conventions)
- Category 2: `crafting-skills`, `releasing-marketplace`, `ingesting-skills`, `plan-lifecycle`, `task-lifecycle`, `evaluating-skills`
- Category 3: `engineering-mcp`, `security`, `rust` (MCP-like domain guidance)

Tessl Table 5 predicts the highest lift for Category 2 (workflow automation) and the lowest for Category 3 (knowledge encoding), consistent with SkillsBench's data.

### Iteration signals (from Anthropic guide)

For each marketplace skill, the iteration signals are:

- **Undertriggering** (skill doesn't load when it should): `consultation` assertion fails (PASS but expected_skill not consulted). Solution: add keywords to `description`.
- **Overtriggering** (skill loads for irrelevant queries): `consultation` assertion succeeds but `compliance`/`quality` assertions fail. Solution: add negative triggers to `description` (this is exactly our `Do NOT use for X` clause).
- **Execution issues** (inconsistent results, errors): `compliance` assertion fails randomly across trials. Solution: improve SKILL.md body, add error handling.

Iter-3 per-eval results can be classified by these three signals to produce actionable description/skill edits.

## See also

- `methodology-note-routing-vs-validator.md` — the same instruction-following vs goal-completion distinction in the context of the validator's `\b\w+\b` count vs the routing test's content-word filter.

## Required infrastructure changes

Iteration-3 needs:

0. **Verify SKILL.md read filter is widened** (the fix from iter-2 commit
   `069b31c` is already in place at `scripts/run_iteration_2.py:30,177-178`).
   The filter `MARKETPLACE_SKILL_DIRS = [REPO / "skills", REPO / ".agents/skills"]`
   matches reads of marketplace skills in either folder. **Action when iter-3
   starts**: re-run the audit-2 case study from `iteration-2/METRIC-BUG-NOTE.md`
   with the new filter and confirm `lint-1` reports 2 reads (was 0 before the
   fix). The 4 `.agents/skills/` skills are: `marketplace-health`,
   `marketplace-validator`, `ingesting-skills`, `releasing-marketplace`. Note:
   these are marketplace-maintenance *meta-skills*; reads of them count as
   "consulted a marketplace skill" for the iter-3 `consultation` assertion
   but should probably be excluded from "user-facing skill consultation"
   metrics (separate flag, TBD).

1. **An `assertions.json` per eval** (or a `assertions[]` field added to
   `evals.json`). **18 evals × 5 assertions each = 90 hand-authored
   assertions**. With each assertion needing a category (IF or GC) + points
   (summing to 100 per category) + type + text + grader (code/model) +
   compare_args (optional) + reference solution, this is roughly 6-9 hours
   of content authoring. This is the biggest blocker — content, not tooling.
   Reuse the `craft-create` example (lines 32-57) as the template; aim for
   3 IF assertions summing to 100 + 2 GC assertions summing to 100 (or
   4+3, 3+4, etc.) per eval.

2. **An LLM-as-judge runner** that takes `(assertion, transcript, response_text, skill_context)` → `(pass, justification)`. The grader is best implemented as another subprocess `claude --print` call with a tightly-scoped prompt. Only `compliance` and `quality` assertions need the judge; `consultation` and `structure` are code-based and bypass it.

3. **An assertion schema** that supports PASS / FAIL / UNKNOWN. UNKNOWN is
   returned by the LLM judge when the evidence is genuinely ambiguous; it is
   treated as FAIL for scoring but flagged for human review. There is **no**
   NOT_APPLICABLE state in iter-3 — `consultation` assertions are binary by
   design (the skill was read or wasn't) and are graded code-based, so
   "not_applicable" cannot arise.

4. **A better signal baseline.** The Tessl paper noted that "When the pass rates are identical, make your test cases harder." Several of our 18 utterances are easy enough that the model can answer them without any skill. For iteration-3, the eval set should be rebalanced toward harder, more specific tasks where the skill actually changes the answer.

## Failure modes iteration-3 should catch that iteration-2 cannot

| Failure mode | Caught by iteration-2? | Caught by iteration-3? |
|--------------|:----------------------:|:----------------------:|
| Agent reads the skill but doesn't apply it | No (shows as +1 read) | Yes (compliance assertion FAIL) |
| Agent produces the right answer by coincidence (no skill needed) | No (passes as no_difference) | Yes (consultation assertion FAIL — agent did not consult the expected skill; skill_lifts_quality=0) |
| Agent produces a structurally wrong output despite reading the skill | No | Yes (structure assertion FAIL) |
| Agent consults a wrong skill (false positive routing) | No (counts as +1 read) | Yes (consultation assertion FAIL on expected_skill) |
| Agent over-applies the skill (recipe overfit) | No | Yes (quality assertion FAIL) |

## Effort estimate

| Step | Effort | Notes |
|------|--------|-------|
| Author 18 `assertions[]` sets | 6-9 hours | 18 × 5 assertions = 90 hand-authored assertions; each requires category + points (summing to 100/category) + reference solution |
| Implement `grader.py` (LLM-as-judge) | 2 hours | Reuse the with/without-skill runner; only `compliance`+`quality` need the judge |
| Implement `comparator.py` | 1 hour | Pure computation; weighted-average formula from line 219 |
| Implement `analyzer.py` | 1 hour | Aggregation + report; per-skill lift, per-eval verdict distribution |
| Calibrate judge model (Haiku vs Sonnet 4.5) | 1 hour | Run 5-10 evals with both judges; check delta agreement |
| Run iteration-3 | ~3 hours (18 evals × 2 configs × ~60s each) | Plus ~60 LLM judge calls (one per compliance+quality assertion per config) |
| **Total** | **~1.5 working days** | Realistic estimate; depends on judge calibration findings |

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
- **Step 3**: Build balanced problem sets. Our set is **18 evals = 9 marketplace-category + 9 local-meta** (per `evals/evals.json`). Need review for class balance — most local-meta evals are easy enough that the model can answer them without any skill.
- **Step 4**: Build a robust eval harness with a stable environment. We use `/tmp/empty-claude-project` as the baseline for without-skill runs (no repo state leaks); with-skill runs use the marketplace repo.
- **Step 5**: Design graders thoughtfully. (See table above.)
- **Step 6**: Check the transcripts. (Run after iter-3.)
- **Step 7**: Monitor for capability eval saturation. (Run after iter-3.)
- **Step 8**: Keep evaluation suites healthy. (Long-term; out of iter-3 scope.)
