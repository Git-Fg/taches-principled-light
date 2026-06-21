---
name: engineering-mcp
description: >
  Load when designing, building, or evaluating an MCP server end-to-end —
  tool decomposition, JSON Schema authoring, Rust implementation with rmcp,
  agent-as-consumer patterns, or quality auditing against an 8-dimension rubric.
  Use when the user says 'design an MCP server', 'write a tool schema',
  'implement an MCP server in Rust', or 'evaluate MCP quality'. Do NOT use for
  general REST API design (use restructuring-code) or general code quality
  review (use reviewing-and-polishing).
when_to_use: |
  - DESIGN: "design an MCP server", "decompose MCP tools", "1 tool vs N tools", "MCP output contract", "MCP error codes", "MCP security checklist", "capability negotiation", "Claude-Optimal validation"
  - SCHEMA: "write a tool schema", "JSON Schema for MCP", "LLM-friendly schema", "constraint discipline", "enum vs oneOf", "additionalProperties false", "property naming", "tool description writing"
  - IMPLEMENT: "implement an MCP server in Rust", "rmcp + schemars", "stdio vs Streamable HTTP", "MCP server lifecycle", "error mapping", "build an MCP tool"
  - CLIENT: "call an MCP server from an agent", "agent as MCP consumer", "consume MCP tools", "MCP client patterns"
  - QUALITY: "evaluate an MCP server", "MCP quality judge", "audit MCP quality", "score MCP server"
---

# engineering-mcp

The MCP expertise hub. Five modes cover the full MCP server lifecycle: design (how to think about tool decomposition, output contracts, error codes, security), schema (how to write LLM-friendly JSON Schemas), implement (how to build a Rust MCP server with rmcp + schemars), client (how to consume MCP servers from an agent context), and quality (how to evaluate an existing server against the Claude-Optimal rubric).

The hub is a pure router. Mechanism content lives in `references/` and loads only on imperative citation. Do not implement or design from this file alone — pick a mode, read its references, then act.

## Decision Router

```
IF tool decomposition, output contract, error codes, security, naming, capability negotiation → DESIGN
IF JSON Schema authoring, constraints, descriptions, property naming, schema pitfalls → SCHEMA
IF Rust implementation with rmcp + schemars, transport choice, lifecycle, testing → IMPLEMENT
IF agent calling remote MCP servers, consumer-side patterns, MCP client usage → CLIENT
IF MCP quality evaluation, judge rubric, audit → QUALITY
```

## §1. When this skill fires

**Use this skill when the user says any of:**

- "Design my MCP server" / "decompose MCP tools" / "1 tool vs N tools" / "MCP output contract" / "MCP error codes" / "MCP security checklist" / "MCP capability negotiation" / "wrap a CLI as an MCP server" / "what makes a Claude-Optimal MCP server"
- "Write a tool schema" / "JSON Schema for MCP" / "LLM-friendly schema" / "constraint discipline" / "enum vs oneOf" / "required vs optional" / "tool description writing" / "the LLM keeps getting args wrong"
- "Implement an MCP server in Rust" / "rmcp + schemars" / "stdio vs Streamable HTTP" / "MCP server lifecycle" / "add a tool" / "build an MCP tool"
- "Call an MCP server from my agent" / "agent as MCP consumer" / "consume MCP tools" / "MCP client patterns"
- "Evaluate my MCP server" / "MCP quality judge" / "audit MCP quality" / "score this MCP server"

---

# Mode: DESIGN

Tool decomposition (1 tool vs N), the equilibrated-recursivity thesis (flat schema, deep data via pass-through), output contracts, JSON-RPC error code discipline, tool annotations, security checklist, capability negotiation, naming conventions, the Claude-Optimal validation.

You MUST read `references/design-decomposition.md` BEFORE committing to a tool decomposition or output contract. It teaches the equilibrated-recursivity thesis, the 1-vs-N decomposition matrix with merge/split signals, the synthetic `git-cli` 5-tool worked example, the text-with-JSON output contract, the JSON-RPC error codes (including the custom `-32xxx` range), tool annotations, the pass-through principle, and the 12 KB context budget. Do not proceed without reading it.

You MUST read `references/design-operations.md` BEFORE declaring a server production-ready. It teaches capability negotiation, the MUST/SHOULD/MAY security checklist, tool naming conventions, and the 8-point Claude-Optimal validation checklist. Do not proceed without reading it.

