# iter-8 Plan — Vendor-Disjoint Mock + Deterministic Grader

**Status:** Designed 2026-06-23. Targets two open problems: (1) iter-6's
structural blockage (the inference-gateway proxy is a single-model gateway,
so vendor-disjoint validation cannot run against the real proxy), and
(2) the +17.5pp sec-audit grader swing on bit-for-bit identical transcripts
(`md5 bda20918d4b7d0b7245bd12b59b09e58`) that the iter-7 REPORT flagged as
**grader noise** (see `iteration-7/GRADER-NOISE-INVESTIGATION.md`).

The mock-based design also opens the door to (3) full N=11 reliability
study (iter-5 follow-up) without the 33-hour wall-time budget the real proxy
would require.

See [`docs/.../research/vendor-disjoint-grader-mock-2026-06-23.md`](../../research/vendor-disjoint-grader-mock-2026-06-23.md)
for the full mock-implementation evaluation (3 candidates compared: WireMock
+ LiteLLM, `zerob13/mock-openai-api`, and a 30-line Python shim).

> **Supplements (2026-06-23):** [`2026-06-23-iter8-design-supplements.md`](../../research/2026-06-23-iter8-design-supplements.md)
> adds three things this plan does not cover: (1) a **two-layer MCP stack**
> for `secret_detection` (mock MCP server + mcp-assert test runner —
> mcp-assert is a test runner, not a mock); (2) a **Claude Code CLI flag
> inventory** with `--mcp-config` and `--max-turns` recommended for
> sub-experiments 8B and 8C; (3) a **LiteLLM multi-model gateway** as the
> v0.0.6+ replacement for the single-model `100.80.231.128:3456` proxy.

---

## Why iter-8

iter-7 shipped the canonical headline (**+21.88pp total_lift, 4/4 lifts, 0
hurts, deterministic endpoint grades**) but left two follow-ups open:

1. **Vendor-disjoint validation is structurally blocked** (iter-6 finding):
   the inference-gateway at `100.80.231.128:3456` serves all 18+ model
   aliases from a single `MiniMax-M3` backend. Only `glm-5.2` is genuinely
   vendor-disjoint, and it returns HTTP 503 `circuit_breaker_open: RateLimit`
   for the full 12-cell grading matrix. The +21.88pp iter-7 number is
   **conservative** (a single-model judge cannot apply Anthropic self-bias),
   but the +14.4pp gap between iter-6's code-only +7.5pp and iter-7's
   LLM-judgment +21.88pp suggests LLM judgment contributes substantially.

