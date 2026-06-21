# Argument Contract and Registry Preamble — a subagent explorer and inline wiki ops

This file is the single source of truth for two things the wiki skill needs:

1. **The a subagent explorer argument contract** — what arguments the hub is expected to pass when spawning it, and what to do when the hub forgets.
2. **The registry preamble** — what the registry is, what `what_to_read` is for, and why walking it is non-negotiable before any wiki operation (read OR write).

INGEST and LINT operations run inline in the hub against the resolved `wiki_path` — they no longer spawn subagents. Their contract is the orientation tail below, applied by the hub itself.

The hub skill (`SKILL.md`) cites this file once. The a subagent explorer agent inherits the contract via the `wiki` skill frontmatter.

---

## Argument Contract for a subagent explorer

The hub spawns a subagent explorer. It is **expected to pass `wiki_path` (preferred) or `alias` (fallback) as an argument**, plus the role-specific `query`:

| Argument | Type | Purpose |
|---|---|---|
| `query` | string | The user's question — "find X", "what does my wiki say about Y", etc. |
| `wiki_path` | string (preferred) | Absolute path to the wiki to operate on. The hub resolves this from the registry before spawning. |
| `alias` | string (fallback) | The label from `~/.claude/wiki-root.md` (e.g., "pharma", "work", "personal"). If received instead of `wiki_path`, a subagent explorer resolves it from the registry. |
| `multi_wiki` | bool (default false) | If true, run the query against every configured wiki and report per-wiki results. |

### Self-discovery fallback (last resort)

If neither `wiki_path` nor `alias` is provided, a subagent explorer should still try to infer the target by reading `~/.claude/wiki-root.md` directly:

- If the registry is unambiguous (exactly one wiki), use it.
- If the registry is ambiguous (multiple wikis and no clear signal), return an error to the hub rather than guessing. The hub will then ask the user to disambiguate.

The hub's job is to do the resolution before spawning. Self-discovery is a fallback for the case where the hub skipped the resolution. Don't rely on it as the normal path.

### Confirmation before mutating

QUERY operations (read-only) skip confirmation — they cannot mutate state. INGEST and LINT operations (inline in the hub) MUST confirm the chosen wiki with the user before any write:

> "Operating on: `[<alias>]` at `<path>`. Proceed?"

The confirmation MUST happen after the disambiguation rules pick a wiki and BEFORE the first write.

---

## Registry Preamble (multi-wiki)

The hub resolves `wiki_path` from `~/.claude/wiki-root.md`, which holds one TOML table per registered wiki along with the `path`, `tags`, `what_to_read` pointers, and a natural-language description of each. The wiki skill teaches the registry schema in full, including the confirmation-before-mutating policy above.

Before you read or write anything inside the wiki, walk its `what_to_read` list in order — those files (typically `SCHEMA.md`, `index.md`, and optionally `log.md`) tell you the wiki's conventions, what pages already exist, and what's been done recently. Skipping that orientation is how duplicate pages, conflicting tag taxonomies, and rewrite loops end up in the wiki.

The `what_to_read` filenames are bare strings, relative to the wiki's `path`. The registry schema reference (`references/registry-schema.md`) defines the full field semantics.

---

## What the orchestrator does inline for INGEST and LINT

Since INGEST and LINT run inline in the hub (no subagent dispatch), the orchestrator applies the same orientation tail itself: read the wiki's `SCHEMA.md`, `index.md`, and `log.md` (per `what_to_read`), then perform the operation directly against the resolved `wiki_path`. The role-specific details — frontmatter schema, tag taxonomy, page-size budget, auto-fix policy — are applied by the orchestrator reading these conventions from `SCHEMA.md` directly.

For LINT, the orchestrator may also spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." for an isolated-context consistency audit when the wiki is large enough that an inline walk would flood the orchestrator's context.