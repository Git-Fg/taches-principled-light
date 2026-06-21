# Publishing and Dependency Management for Rust

Reference for publishing a crate to crates.io (first publish + ongoing) and the dependency management discipline (MSRV enforcement, vendoring, replacement). Read it before your first `cargo publish` and before adding vendoring or MSRV checks.

## §1. First publish

```bash
# 1. Make sure metadata is set (see the Cargo.toml template in the SCAFFOLD mode's `references/scaffold-cargo-and-features.md` §2)
# 2. Verify it builds clean
cargo build --release
cargo test --all-features --locked
cargo clippy --all-targets --locked -- -D warnings

# 3. Dry run first — ALWAYS
cargo publish --dry-run --allow-dirty
# Inspect the .crate file that gets packaged

# 4. Real publish
cargo login              # paste API token from https://crates.io/me
cargo publish
```

## §2. Cargo 1.90+ (Sept 2025) — native workspace publishing

Cargo 1.90 introduced native workspace publishing: `cargo publish --workspace` from the workspace root. For older versions, use `release-plz` and set `publish = false` on internal crates, publishing only the public ones.

## §3. Undo (within reason)

After a publish, you can yank a version (`cargo yank --vers 0.1.2`) but **you cannot delete it**. Yanked versions are skipped by default in new resolution, but existing `Cargo.lock` files keep using them. Yank for "this was a serious bug" or "I uploaded secrets"; don't yank for "I want to use a different number."

## §4. Dependency management — MSRV-aware resolver

Ensures all picked deps support your MSRV (since Rust 1.81):

```toml
# Cargo.toml
[package]
rust-version = "1.81"     # documents your MSRV

# .cargo/config.toml
[resolver]
incompatible-rust-versions = "fallback"   # try MSRV; fall back to newer only if a dep requires it
```

## §5. Vendored sources (offline / reproducible builds)

```toml
# .cargo/config.toml
[source.crates-io]
replace-with = "vendored-sources"

# Then populate with:
cargo vendor
```

Use for: air-gapped builds, reproducible CI without network, license compliance (you ship the vendored deps with the source). Most projects don't need it; the cargo-deny → cargo-vet → Dependabot supply-chain ladder (initial setup is in the QUALITY mode's `references/quality-supply-chain-ladder.md`) is the lighter-weight alternative.

## Authoritative sources

When a `cargo publish`/`yank`/`vendor` flag, a resolver-config question, or a workspace-publish capability is in question, fetch the live canonical source. The triggers below are the *only* reasons to fetch.

| Source | Canonical for | Fetch live when |
|---|---|---|
| `https://doc.rust-lang.org/cargo/commands/cargo-publish.html` | `cargo publish` (`--dry-run`, `--allow-dirty`, `--workspace`) | Running the first-publish playbook or diagnosing a publish failure |
| `https://crates.io/me` | crates.io account / API token page | Running `cargo login` for the first time |
| `https://doc.rust-lang.org/cargo/commands/cargo-yank.html` | `cargo yank` (semantics: skipped in new resolution, NOT deleted) | Deciding whether to yank, or what a yank does and doesn't do |
| `https://doc.rust-lang.org/cargo/reference/resolver.html` | Resolver config (`incompatible-rust-versions = "fallback"`) | Enabling the MSRV-aware resolver in `.cargo/config.toml` |
| `https://doc.rust-lang.org/cargo/commands/cargo-vendor.html` | `cargo vendor` (source replacement for offline/reproducible builds) | Setting up vendored sources |
| `https://github.com/rust-lang/cargo/blob/master/CHANGELOG.md` | Cargo release notes (e.g. 1.90 native `cargo publish --workspace`) | Confirming which Cargo version added workspace publishing |
