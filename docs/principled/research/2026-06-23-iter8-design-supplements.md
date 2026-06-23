# iter-8 Design Supplements — MCP Mocking, CLI Flags, Multi-Model Gateway

**Author:** Kimi Code (autonomous)
**Date:** 2026-06-23
**Scope:** Three research items that supplement the iter-8 plan at `docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-8-PLAN.md`.

---

## 1. MCP Mock for `secret_detection` Grader

### Problem identified after iter-8 plan committed

The iter-8 plan uses `<mock grader>` to mock LLM judge responses.
The sec-audit eval's `secret_detection` assertion uses MCP-style tool calls
against the agent's runtime. iter-7's sec-audit swung +17.5pp on identical
transcripts, partly because the MCP tool responses are not deterministic
even when the agent's behavior is. The iter-8 plan as written does not
address this.

### MCP mocking options (research 2026-06-23)

| Option | Stack | Maintenance | Pros | Cons | Verdict |
|--------|-------|-------------|------|------|---------|
| **mcp-assert** (blackwell-systems) | Go single binary, stdio/SSE/HTTP, MIT | github.com/blackwell-systems/mcp-assert, 18 stars, MIT, 0 open issues, project created 2026-04-23 | Purpose-built for deterministic MCP testing; `snapshot` command captures golden files, `intercept` records live tool-call trajectories, `run` replays against captured fixtures; 18 assertion types in YAML; 24 lint rules; integrated with Vitest / Jest / Bun / PHPUnit / pytest / Go test; adopted by Wyre Technology (25 servers) and Ant Group (AntV) | Only 18 stars, project is ~2 months old (created 2026-04-23); mcp-assert is a **test runner**, not a mock — still need a small mock MCP server (see §"Two-layer MCP stack" below) to feed golden responses | **A-grade (recommended)** for the test-runner + assertion layer |
| **Tyk mock MCP server** | Go, MCP 2025 spec | tyk.io, blog post (search hit) | Deterministic, self-contained, simple | Single-purpose; no schema-driven mock, no snapshot/replay workflow | B-grade (relegated — useful as the mock-MCP-server half, see below) |
| **mcpland/mock-mcp** | TypeScript, OpenAPI → MCP | github.com/mcpland, 2026 | AI-driven mock data from OpenAPI schemas | Heavier setup; depends on schema quality; no snapshot/replay | B-grade for schema-driven |
| **AIMock MCPMock** (CopilotKit) | Part of AIMock superset | github.com/CopilotKit/aimock, Apr 2026 | Integrated with LLMock + A2AMock + VectorMock + drift detection; production-tested at AG-UI | Larger install footprint (the whole AIMock stack); overkill if we only need MCP replay | A-grade only if we adopt the rest of AIMock |
| **Custom Python mock** | Python, minimal HTTP | local | Minimal dependencies; total control | No maintenance; must hand-write all responses | C-grade escape hatch |

**Recommended for iter-8 (revised 2026-06-23):** A **two-layer MCP
stack** for the MCP stdio half:

