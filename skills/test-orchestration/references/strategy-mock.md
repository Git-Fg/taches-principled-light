# MOCK-STRATEGY — When to Mock, When to Use Real

## The Mocking Spectrum

```
Real dependency → In-memory implementation → Test double (mock/stub/fake) → No dependency
```

## Decision Criteria

**Use real dependencies when:**
- The dependency is fast and deterministic (in-memory DB, mocked HTTP server)
- You need to verify integration behavior (end-to-end contracts)
- The behavior is well-understood and stable

**Use mocks when:**
- The dependency is slow, non-deterministic, or has side effects (real API, filesystem, time)
- You need to control specific inputs to reach edge cases (error responses, timeout scenarios)
- The dependency is external and not your responsibility to test

**Never mock when:**
- The mock would duplicate the production implementation's complexity
- You're testing behavior that spans multiple components
- The test becomes more complicated than the code it's testing

## The Trust Boundary

```
Your code ←→ Mock at boundary ←→ External system
```

**Inside your codebase:** Use real implementations or in-memory substitutes. The goal is confidence that components work together.

**At boundaries:** Mock external systems (APIs, databases, file systems). Test your side of the contract, not theirs.

## Mock Types

| Type | Use when | Anti-pattern |
|------|----------|--------------|
| **Stub** | You need to provide specific responses | Asserting on what was never called |
| **Mock** | You need to verify interactions (calls, arguments) | Testing implementation details |
| **Fake** | You need simplified behavior that's still useful | When real implementation is faster |
| **Spy** | You need to observe calls without controlling them | Complex setup for simple verification |

## Anti-Patterns

- **Mocking value objects** — Strings, numbers, dates don't need mocks. Mock the services that consume them.
- **Mocking what you're testing** — If you're testing module A, don't mock module B if A calls B. Use real B or restructure.
- **Excessive stub setup** — If your test setup is longer than your assertions, the design is wrong.