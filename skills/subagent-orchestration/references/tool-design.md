# Tool Design for Agents

Design every tool as a contract between a deterministic system and a non-deterministic agent. Unlike human-facing APIs, agent-facing tools must make the contract unambiguous through the description alone -- agents infer intent from descriptions and generate calls that must match expected formats. Every ambiguity becomes a potential failure mode that no amount of prompt engineering can fix.

## When to Activate

Activate this skill when:
- Creating new tools for agent systems
- Debugging tool-related failures or misuse
- Optimizing existing tool sets for better agent performance
- Designing tool APIs from scratch
- Evaluating third-party tools for agent integration
- Standardizing tool conventions across a codebase

## Core Concepts

Design tools around the consolidation principle: if a human engineer cannot definitively say which tool should be used in a given situation, an agent cannot be expected to do better. Reduce the tool set until each tool has one unambiguous purpose, because agents select tools by comparing descriptions and any overlap introduces selection errors.

Treat every tool description as prompt engineering that shapes agent behavior. The description is not documentation for humans -- it is injected into the agent's context and directly steers reasoning. Write descriptions that answer what the tool does, when to use it, and what it returns, because these three questions are exactly what agents evaluate during tool selection.

## The Tool-Agent Interface

**Tools as Contracts**
Design each tool as a self-contained contract. When humans call APIs, they read docs, understand conventions, and make appropriate requests. Agents must infer the entire contract from a single description block. Make the contract unambiguous by including format examples, expected patterns, and explicit constraints. Omit nothing that a caller needs to know, because agents cannot ask clarifying questions before making a call.

**Tool Description as Prompt**
Write tool descriptions knowing they load directly into agent context and collectively steer behavior. A vague description like "Search the database" with cryptic parameter names forces the agent to guess -- and guessing produces incorrect calls. Instead, include usage context, parameter format examples, and sensible defaults. Every word in the description either helps or hurts tool selection accuracy.

**Namespacing and Organization**
Namespace tools under common prefixes as the collection grows, because agents benefit from hierarchical grouping. When an agent needs database operations, it routes to the `db_*` namespace; when it needs web interactions, it routes to `web_*`. Without namespacing, agents must evaluate every tool in a flat list, which degrades selection accuracy as the count grows.

## The Consolidation Principle

**Single Comprehensive Tools**
Build single comprehensive tools instead of multiple narrow tools that overlap. Rather than implementing `list_users`, `list_events`, and `create_event` separately, implement `schedule_event` that finds availability and schedules in one call. The comprehensive tool handles the full workflow internally, removing the agent's burden of chaining calls in the correct order.

**Why Consolidation Works**
Apply consolidation because agents have limited context and attention. Each tool in the collection competes for attention during tool selection, each description consumes context budget tokens, and overlapping functionality creates ambiguity. Consolidation eliminates redundant descriptions, removes selection ambiguity, and shrinks the effective tool set. Production evidence shows this approach can outperform sophisticated multi-tool architectures.

**When Not to Consolidate**
Keep tools separate when they have fundamentally different behaviors, serve different contexts, or must be callable independently. Over-consolidation creates a different problem: a single tool with too many parameters and modes becomes hard for agents to parameterize correctly.

## Architectural Reduction

Push the consolidation principle to its logical extreme by removing most specialized tools in favor of primitive, general-purpose capabilities. Production evidence shows this approach can outperform sophisticated multi-tool architectures.

**The File System Agent Pattern**
Provide direct file system access through a single command execution tool instead of building custom tools for data exploration, schema lookup, and query validation. The agent uses standard Unix utilities (grep, cat, find, ls) to explore and operate on the system. This works because file systems are a proven abstraction that models understand deeply, standard tools have predictable behavior, agents can chain primitives flexibly rather than being constrained to predefined workflows, and good documentation in files replaces summarization tools.

**When Reduction Outperforms Complexity**
Choose reduction when the data layer is well-documented and consistently structured, the model has sufficient reasoning capability, specialized tools were constraining rather than enabling the model, or more time is spent maintaining scaffolding than improving outcomes. Avoid reduction when underlying data is messy or poorly documented, the domain requires specialized knowledge the model lacks, safety constraints must limit agent actions, or operations genuinely benefit from structured workflows.

