# MCP Design Decisions: Thesis, Decomposition, Output, Errors, Pass-Through, Context Budget

Reference for the design decisions that shape an MCP server's tool surface. Read it before committing to a decomposition, output contract, or error-code scheme. The hub itself is a router — it points you at the right reference, the references carry the mechanism.

## §1. The core design thesis: equilibrated recursivity

**The schema must be flat; the data must be deep.**

- **Tool parameter surface** (what the LLM sees and fills): ≤ 2 nesting levels. Agent-callable schemas must be flat enough for an LLM to construct arguments on the first try.
- **Complex structures** (JSON Schemas, prompts, configuration objects, deep data): passed as serialized strings (`"…JSON-encoded…"`) or file references. The wrapper server validates syntax (JSON parseable, file readable) but not semantics — it passes the blob through.

This is the sweet spot: the agent reasons about simple keys, but the wrapped implementation processes arbitrarily deep content.

**Why it works:** flat schemas fit comfortably in the LLM's prompt, allow accurate tool-selection and argument-fill, and stay under the context budget. The pass-through lets you wrap anything (CLIs, APIs, databases) without trying to make the schema understand the wrapped system.

## §2. Tool decomposition: 1 tool vs N tools

**Default rule: decompose by operational domain.** Expose ~6 tools, not 1 mega-tool. If you have 50+ CLI flags, splitting them into 6 thematic tools beats exposing all 50 in one schema.

| Concern | Tool count | Why |
|---|---|---|
| Single, atomic operation | 1 tool | No decomposition needed; e.g., `read_file(path)` |
| Multiple domains in one system | 4-8 tools | Each domain is its own tool: `claude_execute`, `claude_session`, `claude_context`, `claude_review`, `claude_agent`, `claude_config` |
| Action set on one entity | 1 tool with `action` enum | Use a discriminator instead of one tool per action: `session(action="resume" | "continue" | "fork" | "list", ...)` |
| Cross-cutting concern | Consider a single tool | If 3+ tools always need the same 3 params, maybe one tool is right |
| Test framework has 200+ operations | Decompose by lifecycle: `test.run`, `test.coverage`, `test.list`, `test.filter` | Don't dump all 200 into one tool |

**Decomposition rules (when in doubt):**
1. **Context budget dominates.** A 50-param tool eats 5+ KB of tool-definition tokens; 6 tools at 8-10 params each stays under 2 KB each.
2. **Tool-selection accuracy dominates.** LLMs are better at picking between 6 distinct tools than between 1 mega-tool and 4 vague alternatives.
3. **Atomic operations stay together.** Don't split `read + write` if they're always called as a pair; do split `read` from `delete`.
4. **`action` enum beats 5 sibling tools** when the action set is bounded and the args overlap (e.g., `session(action=...)` not `session_resume/session_continue/session_fork`).
5. **The user should be able to describe each tool in one sentence.** If a tool's description needs two sentences, the tool is probably doing two things.

**Signals to MERGE tools:**
- The agent always calls them in sequence with no independent utility
- Args overlap ≥80% (different action, same params)
- The decomposition is by "version" or "vintage" (anti-pattern: `v1_search`, `v2_search`)

**Signals to SPLIT tools:**
- Two operations are sometimes called independently
- A user would describe them with different verbs
- Combining them costs >1 KB of context for rarely-used args
- One is read-only and the other is destructive (separation helps safety)

## §3. Decomposition worked example (synthetic: `git-cli`)

**This is a hypothetical teaching example, not a shipped wrapper.** It illustrates the same 6-tool decomposition principle that the marketplace's former `claude-cli-wrapper` plugin demonstrated, but uses a well-known CLI (`git`) that every reader has used. The tool names below are illustrative; no plugin in this marketplace ships a `git-cli` wrapper.

Suppose we wrap `git` as MCP tools. The natural decomposition is 5 tools, not 1, because each operation is a distinct verb with a distinct safety profile:

