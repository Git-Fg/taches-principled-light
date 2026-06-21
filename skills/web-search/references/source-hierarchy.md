# Source Hierarchy

Trust is a function of the claim type and the source class. This file is a reference for the trust posture, with cross-source calibration notes.

## The five tiers

### 1. Primary

First-party sources: the original paper, the official spec, the regulator's filing, the person who said the thing.

- Examples: a peer-reviewed paper, an RFC, an FDA approval letter, a company SEC filing, a maintainer's own announcement.
- Trust posture: highest for the specific claim the source is making.
- Required check: read the actual claim against the actual source. A primary source that disagrees with the search snippet is still a primary source.

### 2. Secondary

Reputable journalism, peer-reviewed surveys, recognized expert analysis.

- Examples: NYT/WSJ/FT on a major event, a Nature review article, a respected industry analyst's report.
- Trust posture: high for context and synthesis. Verify load-bearing claims against the primary.
- Required check: who funded the source, who is the named author, and what is their track record on this topic.

### 3. Tertiary

Wikipedia, encyclopedias, textbooks.

- Examples: a Wikipedia article on a programming language, a Britannica entry on a historical event.
- Trust posture: high for orientation, not for citation. The value of tertiary sources is that they cite their primaries.
- Required check: open the references section. If a tertiary source's claim cannot be traced to a primary, do not cite it.

### 4. Aggregator

Reddit, forums, "top 10" listicles, content farms.

- Examples: a Reddit thread, a Hacker News discussion, a "best X of 2026" SEO post.
- Trust posture: low for citation, high for finding primary sources. Use aggregators to surface what the community is paying attention to, then reach through to the primary.
- Required check: who is the named source? If the named source is the original author of a primary, follow the link.

### 5. Sponsored / affiliate

Anything with a buy button tied to the recommendation.

- Examples: "best laptops" posts that link to Amazon, vendor whitepapers, sponsored review units.
- Trust posture: lowest for the recommendation. The recommendation serves the sponsor.
- Required check: distinguish editorial from sponsored. If the source is sponsored, the recommendation is data, not endorsement.

## Cross-source calibration notes

### "Source said X" vs "X is true"

A primary source saying X is a fact about the source, not a fact about X. The source may be wrong, lying, mistaken, or outdated. The discipline is to separate "the source claims X" from "X is true" — and only the latter is what the user is asking about.

### Who paid for this

Funding and motive are not bias, they are context. A pharmaceutical company's study on its own drug is data, not proof; but it is also not automatically false. Read it; weigh it; cite it with the funding context.

### Domain trust calibration

The trust of a source varies by topic:
- A senior engineer's blog is a great source on internal architecture and a poor source on epidemiology.
- A medical journal is a great source on clinical outcomes and a poor source on software engineering practices.
- A government statistics agency is a great source on demographic data and a poor source on subjective user experience.

Match source authority to claim type. Do not cite a source outside its domain of demonstrated competence.

### "Who is the named source?"

When a secondary or tertiary source makes a claim, ask: who is the named source? If the answer is "anonymous", "experts say", "studies show" without a specific citation, do not propagate the claim.

### Time-sensitivity

- **Time-sensitive claims** (current regulations, latest model release, recent events): the source must be dated in the relevant window. A 2022 source on 2024 GPU architectures is stale.
- **Timeless claims** (the boiling point of water, the date of the French Revolution): recency is irrelevant. The oldest authoritative source is fine.

## When sources disagree

When two reputable sources disagree:
1. Check whether they are answering the same question. They may not be.
2. Check the publication date. One may be outdated.
3. Check the source class. One may be out of its domain.
4. Check the funding. One may have a motive.
5. If none of the above resolves it, surface the disagreement to the user. Do not pick a side. Do not average.

## The single most useful question

When in doubt, ask: **"If this claim is wrong, who is the person who would know?"** Then find that person or their direct work.
