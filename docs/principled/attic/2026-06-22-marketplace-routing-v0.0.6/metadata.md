# Archive: 2026-06-22-marketplace-routing-v0.0.6

**Archived:** 2026-06-23
**Milestone:** v0.0.6 release — marketplace-routing eval cycle closure
**Phase:** iter-1 through iter-7 (post-v0.0.5 polish, iter-8 design, citation audit)
**Status:** completed
**Learnings extracted:** 11 (see `docs/principled/memory/learnings.md`)

## Files

- `plans/iteration-5-6-7-PLAN.md`: comprehensive plan for iter-5 (hypothesis exploration), iter-6 (vendor-disjoint grader validation), iter-7 (canonical headline). Closed at iter-7 with +21.88pp total_lift.
- `plans/iteration-3-design.md`: design doc for iter-3; iter-3 itself ran to +8.69pp headline.
- `plans/PLAN.md` (from iter-4 dir): iter-4 plan that corrected iter-3's headline from +8.69pp to +4.94pp after identifying cache contamination.
- `plans/RESEARCH-FINDINGS-iter5-design.md` (from iter-4 dir): research findings that drove the iter-5/6/7 plan; cross-validates 6 third-party papers (Wataoka 2024, Belmadani 2026, SkillRouter 2026, Norman/Rivera/Hughes 2026, Xu 2026, Gorinova 2026).

## Key decisions

- **iter-7 canonical headline = +21.88pp** (4/4 lifts, 0 hurts, deterministic endpoint grades). Decomposed into +8.12pp consultation + +13.75pp filesystem_access.
- **Cache contamination correction** (iter-3 → iter-4): the iter-3 +8.69pp was inflated by stale v2.0.0 plugin cache. iter-4 dropped to +4.94pp after correction.
- **iter-6 vendor-disjoint blocked**: glm-5.2 returned 503 from `100.80.231.128:3456` (single-model gateway). iter-7 used a sonnet-over-haiku heterogeneous pair (not vendor-disjoint) to produce the canonical headline.
- **iter-8 design (forward-looking, NOT archived)**: two-layer MCP test-runner stack (mock MCP server + mcp-assert test runner) addresses the +17.5pp sec-audit grader swing on identical transcripts.
- **LiteLLM as proxy replacement** (forward-looking): BerriAI/litellm (51,259 stars) is the canonical A-grade self-host option, with native MCP gateway + A2A protocol + single-Docker deployment.
- **v0.0.6 self-critic 2 rounds**: round 1 caught line-count drift (3 MEDIUM); round 2 caught external-fact drift (1 HIGH hallucination + 2 MEDIUM) after re-verifying via `mcp__mcp-coderepo` + `mcp__mcp-searxng__fetch`.

## Closures

- Git tag `v0.0.6` pushed: ✓
- CI release-gate PASS: ✓ (runs 28041652620, 28041651474)
- Self-critic round 2 fix committed (`eca1b74`): ✓
- 4 plugin manifests synchronized to 0.0.6: ✓
- CHANGELOG `[0.0.6]` section written: ✓
- README "What's New in 0.0.6" section written: ✓
- `.github/RELEASE-v0.0.6.md` long-form release page: ✓
