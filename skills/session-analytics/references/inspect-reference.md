# INSPECT Mode Reference

Extracts structured data from Claude Code session transcripts (`~/.claude/sessions/{uuid}/raw-transcript.jsonl`).

## Privacy Protocol

Always apply before extracting any data:
- **Strip absolute paths** — replace `~/.claude/sessions/` with `{session}` in all output
- **Never retain user prompts verbatim** — paraphrase intent only
- **Redact environment variables and tokens** — show name, not value
- **Exclude file contents** — tool arguments may reference files, do not include file body data

## Output Formats

### SUMMARY (default)

Write to `docs/principled/scratch/session-inspect-{uuid}.md`:

```
Session: {uuid}
Duration: {ms}ms | Cost: ${cost}
Tools: {count} calls ({errors} errors)
Plugins: {list or NONE}
Rules: {list or NONE}
Hooks: {list or NONE}
Result: {success|error} — {stop_reason}

## Top Tool Calls
{tool_name}: {count} calls

## Errors
{error_message} (occurred {count} times)

## Skills Loaded
{skill_name} (via {trigger})
```

### FULL

Write to `docs/principled/scratch/session-inspect-{uuid}.json`:

```json
{
  "session_id": "{uuid}",
  "duration_ms": {number},
  "total_cost_usd": {number},
  "stop_reason": "{string}",
  "environment": {
    "plugins": ["{name}"],
    "rules": ["{path}"],
    "hooks": ["{event}"],
    "skills": ["{name}"]
  },
  "tool_calls": [
    {
      "tool": "{name}",
      "args": {object},
      "result_status": "success|error",
      "error_message": "{string}|null",
      "duration_ms": {number}
    }
  ],
  "assistant_messages": {
    "count": {number},
    "total_length_chars": {number}
  },
  "git_state": {
    "branch": "{string}",
    "diff_stats": "{string}"
  }
}
```

### FILTER

Apply `--filter` to extract only specific event types:

| Filter | Events Extracted |
|--------|-----------------|
| `errors` | `tool_result` with `subtype: error` — include error message and context |
| `tools` | All `tool_use` and `tool_result` events |
| `cost` | `result` events with token and cost breakdown |
| `skills` | `skill_load` events with skill name and trigger phrase |

Write filtered output to `docs/principled/scratch/session-inspect-{uuid}-{filter}.jsonl`.

## Tool Invocation Pattern

For INSPECT, spawn a a subagent explorer subagent:

```
Spawn a subagent explorer with scope:
"Read the session transcript at {path} and produce structured output. Apply the privacy scrub: strip absolute paths (replace ~/.claude/sessions/ with {session}), never retain user prompts verbatim, redact environment variables and tokens (show name, not value), exclude file contents."

Mode: {SUMMARY|FULL|FILTER}
Filter: {errors|tools|cost|skills}|none
Output path: {output_path}
```

## Error Handling

- If transcript is empty: report "No transcript data found" and suggest checking session validity
- If session is still running (incomplete JSONL): note in output and proceed with available data
- If jaq is unavailable for FILTER: fallback to Bash `grep` + `jq` or Python json module