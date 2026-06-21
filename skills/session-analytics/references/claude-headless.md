# Claude Headless — Pattern Library

`claude -p` is just Claude Code running in a terminal without a UI. It executes a prompt, does its work, and exits. No agents are spawned internally — it's the same Claude you talk to interactively, in batch mode with a prompt you supply.

Discover flags via `claude --help` and `claude <subcommand> --help`. The patterns here are stable combinations; flags evolve — `--help` is always current.

---

## The 5 Use Cases

Invoke this skill when the user wants to:

1. **Probe workspace behavior** — does Claude load the right agents, skills, rules, and tools in a given workspace?
2. **Hot-reload MCP servers or plugins** — run `claude -p` and it picks up updated config without restarting anything
3. **Behavioral testing** — does Claude follow conventions, call the right tools, in the right order?
4. **Batch processing** — any autonomous work that doesn't need a UI
5. **Log analysis** — read a `stream-json` log and report what happened, using native subagents

---

## Part I — Invocation Patterns

### Session Lifecycle

```
One-shot       →  discrete task, exits, no persistence
Stateful       →  multi-turn conversation, same session ID across runs
Ephemeral      →  in-memory only, nothing written to disk (--no-session-persistence)
Fork           →  branch from an existing session without modifying it
```

**Session IDs must be valid UUIDs.** Use `$(uuidgen)` for auto-generation. Non-UUID strings are rejected.

**The `--no-session-persistence` flag** implements ephemeral: adds this flag and no session file is written to disk.

---

### Golden Standard — The Baseline for Every Run

Every headless invocation is a variation of this:

```bash
claude -p "<task>" \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/run-$(date +%s).jsonl
```

**Why this combination:**
- `--output-format stream-json` — one JSON object per line (NDJSON). Each line is a complete event. Easy to stream, easy to read line-by-line.
- `--verbose` — mandatory. Without it, `stream-json` produces no output at all. Not an error — just silence. The `--verbose` flag is what makes the output appear.
- `--dangerously-skip-permissions` — skips permission prompts. This is the only way to grant tool access in headless mode. `--allowedTools` has no effect here and is silently overridden — don't combine them.
- `2>&1 | tee` — stderr carries the init banner, errors, and JSON events. Merging to stdout with `2>&1` and writing to disk with `tee` gives you a forensic log. Never pipe `stream-json` directly to the terminal.

**Always use `tee`** when streaming JSON. The log file is your forensic record.

---

### Golden Standard for Behavioral Observation

When the goal is understanding how Claude behaves — tool call ordering, thinking patterns, error recovery, hook firing — add `--include-partial-messages` and `--include-hook-events` to watch the full assembly of the response:

```bash
claude -p "<task>" \
  --include-partial-messages \
  --include-hook-events \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/observe-$(date +%s).jsonl
```

With both flags active, each line is one of:
- `{"type":"system","subtype":"init",...}` — session init with tools and agents
- `{"type":"assistant","message":{"content":[{"type":"thinking","thinking":"...","partial":true}]}}` — thinking chunk
- `{"type":"assistant","message":{"content":[{"type":"text","text":"...","partial":true}]}}` — text chunk
- `{"type":"tool_use",...}` — a tool was called
- `{"type":"tool_result",...}` — tool returned
- `{"type":"hook","subtype":"PreToolUse|PostToolUse|PreRun",...}` — hook lifecycle event
- `{"type":"assistant","message":{...}}` — final complete response

**Without `--include-hook-events`**, hook events are silently dropped from the stream — the hooks still run, you just can't see them. Add the flag to observe them.

**Reading the log with a subagent:**

```bash
# After the run, spawn a subagent to read the forensic log
claude -p "Read /tmp/observe-123456.jsonl line by line. For each line:
1. Parse the event type
2. Report: event type, key content, any anomalies
3. Summarize: init OK? thinking visible? tools called in order? hook events fired? errors? final response coherent?" \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  --session-id "$(uuidgen)" \
  2>&1 | tee /tmp/observe-audit.jsonl
```

This is the standard behavioral probe pattern for any workspace audit.

---

### Pattern 1: One-Shot Discrete Task

```bash
claude -p "Summarize this file" \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/summary.jsonl
```

**`--bare` note:** `--bare` suppresses CLAUDE.md auto-discovery (which loads project agents from `.claude/agents/`). For subagent testing, omit it. For pure MCP transport checks where you only want tool results, `--bare` is acceptable.

---

### Pattern 2: Stateful Multi-Turn

