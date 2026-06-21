# MCP Outputs and Pitfalls Catalog

Reference for output schemas and the curated catalog of common schema pitfalls. Read before declaring a schema ready to ship.

## §1. Schemas for outputs (outputSchema)

The tool can declare an `outputSchema` describing its return type. This is optional but valuable for:

- Typed clients (TypeScript SDKs) that want to parse the output
- Hosts that surface the result type to the user
- Documentation and validation in test harnesses

**`outputSchema` shape:**

```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "output": { "type": "string", "description": "Raw tool output" },
    "output_parsed": { "type": "object", "description": "Pre-parsed JSON when valid" }
  },
  "required": ["success", "output"]
}
```

**Why most tools skip it:** the `text` content is what the LLM sees; the schema is for typed clients. If your tool returns a JSON envelope in text (the text-with-JSON pattern from `references/design-decomposition.md` §4), an `outputSchema` lets the host parse it for the user.

## §2. Common pitfalls catalog

| Pitfall | What goes wrong | Fix |
|---|---|---|
| `additionalProperties: true` | LLM hallucinates fields; server silently ignores | Set to `false` unless you have a real reason |
| No `required` field | LLM doesn't know what's mandatory; produces incomplete calls | Always include `required: [...]` with the truly mandatory fields |
| Missing `description` on properties | LLM has to guess what each field is; gets them wrong | Every property gets a `description` — non-negotiable |
| Vague descriptions ("the name of X") | LLM doesn't know format/constraints | Add format, constraints, examples |
| Deeply nested objects (>2 levels) | LLM loses track of where it is; produces malformed calls | Flatten or pass-through as JSON string |
| Free-form string for structured data | LLM produces ambiguous parsable-but-wrong content | Use type + constraints; pass-through deep stuff as JSON string |
| `oneOf` for "kinds of X" instead of discriminator enum | LLM has to reason about branches; higher failure rate | Discriminator `enum` + flat fields + cross-field validation via `oneOf` |
| Tool name in `kebab-case` mixed with `snake_case` | LLM doesn't know what to expect | Pick one convention, be consistent |
| Missing `enum` for "kind" fields | LLM invents values | Always enum, never free string for bounded choices |
| `maxLength: 1000000` on text fields | LLM dumps huge outputs; server gets bloated responses | Reasonable maxLength (1-100 KB depending on use) |
| Boolean `*_enabled` instead of verb-form | Less clear semantically | `enable_X: true` is more explicit than `x_enabled: true` |
| Missing `$schema` field | Default is 2020-12, but explicit is better | `"$schema": "http://json-schema.org/draft/2020-12/schema"` |
| Using `format: "uuid"` alone | `format` is informational only — the schema doesn't enforce | Combine `format: "uuid"` with `pattern: "^[0-9a-f-]{36}$"` |
| Inconsistent naming (mix of `id` and `Id`) | LLM has to remember two patterns | Pick one (`id` for snake_case, `Id` for camelCase) and stick to it |
