# MCP Quality Rubric: The 8-Dimension Claude-Optimal Evaluation

Reference for the rubric that QUALITY mode uses to score an existing MCP server. The rubric is the same 8-point Claude-Optimal validation from DESIGN mode's `references/design-operations.md` §4, expanded with concrete evidence requirements and a 4-tier scoring scale. Read it before evaluating any MCP server.

## §1. The 8 dimensions

Each dimension is independently scored. A server passes QUALITY mode when **all 8 dimensions score PASS or EXEMPLARY** (no FAILs, no more than 2 PARTIALs).

### 1. Tool discovery

**What it measures:** Do the tools load cleanly in a host without schema errors?

**Evidence to gather:**
- `claude mcp list` shows the server as connected
- `claude mcp get <server>` lists all tools with no `Invalid input: expected "object"` errors
- MCP Inspector `--cli --method tools/list` returns the full tool list, no JSON-RPC errors

**Score:**
- **EXEMPLARY:** All tools load on first try, no warnings
- **PASS:** All tools load after one restart
- **PARTIAL:** Some tools load, others fail silently
- **FAIL:** Server handshake fails or no tools load

### 2. Single-shot argument accuracy

**What it measures:** Does the LLM fill the args correctly on the first attempt (no re-prompting)?

**Evidence to gather:**
- Run 10-20 representative test invocations via `claude -p` in `--output-format json` mode
- Count how many required a follow-up correction or produced a `-32602 Invalid params` error
- Target: ≥ 90% first-attempt success

