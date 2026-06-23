# Deep Research — Evidence Document

Cited findings per sub-question from `analysis.md`. Sources: `[SC]` = skill-creator SKILL.md; `[SC/schemas]` = references/schemas.md; `[SC/run_eval]` = scripts/run_eval.py; `[SC/run_loop]` = scripts/run_loop.py; `[SC/grader]` = agents/grader.md; `[BP]` = Anthropic best-practices page; `[AG]` = agentskills.io; `[CS]` = local crafting-skills; `[CS/selftest]` = crafting-skills/references/skill-self-testing.md; `[GC]` = local general-critic; `[RAP]` = local reviewing-and-polishing.

---

## SQ-1: The canonical 5-stage loop and runtime boundaries

**Finding (interim verdict):** skill-creator's loop is **8 stages, of which 4 are runtime-specific** — not 5 as the hypothesis guessed. Corrected model:

| # | Stage | Artifact in | Artifact out | Runtime-specific? |
|---|---|---|---|---|
| 1 | Capture intent | conversation | — | **agnostic** |
| 2 | Write `evals.json` | interview | `evals/evals.json` | **agnostic** (pure JSON) |
| 3 | Run with-skill + baseline | `evals.json` | `<workspace>/iteration-N/eval-X/{with_skill,without_skill}/outputs/` | **specific** (subagents or inline) |
| 4 | Grade | runs + `evals.json` | `<run-dir>/grading.json` | **specific** (grader subagent or inline self-grade) |
| 5 | Aggregate | `grading.json` × N + `timing.json` | `benchmark.json` + `benchmark.md` | **agnostic** (pure computation) |
| 6 | Review | `benchmark.json` + outputs | `feedback.json` | **specific** (HTML viewer / static HTML / inline markdown) |
| 7 | Iterate (rewrite skill) | `feedback.json` + transcripts | updated `SKILL.md` | **agnostic** |
| 8 | Optimize trigger description | trigger-eval set | improved `description` frontmatter | **specific** (needs N parallel runs + editor LLM) |

So the hypothesis "only stages 3 and 5 are runtime-specific" is **too optimistic** — stages 4, 6, and 8 are also runtime-specific. But all three have clean agnostic fallbacks, which is what makes a generalistic skill viable. `[SC]` lines 130–260; `[SC/schemas]` confirms artifact locations.

---

## SQ-2: `evals.json` schema

```json
{
  "skill_name": "example-skill",
  "evals": [
    { "id": 1, "prompt": "...", "expected_output": "...",
      "files": ["evals/files/sample1.pdf"],
      "expectations": ["The output includes X", "The skill used script Y"] }
  ]
}
```
`[SC/schemas]` §evals.json. **Closed field set:** `skill_name`, `evals[].{id, prompt, expected_output, files[], expectations[]}`. `expectations` may be empty at write-time and filled during stage 4 — `[SC]` Step 2 explicitly says "assertions can be empty for now" while runs are in flight.

**Generalization note:** this schema is already runtime-agnostic. No change needed for the generalistic skill.

---

## SQ-3: `grading.json` — the grader contract

Exact field names the viewer depends on (`[SC/schemas]` §grading.json, `[SC]` Step 4):

```json
{
  "expectations": [
    { "text": "...", "passed": true, "evidence": "Found in transcript Step 3: ..." }
  ],
  "summary": { "passed": 2, "failed": 1, "total": 3, "pass_rate": 0.67 },
  "execution_metrics": { "tool_calls": {...}, "total_tool_calls": 15, "errors_encountered": 0, ... },
  "timing": { "total_duration_seconds": 191.0 },
  "claims": [ { "claim": "...", "type": "factual", "verified": true, "evidence": "..." } ],
  "eval_feedback": { "suggestions": [ { "assertion": "...", "reason": "..." } ] }
}
```

