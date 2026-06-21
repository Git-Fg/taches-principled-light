# COVERAGE — What to Test, What to Skip

## The Coverage Illusion

100% line coverage is achievable but often meaningless. A test that executes every line but never asserts is worse than no test. Coverage is a proxy, not a goal.

**Coverage that matters:**
- Critical paths (money, security, data integrity)
- Public interfaces of modules with complex internals
- Error and edge cases in business logic
- Integration points where systems meet

**Coverage that doesn't matter:**
- Getter/setter boilerplate
- Framework glue code
- Private implementation details
- Trivial one-liners with obvious behavior

## Decision Framework

| What | Why test | Why skip |
|------|----------|----------|
| Public API | Contract must hold | Implementation details |
| Business rules | Behavior matters | Internal structure |
| Error paths | Failure modes count | Happy path already covered |
| Integration points | Where systems break | Internal logic |
| Configuration | Environment affects behavior | Hardcoded safe defaults |

## Heuristics by System Type

**Business logic:** Test rules, not implementation. If you can explain the rule in one sentence, it's testable. If it requires a paragraph, split it first.

**Data access:** Test queries, not ORMs. Verify the query does what you expect; ORM behavior is covered by the library's own tests.

**External services:** Mock at boundary. Test what you send and receive; don't test the service's internal behavior.

**Configuration:** Test the configuration parsing, not the default values. If the code does X when config is Y, test that mapping.

## Anti-Patterns

- **Testing private methods** — You're testing implementation, not behavior. If the private method matters, make it public (or extract a class).
- **Assertion-free tests** — Tests that execute code but never assert anything: no expect() calls, no assert statements, no comparison assertions. These provide zero confidence — they pass whether the code works or not.
- **Coverage as quality** — High coverage with low assertion density is a false signal. Quality is in assertions, not execution.