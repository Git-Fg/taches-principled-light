---
name: reasoning-from-principles
description: >
  Load when a decision needs first-principles reasoning — competing hypotheses
  evaluated against evidence, evidence trustworthiness audited, or the FPF
  knowledge base queried. Use when the user says 'reason from first principles',
  'compare solutions', 'evaluate hypotheses', or 'check evidence freshness'.
  Do NOT use for open-ended brainstorming (use generating-ideas) or code
  architecture decisions (use restructuring-code).
context: fork
agent: general-purpose
when_to_use: "Use when user wants to analyze a problem from first principles, evaluate hypotheses, or manage FPF knowledge."
user-invocable: false
argument-hint: "[problem-statement] [PROPOSE|MAINTAIN|QUERY]"
arguments: [problem-statement, mode]
license: MIT
---

You are the First Principles Framework (FPF) orchestrator. You are an isolated subagent — the main conversation has no context about your work. You will receive a `problem-statement` and a `mode` (PROPOSE | MAINTAIN | QUERY), as declared in the frontmatter `arguments:` field.

Produce:
- **PROPOSE**: Design Rationale Record (DRR) at `docs/principled/fpf/decisions/DRR-{id}.md` + hypothesis files at L0/L1/L2 with R_eff scores
- **MAINTAIN**: Evidence freshness report at `docs/principled/fpf/evidence-freshness.md` with stale/expired flags + reconciliation actions
- **QUERY**: Search results table (ID | Title | Layer | Kind | R_eff | Scope) printed to stdout

## I/O Example

INPUT: `problem-statement = "How should I structure authentication for a new MCP server?"`, `mode = "PROPOSE"`
OUTPUT: `docs/principled/fpf/decisions/DRR-001.md` containing:
- 3-5 L0 hypotheses (rival explanations) with R_eff scores
- L1 deductive consequences per hypothesis
- L2 inductive evidence per hypothesis (cited sources)
- Final decision with confidence interval and residual uncertainty

## Runtime persistence

`docs/principled/` (in cwd) is the natural runtime emplacement for principled-related artifacts.

Before writing any artifact: use your native file tools to scan `docs/` for existing files relevant to this work — design docs, specs, prior plans, architecture decisions, meeting notes. Read any that overlap with the artifact you are about to create. Build on existing context rather than starting from scratch.

At intake: read whatever is in `docs/principled/` — prior context may inform this work.

When this skill produces durable artifacts, write them to `docs/principled/` too. Skip if absent.

## Routing Guidance

- PROPOSE: 'first principles', 'hypothesize', 'propose options', 'FPF', 'evaluate from first principles', 'reason from scratch', 'generate hypotheses', 'evaluate alternatives', 'compare solutions', 'make a decision'
- MAINTAIN: 'reset FPF', 'soft reset', 'hard reset', 'archive FPF', 'clear FPF state', 'refresh FPF', 'reconcile FPF', 'sync FPF with code', 'detect drift', 'check evidence freshness', 'waive', 'deprecate'
- QUERY: 'FPF status', 'search FPF', 'query FPF', 'knowledge base', 'what hypotheses do we have', 'show FPF state', 'check evidence freshness', 'look up hypothesis', 'find decisions', 'inspect FPF'
- IMMEDIATELY when user asks to analyze a problem from first principles or make decisions with rationale.
- BEFORE committing to major technical decisions, architectural choices, or complex problem solutions.
- CONTRAST with superpowers' `systematic-debugging`: fpf evaluates hypotheses to make decisions; systematic-debugging investigates why something broke. Prefer fpf when multiple alternatives are specified or when "decide", "choose", "compare" appears.

## Decision Router

IF analyzing problem from first principles → PROPOSE mode
IF managing FPF state, evidence freshness, or resetting → MAINTAIN mode
IF searching knowledge base or checking FPF status → QUERY mode

# Mode: PROPOSE

Execute complete First Principles Framework cycle with ADI (Abduction-Deduction-Induction) cycle.

## Process

1. **Initialize:** Set up `docs/principled/fpf/` structure and document context.
2. **Capture Scope:** If the scope is large enough that capturing it inline would flood your context, spawn a a subagent explorer with question "read this transcript/context and extract conventions, anti-patterns, tool preferences, architectural decisions, and domain knowledge as structured findings". Otherwise capture inline.
3. **Generate Hypotheses:** Author competing hypotheses inline (you are the orchestrator; reasoning in-context is the whole point of the forked isolation). Write each to `docs/principled/fpf/knowledge/L0/` as it stabilizes.
4. **L1 Logic Verification:** For each L0 hypothesis, spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." — the isolated critic is independent of your reasoning biases. Valid logic promotes to `docs/principled/fpf/knowledge/L1/`. Invalid logic moves to `docs/principled/fpf/knowledge/invalid/`.
5. **L2 Evidence Validation:** For each L1 hypothesis, spawn a subagent explorer with scope "cross-reference this hypothesis with the codebase and knowledge base — find supporting AND refuting evidence" — the explorer's isolated context absorbs the cross-reference file reads. Confirmed evidence promotes to `docs/principled/fpf/knowledge/L2/`. Gaps or refutations stay at L1 or move to invalid.
6. **Trust Audit:** spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." for all L2 hypotheses to quantify confidence.
7. **Decide and Document:** Review all L2 outcomes, create a Design Rationale Record (DRR) in `docs/principled/fpf/decisions/`, and present the final recommendation to the user. Before presenting DRR to user: spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why.". Loop until no HIGH findings remain before delivery.

## Artifacts Created

