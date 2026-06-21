# Architecture Rules

Guidelines for structuring code for maintainability, focusing on layered architecture, functional core principles, and physical code limits.

## Layered Architecture

Keep business logic in pure domain and use case layers, free of framework or infrastructure dependencies. When domain logic is coupled to controllers, ORMs, or HTTP libraries, it becomes untestable and unreusable.

**Q: Where do I put this code?**
- Business rule/calculation needing no I/O → **pure function** in domain layer
- Orchestration of multiple steps → **use case/service** delegating to interfaces
- HTTP/event handling → **controller/adapter** delegating to use cases
- Data persistence → **repository** implementing domain interface
- Side effects (email, logging, external APIs) → **imperative shell** at composition root

## Functional Core, Imperative Shell

Keep business logic in pure functions (inputs → outputs, no side effects). Push all I/O — database calls, HTTP requests, logging, file I/O — to an outer imperative shell.

Pure functions are deterministic and trivially testable without mocks.

**Why:** Business logic tangled with logging, database reads, and persistence requires mocking everything to test. Pure core + imperative shell = testable domain.

## Early Returns

Handle error conditions and edge cases at the top of functions instead of nested conditionals. Keeps happy path at the top level, reducing cognitive load.

**Rule:** Never nest more than 3 levels. Use guard clauses for all error conditions.

## Function Size Limits

Decompose functions longer than 80 lines into smaller, focused functions of 50 lines or fewer. Keep files under 200 lines.

**Rule:** If a function grows beyond 80 lines, it is doing more than one thing. Extract by responsibility.
