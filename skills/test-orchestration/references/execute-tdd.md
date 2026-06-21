# Test-Driven Development — Red-Green-Refactor

Write the test first. Watch it fail for the right reason. Write minimal code to pass. Never skip the failure step — a test you never saw fail proves nothing.

## Core Principle

If you did not watch the test fail, you do not know whether it tests the right thing.

## The Iron Law

Write the failing test FIRST. Production code before the test fails? Delete it. Start over. Not "keep as reference." Not "adapt it while writing tests." Delete means delete. Implement fresh from tests. Period.

Never skip the failure step — a test you never saw fail proves nothing.

## Red-Green-Refactor

**RED — Write Failing Test:** Write one minimal test for one behavior. Clear name, real code (mocks only if unavoidable), minimal setup. Requirements: one behavior, clear name, real code.

**Verify RED — Watch It Fail:** Never skip. Run the test. Confirm it fails (not errors), the failure message matches expectations, and it fails because the feature is missing (not a typo). Test passes? You are testing existing behavior — fix the test. Test errors? Fix the error, re-run until it fails correctly.

**GREEN — Minimal Code:** Write the simplest code to pass the test. No extra features, no refactoring, no improvements.

**Verify GREEN — Watch It Pass:** Run the test. Confirm pass, other tests still pass, output is pristine. If the test fails, fix the code — not the test.

**REFACTOR — Clean Up:** After green only. Remove duplication, improve names, extract helpers. Keep tests green. Do not add behavior.

**Repeat:** Next failing test for the next behavior. Return to RED.

## Anti-Patterns

- **Testing Mock Behavior** — Asserting on mock existence tests nothing about real behavior
- **Test-Only Methods in Production** — Methods only used in tests pollute production classes and create risk
- **Mocking Without Understanding** — Mocks that break side effects the test depends on produce false passes
- **Incomplete Mocks** — Partial mocks that omit fields downstream code uses cause silent failures

## When Stuck

| Problem | Solution |
|---------|----------|
| Do not know how to test | Write the wished-for API. Write the assertion first. |
| Test is too complicated | The design is too complicated. Simplify the interface. |
| Must mock everything | The code is too coupled. Use dependency injection. |
| Test setup is huge | Extract helpers. Still complex? Simplify the design. |

## Verification Checklist

- Every new function or method has a test
- Watched each test fail before implementing
- Each test failed for the expected reason (feature missing, not typo)
- Wrote minimal code to pass each test
- All tests pass — pristine output (no errors, warnings)
- Tests use real code (mocks only if unavoidable)
- Edge cases and error paths are covered

Cannot check every box? You skipped TDD. Start over.