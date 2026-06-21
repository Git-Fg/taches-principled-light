---
name: analyzing-sessions
description: >
  Load when analyzing agent session transcripts — extracting metrics,
  diagnosing behavioral anti-patterns, filing GitHub issues from findings, or
  cross-analyzing session artifacts. Use when the user says 'parse session log',
  'session metrics', 'review session for anti-patterns', or 'create a
  meta-issue'. Do NOT use for bug diagnosis in source code (use superpowers'
  systematic-debugging), improving an artifact (use reviewing-and-polishing),
  or managing rules (use managing-rules).
allowed-tools: Read, Glob, Grep, Bash, Agent
when_to_use: "Use for session metrics, anti-pattern review, or creating issues from findings. Examples: \"parse debug log\", \"analyze hooks\". CONTRAST: No code analysis (use reviewing-and-polishing); no general project bugs (use meta-issue)."
argument-hint: "<inspect|review|issue> [session-id|--dry-run] [--filter errors|tools|cost|skills] [--full|--summary]"
---

## Routing Guidance

- **CAPTURE**: 'capture session', 'collect artifacts', 'headless capture', 'run verification capture', 'profile a skill invocation', 'audit skill routing', 'measure hook in vivo', 'behavioral capture'
- **INSPECT**: 'parse session', 'session metrics', 'session data', 'inspect transcript', 'session cost', 'what tools did I use', 'how long was this session', 'extract session data'
- **REVIEW**: 'review session', 'what went wrong', 'behavioral review', 'anti-pattern', 'meta-review', 'session critique', 'why did it fail', 'investigate session'
- **ISSUE**: 'create issue from review', 'file report', 'meta-issue', 'generate GitHub issue', 'make a bug report from session'
- CONTRAST with superpowers' `systematic-debugging`: analyzing-sessions analyzes session transcripts; systematic-debugging analyzes code problems.
- CONTRAST with code-review: analyzing-sessions extracts behavioral patterns; code-review analyzes source code quality.

## What This Skill Changes

**Default behavior:** Session data remains unstructured JSONL — tool calls, errors, and cost metrics require ad-hoc grep commands. Anti-patterns surface only when the user explicitly asks, and no systematic recording exists. Issue creation is manual and inconsistent.

**With this skill:** Standardized three-mode extraction (INSPECT), behavioral diagnosis (REVIEW), and sanitized issue generation (ISSUE). The main agent delegates data extraction and analysis to subagents; it synthesizes results and manages the issue creation workflow.

**Why mode separation:** INSPECT is data extraction (fast, single-pass). REVIEW is behavioral interpretation (deeper, may fan out subagents). ISSUE is report generation (post-review action, requires privacy audit).

## Decision Router

IF user wants to collect behavioral artifacts (capture session, headless capture, run verification) → **CAPTURE** mode
IF user wants structured session data (metrics, tool calls, cost) → **INSPECT** mode
IF user wants behavioral anti-pattern diagnosis → **REVIEW** mode
IF user wants to create a GitHub issue from review findings → **ISSUE** mode
IF user passes `--mode cross-analyze` → **CROSS-ANALYZE** mode
IF user passes `--mode adjudicate` → **ADJUDICATE** mode

---

## CAPTURE Mode

Collects behavioral artifacts by running a headless Claude Code session with canonical capture flags. Use before INSPECT, REVIEW, or meta-issue when you need fresh artifacts.

### When to Use

Before behavioral verification, trigger collision testing, hook validation, or plugin A/B testing — whenever you need a fresh capture of Claude Code's actual behavior rather than analyzing an existing transcript.

### CAPTURE Protocol

You MUST read `references/session-anatomy.md` BEFORE running a capture. The capture protocol below writes to paths documented in that file. Do not skip it.

Generate a capture UUID, then run the canonical capture incantation:

1. **Generate identifiers:**
   ```bash
   UUID=$(uuidgen 2>/dev/null || python3 -c "import uuid; print(uuid.uuid4())")
   SESSION_ID="$UUID"
   ```

2. **Create capture directory:**
   ```bash
   mkdir -p ~/.claude/captures
   ```

3. **Run the capture:**
   ```bash
   claude -p "$ARGUMENTS" \
     --session-id "$UUID" \
     --debug "hooks,api,plugins,skills" \
     --debug-file ~/.claude/captures/${UUID}.debug.log \
     --output-format stream-json \
     --include-hook-events \
     --include-partial-messages \
     --max-budget-usd 0.50 \
     --verbose 2>&1 | tee ~/.claude/captures/${UUID}.stream.jsonl
   ```