| Tool | Operational domain | Approx params | Annotation |
|---|---|---|---|
| `git_status` | Working-tree state | 4 | (none) |
| `git_diff` | Code review (read-only) | 3 | `readOnlyHint: true` |
| `git_commit` | Snapshot a change (destructive) | 3 | `destructiveHint: true` |
| `git_log` | History (read-only) | 3 | `readOnlyHint: true` |
| `git_branch` | Branch management (mostly destructive) | 3 | `destructiveHint: true` |

Total: ~16 params across 5 tools. Compare to a single `git_run` tool exposing the ~150 flags of `git` — that would violate the context budget (≤2 KB per tool schema) and bury the high-traffic operations in rarely-used flag noise.

**Lessons from this decomposition:**

- **Read/write separation drives the safety split.** `git_diff` and `git_log` are read-only — they should carry `readOnlyHint: true` so the MCP host can auto-approve them or restrict them to safer execution contexts. `git_commit` and `git_branch` carry `destructiveHint: true`. This split makes the safety profile of each tool self-documenting.

- **The high-traffic tool gets the most params.** `git_status` is the workhorse (called constantly during development), so it earns 4 params (e.g., `path`, `short`, `branch`, `porcelain`). The rarer operations get 3. The most common tool carries the most context cost; that's the right trade.

- **No `action` enum is needed here.** Each tool has a distinct verb (`status`, `diff`, `commit`, `log`, `branch`), so a discriminator is unnecessary. Reserve the `action` enum pattern for tools where multiple operations share a session/context — for example, a `git_session` tool that wraps `git rebase`, `git merge`, `git rebase --abort`, `git rebase --continue`, `git rebase --skip` would benefit from an `action` enum because all five share the same rebase state.

- **The decomposition mirrors the user's mental model.** A developer thinks of "I want to see the diff" as a single operation, not as a `git_diff` mode inside a `git_query` tool. Mirror the user's verbs in your tool names.

- **When NOT to use this pattern.** If the wrapped CLI has only 1-2 operations, a single tool is correct. Forcing a decomposition on a 1-operation CLI just adds tools the user has to learn. The 5-tool shape above works because `git` has 5 distinct operational domains; the same shape would be wrong for a CLI with 2 operations.

## §4. Output contract: CallToolResult text+JSON

MCP tools return `CallToolResult` with `content` items. The dominant pattern is text-with-JSON-payload:

```json
{
  "type": "text",
  "text": "{\"exit_code\": 0, \"stdout\": \"...\", \"stderr\": \"\", \"session_id\": \"uuid\", \"output_parsed\": { ... }}"
}
```

**Fields the text payload typically contains:**
- `exit_code` (for CLI wrappers) or `success` (boolean for pure function tools)
- `stdout` / `output` — raw output (or parsed JSON if `output_format=json`)
- `stderr` / `error` — error stream
- `session_id` — for session continuity
- `output_parsed` — convenience field: pre-parsed JSON when valid
- `error` — error description if non-success

**Why text-with-JSON, not the resource type?** Because tool output is ephemeral execution data, not a persistent file or URI. Text is the most portable across MCP clients.

**Alternative output types (use sparingly):**
- `image` — for vision tools
- `audio` — for speech tools
- `resource` — link to a persistent resource (rare for tool output)

**The hard rules:**
- Tool output MUST be one of the defined `content` types
- Don't return raw non-JSON strings the LLM has to parse
- Don't put secrets in tool output unredacted
- Truncate large outputs (sensible default: 50 KB max, with `[truncated, full output at <URI>]` notice)

## §5. JSON-RPC error code discipline

MCP uses JSON-RPC 2.0 over the wire. Use the standard error codes plus your own for domain:

| Code | Name | When |
|---|---|---|
| **-32700** | Parse error | Malformed JSON, invalid UTF-8, missing required fields |
| **-32600** | Invalid Request | Not a valid JSON-RPC request (wrong shape) |
| **-32601** | Method not found | Unknown method (e.g., tool name typo) |
| **-32602** | Invalid params | Tool args failed schema validation (this is the **most common** in practice) |
| **-32603** | Internal error | Wrapper/SDK crash, not a domain error |
| **-32000 to -32099** | Server error | Custom codes — define per server |

