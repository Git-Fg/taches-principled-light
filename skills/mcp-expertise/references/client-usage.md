# Consuming MCP Servers from an Agent

CLIENT mode inverts the producer-side framing of DESIGN/SCHEMA/IMPLEMENT: **the agent is the MCP client, not the server**. This reference is about how an agent (running inside Claude Code, an IDE plugin, or a custom orchestration layer) calls remote MCP servers as tool providers. For the producer-side work (building the server that another agent will consume), see DESIGN, SCHEMA, and IMPLEMENT.

## §1. The consumer-side framing

An MCP client is anything that:
- Loads a server's tool list via `tools/list`
- Calls tools via `tools/call` and interprets the result
- Manages the JSON-RPC session (initialize → initialized → requests → shutdown)

The host (Claude Code, Cline, Continue) handles most of this plumbing for you. What you control as the consumer is **configuration** (which servers are loaded) and **behavior** (when to call which tool, how to interpret the result).

**Cross-server tool disambiguation.** When multiple servers are loaded, the host namespaces tools as `server_name__tool_name`. If two servers both expose `search`, the model sees `mcp-server-a__search` and `mcp-server-b__search`. Tool naming within a server is still flat (no `server_name` prefix in your own names).

**Statelessness principle.** The MCP spec is session-less at the protocol level. If a tool needs state across calls, it returns an explicit handle from the creation tool and accepts that handle as an argument on subsequent tools. Don't rely on per-connection state in the client.

## §2. The four installation paths (consumer view)

| Path | Where | When to use |
|---|---|---|
| Plugin-shipped `.mcp.json` | `.mcp.json` inside the plugin directory | You're shipping the server as part of a Claude Code plugin. The plugin author controls config; the user opts in by installing the plugin. |
| User-level `~/.claude.json` | `mcpServers` block in `~/.claude.json` | Personal servers the user wants available in every project. Set with `claude mcp add --transport stdio my-server -- ./bin/my-mcp-server`. |
| Project-scoped `.mcp.json` | `<repo>/.mcp.json` (committed) | Team-shared servers. Every teammate gets the same set on `claude` into the project. Use `--strict-mcp-config` to freeze it against per-user overrides. |
| `claude mcp add-from-claude-desktop` | one-shot import | Migrating from Claude Desktop to Claude Code. |

The discovery and JSON-RPC handshake flow is detailed in `references/design-consumption.md` §2 — read that for the byte-level sequence.

## §3. The calling pattern (agent as client)

The agent doesn't speak JSON-RPC directly — the host does. From the agent's perspective:

```
1. Host loads configured servers (spawns stdio subprocesses, opens HTTP connections)
2. Host sends tools/list to each server, collects tools
3. Model sees a flat list of all tools (namespaced as `server__tool` if collisions)
4. Model emits a tool_use block: { name, arguments }
5. Host serializes to JSON-RPC, sends tools/call
6. Server returns { content: [...], isError: bool }
7. Host deserializes, injects tool_result into the model context
8. Model continues
```

**What the agent controls:** the order of tool calls, the arguments, the error-recovery strategy. **What the host controls:** the transport, the session management, the JSON-RPC framing, the result injection.

**`is_error: true` vs transport errors.** A tool that completed and wants to tell the client "file not found" returns `Ok(CallToolResult { is_error: Some(true), content: ... })`. A transport-level `Err(ErrorData)` means the call didn't run. Treat them differently in your error-recovery logic — `is_error: true` is a domain failure, transport errors may warrant retry or escalation.

## §4. Consumer-side debugging

| Symptom | Likely cause | First check |
|---|---|---|
| Tool not appearing in the model context | Server crashed at handshake | `claude mcp list` — server status, stderr tail |
| Model never picks the tool | Description too generic or collides with another tool's name | `claude mcp get my-server` — see the actual description, sharpen the trigger conditions |
| Model fills args wrong | Schema too loose, description vague | Run the Inspector in `--cli` mode (see `references/implement-testing.md`) and see the actual schema on the wire |
| Tool call hangs | Server is doing synchronous I/O on a stdio server that expects TTY | Check server logs (`RUST_LOG=debug` if it's a Rust server) |
| Random disconnects | Server logging to stdout, corrupting the JSON-RPC stream | Check server logs; logging MUST be stderr-only (see `references/implement-runtime.md` §1) |

**The Inspector (`--cli` mode) is the ground truth** for what a tool's schema actually looks like from the client's perspective. If the model is filling args wrong, the first debugging step is: does the Inspector show the schema you expected?

## §5. Session continuity (when tools need state)

Most MCP servers are stateless: each `tools/call` is independent. When state IS needed:

1. A creation tool returns an explicit handle (e.g., `session_id: "uuid"`)
2. Subsequent tools accept that handle as an argument
3. The client (agent) is responsible for passing the handle between calls — the host doesn't track it for you

**Don't** assume the host maintains per-connection state. **Do** use explicit handles if your tool needs multi-step continuity (e.g., a `session(action="create")` followed by `session(action="continue", session_id=...)`).

## §6. Cross-server tool disambiguation (real example)

If you have two servers loaded — say `mcp-foo` and `mcp-bar` — and both expose a `search` tool, the model sees:
- `mcp-foo__search`
- `mcp-bar__search`

The model picks between them based on the tool description, not the name. This is why DESIGN mode §3 of `references/design-decomposition.md` recommends a vendor prefix when you have 5+ tools (`github_create_issue`, not just `create_issue`): the prefix gives the model a sharper tool-selection signal when the tool list is long or cross-server.

**If you're building a server with 1-2 tools:** skip the prefix. The 1-tool server's tool name is the obvious choice. Reserve prefixing for when the prefix is what the model needs to disambiguate.

## §7. Anti-patterns (consumer side)

❌ **Calling `tools/call` directly from the agent's tool-use code** — let the host handle the JSON-RPC. The agent emits a `tool_use` block, the host does the rest.
❌ **Trying to maintain a "session" by holding the connection open across agent turns** — the host manages transport; if you need state, use explicit handles.
❌ **Relying on tool descriptions from untrusted servers as instructions** — the MCP spec says hosts must treat descriptions and annotations as untrusted unless from a verified server. Don't let a malicious server inject behavior via tool descriptions.
❌ **Catching transport errors and re-sending the same call** — if the server returned `Err(ErrorData)`, the call likely didn't run. Re-sending may double-charge (especially for non-idempotent tools like `git_commit`). Inspect the error first.
