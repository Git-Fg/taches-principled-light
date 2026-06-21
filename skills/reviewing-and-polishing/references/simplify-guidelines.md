# Simplify Guidelines

These guidelines define the numeric thresholds and anti-patterns for code simplification to ensure consistent quality and maintainability.

### Numeric Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Function length | >40 lines | Extract cohesive subgroups |
| Nesting depth | >3 levels | Guard clauses, early returns |
| Parameters | >5 | Bundle into config object |
| Boolean flags in params | >=2 | Split function or use enum |
| Duplicate blocks | >=3 occurrences | Extract or parameterize |
| Variables reassigned | >3 times | Split into smaller functions |

### Anti-Patterns

| Wrong | Right | Consequence |
|-------|-------|-------------|
| Splitting a 50-line function into 5 ten-line functions called once | Extract only when the block has a clear identity | Indirection without abstraction increases cognitive load |
| Renaming during extraction | One transformation per commit | Bugs become untraceable |
| Removing "unnecessary" null checks | Keep defensive checks unless type system enforces | Latent production bugs |
| Over-normalizing with reduce/chains | Use comprehensions for simple maps/filters | The simplification becomes harder to read |
| Flattening with boolean flags | Early returns for each condition | Debugging requires evaluating boolean algebra mentally |
| Inlining a helper used in 3 places with different semantics | Only inline when call sites are semantically identical | Subtle semantic differences pass tests but fail at runtime |
| Optimizing before simplifying | Simplify first, profile second, optimize third | Premature optimization creates complex code |
| Leaving dead code as "documentation" | Git history is the record — delete | Signal-to-noise ratio degrades |
