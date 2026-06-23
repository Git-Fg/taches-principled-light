# Project Learnings

Distilled from plan artifacts and session work. Each entry: category + confidence (1-5) + title, source, insight, evidence, action.

---

### [PROCESS] [conf 4] Citation audit must run BEFORE release cut, not after

**Source:** v0.0.6 self-critic rounds 1+2 (`eca1b74`); iter-8 design supplements
**Insight:** The CHANGELOG draft round introduced 4 fabricated arXiv IDs + 1 fabricated κ=0.770 number + 6 hallucinated "Berkeley" affiliations that survived 1 round of self-critic and required a second round after external-fact re-verification.
**Evidence:** Commit `ab33fa8` (citation hallucination remediation for v0.0.5); commit `eca1b74` (Berkeley hallucination removal for v0.0.6). All 6 Berkeley attributions for arXiv:2606.19544 (Norman/Rivera/Hughes) were invented during iterative paraphrasing; the arXiv abstract contains no "Berkeley".
**Action:** Add a pre-release factual-audit step that grep's for newly-introduced proper nouns and verifies each against the cited arXiv abs page or GitHub repo metadata. Include the verification evidence inline in the citation block (e.g., "verified 2026-06-23").

---

### [ANTI-PATTERN] [conf 5] LLM summarization is the failure mode for institutional affiliation hallucination

**Source:** v0.0.6 self-critic round 2 (`eca1b74`)
**Insight:** The word "Berkeley" was never in any source for arXiv:2606.19544 — it was invented during iterative paraphrasing of "Norman/Rivera/Hughes 2026". A pre-commit gate that grep'd for newly-introduced proper nouns against a known-institutions allowlist would catch this class of error.
**Evidence:** arXiv abs page fetched via `mcp__mcp-searxng__fetch` on 2026-06-23; "Berkeley" appears in 0 places in the abstract. The author list is "Norman, Rivera, Hughes" with no institutional attribution in the abstract.
**Action:** For any paper citation, include the institutional affiliation only if it's in the abstract or a verified secondary source (institution's own page, paper PDF's author block). When the affiliation is not directly verifiable, omit it or use "et al." style.

---

### [TECHNICAL] [conf 5] LiteLLM is the canonical A-grade self-host proxy replacement

**Source:** iter-8 design supplements; v0.0.6 release notes
**Insight:** BerriAI/litellm (51,259 stars as of 2026-06-23) is the only A-grade gateway that combines native MCP gateway + A2A protocol + drop-in OpenAI compat + single-Docker self-host. Bifrost is B-grade (partial MCP/A2A support).
**Evidence:** GitHub API: 51,259 stars. `mcp__mcp-coderepo__github_search` confirmed `litellm/a2a_protocol/{client,handler,exception_mapping_utils}.py` and `litellm/proxy/a2a/agent_card.py` and `litellm/proxy/agent_endpoints/a2a_endpoints.py` and dashboard `a2a_send_message.tsx`. Bifrost has only partial MCP/A2A support per the supplements table.
**Action:** Use LiteLLM as the canonical self-host option when
`<private inference gateway>`'s structural single-model limitation
needs to be removed. Bifrost is fallback only.

---

### [PATTERN] [conf 4] Two-layer MCP test-runner stack for deterministic eval

**Source:** iter-8 design supplements; iter-6/7 grader noise investigation
**Insight:** The correct architecture is a mock MCP server (Tyk / AIMock / custom) feeds captured golden responses, AND mcp-assert (github.com/blackwell-systems/mcp-assert, Go, MIT) acts as the test runner that asserts YAML expectations. Neither layer alone solves the problem.
**Evidence:** mcp-assert has `snapshot`, `intercept`, `run` commands; 18 assertion types in YAML; 24 lint rules; project created 2026-04-23. 18 GitHub stars, 0 open issues, MIT license. Adopted by Wyre Technology (25 servers) and Ant Group (AntV) per the supplements note.
**Action:** For any new MCP-based skill eval, use the two-layer stack. Document `claude --mcp-config <file>` (added in v2.1.27+) as the cleanest integration point.

---

### [PROCESS] [conf 4] Cache contamination can inflate eval lifts 30-40%

**Source:** iter-3 to iter-4 transition
**Insight:** iter-3 reported +8.69pp; iter-4's +4.94pp corrected for stale v2.0.0 plugin cache showing different skill names. Without the correction, the lift would have been reported as +8.69pp — a 76% overstatement.
**Evidence:** iter-4 REPORT.md cache-contamination section.
**Action:** For any eval across agent versions, drop the first run (or verify cache state explicitly). Add a cache-state assertion to the eval harness. The marketplace-validator's `cache` lint is a partial mitigation but not a complete fix.

---

### [PROCESS] [conf 5] Self-critic must be at least a 2-stage loop with external-fact re-verification