**Build for Future Models**
Design minimal architectures that benefit from model improvements rather than sophisticated architectures that lock in current limitations. Ask whether each tool enables new capabilities or constrains reasoning the model could handle on its own -- tools built as "guardrails" often become liabilities as models improve.

IF removing specialized tools in favor of primitives or evaluating whether a complex tool architecture is justified → BEFORE deciding read `references/architectural_reduction.md`. Do not proceed without the production evidence in this file.

## Tool Description Engineering

**Description Structure**
Structure every tool description to answer four questions:

1. What does the tool do? State exactly what the tool accomplishes -- avoid vague language like "helps with" or "can be used for."
2. When should it be used? Specify direct triggers ("User asks about pricing") and indirect signals ("Need current market rates").
3. What inputs does it accept? Describe each parameter with types, constraints, defaults, and format examples.
4. What does it return? Document the output format, structure, successful response examples, and error conditions.

**Default Parameter Selection**
Set defaults to reflect common use cases. Defaults reduce agent burden by eliminating unnecessary parameter specification and prevent errors from omitted parameters. Choose defaults that produce useful results without requiring the agent to understand every option.

## Response Format Optimization

Offer response format options (concise vs. detailed) because tool response size significantly impacts context usage. Concise format returns essential fields only, suitable for confirmations. Detailed format returns complete objects, suitable when full context drives decisions. Document when to use each format in the tool description so agents learn to select appropriately.

**Token Efficiency Targets:**
Design outputs to minimize context consumption without sacrificing utility. Text format typically requires ~40% fewer tokens than equivalent JSON. Set concrete targets:
- **Default output**: Minimal fields covering 80% of use cases
- **Verbose mode**: Complete objects for debugging or complex decisions
- **Fixed labels over JSON**: Use `Path: value` syntax as parsing anchors instead of JSON objects when semantic content is identical

**Zero-Transformation Returns:**
Agents consume output directly in context. Every transformation step adds cognitive load and error potential. Design outputs that arrive ready-to-use:

| Category | Wrong | Right |
|----------|-------|-------|
| Paths | Relative to internal dirs | Relative to `process.cwd()` |
| IDs | Requiring separate lookup | Full objects or actionable references |
| Data | Encoded needing parse | Natural language or immediately usable |
| Progress | Every 1% (100+ updates) | Every 10% (~10 updates max) |

**Semantic Density:**
Natural language text outperforms JSON for agent consumption because LLMs are trained on text. JSON adds structural overhead without semantic value. Prefer text format unless the agent specifically requests structured data.

## Error Message Design

Design error messages for two audiences: developers debugging issues and agents recovering from failures. For agents, every error message must be actionable -- it must state what went wrong and how to correct it. Include retry guidance for retryable errors, corrected format examples for input errors, and specific missing fields for incomplete requests. An error that says only "failed" provides zero recovery signal.

**Actionable Failure Patterns:**
Error messages teach the next step, not just "error occurred." Each failure mode includes specific recovery guidance.

| Situation | Teach This |
|-----------|------------|
| No results | Split terms, broaden search, try discovery flag |
| Permission denied | Check permissions, try with elevation |
| Missing dependency | Install command, where to get it |
| Ambiguous input | Show top matches, ask to clarify |
| Invalid format | Show expected format, provide example |

## Tool Definition Schema

Establish a consistent schema across all tools. Use verb-noun pattern for tool names (`get_customer`, `create_order`), consistent parameter names across tools (always `customer_id`, never sometimes `id` and sometimes `identifier`), and consistent return field names. Consistency reduces the cognitive load on agents and improves cross-tool generalization.

## Tool Collection Design

Limit tool collections to 10-20 tools for most applications, because research shows description overlap causes model confusion and more tools do not always lead to better outcomes. When more tools are genuinely needed, use namespacing to create logical groupings. Implement selection mechanisms: tool grouping by domain, example-based selection hints, and umbrella tools that route to specialized sub-tools.

## CLI Tool Design

**The Command Sweet Spot:**
Research shows accuracy degrades at scale: ~85% at 5 commands vs ~60% at 10 commands. Both humans and AI agents suffer from decision paralysis when evaluating large command sets. Design for 5-10 top-level commands, then use subcommands for additional depth.

