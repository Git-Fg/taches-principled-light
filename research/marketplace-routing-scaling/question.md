# Question

Two-part research question on agent-skill marketplaces and routing quality:

1. **Routing-quality degradation curve**: As the number of skills in a marketplace or session grows, how does per-skill trigger recall degrade? Is the curve linear, knee-shaped, or sigmoidal? At what marketplace size does the design recommendation shift from "add skills" to "consolidate or shard"?

2. **Production marketplace implementations**: How do production agent-skill marketplaces (Claude Code Skills API at 8-per-request, Cursor, Codex, kimi-code, Microsoft Agent Framework) implement description-based routing under their respective context-budget and session-discovery constraints? What practical advice exists for marketplaces that want to scale beyond the 8-skill hard ceiling?