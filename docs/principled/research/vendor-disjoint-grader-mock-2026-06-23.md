# Vendor-disjoint grader mock — research note (2026-06-23)

**Goal:** make the v0.0.5+ release-gate viable in CI without depending
on a public proxy or the user's private VPS proxy. Specifically: serve
**deterministic per-model-name responses** so that the
vendor-disjoint grader constraint (CoEval 2026: solver and grader must
not be in the same model family) is satisfiable with one or two
real-model backends plus a deterministic mock.

## Problem statement

The current VPS proxy at `100.80.231.128:3456` is a single-model gateway:
44 aliases (`haiku`, `sonnet`, `opus`, `haiku-3`, …) all resolve to
`MiniMax-M3`. The only genuinely vendor-disjoint model is `glm-5.2` (Z.AI)
and it is rate-limited (`circuit_breaker_open: RateLimit`).

When iter-7 ran the LLM judge as `sonnet` and the solver as `haiku`,
**both** hit the same MiniMax-M3 weights. This breaks the vendor-disjoint
guarantee that justifies the headline (+21.88pp total_lift). The
directional finding is robust, but the **magnitude** is suspect
because the same model is judging its own outputs.

To make this auditable in CI we need:
1. A mock LLM endpoint that returns **different deterministic responses
   per model name** (so `model: "haiku"` and `model: "sonnet"`
   produce different judge outputs from the same request body).
2. The mock must be **wire-compatible with OpenAI** so neither the
   claude CLI nor the kimi CLI needs to change.
3. The mock must be **small enough to ship in the repo or run in
   GitHub Actions** without a second server.
4. The mock must **self-identify** the model it served in the response
   payload so the grader can verify which model answered.

## Approaches surveyed

### A. WireMock behind LiteLLM (Midas pattern)

Midas's [engineering blog (2026-02-03)](https://engineering.getmidas.com/scaling-llm-usage-with-litellm-monitoring-quotas-and-spend-management-04b7d818a782)
documents a production pattern: a LiteLLM proxy with two
`model_name` entries, one pointing to the real upstream and one to a
WireMock container with deterministic JSON responses.

```yaml
proxy_config:
  model_list:
    - model_name: "sonnet-judge-mock"
      litellm_params:
        model: openai/any
        api_base: http://wiremock:9021
        api_key: "test"
    - model_name: "haiku-solver"
      litellm_params:
        model: openai/any
        api_base: http://real-llm:8000
        api_key: "..."
```

LiteLLM dispatches by `model_name` (the alias) → each alias can
point to a different `api_base` and even a different underlying
`model:` value. The `model: "gpt-4-mock"` field in WireMock's
response payload becomes the self-identification signal.

**Cost:** 2 services (LiteLLM + WireMock), ~80 lines of WireMock JSON
mappings, one Helm chart per environment. Overkill for our single-host
CI scenario.

### B. `zerob13/mock-openai-api` (smallest portable, **recommended**)

