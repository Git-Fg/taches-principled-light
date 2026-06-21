# Test Runner and Coverage for Rust

Reference for `cargo-nextest`, coverage tooling, and feature matrix testing. Read it before adopting a faster test runner or adding coverage to a Rust project.

## §1. Why cargo-nextest

- Process-per-test execution (true parallelism, no shared state)
- 1.4-3.4× faster than `cargo test` on real-world projects (see [nexte.st/docs/benchmarks](https://nexte.st/docs/benchmarks/))
- Built-in retries (`--retries 2`)
- Per-test timeouts (`--test-timeout 60s`)
- JUnit XML output for CI (`--message-format junit`)
- No `--no-fail-fast` needed (default)

## §2. `.config/nextest.toml` profile

```toml
# Default profile for local dev
[profile.default]
retries = 0
test-threads = "num-cpus"
slow-timeout = { period = "30s", terminate-after = 2 }

# CI profile (used in GitHub Actions)
[profile.ci]
retries = 2
fail-fast = false
test-timeout = "120s"
```

Activate in CI:
```yaml
- run: cargo nextest run --profile ci --message-format junit > results.xml
```

## §3. When to adopt nextest

- Test suite > 200 tests, OR
- CI test job > 5 min, OR
- You need per-test timeouts, retries, or JUnit XML output

## §4. The Single-Binary Multi-Suite Pattern (recommended once tests/ grows)

When a project accumulates ≥10-20 root-level integration test files in `tests/`, each file becomes a **separate test binary** in Cargo's compilation model. Each binary re-links the entire dependency graph (axum, tokio, reqwest, …) and gets its own compilation unit. Three problems compound:

1. **Link-time tax** — 10-20× more link work per test cycle. On large dep trees, local edit-test loops go from seconds to minutes and CI runs pick up the same cost.
2. **Shared-helper dead-code blindness** — helpers in `tests/common/mod.rs` are shared via `mod common;` in every binary, but the compiler can only see usage *within* each binary. A helper used by only one suite gets flagged dead in every other binary, which forces a project-wide `#![allow(dead_code)]` in `common` and hides genuinely abandoned helpers.
3. **Wasted incremental compilation** — editing one helper re-links every binary that imports `common`.

**The pattern (the modern gold standard):** collapse the N root-level integration test files into a **single integration test binary** that mounts the individual files as submodules. Cargo compiles and links once; the compiler sees the full call graph across all suites.

### New directory structure

```
tests/
├── main.rs                # The single entry point (the only top-level test file)
├── common/
│   └── mod.rs             # Unchanged helpers
└── suites/
    ├── timeout_and_clamping.rs
    ├── models_endpoint_consistency.rs
    └── ...                # All other suites moved here
```

### `tests/main.rs` content

```rust
// Silence `unreachable_pub` on test helpers you mark `pub` — they are never
// consumed from outside this integration-test crate.
#![allow(unreachable_pub)]

mod common;  // shared test environment

// Declare each suite as a submodule under the single binary.
mod suites {
    mod timeout_and_clamping;
    mod models_endpoint_consistency;
    // ... all other suites
}
```

Each file in `tests/suites/` is an ordinary test module — `#[test] fn it_works() { ... }`. Because a suite lives at `crate::suites::<name>`, `super` points at `crate::suites` (which holds only the `mod` declarations), **not** the crate root — so `use super::*;` brings in nothing useful. Access shared helpers with `use crate::common;` (see "Idiomatic variant" below for the cleaner prelude pattern).

### Idiomatic variant: the prelude pattern (mdBook style)

The wrapper layout above groups suites under `crate::suites::*`, which means helper access needs `use crate::common;`. A cleaner, widely-used alternative (the one `rust-lang/mdBook` ships in `tests/testsuite/`) declares suites as **direct crate-root submodules** and exposes shared helpers through a `prelude` module:

```rust
// tests/main.rs
mod common;

mod book_test;
mod build;
mod cli;
// ... one `mod <name>;` per suite, all at the crate root

// Re-export the shared helpers every suite wants.
mod prelude {
    pub use crate::common::{setup, fixtures};
    pub use crate::book_test::BookTest;   // shared test harness type
}
```

Each suite then starts with `use crate::prelude::*;` (or `use super::prelude::*;` — both resolve, since suites are at the crate root). This keeps imports short and makes the "what every suite gets" list explicit and grep-able in one place.

**Gotcha — `unreachable_pub`:** items you mark `pub` inside the integration test crate (helpers, harness types) are never reachable from outside the crate, so the `unreachable_pub` lint fires on them. mdBook silences it once at the crate root with `#![allow(unreachable_pub, reason = "not needed in an integration test crate")]`. Add that to `tests/main.rs` when you start marking test helpers `pub`.

Both layouts are valid; pick the wrapper layout when you want suites namespaced under `suites::`, and the flat + prelude layout when you want the shortest helper imports and a single explicit re-export point.

### Why this works

- **Absolute dead-code accuracy** — `main.rs` is a single crate, so the compiler knows when an item in `common` is used anywhere across the N suites. You can safely remove every `#![allow(dead_code)]`. Any helper that is truly abandoned is now flagged.
- **10-20× faster incremental link speeds** — linking axum / tokio / reqwest once instead of N times saves minutes per local edit-test cycle and per CI run. Cargo's own docs note the N-binary layout "can take longer to compile, and may not make full use of multiple CPUs when running the tests" — the single binary fixes both.
- **Easy filtering** — `cargo test timeout_and_clamping` still runs only that suite (because it's the only integration test binary). `cargo nextest run -E 'test(/timeout_and_clamping/)'` is the nextest equivalent for finer filtering. The single-binary model does not reduce filter granularity.
- **No API change for the tests themselves** — each suite file looks the same as before; only its location and the parent `main.rs` declaration change.
- **No `Cargo.toml` change required** — Cargo discovers `tests/main.rs` as the single integration test binary by default. `[[test]]` entries are only needed if the project already customised them.

### When to adopt

- The project has ≥10-20 root-level integration test files in `tests/`, OR
- Linking an integration test binary takes > 10 s on a warm cache, OR
- `tests/common/mod.rs` carries a `#![allow(dead_code)]` because of the dead-across-binaries problem, OR
- CI integration-test job time is dominated by repeated link steps.

For brand-new projects with 1-3 integration tests, stay with Cargo's default N-binary model. The migration cost is real; the benefit only kicks in at scale.

### Migration playbook

1. `mkdir tests/suites`. Move every existing `tests/<name>.rs` (except `tests/common/`) to `tests/suites/<name>.rs`.
2. Create `tests/main.rs` with the `mod common;` + `mod suites { mod <name>; … }` shape above. Add `#![allow(unreachable_pub, reason = "not needed in an integration test crate")]` if any helpers are (or will be) marked `pub`.
3. In each moved file, add `use crate::common;` (NOT `use super::*;` — `super` from `crate::suites::<name>` is `crate::suites`, which holds only the `mod` declarations, so it imports nothing useful). If the file previously declared its own `mod common;`, delete that line — `common` is now declared once at the crate root. Keep any `use mycrate::...` (the library under test) as-is.
4. Delete `#![allow(dead_code)]` from `tests/common/mod.rs`. Run `cargo test`. Address any genuinely unused helpers by either deleting them or wiring them in.
5. CI: the single binary is the only integration test, so `cargo test` or `cargo nextest run --test main` runs everything. Per-suite filtering works via the test path: `cargo nextest run -E 'test(/timeout_and_clamping/)'`.
6. Commit as a single refactor commit so the link-time delta is attributable. Verify before/after with `cargo clean && time cargo test --no-run`.

### Anti-pattern: keep N binaries when N is large

If `tests/` carries 20 root-level files and CI is slow, do NOT keep the N-binary layout for "familiarity". The migration is mechanical and the link-time win is immediate.

### Anti-pattern: adopt the pattern at N = 2

At ≤5 root-level test files with a small dep graph, the migration cost (restructuring the directory, teaching the team) outweighs the link-time win. Stay with the Cargo default until a real signal appears.

### Anti-pattern: use the pattern when suites need different feature sets

If suite A needs `tokio` and suite B needs `actix`, the single-binary model forces both onto the same feature set. The N-binary model is required here — Cargo does not let a single integration binary conditionally enable features. Document the exception.

### Canonical source

The pattern is Cargo's official recommendation: see [Cargo Targets — Integration tests](https://doc.rust-lang.org/cargo/reference/cargo-targets.html#integration-tests), which states: *"If you have a lot of integration tests, you may want to consider creating a single integration test, and split the tests into multiple modules. The libtest harness will automatically find all of the `#[test]` annotated functions and run them in parallel."* The same picture from a different angle: [The Cargo Book — Tests](https://doc.rust-lang.org/cargo/guide/tests.html).

A proven real-world implementation is [`rust-lang/mdBook`'s `tests/testsuite/main.rs`](https://github.com/rust-lang/mdBook/blob/main/tests/testsuite/main.rs) — the flat + prelude layout above is modelled on it. Per-suite filtering with nextest uses filter-set expressions: see the [nextest filter expression reference](https://nexte.st/docs/filterset/). For a single integration binary, plain `cargo test <substring>` also works because there is only one binary to match against.

## §5. cargo-hack for feature matrix testing

```yaml
- name: Feature matrix
  run: cargo hack check --feature-powerset --no-default-features
```

Use when you have ≥3 features to ensure every combination compiles.

## §6. cargo-llvm-cov (preferred for Linux/macOS)

```bash
cargo install cargo-llvm-cov
cargo llvm-cov nextest --html
# open target/llvm-cov/html/index.html
```

In CI:
```yaml
- name: Coverage
  run: cargo llvm-cov nextest --lcov --output-path lcov.info
- uses: codecov/codecov-action@v4
  with:
    files: lcov.info
```

## §7. cargo-tarpaulin (cross-platform, less accurate)

Use only when you need Windows support and cargo-llvm-cov won't work.

## §8. Coverage scope

Start with line coverage. Add branch coverage when you have a coverage target:
```bash
cargo llvm-cov nextest --branch
```

## §9. Benchmarking (when needed)

**Criterion (default):**
```rust
// benches/parse_bench.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_parse(c: mut Criterion) {
    c.bench_function("parse small input", |b| {
        b.iter(|| mycrate::parse(black_box("input")))
    });
}

criterion_group!(benches, bench_parse);
criterion_main!(benches);
```

Run: `cargo bench`. For CI, use `bencher.dev` or `criterion-cycles` to track regressions.

**divan** (rising alternative): faster, simpler, smaller ecosystem. Use when Criterion's stat-sig machinery is overkill.

**gungraun** (formerly **iai-callgrind**; deterministic): use when you need deterministic, single-run benchmarks via Valgrind's Callgrind/Cachegrind — immune to system noise. No Windows support (Valgrind limitation).

**When to add benchmarks:**
- You have a perf-sensitive hot path
- CI shows build-time regression and you want to track it
- You want to detect perf regressions before users do

DO NOT add benchmarks preemptively. Each one is a maintenance cost.

## Authoritative sources

When a test-runner profile, a coverage-tool choice, a filter-expression syntax, or a benchmark library's API is in question, fetch the live canonical source. The triggers below are the *only* reasons to fetch.

| Source | Canonical for | Fetch live when |
|---|---|---|
| `https://nexte.st/` | cargo-nextest docs (profiles, retries, JUnit, timeouts) | Authoring `.config/nextest.toml` or diagnosing a retry/timeout issue |
| `https://nexte.st/docs/filterset/` | nextest filter-set expressions (`-E 'test(/name/)'`) | Building a per-suite/per-test filter for the single-binary multi-suite pattern |
| `https://doc.rust-lang.org/cargo/reference/cargo-targets.html#integration-tests` | Cargo's integration-test target model (the single-binary recommendation) | Confirming why N root-level test files cost N× link time |
| `https://github.com/taiki-e/cargo-llvm-cov` | cargo-llvm-cov (LLVM-based coverage, line vs branch) | Setting up coverage or choosing llvm-cov over tarpaulin |
| `https://github.com/xd009642/tarpaulin` | cargo-tarpaulin (cross-platform coverage, incl. Windows) | Choosing tarpaulin when llvm-cov won't cover the target |
| `https://github.com/taiki-e/cargo-hack` | cargo-hack (`--feature-powerset`, `--each-feature`) | Setting up the feature-matrix test |
| `https://nnethercote.github.io/perf-book/` | The Rust Performance Book (codegen, allocation, inlining) | A coverage/test gap traces to a perf-sensitive hot path |
| `https://github.com/bheisler/criterion.rs` | Criterion (statistics-driven wall-clock benchmarking) | Authoring a `#[bench]` or interpreting Criterion's statistics output |
| `https://github.com/nvzqz/divan` | Divan (lighter wall-clock benchmarking) | Choosing divan over Criterion |
| `https://github.com/gungraun/gungraun` | Gungraun (formerly iai-callgrind; deterministic Valgrind-based benchmarking) | Needing deterministic, single-run benchmarks immune to system noise |
