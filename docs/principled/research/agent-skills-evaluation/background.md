# Question Restatement

How does Anthropic's official `skill-creator` (in `anthropics/skills`) teach and embody skill-evaluation methodology — specifically the loop from `evals.json` → parallel with-skill + baseline runs → grader subagent → `benchmark.json` → HTML reviewer → iterative rewriting → trigger-description optimization — and how can that methodology be distilled into a **generalistic evaluation skill** that works across interactive agents (Claude Code, Cursor) and headless / non-interactive runtimes (CI, `claude -p`, Reasonix, kimi-code), without depending on `webbrowser.open()`, browser displays, or Claude-Code-specific command files?

The constraint is sharper than the official skill assumes: `skill-creator/SKILL.md` is explicit that description optimization (the `run_loop.py` step) requires the `claude` CLI and works in Cowork but skips on Claude.ai. It also assumes a display for the eval viewer, with a `--static` HTML fallback only mentioned for Cowork. A truly generalistic evaluation skill must work when there is **no** agent runtime capable of spawning sub-process agents and **no** browser display — i.e., when the skill itself must grade outputs using only the orchestrator's tools.

# Key Terms and Disambiguation

| Term | Meaning in this research |
|---|---|
| **evals.json** | The canonical Anthropic schema for declaring test cases for a skill: `{skill_name, evals:[{id, prompt, expected_output, files[], expectations[]}]}`. Lives in `evals/evals.json` next to the skill. |
| **assertions / expectations** | Objectively verifiable statements attached to a test case. The grader produces a `{text, passed, evidence}` tuple for each. (Note: Anthropic's `schemas.md` calls them `expectations`; the grader agent also refers to them as "assertions".) |
| **benchmark.json** | Aggregated pass rate + tokens + duration per configuration, with `mean ± stddev`. Output by `scripts/aggregate_benchmark.py`. |
| **baseline run** | A second parallel subagent run for the same prompt **without** the skill loaded. For new-skill creation, baseline = no skill; for improvement, baseline = the previous version. |
| **with-skill run** | Subagent run with the skill's SKILL.md loaded into context. |
| **trigger accuracy** | Whether a skill's description causes the agent to load it on a given query. Measured by running each query N times (skill-creator uses N=3) and counting triggers. |
| **headless runtime** | An agent runtime that cannot spawn parallel subagents, cannot display HTML in a browser, or cannot open a subprocess. Examples: a CI step, `claude -p` with no MCP tools, kimi-code in non-interactive mode, Reasonix background jobs. |
| **gradability** | Property of an eval: whether its `expected_output` can be checked by a deterministic or model-judge procedure rather than human eyeballing. |
| **critic loop** | The local `taches-principled-light` term (from `general-critic`) for an adversarial-review subagent that loops until no HIGH findings remain. Conceptually the same as Anthropic's grader + analyzer combo. |

# Top Sources

| Title | URL | Author / Org | Date | 1-line takeaway |
|---|---|---|---|---|
| anthropics/skills `skills/skill-creator/SKILL.md` | https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md | Anthropic | accessed 2026-06-22 | Canonical 485-line workflow: capture intent → write draft → write evals → run with+baseline → grade → reviewer → iterate → optimize description. |
| `scripts/quick_validate.py` | https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/quick_validate.py | Anthropic | accessed 2026-06-22 | Local Python validator: checks frontmatter YAML, allowed properties (`name, description, license, allowed-tools, metadata, compatibility`), and required fields. ~100 lines. |
| `scripts/run_eval.py` | https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/run_eval.py | Anthropic | accessed 2026-06-22 | Trigger-accuracy harness. Creates a `.claude/commands/<name>-skill-<uuid>.md` file then runs `claude -p <query> --output-format stream-json --verbose --include-partial-messages` and parses the stream to detect whether the skill was consulted. |
| `scripts/run_loop.py` | https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/run_loop.py | Anthropic | accessed 2026-06-22 | Description-optimizer loop. 60/40 train/test split, 3 runs per query, ≤5 iterations. Calls Claude to propose description improvements, re-evaluates, picks best by held-out test score. |
| `agents/grader.md` | https://github.com/anthropics/skills/blob/main/skills/skill-creator/agents/grader.md | Anthropic | accessed 2026-06-22 | The grader subagent prompt: reads transcript + outputs, returns `{text, passed, evidence}` per expectation. Critical: also critiques the assertions themselves (flags trivially-passing ones). |
| `agents/comparator.md` | https://github.com/anthropics/skills/blob/main/skills/skill-creator/agents/comparator.md | Anthropic | accessed 2026-06-22 | Blind A/B judge that doesn't know which skill produced which output. |
| `agents/analyzer.md` | https://github.com/anthropics/skills/blob/main/skills/skill-creator/agents/analyzer.md | Anthropic | accessed 2026-06-22 | Post-hoc analyzer that explains WHY the blind-comparator's winner won. |
| `references/schemas.md` | https://github.com/anthropics/skills/blob/main/skills/skill-creator/references/schemas.md | Anthropic | accessed 2026-06-22 | JSON schemas for `evals.json`, `grading.json`, `benchmark.json`, `history.json`. |
| `agentskills.io/skill-creation/evaluating-skills` | https://agentskills.io/skill-creation/evaluating-skills | agentskills.io | accessed 2026-06-22 | "The skill-creator Skill automates much of this workflow — running evals, grading assertions, aggregating benchmarks, and presenting results for human review." |
| Anthropic "Skill authoring best practices" | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | Anthropic | accessed 2026-06-22 | The 4-step evaluation-driven-development cycle: identify gaps → create evals → baseline → write minimal instructions → iterate. |
| Local `crafting-skills` (taches-principled-light) | `skills/crafting-skills/SKILL.md` | Felix | local | Teaches a 14-rule compendium + Step 2 "Write Evals First" + Step 6 "Validate Before Shipping" with 4 checks: discovery, YAML, trigger, file-reference audit. |
| Local `general-critic` (taches-principled-light) | `skills/general-critic/SKILL.md` | Felix | local | Reusable critic subagent with HIGH/MEDIUM/LOW severity and explicit "loop until PASS". |
| Promptfoo "Test Agent Skills" guide | https://www.promptfoo.dev/docs/guides/test-agent-skills/ | Promptfoo | recent (2026) | JavaScript-assertion-based agent eval framework; shows assertion types and CI integration. |

# Open Threads

The background did **not** yet answer:

1. **How to grade eval outputs without a subagent runtime.** Anthropic's grader is a separate `Agent` tool invocation. In headless contexts (CI, `claude -p`, kimi-code non-interactive), the orchestrator must grade inline using its own context.
2. **How to detect "skill loaded" without `claude -p`'s stream-json.** The official `run_eval.py` writes a `.claude/commands/<name>.md` file and inspects the streaming output for content-block-start events. That depends on Claude Code's specific CLI. Other runtimes have different loading signals.
3. **How to do trigger-accuracy benchmarking when the agent runtime doesn't expose a "what skills are loaded" hook.** Some headless runtimes only consult skills described in their system prompt and never expose the loading event.
4. **Whether `improve_description.py`'s held-out-test approach generalizes to non-Claude models.** The loop assumes a Claude-shaped chat-completion response. Reasonix / kimi-code use different response formats.
5. **How to keep the local `taches-principled-light` `crafting-skills` and a new `evaluating-skills` from duplicating eval logic.** Need to compare scopes explicitly.
6. **What the right `evals.json` schema is for skills without deterministic outputs** (e.g., writing style, design taste). Anthropic's grader sidesteps this by being LLM-as-judge; a generalistic skill must either inherit that or restrict to gradable outputs.