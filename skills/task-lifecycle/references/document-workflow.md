# Document Workflow

Update documentation after code changes — READMEs, guides, API docs. Preserves style and conventions. Operates immediately after IMPLEMENT completes.

## Core Principle

Documentation must justify its existence. Every document should help users accomplish real tasks, be discoverable, maintainable, and not duplicate existing docs.

## Process

### Preparation

1. **Read project config** (package.json, pyproject.toml) and root README.md to understand the project.
2. **Discover documentation infrastructure**: docs/ structure, README files, JSDoc patterns, doc generation tools.
3. **Inventory existing docs**:

```bash
find . -name "*.md" | grep -E "(README|CHANGELOG|CONTRIBUTING|docs/)"
find . -name "openapi.*" -o -name "*.graphql" -o -name "swagger.*"
```

### Analysis

4. **Map documentation structure**: docs/ folder layout, all README files, API docs, JSDoc patterns.
5. **Analyze code changes**: Run `git status -u` (or `git show --name-status` for latest commit). Filter changes that impact documentation:
   - New/modified public APIs
   - Changed module structures
   - Updated configuration options
   - New features or workflows

### Documentation Triage

6. **Group changes by documentation area**:
   - **API Documentation**: All API changes
   - **Module READMEs**: Changes in same module
   - **User Guides**: Related feature changes
   - **JSDoc**: Complex logic changes
   - **Index Documents**: Navigation and discovery docs

**Simple changes (1-2 files):** Write documentation directly. Follow project conventions, include working examples, avoid duplication.

**Multi-file changes (3+ files or significant changes):** Use multi-agent workflow with analysis + tech-writer + review agents.

### Multi-Agent Documentation Flow (3+ files)

7. **Launch doc-analysis agents** (Haiku, parallel) — one per documentation area. Each produces a prioritized list of documentation tasks:
   - CRITICAL: Breaking changes, new public APIs
   - IMPORTANT: New features, configuration changes, index updates
   - NICE_TO_HAVE: Code comments, minor clarifications

8. **Launch tech-writer subagents** (Sonnet or Opus, parallel) — one per documentation area. Provide: documentation requirements, target files, project conventions, existing docs for style reference.

9. **Launch quality review agents** (Sonnet or Opus, parallel) — verify: all user-facing changes covered, code examples accurate, links valid, follows conventions.

10. **Iterate** if needed — re-launch tech-writer agents only for areas with gaps.

11. **Final verification** — cross-references work, no conflicting information, documentation is navigable.

## Documentation Patterns

For README templates, JSDoc patterns, and index document checklists → BEFORE writing documentation read `references/documentation.md`.

## Index Document Update Checklist

| Document | Update When |
|----------|-------------|
| Root README.md | Features, modules, or overview changes |
| Module README.md | Module exports or purpose changes |
| docs/index.md | Docs structure changes |
| SUMMARY.md / _sidebar.md | Navigation structure changes |
| mkdocs.yml nav | Navigation changes |

## Quality Gates

Before finishing:
- All user-facing changes documented
- Code examples tested and working
- Links verified (no 404s)
- Documentation follows project conventions
- No duplication of generated docs
- Index documents link to new content
