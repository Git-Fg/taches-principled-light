# output-contract

The CLI's output contract is much simpler than the old wrapper's. Here's what an agent caller needs to know.

## Plain text output

```bash
$ claude -p "What is 2+2?"
4
```

Plain text on stdout. Easy to capture; hard to parse programmatically.

## JSON output

```bash
$ claude -p "What is 2+2?" --output-format json | jq .
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "duration_ms": 1234,
  "duration_api_ms": 1100,
  "num_turns": 1,
  "result": "4",
  "session_id": "abc-1234-...",
  "total_cost_usd": 0.0023,
  "usage": { ... }
}
```

The JSON envelope includes:
- `result` (string) — Claude's response
- `session_id` (UUID) — the session that was used or created
- `is_error` (boolean) — whether the call failed
- `duration_ms` / `duration_api_ms` (numbers) — wall-clock and API-only time
- `num_turns` (number) — how many model turns the call used
- `total_cost_usd` (number) — actual cost
- `usage` (object) — token usage breakdown

**`session_id` is inside the JSON output, not lifted to a top-level field.** If you need to resume the session, parse the JSON, extract `session_id`, and pass it to `--resume` on the next call.

```bash
SESSION_ID=$(claude -p "..." --output-format json | jq -r '.session_id')
claude --resume "$SESSION_ID" -p "Continue: also add tests"
```

## Exit codes

- `0` — success
- non-zero — failure (check stderr for the reason)

The CLI uses raw Unix exit codes, not JSON-RPC codes. If you need a structured error, parse the JSON output and check `is_error`.

## Stream-json output

```bash
claude -p "..." --output-format stream-json
```

Writes newline-delimited JSON events as they happen. Each line is a typed event (assistant message, tool use, tool result, etc.). Use this for realtime UI or for piping into another agent's input stream.