```bash
# Turn 1
claude -p "Search for something" \
  --session-id "$(uuidgen)" \
  --mcp-config '{"mcpServers":{"SearXNG":{"type":"http","url":"http://127.0.0.1:8002/mcp"}}}' \
  --strict-mcp-config \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/conv_step1.jsonl

# Turn 2 — add --resume with the same session ID
claude -p "Fetch the first result" \
  --session-id "<same-uuid>" \
  --resume \
  --mcp-config '{"mcpServers":{"SearXNG":{"type":"http","url":"http://127.0.0.1:8002/mcp"}}}' \
  --strict-mcp-config \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/conv_step2.jsonl
```

`--resume` continues from where the session left off with full context. Without `--resume`, the session ID creates a new conversation — state is not automatically carried.

---

### Pattern 3: MCP Server Testing (Two-Phase)

**Phase 1 — Raw plumbing:** Does the tool respond at all?
```bash
claude -p "Call mcp__<server>__<tool> with <args>. Reply with ONLY the raw response, verbatim." \
  --mcp-config '{"mcpServers":{"<server>":{"type":"http","url":"http://127.0.0.1:<port>/mcp"}}}' \
  --strict-mcp-config \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  --session-id "$(uuidgen)" \
  2>&1 | tee /tmp/raw_test.jsonl
```

**Phase 2 — Discoverability:** Can the agent find and use it from natural language?
```bash
claude -p "search for 'MCP protocol specification' and tell me the top 3 results" \
  --mcp-config '{"mcpServers":{"SearXNG":{"type":"http","url":"http://127.0.0.1:8002/mcp"}}}' \
  --strict-mcp-config \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  --session-id "$(uuidgen)" \
  2>&1 | tee /tmp/discover_test.jsonl
```

Plumbing tests transport. Discoverability tests whether the agent can actually use the tool.

---

### Pattern 4: A2A Inter-Agent Messaging

```bash
A2A_CONFIG='{"mcpServers":{"a2a":{"command":"uvx","args":["a2a-mcp-server"],"env":{"MCP_TRANSPORT":"stdio"}}}}'

claude -p "Register as 'worker' using mcp__a2a__register_agent" \
  --mcp-config "$A2A_CONFIG" --strict-mcp-config \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  --session-id "$(uuidgen)" \
  2>&1 | tee /tmp/a2a_register.jsonl

claude -p "Use mcp__a2a__list_agents to discover available agents" \
  --mcp-config "$A2A_CONFIG" --strict-mcp-config \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  --session-id "$(uuidgen)" \
  2>&1 | tee /tmp/a2a_discovery.jsonl
```

A2A sends to **separate external processes**. `--agent` only changes the current session's system prompt.

---

### Pattern 5: Parallel Fan-Out

```bash
claude -p "Task for worker A" \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  --name "fan-a" --session-id "$(uuidgen)" \
  2>&1 | tee /tmp/fan_a.jsonl &

claude -p "Task for worker B" \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  --name "fan-b" --session-id "$(uuidgen)" \
  2>&1 | tee /tmp/fan_b.jsonl &

wait
```

Each run is independent with its own log. `--name` tags the session for identification in logs.

---

### Pattern 6: Stdin Pipe

```bash
echo "List all .json files in /tmp and report their line counts" | claude -p - \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/stdin_task.jsonl
```

The `-` sentinel tells `claude -p` to read the prompt from stdin. Useful for scripts or when the task text is generated programmatically.

---

### Pattern 7: Non-Streaming JSON Output

```bash
claude -p "Count the files in /tmp" \
  --output-format json \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/count.json
```

`--output-format json` (without `stream-`) emits a single complete JSON object when the run finishes — no NDJSON, no streaming. Use this when you want structured output for scripting and don't need the event-by-event trace.

---

### Additional Flags for Specific Needs

These flags affect headless behavior and are discoverable from `--help`, but worth knowing explicitly:

| Flag | When to use |
|------|-------------|
| `--no-session-persistence` | Ephemeral runs — session not written to disk |
| `--include-hook-events` | Hook development and debugging — see all hook lifecycle in the stream |
| `--include-partial-messages` | Streaming analysis — watch message chunks arrive in real time |
| `--allow-dangerously-skip-permissions` | Enable the skip flag as a config setting (not the bypass itself) |
| `--setting-sources <sources>` | Isolate config — load only specific setting sources |
| `--input-format stream-json` | Realtime streaming input to a headless session |

---

### Hook Development with Headless Claude

Hooks are scripts that run at specific points in Claude Code's lifecycle. The `--include-hook-events` flag makes all hook lifecycle events visible in the `stream-json` output, which lets you develop and debug hooks without a UI.

**The 3 hook types:**

