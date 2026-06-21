# qmd Integration — Search Engine Contract and Known Limitations

This file documents how `qmd` (Quick Markdown Search, by Tobi Lütke, v2.5.3)
integrates with the tp-wiki system. While tp-wiki's hub subagents do not
require qmd to function, any subagent that *chooses* to use qmd for
retrieval MUST read this file first to understand the contract, the
scoping rules, and the critical bugs that affect search correctness.

The standalone wiki skill (`~/agents/skills/wiki/SKILL.md`) enforces the
full qmd integration contract directly. This reference exists so tp-wiki
subagents have a discoverable, single-file source of truth for the same
information — without repeating the standalone skill's mode-by-mode
integration.

---

## Collection-per-Wiki Contract

Every wiki registered in `~/.claude/wiki-root.md` is mirrored as a qmd
collection. The scout names wikis by alias (`[pharma]`, `[mevin]`,
`[mywiki]`); qmd scopes searches by the same alias. They are the same
namespace.

```
~/.claude/wiki-root.md                    ~/.cache/qmd/index.sqlite
  [pharma]  → path="..."      ←→           qmd collection: pharma
  [mevin]   → path="..."      ←→           qmd collection: mevin
  [mywiki]  → path="..."      ←→           qmd collection: mywiki
```

**Deriving the collection alias for qmd commands:**

The alias used by qmd is determined by reading the shared file:

1. **Read the wiki's table** from `~/.claude/wiki-root.md`.
2. **Check for `qmd_slug` field** — if present, that is the collection alias for all qmd `-c` flags.
3. **Otherwise**, the table key (the `[<alias>]` header) is the collection alias.
4. The alias MUST match the qmd collection name exactly (case-sensitive).

This means: if a table has `[pharma-dfasp1]` with `qmd_slug = "pharma"`,
the collection is `pharma` — **not** `pharma-dfasp1`. The `qmd_slug`
field lets users rename TOML table keys without breaking the qmd index.

### The two-flag rule for every qmd invocation

1. **`-c <alias>`** — Scope every search to one collection. A naked
   `qmd search "..."` searches every collection, which is only correct
   for multi-wiki operations.
2. **`--json`** — Always request structured output. Parse JSON rather
   than re-parsing human-formatted prose.

### Health check first

Before running any qmd command, run `qmd status` first. If it errors,
fall back to `Grep` + `Read` — do not proceed with qmd.

### Cron health check — `qmd status` as periodic monitor

Run `qmd status` periodically (e.g., via `cron`) to catch index drift,
model corruption, or collection removal before they affect retrieval
quality.

**What to look for:**

| Signal | Likely cause | Fix |
|---|---|---|
| Collection gone from list | `qmd collection remove` accidentally ran | `qmd collection add <path> --name <alias> --mask "**/*.md"` then `qmd embed -c <alias>` |
| Files count decreased (vs. last known good) | Ghost documents not cleaned, or `qmd update` missed new files | `qmd update -c <alias>` then re-check |
| Files count increased unexpectedly | New wiki pages added | No action needed; index is fresh |
| Vectors count decreased | Embedding job interrupted | `qmd embed -c <alias>` to regenerate |
| `Pending: N need embedding` shown | New/updated files waiting for vectors | `qmd embed -c <alias>` to flush pending |

**Recommended cron expression (local time):**

```bash
# Run health check every weekday at ~9:17 AM (slightly after 9 to avoid herd)
57 9 * * 1-5 qmd status >> ~/.cache/qmd/health.log 2>&1
```

**What the cron job captures** (`~/.cache/qmd/health.log`):

```
QMD Status — 2026-06-14
Collections:
  pharma: 335 files, vectors 11372, updated 27m ago
  mywiki: 1367 files, vectors 11372, updated 3m ago
  mevin:  89 files,  vectors 11372, updated 2h ago
```

**Alert conditions** (grep the log for these patterns after each run):

- `Unknown command` — qmd binary is broken or wrong version
- `error` (case-insensitive) in any line
- A collection missing from the list entirely
- File count changed by >10% vs. the previous run (drift or bulk add/remove)

**Log rotation:** Keep the last 30 entries. A simple `tail -30` comparison
catches slow drift across weeks.

**Jitter:** qmd has no built-in per-collection update schedule. Use
host-level jitter (e.g., `KIMI_CRON_NO_JITTER=0` in the cron env) if you
schedule collection-specific `qmd update` calls — the global `qmd update`
without `-c` updates all collections at once.

---

## Commands Available

