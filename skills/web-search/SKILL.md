---
name: web-search
description: >
  Load when finding or verifying information on the open web — web search,
  fact-checking, source evaluation, or claim verification. Use when the user
  says 'find X on the web', 'look up Y', 'is this claim true', 'verify this
  statement', or 'fact-check'. Do NOT use for reading the local codebase (use
  a subagent explorer), deep source traversal (use a subagent explorer), or
  evaluating competing design alternatives (use solving-competitively).
when_to_use: |
  Use when the user asks to find, look up, verify, fact-check, or research
  on the open web, or doubts a factual claim. Tool-agnostic — teaches the
  discipline of search, not which tool. NOT for code/local-file search, DB
  queries, or private systems.
argument-hint: "[claim, question, or proposition to evaluate]"
---

# Web Search

## What This Skill Changes

**Default behavior:** the model treats "is this true?" or "find X" as a **retrieval task** — search, summarize the top results, answer. It quotes whatever the first page says, treats Wikipedia and a Reddit thread as roughly equivalent sources, and confidently reports a consensus that may not exist.

**With this skill:** the model treats the same question as an **epistemological task**. Search is iterative reformulation under verification, not a one-shot query. The agent inspects results before quoting them, prefers primary sources over aggregators, asks one clarifying question when stakes are high or the question is ambiguous, surfaces disagreement rather than collapsing it, and admits when the answer is unfindable on the open web.

## Decision Router

| If the user is... | Apply... |
|-------------------|----------|
| Asking to verify a specific factual claim (number, quote, attribution) | **Verify** — find primary source, cross-check one independent witness, flag if cannot confirm |
| Asking for current data or a comparison across sources | **Triangulate** — three independent sources, surface where they disagree |
| Asking a vague or multi-clause question with high stakes | **Clarify** — one precise question before searching, then proceed |
| Asking a routine "find me X" / "what's the latest Y" | **Default** — reformulate, search, summarize, cite |
| Asking a question whose answer the model can derive from internal knowledge without verification | **Re-route** — do NOT search; answer from training knowledge and note the source class |

## Core Principle

Web search is iterative reformulation under verification, not a one-shot query. The default failure is **anchor + paraphrase** — the model anchors on whatever the first page returns and paraphrases it confidently. The discipline of search is to (a) formulate queries that resist anchoring, (b) read results before quoting them, (c) prefer primary over secondary sources, and (d) surface disagreement rather than collapse it.

## The 5-Movement Loop

When the default path (anchor + paraphrase) is not enough — i.e. when stakes are non-trivial or the user explicitly wants depth — work in five movements:

1. **Frame** — restate the question in your own words. Identify the claim(s) that need verification vs the background context that does not. Decide which sources would count as primary.
2. **Reformulate** — write the query in 3-4 distinct shapes: a narrow version, a broad version, a domain-specific version, and one that includes a likely primary-source identifier (year, name, paper title, official URL fragment).
3. **Inspect** — for each result, before reading the content, ask: who published this, when, with what funding or motive? Is the headline consistent with the body? Does the page cite its own sources?
4. **Cross-reference** — never quote a single source for a non-trivial claim. For numeric or attribution claims, find at least one independent witness. For contested claims, find both sides.
5. **Stop or surface** — either answer with cited sources and a one-line note on confidence, OR admit the answer is unfindable on the open web. Never manufacture consensus by averaging disagreeing sources.

## The 7 Principles

1. **Primary beats secondary** — a peer-reviewed paper, an official report, or a first-party post beats a Wikipedia summary or a news article that quotes it.
2. **Recency matters when recency matters** — for time-sensitive claims (latest model release, current regulations, recent events), prefer pages dated in the relevant window. For timeless claims, recency is irrelevant.
3. **Disagreement is signal, not noise** — if two reputable sources disagree, surface the disagreement and the reason. Do not average.
4. **Authority is a function of the claim** — a senior engineer's blog is a great source on internal architecture, a poor source on epidemiology. Match source to claim.
5. **Funding and motive are not bias, they are context** — a pharmaceutical company's study is data, not proof. Read it; weight accordingly.
6. **"The first result" is a sample of one** — search engines optimize for engagement, not for truth. The first result is the most clicked, not the most correct.
7. **When the answer is unfindable, say so** — the worst output is a confident answer to a question that does not have a confident answer on the open web.

## Query Shaping