You MUST read `references/design-consumption.md` BEFORE telling a user their server is ready to ship. It teaches the four installation paths, the JSON-RPC discovery flow Claude Code runs, the producer→consumer decision table, the verification commands (`claude mcp list` / `claude mcp get` / MCP Inspector), and the consumer-side symptom-cause-fix table. Do not proceed without reading it.

---

# Mode: SCHEMA

JSON Schema for MCP tools — schemas-as-LLM-instruction-manuals, the MCP defaults (`additionalProperties: false`, `required`, `$schema`), constraint discipline (`enum`, `pattern`, `range`, `format`, `length`), `oneOf`-vs-discriminator-enum, required-vs-optional principle, description writing, property naming, nesting rules, the pitfalls catalog.

You MUST read `references/schema-foundation.md` BEFORE writing any tool schema. It teaches the schemas-as-instruction-manuals principle, the three failure modes it defends against, the MCP defaults, the constraint discipline, the oneOf-vs-discriminator-enum decision (95% discriminator enum wins), the required-vs-optional principle, and the description-writing patterns. Do not proceed without reading it.

You MUST read `references/schema-styling.md` BEFORE finalizing property names or tool names. It teaches the snake_case-vs-camelCase decision, full words over abbreviations, the 2-level nesting rule, defaults that help, the verb_noun tool naming pattern, and the 5+ tool prefix convention. Do not proceed without reading it.

You MUST read `references/schema-pitfalls.md` BEFORE declaring a schema ready to ship. It teaches the `outputSchema` shape for typed clients and the 14-row pitfalls catalog (additionalProperties:true, no required, vague descriptions, deeply nested objects, free-form strings, oneOf abuse, mixed naming, missing enums, oversized maxLength, boolean form, missing $schema, format-alone, inconsistent id/Id). Do not proceed without reading it.

If you are writing Rust types for tool input/output, also read `references/implement-rmcp-api.md` Appendix A (the schemars → JSON Schema attribute mapping).

---

# Mode: IMPLEMENT

Rust implementation with rmcp 0.3 + schemars — Cargo.toml setup, the `#[tool]` / `#[tool_handler]` / `#[tool_router]` macro cheat sheet, the server lifecycle (initialize → capabilities → shutdown), transport choice (stdio vs Streamable HTTP), stderr-only logging, error mapping via `rmcp::ErrorData`, output construction, and testing with the MCP Inspector in CLI mode.

**Pre-condition:** If you have not yet decomposed your tools, read `references/design-decomposition.md` FIRST. Bad decomposition is the most common reason implementers ship a server the model can't use.

You MUST read `references/implement-rmcp-api.md` BEFORE writing the `Cargo.toml`, the server struct, or any `#[tool]`-annotated methods. It teaches the rmcp 0.3 feature flags, the macro cheat sheet, the schemars→JSON Schema attribute mapping table, the enum/rename idioms, the optional-field serialization hygiene, and the state management rules. Do not proceed without reading it.

You MUST read `references/implement-transport.md` BEFORE choosing a transport or wiring up initialization. It teaches the MCP server lifecycle, the stdio vs Streamable HTTP vs HTTP+SSE trade-offs, the decision matrix, and the `notify_tool_list_changed` pattern for dynamic tool sets. Do not proceed without reading it.

You MUST read `references/implement-runtime.md` BEFORE writing any tool that logs, surfaces errors, or returns structured output. It teaches the stderr-only logging rule, the `rmcp::ErrorData` constructors and the error-code → category mapping, the output construction idioms, and the long-output truncation pattern. Do not proceed without reading it.

You MUST read `references/implement-testing.md` BEFORE shipping the server. It teaches the test pyramid (unit / integration with MCP Inspector `--cli` / end-to-end / schema validation), the release build optimization, and the cross-compilation matrix. Do not proceed without reading it.

---

# Mode: CLIENT

Agent as MCP consumer — the four installation paths (plugin `.mcp.json` / user `~/.claude.json` / project `.mcp.json` / Desktop import), the JSON-RPC discovery flow, the `tools/call` calling pattern from an agent context, consumer-side debugging, cross-server tool disambiguation, and (for Rust agents) the rmcp client SDK for spawning a server subprocess or connecting to a remote Streamable HTTP server.

You MUST read `references/client-usage.md` BEFORE calling a remote MCP server from an agent. It teaches the agent-as-consumer framing, the discovery flow, the calling pattern, consumer-side debugging, session continuity, and cross-server disambiguation. Do not proceed without reading it.

