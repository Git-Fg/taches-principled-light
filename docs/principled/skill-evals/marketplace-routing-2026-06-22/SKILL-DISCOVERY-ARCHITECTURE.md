# Skill Discovery Architecture in Claude Code

Sources: Anthropic docs (`code.claude.com/docs/en/skills`, `code.claude.com/docs/en/settings`, `code.claude.com/docs/en/plugin-marketplaces`), cross-referenced with the iter-2/iter-3/iter-3.1 behavior eval transcripts.

This note documents **how Claude Code actually discovers skills at runtime**, because that determines what the iter-3 evaluation is and isn't measuring. The iter-3 REPORT does not state this explicitly; future iterations should treat this note as the architectural reference.

## The 5 skill locations

Claude Code loads skills from 5 places per turn. Order matters for name conflicts; **all five contribute to the prompt-time skill listing**.

| # | Location | Path | Source of truth |
|---|----------|------|----------------|
| 1 | **Bundled** | bundled with Claude Code binary | Anthropic |
| 2 | **Enterprise** | managed settings | Anthropic |
| 3 | **Personal** | `~/.claude/skills/<name>/SKILL.md` | user |
| 4 | **Project** | `.claude/skills/<name>/SKILL.md` (cwd and parents) | repo |
| 5 | **Plugin** | `<plugin>/skills/<name>/SKILL.md` (from installed plugins) | installed plugin |
| 6 | **`--add-dir` exception** | `.claude/skills/` inside any `--add-dir` directory | runtime flag |

Plugin skills are namespaced as `plugin-name:skill-name` and cannot conflict with other levels. Non-plugin skills at any level override bundled skills with the same name. The precedence between non-plugin levels is: **enterprise > personal > project** (a skill at any non-plugin level also overrides a bundled skill).

## What `--add-dir` actually does

From the docs:

> The `--add-dir` flag and `/add-dir` command grant file access rather than configuration discovery, but skills are an exception: `.claude/skills/` within an added directory is loaded automatically. This exception applies only to `--add-dir` and `/add-dir`. The `permissions.additionalDirectories` setting in `settings.json` grants file access only and does not load skills.

Critical consequences:

- `--add-dir` does **not** auto-load `SKILL.md` files from `<dir>/skills/` or `<dir>/.agents/skills/`.
- `--add-dir` does **not** auto-load plugin manifests (`<dir>/.claude-plugin/plugin.json`) or marketplace entries.
- The only `.claude/` configuration loaded from `--add-dir` is `.claude/skills/`.
- Other directories (`commands/`, `output-styles/`, etc.) inside `--add-dir` are not loaded.

## The marketplace skill-loading path

The `taches-principled-light` marketplace ships 31 SKILL.md files in two locations:

- `skills/` (26 top-level consumer-facing skills)
- `.agents/skills/` (5 meta-marketplace skills: marketplace-validator, marketplace-health, ingesting-skills, releasing-marketplace, evaluating-skills)

**Neither of these is under `.claude/skills/`.** So the marketplace skills can be loaded into Claude Code only via:

1. **Plugin installation** — `marketplace.json` → `plugins[].skills` declares the paths; Claude Code reads those paths and injects them into the skill listing under the plugin namespace.
2. **Manual Read** — the agent uses the Read tool to fetch a `SKILL.md` file directly because the directory was added via `--add-dir`.
3. **Manual Symlink** — the user symlinks `skills/` into `~/.claude/skills/` or `.claude/skills/` (not a supported workflow but a possible workaround).

In production (user installs the marketplace plugin), path 1 is what happens. In the iter-3 evaluation harness, **only path 2 is exercised**: the agent has `Read` access to the marketplace root via `--add-dir`, and whether it consults the SKILL.md files is a behavioral variable.

## What iter-3 actually measures

iter-3 runs `claude --print --output-format stream-json --model haiku --add-dir <REPO>` with the utterance as stdin prompt. The `--add-dir <REPO>` gives the agent file-system access to the entire marketplace tree, but does **not** inject marketplace skills into the skill listing.