**Source:** v0.0.5 + v0.0.6 release cycles
**Insight:** Round 1 (line-count + cross-reference drift) caught 3 MEDIUM. Round 2 (external-fact re-verification via fresh API calls) caught 1 HIGH hallucination + 2 MEDIUM drift. External-fact verification is the only round that catches institutional-name hallucination.
**Evidence:** 3 self-critic rounds on v0.0.5; 2 self-critic rounds on v0.0.6. Without the second round, the 6 Berkeley hallucinations would have shipped.
**Action:** Always run at least 2 rounds before declaring done: (1) line-count + cross-reference drift, (2) external-fact re-verification via fresh API calls (`mcp__mcp-coderepo` for repos, `mcp__mcp-searxng__fetch` for arXiv).

---

### [DECISION] [conf 5] Two-layer MCP architecture beats single-layer for `secret_detection` eval

**Source:** iter-8 design supplements; v0.0.6 release
**Insight:** A mock MCP server alone is not enough — you need a test runner to assert expectations. mcp-assert is purpose-built for this; AIMock MCPMock and Tyk mock-mcp-server are purpose-built for the mock side. The two are different concerns with different design constraints.
**Evidence:** iter-8 PLAN §"Two-layer MCP stack"; supplements note table; mcp-assert README via SearXNG.
**Action:** Use the two-layer stack for any MCP-based eval. Decompose into mock-server half + test-runner half; pick a tool for each.

---

### [PROCESS] [conf 4] vendor-disjoint grading requires a multi-family proxy

**Source:** iter-6 REPORT.md; iter-8 PLAN §8A
**Insight:** iter-6 needed an external judge vendor (vendor-disjoint
from the configured solver) for vendor-disjoint validation, but the
inference proxy `<private inference gateway>` is a single-model
gateway, so iter-6 returned 503 for all 12 grading cells. Without a
multi-family proxy (LiteLLM), vendor-disjoint validation is
structurally impossible.
**Evidence:** iter-6 REPORT.md; iter-8 PLAN §8A vendor-disjoint design. iter-6 mean lift of +7.5pp (code-only) is below iter-7's +21.88pp (LLM-judgment added) by +14.4pp.
**Action:** For any future iter, the eval harness must either (a) target
a multi-family proxy (LiteLLM), or (b) explicitly note vendor-disjoint
is unvalidated in this iter's REPORT.md.

---

### [TECHNICAL] [conf 5] mcp-assert is a test runner, NOT a mock

**Source:** iter-8 design supplements; round 6 self-critic
**Insight:** This was a class of error caught in round 6 self-critic. AIMock MCPMock and Tyk mock-mcp-server are the mock-server half; mcp-assert is the test-runner half. The two are different concerns and have different design constraints.
**Evidence:** mcp-assert commands are `audit`, `fuzz`, `init`, `run`, `ci`, `coverage`, `snapshot`, `watch`, `matrix`, `intercept`, `lint`, `generate` — all test-runner concerns, not mock concerns.
**Action:** When designing MCP eval, decompose into mock-server half + test-runner half; pick a tool for each. Don't conflate them in design docs.

---

### [PATTERN] [conf 5] Skill-availability lift magnitude cross-confirmed by Xu 2026 + Gorinova 2026

**Source:** iter-7 cross-confirmation; CHANGELOG.md v0.0.6 entry
**Insight:** iter-7's +21.88pp total_lift sits in the middle of Xu 2026's controlled SkillsBench lift bracket (+18-36pp for GPT-5.5 and DeepSeek V4-Flash). Gorinova 2026's 500-skill × 19-model study provides qualitative cross-confirmation: "access to a skill significantly changes model behavior". Two independent witnesses = strongest evidence.
**Evidence:** arxiv:2605.31408 abstract (+26.7-36.0pp GPT-5.5, +18-26.0pp DeepSeek V4-Flash on 30-task domain-balanced SkillsBench subset, 5 trials/cell); arxiv:2606.17819v1 abstract (500 skills, 19 models, "significantly changes model behavior").
**Action:** When claiming a lift magnitude, always cross-check against at least 2 third-party studies. For skills-eval, Xu 2026 (arxiv:2605.31408) and Gorinova 2026 (arxiv:2606.17819) are the canonical references.

---

### [PROCESS] [conf 4] plan-archive workflow needs adaptation for CHANGELOG-as-summary projects

**Source:** This archive session (v0.0.6 marketplace-routing closure)
**Insight:** The `project-maintenance` skill's hard precondition (`SUMMARY.md` at the same path as `PLAN.md`) is too strict for projects using CHANGELOG entries + grading_summary.json as the closure record. A pragmatic adaptation: use `STATUS.md` pointing to the release tag + CHANGELOG entry as the closure marker.
**Evidence:** `skills/project-maintenance/SKILL.md` Phase 1 hard precondition. This project has 4 completed PLAN files but no formal `SUMMARY.md` files (eval-iteration workflow uses CHANGELOG + grading_summary.json instead).
**Action:** Either (a) adopt `plan-lifecycle EXECUTE` mode to produce `SUMMARY.md` per plan, or (b) update `project-maintenance` SKILL.md to accept alternative closure markers (CHANGELOG entry, release tag, grading_summary.json). Suggest option (b) — CHANGELOG-as-summary is the marketplace-plugin convention.

---

## Deduplication

No prior `docs/principled/memory/learnings.md` existed before this session. All 11 entries are novel. Future sessions should check for category+topic overlap before appending.