**MCP convention (community-observed):**
- `-32602` for any schema violation, including enum mismatch, missing required, type mismatch
- `-32603` ONLY for wrapper/SDK crashes (panic, unhandled exception) — never for "tool returned an error"
- Custom `-32xxx` codes (between -32099 and -32000) for domain-specific failures: e.g., `-32001` for "CLI exited with non-zero", `-32002` for "rate limited", `-32003` for "dependency download failed"
- Always include a `data` field with structured details (string message + optional context object)

**Example error response:**
```json
{
  "jsonrpc": "2.0",
  "id": 42,
  "error": {
    "code": -32001,
    "message": "CLI exited with non-zero status",
    "data": { "exit_code": 2, "stderr": "command not found: foo" }
  }
}
```

## §6. Tool annotations

MCP tools can declare behavior hints via annotations. The host (Claude Code, etc.) uses these for safety prompts, UI hints, and tool-selection:

| Annotation | Type | Meaning |
|---|---|---|
| `title` | string | Human-readable tool name (default: name) |
| `readOnlyHint` | boolean | Tool only reads, never modifies state |
| `destructiveHint` | boolean | Tool modifies or deletes state (used by `Auto` mode permissions) |
| `idempotentHint` | boolean | Repeated calls with same args have the same effect |
| `openWorldHint` | boolean | Tool interacts with external systems (network, filesystem, etc.) |

**Annotation discipline:**
- `readOnlyHint: true` for queries, searches, reads
- `destructiveHint: true` for deletes, writes, sends
- `idempotentHint: true` for `set_X(value)` if calling it 3 times = calling it once
- `openWorldHint: true` for anything that hits network, file system, subprocess
- **Honesty matters:** these are TRUST signals. If you mark `readOnlyHint: true` but the tool secretly writes to a cache, the host's safety reasoning is broken.

**The MCP spec notes (2025 spec):** hosts must consider tool descriptions and annotations as untrusted unless from a trusted server. So don't rely on the host to gate based on these — gate in your own auth/permission layer.

## §7. The pass-through principle

For any wrapped feature that requires deep nesting (JSON Schemas, complex settings, agents configs, etc.), the MCP tool accepts it as a **serialized string or file path**. The wrapper validates syntax (JSON parseable, file readable) but not semantics.

**Example — `claude_execute.structured_output_schema_json`:**
```json
{
  "structured_output_schema_json": {
    "type": "string",
    "maxLength": 8192,
    "description": "JSON-encoded JSON Schema for structured output validation. The schema itself is validated by Claude Code, not this server."
  }
}
```

The actual schema is a deep object (could be 100+ lines, nested `anyOf`, `oneOf`, etc.). The LLM fills a STRING; the server forwards the string; Claude Code parses and validates. The tool schema stays flat.

**When to pass-through:**
- JSON Schemas for structured output
- Settings/permissions JSON
- Agent role definitions
- Tool definitions themselves (when wrapping a tool framework)
- Any "deep config" the wrapped system needs

**When NOT to pass-through:**
- Things the LLM should reason about (file paths, IDs, choices)
- Things that need server-side validation (auth tokens, rate limits)
- Things where a flat representation exists and is more useful

## §8. Context budget: keep total schema under 12 KB

**Rule of thumb:** all tool definitions combined should be < 12 KB serialized, which keeps the tool-definition token cost under 3k tokens (cheap for the LLM to carry per turn).

**Calculation:**
- Each tool definition has: name, description, inputSchema (JSON Schema)
- A well-designed tool: ~300-800 bytes serialized
- 6 tools at 500 bytes each: 3 KB
- 12 tools at 800 bytes each: 9.6 KB
- Beyond 12 tools or so, every additional tool costs more in selection noise than it saves in decomposition

**If you're over budget:**
1. Shorten descriptions (use action verbs, drop examples that fit in `description` of the property)
2. Trim `description` on properties (one sentence each)
3. Move long descriptions to `references/` files (rarely the right move for tool defs)
4. Decompose one fat tool into 2-3 thin tools (decomposing itself can save context because unused tool defs can be selectively omitted by the host)