**CORRECTION (2026-06-23):** the iter-3.1 transcripts revealed that `--add-dir <REPO>` does NOT isolate the skill listing. All installed plugins load their skills into the system prompt's `slash_commands` array **regardless of cwd**. iter-3.1 evidence: even the `without_skill` config (cwd=`/tmp/empty-claude-project`) shows the same `taches-principled-light:skill-authoring`, `superpowers:writing-skills`, etc. in `slash_commands` as the with-skill configs. The marketplace plugin is globally enabled via the user's normal plugin setup, not loaded per-directory.

Therefore iter-3 measures:

- **with-skill config**: agent has `Read` access to marketplace SKILL.md files (via cwd pointing at REPO) AND has all installed plugin skills in the slash_commands listing.
- **without_skill config**: agent has `Read` access only to an empty project directory (cwd=`/tmp/empty-claude-project`), but **still has the same slash_commands listing** — the marketplace plugin is global.

This is a critical eval-harness flaw: **the without_skill baseline is contaminated**. Both configs have the same marketplace + superpowers skills in their listing; they differ only in whether the agent can `Read` the actual SKILL.md files in the cwd.

iter-3 results therefore measure **the marginal lift of `Read`-driven discovery given that plugin-listing-driven discovery is already in scope**. The "+8.69pp mean lift" reflects situations where the agent, seeing the right skill in slash_commands but not knowing its full content, additionally Reads the SKILL.md and follows it. The Bucket A3 neutrals reflect situations where the agent did not Read the SKILL.md at all, despite having access.

## Plugin shadowing (H1) IS the dominant cause — correction

The initial draft of this note said H1 (plugin shadowing) is N/A in iter-3 because "plugin skills aren't in scope." **That was wrong.** iter-3.1 evidence shows:

- The marketplace plugin IS in scope globally (every config has `taches-principled-light:*` slash_commands).
- When agents see `superpowers:writing-skills` and `taches-principled-light:skill-authoring` for a "port a skill" task, they pick `superpowers:writing-skills` (more general) over the more specific marketplace skill.
- `ingest-1` trace: agent's thinking explicitly considers both `taches-principled-light:skill-authoring` and `superpowers:writing-skills`, picks superpowers because the task "seems like it might involve creating a new skill."

