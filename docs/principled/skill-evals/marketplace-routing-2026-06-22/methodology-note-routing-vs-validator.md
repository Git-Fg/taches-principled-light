# Routing Test Methodology — Validator vs. Routing Test Tokenization

## Question

The marketplace-validator counts description words with `re.findall(r"\b\w+\b", desc)`. The routing test counts tokens with `re.split(r"\W+", s.lower())` and then filters by `len(t) > 2`. The CHANGELOG `0.0.2` release (commit `9cd1841`) and the post-release fixup (`60de87d`) both used the **validator's** total-word count (e.g., "marketplace-validator 52"). This raises a natural question: are the two methodologies consistent, and which one is the right number to cite for what purpose?

## Empirical comparison

Reproducible via `scripts/count_words.py` (re-run any time the descriptions change). Current numbers (post-`eeaca8b` refactor, all v0.0.2 + the 0.0.2 follow-up batch):

| Skill                  | Validator (`\b\w+\b`) | Routing test (`\W+`, `> 2` chars) | `str.split()` |
|------------------------|----------------------:|----------------------------------:|--------------:|
| `crafting-skills`      |                    53 |                                36 |            52 |
| `test-orchestration`   |                    52 |                                38 |            44 |
| `marketplace-validator`|                    52 |                                38 |            50 |

The validator count and `split()` count are within 2-8 of each other because both count the same kind of token (every word run). The routing test count is systematically lower because it filters out short tokens (`a`, `do`, `is`, `or`, `s`, `t`, etc.).

## What the divergence is (and is not)

- **Apostrophe handling is NOT the divergence.** Both the validator (`\b\w+\b`) and the routing test (`\W+` split) treat apostrophes as word boundaries — so `skill's` becomes 2 tokens in both. (`split()` is the only methodology that preserves the apostrophe inside the token.)
- **The actual divergence is by design:** the routing test intentionally filters out short tokens (`len(t) > 2`) to focus on content words for semantic overlap scoring. The validator counts every word for the "description too long" budget warning.

## Which to use where

- **Validator total word count** (`\b\w+\b`): correct for the "≤50 word target" check and the `description_word_count` validator finding. This is what `parse_frontmatter_safe` consumers should report when they describe description length.
- **Routing test content-word count** (`\W+` split, `> 2`): correct for "how much semantic signal does this description carry for token-overlap routing?" This is the number that the routing test internally uses, and the reason the 5-of-35 pre-fix bug went undetected: short-token filtering made the descriptions look "long enough" even when they were short.
- **`split()`:** the easiest ad-hoc count, but it preserves apostrophes and quotes inside tokens, so it disagrees with both the validator and the routing test on real-world descriptions. Avoid it in documentation; use only for ad-hoc human estimation.

## Implications for CHANGELOG 0.0.2

The CHANGELOG `0.0.2` section cites the **validator** total-word count (52 for marketplace-validator, 53 for crafting-skills, 52 for test-orchestration). This is correct for the description-length framing ("Two skills in `skills/` retained signal qualifiers and ended slightly above the ≤50 target"). The framing "Compendium Rule 3 target ≤50 words" is intentionally validator-based, since Rule 3 is about description-length budget, not about content-word overlap.

If a future CHANGELOG cites "content words" or "routing-relevant tokens", it should use the routing test's count and explicitly name the methodology to avoid confusion with the validator's count.

## Implementation note

The two methodologies could be unified in a future refactor — e.g., add a helper to `marketplace-validator/scripts/validate.py` that exposes `word_count(content=True)` for content-word counts and `word_count(content=False)` for total counts. Today, the divergence is invisible to most readers because the routing test and the validator operate on different files (`routing_test.py` for routing, `validate.py` for description linting). The CHANGELOG should be the single source of truth for "which number did we measure, with which methodology".

## See also

- `iteration-3-design.md` — discusses the same instruction-following vs goal-completion distinction in the context of the Gorinova et al. 2026.
- `scripts/count_words.py` — the reproducible script that produces the empirical comparison table above.
