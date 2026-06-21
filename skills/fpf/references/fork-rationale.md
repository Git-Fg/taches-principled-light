# Why this fork — `fpf`

`fpf` (First Principles Framework) uses `context: fork` to run PROPOSE, MAINTAIN, and QUERY modes in an isolated subagent. This file justifies the fork flag .

## Isolation value

First-principles reasoning is iterative and hypothesis-laden:
- **PROPOSE** generates competing hypotheses at L0, then verifies logic (L1), cross-references evidence (L2), and audits trust (R_eff / WLNK). Each stage iterates over the prior stage's output.
- **MAINTAIN** scans git diff and evidence files for staleness — reading many files.
- **QUERY** searches the FPF knowledge base for prior reasoning.

The hypothesis tree, evidence cross-references, and trust calculations are verbose intermediate state. Running them inline would flood the user's session with the reasoning chain. The fork absorbs that; the user gets back a Design Rationale Record (DRR), a freshness report, or a search-results table.

The fork's isolation is *especially* valuable for FPF because **the reasoning must be free of the orchestrator's accumulated biases.** A hypothesis generator that has read the user's prior conversation may anchor on it; a fresh-context generator reasons from first principles, as the name promises.

## What the fork inherits

- The user's literal `$ARGUMENTS` (problem statement + mode)
- Its own frontmatter + body
- Any `docs/principled/fpf/` artifacts from prior runs (the fork reads these at intake)

## What the fork does NOT inherit

- The user's earlier conversation (deliberately — see "isolation value")
- Skills loaded in the parent session

## Post-fork return

- **PROPOSE:** a Design Rationale Record (DRR) at `docs/principled/fpf/decisions/`
- **MAINTAIN:** a freshness report flagging stale evidence
- **QUERY:** a search-results table

## Why the fork is not for inner parallelism

Pre-1.23.0, each L-stage spawned its own specialist subagent (`fpf-hypothesis-generator`, `fpf-logic-verifier`, `fpf-evidence-validator`, `fpf-trust-auditor`). Post-1.23.0, the orchestrator reasons inline within the fork and spawns only a subagent generalist (with FPF-specific lenses) and a subagent explorer (for evidence cross-referencing). The fork's value is the isolation of the hypothesis-to-decision reasoning chain from the user's session — which preserves the "first principles" property by keeping the reasoning context clean.