| Command | Purpose |
|---|---|
| `qmd search -c <alias> "<q>" --json` | BM25 keyword search, instant, no LLM. Default for lookups. |
| `qmd vsearch -c <alias> "<q>" --json` | Vector semantic similarity. Requires `qmd embed` to have been run. |
| `qmd query -c <alias> "<q>" --json` | Hybrid with LLM expansion + reranking. Slowest. Reserve for explicit high-quality requests. |
| `qmd get <file>[:from[:count]]` | Show a document (line-numbered). |
| `qmd multi-get "<pattern>"` | Batch fetch via glob or comma-list. |
| `qmd update -c <alias>` | Re-index the collection (scan filesystem, diff vs SQLite). |
| `qmd update --pull -c <alias>` | `git pull` then re-index. Git-tracked wikis. |
| `qmd embed -c <alias>` | Generate / refresh vector embeddings. |
| `qmd collection add <path> --name <alias> --mask "**/*.md"` | Register a new collection. |
| `qmd collection rename <old> <new>` | Rename a collection (preserves all vectors + contexts). Preferred over remove+add. |
| `qmd collection remove <name>` | Remove a collection from the index (preserves files). |
| `qmd collection list` | List all registered collections. |
| `qmd context add qmd://<alias> "<description>"` | Attach a human-written context summary (uses wiki's `description` from shared file). |
| `qmd ls <alias>` | List indexed files in a collection. |
| `qmd status` | View index + collection health. |

---

## Critical Bugs and Limitations

### 1. CJK BM25 zero hits (built-in limitation)

qmd's default BM25 tokenizer is `porter unicode61` — a Porter-stemmer
English-only tokenizer that strips stop-words and applies English
morphology reduction. CJK/Asian text (Chinese, Japanese, Korean)
receives **zero BM25 hits** because the tokenizer cannot segment
multi-byte characters into queryable terms.

- `vsearch` (vector) and `query` (hybrid) still work because they
  operate on embeddings, not tokenized text.
- **Fallback for CJK content:** use `qmd vsearch -c <alias> "..."
  --json` instead of `qmd search`.
- The CJK limitation applies only to BM25; semantic search is unaffected.

### 2. Ghost document bug (Issue #585, CRITICAL)

`qmd update -c <alias>` scans the filesystem for new and changed files
but **never marks removed files as inactive** in the SQLite index. A
file that is deleted or renamed persists in the index as a "ghost
document." In observed installations, ~92% of the indexed documents
were ghosts after repeated delete + add cycles.

**Root cause:** The update path lacks a filesystem-to-DB diff
reconciliation step — it inserts/updates entries but never deletes.
Combined with content-hash identity (a file's docid is the first 6
hex chars of its content hash, not its path), renaming or moving a
file stores it under a new hash, while the old hash remains as a ghost.

**Workaround:** After any file deletion or rename within a collection,
fully re-create the collection:

```bash
qmd collection remove <alias>
qmd collection add <path> --name <alias> --mask "**/*.md"
qmd update -c <alias>
```

> **Collection-level rename is different.** If you only need to rename
> the collection itself (e.g. the wiki's alias changed), use `qmd
> collection rename <old> <new>` instead — it preserves all vectors,
> contexts, and document IDs without a full rebuild.

If `qmd collection remove` is unavailable (should not happen in
v2.5.3+), delete the SQLite index at `~/.cache/qmd/index.sqlite`
and re-register all collections from scratch.

### 3. Path moves are silently stale

A collection's path is stored verbatim in `~/.config/qmd/collections`.
If the wiki directory moves on disk, `qmd update` still runs
successfully but scans **zero files** — no error, no warning. `qmd
status` shows the collection as healthy. Always verify the resolved
path after a filesystem move: `qmd collection list` shows the stored
path; compare it against the wiki's `path` in the shared file.

### 4. `qmd embed -c <name>` was broken before v2.5.0

The `-c` flag was silently ignored in prior versions — `qmd embed`
would embed every collection instead of the scoped one. If running
qmd < 2.5.0, the bootstrap step `qmd embed -c <alias>` embeds all
collections. Upgrade to v2.5.0+ to scope embeddings. Check version
with `qmd --version`.

---

## BM25 Internals (for troubleshooting)

qmd uses SQLite FTS5 with BM25 ranking:

| Parameter | Value |
|---|---|
| k1 | 1.2 |
| b | 0.75 |
| Column weight: filepath | 10.0 |
| Column weight: title | 5.0 |
| Column weight: body | 1.0 |
| Chunk size | ~900 tokens |
| Chunk overlap | 15% |
| Boundary score: H1 | 100 |
| Boundary score: H2 | 90 |
| Boundary score: H3 | 80 |
| Boundary score: body | 0 |
| Default results | 10 (overridable with `--limit N`) |

These parameters are hardcoded — there is no user-facing config for
BM25 tuning.

---

## Default Models

| Role | Model | Format | Size | Source |
|---|---|---|---|---|
| Embedding | EmbeddingGemma-300M-Q8_0 (Google) | GGUF | ~300 MB | HuggingFace |
| Reranker | Qwen3-Reranker-0.6B-Q8_0 | GGUF | ~640 MB | HuggingFace |
| Query expansion | tobil/qmd-query-expansion-1.7B-gguf | GGUF | ~1.7 GB | HuggingFace |

Models are downloaded to `~/.cache/qmd/models/` on first use. The
embedding model download is a one-time delay of ~30s.

---

## MCP vs Bash Tradeoff

Running qmd through `qmd mcp` (its stdio MCP server) costs 1.3×–80×
more tokens per invocation than the equivalent Bash call because each
MCP tool call carries JSON-RPC request/response schema overhead.

- **Use Bash** for 1–3 queries per session (the common case for query mode).
- **Use MCP** only for sustained retrieval workflows (>5 vector or hybrid
  queries per session) where the per-call savings from skipping shell
  startup outweigh the schema overhead.
