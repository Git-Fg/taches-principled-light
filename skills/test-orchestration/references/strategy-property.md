# PROPERTY-BASED — Generative Edge Case Discovery

## When to Use

Property-based testing shines when:
- Input space is large (strings, numbers, dates)
- Edge cases are non-obvious (null, empty, boundary values)
- Human intuition misses patterns (combinatorial explosion)
- Same property should hold across all inputs

## The Property Mindset

Instead of "test these 5 specific inputs," ask "what invariant must hold for ALL inputs?"

```
Example: Sort is reversible
- Pick 10 random arrays
- Sort each array
- Verify: original array == sorted array.sort()  // reverse sort

Example: Parser rejects invalid input
- Pick 100 random strings
- Verify: invalid strings raise ParseError
```

## Shrink Wrapping

When a generated input causes a failure, the test framework tries smaller inputs to find the minimal reproduction. This minimal case is the "shrunk" input — the simplest version that still triggers the bug.

**Why it matters:** A failing test that generates "f8xK29!@#qwer" is unhelpful. A shrunk input of "" (empty string) pinpoints the actual issue.

## Test Frameworks

| Language | Framework | Shrink algorithm |
|----------|-----------|------------------|
| JavaScript | fast-check | Power of 2 tree |
| Python | hypothesis | Binary search |
| TypeScript | fast-check | Power of 2 tree |
| Rust | proptest | Linear search |
| Go | testing/quick | Binary search |

## Common Properties to Test

- **Round-trip:** Serialize then deserialize, verify equality
- **Commutativity:** A op B == B op A
- **Idempotence:** op(op(x)) == op(x)
- **Identity:** op(x, identity) == x
- **Distributivity:** A op (B op C) == (A op B) op C
- **Monotonicity:** input grows → output doesn't decrease (or similar)

## Anti-Patterns

- **Testing implementation** — "Property holds for random inputs" is fragile if implementation changes. Test behavior, not structure.
- **Weak invariants** — "Result is defined" is not a property. "Result is in range [0, max]" is a property.
- **Too many properties** — One strong property beats five weak ones. Each property is a potential false failure.

## Integration with EXECUTE

ALWAYS design the test strategy inline for complex test suites — author the strategy, the property list, the shrinkage heuristics, and the integration boundaries yourself, then iterate against spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why.". Property-based tests complement TDD: use TDD for known cases and edge cases you can anticipate; use property-based for combinatorial exploration. A complete test suite has both.