You MUST read `references/client-rmcp-client.md` BEFORE building an MCP client with the rmcp SDK. It teaches the `rmcp::client` feature flag, the `ClientHandler` trait, stdio and Streamable HTTP client wiring, and `CallToolResult` handling. Do not proceed without reading it.

---

# Mode: QUALITY

Quality evaluation of an existing MCP server via the 8-dimension Claude-Optimal rubric. Server must already be implemented (IMPLEMENT mode) before evaluation.

You MUST read `references/quality-rubric.md` BEFORE running any evaluation. It teaches the 8-dimension rubric, the FAIL/PARTIAL/PASS/EXEMPLARY scoring scale, the pass threshold, and the per-dimension evidence requirements. Do not proceed without reading it.

You MUST read `references/quality-judge-pattern.md` BEFORE spawning judges. It teaches the parallel-judge pattern (8 judges, one per dimension), the judge contract (JSON output with score/evidence/recommendation), the tiebreak rule (>1-tier disagreement triggers a tiebreak judge), the pass threshold (any FAIL = overall FAIL; >2 PARTIALs = overall FAIL), and the report format. Do not proceed without reading it.

## Orchestration

Spawn the 8-dimension evaluation as an isolated forked subagent. The forked subagent:

1. **Establishes server artifacts** — source, compiled binary, .mcp.json entry, README
2. **Spawns exactly 8 a subagent generalist subagents in parallel**, one per dimension, each writing its JSON result to a dedicated temp file
3. **Reads all 8 JSON results**, applies the pass threshold and tiebreak logic
4. **Synthesizes a markdown report** with per-dimension scores, evidence, and overall PASS/FAIL verdict

The forked subagent's output is the complete markdown evaluation report. When the report returns, route PARTIALs and FAILs to IMPLEMENT mode (code fixes) or SCHEMA mode (schema fixes).

---

## Output

DESIGN: Tool decomposition plan, output contract, error code map, security checklist, naming plan
SCHEMA: JSON Schema for one or more tools (or a refactor plan for an existing one)
IMPLEMENT: Working Rust MCP server (rmcp 0.3 + schemars), with the test pyramid green
CLIENT: Agent-side MCP client integration (config + discovery + calling pattern)
QUALITY: Judge evaluation report with per-dimension scores, evidence, and recommendations

---

## Gotchas

- Do NOT design tools that overlap in function — if a human can't decide which tool to use, neither can the model.
- Do NOT write a tool schema without testing it against Claude first. Schema that parses correctly may still confuse the model.
- Do NOT forget `additionalProperties: false` on all tool input schemas — it's the single most common MCP quality failure.
- Do NOT mix transport concerns (stdio vs Streamable HTTP) into tool design. Design tools transport-agnostic.
- MUST run the 8-dimension quality rubric on every MCP server before declaring it production-ready.

## §CONTRAST

**DO NOT use this skill for:**

- "Drive the `claude` CLI from Bash" → use `claude-cli`
- "Spawn in-process subagents within a session" → use orchestrating-subagents
- "Build a non-MCP CLI tool" → use orchestrating-subagents or shell tooling
- "Investigate a runtime bug or root cause" → use superpowers' `systematic-debugging`
- "Design a non-MCP JSON Schema (OpenAPI, function calling, raw JSON Schema)" → use the target system's docs (most patterns transfer, but MCP-specific guidance lives here)
- "Implement an MCP server in Python, TypeScript, or Go" → use the SDK-specific docs (this hub covers Rust + rmcp only)

**CONTRAST with `claude-cli`:** `claude-cli` drives the `claude` binary as a tool from Bash; `engineering-mcp` builds and uses MCP servers. The boundary is the same: anything that touches MCP server design/schema/implementation/usage lives here, anything that drives the `claude` CLI itself lives in `claude-cli`.

**CONTRAST with generic parallel-judge patterns:** QUALITY mode applies a parallel-judge pattern specialized for MCP servers (one judge per dimension of the Claude-Optimal rubric).

**Within the hub:**
- CLIENT mode is for consuming MCP servers as an agent; it does NOT cover building a server (use IMPLEMENT mode).
- QUALITY mode evaluates existing servers; it does NOT fix problems — dispatch to IMPLEMENT or SCHEMA mode after diagnosis.