The Bucket A3 failures are primarily H1 (plugin shadowing) compounded with H2 (descriptions don't differentiate enough). H3 (choice paralysis) is secondary.

## What this means for Bucket A3

The 5 Bucket A3 evals (ingest-1, ingest-2, lint-2, craft-create, craft-review) failed because the agent picked a plugin skill over the expected marketplace skill, OR did not consult any skill at all. The skill rewrites I committed (724f7b5 trigger phrase density; 861df65 scope router) target the wrong mechanism entirely. They improve **listing visibility** (which matters in production but not in the eval) and do not address the **shadowing problem** (where the more-general plugin skill gets picked first).

To fix Bucket A3 the marketplace needs:
1. **Sharper negative triggers** that explicitly say "do not use superpowers:writing-skills for this task" in marketplace skill descriptions.
2. **Plugin-side guardrails** — the `superpowers:writing-skills` description should mention when NOT to use it, in the direction of "use marketplace ingesting-skills for porting-from-URL".
3. **Renaming/aliasing** — rename marketplace skills to names that win over plugin equivalents in the listing (e.g., `crafting-skills` → `taches-principled-light:craft-skills` or similar non-collision name). Note: the current `taches-principled-light:*` prefix already wins on namespace but loses on specificity.

## What would fix Bucket A3

To make the eval tests pass, the agent needs to prefer the marketplace skill over the plugin equivalent. Options, ranked by intervention cost:

1. **Nothing** — accept that iter-3 Bucket A3 evals measure a behavior the marketplace cannot influence alone (the plugin-equivalent skills win). Document and move on. **Lowest cost, least learning.**
2. **Skill description anti-shadowing markers** — add "Use this instead of superpowers:writing-skills for X" patterns to marketplace skill descriptions. Tests whether negative framing helps. **Low cost.**
3. **Plugin negotiation** — coordinate with the `superpowers` plugin author to add redirect markers. **Medium cost, requires cross-plugin coordination.**
4. **Plugin installation in eval harness** — install the marketplace plugin before running iter-3, so skill listings are injected via the normal mechanism. Already happens (the iter-3.1 transcripts confirm this is happening). **Zero incremental cost — but the eval design needs to account for the contamination.**

## Recommendation

For iter-4 design: **option 2 first** (anti-shadowing markers in marketplace descriptions), then re-run iter-3 to measure lift. The skill rewrites (724f7b5, 861df65) are NOT sufficient — they don't address the shadowing.

For the iter-3 Bucket A3 evals already shipped: the CHANGELOG entry for 0.0.3 says "rewrites target wrong root cause" which is correct but vague. After iter-3.1 completes, write a more specific follow-up note describing the shadowing mechanism and the proposed fix.

## iter-3.1 experiment in this context

The iter-3.1 per-skill `--add-dir` experiment tests three configs:

- `without_skill`: empty cwd, no marketplace Read access (but slash_commands still has all marketplace skills)
- `with_full_marketplace`: cwd=REPO, full marketplace Read access AND slash_commands has marketplace skills
- `with_skill_only`: cwd=specific skill directory, only that skill Read access AND slash_commands has marketplace skills

Given the discovery architecture above, the predictions are:

- All three configs should have access to the SAME marketplace + superpowers slash_commands (the cwd does not affect slash_commands).
- The configs differ only in whether the agent can Read specific SKILL.md files from cwd.
- The lift from with_skill_only → with_full_marketplace should be **zero** (same slash_commands, same plugin shadowing) unless the marketplace has hundreds of redundant skills causing choice paralysis.
- The lift from without_skill → with_skill should reflect Read-driven discovery — does the agent actually Read a SKILL.md file when given the chance?

iter-3.1 evidence (partial, ingest-1 only):

| Config | Skill tool calls | Read tool calls | Outcome |
|--------|------------------|-----------------|---------|
| without_skill | 0 | 0 | Just text "I need the URL" |
| with_full_marketplace | 0 | 0 | Just text "I need the URL" |
| with_skill_only | 0 | 0 | Just text "I need the URL" |

All three configs are **behaviorally identical** for ingest-1: the agent doesn't consult any marketplace skill. This is a routing-heuristic failure, not a discovery failure. The agent's prompt-time reasoning doesn't say "I should consult a marketplace skill before responding to a porting-from-URL task."

The fix is not in the skill descriptions — it's in the agent's general routing heuristic, which is trained upstream by Anthropic and not modifiable from the marketplace.

## References

- Skills: <https://code.claude.com/docs/en/skills>
- Settings (skill scopes): <https://code.claude.com/docs/en/settings>
- Plugin marketplaces: <https://code.claude.com/docs/en/plugin-marketplaces>
- Model-Harness-Fit (Bustamante 2026): <https://www.nicolasbustamante.com/blog/model-harness-fit> — independent analysis of how harness conventions become part of the model's behavior

## Doc version

v1.1 — 2026-06-23. **Corrected** after iter-3.1 transcript inspection revealed that plugin skills ARE in scope globally (the `--add-dir` mechanism only controls cwd and file access, not skill listing). Original v1 (same date) incorrectly claimed H1 (plugin shadowing) was N/A in iter-3. The corrected analysis: H1 IS active and is the dominant cause of Bucket A3 failures.

## Changelog

- **v1.1 (2026-06-23)**: corrected after iter-3.1 partial transcript inspection. H1 (plugin shadowing) IS active because all installed plugins load into slash_commands globally. Without_skill baseline is contaminated — it has the same slash_commands as with_skill. iter-3 measures marginal lift of Read-driven discovery given listing-driven discovery is already in scope.
- **v1 (2026-06-23)**: initial draft. Incorrectly claimed H1 was N/A.