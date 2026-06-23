# Hub + Subskills Design — Cross-Agent Compatibility

## Question

The marketplace has one hub-and-spokes pattern: `skills/design-hub/SKILL.md` (hub) with 5 subskills under `skills/design-hub/*/SKILL.md`. The user asked whether this design is optimally compatible with all AI agents, even those that don't natively handle subskill syntax.

## Answer (TL;DR)

The current design **already is** optimally compatible with the [Agent Skills open standard](https://agentskills.io/) (agentskills.io, supported by 27+ AI agents including Claude Code, Cursor, Codex, Gemini CLI, VS Code Copilot). The hub+subskills pattern is a routing aid, not a syntactic requirement — each subskill is a self-contained skill from the agent's perspective.

## Why this works

Per the Agent Skills standard:

> "Agent Skills are a lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows. At its core, a skill is a folder containing a `SKILL.md` file."

The standard defines a **folder structure**, not a routing hierarchy. From the agent's discovery perspective:

1. **At startup, the agent scans all `SKILL.md` files** (recursive by default in Claude Code, Gemini CLI, Cursor, Codex, VS Code Copilot, etc., per the standard).
2. **The agent reads each skill's frontmatter** (`name` + `description`) into a discoverable index.
3. **The agent decides which skill to invoke** based on natural-language matching of the user's request against the descriptions.

In our marketplace:

| Path | What the agent sees |
|---|---|
| `skills/design-hub/SKILL.md` | Skill `design-hub`, description: "Load when the user needs design guidance — palette, typography, tokens, spacing, or visual hierarchy..." |
| `skills/design-hub/pdf-design-guide/SKILL.md` | Skill `pdf-design-guide`, description: "Pick a palette by mood — 10 named moods with WCAG check + anti-patterns..." |
| `skills/design-hub/typography-guide/SKILL.md` | Skill `typography-guide`, description: "Apply professional typography — font pairing, type scale..." |
| ... 3 more subskills | ... |

**All 6 skills (1 hub + 5 subskills) are independently discoverable.** An agent doesn't need to "navigate" the hub to find a subskill. If the user asks "what color should this be?", the agent matches against the descriptions and likely picks `pdf-design-guide` directly. If the user says "I need design help", the agent matches `design-hub` and the hub body says "for palette, read `pdf-design-guide`" — at which point the agent reads the subskill.

## Why this is BETTER than a flat structure

A flat structure (e.g., `skills/pdf-design-guide/SKILL.md` without the `design-hub/` parent) would:
- Lose the **routing table** that the hub provides (a quick-reference map of "user intent → subskill")
- Lose the **workflow order** that the hub documents (pdf-design-guide → design-system-palettes → typography-guide → design-principles → design-good-bad-examples is the recommended pipeline)
- Lose the **companion-skill links** (security, reviewing-and-polishing, browser-automation for screenshot verification)

A flat structure with the hub's content duplicated into each subskill would be redundant and harder to maintain. The hub+subskills pattern keeps the routing info in one place while letting each subskill be fully self-describing.

## What about agents that DON'T do recursive discovery?

Some older or simpler agents might only scan `skills/<name>/SKILL.md` at the top level, missing `skills/<name>/<subskill>/SKILL.md`. For these agents:

1. **They would still see `design-hub`** — the top-level entry is intact.
2. **They would NOT see the 5 subskills** — they're nested one level deeper.
3. **The hub's body has a Decision Router** — when the agent invokes the hub, the body tells it which subskill to read. If the agent can `Read` files at relative paths (most can), it follows the routing table and reads the right subskill.

This degrades gracefully — the agent loses the upfront "see the right subskill first" UX but can still navigate via the hub.

## Compatibility with the marketplace manifests

The 4 plugin manifests (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.kimi-plugin/plugin.json`) currently describe the marketplace as "26 specialist skills" or similar phrasing. The descriptions mention "design-hub (palette/typography/principles)" — implying the hub+subskills structure.

For maximum compatibility, the manifest descriptions could:
- Spell out every leaf explicitly (e.g., "design-hub with pdf-design-guide, design-system-palettes, typography-guide, design-principles, design-good-bad-examples")
- Add a `skills/` field listing every top-level entry

But the current descriptions are sufficient because the marketplace is published via auto-discovery (no per-skill manifest entries needed).

## Recommendation: no structural changes required, but document the contract

The design is already compatible with the Agent Skills standard. The hub's "Decision Router" is a routing aid, not a syntactic requirement. Each subskill is self-contained and independently discoverable.

What we SHOULD add: a one-paragraph note in `skills/design-hub/SKILL.md` explaining that the hub is a **router** and the subskills are the **actual skills**. This makes the design intent explicit to any reader, including future maintainers.

What we should NOT add: a flat mirror directory at the top level (e.g., `skills/pdf-design-guide-flat/SKILL.md` pointing to the nested one). This would:
- Create duplicate discovery entries (the agent sees both `pdf-design-guide` and `pdf-design-guide-flat`)
- Cause routing confusion (which one wins on description overlap?)
- Require maintenance overhead (every change to a subskill would need to be mirrored)

## References

- [Agent Skills open standard](https://agentskills.io/) — folder structure, progressive disclosure, 27+ agent support
- [Claude Code skills docs](https://code.claude.com/docs/en/skills) — `Automatic discovery from parent and nested directories`
- [Claude Agent Skills: A First Principles Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) — prompt-based meta-tool architecture; "There is no algorithmic skill selection or AI-powered intent detection at the code level"
- [SKILL.md: The Agent Skills Format](https://www.mdskills.ai/specs/skill-md) — schema and client compatibility list
- [Agent Skills: The Open Standard for AI Capabilities](https://inference.sh/blog/skills/agent-skills-overview) — "skills.sh lists compatibility with Claude Code, Cursor, ... agentskills/agentskills welcomes input from platform vendors"

## Action items (small)

1. Add a "Hub contract" paragraph to `skills/design-hub/SKILL.md` clarifying the hub-as-router design.
2. Optionally add a `references/leaves.md` file listing every subskill with its description and path, for agents that prefer a flat reference over the body-internal Routing Table.
3. Verify the existing `evaluating-skills` skill follows the same pattern (it has no subskills currently — confirm it stays flat).
