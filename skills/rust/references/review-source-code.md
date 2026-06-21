# Source-Code Health and Rust Idioms — Audit Reference

Used by the `"audit source-code health and idioms"` lens (Lens 1 of REVIEW). Audits `.rs` files in the target project for idiomatic patterns, clippy profile soundness, `unsafe` correctness, error-handling discipline, and async/concurrency hazards. Augments (does not replace) `references/quality-clippy-and-fmt.md` (lints setup) and `references/rust-idiom-polish.md` (the inline checklist).

Lens 1 spawns with the contract defined in `references/review-orchestration.md` and produces findings in that schema.

## §1. Idiomatic patterns checklist

Apply these in order. Each item has a finding template; substitute the actual `path:line` and a concrete `fix`.

1. **Clone elimination** — flag `.clone()` or `.to_owned()` where borrowing suffices. Specifically: `.clone()` on a `&str` to feed an `Into<String>` (use `String::from` only if the value must be owned; otherwise pass `&str`); `.clone()` on a `&[T]` where the callee could take `&[T]`; `.clone()` on a `Copy` type (use `.copied()` instead, see §5).
2. **`?` over nested `match`** — flag any 3+ arm `match` whose only useful arms are the `Ok`/`Err` paths. Replace with `?` (or `let else` for `Option`).
3. **`let else` for single-arm `Option`/`Result`** — flag `match`/`if let Some(x) = ... else { return ... }` chains. `let else` (1.65+) is the canonical form.
4. **Iterator chains** — flag manual `for` loops that compile to index manipulation, `push` into a pre-sized `Vec`, or `while let` patterns that `iter().map().filter().collect()` would express. Do not flag loops whose readability genuinely benefits from the explicit form.
5. **`.copied()` over `.cloned()`** — for `Copy` iterators (most numeric, `bool`, references via `&T`), `.copied()` is the zero-cost form. `.cloned()` is correct but `clippy::cloned_instead_of_copied` will flag it.
6. **`&str` over `&String`** — public function parameters that take `&String` should take `&str`. Internally, `.as_str()` is one method away.

## §2. Clippy profile evaluation

For the *configured* lints, not the code:

1. `clippy.toml` MSRV — verify the `msrv` key (or top-level `rust-version` in `Cargo.toml`) matches the actual floor. MSRV-aware lints (`clippy::manual_strip`, `clippy::needless_lifetimes`, etc.) will silently produce false positives if MSRV is too high.
2. `disallowed-types` — confirm the list is appropriate for the project (e.g. `std::sync::Mutex` banned in async code; `tokio::sync::Mutex` banned where blocking is fine).
3. Library-level pragmas in `src/lib.rs`:
   - `#![warn(missing_docs)]` should be present for any public-API crate.
   - `#![forbid(unsafe_code)]` for safe-API libraries (and `#[allow(unused_unsafe)]` for FFI crates that have to escape it).
   - `#![deny(warnings)]` is the anti-pattern from `quality-clippy-and-fmt.md`; flag if present.
4. Lint-group selection per use case — binary / library / embedded / `no_std` each warrant different default lint sets.

## §3. Unsafe and soundness guardrails

For every `unsafe` block in the audited code:

1. **Soundness comment** — every `unsafe` block MUST have a `// SAFETY: <reason>` comment naming the compiler invariant upheld. Missing comment is a BLOCKER (the next maintainer has no way to verify the contract).
2. **Raw-pointer hygiene** — flag raw pointers dereferenced without explicit bounds checks, raw pointers that escape the lifetime of their origin, or raw pointers obtained from a `Box::into_raw` without a matching `from_raw`.
3. **FFI invariants** — flag C calls that do not validate the input pointer is non-null and properly aligned, or that accept a `c_char*` without an explicit length.
4. **`unsafe` in safe-API libraries** — flag any `unsafe` outside of a clearly isolated `mod ffi` or `mod sys`. Public APIs that leak `unsafe` requirements to callers are a soundness hazard.
5. **Unsafe transmute** — `std::mem::transmute` is a smell. Prefer `try_into` + size check, `bytemuck` for POD, or explicit `from_le_bytes`/`to_le_bytes`.

## §4. Error-handling discipline

1. **`Result` over `panic!` in library code** — flag `panic!`, `unwrap()`, `expect()` in non-test library code. Each occurrence is at minimum a WARN; if the panic happens on a user-supplied input, it is a BLOCKER (DoS surface).
2. **`thiserror` vs `anyhow`** — libraries should use `thiserror` (typed errors, `From` impls); binaries can use `anyhow` (opaque error context). Mixing them in the wrong role is a WARN.
3. **Error context** — flag bare `Err(e) => Err(e.into())` chains that lose context. Use `.context("doing X")` (anyhow) or `#[error("...{var}...")]` (thiserror) to preserve call-site information.
4. **`#[must_use]` on fallible constructors** — `Result`-returning constructors should be `#[must_use]` to prevent silently dropping errors.

