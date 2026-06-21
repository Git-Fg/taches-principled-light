# Consuming MCP Servers in Claude Code

The schema design work in the hub and the `design-decomposition` reference is producer-side. This reference is the consumer-side view: once your server ships, **how does Claude Code actually discover, present, and use your tools?** Most of the design decisions show up here as observed behavior.

## §1. Installation paths

**1. Plugin-shipped `.mcp.json` (recommended for skills/plugins):**
Place a `.mcp.json` in the plugin root and Claude Code auto-loads it
when the plugin is enabled:
```json
{
  "my-server": {
    "command": "./bin/my-mcp-server",
    "args": [],
    "env": {}
  }
}
```
No `"type": "stdio"` needed — stdio is the default. Adding it
explicitly is harmless but redundant.

**2. User-level `~/.claude.json` (for personal servers):**
Use `claude mcp add --transport stdio my-server -- ./bin/my-mcp-server`.
Equivalent JSON lands under `mcpServers` in the user config.

**3. Project-scoped `.mcp.json` (for repos the team shares):**
Place in the repo root and commit it. Each teammate gets the same
servers when they `claude` into the project. The `--strict-mcp-config`
flag freezes the project config so a teammate's personal `~/.claude.json`
additions don't leak in.

**4. `claude mcp add-from-claude-desktop`:** one-shot import from a
Desktop config. Useful for moving from Claude Desktop into Claude Code.

## §2. The discovery flow (what Claude Code actually does)

```
claude -p "..." (or interactive session start)
  ↓
load user mcpServers + project .mcp.json + plugin .mcp.json
  ↓
for each server: spawn child process, capture stdio
  ↓
JSON-RPC initialize handshake
  → server returns: protocolVersion, serverInfo, capabilities, instructions
  ↓
client sends notifications/initialized
  ↓
client sends tools/list
  → server returns: list of { name, description, inputSchema, annotations? }
  ↓
client prepends server instructions to the system prompt (if any)
client prepends each tool's description + JSON schema to the model context
  ↓
[per turn]
  → model emits a tool_use block (tool name + arguments)
  → client sends tools/call
  → server returns: { content: [...], isError: bool }
  → model sees the result, continues
  ↓
shutdown
  → stdio: client closes the child process's stdin
```

**Where your design choices land in this flow:**

| Producer-side decision | Consumed by Claude Code as |
|---|---|
| `ServerInfo::instructions` | Prepended to system prompt (cached per session) |
| `ServerInfo::capabilities.tools` | Tells client it can request `tools/list` and `tools/call` |
| `#[tool(description = "...")]` | Per-tool description in model context (selects and triggers tool use) |
| `inputSchema` (from `JsonSchema` derive) | The argument schema the model must satisfy when emitting `tool_use` |
| `#[tool(annotations(...))]` | Hints the host's safety layer reads to decide confirmation prompts, parallelism, retry |
| Server name (`my-server` in `.mcp.json`) | Becomes the `serverName` prefix in tool identifiers; affects how the model disambiguates `my-server__my_tool` vs another `my_tool` |

## §3. Verifying discovery and behavior

```bash
# See what Claude Code thinks is installed
claude mcp list

# Get verbose connection + handshake output
claude mcp get my-server

# Test a tool call without the model in the loop (use --cli mode; the interactive web UI is for humans)
npx @modelcontextprotocol/inspector --cli ./bin/my-mcp-server --method tools/list
npx @modelcontextprotocol/inspector --cli ./bin/my-mcp-server --method tools/call --tool-name mytool --tool-arg key=value
# → Inspector in --cli mode speaks JSON-RPC over stdio directly
# → Lets you call tools/list, tools/call with arbitrary args
# → Shows every request/response frame on the wire
# → No browser needed — works in any shell, including headless agents
```

For more inspector patterns (config files, JSON arguments, remote servers, custom headers, transport selection), see the IMPLEMENT mode's testing reference at `references/implement-testing.md`.

**The Inspector (`--cli` mode) is the ground truth** for what your schema actually looks
like on the wire. If the model is calling the tool with wrong args, the
first debugging step is: does the Inspector show the schema you thought
you wrote?

## §4. What the model sees (and doesn't)

The model sees:
- Each tool's `name` and `description` verbatim
- The full `inputSchema` as compact JSON (this is the 12 KB context cost from the design-decomposition reference)
- The server's `instructions` once per session
- Annotations indirectly (the host's safety layer reads them; the model itself doesn't see them as text)

The model does NOT see:
- The Rust type names or struct definitions
- The `#[serde(rename = "...")]` aliases — it sees the renamed output
- The `#[schemars(description = "...")]` for fields NOT in the schema (e.g. `Option<T>` fields with `skip_serializing_if` set so they're absent)
- The `inputSchema`'s `examples` unless the host surfaces them
- Tool names from other servers unless those servers are also loaded

## §5. Common consumer-side debugging

| Symptom | Likely cause | Fix |
|---|---|---|
| Tool not showing up in `claude` session | Server crashed at handshake; check stderr | `RUST_LOG=debug claude` and re-run |
| Model never picks the tool | Description is too generic or collides with another tool | Rename to `verb_noun`; sharpen the description's trigger conditions |
| Model picks the tool but fills args wrong | Schema is too loose, or `description` is vague | Add constraints (`enum`, `range`, `regex`); rewrite descriptions with "Use when…" framing |
| Model sends a hallucinated field | Missing `additionalProperties: false` / `deny_unknown_fields` | Add both |
| Model calls a "destructive" tool without confirmation | `destructiveHint` is missing or `false` | Add `annotations(destructive_hint = true)` |
| Server returns content but model ignores it | Output format is `String` where a typed envelope would be better | Return a JSON envelope; see `claude-cli-wrapper` tools for the pattern |
| Random disconnects mid-session | `println!` somewhere in your tool impl | Replace with `tracing` to stderr (the stderr-only logging rule lives in the IMPLEMENT mode's runtime reference at `references/implement-runtime.md`) |

> **Iterative loop:** change the schema → rebuild → restart Claude Code
> (or use a plugin dev mode that hot-reloads) → repeat the same prompt →
> watch whether the model's tool call improved. The first version is
> never the right version.
