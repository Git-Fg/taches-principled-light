# Shadow-Skill Scaffold

A template for generating one **adversarial shadow skill** to test whether your skill's `description` is specific enough to be distinguishable from a topically-similar but functionally-distinct sibling.

Per AGENTS.md "Description as Routing Signal" rule 6: if your description AND a shadow skill both match the same query set, your description is too vague. The shadow should look like your skill from a keyword distance but do something materially different.

## When to use this

- After running the trigger-eval harness (`scripts/trigger_eval.py score`) and finding trigger_rate on the should_not side above the threshold.
- When your skill shares a thematic cluster with one or more siblings and you want to confirm the description disambiguates.
- Before declaring a new skill shipped, to catch the "two skills both fire" failure mode.

## How to use

1. Copy the **Scaffold prompt** below into your editor LLM (Claude, GPT, etc.).
2. The LLM fills in the scaffold with a real shadow skill definition. Review it — the shadow should be plausible but **functionally distinct** (e.g., yours: "extract a PDF table to CSV"; shadow: "compress a PDF for email").
3. Create a temporary sibling skill directory at `shadow-skills/<shadow-name>/SKILL.md` and copy the generated definition.
4. Run your trigger-eval set again with the shadow present in the discovery path. If the shadow's trigger rate matches yours on the same queries, your description is too vague.

## Scaffold prompt

```
Generate a shadow skill for adversarial description-routing testing.

TARGET SKILL (mine):
- name: <your-skill-name>
- description: <your-skill-description>
- domain: <one-sentence summary of what it does>
- sibling cluster: <list 1-3 sibling skills in the same thematic area>

SHADOW REQUIREMENTS:
1. Topically similar — share 2-3 keywords with the target so a naive keyword
   match would fire on the same queries. The shadow should look like a sibling
   from across the room.
2. Functionally distinct — does something materially different. The shadow
   should solve a real problem, but a different one from the target.
3. Plausible — written well enough that a reviewer would not immediately
   dismiss it as a test artifact. Real skill names, real-sounding domain.
4. Same shape — same frontmatter (name, description, when_to_use,
   argument-hint, allowed-tools, license) so the harness can include it in
   the discovery path identically.

OUTPUT FORMAT (markdown, no commentary):

---
name: <shadow-name>
description: "<one-sentence shadow description, ~30-50 words, topically similar to target but functionally distinct>"
when_to_use: |
  <2-3 lines, same shape as target's when_to_use but for the shadow's domain>
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
license: MIT
---

# <Shadow Name>

<1-paragraph summary of what the shadow does. The shadow is a real, plausible
skill, not a parody. The point is to test whether a routing agent can
distinguish yours from this when the two descriptions share keywords.>
```

## What to look for in the result

After running the trigger-eval set with the shadow present:

| Pattern | Interpretation | Action |
|---|---|---|
| Shadow matches on should_trigger queries at high rate | Your description is **not** specific enough; both fire | Narrow your description; add "Use for X, not Y" framing |
| Shadow matches on should_NOT queries at high rate | The shadow's description is too vague | Less interesting — fix the shadow, not your skill |
| Shadow matches on your should_trigger at low rate | The shadow doesn't compete on your domain | Shadow is not a useful test for this skill |
| Your skill matches on the shadow's should_trigger at high rate | The shadow pulled you into its domain | Consider whether the skills should be merged (see `crafting-skills` Compendium Rule 2 on tightly-coupled clusters) |

## Cleanup

After the test, remove the shadow skill from `shadow-skills/`. The shadow is a test artifact, not a shipped skill. Do not commit it to the marketplace.

## See also

- `references/trigger-eval-guide.md` — full trigger-eval methodology
- AGENTS.md "Description as Routing Signal" rules 6 + 7
- `crafting-skills` Compendium Rule 2 (tightly-coupled-cluster exception)
