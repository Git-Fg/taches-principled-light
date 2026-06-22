---
name: claude-cli
description: >
  Load when driving Claude Code CLI programmatically — headless sessions,
  structured JSON output, model/permission control, cloud code reviews, or
  session continuation. Use when the user says 'spawn a headless Claude
  session', 'run a cloud code review', 'continue a Claude session', or 'change
  the model or permission mode'. Do NOT use for interactive Claude use or
  non-CLI Claude features.
when_to_use: |
  - "Spawn a headless Claude session to run a task"
  - "Continue or resume a previous Claude Code session"
  - "Get structured JSON output from Claude"
  - "Run a cloud-hosted code review"
  - "Change the model, effort, or permission mode for a Claude invocation"
  - "Drive Claude Code programmatically from a Bash command"
license: MIT
---

# claude-cli

The `claude` CLI is the same binary that powers interactive Claude Code. With `-p` (print) it runs headlessly, accepts a prompt, and writes the response to stdout. This skill is a hub: it routes you to per-operation references rather than inlining every flag. The six conceptual operations (execute, session, context, review, agent, config) are now native CLI flags rather than wrapper-tool calls.

For MCP design/implementation/schema patterns (i.e., *building* MCP servers, not *using* the `claude` CLI), see the marketplace's engineering-mcp skill (modes: DESIGN, SCHEMA, IMPLEMENT, CLIENT, QUALITY).

---

## §1. When this skill fires

**Use this skill when the request is to drive the `claude` CLI from a Bash invocation:**

- "Run Claude on this prompt headlessly"
- "Spawn a headless Claude session to do X"
- "Continue the Claude session from earlier"
- "Get Claude to return JSON in this schema"
- "Run a code review on this branch"
- "Change the model to opus for this invocation"
- "Drive Claude Code programmatically"

**DO NOT use this skill for:**
- "How do I design an MCP server" → the marketplace's MCP expertise skill, DESIGN mode
- "How do I implement an MCP server in Rust" → the marketplace's MCP expertise skill, IMPLEMENT mode
- "How do I write a good JSON Schema" → the marketplace's MCP expertise skill, SCHEMA mode
- "How do I run a shell command from the host environment" → your host platform's shell docs
- "How do I run Claude Code interactively" → Claude Code's built-in docs (not headless)

## CONTRAST

- NOT for: spawning in-process subagents within the current Claude Code session — use orchestrating-subagents
- NOT for: designing an MCP server from scratch — use engineering-mcp DESIGN mode
- NOT for: writing a single Claude Code hook — see the official hooks docs
- NOT for: managing installed plugins/MCP servers — use `claude plugin list` / `claude mcp list` directly in Bash

---

## §2. The 6 conceptual operations

The marketplace historically exposed the `claude` CLI as six MCP tools. The wrapper is gone, but the conceptual decomposition is still useful as a mental model. Here's the mapping to native CLI flags:

| Operation | Old MCP tool | Native CLI pattern |
|---|---|---|
| **execute** | `claude_execute` | `claude -p "..." --output-format json` |
| **session** | `claude_session` | `claude --resume <uuid>` or `claude --continue` or `claude --session-id <uuid>` |
| **context** | `claude_context` | `claude --add-dir <path>` or `claude --worktree [name]` or `claude doctor` |
| **review** | `claude_review` | `claude ultrareview [target] --json` |
| **agent** | `claude_agent` | `claude --agent <name> -p "..."` and `claude agents --json` |
| **config** | `claude_config` | per-invocation flags: `--model`, `--effort`, `--permission-mode`, `--settings` |

---

## §3. Reference router

This skill is a hub. The six operations, plus two cross-cutting topics, live in per-operation references. You MUST read the matching reference BEFORE writing the corresponding CLI invocation. Do not inline flag knowledge from the hub — the references are authoritative.

| If you are… | You MUST read this reference BEFORE proceeding |
|---|---|
| Running a headless prompt with flags | `references/execute.md` |
| Resuming or managing a session lifecycle | `references/session.md` |
| Telling Claude about directories or worktrees | `references/context.md` |
| Running a cloud-hosted code review | `references/review.md` |
| Spawning or managing background agents | `references/agent.md` |
| Tuning model, effort, permission mode, settings | `references/config.md` |
| Parsing CLI output (text/json/stream-json/exit codes) | `references/output-contract.md` |
| Composing an end-to-end workflow | `references/workflows.md` |

Each reference is self-contained for its operation. References MUST NOT cross-cite each other — return to this hub for routing.

---

## §4. Anti-patterns

❌ **Looping `claude -p` 50 times for 50 small tasks** — use `--continue` to maintain context, or batch related tasks into a single prompt. Each `-p` invocation is a fresh model call; the session_id is the only state that persists.

❌ **Forgetting `--permission-mode acceptEdits`** — Claude will refuse to edit files (or ask the user, who isn't there). The call appears to hang. Always set the permission mode for agent-driven invocations.

❌ **Using `--dangerously-skip-permissions` in shared environments** — this bypasses all safety checks. Only use in sandboxes with no internet access.

❌ **Using `--output-format text` when you need to parse the result** — use `json` and parse with `jq`. Don't try to regex-match plain text.

❌ **Putting a JSON Schema as a nested object** — `--json-schema` takes a STRING. The CLI passes it to the model verbatim.

❌ **Setting `--disallowed-tools "Read,Edit"`** — these are core tools; you're effectively turning Claude into a chat-only instance.

❌ **Using `--bare` in production** — you lose hooks, LSP, plugin sync, attribution, auto-memory, keychain reads, and CLAUDE.md auto-discovery. Only use for clean test environments.

❌ **Hardcoding a full model name like `claude-opus-4-8`** — prefer aliases (`sonnet`, `opus`, `haiku`) so the call tracks the latest model. Hardcoded names break when models are deprecated.

❌ **Resuming a session without verifying the UUID format** — invalid UUIDs cause the CLI to error. Validate with a regex check or use `--continue` (no UUID needed).

❌ **Forgetting `--add-dir` when Claude needs to read files outside the cwd** — without it, Claude is sandboxed to the current working directory and will fail to read external files.

---

## §5. Handoff

- **MCP design principles** (why some tools decompose the way they do) → the marketplace's engineering-mcp skill, DESIGN mode
- **MCP implementation in Rust with rmcp + schemars** → the marketplace's engineering-mcp skill, IMPLEMENT mode
- **JSON Schema authoring details** → the marketplace's engineering-mcp skill, SCHEMA mode
- **Subagent orchestration patterns** (parallel dispatch, scratchpad, critic loops) → the marketplace's orchestrating-subagents skill
- **Session analytics and behavioral review** → the marketplace's analyzing-sessions skill

---

## §6. Key sources

- [1] Claude Code CLI documentation — https://docs.claude.com/en/docs/claude-code
- [2] Decomposition patterns (why 6 tools vs 1) — the engineering-mcp skill's design-decomposition.md reference (DESIGN mode)
- [3] Structured output with `--json-schema` — official Claude Code docs on JSON Schema validation
