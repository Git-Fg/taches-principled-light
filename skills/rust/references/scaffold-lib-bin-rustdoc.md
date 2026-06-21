# Lib vs Bin Design, rustdoc Conventions, Examples, Edition Migration

Reference for the lib+bin pattern, rustdoc conventions, examples & tests directory structure, and the edition-2021-to-2024 migration playbook. Read it before designing a new project's code layout or migrating an existing crate's edition.

## §1. Lib vs bin design

**Pattern (ripgrep, bat, fd, cargo):** put the work in `src/lib.rs`, keep `src/main.rs` thin.

```rust
// src/main.rs (~30 lines)
use mycrate::{run, Config};
use clap::Parser;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let config = Config::parse();
    run(config)
}
```

**Why:** lib code is testable (you can `use mycrate::...` from `tests/`), reusable (downstream users get it), and refactorable (binary code isn't).

**Crate feature gating the binary:** if you want library users to be able to disable the CLI entirely, use a feature:
```toml
[features]
default = ["application"]
application = []
```
Then in `src/main.rs`: `#[cfg(feature = "application")] fn main() { ... }`. bat uses this pattern.

## §2. rustdoc conventions

**Every public item gets doc comments.** Use the standard sections:
```rust
/// One-line summary.
///
/// Longer description with motivation, examples, edge cases.
///
/// # Examples
///
/// ```
/// use mycrate::foo;
/// assert_eq!(foo(2), 4);
/// ```
///
/// # Errors
///
/// Returns `Err(MyError::Invalid)` if the input is out of range.
///
/// # Panics
///
/// Panics if `n == 0` (division by zero).
pub fn foo(n: u32) -> Result<u32, MyError> { ... }
```

**Section order:** `# Examples` first, then `# Errors`, `# Panics`, `# Safety` (for `unsafe`).

**Module-level docs** use `//!`:
```rust
//! This crate provides utilities for parsing X.
//!
//! # Quick start
//!
//! ```
//! use mycrate::Parser;
//! let p = Parser::new("input");
//! ```
```

**Deny missing docs in libraries:**
```rust
// src/lib.rs
#![warn(missing_docs)]
#![warn(rust_2018_idioms)]
#![forbid(unsafe_code)]   # if you're safe-Rust
```

**DO NOT use `#![deny(warnings)]`** — it breaks on transitive-dep warnings and you cannot opt out. Use `RUSTFLAGS="-D warnings"` in CI for your crate only, and configure per-crate clippy via `clippy.toml` (the lints reference covers MSRV-aware lints, the disallowed-types list, and the library-vs-binary lint group selection).

## §3. Examples & tests directory

```
mycrate/
├── src/lib.rs
├── examples/                   # runnable examples, compiled with `cargo run --example <name>`
│   ├── basic.rs
│   └── advanced.rs
└── tests/                      # integration tests, compiled with `cargo test`
    ├── api_test.rs
    └── fixtures/
```

**Examples** are user-facing documentation. They should be runnable (`cargo run --example basic`) and serve as a quick start. Document each with `//!` module docs and a comment at the top saying what it demonstrates.

**Integration tests** in `tests/` are end-to-end tests that exercise the public API. They have access to `mycrate` as if they were a downstream user. Use them for:
- API contract tests
- Edge cases that need full crate setup
- Tests that need a real filesystem or network

**Do NOT put unit tests in `tests/`.** Unit tests live in `src/foo.rs` with `#[cfg(test)] mod tests`. Integration tests in `tests/` are slower (separate compilation) and have no access to internals.

**When the suite grows:** once `tests/` carries ≥10-20 root-level files (`api_test.rs`, `auth_test.rs`, …), each becomes a separate test binary in Cargo, with N× link-time cost. Collapse them into a single `tests/main.rs` that mounts the files as `tests/suites/<name>.rs` submodules. See `references/quality-testing-and-coverage.md` §4 (the single-binary multi-suite pattern) for the migration playbook, the dead-code accuracy benefit, and the per-suite filtering syntax. For brand-new projects with 1-3 integration tests, stay with the Cargo default; the migration cost outweighs the benefit until the suite grows.

## §4. Edition migration (when working with an existing 2021 crate)

The edition-2024 migration is mostly automated but has a few sharp edges:

```bash
# 1. Bump in Cargo.toml
# edition = "2021" → edition = "2024"

# 2. Run cargo fix
cargo fix --edition

# 3. Handle the breaking changes (see below)

# 4. Verify
cargo build --all-features
cargo test --all-features
cargo clippy --all-targets -- -D warnings
```

**Breaking changes to watch for:**
- `gen` keyword (used to be valid in `block!{}` macros) — now a reserved word; rename to `gen_` or use `r#gen`
- `expr_2021` macro fragment spec — behavior changed for trailing commas
- Lifetime capture rules in `impl Trait` — may need explicit `+ 'a` annotations
- RPIT (return-position impl Trait) lifetime capture defaults tightened

**Strategy:** bump edition, run `cargo fix --edition`, fix the remaining compile errors one at a time, run clippy. Most projects migrate in 1-2 hours.

## Authoritative sources

When a rustdoc convention, a doctest attribute, a Cargo target-discovery rule, or an edition-migration sharp edge is in question, fetch the live canonical source. The triggers below are the *only* reasons to fetch.

| Source | Canonical for | Fetch live when |
|---|---|---|
| `https://doc.rust-lang.org/rustdoc/` | The rustdoc Book (doc-comments, `# Panics`/`# Errors`/`# Safety` sections, intra-doc links) | Authoring rustdoc conventions or auditing doc-section compliance |
| `https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html` | Doctest semantics and attributes (`no_run`, `ignore`, `should_panic`, `compile_fail`) | Deciding a doctest attribute or diagnosing why a doctest fails to compile |
| `https://doc.rust-lang.org/cargo/reference/cargo-targets.html` | Cargo targets (lib, bin, examples, tests auto-discovery rules) | Confirming the lib+bin layout or the `examples/` vs `tests/` discovery rules |
| `https://doc.rust-lang.org/edition-guide/` | Edition Guide, including the 2021→2024 migration playbook | Running `cargo fix --edition` or auditing migration sharp edges (`gen` keyword, `expr_2021`, lifetime capture, RPIT) |
| `https://doc.rust-lang.org/reference/` | The Rust Reference (module, item, and visibility semantics) | A layout or visibility question hinges on exact language semantics |