**Score:**
- **EXEMPLARY:** 100% first-attempt accuracy across 20+ tests
- **PASS:** ≥ 90% first-attempt accuracy
- **PARTIAL:** 70-89% first-attempt accuracy
- **FAIL:** < 70% (the LLM can't reliably use this server)

### 3. Context efficiency

**What it measures:** How much of the model context does the tool surface consume?

**Evidence to gather:**
- Sum the serialized bytes of all tool definitions (name + description + inputSchema)
- Check: total < 12 KB? Per-tool < 2 KB?
- Compare to the 6-tool decomposition target in DESIGN mode (`references/design-decomposition.md` §2)

**Score:**
- **EXEMPLARY:** Total < 6 KB, no tool > 1 KB
- **PASS:** Total < 12 KB, no tool > 2 KB
- **PARTIAL:** Total 12-20 KB, or 1-2 tools > 2 KB
- **FAIL:** Total > 20 KB, or any tool > 4 KB (model will struggle to select)

### 4. Pass-through integrity

**What it measures:** Do complex blobs (JSON Schemas, settings) round-trip through the tool without mutation?

**Evidence to gather:**
- If the server passes through structured data (e.g., a JSON-encoded schema in a string arg), test that:
  - The server validates only syntax (JSON parseable), not semantics
  - The blob is returned verbatim in output when the tool is a no-op echo
  - Deep nesting (5+ levels) is preserved

**Score:**
- **EXEMPLARY:** All pass-throughs round-trip byte-for-byte
- **PASS:** Pass-throughs work for the common case
- **PARTIAL:** Some pass-throughs truncate or normalize
- **FAIL:** Server tries to validate semantics, breaks legitimate uses

### 5. Session continuity

**What it measures:** Do `session_id` (or analogous handle) round-trip cleanly across tools?

**Evidence to gather:**
- If the server has multi-step workflows (session create → continue → end), test:
  - The create tool returns a stable handle
  - Subsequent tools accept the handle and produce expected results
  - The handle is opaque (not a parsed structure the client has to understand)

**Score:**
- **EXEMPLARY:** Handle round-trips across 5+ tools without transformation
- **PASS:** Handle round-trips across 2+ tools
- **PARTIAL:** Handle works but requires client-side parsing
- **FAIL:** No handles; server relies on implicit per-connection state (violates the spec)

### 6. Headless reliability

**What it measures:** Does the server work when stdin is not a TTY?

**Evidence to gather:**
- Run the server with stdin redirected from /dev/null
- Confirm it doesn't hang waiting for interactive input
- Confirm MCP Inspector `--cli` mode works (the canonical headless test)
- Check for any "Press Enter to continue" or "type 'y' to confirm" prompts

**Score:**
- **EXEMPLARY:** Server runs cleanly in any non-TTY environment
- **PASS:** Server runs in `--cli` Inspector mode
- **PARTIAL:** Server has one or two prompts that need a flag to disable
- **FAIL:** Server hangs in non-TTY environments

### 7. Error distinction

**What it measures:** Are errors categorized correctly (schema vs domain vs internal)?

**Evidence to gather:**
- Trigger a schema violation (send invalid args) → should return `-32602`
- Trigger a domain error (e.g., file not found) → should return custom `-32xxx` with a clear `data` field
- Trigger a real internal bug (force a panic) → should return `-32603` (not `-32602`, not silent)

**Score:**
- **EXEMPLARY:** All three categories are cleanly distinguished
- **PASS:** Schema vs domain distinguished; internal errors at least return *some* error
- **PARTIAL:** All errors are `-32603` or all are `-32602` (categories collapsed)
- **FAIL:** Tool returns `Ok` with `is_error: true` for transport-level failures (or vice versa)

### 8. Schema hygiene

**What it measures:** Are the tool schemas clean and LLM-actionable?

**Evidence to gather:**
- Every object schema has `additionalProperties: false`?
- Every property has a `description`?
- Every required field is in `required`?
- `enum` is used for bounded choices, not free-form strings?
- `$schema` is explicit?

**Score:**
- **EXEMPLARY:** 100% compliance on all checks
- **PASS:** ≥ 90% compliance (1-2 minor misses)
- **PARTIAL:** 70-89% compliance
- **FAIL:** < 70% (LLM will hallucinate fields or skip required ones)

## §2. The 4-tier scoring scale

| Tier | Meaning | Pass/Fail status |
|---|---|---|
| **EXEMPLARY** | Best-practice implementation; serve as a reference for others | Pass |
| **PASS** | Meets the bar; ship it | Pass |
| **PARTIAL** | Works but has a documented gap; either fix it or document the constraint | Pass (with caveat) |
| **FAIL** | Below the bar; must fix before shipping | Fail |

**Pass threshold:** all 8 dimensions must score PASS or EXEMPLARY. **Up to 2 PARTIALs** are acceptable if accompanied by clear documentation of the limitation. **Any FAIL** blocks the server from being rated as Claude-Optimal.

## §3. How to surface findings

For each dimension, the judge records:
- **Score:** EXEMPLARY / PASS / PARTIAL / FAIL
- **Evidence:** the actual command run, the actual output observed, the file/line that caused the issue
- **Recommendation:** the concrete fix (or "ship it as-is" if EXEMPLARY)

Findings are reported in a markdown table (see `references/quality-judge-pattern.md` §5 for the format). FAILs go to the top of the report. EXEMPLARYs are noted in a summary section at the bottom.

## §4. Anti-patterns (evaluation side)

❌ **Scoring without evidence** — every PASS needs a concrete observation (a command run, a test case passed, a file/line cited). "Looks good" is not evidence.
❌ **Combining dimensions into a single "overall" score** — the 8 dimensions are independent. A server can be EXEMPLARY on context efficiency and FAIL on error distinction. The granularity is the value.
❌ **Skipping the headless-reliability check** — many servers pass all other checks but hang in non-TTY environments. The Inspector `--cli` test is the only reliable way to catch this.
❌ **Treating the 8 dimensions as a fixed checklist you tick** — the rubric is a frame, not a script. If a server has no session continuity because it's stateless, mark dimension 5 N/A and note it. If a server exposes resources but not tools, dimensions 1-3 still apply to the resources.