**Critical grader behaviors** (`[SC/grader]`):
- Verdict is `PASS` only when evidence reflects **genuine task completion, not surface compliance** ("correct filename but empty/wrong content" is FAIL).
- Grader **extracts and verifies implicit claims** beyond the declared expectations — catches issues the eval author missed.
- Grader **critiques the assertions themselves** — flags trivially-passing ones in `eval_feedback`. "A passing grade on a weak assertion is worse than useless — it creates false confidence."
- `execution_metrics` comes from a separate `metrics.json` the *executor* writes; grader just reads it.

**Generalization:** the grader is a Read + reason task. Any agent can do it inline. The local `[GC]` general-critic already implements the "loop until PASS" contract — it can be the inline grader with the schema above as its output format.

---

## SQ-4: `benchmark.json` — inline-computable

`[SC/schemas]` §benchmark.json. Key structure: `metadata`, `runs[]` (each with `configuration: "with_skill"|"without_skill"`, `result.pass_rate/time_seconds/tokens`), `run_summary` (per-config `mean/stddev/min/max` + `delta`), `notes[]`.

**Computable inline:** yes. `aggregate_benchmark.py` is pure Python — mean, stddev, min, max, delta. No subprocess needed. The generalistic skill can teach the formula and let the orchestrator compute it with Bash + a small inline script, or by hand for small N.

**Caveat:** meaningful stddev needs ≥3 runs per configuration. `[SC/run_eval]` default `runs_per_query` and `[SC/run_loop]` both use 3. In headless/inline mode where each "run" is a full agent task, N=3 triples cost — the skill must make N a conscious choice, not a silent default.

---

## SQ-5: Trigger-detection without `claude -p` (SUPERSEDED — see "Resolution" section below)

`[SC/run_eval]` detection logic, distilled:
1. Write a command-file to `.claude/commands/<skill>-skill-<uuid>.md` containing the skill's description in frontmatter (this makes it appear in Claude's `available_skills`).
2. Run `claude -p <query> --output-format stream-json --verbose --include-partial-messages`.
3. Parse the stream: a `content_block_start` with `tool_use` whose name is `Skill` or `Read`, followed by an `input_json_delta` whose accumulated JSON contains the command-file name → **triggered**.
4. Any *other* tool_use first → **not triggered** (Claude handled it with basic tools).

**Original verdict:** this is deeply Claude-Code-specific; the abstract pattern needs a different injection surface and trace parser per runtime.

**Superseded verdict (see Resolution):** don't detect the load event at all. Capture raw JSONL transcripts of two full runs (with-skill available vs without) and let a reviewer subagent score the **behavioral** delta. The detection problem disappears because measurement shifts from "did it load" to "did behavior differ" — the latter is observable from any JSONL.

---

## SQ-6: Description-optimizer loop generalization

`[SC/run_loop]` + `[SC/improve_description]`:
- **Train/test split:** stratified by `should_trigger`, default 60/40 (`holdout=0.4`). `[run_loop.split_eval_set]`
- **Runs per query:** 3 (for stable trigger rate).
- **Trigger threshold:** 0.5 (a query "triggers" if >50% of runs fire).
- **Max iterations:** 5.
- **Editor:** `improve_description.py` calls `claude -p` with the eval failures + history on stdin, gets back a proposed description.
- **Selection:** best by **held-out test score**, not train score — explicitly to avoid overfitting. `[run_loop]` returns `best_description`.

**Generalization:** the loop is **model-agnostic in structure**. The "editor LLM" is just "some LLM that proposes description improvements given failures" — Claude is one choice; any chat-completion model works. The subprocess (`claude -p`) is the only Claude-Code-specific bit; the generalistic skill says "call your editor LLM" and lets the runtime pick.

**Honest limitation:** the whole optimizer assumes the runtime can (a) run N queries in parallel and (b) detect triggering. Both are runtime-specific (SQ-5). The generalistic skill flags this as "requires runtime support; skip if unavailable" — matching what Anthropic itself says for Claude.ai (`[SC]` "Description optimization … is only available in Claude Code. Skip it if you're on Claude.ai.").

---

