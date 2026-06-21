# Verification Protocol

Three gates to run before quoting a non-trivial claim. The goal is not to make you slow — it is to make the rare load-bearing claim land correctly.

## Gate 1: Primary exists?

Is there a first-party source for this claim?

| If... | Then... |
|-------|---------|
| Yes, and the primary directly states the claim | Cite the primary. Your answer is grounded. |
| Yes, but the primary is paywalled, behind a login, or otherwise inaccessible | Cite what you can see (abstract, summary, citation); note the access limit. |
| No first-party source exists for this kind of claim | The claim is in the "secondary" or "tertiary" tier; verify it via the next gate instead. |
| No first-party source CAN exist (the claim is speculative, about the future, etc.) | Stop searching. Tell the user the question does not have an answer on the open web. |

Examples:
- "Is the boiling point of water 100°C at sea level?" — Primary: any chemistry textbook or NIST database. The gate passes trivially.
- "Did Anthropic release Claude M2.7 in January 2026?" — Primary: Anthropic's own release notes or press. Find it.
- "Will AI replace radiologists by 2030?" — No first-party source CAN exist for a future prediction. The gate is "no". Stop.

## Gate 2: Independent witness?

Can you find at least one source with no shared citation chain that makes the same claim?

- **Same dataset, different analysis**: if two organizations both analyzed the same data, that is one witness, not two.
- **Same primary, two secondaries**: the two secondaries are NOT independent if they both quote the primary.
- **Different geographies**: a US source and a UK source on a global event may be independent if they have separate reporting.
- **Different authors, different funders, different outlets**: this is the strong form of independence.

When the gate fails:
- A claim that has only one source is a hypothesis, not a fact. Cite it as "according to X" rather than as fact.
- If you cannot find an independent witness for a numeric or attribution claim, flag the claim as unverified in your answer.

## Gate 3: Dissent on the record?

If reputable sources disagree, your answer must surface that disagreement.

Steps:
1. Search for the claim + "criticism", "rebuttal", "limitations", "dispute".
2. Look for the strongest version of the counter-argument.
3. If found, the answer is not "X is true" but "X is true per A; B disagrees because Y."
4. If the dissent is from a source with low domain credibility, note that too — but do not hide it.

When the gate fails (you cannot find dissent):
- That is informative. The absence of dissent is not the same as the presence of consensus. Note the absence.

## The four independence tests

When judging whether two sources are independent witnesses, apply these four tests:

1. **Different funding**: paid for by different parties.
2. **Different authorship**: not the same person or research group.
3. **Different outlet**: not the same publication, blog, or platform.
4. **No shared citation chain**: neither source's argument depends on the other.

Two sources that fail any one of these are not independent. The bar is "passes all four".

## Echo-chamber detection

If every source you find cites the same upstream — the same paper, the same primary, the same "according to" chain — you are in an echo chamber. The answer feels robust but is actually a single claim re-stated by re-packagers.

To break out:
- Search in a different language.
- Search on a domain outside the obvious one (e.g. for a US tech claim, search EU and Asian sources).
- Search for the original author of the primary source and read their OTHER work for context.
- Look for the dissent explicitly, even if you think there isn't any.

## "Where is the dissent?"

This is the one search every verification-protocol run should include. The phrasing matters:

```
<claim>  criticism
<claim>  rebuttal
<claim>  limitations
<claim>  "is wrong" OR "is misleading"
```

If you cannot find dissent after these four searches, you have either found a robust consensus (rare) or you are in an echo chamber (common). State which.

## Speed budgets

- **Low-stakes, routine question**: skip the gates. Answer from search results with citations. This is the 80% case.
- **Medium-stakes** (claim that affects a decision, a recommendation): gate 1 only.
- **High-stakes** (claim that affects someone's money, health, career, or legal position): all three gates.

Match gate count to claim weight. Do not over-verify trivial claims; do not under-verify load-bearing ones.
