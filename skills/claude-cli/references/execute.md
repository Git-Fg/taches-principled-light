# execute — the workhorse

The primary operation. Run a prompt, get output. The `claude -p` form is non-interactive: it reads the prompt, processes it, writes the result to stdout, and exits.

## Minimum viable invocation

```bash
claude -p "What is 2+2?"
```

This works but writes plain text. For an agent caller, you almost always want JSON.

## The canonical invocation

```bash
claude -p "Refactor src/auth.rs to use the newtype pattern" \
  --output-format json \
  --model sonnet \
  --effort high \
  --permission-mode acceptEdits
```

Flags by category:

**Execution mode:**
- `-p, --print` — non-interactive, write response to stdout, exit. This is the universal invocation prefix for headless use.
- `--bare` — minimal mode. Skips hooks, LSP, plugin sync, attribution, auto-memory, background prefetches, keychain reads, and CLAUDE.md auto-discovery. Sets `CLAUDE_CODE_SIMPLE=1`. Use only when you need to bypass plugin/hook machinery for a clean test or sandbox.

**Output:**
- `--output-format text|json|stream-json` — serialization. Default `text`. Use `json` when an agent will parse the response. Use `stream-json` for realtime token-by-token output.
- `--json-schema <schema>` — JSON Schema for structured output validation. Inline string, not a file path. The CLI validates the response against the schema; if it doesn't match, the call fails. **This is the right way to get typed output from Claude** — much better than asking Claude to "please respond in JSON" in the prompt.
- `--input-format text|stream-json` — input format (default `text`). Use `stream-json` for realtime streaming input.
- `--include-partial-messages` — include partial message chunks as they arrive (only with `--print` and `--output-format=stream-json`).
- `--replay-user-messages` — re-emit user messages from stdin back on stdout for acknowledgment (only with `stream-json` input + output).

**Model / effort / budget:**
- `--model <model>` — `sonnet`, `opus`, `haiku`, or a full name like `claude-opus-4-8`. Aliases resolve to the latest version of that family.
- `--fallback-model <model>` — automatic fallback when the default model is overloaded or unavailable. Only works with `--print`.
- `--effort <level>` — `low`, `medium`, `high`, `xhigh`, `max`. Default is whatever's configured in the project. Higher effort = more reasoning, more cost, more time.
- `--max-budget-usd <amount>` — spend cap for this invocation. Only works with `--print`. The CLI exits cleanly when the budget is reached.

**Permissions:**
- `--permission-mode <mode>` — `acceptEdits`, `auto`, `bypassPermissions`, `default`, `dontAsk`, `plan`. **For agent-driven invocations, use `acceptEdits`** so Claude can edit files without prompting the user.
- `--allow-dangerously-skip-permissions` — make `bypassPermissions` available without defaulting to it.
- `--dangerously-skip-permissions` — bypass all permission checks. **Recommended only for sandboxes with no internet access.** Do not use this in shared environments.

**Tool access:**
- `--allowedTools, --allowed-tools <tools...>` — comma- or space-separated allowlist. Example: `Bash(git *),Edit`. Repeatable; multiple values accumulate.
- `--disallowedTools, --disallowed-tools <tools...>` — denylist. Same syntax.
- `--tools <tools...>` — specify the available built-in tools. `""` disables all tools, `"default"` uses the full set, or list names like `Bash,Edit,Read`.

**System prompt:**
- `--system-prompt <prompt>` — override the entire system prompt. Use for forcing a specific persona.
- `--append-system-prompt <prompt>` — extend the default system prompt. Use for adding context (project conventions, role).
- `--exclude-dynamic-system-prompt-sections` — move per-machine sections (cwd, env, memory paths, git status) out of the system prompt into the first user message. Improves cross-user prompt-cache reuse. Only applies with the default system prompt (ignored with `--system-prompt`).

**MCP / extensions:**
- `--mcp-config <configs...>` — load MCP servers from JSON files or inline JSON strings. Space-separated. Each config is independent.
- `--strict-mcp-config` — only use MCP servers from `--mcp-config`, ignoring all other MCP configurations.
- `--plugin-dir <path>` — load a plugin from a directory or .zip for this session only. Repeatable.
- `--plugin-url <url>` — fetch a plugin .zip from a URL for this session only. Repeatable.

**Metadata:**
- `-n, --name <name>` — display name for the session (shown in `/resume` picker and terminal title).
- `--setting-sources <sources>` — comma-separated list of setting sources to load: `user`, `project`, `local`. Default loads all three.

**File preloading:**
- `--file <specs...>` — file resources to download at startup. Format: `file_id:relative_path`. Used for hosted files.

## Example: structured output (the right way to do it)

```bash
claude -p "Classify this support ticket: '$TICKET_TEXT'" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"category":{"type":"string","enum":["bug","feature","question"]},"priority":{"type":"string","enum":["low","medium","high"]}},"required":["category","priority"]}'
```

Claude's response is validated against the schema. If it doesn't match, the call fails with a validation error.
