# Session Anatomy — Where Claude Code Writes Logs

A scannable map of every log location Claude Code produces, when each is created, and which mode of `session-analytics` consumes it.

## On-disk artifact map

| Artifact | Path pattern | When created | What it contains | Consumed by |
|----------|--------------|---------------|------------------|-------------|
| **Main session transcript** | `~/.claude/projects/<encoded-cwd>/<sessionId>.jsonl` | Every persistent session | Full NDJSON: tool calls, results, assistant messages, errors, usage metrics | INSPECT, REVIEW |
| **Subagent transcript** | `~/.claude/projects/<encoded-cwd>/<sessionId>/subagents/<agent-id>.jsonl` | When a subagent is spawned | Subagent's full NDJSON transcript (isolated from main context) | INSPECT, REVIEW |
| **Subagent metadata** | `~/.claude/projects/<encoded-cwd>/<sessionId>/subagents/<agent-id>.meta.json` | When a subagent is spawned | Agent type, description, parent session reference | INSPECT |
| **Tool results cache** | `~/.claude/projects/<encoded-cwd>/<sessionId>/tool-results/` | Some sessions | Per-tool-call raw output artifacts | INSPECT |
| **Captured stream-json** | `~/.claude/captures/<UUID>.stream.jsonl` | `claude -p ... --output-format stream-json` | Real-time stream events: `system.init`, `assistant.message`, `tool_use`, `tool_result` | CAPTURE, REVIEW |
| **Captured debug log** | `~/.claude/captures/<UUID>.debug.log` | `claude -p ... --debug-file <path>` | Init events, hook lifecycle, API calls, permission decisions, plugin sync, MCP status, errors | CAPTURE, REVIEW |
| **Persisted JSONL** | `~/.claude/captures/<UUID>.jsonl` | `claude -p ...` with full capture flags | Persisted session transcript (post-run, normalized) | CAPTURE, INSPECT |
| **Raw transcript (legacy)** | `~/.claude/sessions/{uuid}/raw-transcript.jsonl` | Older sessions | Pre-`projects/`-layout session files | INSPECT (legacy) |

## Encoded-CWD scheme

`<encoded-cwd>` is the working directory with `/` replaced by `-`. Examples:

- `/Users/felix/Documents/AutoPluginClaw/taches-principled` → `-Users-felix-Documents-AutoPluginClaw-taches-principled`
- `/home/devadmin/projects/api` → `-home-devadmin-projects-api`

This encoding is a Claude Code convention, not a marketplace invention. To recover the original path, replace every `-` with `/` (which only works on POSIX paths with no hyphens — Windows paths are ambiguous, but Claude Code stores the original `cwd` in each event for unambiguous recovery).

## Hook input field reference

Every hook event receives a JSON payload on stdin (or POST body for HTTP hooks). The `transcript_path` field is the most important field for audit workflows:

| Field | Type | Notes |
|-------|------|-------|
| `session_id` | string | UUID of the parent session |
| `transcript_path` | string | Absolute path to the main session's `.jsonl` |
| `agent_transcript_path` | string (SubagentStop only) | Absolute path to the subagent's own `.jsonl` |
| `cwd` | string | Original working directory (unencoded) |
| `hook_event_name` | string | Event type (`PreToolUse`, `PostToolUse`, `SubagentStart`, `SubagentStop`, `SessionStart`, `SessionEnd`, etc.) |
| `agent_id` | string (subagent events) | Subagent UUID |
| `agent_type` | string (subagent events) | Agent name (`Explore`, `Plan`, `general-purpose`, custom) |
| `last_assistant_message` | string (SubagentStop) | Subagent's final message before stopping |

The `transcript_path` and `agent_transcript_path` fields are **load-bearing**: a hook can use them to read the full session context, correlate events, or stream additional context back to the model. No other field reliably identifies the file location.

## One-liners

List all session transcripts for the current project:
```bash
ls -lt ~/.claude/projects/<encoded-cwd>/*.jsonl
```

List all subagent transcripts for a given session:
```bash
ls -lt ~/.claude/projects/<encoded-cwd>/<sessionId>/subagents/
```

Find the most recent session:
```bash
ls -t ~/.claude/projects/<encoded-cwd>/*.jsonl | head -1
```

Search all session transcripts for a string (e.g. a tool name or error):
```bash
grep -l "permission_denied" ~/.claude/projects/<encoded-cwd>/*.jsonl
```

Recover the original cwd from a session file (no encoding ambiguity):
```bash
head -1 ~/.claude/projects/<encoded-cwd>/<sessionId>.jsonl | jq -r .cwd
```