4. **Wait for completion** (the command blocks until the capture finishes).

5. **Report artifact paths:**
   Return the three artifact paths:
   - Debug log: `~/.claude/captures/<UUID>.debug.log`
   - Stream-json: `~/.claude/captures/<UUID>.stream.jsonl`
   - Persisted JSONL: `~/.claude/projects/<encoded-cwd>/<UUID>.jsonl`

6. **Store the session ID** for downstream skills:
   ```bash
   echo "$UUID" > ~/.claude/captures/.last-capture-id
   ```

### Artifact Provenance

| Artifact | Path | Best for |
|---|---|---|
| Debug log | `~/.claude/captures/<UUID>.debug.log` | Hook fires, permission gates, plugin sync, MCP errors |
| Stream-json | `~/.claude/captures/<UUID>.stream.jsonl` | Streaming behavior, partial chunks, early termination |
| Persisted JSONL | `~/.claude/projects/<encoded-cwd>/<UUID>.jsonl` | Tool calls, results, usage, errors |

### Execution

**Default: subagent delegation.** For CAPTURE, spawn a Bash subagent to execute the headless capture command.

**Spawn pattern:**
- Scope: `~/.claude/captures/` directory for artifact output
- Role: general-purpose (headless execution)
- Output: Three artifact paths reported to main agent

After CAPTURE, route to **INSPECT** mode for artifact parsing, then to **REVIEW** mode for analysis.

---

## INSPECT Mode

### Multi-Artifact Routing

`session-inspect` handles three artifact types. Detect which type you're working with:

**Routing rules (apply in order):**
1. If input path ends with `.jsonl` → check if first line contains `"type"` or `MessageParam` → JSONL parser (existing)
2. If input path ends with `.debug.log` → debug-log parser (grep for `[HOOK]`, `[API]`, `[PERMISSION]`, `[ERROR]` sections)
3. If input path ends with `.stream.jsonl` → stream-json parser (parse per-turn delta events, extract `type`, `model`, `usage`, `stop_reason`)
4. If the input is a directory → scan for `.debug.log`, `.stream.jsonl`, and `.jsonl` files and process all three

**Debug-log parser** (apply to `.debug.log` files):
- Extract lines matching `\[HOOK\]`, `\[API\]`, `\[PERMISSION\]`, `\[ERROR\]`, `\[MCP\]`, `\[PLUGIN\]`
- Group by category
- Return categorized event list

**Stream-json parser** (apply to `.stream.jsonl` files):
- Parse each line as a JSON object
- Extract: `type` (message/ping/partial_message/etc), `model`, `usage` (input_tokens, output_tokens), `stop_reason` (end_turn/partial/etc)
- Count unique event types
- Return structured event summary

---

Parses raw session JSONL into structured data — tool calls, errors, cost, loaded plugins, and behavioral events. You MUST read `references/inspect-reference.md` AND `references/session-anatomy.md` before executing INSPECT mode. Do not proceed without reading both files.

### Session Discovery

Claude Code stores session transcripts at `~/.claude/projects/<encoded-cwd>/<sessionId>.jsonl` (and `~/.claude/sessions/{uuid}/raw-transcript.jsonl` for older sessions). The full filesystem layout — including subagent paths, capture artifact paths, and the encoded-CWD scheme — is in `references/session-anatomy.md`. Read that file first to decode project paths and locate subagent transcripts.

1. **By project**: glob `~/.claude/projects/<encoded-cwd>/*.jsonl` — the encoded-CWD is `/` → `-` substitution
2. **Latest session**: `ls -t ~/.claude/projects/<encoded-cwd>/*.jsonl | head -1` → use that session ID
3. **By ID**: user provides the session UUID directly
4. **By content**: `grep -l <keyword> ~/.claude/projects/<encoded-cwd>/*.jsonl` for grep-based discovery
5. **Subagents**: `ls ~/.claude/projects/<encoded-cwd>/<sessionId>/subagents/` for that session's subagent transcripts

If no session ID provided and latest session is empty or still running, try the previous one.

### INSPECT Submodes

**Default: SUMMARY** — quick overview of session metadata, tool counts, error summary, and environment loaded.

