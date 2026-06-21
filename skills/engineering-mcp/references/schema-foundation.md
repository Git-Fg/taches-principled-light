# MCP Schema Foundation: Principle, Defaults, Constraints, OneOf-vs-Enum

Reference for the foundational design choices that every MCP tool schema must get right: the core "schemas are LLM instruction manuals" principle, the MCP defaults that should always be set, the constraint discipline, and the oneOf-vs-discriminator-enum call.

## §1. The core principle: schemas are LLM instruction manuals

A JSON Schema for an MCP tool is not primarily a validator. It's the
**instruction manual the LLM reads to decide which tool to call and how to
fill the arguments**. Every design choice should be evaluated against:
"does this make it easier for the LLM to construct a correct call?"

**Three failure modes this principle defends against:**
1. **Tool-selection failure** — LLM picks the wrong tool (e.g., calls `search` when it should call `search_products`)
2. **Argument-fill failure** — LLM uses the right tool but wrong args (e.g., passes `"eighty-eighty"` for a port number)
3. **Schema-violation failure** — LLM hallucinates a field that doesn't exist, or omits a required one

**Schema design that prevents all three:**
- **Tool name** does the heavy lifting for tool-selection (`verb_noun`, not `do_stuff`)
- **`description`** is the LLM's instruction manual for the tool's purpose
- **Property `description`s** are the LLM's instruction manual for each arg
- **Constraints** (`enum`, `pattern`, `range`) prevent hallucination
- **`required`** + `additionalProperties: false` force schema conformance

## §2. MCP defaults you should always set

```json
{
  "$schema": "http://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["..."],
  "properties": { ... }
}
```

**`additionalProperties: false` is non-negotiable** — without it the schema
accepts anything, which means LLM hallucinations silently get through. Set it
on every object schema, no exceptions.

**`required: [...]`** must list every field the tool truly needs to function.
Optional fields go in `properties` but not in `required`. The LLM uses
`required` to decide which fields to definitely fill.

**`$schema` is informational but explicit is better** — pin the 2020-12 draft
so future draft changes don't surprise you.

## §3. Constraints: every property should have one

Unconstrained string fields are LLM-failure factories. Pick a constraint for
every property:

| Type | Constraint | Use |
|---|---|---|
| `string` | `enum: [...]` | Bounded set of choices (action, mode, status) |
| `string` | `pattern: "^[0-9a-f-]{36}$"` | UUID, hash, structured ID |
| `string` | `format: "date-time"` | ISO 8601 timestamps |
| `string` | `minLength`, `maxLength` | Bound the input size |
| `string` | `format: "email"`, `format: "uri"` | Common formats (combine with `pattern` for enforcement) |
| `integer` / `number` | `minimum`, `maximum` | Numeric ranges (port numbers, counts) |
| `array` | `minItems`, `maxItems`, `items` | Bound length and shape |
| `object` | `additionalProperties: false`, `required` | Nested discipline |

**`format` alone is informational** — JSON Schema validators don't enforce
`format: "uuid"` by default. Combine `format` with `pattern` for actual
enforcement.

**Combine constraints** — `format: "uuid"` + `pattern: "^[0-9a-f-]{36}$"` +
`maxLength: 36` is the triple that actually rejects bad UUIDs at the schema
layer.

## §4. `oneOf` vs discriminator enum: the right call 95% of the time

**Default: discriminator enum + flat fields + cross-field validation.**

```json
{
  "type": "object",
  "properties": {
    "action": { "type": "string", "enum": ["create", "update", "delete"] },
    "create_id": { "type": "string" },
    "update_id": { "type": "string" },
    "delete_id": { "type": "string" }
  },
  "required": ["action"]
}
```

This is 95% of what you need. The LLM fills the discriminator and the
relevant field; cross-field logic (e.g., "if action=create then create_id
required") is enforced in the tool implementation, not the schema.

**When `oneOf` is the right call:** genuinely disjoint object shapes where
the union of all fields would be ambiguous. Example: a `geometry` field
that can be a Point, LineString, or Polygon — each with different
properties, and a generic shape would mislead the LLM.

```json
{
  "oneOf": [
    { "type": "object", "required": ["type", "coordinates"], "properties": {
      "type": { "const": "Point" },
      "coordinates": { "type": "array", "items": { "type": "number" }, "minItems": 2, "maxItems": 3 }
    }},
    { "type": "object", "required": ["type", "coordinates"], "properties": {
      "type": { "const": "LineString" },
      "coordinates": { "type": "array", "items": { "type": "array" } }
    }}
  ]
}
```

**Anti-pattern: `oneOf` for "kinds of X" with overlapping fields.** If all
the variants share 80% of their fields, the `oneOf` branches create
duplication and the LLM has to reason about which branch applies. Use a
discriminator enum + flat fields instead.

## §5. Required vs optional

**The principle: `required` should be minimal.** Mark a field required only
if the tool genuinely cannot function without it. Everything else goes
optional with a sensible default (or `None` if Rust-side `Option<T>`).

**Common mistakes:**
- Marking every field required "just to be safe" → LLMs fabricate values for fields they don't have
- Marking nothing required → LLMs omit critical fields and the server errors out at runtime
- Using `null` as a value for optional → use absence instead (no `null` in the JSON output, no field in the input)

**When in doubt:** if the field's value can be sensibly defaulted server-side, mark it optional. If the tool returns a clear error without it, mark it required.

## §6. Description writing: earn your context cost

Each `description` costs context tokens for every turn. Make them count.

**Good description patterns:**

1. **Action + scope:** "Get current weather for a city. Use when the user asks about temperature, rain, or forecast."
2. **Format + examples:** "City name to get weather for, e.g., 'London' or 'Paris, FR'."
3. **Constraint reminder:** "ISO 8601 date with timezone, e.g., '2025-03-26T14:30:00Z'. Use this for the `--since` flag in continuous mode."
4. **Discriminator hint:** "One of 'create', 'update', or 'delete'. Determines which other fields are required."

**Bad description patterns:**

1. **"The name of the X"** — adds nothing the field name doesn't already say
2. **"Required"** — that's what `required: [...]` is for
3. **Multi-paragraph essays** — LLMs lose the actionable signal in the noise
4. **Marketing speak** — "Powerful, flexible configuration" tells the LLM nothing

**Per-field budget:** aim for 5-25 words. Long enough to disambiguate and give examples, short enough to fit in the context budget.