1. **Mock MCP server** (the actual mock the agent talks to via stdio):
   `<mock grader>` is **not** an option here (it's HTTP-only).
   Candidates: Tyk mock MCP server, AIMock MCPMock, or a custom Python
   mock — the simplest one that serves the captured golden responses.
2. **Test runner** (asserts behavior against the mock): **mcp-assert**
   for `snapshot --update` (capture phase) and `run --suite`
   (replay-and-assert phase). This is the new addition to iter-8.

The previous recommendation of "Tyk mock MCP server" or "AIMock
MCPMock" as the *sole* MCP solution is superseded — neither offers
snapshot/replay as a first-class workflow. mcp-assert is the missing
piece for determinism, but it doesn't replace the mock server, it
sits on top of it.

**OpenAI HTTP half** (unchanged): `<mock grader>` listens on
`:3000` inside the iter-8 `grader-mock` Docker Compose service
(per iter-8 PLAN.md docker-compose.yml lines 112-127).

### mcp-assert snapshot/replay workflow (new)

```bash
# 1. One-time capture phase: point mcp-assert at the REAL secret_detection
#    MCP server and snapshot the responses. --update writes (or overwrites)
#    the golden snapshot file; see mcp-assert docs for the default file
#    location (the pytest config shows the convention is a `fixtures/`
#    directory under the suite, but the CLI may use a different default).
#    Replace <secret-detection-server-cmd> with the actual command that
#    launches the real server.
mcp-assert snapshot --suite evals/secret-detection/ \
  --server "<secret-detection-server-cmd>" \
  --update

# 2. iter-8 runs: a mock MCP server (e.g., Tyk's mock-mcp-server binary)
#    serves those captured responses to the agent. mcp-assert then
#    asserts YAML expectations against the mock's outputs (not the
#    real server's). Replace <mock-mcp-server-cmd> with the actual
#    mock server's invocation; many mock servers take a --fixture flag.
mcp-assert run --suite evals/secret-detection/ \
  --server "<mock-mcp-server-cmd> --fixture evals/secret-detection/fixtures/secret-detection.json"

# 3. CI: gate on snapshot diff + assertion pass-rate
mcp-assert ci --suite evals/secret-detection/ --threshold 95 --junit results.xml
```

**Note on the bash example above:** the `<secret-detection-server-cmd>`
and `<mock-mcp-server-cmd>` placeholders are intentionally generic — the
exact package/binary names depend on which mock server we pick for
iter-8 (Tyk mock-mcp-server, AIMock MCPMock, or a custom Python mock).
The point of the example is to show the **workflow shape** (snapshot
real server → mock serves captured responses → mcp-assert asserts),
not to lock in specific package names.

**Key clarification from round-6 self-critic:** mcp-assert is a
**test runner**, not a mock. The architecture has two layers, not
one. mcp-assert does NOT serve responses to the agent — the mock
MCP server does. mcp-assert speaks the real MCP protocol (initialize
handshake, tools/list, tools/call) against whatever server you point
it at, then asserts YAML expectations against the responses. For
iter-8, the "server" is a mock that returns the captured golden
responses.

### Claude Code CLI integration

`claude --mcp-config <file>` (added in a recent claude-code version per the
[changelog](https://code.claude.com/docs/en/changelog); the version pin is
not verified from this research, treat as "newer claude-code only") accepts
a JSON file that lists MCP servers. This flag is the cleanest integration
point for iter-8: configure `secret_detection` to point at a mock MCP
server via `--mcp-config`, the agent calls the mock, and the grader sees a
deterministic response.

```bash
claude --mcp-config mocks/secret-detection-mock.json \
       --add-dir <eval project dir> \
       -p "<sec-audit prompt>"
```

**Sources:**
- [Tyk mock MCP server blog post](https://tyk.io/blog/imagine-build-share-how-integration-testing-led-me-to-create-the-tyk-mock-mcp-server/)
- [mcpland/mock-mcp on GitHub](https://github.com/mcpland/mock-mcp)
- [AIMock: One Mock Server For Your Entire AI Stack (CopilotKit DEV.to post, 8 Apr 2026)](https://dev.to/copilotkit/aimock-one-mock-server-for-your-entire-ai-stack-1jhp)
- [MockServer AI Protocol Mocking](https://www.mock-server.com/mock_server/ai_protocol_mocking.html)
- [Claude Code changelog](https://code.claude.com/docs/en/changelog) (--mcp-config added)

---

## 2. Claude Code CLI Flag Inventory (full list, 2026-06-23)

Discovered during the research for iter-8: the iter-7 design uses
`--disable-slash-commands` and `--add-dir` exclusively. The cheat-sheet
inventory below shows several other flags relevant to iter-8 and future
iter-N design.

### Flags directly relevant to the 3-config lift disambiguation

| Flag | Description (per cheat sheet) | iter-N relevance |
|------|------------------------------|------------------|
| `--bare` | "Scripted mode — skip hooks, LSP, **plugins**" (cheat sheet description, not verified against official changelog) | Alternative to `--disable-slash-commands` for true no-plugin baseline. **Worth testing in iter-8B** to see if it's a cleaner mechanism than `--disable-slash-commands` (which only affects slash command resolution, not plugin auto-load). |
| `--plugin-dir <path>` | Load plugin directory or `.zip` archive for the current session (cheat sheet description, version unverified) | Load a pinned version of the marketplace plugin for reproducibility. Iter-4 cache contamination finding made this relevant: loading a specific plugin path eliminates the v2.0.0 stale cache risk. |
| `--settings <file>` | Point at a custom settings.json | Could be used to set per-config permissions, model, or allowedTools without touching the global settings. |
| `--mcp-config <file>` | MCP server config (cheat sheet description, version unverified) | See section 1 above. |
| `--model` | Override model for the session | Useful for testing different solver models on the same eval (relevant to iter-6's vendor-disjoint goal once the proxy is fixed). |
| `--effort` | Set effort level: low, medium, high | Test whether effort changes the consultation/structure signals. |
| `--allowedTools` | Restrict available tools (e.g., "Edit,Bash(npm:*)") | Could disable specific tools in the baseline to isolate the marketplace lift from tool-availability noise. |
| `--max-turns` | Limit autonomous turns | Bounds the eval runtime. iter-7 already uses 180-300s timeouts; --max-turns would be a more deterministic budget. |
| `--permission-mode` | Set permission mode (auto, plan, etc.) | Test whether agent autonomy changes the consultation signal. |

### iter-8 design recommendation

**Add `--mcp-config` to the iter-8B grader-noise root-cause sub-experiment** (sub-experiment 8B from iter-8 PLAN.md). Concretely:

1. Run sec-audit with `--mcp-config mocks/secret-detection-mock.json` pointing at the mock MCP server (Tyk mock or a custom Python mock that serves the captured responses from §1). The harness invokes the mock via stdio.
2. Use `mcp-assert snapshot --server <real-server>` to capture the original responses once, then have the mock MCP server serve those exact responses to the agent in iter-8 runs.
3. If the +17.5pp grader swing collapses to <2pp, the cause was non-deterministic MCP tool responses, not LLM judge noise.
4. If the swing persists, the cause is the LLM judge (which is the next thing to test via `<mock grader>`).

This is a cheap 1-hour experiment that surgically disambiguates the two suspected noise sources.

**Sources:**
- [Claude Code Cheat Sheet 2026 (Blake Crosley)](https://blakecrosley.com/guides/claude-code-cheatsheet) — every flag, command, shortcut
- [Claude Code changelog](https://code.claude.com/docs/en/changelog) — versioned flag additions

---

## 3. Multi-Model Gateway for `<private inference gateway>` Replacement

### Problem

The current proxy at `<private inference gateway>` is structurally a single-model
gateway (20 vendor aliases — all serve `the configured backend`; only
`an external judge vendor` is vendor-disjoint and is rate-limited). This blocks iter-6's
vendor-disjoint validation goal and is a real architectural constraint on
the marketplace evaluation methodology going forward.

### Gateway options (research 2026-06-23)

| Gateway | Stack | License | Stars | MCP support | A2A support | Self-host complexity | Verdict |
|---------|-------|---------|-------|-------------|-------------|----------------------|---------|
| **LiteLLM** | Python | NOASSERTION (dual) | 51,259 | ✅ native MCP gateway | ✅ A2A Protocol | Low (single Docker) | **A-grade (recommended)** |
| **Bifrost** | Go | open source | (smaller) | partial | partial | Low | B-grade |
| **Portkey** | hosted + self-host | proprietary | n/a | yes | yes | Low (managed) | B-grade if managed is OK |
| **Kong AI Gateway** | Kong + plugin | Apache | n/a | via plugin | via plugin | Medium (Kong stack) | B-grade for orgs already on Kong |
| **OpenRouter** | hosted only | proprietary | n/a | no | no | Zero (managed) | A-grade if managed-only is OK |

**Recommended:** **LiteLLM** as the self-hosted replacement. Reasons:

1. **De-facto standard**: 51K stars, used by Stripe, Netflix, and major
   agent SDK vendors
2. **Drop-in OpenAI compatibility**: the existing iter-N harness code that talks to `<private inference gateway>` continues to work with just a base-URL change
3. **Native MCP gateway**: iter-8's mock work extends naturally to a real MCP gateway in v0.0.6+
4. **Native A2A protocol support**: future-proofs for agent-to-agent evaluations
5. **8ms P95 latency at 1k RPS**: well within the eval harness's needs
6. **Admin dashboard + virtual keys + spend tracking + guardrails**: production-ready
7. **100+ providers**: includes the vendor-disjoint options needed
   (multiple independent model families beyond the configured backend)

**Migration path (v0.0.6+):**

1. Stand up LiteLLM in a Docker container pointing at the existing
   `the configured backend` endpoint + at least 2 vendor-disjoint
   providers (e.g., two independent model families).
2. Update the iter harness's `OPENAI_BASE_URL` env var from `http://<private inference gateway>` to `http://litellm:4000`.
3. Re-run iter-6 with the new gateway. The vendor-disjoint grading should now succeed (instead of 503ing like in iter-6 REPORT.md).
4. Drop the `<mock grader>` for production eval runs (keep it for offline regression tests).

**Sources:**
- [BerriAI/litellm on GitHub](https://github.com/BerriAI/litellm) — 51,259 stars, MCP gateway, A2A protocol
- [Stop Juggling LLM APIs: 8 Gateways Ranked 2026 (TECHSY)](https://techsy.io/en/blog/best-llm-gateway-tools)
- [AI Gateway Comparison 2026 (SlashLLM)](https://slashllm.com/resources/ai-gateway-comparison)
- [LLM Gateway Comparison 2026 (FloTorch)](https://www.flotorch.ai/blogs/llm-gateway-comparison-2026)
- [Multi-Model Routing — The AI Gateway Pattern (akshayghalme.com, 25 Apr 2026)](https://akshayghalme.com/blogs/multi-model-routing-ai-gateway-pattern/) — the 40-70% bill reduction thesis

---

## Summary

| Finding | Impact on iter-8 | v0.0.6+ impact |
|---------|-------------------|------------------|
| **mcp-assert** (snapshot/replay) for MCP stdio + **<mock grader>** for OpenAI HTTP | Surgical disambiguation of the sec-audit +17.5pp grader swing (1-hour experiment); full snapshot/replay determinism for both halves of the eval stack | Real MCP gateway via LiteLLM MCP support; `mcp-assert snapshot` mode becomes the CI regression gate |
| Claude Code CLI flag inventory | iter-8B design needs `--mcp-config`; iter-8C design could use `--max-turns` for budget | iter-N+1 designs benefit from `--plugin-dir` for pinned reproducibility |
| LiteLLM as multi-model gateway | Unblocks iter-6 vendor-disjoint validation | Replaces the single-model `<private inference gateway>` proxy |

---

*Generated autonomously as iter-8 design supplements (2026-06-23). MCP-mocking section revised 2026-06-23 after mcp-assert was discovered; previous recommendation of Tyk mock / AIMock MCPMock is superseded. All three findings sourced from web research 2026-06-23 (SearXNG + GitHub API).*