## §5. Concurrency and async hazards

1. **Blocking in async** — flag `std::fs::read`, `std::sync::Mutex::lock`, `std::thread::sleep`, or any sync I/O inside an `async fn` or `tokio::task` block. Use `tokio::fs`, `tokio::sync::Mutex`, `tokio::time::sleep`, or `tokio::task::spawn_blocking` instead.
2. **`Send` / `Sync` leaks** — flag `Rc<...>` held across an `.await` point (won't compile, but is often a sign the API needs `Arc`); flag `RefCell` in async (same reason).
3. **Lock contention patterns** — flag `Mutex` held across an `.await` (the future is not cancel-safe and the lock may be poisoned); flag nested `Mutex` acquisitions (deadlock risk).
4. **Missing `spawn_blocking`** — CPU-bound work (hashing, compression, JSON parse of large payloads) inside an async context. Spawn it off the runtime.
5. **Select with cancellation** — `tokio::select!` with multiple branches where one holds a lock is a footgun. The unawaited branch's lock is leaked.

## §6. Async runtime and trait correctness

1. **Async-in-trait** — Rust 1.75+ supports `async fn` in traits natively. Pre-1.75 code often uses `async-trait`; flag if the project is on 1.75+ and still uses `async-trait` for non-dyn-compat reasons. Native async-in-trait avoids the `Box<dyn Future>` allocation.
2. **`Pin` and self-referential types** — flag manual `unsafe` `Pin` projection that could use `pin-project` or `pin-project-lite`. Manual `Pin` is a soundness risk.
3. **Send-ness of futures** — flag `async fn` returning a future that is not `Send` when the surrounding API is `async fn -> impl Future + Send` (common Tokio task boundary).

## §7. Performance smell-tests (light pass — not a perf audit)

This lens does a quick smell-test, not a full perf audit. For regression analysis or codegen investigation, use a dedicated perf pass (see `## Authoritative sources`).

- Flag `String`/`Vec` allocations inside hot loops where `&str` / a reusable buffer would do.
- Flag `clone()` in a loop that could be a single allocation followed by `iter_mut`.
- Flag `format!` in a tight loop; pre-allocate with `write!` to a `String` or use a `SmallString`/`CompactString`.
- Flag `HashMap`/`BTreeMap` lookups in O(n) per item in a loop that could be one `entry().or_insert_with()` pass.

## Authoritative sources

When a finding hinges on a specific clippy lint, an unsafe-code invariant, a rustdoc attribute, an edition-2024-specific rule, or a perf pattern that the embedded knowledge can't resolve with confidence, fetch the live canonical source. The trigger conditions below are the *only* reasons to fetch — fetching on every audit wastes tokens.

| Source | Canonical for | Fetch live when |
|---|---|---|
| `https://rust-lang.github.io/rust-clippy/master/` | The complete clippy lint index (name, category, default level, configuration key) | A specific clippy lint code appears in a finding and its meaning / default level / category / config key is unclear |
| `https://doc.rust-lang.org/clippy/` | The Clippy Book — lint levels, configuration semantics, `clippy.toml` reference | Auditing or authoring `clippy.toml`, choosing which lint group to enable per project type |
| `https://doc.rust-lang.org/reference/` | The Rust Reference — full language semantics | Auditing lifetimes, variance, trait coherence, visibility, or any language-semantic claim that the audit hinges on |
| `https://doc.rust-lang.org/nomicon/` | The Rustonomicon — unsafe, soundness, FFI, drop check, stacking, layout | Auditing `unsafe` blocks, FFI boundaries, or any soundness claim that the embedded knowledge can't back |
| `https://rust-lang.github.io/unsafe-code-guidelines/` | Unsafe Code Guidelines — formal invariants for `unsafe` | Verifying the specific invariant (`validity`, `aliasing`, `layout`) an `unsafe` block relies on |
| `https://doc.rust-lang.org/rustdoc/` | The rustdoc Book — doc-comments, doctests, intra-doc links, lint attributes | Auditing doc-comment conventions, doctest setup, `#[doc = "..."]` attributes, intra-doc link resolution, or `missing_docs`/`missing_doc_code_examples` behavior |
| `https://doc.rust-lang.org/edition-guide/` | The Rust Edition Guide — edition transitions incl. 2024 | Auditing edition-specific rules (gen keyword, lifetime capture, `expr_2021`, `IntoIterator` for arrays) or migration gaps from an earlier edition |
| `https://nnethercote.github.io/perf-book/` | The Rust Performance Book — inlining, codegen, allocation, allocator | A finding is a performance smell and the recommended remedy needs codegen or inlining justification |
| `https://rust-lang.github.io/rfcs/` | Rust RFCs | A design decision in the audited code cites an RFC, or a feature's stabilization status affects the audit (e.g. native async-in-trait, `let chains`) |