# Developer Experience and Tool Matrix for Rust

Reference for local dev file-watchers, build-speed configuration, toolchain pinning, CI cache, and the consolidated tool matrix. Read it before optimizing local dev loops or adding more tooling.

## §1. `bacon` for file-watching

```bash
cargo install bacon --locked
bacon test       # auto-runs nextest on file change
bacon clippy     # auto-runs clippy on file change
```

## §2. `.cargo/config.toml` for build speed

```toml
# Use a faster linker (2-10x faster linking on Linux)
[target.x86_64-unknown-linux-gnu]
linker = "clang"
rustflags = ["-C", "link-arg=-fuse-ld=mold"]

# Use sccache if available
[build]
rustc-wrapper = "/path/to/sccache"
```

## §3. Toolchain pinning (`rust-toolchain.toml`)

```toml
[toolchain]
channel = "1.85.0"                       # pin to a specific version
components = ["rustfmt", "clippy", "rust-analyzer"]
profile = "minimal"                      # skip docs, faster install
```

## §4. CI cache

`Swatinem/rust-cache@v2` is the standard. Caches Cargo registry + build artifacts. Cuts CI time 30-70%.

## §5. Tool matrix (quick reference)

| Tool | Purpose | When to adopt |
|---|---|---|
| `rustfmt` | Formatting | Day 1 (non-negotiable) |
| `clippy` | Lints | Day 1; pedantic for libs |
| `cargo-nextest` | Fast test runner | Test suite > 200 OR CI > 5 min |
| `cargo-hack` | Feature matrix testing | ≥3 features |
| `cargo-deny` | License + advisory + ban + source | Day 1 of published crate |
| `cargo-audit` | RUSTSEC check (subsumed by deny) | Standalone if you don't want deny |
| `cargo-vet` | Supply-chain audits | Stage 2+ (security-critical) |
| `cargo-machete` | Unused dependencies | Weekly in CI |
| `cargo-outdated` | Out-of-date deps | Weekly, not in PR CI |
| `criterion` / `divan` | Benchmarking | When you have perf-sensitive code |
| `cargo-llvm-cov` | Coverage | When you have a coverage target |
| `cargo-mutants` | Mutation testing | Mature, high-stakes code (weekly) |
| `bacon` / `cargo-watch` | Local dev file-watcher | Day 1 |
| `sccache` | Shared compilation cache | CI > 10 min |
| `mold` / `lld` / `wild` | Fast linker | When link time > 5s |
| `rust-analyzer` | LSP | Day 1 |
| `dtolnay/rust-toolchain` | GH Action: toolchain | Day 1 on GH |
| `Swatinem/rust-cache@v2` | GH Action: cache | Day 1 on GH |
| `taiki-e/install-action` | GH Action: pre-built cargo subcommands | When you use nextest/hack/audit |

## Authoritative sources

When a dev-tool's config schema, a toolchain-pin question, or a CI-cache behavior is in doubt, fetch the live canonical source. The triggers below are the *only* reasons to fetch.

| Source | Canonical for | Fetch live when |
|---|---|---|
| `https://dystroy.org/bacon/` | bacon (file-watcher, jobs, `bacon.toml`, key bindings) | Configuring bacon jobs or key bindings |
| `https://github.com/mozilla/sccache` | sccache (shared compilation cache) | Diagnosing cache misses or sizing the cache |
| `https://github.com/rui314/mold` | mold (fast linker; also `lld`, `wild`) | Choosing a linker or diagnosing a link-step regression |
| `https://rust-lang.github.io/rustup/overrides.html#the-toolchain-file` | `rust-toolchain.toml` schema (channel, components, profile) | Pinning the toolchain or adding a component |
| `https://github.com/Swatinem/rust-cache` | The Cargo cache GitHub Action | Tuning CI cache behavior or diagnosing a miss |
| `https://doc.rust-lang.org/cargo/reference/config.html` | The `.cargo/config.toml` reference (linker, rustflags, build settings) | Authoring or auditing `.cargo/config.toml` build-speed tweaks |
