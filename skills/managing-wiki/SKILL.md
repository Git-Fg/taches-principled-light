---
name: managing-wiki
description: >
  Load when searching, querying, ingesting, or verifying a personal wiki,
  knowledge base, or notes system. Use when the user mentions 'wiki', 'KB',
  'knowledge base', 'look up in my notes', 'lint wiki', 'add to wiki', or
  'build wiki'. Do NOT use for looking up information on the public web (use
  web-search) or researching an unfamiliar library/API (use a subagent
  explorer).
when_to_use: |
  - "Find something in my wiki / KB / notes"
  - "Search the wiki for X"
  - "Lint / verify / check consistency of the wiki"
  - "Add to the wiki / ingest into the wiki / populate the wiki"
  - "Build the wiki from a URL / file / notes"
  - NOT for: general web search (use web-search), code search, reading project documentation outside the wiki, real-time meeting notes
argument-hint: "[query|ingest|lint] [args...]"
---

# Wiki Hub — Routing and Operations

Build, query, and maintain a persistent, compounding knowledge base as interlinked markdown files.
Based on [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

## Teaching: Always Tell Subagents Which Wiki to Target

**The rule:** This skill is a hub. The hub spawns one specialist subagent for read-only queries (a subagent explorer) and performs ingest/lint operations inline against the resolved wiki path. **The hub's job is to resolve the target wiki BEFORE spawning or writing, and pass it as the working directory.**

**Why this rule exists:** A subagent that doesn't know the target wiki has to re-resolve it from the registry. That re-resolution can disagree with what the user meant (the user said "the work wiki" but the subagent picked "main" because the alias was ambiguous). When the hub does the resolution, the user can correct it once at dispatch time, and every subsequent call inherits the same answer.

**How to follow the rule:**

1. **Resolve the target wiki first** — read `~/.claude/wiki-root.md` (the registry) and apply the disambiguation rules from `references/registry-schema.md` to get the absolute path. If the user named a wiki, match by alias. If the user said "all my wikis", resolve all of them.
2. **For QUERY**: spawn a subagent explorer with `wiki_path` (preferred) or `alias` (fallback). Never spawn without one of them.
3. **For INGEST / LINT**: perform the operation inline in the resolved `wiki_path`. The registry-resolved path is your working directory.
4. **For multi-wiki operations** ("lint all my wikis", "ingest this into every wiki"): loop over the resolved wikis, repeating the operation in each.

**Argument contract (still applies when spawning a subagent explorer):**

| Subagent | Required | Optional |
|---|---|---|
| a subagent explorer | `query` (string), `wiki_path` (string) — OR `alias` (string) | `multi_wiki` (bool, default false) — set to `true` to run across all configured wikis |

a subagent explorer falls back to self-discovery from `~/.claude/wiki-root.md` if neither `wiki_path` nor `alias` is provided, following the disambiguation rules in `references/registry-schema.md`. If exactly one wiki is configured, it uses it; if ambiguous, it returns an error to the hub so the hub can ask the user to disambiguate.

## Wiki Root Resolution (multi-wiki registry)

The registry at `~/.claude/wiki-root.md` is the single source of truth for which wikis exist, what they contain, and what to read inside each one before doing anything else. As the hub, your first job in any wiki operation is to read that registry, pick the right wiki for the user's request, and pass the resolved `wiki_path` to whichever subagent you spawn next.

You MUST read `references/registry-schema.md` BEFORE any wiki operation. Do not proceed without reading it. It teaches the TOML schema, per-field semantics, the parsing algorithm, the disambiguation rules for picking the right wiki when several are configured, the no-registry first-time setup flow, the confirmation-before-mutating policy, and the front-load convention for descriptions. None of those mechanics live in this file anymore — they live in the reference, and the reference is the only place to consult them.

You MUST read `references/subagent-arguments.md` BEFORE spawning any subagent. Do not proceed without reading it. It defines the argument contract (what `wiki_path`, `alias`, `multi_wiki` mean, what the self-discovery fallback does), the registry preamble every subagent inherits, and the confirmation-before-mutating policy the hub must enforce before spawning a writing subagent. The three wiki agents inherit this contract transitively via their `skills: [wiki]` frontmatter — do not re-explain it in the spawn directive, and do not paste it into a spawn prompt.

Any subagent that intends to use `qmd` (Quick Markdown Search by Tobi Lütke, v2.5.3) for vector or keyword search MUST read `references/qmd-integration.md` BEFORE running any qmd command. It documents the collection-per-wiki contract, the full qmd command table (search/vsearch/query/embed/etc.), the two-flag rule (`-c <alias>` + `--json`), known critical bugs (CJK BM25 zero hits, ghost document Issue #585, path staleness), BM25 internals, default embedding models, and the MCP vs Bash tradeoff guidance. Subagents that do not use qmd can ignore this reference — it is strictly additive to the core wiki contract.

## Decision Router

Classify the user's intent. QUERY spawns a subagent explorer; INGEST and LINT run inline. When in doubt, ask the user to disambiguate ("Do you want to search the wiki, or add something to it?").

| User intent (signal words) | Action | Pass to the action |
|---|---|---|
| **Query / Search**: "find", "look up", "search", "what does my wiki say about", "do I have notes on" | Spawn a subagent explorer (read-only) | `query` (string) + `wiki_path` (string) or `alias` (string) — see Argument Contract below |
| **Ingest / Build / Add**: "add to wiki", "ingest", "save to wiki", "import", "file this into wiki", "populate wiki", "build wiki from <source>" | Perform ingest inline against the resolved `wiki_path` | n/a — operates on `$WIKI_ROOT` directly |
| **Lint / Verify**: "lint", "check consistency", "verify", "find broken links", "reconcile", "audit" | Perform lint inline against the resolved `wiki_path` (or spawn spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." for an isolated-context audit) | n/a |

### Argument Contract (steering the orchestrator)

**The hub (you) is the orchestrator. Always pass `wiki_path` when spawning a subagent explorer. Always.**

- `wiki_path` is the absolute path the subagent should operate on. **Resolve it before spawning** — read `~/.claude/wiki-root.md` and apply the disambiguation rules from `references/registry-schema.md` to get the path.
- If you don't know the path but know the alias, pass `alias` instead. The subagent will resolve it from the registry.
- **Never spawn a subagent explorer without one of `wiki_path` or `alias`.** It can technically self-discover from the registry as a last resort, but the contract is: the hub has already done the resolution work, the subagent just executes.
- For multi-wiki operations ("all my wikis"): spawn a subagent explorer once per wiki, passing each resolved `wiki_path` in turn. The subagent reports per-wiki results.

**The subagent will refuse to start if neither `wiki_path` nor `alias` is provided** and the registry is empty/unreadable. Treat that as a setup error and surface the no-registry message to the user.

**Dispatch notes:**
- a subagent explorer is the only subagent that ships with this skill — it does no writes, so the read-only contract is load-bearing (it's the allowed `tools:` exception).
- INGEST and LINT operate inline against the resolved `wiki_path`. The orchestrator reads `$WIKI_ROOT/SCHEMA.md`, `index.md`, and `log.md` (per the orientation rules below) before writing. For LINT, you may also spawn spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." for an isolated-context consistency audit when the wiki is large enough that an inline walk would flood your context.
- If the user's intent is ambiguous between `ingest` and `lint` (e.g., "fix my wiki"), default to `lint` (read-only path) and let the user escalate to `ingest` if needed.
- For multi-source bulk ingest, prefer `bulk` mode — it does one search pass instead of N.
- **Multi-wiki operation:** if the user says "lint all my wikis" or "ingest this into all my wikis", loop over the resolved wikis and repeat the operation in each.

## Reference Index

This hub skill ships with one specialist subagent (read-only) and performs INGEST / LINT inline.

- **subagent explorer** (read-only tools `[Read, Glob, Grep]`) — `QUERY` mode. Retrieves and synthesizes information from the user's wiki. Cites source pages. Never writes. This is the single allowed `tools:` restriction in the marketplace — read-only enforcement is the point (the wiki's mutation paths run inline in the hub, not through a subagent).

INGEST runs inline in the hub: read `$WIKI_ROOT/SCHEMA.md` → fetch the source → cross-reference existing pages → write new pages with 2+ outbound wikilinks → update `index.md` and `log.md`. LINT runs inline or via spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." for an isolated-context consistency audit; either path reads `SCHEMA.md` + `index.md` + (optional) `.wiki/intent.md` → runs the wiki's lint checks → groups findings by severity → auto-fixes safe items.

## Mandatory Orientation — Every Wiki Operation

**Before touching the wiki, always orient yourself first.** This applies to all three subagents before they read or write anything.

1. **Read `$WIKI_ROOT/SCHEMA.md`** — domain, conventions, tag taxonomy, page thresholds
2. **Read `$WIKI_ROOT/index.md`** — what pages already exist (prevents duplicates)
3. **Scan `$WIKI_ROOT/log.md`** (last 20-30 lines) — what's been done recently

(These three files live in the user's wiki at `$WIKI_ROOT/`, not in this plugin. They are the wiki's own configuration and state, not the plugin's.)

## Cross-plugin dependencies

This skill is part of the `taches-principled-light` plugin and depends on **optional** MCP tools. The skill works without them, falling back to the noted substitute.

| MCP tool | Used in | Fallback if absent |
|---|---|---|
| `mcp__mcp-searxng__fetch` | INGEST mode `url` (fetch the web page) | `WebFetch` (Claude Code's built-in) — slower but always available |
| `mcp__mcp-searxng__extract` | INGEST mode `url` (RAG-ranked chunks for better summarization) | Fetch full page and post-process locally |
| `web_extract` (alias) | Same as `mcp__mcp-searxng__extract` | Same as above |

**Why these aren't hard dependencies:** `taches-principled-light` ships standalone — a user who only wants wiki management should be able to install just this plugin. The MCP tools are accelerators (faster, RAG-ranked), not requirements. The fallback path uses Claude Code's built-in `WebFetch`.

**No marketplace-plugin dependencies.** This plugin does not import any other `tp-*` plugin. It is self-contained.

## qmd Cron Health Check (optional, recommended)

Any wiki that uses `qmd` for vector or BM25 search should be monitored
periodically with `qmd status` to catch index drift, collection
removal, or broken embeddings before they degrade retrieval quality.

**Recommended cron expression (local time):**
```bash
57 9 * * 1-5 qmd status >> ~/.cache/qmd/health.log 2>&1
```

**Alert conditions — grep the log after each run:**
- `Unknown command` → qmd binary broken or wrong version
- `error` (anywhere in the line) → qmd itself is failing
- A collection missing from the list → it was accidentally removed
- File count changed >10% since the last known-good run → ghost
  documents or bulk add/remove

**What each signal means and how to fix it:**

| Signal | Likely cause | Fix |
|---|---|---|
| Collection gone | `qmd collection remove` ran accidentally | Re-add: `qmd collection add <path> --name <alias> --mask "**/*.md"` then `qmd embed -c <alias>` |
| Files decreased | Ghost docs not cleaned, or missed new files | `qmd update -c <alias>` then re-check |
| Files increased | New wiki pages added | Normal; index will catch up |
| Vectors decreased | Embedding job interrupted | `qmd embed -c <alias>` |
| `Pending: N` shown | New/updated files waiting for vectors | `qmd embed -c <alias>` |

**Log rotation:** Keep last 30 entries. `tail -30 ~/.cache/qmd/health.log`
covers ~6 weeks of daily runs. Any trend in file counts is a drift signal.
For the full qmd integration reference (commands, two-flag rule, known bugs),
read `references/qmd-integration.md`.

## Anti-patterns

❌ **Modifying `raw/` files after they are written.** Sources are immutable. The ingester writes them once with `source_url` / `source_path` / `ingested` frontmatter and never re-touches them. Re-fetching for a new ingest is a separate event with a new `ingested` date.

❌ **Creating a page from a single mention.** Page threshold is 2+ sources OR central to one source. A single mention in passing doesn't earn its own page — it goes in a more general page or stays as a wikilink target stub.

❌ **Adding a new tag without updating `SCHEMA.md` first.** Tag sprawl is the wiki's version of type-system rot. New tag → add to `SCHEMA.md` taxonomy → THEN use it.

❌ **Skipping the orientation step.** Reading `SCHEMA.md` / `index.md` / `log.md` first is not optional. Skipping it is how you end up with duplicate pages, conflicting tag taxonomies, and rewrite loops in `log.md`.

❌ **Returning a "no results found" without checking the wiki root.** The wiki may not be configured. Resolve the root first; if unresolved, ask the user for the path. Don't return empty from a misconfigured wiki root — that's a setup bug, not a search miss.

❌ **Ingesting into the wiki while another ingester is running.** `bulk` mode assumes a single writer. Concurrent ingests will produce duplicate pages, conflicting `index.md` updates, and torn `log.md` entries. The hub should serialize ingest operations.

❌ **Linting then auto-fixing in one shot.** LINT should report findings first; the user should approve the auto-fix policy (e.g., "yes, auto-fix orphan detection and missing frontmatter, but flag broken wikilinks for me"). Don't conflate the two phases.

## CONTRAST

- NOT for: general web search, code search, or reading project documentation outside the wiki
- NOT for: replacing a database, CRM, or structured data store
- NOT for: real-time note-taking during a meeting (use a dedicated notes tool)
- NOT a static site generator — the wiki is agent-maintained, not published

## Detailed Methodology

For full operational guidance (ingest, query, lint, archiving, Obsidian sync, pitfalls),
read `$WIKI_ROOT/concepts/llm-wiki-methodology.md`. The wiki format itself is documented in
`$WIKI_ROOT/SCHEMA.md`. The intent file format (`.wiki/intent.md`) is in
`$WIKI_ROOT/concepts/intent-format.md`.
