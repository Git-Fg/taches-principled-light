# Bucket A Transcript Inspection — Detailed Findings

**Date**: 2026-06-23
**Source**: `/tmp/inspect_bucket_a.py` (run against iter-2 transcripts)
**Reference**: corrected iter-3 REPORT.md (commit `dabe1bc`)

## What the 8 Bucket A evals actually show

The iter-3 corrected report classified 8 evals as "Bucket A — discovery
failure" because the with-skill agent scored 0/5 on assertions. The
transcript inspection reveals a more nuanced picture: **3 of the 8 are
proxy API errors (not discovery failures)**, and 1 of the 8 actually
DID invoke the marketplace skill but produced no useful output.

### Sub-bucket A1: Proxy API errors (NOT discovery failures)

| Eval | Both configs error | Why this happened |
|---|---|---|
| `plan-multi` | 503 All providers exhausted | proxy outage |
| `task-small` | 503 All providers exhausted | proxy outage |

These two evals are **non-discriminating**: both with_skill and
without_skill hit the same proxy error and produced no output. The
marketplace skill had nothing to do with the 0/0 result. They should
be EXCLUDED from the discovery-failure analysis and re-run before
drawing conclusions about `plan-lifecycle` and `task-lifecycle`.

### Sub-bucket A2: Skill invoked but no output (partial discovery)

| Eval | with-skill skill calls | assistant text blocks | Diagnosis |
|---|---|---|---|
| `research` | 1 (`deep-research`) | **0** | Skill was invoked but produced no visible output |

The agent DID invoke the marketplace `deep-research` skill. But the
transcript shows 0 assistant text blocks — the skill invocation may
have returned empty content or the agent's response was filtered out.
This is a **partial discovery success** that masquerades as failure.

### Sub-bucket A3: True discovery failures (agent picks plugin over marketplace)

| Eval | with-skill action | Diagnosis |
|---|---|---|
| `ingest-1` | 0 reads, 0 skill calls, just asks "what's the URL?" | Agent didn't read `ingesting-skills`; asked for clarification |
| `ingest-2` | 1 read (`marketplace.json` — wrong file), 0 skill calls | Agent scanned the wrong directory; never found `ingesting-skills/SKILL.md` |
| `lint-2` | 0 reads, 0 skill calls, just asks "which skill?" | Agent didn't read `marketplace-validator`; routed to `crafting-skills` in its response |
| `craft-create` | 1 skill call: **`superpowers:writing-skills`** | **Direct evidence** of H1: marketplace `crafting-skills` shadowed by plugin skill |
| `craft-review` | 0 reads, 0 skill calls, just asks "which skill?" | Same as lint-2: agent asks for clarification |

**The most important finding**: `craft-create` is **direct evidence
that the marketplace catalog is shadowed by the plugin catalog**. The
agent had both `crafting-skills` (marketplace) and
`superpowers:writing-skills` (plugin) in scope. It picked the plugin
skill. The without_skill config also picked the same plugin skill.
Both scored 0/5 because neither consulted the marketplace skill.

## What this tells us about the discovery problem

### H1 (plugin skills shadow marketplace) — **CONFIRMED**

`craft-create` is a smoking gun: the with-skill config loaded
`crafting-skills` AND the agent still picked `superpowers:writing-skills`.
The marketplace catalog is NOT being surfaced in the agent's discovery
path with the same priority as plugin skills.

### H2 (descriptions don't surface) — partially supported

`ingest-2` reads `marketplace.json` (the plugin manifest) but not
`ingesting-skills/SKILL.md`. The agent scanned the wrong directory.
This suggests the discovery path is: (1) read plugin manifest, (2)
look at slash_commands. Marketplace skills added via `--add-dir`
require a separate scan that the agent doesn't always perform.

### H3 (choice paralysis from 26+ skills) — partially supported

`ingest-2` reads `marketplace.json` and sees the full marketplace
catalog, then asks "which skill?" instead of picking `ingesting-skills`.
This is consistent with choice paralysis, though it's a single data point.

## Revised bucket breakdown

| Sub-bucket | Count | Evals | Discovery failure? |
|---|---:|---|---|
| A1 (proxy error) | 2 | plan-multi, task-small | NO — re-run before judging |
| A2 (skill invoked, no output) | 1 | research | PARTIAL — investigate skill invocation |
| A3 (true discovery failure) | 5 | ingest-1, ingest-2, lint-2, craft-create, craft-review | YES — discovery path issue |

The true discovery failure rate is **5 of 17 evals (29%)**, not 8 of 17.
And the discovery failures cluster around marketplace skills that have
plugin-skill twins:

| Marketplace skill | Plugin twin | Eval |
|---|---|---|
| `crafting-skills` | `superpowers:writing-skills` | craft-create, craft-review |
| `ingesting-skills` | `superpowers:writing-skills` (overlapping scope) | ingest-1, ingest-2 |
| `marketplace-validator` | `taches-principled-light:skill-authoring` | lint-2 |

## Recommended action updates

The iter-3.1 plan (in DISCOVERY-INVESTIGATION.md) is updated as follows:

1. **Re-run `plan-multi` and `task-small`** — these are proxy errors,
   not marketplace failures. Need clean runs before judging
   `plan-lifecycle` and `task-lifecycle`.

2. **Investigate `research` deep-research invocation** — the agent
   called the skill but got no useful output. Is the skill broken?
   Does the invocation require specific arguments?

3. **Test per-skill `--add-dir` for `crafting-skills`** — if the agent
   picks `crafting-skills` (marketplace) over `superpowers:writing-skills`
   (plugin) when only the marketplace is in scope, H1 is confirmed
   and the fix is catalog-priority, not description rewrites.

4. **Test per-skill `--add-dir` for `ingesting-skills`** — same logic.
   If the agent picks `ingesting-skills` when only it is in scope,
   the shadowing effect is confirmed.

5. **Description rewrites for `marketplace-validator`** — even though
   the H1 evidence is strongest for `crafting-skills` and
   `ingesting-skills`, `marketplace-validator` was the only lift in
   the corrected report that hit +45. Adding more trigger phrases
   could help `lint-2` surface the skill.

## What this validates

- The corrected iter-3 methodology correctly surfaced these
  distinctions (the original report lumped all 8 neutrals together).
- The Bucket A → sub-bucket A1/A2/A3 split is non-obvious from the
  aggregate numbers alone — it requires transcript inspection.
- The discovery failure hypothesis (H1) is the most likely root cause
  for the 5 true discovery failures, supported by direct evidence
  in `craft-create` (plugin skill chosen over marketplace twin).

## What this does NOT validate

- H2 (descriptions don't surface) — partially supported by `ingest-2`
  reading the wrong file, but only one data point.
- H3 (choice paralysis) — possible but not directly evidenced.
- The 3 proxy-error evals are confounded — they need re-runs before
  any conclusion about the underlying skills (`plan-lifecycle`,
  `task-lifecycle`, `deep-research`) can be drawn.