- **Broad → narrow funnel**: start broad enough to map the landscape, then narrow once you have named the actual question.
- **Use specific identifiers**: dates ("2024 Q3"), names ("RFC 9293"), versions ("Python 3.12"), product codes — these disambiguate fast.
- **Quote exact phrases when the user did**: if the user wrote "X-Foo error code 47", search for that exact phrase. Do not paraphrase the user's query.
- **Domain anchor when it helps**: prefer `site:` to get first-party content when you know the authoritative domain (e.g. a regulator's site for a regulation question).
- **Pivot on a single token**: if the broad query returns noise, swap one term (synonym, related concept) and try again. Two pivots usually surface a useful variant.
- **Read the search engine's own suggestions**: the "People also ask" and related-search blocks are a free source of reformulations.

Detailed examples: `references/query-shapes.md`.

## Source Hierarchy

| Tier | Source class | Trust posture |
|------|--------------|---------------|
| **Primary** | First-party: original paper, official spec, regulator filing, the person who said the thing | Highest. Read carefully; check the actual claim against the actual source. |
| **Secondary** | Reputable journalism, peer-reviewed surveys, recognized expert analysis | High for context; verify the load-bearing claim against the primary. |
| **Tertiary** | Wikipedia, encyclopedias, textbooks | High for orientation; do not cite as the source of a specific claim. |
| **Aggregator** | Reddit, forums, "top 10" listicles, content farms | Low. Useful for finding primary sources, not for citing. |
| **Sponsored / affiliate** | Anything with a buy button tied to the recommendation | Lowest. Assume the recommendation serves the sponsor. |

Detailed examples and cross-source trust calibration: `references/source-hierarchy.md`.

## Verification Protocol

Before quoting a non-trivial claim, run three gates:

1. **Primary exists?** — Is there a first-party source for this claim? If yes, the answer to "is this true" comes from reading that source, not from a search-engine summary.
2. **Independent witness?** — Can you find at least one source with no shared citation chain that makes the same claim? For a number, that's a second dataset or a different organization's analysis. For an attribution, that's a second outlet that covered the same event.
3. **Dissent on the record?** — If reputable sources disagree, your answer must surface that disagreement. Do not pick a side; do not average.

Detailed protocol with worked examples: `references/verification-protocol.md`.

## When NOT to Search

Sometimes the right answer is to NOT search. Stop and answer from training knowledge (or re-route to a different skill) when:

- The answer is in the conversation already (don't re-search what the user just said).
- The question is about the model's own behavior, design, or capabilities (consult the relevant plugin/skill instead).
- The question requires private or internal context the open web cannot have (the user's codebase, the user's own data).
- The question is speculative about the future ("will X release in 2027") — there is no answer to find.
- The question is value-laden or contested where the open web is mostly noise (taste, ethics in a specific situation).

Detailed: `references/when-not-to-search.md`.

## Gotchas

- Do NOT treat search results as authoritative without source evaluation. Check: authorship, date, corroboration.
- Do NOT search for information already available in the local context or codebase — read locally first.
- Do NOT use web search for evaluating competing design alternatives — use solving-competitively.
- When a claim fails verification, MUST state what was found instead, not just "unverified."
- Do NOT cite search result snippets as facts. Fetch and read the full source before citing.

## Failure Modes

| # | Failure | Symptom | Defense |
|---|---------|---------|---------|
| 1 | Anchor on first result | The first page's framing shapes the whole answer | Reformulate to 3 shapes before committing |
| 2 | Paraphrase without reading | The summary in the search snippet becomes the answer | Open the source; verify the claim against the actual content |
| 3 | Single-source citation | One URL carries a non-trivial claim | Run the 3-gate verification protocol |
| 4 | Wikipedia-as-source | Quoting a tertiary source as if it were primary | Reach through Wikipedia to its citations |
| 5 | Reddit consensus | Treating upvote-driven agreement as evidence | Ask: who benefits? who is the named source? |
| 6 | Stale data | Quoting a number from 2019 in a 2026 context | Check the date on the source; pivot to fresher data |
| 7 | Sponsored rec as fact | A buy-button listicle becomes a recommendation | Distinguish editorial from sponsored; weight the recommendation accordingly |
| 8 | Manufactured consensus | Averaging disagreeing sources into a midpoint | Surface the disagreement, the reason, and the source classes |
| 9 | Echo chamber | Sources all cite the same upstream | Find a source outside the citation chain |
| 10 | False precision | Reporting a number with three decimals | Round to the precision the primary source actually supports |
| 11 | Domain mismatch | Quoting a hobbyist blog as a scientific source | Match source authority to claim type |
| 12 | Translation drift | Quoting a translated source as if it were the original | When possible, cite the original-language source |
| 13 | "According to the internet" | The model itself becomes the source | If the model has no source, say so; never round-trip through itself |
| 14 | Missing the question | Answering a related-but-different question | Restate the question before answering |
| 15 | Over-searching | Burning budget on a question that needs one good source | Match search depth to claim weight |
| 16 | Asking too many clarifying questions | The user wants a search, not an interview | Clarify ONCE, only when stakes are high |
| 17 | False completion | Reporting "found it" when the result doesn't actually address the claim | Quote the relevant sentence; confirm it answers the user's question |

## CONTRAST

NOT for:
- Code search — use the code-search skill or `grep` directly
- Local file search — use the file-search skill
- Database queries — use the data skill
- Private or internal systems (the user's own codebase, internal docs) — the open web cannot have these
- Speculative or value-laden questions where the open web is mostly noise
- Recitation of training knowledge the model already has — search is for what the model does not know

## References

You MUST read `references/query-shapes.md` BEFORE reformulating a non-trivial query.
You MUST read `references/source-hierarchy.md` BEFORE trusting a source's authority.
You MUST read `references/verification-protocol.md` BEFORE quoting a load-bearing claim.
You MUST read `references/when-not-to-search.md` BEFORE searching for a question that may not need searching.