**--full flag: FULL** — complete structured extraction including every tool call, assistant message count, git state snapshot, and init event details.

**--filter flag: FILTER** — specific event filtering (`errors`, `tools`, `cost`, `skills`).

### Execution

**Default: subagent delegation.** For structured extraction, spawn a a subagent explorer subagent with scope "parse this session JSONL, apply the privacy scrub, and write structured output" and mode (SUMMARY / FULL / FILTER). The subagent reads the JSONL in its own disposable context — the raw transcript never enters the main conversation — and writes the parsed output to `docs/principled/scratch/session-inspect-{uuid}.{json|md}`.

**Spawn pattern:**
- Scope: session transcript at `~/.claude/sessions/{uuid}/raw-transcript.jsonl`
- Role: **a subagent explorer** (data extraction; privacy scrub applied in spawn prompt)
- Output: `docs/principled/scratch/session-inspect-{uuid}.json` (FULL) or `docs/principled/scratch/session-inspect-{uuid}.md` (SUMMARY)
- Mode: SUMMARY / FULL / FILTER as specified by user flags

---

## REVIEW Mode

Reviews Claude Code session transcripts for behavioral anti-patterns and investigates root causes. You MUST read `references/review-reference.md` AND `references/session-anatomy.md` before executing REVIEW mode. Do not proceed without reading both files.

### REVIEW Submodes

**Default: REVIEW** — quick diagnostic of the most recent or specified session using a single diagnostic subagent.

**investigate argument: INVESTIGATE** — deep investigation with parallel subagent fan-out (2 subagents simultaneously) for structural or recurring failures.

### Process (REVIEW mode)

1. **Discover session** — find the target transcript
2. **spawn a subagent generalist for isolated review** (lens: "examine this session transcript for behavioral anti-patterns") — reads full JSONL in its isolated context, produces behavioral analysis
3. **Present findings** — anti-patterns (PLUGIN scope only), what went well, scope verdict
4. **Next step suggestion** — if actionable findings exist, suggest running ISSUE mode

### Process (INVESTIGATE mode)

1. **Discover session** — same as REVIEW
2. **Spawn 2 parallel subagents**:
   - **Diagnostic subagent** (a subagent generalist with lens "examine this session transcript for behavioral anti-patterns — diagnose root cause and scope"): reads transcript, identifies anti-patterns and root cause scope
   - **Context & Outcome subagent** (a subagent explorer with scope "analyze this session's git state, environment, and behavioral outcomes — what worked vs what broke"): analyzes git state, environment, and behavioral outcomes
3. **Synthesize** — merge findings, cross-reference with git state, deduplicate, assign severity
4. **Scope gate** — check if findings are PLUGIN scope (reportable) or USER-FILE/ENVIRONMENT scope (excluded)
5. **Write unified report** to `docs/principled/scratch/meta-review-{session_id}.md`

### Privacy

The privacy scrub (file contents from workspace, user prompts verbatim, project directory paths, environment variables, tokens, credentials) MUST be specified in the spawn prompt for any subagent that reads session data — it is no longer a property of a dedicated agent.

### Execution

**Default: subagent delegation.** For REVIEW, spawn one a subagent generalist subagent (lens: "examine this session transcript for behavioral anti-patterns"). For INVESTIGATE, spawn 2 parallel subagents as detailed in the INVESTIGATE process above. The main agent synthesizes results; it never performs transcript analysis inline.

**Spawn pattern:**
- Scope: session transcript at `~/.claude/sessions/{uuid}/raw-transcript.jsonl`
- Role: **a subagent generalist** (diagnostic, anti-pattern review), **a subagent explorer** (context & outcome analysis)
- Output: `docs/principled/scratch/meta-review-{session_id}.md`

---

## ISSUE Mode

Creates a GitHub issue from meta-review findings. You MUST read `references/issue-reference.md` before executing ISSUE mode.

### ISSUE Submodes

**Default: CREATE** — creates a GitHub issue using `gh issue create`.

**--dry-run flag: DRY-RUN** — builds and prints the issue body without creating it.

### Prerequisites

1. **Verify `gh` is available** — `which gh`. If missing, tell user to install GitHub CLI.
2. **Verify git remote** — `git remote get-url origin`. If missing, tell user this only works in a git repo with a GitHub remote.
3. **Verify review file exists** — read the meta-review output from `docs/principled/scratch/`

### Privacy Audit (CREATE mode)

