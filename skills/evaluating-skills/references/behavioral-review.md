# Behavioral Review

The reviewer subagent contract for stage 4. This is the core innovation over Anthropic's `skill-creator`, which detects the skill *load event* via Claude-Code-specific command-file injection. We measure *behavioral consequence* on raw transcripts instead — universal across any JSONL-emitting runtime, and strictly more informative.

## Why behavioral, not load-event

A skill can be:
- **loaded then ignored** — the agent consulted the SKILL.md but didn't follow it. Load-event model says "triggered ✓"; reality says the skill failed.
- **behaviorally embodied without an explicit load** — the agent already knew the pattern; the skill added nothing. Load-event model says "not triggered ✗"; reality says the skill is redundant.

Only reviewing the full transcript distinguishes these. The output is an *annotated transcript* + per-dimension scores + a `material_difference` flag — not a boolean.

## Inputs

- `with_skill.jsonl` — raw transcript of the run where the skill was available
- `without_skill.jsonl` — raw transcript of the baseline run (same prompt, skill absent)
- the skill's `SKILL.md`
- the eval's `expectations[]` (may be empty — you draft them)

## Process

### Step 1 — Read both transcripts end-to-end

Note the prompt, the tool-call sequence, the final output, any errors. If the transcript is a JSONL stream of events (kimi `stream-json`, codex `--json`, reasonix `agent.NewTextSink`), the meaningful events are usually: assistant text, `tool_calls`, tool results, errors, usage. Skip pure progress/spinner events.

### Step 2 — Annotate each transcript

For each run, mark where behavior **aligned with** or **deviated from** the skill's explicit guidance. Self-edit the JSONL by adding an `annotation` field to the relevant event, or write a sibling `<run>.annotations.jsonl` overlay keyed by line/event id. Quotable evidence is the goal.

Alignment markers to look for:
- Did the agent follow the skill's documented step ordering?
- Did it use the skill's bundled scripts/references where the skill told it to?
- Did it produce the output structure the skill specifies?
- Did it handle the edge cases the skill warns about?

Deviation markers:
- Did it skip a step the skill mandates?
- Did it improvise a path the skill exists to prevent?
- Did it produce a different output shape?
- Did it hit an error the skill's guidance would have avoided?

### Step 3 — Score both runs on the rubric

Default dimensions (configurable — calibrate to the skill's domain before trusting):

| Dimension | What it measures | 1 | 5 |
|---|---|---|---|
| `followed-step-ordering` | Did the agent follow the skill's documented workflow? | improvised freely | exact order |
| `used-skill-patterns` | Did it use the skill's scripts/references/templates? | reinvented everything | used bundled assets |
| `output-completeness` | Did the output meet the eval's `expected_output`? | missing pieces | complete |
| `output-quality` | Is the output good (accuracy, clarity)? | wrong or poor | excellent |
| `tool-discipline` | Did it use tools appropriately (no wasted calls, no errors)? | many errors/waste | clean |

Score 1–5 per dimension per run. Cite transcript evidence for every score.

**Adaptive dimension selection by skill type.** The 5 dimensions above are calibrated for *workflow* skills (the most common type). For other skill types, swap the dimensions to ones the skill is actually supposed to influence:

| Skill type | Drop | Add | Why |
|---|---|---|---|
| **Workflow** (e.g. `pdf`, `code-review`) | — | (use all 5 defaults) | Steps + patterns + output are the natural axes |
| **Reference** (e.g. `pdf-design-guide`, `typography-guide`) | `followed-step-ordering` | `applied-correct-pattern`, `pattern-completeness` | Reference skills are lookup tables; there's no "step order" — the question is whether the right pattern was applied |
| **Content generation** (e.g. `general-critic` writing outputs, design `canvas-design`) | `tool-discipline` | `style-adherence`, `voice-consistency` | Content generation is judged on the output artifact, not tool use |
| **Methodology / framework** (e.g. `crafting-skills`, `evaluating-skills`) | `followed-step-ordering` | `framework-applied`, `step-coverage` | The skill teaches a methodology; the question is whether the framework was applied end-to-end, not whether steps were followed literally |

Document the dimension set you used in `behavioral_comparison.json` (e.g. `"dimensions_used": ["applied-correct-pattern", "pattern-completeness", "output-completeness", "output-quality", "tool-discipline"]`) so a reader can re-derive the verdict.

### Step 4 — Emit `behavioral_comparison.json`

Per the schema in `schemas.md`: per-dimension `with_skill` / `without_skill` / `delta` / `evidence_with` / `evidence_without`, plus `expectations[]` (same field names as Anthropic's `grading.json`), `verdict`, and `material_difference`.

`material_difference` is the load-bearing field. Set it `true` only if the with-skill run scored meaningfully higher on dimensions the skill is supposed to influence. A skill that changes nothing sets it `false` — that is the signal to either rewrite the skill or delete it.

**Default threshold** (so two reviewers agree): `material_difference = true` when the with-skill run beats the baseline by **≥ 2 points on at least 2 dimensions**, OR by **≥ 1.5 on the mean across all dimensions**. Otherwise `false`. State the threshold you used in the `summary` so a reader can re-derive the verdict. If the result lands in the band between (e.g. one dimension +3, everything else +0), set `verdict: AMBIGUOUS` and re-review rather than guessing.

### Step 5 — Loop if ambiguous

If `verdict` is `AMBIGUOUS` (scores too close, or evidence thin), re-review with a narrower focus, or spawn a second reviewer with the `general-critic` HIGH/MEDIUM/LOW contract for a tie-break. Do not declare a skill good on ambiguous evidence.

## Trigger-eval queries (for OPTIMIZE mode)

When optimizing the skill's `description` frontmatter, scaffold the eval set with the trigger-eval harness rather than writing it by hand:

```bash
python scripts/trigger_eval.py init --out /tmp/queries.json --skill-name <name> --n 20
# (the script warns on stderr when --n < 16, the AGENTS.md Description-as-
# Routing-Signal rule 7 minimum: 8-10 should-trigger + 8-10 should-not.)
```

The discipline that makes this work:

- **Realistic, not abstract.** Include file paths, column names, personal context, typos, casual speech. "ok so my boss just sent me this xlsx..." not "format this data".
- **Should-not must be near-misses.** "Write a fibonacci function" as a negative for a PDF skill tests nothing. The valuable negatives share keywords/concepts with the skill but need something else — adjacent domains where a naive keyword match would wrongly fire.
- **Substantive enough to need the skill.** Trivial one-step queries ("read file X") won't trigger any skill regardless of description quality, because the agent handles them with basic tools. The query must be complex enough that consulting the skill would actually help.

For each query, the behavioral judgment is: did the with-skill run behave as the skill intends, and did the without-skill run behave differently? (Not: was the skill *loaded*.) After collecting ≥3 runs per query, use `trigger_eval.py score` (with the 60/40 train/val split from `trigger_eval.py split`) to compute the trigger-rate report; pick the description by **validation** pass rate, not train pass rate. See `references/trigger-eval-guide.md` for the full methodology.
