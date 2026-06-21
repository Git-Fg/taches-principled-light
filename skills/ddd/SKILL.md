---
name: ddd
description: "Restructure tangled files, untangle mixed layers, fix business logic in the wrong place, audit an API contract, or resolve deeply nested code. Use when the user says 'this file is a mess', 'logic is in the wrong place', 'API contract is unclear', 'too much nesting', 'function does too much', 'business logic in controllers', 'restructure this', 'untangle this'. NOT for: incremental code cleanup (use `refine`); NOT for: runtime bugs (use superpowers' `systematic-debugging`)."
when_to_use: "Use when tangled files, wrong-layer logic, messy API contracts, or deeply nested code appear. Trigger symptoms: 'this file is a mess', 'logic is in the wrong place', 'API contract is unclear', 'too much nesting', 'function does too much', 'business logic in controllers'."
---

## What This Skill Changes

ddd changes how you respond when code structure, layering, API contracts, or behavior visibility questions surface. By default, you might give one-line advice, refactor inline, or skip the analysis. ddd forces structured diagnosis before any code changes.

| Concern | Default behavior | ddd behavior |
|---------|-----------------|--------------|
| Architecture | Suggest a refactor; hope for the best | Map structure with a subagent explorer (scope: "map the module structure under src/ and identify layering violations"), emit a Failure Signal, dispatch to `implement` |
| API design | Sketch endpoints from intuition | Spawn spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why.", produce a contract failure signal, dispatch to `refine` |
| Transparency | Note CQS violations in passing | Audit Command/Query boundaries explicitly; classify as pure/impure |
| Quality | Catch obvious smells | Apply library-first threshold (30 lines), error-as-vocabulary, naming idioms |

**Downstream action:** this skill never edits code. After diagnosis, dispatch the Failure Signal JSON to `core-principled:implement` (for restructuring) or `core-principled:refine` (for contract polish and quality cleanup).

## Routing Guidance

- ARCHITECTURE: 'where does business logic go', 'too much nesting', 'too many parameters', 'function does too much', 'business logic in controllers'
- QUALITY: 'what should I name this', 'should I use a library', 'silent failure'
- TRANSPARENCY: 'hidden side effect', 'does this return or mutate', 'is this a side effect', 'mutation disguised as query'
- API: 'design REST API', 'API endpoint design', 'HTTP semantics', 'API versioning'

## Relationship to kaizen

ddd and kaizen are complementary, not redundant. They operate at different layers of the same concern (preventing bad code from entering the codebase).

**ddd** is a detailed analysis methodology with 4 modes (ARCHITECTURE, QUALITY, TRANSPARENCY, API) invoked when a specific structural question surfaces. It produces a written analysis, may spawn subagents (codebase scanner, endpoint auditor), and is selected per mode based on the question at hand.

**kaizen** is a lightweight 4-pillar filter applied to every code decision. It runs continuously in the background as guardrails — a developer does not "invoke" kaizen, they apply it as they write. No artifact, no analysis mode, no spawned subagent. The output is shaped code, not a written report.

**Conceptual layering:** kaizen is the immune system (always on, lightweight, prevents infection); ddd is the specialist (called in for specific diagnoses, produces a treatment plan).

## Decision Router

IF code structure or layering issue → ARCHITECTURE mode — ALWAYS spawn a a subagent explorer subagent (scope: "map the module structure under src/ and identify layering violations") to map structure
IF naming or error handling issue → QUALITY mode
IF behavior visibility or data flow issue → TRANSPARENCY mode
IF REST API contract design, resource modeling, or versioning issue → API mode — ALWAYS spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." to review contracts

---

# Mode: ARCHITECTURE

Structure code for maintainability through layered architecture and functional core principles.

**ALWAYS spawn a a subagent explorer subagent (scope: "map the module structure under src/ and identify layering violations") to map structure and identify layering violations.**

### Failure Signal Schema

Emit this JSON when diagnosis completes. `core-principled:implement` consumes it directly.

```json
{
  "mode": "ARCHITECTURE",
  "violations": [
    {
      "file": "path/to/file.ts",
      "line": 42,
      "layer": "controller",
      "actual_content": "domain logic",
      "expected_layer": "service",
      "severity": "HIGH"
    }
  ],
  "anti_patterns": ["business-logic-in-controller", "deep-nesting", "fat-service"],
  "metrics": {
    "max_nesting": 6,
    "files_examined": 12,
    "violations_count": 4
  },
  "severity_rules": {
    "HIGH": "Layer inversion — business logic in wrong layer; fix before commit",
    "MEDIUM": "Functional impurity — IO mixed with pure logic; refactor when touched",
    "LOW": "Nesting or size limit; clean up opportunistically"
  }
}
```

