# MCP Schema Styling: Naming, Nesting, Defaults, Tool Names

Reference for the stylistic choices that make a schema feel right to an LLM: property naming, when to nest vs flatten, defaults that help, and tool name conventions. Read after `schema-foundation.md` to round out the schema design.

## §1. Property naming

**Pick one convention and stick to it across the whole server:**

- `snake_case` for `snake_case` tool names (matches Python/JSON convention): `city_name`, `max_results`
- `camelCase` for `camelCase` tool names (matches JavaScript/JSON Schema convention): `cityName`, `maxResults`

**LLM-friendly rules:**
- Full words over abbreviations: `description` not `desc`, `identifier` not `id` (exception: `id` is universally understood)
- Singular for one, plural for many: `city` not `cities` (when one), `tags` not `tag` (when many)
- No vendor prefixes on property names (the server name is the prefix): `issue_number` not `github_issue_number`
- Boolean fields as positive statements: `enable_notifications` not `notifications_disabled`

**Anti-pattern: mixed conventions in the same schema.** If one field is `city_name` and the next is `cityName`, the LLM has to remember two patterns and the failure rate goes up.

## §2. Nested objects: avoid when possible

**Default: flat.** Two levels of nesting maximum. Anything deeper should be passed through as a serialized string (the wrapper validates syntax, not semantics — see `references/design-decomposition.md` §7 for the full pass-through rationale).

**Why flat wins:**
- The LLM has to reason about each field position
- Deeply nested schemas cost more tokens per tool definition
- Selection accuracy drops with nesting depth
- The pass-through principle lets the wrapped system handle the depth

**When nesting is acceptable:**
- A natural sub-entity (e.g., `address: { street, city, country }` for shipping)
- The nested shape is stable and the LLM can pattern-match
- Flattening would lose semantic meaning

**The 2-level rule:** if you find yourself writing `obj.obj.obj`, stop and use a pass-through string.

## §3. Defaults that help

Server-side defaults that the LLM can rely on reduce the number of fields the LLM has to fill:

| Default | When to use | Schema syntax |
|---|---|---|
| `false` for booleans | Most boolean features default to off | `default: false` |
| `[]` for optional arrays | Empty list is a sensible "no items" | `default: []` |
| `0` / `1` for numeric counts | Sensible default count | `default: 10` |
| Specific mode string | Most common case | `default: "standard"` |
| `null` for Optional<T> | Server-side, not in the schema | (handled by schemars skip_serializing_if) |

**Don't default critical fields.** If the user must explicitly opt into a destructive action, leave the default `false` and let the LLM (or user) set it `true` explicitly.

## §4. Tool name = verb + noun

**The verb_noun pattern:**

- `read_file`, `create_issue`, `search_products`, `list_sessions`
- `move_application` not just `application` (verb says what you do TO the application)
- For action sets, the tool name is the entity, the action is the discriminator:
  - `session(action="resume")` not `resume_session`
  - `config(action="update")` not `update_config_field`

**Group with prefix when 5+ tools from one domain:**
- `github_create_issue`, `github_list_repos`, `github_search_code`
- The prefix helps the LLM disambiguate when multiple servers are loaded
- Don't prefix if you only have 1-2 tools (overhead without benefit)

**Avoid generic names:**
- `search`, `query`, `run`, `do`, `handle` — collide with other servers, vague to the LLM
- Names that describe implementation not behavior: `http_post_v2` (what does that DO?)

**Test for clarity:** a user who sees the tool name in a list should be able to guess what it does without reading the description. `get_weather(city)` ✓ vs `gw(city)` ✗.

## §5. Schemas for outputs (outputSchema)

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
