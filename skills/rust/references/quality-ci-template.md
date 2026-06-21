# GitHub Actions CI Template for Rust

Reference for the canonical Rust CI workflow as of 2026. Copy this file into `.github/workflows/ci.yml` and adjust the OS matrix, MSRV, and audit tools. Read it before setting up CI for a new Rust project.

## §1. Canonical CI YAML

`.github/workflows/ci.yml`:

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Cancel in-progress runs on PR branches (saves 20+ min/force-push on large codebases).
# Never cancel on main — every push there should complete.
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}

env:
  CARGO_TERM_COLOR: always
  CARGO_INCREMENTAL: 0          # disable incremental in CI (faster, smaller cache)
  RUSTFLAGS: "-D warnings"      # deny warnings for your crate, not transitive deps

jobs:
  # Cheapest check first. Everything else depends on it.
  format:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@nightly
        with:
          components: rustfmt
      - run: cargo fmt --all -- --check

  # Cross-platform test matrix. Add windows-latest only if you claim cross-platform support.
  test:
    needs: format
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo test --locked --all-features
      - run: cargo test --doc --locked

  # Lint (depends on format so we fail fast).
  lint:
    needs: format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy
      - uses: Swatinem/rust-cache@v2
      - run: cargo clippy --all-targets --locked -- -D warnings

  # Build docs (also catches broken intra-doc links).
  doc:
    needs: format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
      - run: cargo doc --no-deps --all-features --locked
        env:
          RUSTDOCFLAGS: "-D warnings"

  # Audit only on main — advisory DB changes shouldn't break PRs.
  audit:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: taiki-e/install-action@v2
        with:
          tool: cargo-deny
      - run: cargo deny check

  # MSRV check (run the same matrix's MSRV).
  msrv:
    needs: format
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@1.81.0   # match your MSRV
      - uses: Swatinem/rust-cache@v2
      - run: cargo check --locked
```

## §2. Alternative: setup-rust-toolchain one-liner

`actions-rust-lang/setup-rust-toolchain` bundles `dtolnay/rust-toolchain` + `Swatinem/rust-cache`:

```yaml
- uses: actions/checkout@v4
- uses: actions-rust-lang/setup-rust-toolchain@v1
  with:
    toolchain: stable
    cache: true                              # bundles Swatinem/rust-cache
    components: rustfmt, clippy
```

This is the canonical stack as of 2026: `dtolnay/rust-toolchain` (or `actions-rust-lang/setup-rust-toolchain` which bundles it) + `Swatinem/rust-cache@v2` + `taiki-e/install-action` for pre-built cargo subcommands. Source: rust-project-primer CI chapter.

**For Forgejo/Gitea:** same YAML, just replace `actions/checkout` with `actions/checkout@v4` and the cache action works on self-hosted runners using the native Gitea cache backend.

## Authoritative sources

When a GitHub Actions concurrency rule, an action's inputs, or a cache-key question is in doubt, fetch the live canonical source. The triggers below are the *only* reasons to fetch.

| Source | Canonical for | Fetch live when |
|---|---|---|
| `https://docs.github.com/en/actions/using-jobs/using-concurrency` | GitHub Actions concurrency (`cancel-in-progress`, `group` keys) | Tuning the concurrency rule or diagnosing a cancelled-run bug |
| `https://github.com/actions-rust-lang/setup-rust-toolchain` | The one-liner action that bundles toolchain + cache + components | Choosing between the one-liner and the separate dtolnay/Swatinem actions |
| `https://github.com/dtolnay/rust-toolchain` | Toolchain-install action (pinning stable/nightly/MSRV, components) | Pinning a specific toolchain version or adding a component |
| `https://github.com/Swatinem/rust-cache` | Cargo registry + build-artifact cache action | Diagnosing cache misses or sizing the cache key |
| `https://github.com/taiki-e/install-action` | Pre-built cargo-subcommand installer (cargo-deny, nextest, hack) | Adding a cargo subcommand to CI without a build-from-source step |
