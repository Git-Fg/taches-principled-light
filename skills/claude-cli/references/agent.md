# agent — background management

The `claude` CLI has two ways to spawn agents:

1. **Per-invocation agent selection** (`--agent <name>`) — pick an agent for the current session
2. **Background agent view** (`claude agents`) — manage agents that are running in the background

## Spawn an agent for the current session

```bash
claude -p "Review this codebase through the OWASP Top 10 lens (injection, auth bypass, exposed secrets, insecure crypto)" --agent general-purpose
```

The agent is selected for the current session only. If `--agent` is not specified, the default agent is used (or whatever the `agent` setting resolves to).

## Define an inline custom agent

```bash
claude -p "Review this PR" \
  --agents '{"reviewer": {"description": "Reviews code for security and quality issues", "prompt": "You are a code reviewer focused on security. For each finding, cite file:line and explain the exploit."}}'
```

`--agents` is a JSON object defining custom agents for this session. The keys are agent names; the values have `description` and `prompt` fields.

## Manage background agents

```bash
claude agents                      # open the interactive agent view
claude agents --json               # list live background sessions as JSON, exit
claude agents --cwd /path/to/proj  # filter by starting directory
```

`claude agents --json` is the right pattern for an agent caller that needs to enumerate running sessions. The output is a JSON array of session metadata.

## Set defaults for dispatched sessions

When using the agent view, you can set defaults that apply to all sessions dispatched from it:

```bash
claude agents --model opus                          # default model
claude agents --effort high                         # default effort
claude agents --permission-mode acceptEdits         # default permissions
claude agents --mcp-config /path/to/config.json     # default MCP config
claude agents --add-dir /extra/dir                  # additional directories
```

## Terminate a background agent

The CLI does not have a `--kill-agent` flag. To terminate a background agent:

- In the interactive agent view (`claude agents`): use the keyboard shortcut to terminate the selected session.
- From a script: send the process a signal. The session is a regular OS process; `kill <pid>` works but is unclean. Prefer the interactive view or letting the agent complete naturally.
- Set a max budget with `--max-budget-usd` so the agent stops itself at the spend cap.

For agent-runtime semantics (subagent orchestration, parallel dispatch, etc.), see the marketplace's orchestrating-subagents skill. The CLI flags here are the surface; the orchestration pattern is the marketplace's separate concern.
