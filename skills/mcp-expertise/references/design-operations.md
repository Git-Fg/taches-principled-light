# MCP Operations Discipline: Capabilities, Security, Naming, Validation

Reference for the four operational disciplines that separate a working MCP server from a Claude-Optimal one: capability negotiation, the security checklist, tool naming conventions, and the validation checklist. Read it before declaring a server production-ready.

## §1. Capability negotiation

Every MCP server declares what it supports in its `ServerCapabilities` during the `initialize` handshake:

| Capability | What you expose | How to declare |
|---|---|---|
| `tools` | Callable functions | `tools: {}` or `tools: { listChanged: true }` (if you notify on changes) |
| `resources` | URI-addressed read-only data | `resources: {}` or `resources: { subscribe: true, listChanged: true }` |
| `prompts` | Reusable prompt templates | `prompts: {}` or `prompts: { listChanged: true }` |
| `logging` | Server can emit log messages | `logging: {}` |
| `completions` | Server supports argument completion | `completions: {}` |
| `tasks` (experimental) | Server can run long-running tasks | `tasks: {}` (not yet standardized) |

**Server-initiated capabilities (from server to client):**
- `sampling` — server can ask the host to run an LLM completion (enables agentic loops)
- `elicitation` — server can ask the host to request user input (consent flows, structured forms)
- `roots` — server can ask the host about filesystem boundaries

**Negotiation rules:**
- Only declare what you actually implement (don't claim `sampling` if you never call `create_message`)
- `listChanged: true` means you'll send `notifications/tools/list_changed` when the tool set changes
- The host uses your declared capabilities to know which requests to send

## §2. Security: the MUST/SHOULD/MAY checklist

**MUST (per spec):**
- Validate all input against your JSON Schema (server-side, regardless of client-side validation)
- Obtain explicit user consent before invoking any tool that takes a destructive action
- Never expose user data to a server without consent
- Validate the `Origin` header on every Streamable HTTP connection (DNS rebinding protection)
- Use `additionalProperties: false` on your tool schemas (don't accept undocumented params)
- Treat tool descriptions and annotations as untrusted input (don't let them inject instructions)

**SHOULD:**
- Add authentication to remote servers (OAuth 2.0 Resource Server, since June 2025 spec)
- Use HTTPS for Streamable HTTP in production
- Rate-limit clients
- Sanitize paths against traversal attacks
- Bound resource consumption (memory, CPU, file handles, subprocess count)
- Log to stderr only (stdout is the protocol stream)
- Log enough to debug, not so much it leaks secrets

**MAY:**
- Cache responses
- Support both stdio and Streamable HTTP transports
- Send progress notifications for long-running operations
- Implement cancellation for in-flight tool calls

**Anti-pattern: hidden state in tool calls.** MCP has no protocol-level session. If your tool needs state, return an explicit handle from a creation tool, then accept that handle as an argument on subsequent tools. Don't rely on implicit per-connection state.

## §3. Tool naming conventions

The MCP spec says tool names SHOULD be 1-128 characters, case-sensitive, only:
- Uppercase and lowercase ASCII letters (A-Z, a-z)
- Digits (0-9)
- Underscore (`_`), hyphen (`-`), dot (`.`)

**Best practices:**
- `snake_case` for multi-word names (matches Python/JSON convention): `read_file`, `create_issue`
- `verb_noun` pattern: `search_products`, `move_application`, not just `products` or `application`
- Group by domain with a prefix when you have many tools from one vendor: `github_create_issue`, `github_list_repos` (when you have 5+ tools, the prefix helps selection)
- Avoid generic names that conflict with other servers' tools: `search`, `query`, `run`
- For tools with an `action` enum, the tool name describes the entity, the action is the discriminator: `session(action="resume")`, not `resume_session`

**Test for clarity:** a user who sees the tool name in a list should be able to guess what it does. `get_weather(city)` ✓ vs `gw(city)` ✗.

## §4. Validation: the Claude-Optimal checklist

A server passes when:

1. **Tool discovery works** — all tools load in Claude Code (or other hosts) without `Invalid input: expected "object"` errors.
2. **Single-shot accuracy** ≥ 90% — in `--print --output-format json` mode, the LLM generates valid tool arguments on the first attempt in ≥ 90% of test invocations.
3. **Context efficiency** — total serialized schema < 12 KB, per-tool < 2 KB.
4. **Pass-through integrity** — complex blobs (JSON Schemas, settings) round-trip through your tool without mutation.
5. **Session continuity** — `session_id` from one tool works in another without manual transformation.
6. **Headless reliability** — the wrapper never hangs waiting for TTY. `mode: "interactive"` is rejected or sandboxed when stdin is not a TTY.
7. **Error distinction** — JSON-RPC `-32602` for schema violations, custom codes for domain failures, `-32603` only for wrapper crashes.
8. **Schema hygiene** — `additionalProperties: false` on every object schema, `description` on every property, `required` for non-optional args.

**Worked example: `claude-cli-wrapper` v0.2.0 in this marketplace** meets all 8 criteria (verifiable in its marketplace description).