| Hook | When it fires | stdin input |
|------|--------------|-------------|
| `PreToolUse` | Before a tool is called | JSON with `tool_name`, `tool_input`, `session_id` |
| `PostToolUse` | After a tool returns | JSON with `tool_name`, `tool_input`, `tool_result`, `session_id` |
| `PreRun` | Before a session starts | JSON with `session_id`, `working_directory` |

**Hook scripts live in:** `~/.claude/hooks/` (user-level) or `{workspace}/.claude/hooks/` (project-level)

Each hook is a standalone executable (bash script, python, binary). Exit code `0` = allow. Exit code `2` = block with a message. Any other non-zero = silent block.

**Example: a simple PreToolUse hook that blocks `cat`**

```bash
#!/bin/bash
# ~/.claude/hooks/restrict-bash-fileops.sh — PreToolUse hook
HOOK_INPUT=$(cat)
COMMAND=$(echo "$HOOK_INPUT" | python3 -c "
import sys, json; d=json.load(sys.stdin)
print(d.get('tool_input', {}).get('command', ''), end='')
")
[[ -z "$COMMAND" ]] && exit 0
if echo "$COMMAND" | grep -qE '^(cat|grep|find)\b'; then
    echo "BLOCKED: Use Read/Edit/Grep/Glob instead" >&2
    exit 2
fi
exit 0
```

**Iterative hook development with `claude -p`:**

```bash
# Watch hook events in real time as you develop
claude -p "List all files in /tmp using ls" \
  --include-hook-events \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/hook_debug.jsonl
```

Each hook event line in the JSONL looks like:
```json
{"type":"hook","subtype":"PreToolUse","tool_name":"Bash","session_id":"...","allowed":true}
{"type":"hook","subtype":"PostToolUse","tool_name":"Bash","tool_input":{"command":"ls /tmp"},"tool_result":{"stdout":"...\n"},"session_id":"..."}
```

**Hook debugging workflow:**

```bash
# 1. Edit your hook script
$EDITOR ~/.claude/hooks/restrict-bash-fileops.sh

# 2. Run a headless test — watch whether the hook fires and what it outputs
claude -p "Run cat /etc/hostname" \
  --include-hook-events \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | rg "hook"

# 3. If blocked, the PostToolUse will show is_error:true with your message
# 4. If allowed, you'll see both PreToolUse and PostToolUse events

# 5. To test project-level hooks only (isolate from user hooks)
claude -p "List /tmp" \
  --setting-sources project \
  --include-hook-events \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/project_hook_test.jsonl
```

** `--include-partial-messages` — watching thinking in real time:**

```bash
# See thinking chunks as they arrive, before the full response is complete
claude -p "Explain why Rust borrow checker is sound" \
  --include-partial-messages \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | rg "partial\|thinking\|text" | head -20
```

Partial message events look like:
```json
{"type":"assistant","message":{"content":[{"type":"thinking","thinking":"...","partial":true}]}}
{"type":"assistant","message":{"content":[{"type":"text","text":"The borrow checker...","partial":true}]}}
```

Without `--include-partial-messages`, you only see the final complete events. With it, you watch the response being assembled in real time — useful for monitoring long reasoning chains.

---

### Setting Sources — Isolating Config in Headless Runs

`--setting-sources` controls which setting layers are active. This is critical for testing, CI, and when you need to isolate a headless run from project or user configuration.

**The 3 sources:**

| Source | Where it lives | What it contains |
|--------|----------------|-----------------|
| `user` | `~/.claude/settings.json` | Global preferences, permission allowlists, model defaults |
| `project` | `{workspace}/.claude/settings.json` | Project-specific settings, hook configs |
| `local` | `{workspace}/.claude/settings.local.json` | Workspace-local overrides, secrets |

**Default behavior:** all three sources load (user, project, local). Headless runs inherit the full config stack.

**When to restrict sources:**

```bash
# CI/test isolation — ignore project and local settings, only user preferences apply
claude -p "Run the smoke test" \
  --setting-sources user \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/ci_test.jsonl

# Plugin/Skill debugging — ignore ALL settings, pure headless with only CLI flags
claude -p "Test the skill without any settings polluting the context" \
  --setting-sources "" \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/clean_test.jsonl

# Verify project hooks load correctly — project settings active, user settings ignored
claude -p "Check if the pre-run hook fires" \
  --setting-sources project \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/hook_test.jsonl

# Override a specific setting inline without touching settings files
claude -p "Summarize the diff" \
  --settings '{"maxTokens":2000}' \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/override_test.jsonl
```