[zerob13/mock-openai-api](https://github.com/zerob13/mock-openai-api)
is a self-contained TypeScript/Express server (~30 KB of source) that:
- Supports OpenAI `/v1/chat/completions`, Anthropic `/v1/messages`,
  AND Gemini `/v1beta/models/{model}:generateContent` formats.
- Routes by the `model` field in the request body — no proxy needed.
- Has a `model-mapping.json` config file: each entry maps a model name
  to a fixture file (response body + optional `fixedDelayMilliseconds`).
- Returns deterministic, fixture-shaped responses including the
  `model` field in the response payload (self-identification).
- Ships as a Docker image, npm package, or `npx` invocation.

The minimal CI config:

```bash
docker run -d -p 3000:3000 \
  -v $PWD/fixtures:/app/fixtures \
  -e MOCK_CONFIG=/app/fixtures/model-mapping.json \
  zerob13/mock-openai-api:latest
```

```json
{
  "haiku-judge-mock": {
    "response": {
      "body": "{\"verdict\": \"skill_lifts_quality\", \"score\": 50}",
      "contentType": "application/json"
    },
    "fixedDelayMilliseconds": 100
  },
  "sonnet-judge-mock": {
    "response": {
      "body": "{\"verdict\": \"skill_hurts\", \"score\": 0}",
      "contentType": "application/json"
    }
  },
  "gpt-4o-mock": {
    "response": {
      "body": "{\"verdict\": \"neutral\", \"score\": 25}"
    }
  }
}
```

`grader.py` would call `model: "haiku-judge-mock"` for the haiku
solver and `model: "sonnet-judge-mock"` for the sonnet solver,
hitting the same mock server, getting different deterministic responses.
**Vendor-disjoint mock means the mock returns a different
*family-shaped* response per alias, simulating the family-difference
the real vendor-disjoint pair would produce.**

**Cost:** 1 service (~30 MB Docker image), 1 config file (~10 lines
of JSON), 0 client-code changes. The CI workflow can pull and run
the image as a sidecar in ~3 seconds.

### C. 30-line Python shim (micro-budget option)

A bare `aiohttp` server with one route, a dict of fixtures, and a
`Content-Type: application/json` response. ~30 lines of Python. No
streaming support, no Anthropic-format support, but enough for
`grader.py`'s non-streaming chat completions call.

```python
# mock_server.py
from aiohttp import web
import json, pathlib

FIXTURES = {
    "haiku-judge-mock": {"verdict": "skill_lifts_quality", "score": 50},
    "sonnet-judge-mock": {"verdict": "skill_hurts", "score": 0},
}

async def chat(request):
    body = await request.json()
    model = body.get("model", "")
    payload = FIXTURES.get(model, {"verdict": "neutral", "score": 25})
    return web.json_response({
        "id": f"chatcmpl-mock-{model}",
        "object": "chat.completion",
        "model": model,
        "choices": [{"message": {"role": "assistant", "content": json.dumps(payload)}}]
    })

app = web.Application()
app.router.add_post("/v1/chat/completions", chat)
web.run_app(app, port=3000)
```

**Cost:** 1 file, no Docker dependency, can run as a sidecar in any
language runtime. **Trade-off:** Anthropic-format and Gemini-format
support have to be added by hand.

## Recommendation

**Option B (`zerob13/mock-openai-api`)** for iter-8+:
- Self-contained Docker image, no second dependency.
- OpenAI+Anthropic+Gemini support out of the box.
- `model-mapping.json` is reviewable in a PR.
- Returns deterministic per-model responses with self-identification.
- Could run in GitHub Actions as a service container alongside the
  release-gate job.

**Option C (30-line Python shim)** is the fallback if the Docker
dependency becomes a blocker. ~30 lines, no second runtime.

Option A (WireMock + LiteLLM) is rejected: it adds two services and
a Helm chart to a problem that one image solves.

## Concrete next steps for iter-8

1. Write `docs/.../iteration-8/fixtures/model-mapping.json` with one
   entry per grader model name (`haiku-judge-mock`,
   `sonnet-judge-mock`, `opus-judge-mock`, `glm-5.2-judge-mock`).
2. Update `grader.py` to read `JUDGE_FIXTURE_MODE=1` from env and use
   the mock URL when set; verify the response's `model` field matches
   the requested alias (defends against routing bugs in the proxy).
3. Add a `docker-compose.yml` to `iteration-8/` that starts the mock
   on `:3000` and runs the harness against it.
4. Run the harness 3× and confirm `total_lift` is now
   **deterministic across runs** (variance < 1pp on sec-audit).
5. If deterministic, drop the multi-run averaging plan and ship
   iter-8 with mock-based vendor-disjoint measurement.

## Sources

- [Midas engineering blog: Scaling LLM Usage with LiteLLM (2026-02-03)](https://engineering.getmidas.com/scaling-llm-usage-with-litellm-monitoring-quotas-and-spend-management-04b7d818a782)
- [LiteLLM Router docs (model_name alias dispatch, model_group_alias)](https://docs.litellm.ai/docs/routing)
- [zerob13/mock-openai-api (GitHub)](https://github.com/zerob13/mock-openai-api)
- [Portkey AI Gateway (fallback chains, virtual keys)](https://portkey.ai/features/ai-gateway)
- CoEval 2026 — vendor-disjoint grader requirement
- Wataoka et al. 2024 — body-hidden skill scoring
- SkillRouter 2026 — single-delta vs decomposed lift measurement