## SQ-7: Generalistic grading without subagents

The Anthropic grader is an `Agent`-tool subagent. **But its inputs are just files** (`transcript_path`, `outputs_dir`) and its output is JSON any agent can emit. `[SC/grader]`.

**The inline pattern:** the orchestrator, after running a with-skill task inline, switches hats and grades its own output. This is less rigorous (the grader has full context = bias), but Anthropic already sanctions it for Claude.ai (`[SC]` "read the skill's SKILL.md, then follow its instructions … Do them one at a time. This is less rigorous … but the human review step compensates. Skip the baseline runs.").

**Local reuse:** `[GC]` general-critic is already a reusable inline critic with `HIGH/MEDIUM/LOW` severity and a "loop until PASS" contract. The generalistic skill can adopt `[GC]`'s contract **and** the `[SC/schemas]` grading.json field names — the two are compatible (GC's findings map to grading.json's `expectations[]` with `text/ passed/ evidence`).

---

## SQ-8: Overlap with existing taches-principled-light skills

| Concern | crafting-skills `[CS]` | general-critic `[GC]` | reviewing-and-polishing `[RAP]` | **evaluating-skills (new)** |
|---|---|---|---|---|
| Write `evals.json` | Step 2 "Write Evals First" (3 categories, simple schema) | — | — | Adopt Anthropic's `evals.json` schema; reference `[CS]` for the *intent-capture* stage |
| Pre-commit validation | Step 6 + `[CS/selftest]` (YAML, thresholds, trigger grep) | — | — | Defer to `[CS/selftest]`; don't duplicate |
| Output-quality grading (stage 4) | mentions trigger test only | reusable critic, generic artifact | REVIEW/CRITIQUE on code/PRs | **owns this** — schema-bound grading.json, inline-or-subagent |
| Benchmark aggregation (stage 5) | — | — | — | **owns this** — benchmark.json mean/stddev/delta |
| Iteration loop (stage 7) | OPTIMIZE mode (routing only) | loop-until-PASS | CRITIQUE multi-judge | **owns this** — feedback.json → rewrite → re-run |
| Trigger optimization (stage 8) | OPTIMIZE mode knobs | — | — | Reference `[CS]` OPTIMIZE + `[CS/selftest]`; teach the train/test methodology, defer execution to runtime |

**Carve-out:** the new skill **does not** replace crafting-skills (which owns CREATE/OPTIMIZE routing and the 14-rule compendium) or general-critic (which owns the generic critic contract). It sits **between** them: it is the *evaluation harness* that crafting-skills' Step 2/6 and general-critic's loop plug into, using Anthropic's public schemas.

---

## SQ-9: Fallback table for each runtime-specific stage

| Stage | Subagent-native (Claude Code, Cursor, Cowork) | Headless fallback (`claude -p`, CI, kimi-code, Reasonix) |
|---|---|---|
| 3 Run | spawn 2 subagents/eval in parallel (with-skill + baseline) | run inline, sequentially; baseline = no-skill or previous-version snapshot; skip baseline if cost-prohibitive |
| 4 Grade | spawn grader subagent per run | grade inline (switch hats); reuse `[GC]` contract; write grading.json |
| 6 Review | `generate_review.py` server + `webbrowser.open()` | `generate_review.py --static report.html` (no server) OR write `report.md` + present outputs inline; user feedback collected as conversation → saved to `feedback.json` |
| 8 Optimize trigger | `run_loop.py` with `claude -p` subprocess, 60/40 split, 3 runs/query | **skip** if runtime can't detect triggering (per Anthropic's own Claude.ai guidance); OR do a reduced single-run qualitative check |

Anthropic already documents the Cowork + Claude.ai fallbacks in `[SC]` ("Cowork-Specific Instructions", "Claude.ai-specific instructions"). The generalistic skill **codifies** these into an explicit adapter table indexed by capability rather than by product name — so kimi-code/Reasonix map cleanly.

---

## SQ-10: Minimum viable skill

