# Query Shaping

The five-movement loop calls for reformulation. This file is a reference of the concrete shapes your reformulation should produce.

## The four canonical shapes

For any non-trivial query, write it in four distinct shapes before searching:

| Shape | Purpose | Example (for "latest Python web framework recommendations in 2026") |
|-------|---------|-------------------------------------------------------------------|
| **Narrow** | Lock onto the specific thing the user named | `"Python web framework" 2026 benchmark` |
| **Broad** | Map the landscape; let the search engine help disambiguate | `best Python web frameworks 2026` |
| **Domain-specific** | Anchor to a known authoritative source class | `Django vs FastAPI vs Litestar site:news.ycombinator.com` |
| **Identifier-rich** | Include a likely primary-source identifier (year, version, name) | `PEP 1234 web framework 2026` |

If the four shapes return the same first result, you have anchored; pivot. If they return genuinely different results, the question has real sub-questions — answer the sub-questions, not the headline.

## Reformulation patterns

When the broad query returns noise, swap ONE term at a time:

- **Synonym swap**: `framework` → `library` → `toolkit` → `stack`
- **Domain shift**: `web framework` → `HTTP server` → `ASGI` → `WSGI`
- **Temporal shift**: add a year; remove a year; add a half-decade
- **Audience shift**: `Python web framework for production` vs `Python web framework for prototypes`
- **Constraint shift**: `Python web framework` → `async Python web framework` → `typed Python web framework`

Two pivots usually surface a useful variant. Three pivots means the question is malformed; clarify.

## When to use `site:`

Prefer `site:` when you know the authoritative domain for the claim type:

- **Regulations**: regulator's official site (e.g. `site:fda.gov`)
- **Standards**: the standards body's site (e.g. `site:ietf.org`)
- **Internal company practice**: the company's own engineering blog or docs
- **Code libraries**: the official docs domain
- **News**: established outlets with editorial standards

Do NOT use `site:` to "filter for trustworthy sources" — it filters for a domain, not for trust. A site:github.com search can return hobbyist code; a site:reddit.com search can return authoritative threads. Use site: as a disambiguator, not a quality filter.

## Query templates

For factual claims:
```
"<exact claim as user wrote it>"  <likely year or version>  <likely primary source identifier>
```

For current-data questions:
```
<topic>  <most recent year>  <known authoritative domain>
```

For "is X true" verification:
```
<exact claim>  site:<known authoritative domain>
<exact claim>  criticism  OR  rebuttal
```

For comparison questions:
```
<A> vs <B>  <year>  benchmark OR comparison
<A> <B>  differences  site:<authoritative domain>
```

## Anti-patterns

- **Don't paraphrase the user's question.** If the user wrote `"X-Foo error code 47"`, search for that exact phrase.
- **Don't add constraints the user didn't ask for.** `"Python web framework"` not `"type-safe async Python web framework"` unless they specified.
- **Don't double-quote.** `"the" "best" "framework"` is not a search query.
- **Don't paste an entire question into the search bar.** Extract the load-bearing claim(s) and search for those.