Before creating any issue, scan the review content for:
- Absolute file paths (except `~/.claude/sessions/` which is generic)
- User prompt text (should be paraphrased, not quoted)
- Environment variable values
- Token or credential strings
- Project-specific file contents

If any sensitive content found: **ABORT** and tell the user what needs to be redacted.

### Scope Exclusion

If the meta-review file has `Report advised: NO` (all findings are USER-FILE/ENVIRONMENT/MODEL scope), tell the user:

> "The review found no actionable plugin-scope findings. All issues trace to user configuration or environment state. Creating a public issue is not recommended — the root cause is outside the plugin's control."

The user can override with explicit confirmation.

### Execution

**Default: subagent delegation.** For privacy audit and body construction, spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why.". For issue creation, use the Bash tool directly with `gh issue create`.

**Spawn pattern:**
- Scope: `docs/principled/scratch/meta-review-{session_id}.md`
- Role: **a subagent generalist** (privacy audit, body construction)
- Output: issue body file → `gh issue create`

---

## CROSS-ANALYZE Mode

**When to use:** After a capture session has been collected. Analyzes the three artifacts (debug log, stream-json, persisted JSONL) in parallel using three specialized agents, then reports convergence across analysts.

**Execution:**

1. **Detect artifact paths** from the capture session:
   - If user provides a capture UUID → construct paths from `~/.claude/captures/<UUID>*` and `~/.claude/projects/<encoded-cwd>/<UUID>.jsonl`
   - If user provides paths directly → use those paths
   - If no capture found → error with `{"status": "failed", "reason": "no-capture", "remediation": "Run /capture first"}`

2. **Fan out three parallel specialists** (spawn all three concurrently with background=true):
   - **a subagent explorer** with scope "parse stream-json output → structured event list" (FULL mode)
   - **a subagent generalist** with lens "examine persisted JSONL for behavioral anti-patterns" ← persisted JSONL → anti-pattern list
   - **a subagent explorer** with scope "extract root-cause traces from debug log" ← debug log → root-cause traces
     - **Note:** debug-log root-cause tracing is also used by superpowers' `systematic-debugging` STACK-TRACE mode.

   - All three agents use the same privacy-scrub directive applied via the spawn prompt.

3. **Wait for all three** (TaskOutput with block=true for all three)

4. **Aggregate findings:**
   - Compile all findings from all three analysts
   - **Convergence signal:** Mark findings that appear in ≥2 analyst outputs with a `convergence: high` flag
   - Findings from only one analyst → `convergence: low` (could be analyst artifact or noise)

5. **Report:**
   - Summary table: finding | analysts_that_found_it | convergence | severity
   - High-convergence findings listed first
   - Each finding references the specific artifact/line that supports it

**Output format:**
```json
{
  "status": "complete",
  "mode": "cross-analyze",
  "capture_id": "<UUID>",
  "findings": [
    {
      "finding": "<description>",
      "analysts": ["critic", "debug-explorer"],
      "convergence": "high",
      "severity": "HIGH",
      "evidence": { "file": "<path>", "line": <n>, "text": "..." }
    }
  ],
  "summary": { "total": N, "high_convergence": M, "low_convergence": K }
}
```

---

## ADJUDICATE Mode

**When to use:** After cross-analyze has produced findings. Validates each finding against evidence and runs adversarial challenge.

**Execution:**

1. **Collect findings** from cross-analyze output (passed as file path argument or previous session-inspect output)

2. **Parallel validation per finding** — for each finding, spawn two agents concurrently:
   - **an FPF evidence-validator subagent** ← the finding + the JSONL artifact → "evidence supports" or "L1-speculative"
   - **a a subagent generalist subagent** ← the finding → try to refute it (refuted=true if uncertain)

   Use `background: true` for all spawns. Spawn all evidence-validators and all adversarial challengers concurrently.

3. **Await all results** (TaskOutput with block=true)

4. **Classify each finding:**
   - **Validated:** evidence-validator says "supports" AND adversary says "not refuted"
   - **Speculative:** evidence says "L1" OR adversary says "refuted"
   - **Rejected:** both say negative

5. **Report:**
   ```json
   {
     "status": "complete",
     "mode": "adjudicate",
     "findings": [
       {
         "finding": "<text>",
         "classification": "validated|speculative|rejected",
         "evidence_check": "supports|L1-speculative|no-evidence",
         "adversarial_check": "not_refuted|refuted",
         "reason": "<explanation>"
       }
     ],
     "summary": { "validated": N, "speculative": M, "rejected": K }
   }
   ```

