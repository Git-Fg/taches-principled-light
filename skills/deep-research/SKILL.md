---
name: deep-research
description: "Load when a research question needs a sourced long-form answer with citations. Use when the user asks for 'deep research', 'research report', 'sourced answer', 'evidence-backed investigation', '调研报告', 'literature review', 'background research', 'long-form answer with sources', or 'primary sources'. Do NOT use for one-line lookups, code reading, or project work in the current repo."
when_to_use: |
  Run the five-step pipeline for any research question that needs primary
  sources, independent verification, and cited output written to
  `docs/principled/research/<slug>/`. NOT for one-line lookups, code reading, or repo work.
argument-hint: "[research question]"
allowed-tools: Read, Write, Bash, WebSearch
license: MIT
---

# Deep Research

Run the complete five-step pipeline below and write every artifact to a
per-question directory. The model acts as the orchestrator; subagents are
spawned only where the source notes say `parallel: true`.

## Pipeline (always run all 5 steps in order)

1. **Background search** → `background.md`
2. **Direction judgment** → `judgment.md`
3. **Deep analysis** → `analysis.md` and `research_plan.md`
4. **Deep research** → `document.md`
5. **Final writing** → `final.md`

Do not skip steps. Do not collapse the pipeline. Each step's input is the
previous step's output.

## Output layout

```
docs/principled/research/
  <slug>/                         # kebab-case of the question, ≤ 60 chars
    question.md                   # verbatim user question
    conversations.md              # optional, only for follow-up turns
    background.md                 # step 1
    judgment.md                   # step 2
    analysis.md                   # step 3
    research_plan.md              # step 3
    document.md                   # step 4
    final.md                      # step 5 — the user-facing answer
```

Create the directory with `mkdir -p docs/principled/research/<slug>` at the start of step 1.

## Step 1 — Background Search → background.md

- Run 3–6 broad web-search queries covering different angles of the question.
- Pull the top 5–8 results with a web-fetch or page-extraction tool and skim the first 2–3 paragraphs each.
- Write `background.md` with:
  - **Question restatement** (one paragraph)
  - **Key terms and disambiguation** (bullet list)
  - **Top sources** (table: `Title | URL | Author | Date | 1-line takeaway`)
  - **Open threads** (what the searches did NOT answer yet)

## Step 2 — Direction Judgment → judgment.md

- Re-read `background.md`.
- Decide the **research angle**: which subset of the question is most worth
  going deep on, given the user's stated intent.
- Write `judgment.md` with:
  - **Chosen angle** (one sentence)
  - **Why this angle over alternatives** (2–3 bullets)
  - **Hypothesis to validate or refute** (one paragraph)
  - **Out of scope** (what we are explicitly NOT covering)

## Step 3 — Deep Analysis → analysis.md + research_plan.md

- Decompose the angle into 4–8 sub-questions.
- For each sub-question, note: what we already know from `background.md`,
  what we still need to find, which queries will surface it, which sources
  to prioritize.
- Identify the sub-questions that can be researched in parallel (label
  `parallel: true`) vs sequentially (label `parallel: false`).
- Write `analysis.md` with the full sub-question table.
- Write `research_plan.md` with the same table plus a per-step task list
  ready to be executed in step 4.

## Step 4 — Deep Research → document.md

- Execute `research_plan.md` step by step.
- For each sub-question: 2–4 web-search queries, 2–3 page fetches,
  save the key fact under a `## <sub-question title>` heading in
  `document.md` with `[source](url)` citations.
- After each sub-question, write a 1-sentence **interim verdict** at the
  end of its section.
- When all sub-questions are done, add a final section `## Synthesis`
  with the cross-cutting answer (3–5 paragraphs) and a numbered list of
  `## Open questions` (things that would need a primary source or an
  experiment to settle).

If `analysis.md` marks sub-questions as `parallel: true`, you may use your
runtime's native subagent tooling to dispatch them concurrently; merge the
results back into `document.md` under the same section headings.

## Step 5 — Final Writing → final.md

- Read `background.md`, `judgment.md`, `analysis.md`, `document.md` in order.
- Write `final.md` as the user-facing report. Structure:
  - **TL;DR** (3–6 bullets, no fluff)
  - **Body** (one H2 per angle / sub-question, with `[source: title](url)`
    inline citations at the end of every paragraph that uses a fact)
  - **What this does NOT settle** (numbered, links to `document.md`
    `Open questions`)
  - **References** (deduped, ordered by first mention in the body)
- Re-read `final.md` end-to-end once. Remove any sentence that does not
  earn its place.

## Follow-up turns (optional)

If the user asks a follow-up, append the new question to
`docs/principled/research/<slug>/conversations.md` and rerun all five steps, but reuse the
existing `background.md` / `judgment.md` as the starting point and
emphasize the *delta* in `final.md`.

## Quality bar (self-check before declaring done)

- `final.md` has a TL;DR with 3+ bullets, each backed by at least one
  citation.
- Every body paragraph that states a fact ends with `[source: title](url)`.
- The "What this does NOT settle" section is non-empty.
- `references` section deduplicates sources and orders them by first
  mention in the body.
- No paragraph in `final.md` is longer than 6 lines; long arguments get
  broken into bullet lists.
- No "as an AI" / "in conclusion" / "ultimately" filler.

## When to stop

Stop after step 5 only. Do not re-loop, do not add a verify/rewrite gate, do
not generate best-of-N candidates. The user can re-ask if they want a
revision.