The smallest skill that preserves the loop's intent:

1. **Capability probe** (top of skill): "Detect your own capabilities. Do you have a subagent/Agent tool? A Bash/subprocess tool? A browser/display? Mark each as available or not."
2. **Stage contract** (the 8 stages, each with: required input artifact, required output artifact, and the two adapter forms).
3. **Schema reference** (pointer to `references/schemas.md` containing the 4 Anthropic JSON schemas verbatim).
4. **Reuse pointers** (to `[CS]`, `[GC]`, `[CS/selftest]`).
5. **Capability-gated branches**: where subagents exist, fan out; where they don't, run inline; where browser exists, offer HTML; where it doesn't, write markdown.

That is the draft in Batch C.

---

## Synthesis

The official skill-creator is a **Claude-Code-interactive-first** implementation of a **runtime-agnostic** methodology. The methodology (8 stages, public schemas, grade-then-iterate loop) is fully portable; only 4 stages have runtime-specific *mechanisms*, and each has a documented fallback. Anthropic's own SKILL.md already contains the degradation paths (Claude.ai, Cowork) — the generalistic skill's job is to (a) promote those paths from product-name sections to capability-keyed adapters, (b) adopt the public schemas verbatim for interop, and (c) reuse the local `[GC]` critic as the inline grader.

## Open questions (would need a primary source or experiment to settle)

1. ~~Whether kimi-code / Reasonix expose a "skill consulted" signal at all.~~ **RESOLVED (see "Resolution: behavioral JSONL review" below) — the signal is not required.**
2. Whether the marketplace wants per-skill `evals/evals.json` files committed for all 28 skills, or only for new skills going forward. (Out of scope here — methodology only.)
3. Whether to vendor the 4 Anthropic schemas into `evaluating-skills/references/schemas.md` (current plan) or fetch them live from GitHub on demand (risk: drift; benefit: always current).

---

## Resolution: behavioral JSONL review (supersedes the SQ-5/6 "runtime-specific" verdict)

**Trigger.** The original verdict held that trigger-accuracy benchmarking (SQ-5/6) was "runtime-specific and opt-in" because Anthropic's `run_eval.py` detects the skill-load event via Claude-Code-specific `.claude/commands/` injection + `stream-json` tool-name parsing. That mechanism is brittle and Claude-Code-only.

**Reframe.** Measure **behavioral consequence**, not the load event. Every agent CLI in scope (kimi-code, Reasonix, Codex, Cursor, `claude -p`, Claude Code interactive) can emit a **raw streaming JSONL transcript**. Two runs of the same eval prompt — one with the skill available, one without — produce two JSONL files. A reviewer subagent reads both, annotates them inline (self-editing the JSON), and scores the behavioral delta. No load-event detection needed.

**Why this is strictly better:**

1. **Universal.** The only runtime requirement is "can I capture a raw JSONL transcript?" — which every serious agent CLI satisfies. kimi-code/Reasonix/Codex all qualify.
2. **Behavioral, not mechanical.** A skill can be loaded-then-ignored (false positive in the load-event model) or behaviorally embodied without an explicit load (false negative in the load-event model). Reviewing the transcript catches both.
3. **Richer artifact.** The output is an *annotated transcript* + per-dimension behavioral scores + evidence quotes — strictly more informative than Anthropic's per-query boolean.
4. **Drops the brittle injection.** The `.claude/commands/<name>.md` trick disappears from the generalistic design. It was only ever a Claude-Code hack to manufacture a detectable event; measuring consequence removes the need for a detectable event.

**Verified — all three named runtimes support the universal pattern:**