**Key insight:** `--setting-sources ""` (empty string) loads nothing — no user, no project, no local. The session runs with only CLI flags and `--help`-discoverable defaults. This is the cleanest possible headless environment.

**Overriding specific settings inline:**

```bash
# Override a setting without touching settings files
claude -p "Summarize the diff" \
  --settings '{"maxTokens":2000}' \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/override_test.jsonl

# Load from a settings file instead of inline JSON
claude -p "Run with test credentials" \
  --settings /tmp/test-settings.json \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/file_settings.jsonl
```

**Tool allowlist — restrict what tools are available:**

```bash
# Read-only headless — no write tools, no destructive ops
claude -p "Audit the codebase for TODO comments" \
  --tools "Bash,Read,Glob,Grep" \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/read_only_audit.jsonl

# No tools at all — pure text generation
claude -p "Explain this code excerpt" \
  --tools "" \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/no_tools.jsonl
```

**Combining isolation flags:**

```bash
# Fully isolated: no settings + only specified MCP servers + read-only tools
claude -p "Probe MCP server behavior with zero config pollution" \
  --setting-sources "" \
  --strict-mcp-config \
  --tools "Bash,Read" \
  --mcp-config '{"mcpServers":{"test":{"type":"http","url":"http://127.0.0.1:9001/mcp"}}}' \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/fully_isolated.jsonl
```

**Override the system prompt:**

```bash
claude -p "You are a security auditor. Only report vulnerabilities, nothing else." \
  --system-prompt "You are a security auditor. Focus only on CVEs and misconfigurations." \
  --output-format stream-json --verbose \
  --dangerously-skip-permissions \
  2>&1 | tee /tmp/security_audit.jsonl
```

---

## Part II — Analyzing Output

A `stream-json` log is a sequence of NDJSON lines — one complete event per line. There are two ways to read it: with a native Claude Code subagent (preferred for detailed analysis), or manually with native comprehension (fine for quick checks).

---

### With a Native Subagent (Preferred for Serious Analysis)

Spawn a subagent to read the log directly — do NOT spawn another `claude -p` to read it. Native subagents use the same Claude model and have full tool access.

**Single log:**
```
Read /tmp/run-123456.jsonl line by line. For each line:
1. Parse the event type — system.init, tool_call, tool_result, assistant, error
2. Report: event type, key content, any anomalies
3. Summarize: init OK? tools called? errors? final response coherent?
```

**Multiple logs in parallel:**
Spawn independent subagents — each reads one file. Then merge the summaries. Do NOT chain subagents reading subagent output.

---

### The 7 Questions (Manual Triage)

Read the raw log with native comprehension first. Don't reach for `jq` until after you've read the full thinking traces.

```
- [ ] Init completed?     — system.init with "tools" array present
- [ ] Tool called?        — at least one tool_call event
- [ ] Tool result?        — tool_result follows each tool_call 1:1
- [ ] is_error: true?    — read the error string on that line
- [ ] Thinking first?     — thinking events precede first tool_call (deliberate planning)
- [ ] Error recovery?     — retry or fallback after an errored tool call
- [ ] Final complete?     — last assistant event is coherent with the task
```

### What Each Question Means

1. **Init completed?** — `system.init` must contain a `"tools"` array. No tools = MCP server failed to load or config is wrong. Check the `--mcp-config` URL and that the server process is running.

2. **Tool called?** — `tool_call` events are the proof the agent did something. Zero tool calls with a text-only response = agent declined to act, likely a permission issue or empty context.

3. **Tool result?** — every `tool_call` must be followed by a `tool_result`. Missing result = execution stalled or timed out. Check that the target server is responsive.

4. **is_error: true?** — Any `is_error: true` is significant. Read the error string. Common causes: connection refused (server not running), malformed JSON in `--mcp-config`, tool not found (server name mismatch). One error does not invalidate the run unless it is the final event.

5. **Thinking first?** — `thinking` events before the first `tool_call` indicate deliberate planning. Absence of thinking is not a failure — simple tasks often skip it. Combined with incoherent final output, it suggests a prompt or context problem.

6. **Error recovery?** — look for a `tool_call` with the same target after a `tool_result` with error, or a different tool serving the same goal. Silent continuation (no error, no retry, degraded output) = partial recovery. No retry at all = failed.

7. **Final complete?** — the last assistant event should contain a text response matching the task. Empty response or agent asking for clarification = the prompt was underspecified or the task was impossible with available tools.

---

### Common Error Patterns

| Error string | Likely cause |
|---|---|
| `Connection refused` | MCP server not running on that port |
| `Tool not found` | Server name mismatch in `--mcp-config` |
| `JSON parse error` | Malformed JSON in `--mcp-config` argument |
| `Session not found` | `--resume` used with unknown session ID |
| `Permission denied` | `--dangerously-skip-permissions` not set in headless mode |

