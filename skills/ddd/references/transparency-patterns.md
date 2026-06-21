# Transparency Patterns

Patterns and anti-patterns for ensuring code behavior is visible and predictable at the call site.

## Command-Query Separation

A function must either return a value (query) or cause a side effect (command), never both.

```typescript
// WRONG: mutation disguised as query
const result = {}
if (featureEnabled)
  applyNewFeature(result)  // mutates in-place

// WRONG: hidden throw at call site
const result = performProcess(param)
validateResult(result)  // throws — caller sees no branching

// RIGHT: return value directly
const result = featureEnabled ? applyNewFeature(baseData) : {}

// RIGHT: explicit control flow
const result = performProcess(param)
if (!isValid(result))
  throw new ProcessingError(result)
```

## Anti-Patterns to Avoid

| Pattern | Problem | Fix |
|---------|---------|-----|
| `const x = compute()` then `compute()` again | Mutation disguised as command | Return value, assign once |
| `let x = {}; mutate(x)` | Mutation hidden behind assignment | Return new value, use const |
| `validate(x)` without return check | Hidden throw at call site | Return boolean, explicit if |
| `process(order)` as single opaque call | Side effects hidden in implementation | Expand at call site |
| `if (x) transform(x)` unclear if x mutated | Data flow opaque | Return new value, assign to new name |

## Unified Example

All four principles working together (Visible Side Effects, Data Flow Through Return Values, Explicit Control Flow, Command-Query Separation):

```typescript
// Query: pure, returns, no mutation
function calculatePrice(items: Item[]): number {
  return items.reduce((sum, item) => sum + item.price, 0)
}

// Query: pure, returns, no mutation
function applyDiscount(price: number, code: string): number {
  return code === "SAVE20" ? price * 0.8 : price
}

// Policy visible at call site
const price = calculatePrice(order.items)
const discounted = applyDiscount(price, order.couponCode)
if (discounted > 1_000_000)
  throw new ValidationError("Price exceeds limit")

// Commands: side effects visible
await db.save({ orderId: order.id, total: discounted })
await paymentGateway.charge(order.customerId, discounted)
```