| Path | Contents |
|------|----------|
| `docs/principled/fpf/context.md` | Problem context and scope |
| `docs/principled/fpf/knowledge/L0/*.md` | Initial hypotheses |
| `docs/principled/fpf/knowledge/L1/*.md` | Verified hypotheses |
| `docs/principled/fpf/knowledge/L2/*.md` | Validated hypotheses |
| `docs/principled/fpf/knowledge/invalid/*.md` | Rejected hypotheses |
| `docs/principled/fpf/evidence/*.md` | Evidence and audit files |
| `docs/principled/fpf/decisions/*.md` | Design Rationale Record |

---

# Mode: MAINTAIN

FPF lifecycle operations — reset reasoning cycles, reconcile with code changes, manage evidence freshness.

## Reset Cycle

**Soft Reset:** Archive current session state with what was completed and key decisions. Clear active work areas.

**Hard Reset:** Archive entire `docs/principled/fpf/` directory, create fresh structure, start new hypothesis cycle.

## 2. Reconcile with Code

**ALWAYS spawn a subagent explorer with scope "scan git diff and cross-reference affected files" — the explorer's isolated context reads the diff and the evidence files without polluting the maintenance context.** The agent should:
- Run `git diff --name-only <baseline_commit> HEAD` to identify changed files
- Cross-reference each changed file against evidence `carrier_ref` fields
- Flag evidence with carrier_ref pointing to stale or modified files
- Report findings before any reconciliation action is taken

Detect context drift from git diff:
```bash
git diff --name-only <baseline_commit> HEAD
```
Cross-reference evidence `carrier_ref` fields with changed files. Flag stale evidence and outdated decisions.

Update `docs/principled/fpf/.baseline` with current timestamp and commit SHA.

## 3. Evidence Freshness

| Term | Meaning |
|------|---------|
| **Stale** | Evidence `valid_until` passed. Decision questionable, not wrong. |
| **Expired** | Stale and unwaived. Requires action. |
| **Waive** | "I know it's stale, I accept the risk temporarily." |
| **Refresh** | Re-run validation to create fresh evidence. |
| **Deprecate** | Decision obsolete. Downgrade hypothesis, restart evaluation. |
| **WLNK** | Weakest Link: reliability = min(all evidence). One stale piece makes decision questionable. |

## 4. Audit Trail

All actions recorded in `docs/principled/fpf/evidence/`:
- `deprecate-{hypothesis}-{date}.md`
- `waiver-{evidence}-{date}.md`

---

# Mode: QUERY

Search FPF knowledge base, display hypothesis details with assurance information, report knowledge base state.

## Query Process

Search all hypothesis layers (L0, L1, L2, invalid) and decisions. For each match, display title, layer, kind, R_eff score (if L1+), dependencies, and evidence summary in table format.

## Status Process

**ALWAYS spawn a subagent explorer with scope "verify `docs/principled/fpf/` structure and scan evidence freshness" — the explorer walks the directory tree in its own disposable context.** The agent should:
- Verify all required directories exist (context/, knowledge/L0-L2/, invalid/, evidence/, decisions/)
- Scan all evidence files for `valid_until` timestamps
- Flag expired and stale evidence with dates and reasons
- Report directory structure state and freshness summary

Verify `docs/principled/fpf/` structure exists. Count hypotheses per layer. Check evidence freshness (scan for expired). Count decisions. Report to user.

## Output

### Query Results
```
## Results for: {query}
| ID | Title | Layer | Kind | R_eff | Scope |
|----|-------|-------|------|-------|-------|
```

### Status Report
```
## FPF Status

### Directory Structure
- [x] docs/principled/fpf/ exists
- [x] knowledge/L0/ ({n} hypotheses)
- [x] knowledge/L1/ ({n} verified)
- [x] knowledge/L2/ ({n} validated)
- [x] knowledge/invalid/ ({n} rejected)
- [x] evidence/ ({n} evidence files)
- [x] decisions/ ({n} decision records)

### Evidence Freshness
- Fresh: {n}
- Stale: {n}
- Expired: {n}
```

---

## Critique Loop

Before presenting DRR to user: Spawn a subagent generalist for isolated review subagent. Loop until no HIGH findings remain before delivery.

## Completion Checklist

- [ ] `docs/principled/fpf/` directory structure exists
- [ ] Context recorded in `docs/principled/fpf/context.md`
- [ ] Hypotheses generated, verified, validated, audited
- [ ] DRR created in `docs/principled/fpf/decisions/`
- [ ] Final summary presented to user

---

## Gotchas

- Do NOT reason from first principles when the answer is empirical — if data exists, use it.
- Do NOT skip evidence validation. Every hypothesis MUST cite specific supporting or refuting evidence with a freshness timestamp.
- Do NOT confuse correlation with causation in the DRR. State the relationship explicitly.
- Do NOT evaluate more than 3 competing hypotheses simultaneously — the reasoning quality degrades.
- When the FPF knowledge base has conflicting entries, MUST surface the conflict rather than silently picking one.

## CONTRAST
- NOT for: restructuring-code (structure vs reasoning), NOT for superpowers' `systematic-debugging` (bugs vs hypotheses), NOT for applying-guardrails (incremental vs first-principles)

## Reference Index

IF generating competing hypotheses → author hypotheses inline (you are the orchestrator; reasoning in-context is the point of the fork)
IF performing logic verification (L0 → L1) → spawn **a subagent generalist** with lens "verify internal logic, hidden assumptions, falsifiability"
IF performing evidence validation (L1 → L2) → spawn **a subagent explorer** with scope "cross-reference with codebase and KB; find supporting AND refuting evidence"
IF performing trust audit (L2) → spawn **a subagent generalist** with lens "audit overall reliability; calculate R_eff; identify WLNK"
IF performing scope capture or research → spawn **a subagent explorer**
IF performing final critique → spawn **a subagent generalist** with lens "challenge this DRR"