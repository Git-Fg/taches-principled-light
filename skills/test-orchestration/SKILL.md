---
name: test-orchestration
description: >
  Load when planning test strategy or fixing and adding tests — coverage
  planning, mock strategy, fixture design, property-based testing, post-hoc
  coverage addition, and test repair. Use when the user says 'plan tests',
  'add coverage', 'fix failing tests', 'mock strategy', or 'design a test
  suite'. Do NOT use for new-feature red-green-refactor TDD (use superpowers'
  test-driven-development), diagnosing why production code broke (use
  superpowers' systematic-debugging), or PR code review (use
  reviewing-and-polishing).
when_to_use: "Use for planning test suites, mocking, or fixing broken tests. Triggers: coverage strategy, add coverage, fix broken tests, mock strategy, fixture design. NOT for: red-green-refactor TDD cycles (use superpowers' `test-driven-development`)."
argument-hint: "[mode] [target]"
license: MIT
---

## Routing Guidance

**Priority Order:** Strategy precedes execution. Use STRATEGY when making decisions about tests. Use EXECUTE when writing or fixing tests.

IF deciding what to test, coverage strategy, mocking approach, fixture design, or property-based testing → use STRATEGY
IF adding post-hoc coverage, or fixing failing tests → use EXECUTE

IMMEDIATELY when the user says: 'fix tests', 'fix failing tests', 'tests are broken', 'restore test suite', 'update assertions'
BEFORE implementing any new feature or bug fix when tests do not yet exist

## Decision Router

| Mode | Trigger | Sub-modes |
|------|---------|-----------|
| STRATEGY | Deciding what to test, coverage, mocks, fixtures | COVERAGE, MOCK-STRATEGY, FIXTURE, PROPERTY-BASED |
| EXECUTE | Writing tests for existing code, fixing failing tests | Write Tests, Fix Tests |

IF implementing a new feature from scratch → use superpowers' `test-driven-development` (RED first)
IF fixing a bug → use superpowers' `test-driven-development` (write reproducing test first)
IF adding test coverage for existing uncommitted changes → use Write Tests
IF fixing failing tests after refactoring or dependency updates → use Fix Tests
IF refactoring → tests must already exist and pass before starting

---

## §CONTRAST

**DO NOT use this skill for:**
- "Run the tests / see if they pass" — just run `cargo test` / `pytest` etc. directly; this skill is for *planning* and *fixing*, not for routine test runs
- "Review my code quality" → `reviewing-and-polishing` REVIEW mode
- "Investigate a failing test's root cause" → superpowers' `systematic-debugging` (this skill fixes symptoms; systematic-debugging finds the underlying cause)
- "Plan the project / break it into phases" → `plan-lifecycle`
- "Scan code for security vulnerabilities" → `security` skill

CONTRAST with superpowers' `test-driven-development`: that skill is the authority on Red-Green-Refactor TDD cycles for new features and bug fixes; this skill is for test strategy decisions and repairing/filling gaps in existing test suites.

---

# STRATEGY

Test planning decisions — what to test, what to mock, how to structure test data.

## COVERAGE

IF deciding what to test or what coverage matters → BEFORE proceeding read `references/strategy-coverage.md`. Do not proceed without reading this file.

## MOCK-STRATEGY

IF deciding whether to mock or use real dependencies → BEFORE proceeding read `references/strategy-mock.md`. Do not proceed without reading this file.

## FIXTURE

IF test setup exceeds 10 lines or data management is messy → BEFORE proceeding read `references/strategy-fixture.md`. Do not proceed without reading this file.

## PROPERTY-BASED

IF finding edge cases systematically or generating minimal reproduction → BEFORE proceeding read `references/strategy-property.md`. Do not proceed without reading this file.

---

# EXECUTE

Test execution — post-hoc coverage addition and test repair.

## Write Tests

IF adding post-hoc test coverage for existing code → BEFORE proceeding read `references/execute-write-tests.md`. Do not proceed without reading this file.

## Fix Tests

IF fixing failing tests after refactoring or dependency updates → BEFORE proceeding read `references/execute-fix-tests.md`. Do not proceed without reading this file.

---

## Reference Index

| IF condition | Read this reference |
|-------------|---------------------|
| Deciding what to test or coverage strategy | `references/strategy-coverage.md` |
| Deciding mocking approach | `references/strategy-mock.md` |
| Test data management or fixture design | `references/strategy-fixture.md` |
| Finding edge cases with property-based testing | `references/strategy-property.md` |
| Adding post-hoc coverage for existing code | `references/execute-write-tests.md` |
| Fixing failing tests after refactoring | `references/execute-fix-tests.md` |