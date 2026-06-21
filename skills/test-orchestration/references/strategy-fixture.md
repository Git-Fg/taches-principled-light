# FIXTURE — Test Data Management

## Fixture Complexity Signal

Test setup complexity is a design smell. If setup grows beyond 10 lines for a single test, the code under test likely has too many dependencies. Fix the code, not the fixture.

## Patterns by Complexity

**Simple (0-3 fixtures):** Inline data. Direct object construction in the test. Works when dependencies are minimal.

**Medium (4-10 fixtures):** Factory methods. Shared setup in a method, customized per test. "createValidOrder()" returning an order with sensible defaults.

**Complex (10+ fixtures):** Builder pattern. Chain methods to construct objects step by step. "OrderBuilder().withItem(product).withShipping(express).build()"

## Factory vs Builder

**Factory:** Creates complete objects with sensible defaults. Good for "most tests use this shape." Less flexible, simpler.

**Builder:** Constructs objects piece by piece. Good for "each test needs a different slice." More flexible, more verbose.

```
Factory: order = createOrder()     // complete, ready to use
Builder: order = OrderBuilder()    // configure then build
        .withItem(sKU: "SKU-1")
        .withShipping(expedited)
        .build()
```

## Shared Fixtures vs Local Fixtures

| Approach | Use when | Trade-off |
|----------|----------|-----------|
| **Shared fixture** | Same data across many tests | One change breaks many tests |
| **Local fixture** | Each test needs different shape | More setup code, isolation |
| **Parameterized** | Many tests need same data shape | DRY but less explicit |

## Anti-Patterns

- **God fixtures** — One fixture used by 50 tests. Change it, break 50 tests.
- **Mystery data** — Fixtures with unexplained fields: `{name: "x", amount: 100, flag: true}`. Document or remove.
- **Fixture inheritance chains** — BaseFixture → OrderFixture → ValidOrderFixture. Hard to trace, easy to break.