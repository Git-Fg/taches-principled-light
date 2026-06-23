# Subagent Contract Design

**Audience:** anyone authoring or auditing subagent spawn instructions in this plugin.
**Source of authority:** issues #35 (taches-principled-light 5 principles from JSONL testing), #36 (3 universal gaps + P6 ground truth), #37, #38.

This document defines 6 design principles for subagent contracts in the `taches-principled-light` plugin. A contract is the agent's frontmatter (`description`) plus its body instructions. A well-designed contract makes LLM behavior auditable; a poorly-designed one produces plausible-looking but unreliable output.

**The 6 principles, summarized:**

| # | Principle | One-line |
|---|---|---|
| P1 | Source of truth | Every field the contract sets has a single, computable source. |
| P2 | Bind Writes to Reads | Every Write is paired with a named content source, never "the most recent Read." |
| P3 | Ordered operations with verification | Operations listed in execution order with explicit verification between them. |
| P4 | Explicit link resolution | Any identifier-to-path mapping has a single, testable algorithm. |
| P5 | Failure-mode footer | A "Failure modes this subagent defends against" section at the bottom of every contract. |
| P6 | Ground truth (NEW, from #36) | Subagents that make factual claims must have Read access to the source of truth. |

---

## P1 — Name the source of truth for every value

**Rule:** Every field the contract says the subagent must set has a single, computable source. If the contract says "compute X" but X has no source, fix the tool list (add a way to compute X) or fix the contract (drop X). Never "compute X" with no source.

**Anti-pattern:**

> "Save with frontmatter (source_path, ingested, sha256 of the body)."

There is no source for `sha256` — the ingester agent has `Read` but no `Bash`, so it cannot compute a real hash. The result: a placeholder hex string that the linter accepts as valid frontmatter but is semantically wrong (drift detection breaks). Verified in issue #35 finding #2.

**Pattern:**

> "Save with frontmatter (source_path, ingested: today's date)."

`ingested` is a system value — always computable from `date` or a runtime clock. The schema doesn't need a tool that's not in the tool list.

**What to check when auditing:**
- For every field in the contract's output spec, ask: "How does the subagent get this value?"
- If the answer is "compute it" but the tool list doesn't include a way to compute it, the contract is wrong.
- Either add the tool (preferred when the field is load-bearing) or drop the field (preferred when the field is a nice-to-have proxy).

---

## P2 — Bind Writes to Reads explicitly

**Rule:** Every Write should be paired with a named content source. If a subagent Reads file X and then Writes file Y, the instruction must say: "the body of Y is the body of X." This prevents the "most-recent-Read-wins" failure mode.

**Anti-pattern:**

> "Read the source file, then save with frontmatter."

LLMs have a strong prior to use the most-recently-Read content as the basis for Writes. When the ingester had a wrong "most recent Read" in context (it Read vaswani-2017.md for format reference, then Wrote its body to a different file), the bug emerged. Verified in issue #35 finding #1: ingester wrote vaswani's body into the GQA raw archive.

**Pattern:**

> 1. Read source file at `<source_path>`. Bind body to variable `source_content`.
> 2. (You may Read other files for format reference. Do NOT use their content for Writes.)
> 3. Write `<archive_path>` with frontmatter + `source_content` as the body.
> 4. Verify: Read back `<archive_path>`. Body must equal `source_content`.

**What to check when auditing:**
- For every Write in the contract, trace backward: what Read supplied the body?
- If the contract says "Read X, then Write Y" without binding, the model is free to use any other Read in context for the Write.
- Add a `source_content` variable binding; reference it explicitly in the Write step.

---

## P3 — Order operations explicitly with verification steps

**Rule:** The contract should list operations in execution order with explicit verification between them. "After Write X, Read X to confirm the content is what you intended."

**Anti-pattern:**

> "Save to raw/articles/, then process as above."

No order, no verification. The model has to infer both.

**Pattern:**

```
1. Read source. Bind body to `source_content`.
2. Write raw archive at `raw/<name>.md`. Verify: Read back; body == source_content.
3. Write wiki page at `concepts/<name>.md`. Verify: count outbound [[wikilinks]] >= 2.
4. Update index.md. Verify: Read back; new page is listed.
5. Append log.md. Verify: Read back; new entry was appended (not overwritten).
```

**What to check when auditing:**
- Operations in a sensible execution order (Read sources → Write archive → Write pages → Update index → Update log).
- Each Write followed by a Read-back verification.
- The verification check is testable — the model can mechanically determine pass/fail.

---

## P4 — Make link resolution an explicit algorithm

**Rule:** Any subagent that resolves identifiers to paths needs a single, testable resolution algorithm. Reference it from every subagent that does resolution.

**Anti-pattern:**

> "use [[wikilinks]]"

A convention with no algorithm. The linter and the searcher can disagree on whether a bare name resolves to a file. Verified in issue #35 finding #4.

**Pattern:**

> When resolving `[[X]]`:
> 1. Check `<wiki>/X.md`
> 2. Check `<wiki>/entities/X.md`
> 3. Check `<wiki>/concepts/X.md`
> 4. Check `<wiki>/comparisons/X.md`
> 5. Flag as broken (do NOT silently resolve)

Document the algorithm in one place (the schema) and reference it from every subagent that does resolution.

**What to check when auditing:**
- Find every place the contract says "resolve X to a file" or "find the page for Y."
- For each, the contract should either reference a documented algorithm or spell it out inline.
- If two subagents could resolve the same identifier differently, there's a bug.

---

## P5 — Make the contract's failure modes explicit

**Rule:** Add a "Failure modes this subagent defends against" footer to every subagent contract. List the specific failure modes with the defensive step for each.

**Anti-pattern:**

Subagent contracts end at "Output Format" with no self-awareness. The model has no checklist for "what could go wrong here?"

**Pattern:**

```markdown
## Failure modes this subagent defends against

- **Copy from wrong source (most-recent-Read wins)**: bind body to `source_content` variable, never use other Reads for Writes.
- **Missing tool**: if `Bash` is unavailable, document the fallback in this contract before spawning. If a required tool is missing, abort with a clear error to the hub.
- **Tool-output desync**: verify by reading back what was just written.
- **Concurrency**: this subagent is single-writer. The hub must serialize invocations against the same wiki.
- **Contract drift**: the schema may evolve; if a required frontmatter field is missing, fail with a clear error rather than guessing a default.
```

**What to check when auditing:**
- Every contract has a "Failure modes" section (or equivalent: "Pitfalls", "What could go wrong", "Self-audit checklist").
- The failure modes listed are real, not generic ("be careful").
- Each mode names a defensive step the subagent can take.

---

## P6 — Subagents that produce factual claims MUST have Read access to ground truth

**Rule:** If the contract says "summarize what happened", "validate against the codebase", "find supporting evidence", or any other factual claim about prior behavior or external state, the subagent must have a path to Read the source of truth.

**Anti-pattern (illustrative):** A subagent declares `tools: []` and is asked to "generate a hypothesis about the wiki ingest failure". It has no Read access to the wiki's JSONL trace, so it guesses at the Glob pattern. Its guess is wrong but plausible — it asserts the pattern confidently, not as speculation.

**Pattern:** The subagent inherits the full tool pool (no `tools:` field) AND has a contract clause: "When making factual claims about the codebase, you MUST Read or Grep the relevant files first. Do not assert specific file paths, line numbers, function names, or content based on speculation. If you cannot verify a claim with the available tools, mark the claim as 'unverified' rather than asserting it." This is the standard `## Ground truth` (or `## Ground truth (P6)`) section in the marketplace's spawn patterns (a subagent generalist, a subagent explorer, a subagent explorer, a subagent generalist, a subagent generalist, a subagent explorer).

**Two-part check:**

1. **Tool list check:** if the subagent makes factual claims, the inherited tool pool must include `Read` (which it does unless `tools:` restricts). Single allowed exception: a subagent explorer (`tools: [Read, Glob, Grep]`) — read-only is the point.
2. **Contract clause check:** the body should have an explicit "verify before asserting" rule. Without it, the model will fabricate confidently.

**What to check when auditing:**

For every subagent, ask:
- Does the contract ask the subagent to make any factual claim about external state?
- If yes: does the `tools:` list include Read (i.e., is there NO restriction that strips it)?
- If yes: is there a "verify before asserting" clause in the body?

If the answer to the first is yes and either of the next two is no, the subagent is in the failure mode.

---

## Application: the 4 marketplace tool-source patterns

There are 4 distinct patterns in the marketplace for how a subagent gets its tools. **Patterns 1 and 2 are exceptional — only use them when a NEVER policy requires the tool boundary as enforcement.** Patterns 3 and 4 (no `tools:` field at all) are the actual defaults.

| Pattern | When to use | Example |
|---|---|---|
| **Default: no `tools:` field** | Most subagents. Agent inherits the full tool pool. | most subagents currently use this (a subagent generalist, a subagent explorer, a subagent explorer, a subagent generalist, a subagent generalist). |
| **A. Explicit full tool list** | ONLY when body says "NEVER do X" and the boundary enforces it. | Zero current marketplace examples — only add when a NEVER policy demands it. |
| **B. Explicit restricted tool list** | ONLY when body says "NEVER do X" and the tool boundary is the enforcement layer. | a subagent explorer (`tools: [Read, Glob, Grep]`) is the **only** current example. |
| **C. `tools: []` with implicit orchestrator handling** | Subagent returns text output. The orchestrator writes to disk on its behalf. **Only valid when the contract is text-only.** | No current marketplace example — all spawn patterns return rich output, not text-only. |
| **D. `tools: []` inheriting from skill `allowed-tools`** | Partial; harness inheritance is undocumented. **Avoid.** | No current marketplace example. |

**The decision rule:**

- If the agent's body has no NEVER policy → use the default (no `tools:` field). The agent inherits the full tool pool.
- If the agent's body says "NEVER do X" and the tool boundary IS the enforcement layer → use Pattern A or B. Choose A when the agent needs full access but must be blocked from specific tools; choose B when the agent should only have narrow access.
- If the agent returns text only and the orchestrator handles file I/O → use Pattern C. **State this explicitly in the contract** ("The orchestrator writes the output to disk on your behalf.").
- Avoid Pattern D. Document it in the schema if you must support it.

---

## When to declare a `tools:` list

**Only when a body policy says "NEVER do X" and the tool boundary is the enforcement layer.**

The tool boundary is not a way to scope down an agent's capabilities for hygiene or least-privilege aesthetics — it is a hard enforcement mechanism. If the body policy is advisory (the model is trusted to follow it), the `tools:` list is unnecessary and harmful.

**Worked example — the canonical case:**

a subagent explorer has body text: "NEVER write or modify any wiki file." Its frontmatter declares:
```yaml
tools: [Read, Glob, Grep]
```
This is legitimate because:
1. The body contains an explicit NEVER policy ("NEVER write or modify")
2. The tool boundary is the **only** enforcement mechanism — without it, the model could choose to ignore the advisory
3. The tool list is minimal (only Read operations that support the search function)

**The restriction cost is real:** any `tools:` list removes the agent's access to user-configured MCP servers, project-specific tools, and `settings.json` quirks. This is an acceptable trade-off only when the NEVER policy is load-bearing and the cost is intentional.

---

## When NOT to declare a `tools:` list

Do not add `tools:` when:

- The body has no NEVER policy — the agent is trusted to use tools as appropriate for its role
- The body says "produce a solution" or "generate output" with no restrictions — this is a DO policy, not a NEVER policy, and the agent should inherit the full tool pool
- The body references file I/O but the orchestrator handles it — use Pattern C instead
- The rationale is "least privilege" or "security hygiene" without a specific NEVER policy — this is imaginary security that costs real capability

---

## Testing methodology (the 3-phase method)

Per issue #35 R4, the marketplace's testing methodology for subagents is three phases:

1. **Static read** — read every skill in the plugin (`skills/*/SKILL.md`). Map the spawn patterns. Identify the tool/contract surface.
2. **Real-condition invocation** — set up a realistic test scenario. Spawn the subagent with a concrete task. Capture the JSONL trace.
3. **JSONL trace analysis** — compare what the subagent reported to what it actually did (via tool calls). The discrepancy between subagent-report and JSONL is the ground truth for any audit.

**The trace is not optional.** It is the only way to find bugs the model didn't surface in its own report (issues #35 findings #1 and #2 are both invisible without JSONL analysis).

**Test scenarios to cover:**
- Happy path (the subagent's primary use case)
- Edge case A (missing required input)
- Edge case B (subagent receives only metadata, no body)
- Adversarial case (the input is wrong, contradictory, or hostile)

**For every redesigned contract, write at least one JSONL test before declaring it done.** Save the JSONL alongside the agent definition in a `tests/<agent-name>/` directory.

---

## Per-plugin contract template

For new subagent files in this marketplace, use this template:

```yaml
---
name: <plugin>-<role>
description: |
  <one-paragraph role description in user vocabulary, with 5-7 example phrasings>
color: <red|blue|green|yellow|purple|orange|pink|cyan>
background: true   # only for long-running agents
skills:
  - <owning skill>            # 1-3 skills, never 0 unless pure reasoning
# tools:                           # OMIT unless body has a NEVER-do-X policy
#   - Read                      # Only when a NEVER policy requires the tool boundary
#   - Write                     # as the enforcement layer. Default: inherit all tools.
---

# Role

<one paragraph: what this subagent does, when it fires>

# Inputs (the contract)

<what the orchestrator passes: paths, IDs, modes, options>

# Procedure (P3 — ordered operations with verification)

1. Read `<source>`. Bind to `<variable_name>`.
2. Write `<target>`. Verify: Read back.
3. ...

# Outputs

<shape of the output: text? file path? JSON?>

# Failure modes (P5)

- <mode>: <defensive step>
- ...

# Ground truth (P6, if applicable)

<clause about verifying before asserting, if the subagent makes factual claims>
```

---

## References

- Marketplace audit history: `docs/principled/plans/` (search for `AUDIT-*.md`)
- The P6 rule itself: a subagent that makes factual claims must have Read access to the source of truth, must verify with tool calls, and must mark unverified claims as such. See the `## Ground truth (P6)` sections in the spawn patterns for the canonical wording.
- Volatile provenance (issue numbers, PR numbers, file paths from specific PRs, contributor names, dates) belongs in commit messages and CHANGELOG entries — not in this reference doc.