**Note:** If an FPF evidence-validator subagent is not available (partial install), skip evidence validation and note it. If a a subagent generalist subagent is not available, use a marketplace critic subagent (such as a single-pass critic) as fallback adversarial agent.

---

## CONTRAST
NOT for superpowers' `systematic-debugging` (session patterns vs code bugs), NOT for code-review (workflow anti-patterns vs code quality)

## Gotchas

- Do NOT analyze a session while it's still running — the transcript is incomplete and metrics will be wrong.
- Do NOT conflate correlation with anti-patterns. A spike in tool calls may be legitimate, not a behavioral issue.
- Do NOT create GitHub issues without reproduction steps. Every issue MUST include: session ID, turn number, expected vs actual behavior.
- Do NOT run session analytics on truncated transcripts — verify the session is complete before analysis.

## Reference Index

IF performing structured data extraction (INSPECT) → spawn **a subagent explorer** (scope: "parse JSONL with privacy scrub → structured output")
IF performing behavioral diagnosis (REVIEW) → spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why."
IF performing deep investigation (INVESTIGATE) → spawn **a subagent generalist** (anti-pattern diagnosis) + **a subagent explorer** (scope: "analyze git state, environment, behavioral outcomes")
IF performing privacy audit and issue body construction (ISSUE) → spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why."
IF performing forensic log analysis (CROSS-ANALYZE) → spawn **a subagent explorer** (scopes: stream-json parsing + debug-log root-cause tracing) + **a subagent generalist** (lens: anti-pattern review of persisted JSONL)

## Reference routing

This skill ships seven reference files. The mode sections above already
imperatively cite the ones they require; this table consolidates the
"if you need X, read Y" mapping for quick lookup. References here are
file names within this skill's `references/` directory; session-anatomy
itself is the on-disk artifact map and is cited from the per-mode
sections for path discovery.

| If you need to… | Read |
|------------------|------|
| Find sessions for this project | `references/session-anatomy.md` (one-liners section) |
| Parse a session's event stream | `references/inspect-reference.md` (INSPECT mode) |
| Diagnose why a subagent went wrong | `references/claude-headless.md` + the subagent's `.jsonl` |
| Audit permission/hook decisions | `~/.claude/captures/<UUID>.debug.log` (the debug-log event categories) |
| Reproduce a headless run | `references/claude-headless.md` (the `claude -p` capture protocol) |
| See what tools a hook fired on | `transcript_path` field in hook input → main session JSONL |
| Run an evidence-validated cross-analyze | `references/cross-analyze-protocol.md` + `references/adjudicate-protocol.md` |

The mode sections above (CAPTURE, INSPECT, REVIEW, ISSUE, CROSS-ANALYZE,
ADJUDICATE) are the authoritative entry points — read those first; this
table is the secondary lookup for the per-reference scope of each file.

## Cross-plugin dependencies

This skill is part of taches-principled-light and depends on
**optional** agents from other plugins. Each is a soft dependency —
the skill works without it, falling back to the noted substitute.

| Agent role | Source | Used in | Fallback if absent |
|---|---|---|---|
| a subagent explorer (debug-log scope) | the marketplace's shared a subagent explorer | `CROSS-ANALYZE` mode, for backward call-chain root-cause from debug logs | the same a subagent explorer with a narrower scope on the debug log (single-agent path) |
| FPF evidence-validator | the marketplace's shared a subagent explorer (cross-reference scope) | `CROSS-ANALYZE` evidence validation stage | Skip the validation stage and note it in the report |
| a subagent generalist | the marketplace's solving-competitively skill | `CROSS-ANALYZE` adversarial-check pass | a single a subagent generalist instance (instead of a judge panel) |

Why these aren't hard dependencies: this skill ships
standalone — a user who only wants session analytics should be
able to install just this plugin. The optional cross-plugin agents
add depth (judge panels, evidence validation, stack-trace
root-causing) but are not required for the core flow.

The body of this skill (under `## Process → CROSS-ANALYZE` and
`## Process → meta-analysis`) already says "if available" and names
the fallback inline; this section exists to make the dependency
contract greppable for maintainers and CI scripts that audit
cross-plugin coupling.