| Runtime | Streaming / JSONL mechanism | Skills setup mechanism | Source |
|---|---|---|---|
| **kimi-code (CLI)** | `kimi -p "<prompt>" --output-format stream-json` — "each line on stdout is a JSON object … regular replies produce an Assistant message; when the model calls a tool, an Assistant message with `tool_calls` is emitted first, followed by the corresponding Tool message, then subsequent Assistant messages" | `--skills-dir <dir>` (replaces automatically discovered skills dirs for this launch) — enables the with-skill/without-skill comparison trivially | [kimi.com/code/docs/.../kimi-command.html](https://www.kimi.com/code/docs/en/kimi-code-cli/reference/kimi-command.html) §"Non-Interactive Execution" |
| **Codex CLI (OpenAI)** | `codex exec --json` — "Print newline-delimited JSON events instead of formatted text … one per state change"; pair with `--output-last-message` to capture the final natural-language response | Plugins (skills not yet native) — a skill can be added/removed via `codex plugin add`/`remove`; the with/without comparison runs by including or excluding the plugin in the workspace | [developers.openai.com/codex/cli/reference](https://developers.openai.com/codex/cli/reference) §`codex exec` |
| **Reasonix (esengine/DeepSeek-Reasonix, v1.x Go rewrite)** | Live stream of `event.Event` types (`event.Reasoning`, `event.Text`, `event.ToolDispatch`, `event.Usage`, `event.Error`) to `os.Stdout` via `agent.NewTextSink`; legacy 0.x also has `--transcript` for JSONL file output. "Rendered as Markdown on a TTY, but if piped or captured, it maintains the raw stream." | `run_skill` tool + `/skill` slash command; built-in `explore`/`research`/`review`/`security_review` skills, plus user-defined Markdown skills loaded from custom skill roots; the with/without comparison is natural (the agent either has the skill in its toolset or doesn't) | [esengine.github.io/DeepSeek-Reasonix](https://esengine.github.io/DeepSeek-Reasonix/) + DeepWiki/CodeWiki analysis |
| **Claude Code / `claude -p`** | `claude -p ... --output-format stream-json --include-partial-messages` | Skills in `.claude/commands/` or by being present in the skills dir | [run_eval.py](https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/run_eval.py) |

All four runtimes satisfy the pattern. The generalistic skill is viable on all of them — **the Open Question #1 from the original research is closed**.

**The behavioral-reviewer subagent contract (revised SQ-7 + SQ-9):**

Inputs: `with_skill.jsonl`, `without_skill.jsonl`, the skill's `SKILL.md`, the eval's `expectations[]`.
Process:
1. Read both transcripts end-to-end.
2. For each, mark inline (by editing/annotating the JSONL or writing an overlay) where the agent's behavior aligned with or deviated from the skill's explicit guidance.
3. Score per behavioral dimension (e.g. *followed-step-ordering*, *used-skill-patterns*, *output-completeness*, *output-quality*, *tool-discipline*) on a fixed rubric, for both runs.
4. Emit `behavioral_comparison.json`: `{dimensions: [{name, with_skill, without_skill, delta, evidence_with, evidence_without}], verdict, material_difference: bool}`.
5. Optionally loop (reuse `[GC]` general-critic's "until no HIGH findings" contract) if the comparison is ambiguous.

**Consequence for the capability matrix (SQ-9 revised):** stage 8 (optimize trigger) is **no longer runtime-blocked**. The setup half (make the skill available in one run) is still runtime-specific but trivial; the measurement half is now universal via JSONL review. So:

| Stage | Old verdict | **Revised verdict** |
|---|---|---|
| 3 Run | specific | specific (but trivial setup) |
| 4 Grade | specific | **agnostic** — reviewer subagent on JSONL, or inline |
| 6 Review | specific | specific (HTML vs markdown — unchanged) |
| 8 Optimize | specific / opt-in | **agnostic for measurement** — behavioral delta via JSONL; runtime-specific only for *re-running* N times (cost decision, not capability block) |

This collapses the original 4 runtime-specific stages down to effectively 1.5 (stage 3's setup, and stage 6's display choice). The generalistic skill is now viable as a **single** skill, not a split interactive/headless pair — which was the hypothesis-test in `judgment.md`. **Hypothesis: confirmed (with the correction that "runtime-specific" stages are fewer than first counted, thanks to behavioral JSONL review).**