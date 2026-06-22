# session — lifecycle

Sessions are how you keep context across multiple invocations. The CLI manages session IDs as UUIDs; you pass them between invocations to resume continuity.

## Resume an existing session

```bash
claude --resume <session-uuid> -p "Continue the refactor: also add tests"
```

The UUID must be valid (8-4-4-4-12 hex). If invalid, the CLI rejects it.

## Open the resume picker (interactive)

```bash
claude --resume
```

With no value, `--resume` opens an interactive session picker. Filter with a search term:

```bash
claude --resume "auth refactor"
```

(The interactive picker is unavailable in non-TTY contexts — for scripted use, pass an explicit UUID.)

## Continue the most recent session in the current directory

```bash
claude --continue -p "Continue the refactor"
```

This is shorthand for "find the most recent session whose CWD matches the current directory and resume it". Use this when you've been iterating and just want to pick up where you left off.

## Use an explicit session ID

```bash
claude --session-id <uuid> -p "Start a new session with this specific ID"
```

The UUID must be valid. Use this when you want to pre-allocate a session ID (e.g., for logging or external tracking) before the first invocation.

## Branch a session

```bash
claude --resume <existing-uuid> --fork-session -p "Try a different approach"
```

`--fork-session` creates a new session ID branched from the existing one. The original session is unchanged. Use this for A/B exploration without polluting the original.

## List sessions

The CLI does not have a dedicated `list-sessions` flag. The two ways to enumerate sessions:

1. **Interactive**: `claude --resume` with no value opens the picker, which lists all known sessions.
2. **Programmatic**: read `~/.claude/sessions/` (or `$CLAUDE_CONFIG_DIR/sessions/`) directly. The CLI stores session metadata as JSONL files.

For a Bash script, the second approach is the only one that works in non-TTY contexts.

## Inspect session metadata

The CLI does not have a dedicated `session-info` flag. To get metadata:

- For an active session: the JSON output of `claude -p --output-format json` includes the session ID.
- For a stored session: parse the session's JSONL file in `~/.claude/sessions/`.

## Close a session

The CLI does not have a dedicated `close-session` flag. Sessions are closed by:

- Exiting the interactive session (Ctrl-C, Ctrl-D, or natural end of conversation).
- Letting the session expire (the CLI's default retention policy is 30 days; configurable via `--setting-sources` and project settings).
- Using `--no-session-persistence` to opt out of persistence entirely (sessions are not saved to disk and cannot be resumed).

## Resume a session linked to a PR

```bash
claude --from-pr                    # interactive picker
claude --from-pr <pr-number>        # session linked to the given PR
claude --from-pr https://github.com/<owner>/<repo>/pull/<pr-number>
```

Resumes a session that was started in the context of a specific PR. The session picker accepts an optional search term.