---

## Flag Discovery

```bash
claude --help              # global flags and subcommand inventory
claude <subcommand> --help  # subcommand-specific flags
```

The patterns in this skill use stable combinations. The individual flags are always discoverable from `--help`.

## Failure Signal

```json
{"status": "failed", "reason": "session-timeout|permission-denied|tool-unavailable", "completed_portion": "...", "retry_possible": true|false}
```

| status | reason | retry_possible |
|--------|--------|---------------|
| `failed` | `session-timeout` | `true` |
| `failed` | `permission-denied` | `true` |
| `failed` | `tool-unavailable` | `false` |

## Session artifact filesystem layout

For a complete scannable map of every log location, see `references/session-anatomy.md` in this skill. The map covers:

- **Main session transcript** at `~/.claude/projects/<encoded-cwd>/<sessionId>.jsonl`
- **Subagent transcripts** at `~/.claude/projects/<encoded-cwd>/<sessionId>/subagents/<agent-id>.jsonl` (and `.meta.json`)
- **Capture artifacts** at `~/.claude/captures/<UUID>.{stream.jsonl,debug.log,jsonl}`
- **Legacy raw transcript** at `~/.claude/sessions/{uuid}/raw-transcript.jsonl` (older sessions)

If you need to find logs, decode the `<encoded-cwd>`, or glob for a project's sessions, read `references/session-anatomy.md` BEFORE proceeding. Do not skip it.

## Hook input field schema (audit-critical)

Every hook event receives a JSON payload (stdin for command hooks, POST body for HTTP hooks). The fields most relevant to audit workflows:

| Field | Present on | Type | Notes |
|-------|-----------|------|-------|
| `session_id` | all events | string | UUID of the parent session |
| `transcript_path` | all events | string | Absolute path to the main session's `.jsonl` |
| `agent_transcript_path` | `SubagentStop` only | string | Absolute path to the subagent's own `.jsonl` |
| `cwd` | all events | string | Original working directory (unencoded) |
| `hook_event_name` | all events | string | Event type (`PreToolUse`, `PostToolUse`, `SubagentStart`, etc.) |
| `agent_id` | subagent events | string | Subagent UUID |
| `agent_type` | subagent events | string | `Explore`, `Plan`, `general-purpose`, or custom |
| `last_assistant_message` | `SubagentStop` | string | Subagent's final message |

The `transcript_path` field is the load-bearing field for any audit/review workflow. A hook that needs to read the full session context, correlate events, or stream additional context back to the model uses this path directly. No other field reliably identifies the on-disk file.

For `SubagentStop`, the `agent_transcript_path` field points to the subagent's own isolated transcript at `<session-dir>/subagents/agent-<id>.jsonl`. Subagent transcripts persist independently of the main conversation compaction and survive session restarts.

## Subagent transcripts

When the main conversation spawns a subagent, three files appear under the session directory:

```
~/.claude/projects/<encoded-cwd>/<sessionId>/
├── <sessionId>.jsonl                          # main session transcript
├── tool-results/                               # per-tool-call raw output
└── subagents/
    ├── agent-<agent-id>.jsonl                  # subagent's own transcript
    └── agent-<agent-id>.meta.json              # agent type, description, parent ref
```

Subagent transcripts are **isolated**: they do not share context with the main conversation. When a subagent runs in foreground, the parent waits; when it runs in background, the parent proceeds in parallel. Either way, the subagent's full event stream is written to its own `.jsonl`. The parent can read this file after `SubagentStop` to understand what the subagent did.

Transcripts persist for `cleanupPeriodDays` (default: 30 days) before automatic cleanup. Resume a subagent's context by resuming the parent session — the `claude` CLI re-loads subagent transcripts from disk on resume.

## Encoded-CWD path convention

Claude Code encodes the working directory for the `~/.claude/projects/` directory name by replacing `/` with `-`. Examples:

| Original | Encoded |
|----------|---------|
| `/Users/felix/projects/api` | `-Users-felix-projects-api` |
| `/home/devadmin/work` | `-home-devadmin-work` |
| `/Users/felix/Documents/AutoPluginClaw/taches-principled` | `-Users-felix-Documents-AutoPluginClaw-taches-principled` |

This encoding is a Claude Code convention. To recover the original path, replace every `-` with `/` (which only works for POSIX paths with no hyphens — Windows paths are ambiguous, but each event's `cwd` field stores the unencoded value for unambiguous recovery).