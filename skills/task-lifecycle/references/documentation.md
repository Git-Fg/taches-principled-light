# Documentation Patterns Reference

Patterns, templates, and guidelines for writing maintainable documentation after code changes.

## README.md Best Practices

### Project Root README

```markdown
# Project Name

Brief description (1-2 sentences max).

## Quick Start
[Fastest path to success - must work in <5 minutes]

## Documentation
- [API Reference](./docs/api/) - if complex APIs
- [Guides](./docs/guides/) - if complex workflows
- [Contributing](./CONTRIBUTING.md) - if accepting contributions

## Status
[Current state, known limitations]
```

### Module README Pattern

```markdown
# Module Name

**Purpose**: One sentence describing why this module exists.

**Key exports**: Primary functions/classes users need.

**Usage**: One minimal example.

See: [Main documentation](../../README.md) for detailed guides.
```

## JSDoc Best Practices

### Document These

```typescript
/**
 * Processes payment with retry logic and fraud detection.
 *
 * @param payment - Payment details including amount and method
 * @param options - Configuration for retries and validation
 * @returns Promise resolving to transaction result with ID
 * @throws PaymentError when payment fails after retries
 *
 * @example
 * ```typescript
 * const result = await processPayment({
 *   amount: 100,
 *   currency: 'USD',
 *   method: 'card'
 * });
 * ```
 */
async function processPayment(payment: PaymentRequest, options?: PaymentOptions): Promise<PaymentResult>
```

### Don't Document These

```typescript
// Obvious functionality
getName(): string

// Simple CRUD
save(user: User): Promise<void>

// Self-explanatory utilities
toLowerCase(str: string): string
```

## When to Generate vs Write

### Use Automated Generation For

- OpenAPI/Swagger: REST API reference, request/response examples
- GraphQL Schema: Type definitions and queries
- JSDoc: Function signatures and basic parameter docs
- Database Schemas: Prisma, TypeORM, Sequelize models

### Write Manual Documentation For

- Integration examples: Real-world usage patterns
- Business logic explanations: Why decisions were made
- Troubleshooting guides: Solutions to actual problems
- Getting started workflows: Curated happy paths

## Index Document Update Checklist

When documentation changes affect a module or feature:

| Document | Update When |
|----------|-------------|
| `README.md` (root) | New features, modules, or overview changes |
| `README.md` (module) | Module exports, purpose, or usage changes |
| `docs/index.md` | New documentation pages or structure changes |
| `getting-started.md` | Setup steps or quickstart changes |
| `guides.md` | New guides or guide categories |
| `reference.md` | New API references or structure |
| `SUMMARY.md` | Documentation structure changes (GitBook) |
| `_sidebar.md` | Navigation structure changes (Docsify) |
| `mkdocs.yml` nav | Documentation navigation changes (MkDocs) |

### Example: Adding a New Feature

```text
Files to update:
├── src/reporting/README.md      → Add to key exports
├── docs/guides/index.md         → Link to new guide
├── docs/guides/exporting.md     → Create new guide
├── docs/reference/index.md      → Link to API reference
├── README.md                    → Mention in features list
└── SUMMARY.md                   → Add navigation entries
```

## Documentation Quality Checklist

Before finishing documentation work:

- [ ] All user-facing changes documented
- [ ] Code examples tested and working
- [ ] Links verified (no 404s)
- [ ] Documentation follows project conventions
- [ ] No duplication of generated docs
- [ ] Index documents link to new content

## What to Document

- Getting started (quick setup, first success in <5 minutes)
- How-to guides (task-oriented, problem-solving)
- API references (when manual adds value over generated)
- Troubleshooting (real problems with proven solutions)
- Complex business logic JSDoc

## What NOT to Document

- API docs duplicating generated schema docs
- Code comments explaining what code obviously does
- Process documentation for processes that don't exist
- Changelogs duplicating git history
- Documentation of temporary workarounds

## Design Decisions

### Why multi-agent for docs

Analysis, writing, and review require different expertise and perspective. Parallel agents with distinct focuses produce more complete documentation coverage.

### Why index document checklist

Index documents (READMEs, docs/index, navigation) are the most commonly missed update — they connect users to content. Explicitly checking them prevents orphaned documentation.

### Why simple change shortcut

For 1-2 file changes, the overhead of spawning agents exceeds the value. Direct writing is faster and equally effective.

### Why documentation hierarchy

Not all docs are equal. The CRITICAL/IMPORTANT/NICE_TO_HAVE triage ensures effort goes where it matters most — breaking changes and new APIs before polish.

### Relationship to development pipeline

- Operates after code changes are made but before commit
- Complements code review by ensuring documentation quality
- Produces documentation updates ready for commit alongside code

## Output Template

Report of documentation updates completed:

```markdown
## Documentation Updates

### Files Updated
- [ ] Root README.md
- [ ] Module README files
- [ ] docs/ content files
- [ ] JSDoc comments

### Index Documents Updated
- [ ] Root README.md
- [ ] docs/index.md / SUMMARY.md
- [ ] Module README files

### Changes Documented
- [List of changes covered]

### Quality Review
- [ ] All criteria passed
```