| Structure | Cognitive Load | Discovery |
|-----------|---------------|-----------|
| `cmd_create`, `cmd_get`, `cmd_delete` (flat) | High: n tools to evaluate | Massive manifest |
| `cmd [create\|get\|delete]` (layered) | Low: 1 tool + subcommands | Progressive via --help |

**Self-Teaching Hierarchical --help:**
Every CLI level must have complete `--help` output that serves as a self-contained manual. Agents discover capabilities through --help before making calls.

Required sections at EACH level:
- **USAGE**: Command pattern with placeholders
- **OPTIONS**: All flags with WHEN to use them
- **BEHAVIOR**: What default shows and how flags change it
- **EXAMPLES**: 2-4 concrete usage patterns

## MCP Tool Naming Requirements

Always use fully qualified tool names with MCP (Model Context Protocol) to avoid "tool not found" errors.

Format: `ServerName:tool_name`

```python
# Correct: Fully qualified names
"Use the BigQuery:bigquery_schema tool to retrieve table schemas."
"Use the GitHub:create_issue tool to create issues."

# Incorrect: Unqualified names
"Use the bigquery_schema tool..."  # May fail with multiple servers
```

## Testing Tool Design

ALWAYS spawn a tool-tester subagent to validate tool designs against five criteria: unambiguity, completeness, recoverability, efficiency, and consistency. The subagent evaluates representative agent requests against expected behavior.

## Common Mistakes

These five patterns show failure modes with wrong/right examples. Each demonstrates exactly what breaks and why, then shows the correct alternative.

### 1. Incomplete --help
```
BAD:  USAGE: tool [options]
      OPTIONS: --help, --version

GOOD: USAGE: tool <query> [options]
      OPTIONS: --list, --verbose, --help
      BEHAVIOR: Explains what default shows and when to use flags
      EXAMPLES: tool "query", tool --list
```
Agents cannot discover capabilities without complete help output.

### 2. Verbose Default Output
```
BAD:  📄 file.md (score: 0.15)
       Local:  /abs/path/file.md
       Online: https://example.com/file
       Title:  File Title
       Summary: File summary
       ReadWhen: Context

GOOD: file.md
        Summary: File summary
        ReadWhen: Context
```
Default output should cover 80% of use cases. Verbose flags for detailed debugging.

### 3. Generic Errors
```
BAD:  Error: No results found

GOOD: No results for: "multi word query"
      Try splitting: "multi" OR "word" OR "query"
      Or use: --threshold 0.5 for looser matching
```
Every error message must provide forward momentum, not dead ends.

### 4. Missing Recovery Footer
```
BAD:  Found 15 results

GOOD: Found 15 results

      REMINDER: Use native read tools for contents; tool for discovery.
      Run "tool --help" to refresh your knowledge.
```
Footer guidance reinforces best practices after the main result.

### 5. Non-Agent-Usable Paths
```
BAD:  gateway/auth.md

GOOD: docs/gateway/auth.md
```
Paths must be relative to `process.cwd()` -- agents cannot prepend directories mentally.

## Best Practices Reference

IF designing a new tool from scratch or auditing an existing tool collection for quality gaps → BEFORE designing read `references/best_practices.md`.

## Guidelines

1. Write descriptions that answer what, when, and what returns
2. Use consolidation to reduce ambiguity
3. Implement response format options for token efficiency
4. Design error messages for agent recovery
5. Establish and follow consistent naming conventions
6. Limit tool collections to 5-10 commands to maintain ~85% accuracy (avoid 10+ where accuracy drops to ~60%)
7. Use subcommands for depth instead of additional top-level tools
8. Design CLI help as self-contained manual at each level (usage, options, behavior, examples)
9. Default to text format (~40% fewer tokens than JSON)
10. Include AGENTS.md sections for proactive tool teaching
11. Test tool designs with actual agent interactions
12. Iterate based on observed failure modes
13. Question whether each tool enables or constrains the model
14. Prefer primitive, general-purpose tools over specialized wrappers
15. Invest in documentation quality over tooling sophistication
16. Build minimal architectures that benefit from model improvements
17. Design zero-transformation outputs: paths relative to cwd, actionable references, immediately usable data
18. Provide complete error recovery guidance in every failure message