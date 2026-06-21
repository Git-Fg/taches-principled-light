# Cargo.toml Template, MSRV Policy, and Feature Flags

Reference for the lib/bin decision tree, the recommended Cargo.toml template, the MSRV policy, and the feature flag playbook. Read it before scaffolding a new Rust project.

## §1. Decision tree: lib-only / bin-only / lib+bin

```
What does the user want?
├─ Library consumed by others (or no clear binary need)
│  → lib-only: `cargo new --lib mycrate`
│
├─ Binary that may grow complex (CLI app, server, tool)
│  → lib+bin: `cargo new --bin mytool` + add src/lib.rs
│  (ripgrep, bat, fd pattern: logic in lib, thin main.rs)
│
└─ Pure single-file script or throwaway
   → bin-only: `cargo new --bin throwaway`
```

**Default recommendation: lib+bin** for anything that may grow. The cost of adding a lib.rs is one file; the cost of refactoring a main.rs into a lib later is much higher.

**Signal to go lib+bin:** the user mentions "test", "reuse", "library", or names subcommands.

## §2. Cargo.toml template — recommended variant

```toml
[package]
name = "mycrate"
version = "0.1.0"
edition = "2024"                          # default since Rust 1.85 (Feb 2025)
rust-version = "1.81"                     # MSRV — see §3
description = "One-line description for crates.io search"
license = "MIT OR Apache-2.0"
repository = "https://github.com/you/mycrate"
documentation = "https://docs.rs/mycrate"
readme = "README.md"
keywords = ["mycategory"]                # max 5, lowercase, alphanumeric
categories = ["development-tools"]        # max 5, must exist on crates.io
include = ["src/**/*", "Cargo.toml", "README.md", "LICENSE*"]
exclude = [".github/", "tests/fixtures/"]
publish = true                            # set false for internal-only crates

[lib]
name = "mycrate"                          # default; override if crate and lib name differ
path = "src/lib.rs"

[[bin]]
name = "mytool"
path = "src/main.rs"

[dependencies]
# minimal — add as needed

[dev-dependencies]
# test-only deps

[features]
default = []                              # see §4
# example-feature = ["dep:serde"]

[profile.release]
lto = "thin"
codegen-units = 1
strip = "symbols"
```

`resolver = "2"` is implied for `edition = "2021"` and `edition = "2024"`. Only set it explicitly for a virtual workspace.

## §3. MSRV policy

**Default MSRV for new projects: `rust-version = "1.81"`** (Sept 2024 release). This unlocks:
- MSRV-aware dependency resolver (RFC 3537) — `cargo update` no longer picks newer-than-MSRV versions
- Edition 2024 features (when paired with `edition = "2024"`)
- `let-chains`, `if let` chains (stabilized in 1.88/1.85)
- Modern async, trait improvements

**MSRV policy template:**
1. **Pick N-2 stable** as your MSRV (the version before last + the one before that). E.g., if current stable is 1.88, MSRV is 1.85.
2. **Document the policy** in README and a top-level MSRV comment in Cargo.toml.
3. **CI-test the MSRV** with a separate `msrv` job pinning `dtolnay/rust-toolchain@<MSRV>` and running `cargo check --locked` — the canonical 6-job CI template (format → test → lint → doc → audit → msrv) is in the CI reference.
4. **MSRV bumps are breaking** if downstream users compile against you. Treat them as a minor-version bump at minimum; many projects (RustCrypto, rust-bitcoin) treat MSRV bumps as major. Ask the user.

**Tools:**
- `cargo +1.81 check` — local MSRV test
- `cargo-msrv find` — automated MSRV detection from your dep tree
- CI matrix (the matrix pattern lives in the CI reference's canonical 6-job workflow)

**Important historical note:** the `rust-version` field was added in **Cargo 1.56 (Oct 21, 2021)** as *advisory only*. The MSRV-aware resolver that actually *enforces* MSRV came in **Rust 1.81 (Sept 5, 2024)**. Older advice that says "rust-version is enforced since 1.56" is wrong.

## §4. Feature flag playbook

**The rule (per Cargo Reference):** features *should* be additive — they add code, never remove it. Cargo Reference uses the soft "should", not "MUST". The mutual-exclusion escape hatch is documented in Cargo Reference §"Mutually exclusive features" — it is rare but valid when guarded by `compile_error!`.

**5 rules for feature flags:**
1. **Naming:** short, lowercase, no underscores if possible (`serde`, `tls`, `jemalloc`).
2. **Defaults:** keep `default = []` minimal. Users who want a feature should opt in.
3. **Additive only** (with documented mutual-exclusion escape hatch).
4. **Public features ≠ internal features** — use `__internal` prefix (double underscore) for testing-only features that are NOT public API. See reqwest's `__rustls`/`__native-tls` pattern.
5. **Test with the feature matrix:** use `cargo-hack` in CI to test all feature combinations.

**Example internal-feature pattern (from reqwest):**
```rust
// in Cargo.toml
[features]
default = ["default-tls"]
default-tls = ["__native-tls"]
rustls-tls = ["__rustls"]
__rustls = ["dep:rustls", "dep:rustls-pemfile", "dep:rustls-webpki-roots"]
__native-tls = ["dep:openssl"]

// in src/lib.rs
#[cfg(feature = "__rustls")]
pub(crate) mod rustls_impl;
```

The `__` prefix signals "internal, not part of public API, may disappear at any time" (reqwest's documented comment).

**Deprecation cycle:** when removing a feature post-1.0: `warn` in 1.x, `#[deprecated]` in 1.x+1, remove in 1.x+2. Use `#[cfg_attr(feature = "old-feature", deprecated = "use new-feature instead")]` for items.

## Authoritative sources

When a manifest field's exact schema, the MSRV-resolver semantics, or the additive-feature rule is in question, fetch the live canonical source. The triggers below are the *only* reasons to fetch — fetching on every scaffold wastes tokens.

| Source | Canonical for | Fetch live when |
|---|---|---|
| `https://doc.rust-lang.org/cargo/reference/manifest.html` | The Manifest schema (every `[package]`/`[lib]`/`[[bin]]`/`[features]` field) | Auditing or authoring a `Cargo.toml` field's correctness, deprecation, or exact schema |
| `https://doc.rust-lang.org/cargo/reference/features.html` | Cargo features reference (additivity, `dep:` syntax, mutual-exclusion escape hatch, optional deps) | Designing or reviewing a `[features]` table; deciding whether a feature combination is valid |
| `https://doc.rust-lang.org/edition-guide/` | The Edition Guide (2024 stabilization, what each edition unlocks) | Choosing `edition` or auditing edition-locked behavior |
| `https://doc.rust-lang.org/cargo/reference/rust-version.html` | `rust-version` field semantics and the MSRV-aware resolver (RFC 3537, Cargo 1.81+) | Setting or questioning an MSRV; verifying when the resolver enforces vs. merely advises |
| `https://github.com/taiki-e/cargo-hack` | cargo-hack (`--feature-powerset`, `--each-feature`, feature-matrix testing) | Setting up the CI feature-matrix test the feature-flag playbook requires |
| `https://github.com/foresterre/cargo-msrv` | cargo-msrv (automated MSRV detection) | Running `cargo msrv find` to verify a declared MSRV against the real dep tree |
| `https://rust-lang.github.io/api-guidelines/` | Rust API Guidelines (feature naming, `C-FEATURE` conventions) | Deciding feature-flag naming or whether a feature counts as public API |