**Severity rules:**
- **HIGH** — layer inversion (controller holds business logic, repository handles authorization)
- **MEDIUM** — functional impurity (pure functions calling IO, hidden dependencies)
- **LOW** — nesting depth >4 or file/function size exceeds budget

### Implementation Guidelines

You MUST read `references/architecture-rules.md` BEFORE beginning architectural analysis to ensure compliance with layering rules, functional core principles, and physical code limits (nesting, size).

---

# Mode: QUALITY

Apply idiom checks: domain-specific naming, library-first approach, visible error handling.

**Principle: errors are vocabulary, not telemetry.** A typed error is a word the caller can pattern-match on. A logged-and-swallowed exception is a missing word. The catch block either recovers, rethrows with context, or converts to a domain term.

## 5-Step Process

1. **Scan names** — flag `utils`, `helpers`, `common`, `shared`; demand domain verbs (`order-pricing.ts`, `csv-encoder.ts`).
2. **Apply the 30-line library threshold** — if custom non-trivial logic would exceed 30 lines and a battle-tested library exists, use the library. Below 30 lines, write it inline.
3. **Audit error handling** — every `catch` must rethrow, recover, or convert to a typed domain error. No silent swallows.
4. **Check library fit** — reject libraries that bring their own runtime, framework, or inversion of control. Prefer composable libraries over batteries-included frameworks.
5. **Score transparency** — can a new reader tell from the call site what the function does and what it mutates? If not, rename or split.

## 4 Anti-Patterns

- **Generic names** (`utils.ts`, `helpers.go`) — hide intent; rename to what they do.
- **Reinventing wheels** — hand-rolled date math, URL parsing, retry loops, validation. Use `date-fns`, `URL`, `p-retry`, `zod`.
- **Silent catch** — `catch (e) {}` or `catch (e) { console.log(e) }` strips the caller of error vocabulary.
- **Library as framework** — adopting a library that brings its own runtime, dependency tree, or inversion of control.

## 4 Failure Cases

- **`utils.ts` at 800 lines** — generic name attracted every helper; the file became a junk drawer. Rename to domain-specific modules; split immediately.
- **Custom retry with exponential backoff** — 40 lines of code, three edge cases missed (jitter, max attempts, idempotency). `p-retry` solves it in 3 lines.
- **Logged-and-continued exception** — `catch (e) { logger.error(e); return null }` — the caller cannot distinguish "not found" from "DB down". Return a typed `Result<T, NotFound | DbError>`.
- **Date math via `new Date()` arithmetic** — DST, timezone, and locale bugs. Use `date-fns` or `Temporal`.

---

# Mode: TRANSPARENCY

Ensure code reveals its behavior at the call site through CQS and explicit data flow.

### Implementation Guidelines

You MUST read `references/transparency-patterns.md` BEFORE analyzing behavior visibility to ensure compliance with Command-Query Separation and transparency anti-pattern protections.

---

# Mode: API

Design REST API contracts with proper resource modeling, HTTP semantics, and versioning strategies.

**ALWAYS spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." to review contracts.**

### Failure Signal Schema

Emit this JSON when contract audit completes. `core-principled:refine` consumes it directly.

```json
{
  "mode": "API",
  "endpoints": [
    {
      "method": "POST",
      "path": "/orders",
      "violation": "verb-in-path",
      "current": "/orders/create",
      "expected": "/orders",
      "severity": "HIGH"
    }
  ],
  "anti_patterns": ["verb-in-path", "inconsistent-status-codes", "missing-pagination", "no-versioning"],
  "http_semantics": {
    "status_codes_valid": false,
    "idempotency_keys_used": false
  },
  "severity_rules": {
    "HIGH": "Contract breaks clients — wrong verb, missing status code, broken idempotency",
    "MEDIUM": "Discoverability — no pagination, no filtering, inconsistent error shape",
    "LOW": "Style — casing, header conventions, trailing slashes"
  }
}
```

**Severity rules:**
- **HIGH** — contract breaks clients (verb in path, wrong status code, broken idempotency, missing auth)
- **MEDIUM** — discoverability (no pagination, no filtering, inconsistent error shape across endpoints)
- **LOW** — style (casing, header conventions, trailing slashes)

### Implementation Guidelines

You MUST read `references/api-design.md` BEFORE designing or auditing REST endpoints to ensure compliance with resource modeling rules, HTTP semantics, and versioning strategies.

---

## CONTRAST

- NOT for: runtime bugs and crashes — use superpowers' `systematic-debugging`
- NOT for: incremental code improvement — use refine
- NOT for: design-time constraint decisions — use kaizen
- NOT for: test-driven development cycles — use test-orchestration

## Reference Index

IF mapping code structure or layering → spawn **a subagent explorer** (scope: "map the module structure under src/ and identify layering violations")
IF auditing REST API contracts or resource modeling → spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why."