2. **Grader noise is uncontrolled** (iter-7 caveat #8): sec-audit's
   `secret_detection` assertion swung from 15.0 (iter-4) to 32.5 (iter-7) on
   bit-for-bit identical transcript. The 17.5pp swing on a deterministic
   input is a grader-side bug, not a model-side variance. Per Yagubyan 2026
   (arxiv:2606.13685), the grader's inter-run flip rate on a fixed input
   should be < 5pp; the observed 17.5pp is 3.5× the threshold.

iter-8 addresses both by introducing a **local OpenAI-API-compatible mock
grader** that returns deterministic responses for any (model_name, prompt)
pair, then routing the iter-7 harness through the mock in two modes:

- **Mode A (vendor-disjoint)**: mock returns sonnet-shaped responses when
  called with `model=sonnet-judge` but haiku-shaped responses when called
  with `model=haiku-judge`. This simulates a vendor-disjoint judge pipeline
  without requiring a second-model proxy.
- **Mode B (multi-run averaging)**: mock returns the same response for the
  same input on repeated calls (idempotent at the message level), enabling
  N=11 reliability study without model-side variance.

---

## iter-8 design

### Mock implementation: `zerob13/mock-openai-api` (B-grade)

Per the [vendor-disjoint mock research note](../../research/vendor-disjoint-grader-mock-2026-06-23.md),
the recommended mock is [`zerob13/mock-openai-api`](https://github.com/zerob13/mock-openai-api)
(Go-based, OpenAI-API-compatible, single binary, configurable per-route
response files). WireMock + LiteLLM (A-grade) is more featureful but
heavier; the 30-line Python shim (C-grade) is the fallback.

**Why not the real proxy:** the proxy serves all aliases from `MiniMax-M3`,
so a vendor-disjoint test against the proxy is structurally impossible
without changing the proxy. The mock gives us vendor-disjoint semantics
*for testing the grader harness*, not for testing the model.

### Fixtures: `iteration-8/fixtures/model-mapping.json`

One entry per grader model name. Each entry maps a request
`(model_name, prompt_hash)` to a canned response.

```json
{
  "haiku-judge": {
    "endpoint": "/v1/chat/completions",
    "responses_dir": "fixtures/haiku-judge/"
  },
  "sonnet-judge": {
    "endpoint": "/v1/chat/completions",
    "responses_dir": "fixtures/sonnet-judge/"
  },
  "opus-judge": {
    "endpoint": "/v1/chat/completions",
    "responses_dir": "fixtures/opus-judge/"
  },
  "glm-5.2-judge": {
    "endpoint": "/v1/chat/completions",
    "responses_dir": "fixtures/glm-5.2-judge/"
  }
}
```

### Grader integration: `JUDGE_FIXTURE_MODE=1`

`grader.py` reads `JUDGE_FIXTURE_MODE` from the environment. When set:

1. Override the judge base URL to `http://localhost:3000/v1`
2. Read the model name from the per-eval config and append `-judge` to
   select the fixture (e.g. `haiku` → `haiku-judge`)
3. Verify the response's `model` field matches the requested alias
   (defends against routing bugs in the mock)
4. Log the prompt-hash to the response file so we can audit the
   determinism claim

When unset, the grader behaves exactly as it does today (real proxy).

### docker-compose: `iteration-8/docker-compose.yml`

```yaml
version: "3.8"
services:
  grader-mock:
    image: zerob13/mock-openai-api:latest
    ports: ["3000:3000"]
    volumes:
      - ./fixtures:/app/fixtures:ro
  harness:
    build: ../  # uses the iter-7 runner image
    environment:
      JUDGE_FIXTURE_MODE: "1"
      ANTHROPIC_BASE_URL: "http://grader-mock:3000/v1"
    depends_on: [grader-mock]
    command: python scripts/run_iteration_8.py
```

---

## Iter-8 Sub-experiments

### iter-8A: Mock-based vendor-disjoint validation (the iter-6 follow-up)

**Goal:** Re-run iter-7's 4-eval subset (eval-skill, sec-audit, lint-1,
release-2) with the mock configured to return **haiku-shaped responses
when called as `sonnet-judge`** (simulating a vendor-disjoint judge).
Compare the resulting headline against iter-7's +21.88pp.

- **Wall time:** 4 evals × 3 configs × 1 trial = 12 runs ≈ 30 min
- **Output:** `total_lift_mock_vendor_disjoint` and per-eval deltas vs
  iter-7's same-vendor number
- **Decision rule:** if `|iter-8A total_lift − iter-7 total_lift| < 2pp`,
  the iter-7 headline is robust to vendor-disjoint substitution
  (same-family bias is negligible for this harness). If the gap is > 5pp,
  iter-7 needs a vendor-disjoint re-run before publishing.

### iter-8B: Grader noise root-cause (the sec-audit 17.5pp swing)

**Goal:** Replay the sec-audit iter-7 grading against the mock with
`JUDGE_FIXTURE_MODE=1` and confirm the response is bit-for-bit identical
across replays. If the mock response is identical but the iter-7 harness
produced a different number, the bug is in `grader.py`'s state machine
or its evaluation criteria, not in the model.

- **Wall time:** 1 eval × 3 configs × 10 replays = 30 grader calls ≈ 5 min
- **Output:** per-replay score, stddev, max-swing
- **Decision rule:** if stddev < 0.5pp across 10 replays, the mock is
  deterministic and the original 17.5pp swing is harness-side; the fix
  is in `grader.py` (likely the consultation-as-skill-match bug we
  already fixed in iter-3 for `lint-1`/`critic`/`release-2`).

### iter-8C: Multi-run averaging (the iter-5 follow-up)

**Goal:** N=11 trials per (eval, config) on the 4-eval subset with the
mock guaranteeing identical responses on identical inputs. This isolates
**agent-side variance** (the haiku solver's stochasticity on the
benchmark eval) from **judge-side variance** (which the mock removes).

- **Wall time:** 4 evals × 3 configs × 11 trials = 132 runs ≈ 2.5 hours
- **Output:** per-eval flip rate, per-config mean ± 95% CI, headline
  consultation-driven + file-access-driven lift with confidence intervals
- **Decision rule:** if per-eval flip rate < 10% (Yagubyan 2026 says
  13.6% mean), the +21.88pp iter-7 headline is well above the noise
  floor and a single trial is sufficient for the headline (N=1 is
  acceptable for magnitude claim; N=11 is required for significance).

---

## Decision Tree

```
Run iter-8A
  ├─ |iter-8A − iter-7| < 2pp → vendor-disjoint substitution does not
  │   move the headline; iter-7's +21.88pp is robust
  ├─ gap 2-5pp → soft caveat: same-family bias is real but small
  │   (publishable with footnote)
  └─ gap > 5pp → HARD STOP: iter-7 needs a vendor-disjoint re-run
       before next release

Run iter-8B in parallel
  ├─ mock replays give stddev < 0.5pp → bug is in grader.py, fix
  │   before next iteration
  └─ mock replays give stddev > 0.5pp → mock is non-deterministic
       (response caching bug); not safe to use for iter-8C

Run iter-8C (if 8B passes)
  └─ publish per-eval CI for +21.88pp in next CHANGELOG
```

---

## Wall-time budget

| Sub-experiment | Runs | Wall time | Status dependency |
|----------------|------|-----------|-------------------|
| iter-8A | 12 | 30 min | none (parallel) |
| iter-8B | 30 | 5 min | none (parallel) |
| iter-8C | 132 | 2.5 hours | iter-8B must pass |
| **Total (parallel)** | 174 | **3 hours** | iter-8A/8B independent |

---

## Files to create

```
docs/principled/skill-evals/marketplace-routing-2026-06-22/iteration-8/
  PLAN.md                              # this file
  docker-compose.yml                   # mock + harness orchestration
  fixtures/
    model-mapping.json                 # 4 grader aliases
    haiku-judge/                       # 12 canned responses
    sonnet-judge/                      # 12 canned responses
    opus-judge/                        # 12 canned responses
    glm-5.2-judge/                     # 12 canned responses
  scripts/
    run_iteration_8.py                 # iter-7 runner + JUDGE_FIXTURE_MODE
    capture_responses.py               # one-shot: record real-proxy
                                       # responses into fixtures/
    replay_grader.py                   # iter-8B: replay grader N times
  REPORT.md                            # post-run synthesis
```

---

## Success criteria

iter-8 ships when all 3 are true:

1. **iter-8A** shows |iter-8A − iter-7| < 5pp (vendor-disjoint substitution
   does not invalidate iter-7)
2. **iter-8B** shows stddev < 0.5pp on 10 replays of the same transcript
   (mock is deterministic)
3. **iter-8C** publishes per-eval CIs for the +21.88pp headline (if the
   iter-7 RELEASE-v0.0.5 is to be amended with significance claims)

If iter-8A fails criterion 1, iter-7 is still publishable but the next
release (v0.0.6) must include a vendor-disjoint re-run on a proxy that
isn't structurally single-model.

---

## Research grounding

- **Yagubyan 2026** (arxiv:2606.13685, 23 Apr 2026): N=11 trials for 95%
  majority-vote recovery; 13.6% mean pairwise flip rate. Justifies iter-8C.
- **Wataoka 2024** (arxiv:2410.21819, NeurIPS 2024 SGAI): self-preference
  bias via lower-perplexity preference. Justifies iter-8A's vendor-disjoint
  substitution.
- **CoEval 2026** (arxiv:2606.03650, 4 Jun 2026 v2): vendor-disjoint panel
  design. The mock-based vendor-disjoint is a test-harness simulation of
  the CoEval design, not a CoEval re-run.
- **zerob13/mock-openai-api** ([GitHub](https://github.com/zerob13/mock-openai-api)):
  Go-based OpenAI-API-compatible mock with per-route response files.
  Recommended in [vendor-disjoint-grader-mock research note](../../research/vendor-disjoint-grader-mock-2026-06-23.md).
- **Systematic 2026** (arxiv:2606.19544, 17 Jun 2026, Norman/Rivera/Hughes
  Berkeley): κ deflation 33.8-41.2pp universal across 21 judges; test-retest
  reliability >0.943 but decoupled from correctness. The "consistency-bias
  paradox" means a deterministic mock grader (high test-retest) is necessary
  but **not sufficient** for grading accuracy — iter-8B's stddev check
  measures the mock's consistency, not its correctness.

---

## Open follow-ups beyond iter-8

- **Real proxy upgrade**: the `100.80.231.128:3456` proxy is structurally
  single-model. iter-6 is structurally blocked until a vendor-disjoint
  proxy is available. Track as a v0.0.6+ prerequisite.
- **Heterogeneous judge matrix**: iter-4 used sonnet over haiku. iter-7
  reused iter-4's grading for time reasons. iter-9 should re-grade
  iter-7's transcripts with a heterogeneous judge matrix (sonnet / haiku /
  opus in rotation) to measure judge-side variance directly.
- **SkillsBench / SoK alignment**: arxiv:2602.12670 (SkillsBench, 87 tasks
  / 8 domains) and arxiv:2602.20867 (SoK: Agentic Skills) suggest a
  standardized eval surface that this marketplace does not currently
  target. Track as v0.1.0 scope.
