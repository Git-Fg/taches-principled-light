# Iter-3 Discovery Investigation (post-correction, June 2026)

**Status**: Notes for iter-3.1. Generated after the corrected iter-3
report (commit `dabe1bc`) which found that the 3 `skill_hurts` were
artifacts of the consultation assertion bug, and that the real
binding constraint is **skill discovery, not skill content**.

## The corrected root cause (from F1/F2 revised)

After fixing the consultation bug (grader.py commit `b45c40a`) and
re-running iter-3, the pattern is clear: the marketplace skills are
well-authored (when consulted, they lift 15-45pp), but **the
with-skill agent often doesn't read the marketplace skill at all**.

Evidence from the with-skill transcripts of the 8 Bucket A evals:

| Eval | with-skill reads | with-skill skill calls | Outcome |
|---|---|---|---|
| ingest-1 | 0 | 0 | 0/0 neutral (agent did nothing) |
| ingest-2 | 1 (wrong file: `.claude-plugin/marketplace.json`) | 0 | 0/0 neutral |
| lint-2 | 0 | 0 | 0/0 neutral |
| craft-create | (assumed 0) | (assumed 0) | 0/0 neutral |
| craft-review | (assumed 0) | (assumed 0) | 0/0 neutral |
| plan-multi | (assumed 0) | (assumed 0) | 0/0 neutral |
| research | (assumed 0) | (assumed 0) | 0/0 neutral |
| task-small | (assumed 0) | (assumed 0) | 0/0 neutral |

And the one Bucket A success (lint-1):

| Eval | with-skill reads | Outcome |
|---|---|---|
| lint-1 | 3 (marketplace-health, marketplace-validator, health report) | **+45pp lift** |

The agent read 3 marketplace skills for lint-1 and ran the validator.
For the 8 Bucket A failures, the agent read 0 (or 1 wrong file) and
produced no useful work.

## Why this matters

The skill rewrites committed in `861df65` (ingesting-skills scope router,
marketplace-validator scope router) target the wrong root cause. They
improve the skill's internal structure but don't help if the agent
doesn't read the skill in the first place.

That said, the rewrites are still useful improvements:
- The marketplace-validator scope router explicitly routes pre-commit
  utterances to crafting-skills, which is the right answer
- The ingesting-skills scope router gives the agent a quick-port path
  for short utterances, which is the right answer for fast porting

So: KEEP the rewrites (they're still improvements), but **don't expect
them to fix the 8 Bucket A neutrals** — those need a discovery fix.

## Why the discovery fails (hypotheses, ordered by likelihood)

### H1. Marketplace catalog shadowed by plugin skills

The agent's discovery path has TWO competing skill catalogs:
1. The marketplace (26 skills in `skills/` + 4 in `.agents/skills/`)
2. The plugin skills (`superpowers:writing-skills`,
   `taches-principled-light:skill-authoring`, etc.)

The plugin skills are advertised in the slash_commands list of the
agent's system prompt (visible in the transcript's `init` event). The
marketplace skills are advertised via `--add-dir` and only surface if
the agent actively scans them.

For `ingest-1` (utterance: "port this skill from a github url into our
collection"), the agent's plausible routing paths are:
- `superpowers:writing-skills` (plugin, always visible) — handles
  general writing/authoring tasks
- `ingesting-skills` (marketplace, requires --add-dir scan) — handles
  porting from external sources
- `taches-principled-light:skill-authoring` (plugin) — handles skill
  authoring

The agent picked `superpowers:writing-skills` because it was visible
in the slash_commands list. It didn't scan the marketplace directory
to discover `ingesting-skills`.

### H2. Marketplace skill descriptions don't surface in agent's discovery

Even if the agent scans the marketplace directory, it might not pick
the right skill. Per Anthropic best practices, descriptions should
include 5-10 trigger phrases that match how users actually phrase
requests. The current descriptions are concise (46-79 words) but
may not have enough trigger diversity to surface in all discovery
patterns.

### H3. With-skill config adds 26 extra skills → distraction

When the agent has 26 marketplace skills + ~20 plugin skills in scope,
the choice paralysis may cause the agent to either:
- Pick a generic plugin skill (e.g., `superpowers:writing-skills`)
- Do nothing and ask for clarification
- Try multiple skills and produce no useful output

This is consistent with the pattern: Bucket A evals often have the
with-skill agent producing very short responses ("I don't see a URL…")
while the without-skill agent picks a plugin skill and does something
useful (if suboptimal).

## Recommended actions (ordered by likelihood of fixing discovery)

1. **Audit the with-skill config's `--add-dir` behavior**. Does the
   marketplace skills surface in the agent's system prompt, or does
   the agent need to actively scan the directory? If the latter, the
   discovery path is unreliable.

2. **Test with `--add-dir` on a per-skill basis**. Run the iter-3
   eval with the marketplace loaded BUT only one skill visible at a
   time. If lifts appear for `ingest-1` when only `ingesting-skills`
   is visible, the issue is choice paralysis from 26 skills, not
   skill content.

3. **Increase trigger phrase density** in the skill descriptions.
   Per Microsoft best practices, 5-10 trigger phrases per topic. The
   current descriptions have 3-5 trigger phrases. More would help.

4. **Add a "routing decision table" to each marketplace skill's
   description** — explicit "USE THIS for X, USE SIBLING for Y"
   clauses that make the routing boundary unambiguous. This is what
   the scope routers in commit `861df65` started doing but they need
   to be more explicit.

5. **Consider a meta-skill**: a `marketplace-router` skill that
   explicitly takes the user's utterance and routes to the right
   marketplace skill. This is an architectural change, not a content
   fix, and is deferred to iter-3.2.

## Recommended action for the rewrites in commit 861df65

KEEP the rewrites. They improve skill structure even if they don't
fix discovery. After iter-3.1 discovery investigation, decide whether
to enhance the rewrites with stronger trigger phrases and routing
tables (per action #3 and #4 above).

## Next steps

The iter-3.1 plan (per the corrected REPORT.md) includes:
- Sample-inspect 8 Bucket A transcripts in detail (action #1)
- Re-run with per-skill --add-dir to isolate choice-paralysis effect
  (action #2)
- Increase trigger phrase density across marketplace skills (action #3)
- Re-run iter-3 with new descriptions to verify the discovery fix
  improves Bucket A evals

This investigation is necessary BEFORE additional skill rewrites, since
further rewrites targeting content (per the original F1/F2 hypothesis)
will not improve discovery outcomes.