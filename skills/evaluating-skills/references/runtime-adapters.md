# Runtime Adapters

Per-runtime flags for capturing raw transcripts (stage 3) and making a skill available/unavailable for the with/without comparison. The behavioral-review methodology (stage 4) is runtime-agnostic; only this capture/setup step varies.

## The 2-axis capability matrix

Each target runtime has two independent properties that shape the adapter choice:

| Runtime | Subagents? | Headless subprocess? | Skills available/unavailable mechanism |
|---|---|---|---|
| **Claude Code** (interactive) | yes | yes (`claude` binary) | skill present in / absent from `.claude/skills/` or via plugin |
| **`claude -p`** (headless) | yes | yes | same; driven as subprocess |
| **Codex CLI** | yes | yes (`codex exec`) | plugins (`codex plugin add`/`remove`); native skills not yet |
| **kimi-code / kimi-cli** | yes | yes (`kimi -p`) | `--skills-dir <dir>` (replaces discovered dirs for this run) |
| **Reasonix** (v1.x Go) | yes | yes (`reasonix run`) | skills loaded from custom skill roots; `run_skill` tool present/absent |
| **Cursor** | yes (agent mode) | **unreliable as subprocess** | IDE agent-mode transcript; `cursor agent -p --output-format stream-json` flag exists but headless `-p` has documented silent-hang bugs (Cursor forum, Jan–Mar 2026) — prefer **COMPARE** mode with pre-captured transcripts |
| **Generic CI** (no agent subprocess) | varies | no | n/a — use pre-captured transcripts (COMPARE mode) |

Subagent availability decides whether stage 3 fans out in parallel or runs inline. Display availability decides whether stage 6 is an HTML viewer or a `report.md`. These are independent — do not assume "headless = no subagents".

## Transcript capture flags

| Runtime | Flag | Output |
|---|---|---|
| Claude Code / `claude -p` | `--output-format stream-json --include-partial-messages` | JSON object per line; `content_block_start`/`content_block_delta`/`tool_use` events |
| Codex CLI | `codex exec --json` (+ `--output-last-message <path>` for the final text) | newline-delimited JSON events, one per state change |
| kimi-code | `kimi -p "<prompt>" --output-format stream-json` | "each line on stdout is a JSON object; regular replies produce an Assistant message; tool calls produce an Assistant message with `tool_calls`, then the Tool message, then subsequent Assistant messages" |
| Reasonix | default stdout stream (raw when piped, not a TTY); legacy 0.x adds `--transcript <file>` for JSONL-to-file | `event.Event` types: `Reasoning`, `Text`, `ToolDispatch`, `Usage`, `Error` |

Capture pattern (universal): redirect the streaming stdout to `<run-dir>/<config>.jsonl`. For with-skill, make the skill available first (the runtime's mechanism above); for baseline, make it unavailable. Same prompt, same input files, same model.

### Two distinct capture paths — do not confuse them

1. **Subprocess CLI** (`claude -p`, `codex exec`, `kimi -p`, `reasonix run`, `cursor agent -p`). The target runtime is a child process; redirect its stdout to `.jsonl`. This is the path the table above describes.

2. **Interactive Agent-tool subagent** (the primary Claude Code / Cursor / Cowork path where *you* are the orchestrator spawning subagents). Here the "transcript" is **not** a CLI's redirected stdout — it is the subagent's own tool-call log and returned result. Capture it by instructing the subagent in its spawn prompt to (a) write its full step-by-step trace to `<run-dir>/<config>.trace.md` as it works, and (b) return a structured summary. The orchestrator then normalizes that `.trace.md` into the same event shape the reviewer expects (assistant text / tool_calls / tool results / errors). If the runtime exposes the subagent's raw event stream directly (e.g. Claude Code task notifications include `total_tokens` / `duration_ms`), prefer that over a self-reported trace.

The reviewer subagent (stage 4) only needs *some* normalized transcript per run — it does not care which path produced it. The capability probe picks path 1 if you have bash + a drivable CLI, path 2 if you have subagents but no CLI, and COMPARE mode if you have neither.

## Reasonix note

Reasonix's `run_skill` tool and its built-in `explore`/`research`/`review`/`security_review` skills mean a user skill is "available" when it's loaded from a skill root the agent reads. The with/without comparison is natural: point the agent at a skill root that includes the skill, vs one that doesn't. The raw event stream (`Text`/`ToolDispatch`/`Usage`/`Error`) is sufficient for behavioral review — `ToolDispatch` events show which tool (including `run_skill`) fired.

## Codex note

Codex does not yet have native "skills" in the Agent-Skills sense; it has plugins. Treat a skill packaged as a Codex plugin as the unit. The with/without comparison runs by including or excluding the plugin in the workspace before `codex exec`. The `--json` event stream covers behavioral review.

## Cursor note

`cursor agent` / `cursor-agent` supports `--output-format stream-json` (same flag family as Claude Code), so the *capture mechanism* exists. But headless `-p` mode has documented reliability bugs as of early 2026 — multiple Cursor forum threads report it hanging silently with zero stdout, across models and output formats. Until that stabilizes, treat Cursor as a **COMPARE**-mode target: capture transcripts from the IDE's agent mode (or a working interactive session) and feed them to stage 4 directly, rather than driving `cursor agent -p` as a subprocess.

## When no subprocess is available

If the orchestrator cannot drive the target runtime as a subprocess (e.g. evaluating an IDE-resident agent, or a runtime with no CLI), fall back to **COMPARE** mode: the user supplies pre-captured `with_skill.jsonl` and `without_skill.jsonl`. Stage 4 (behavioral review) still works — it only needs the two transcripts. Stages 3, 5 (benchmark over N runs), and 8 (optimize) are not available in this mode; say so.

## Cost guardrail

Each "run" in stage 3 is a full agent task. The default `--runs 3` × (with + baseline) × n-evals = **6n agent tasks per iteration**. For 3 evals that's 18 runs/iteration. Before raising `--runs` or the eval count, confirm the budget allows it. For a quick check, `--runs 1` gives a single-pass comparison (no stddev, but a material_difference signal) at 1/3 the cost.
