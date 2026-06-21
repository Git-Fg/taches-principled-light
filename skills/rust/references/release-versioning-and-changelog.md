# Versioning and Changelog Tooling for Rust

Reference for Cargo semver versioning (including the contested MSRV policy) and the changelog tooling decision tree. Read it before tagging a release or choosing a changelog generator.

## §1. Pre-1.0 vs 1.0+ semver

| Aspect | `0.x.y` | `1.x.y` and above |
|---|---|---|
| API stability | "Anything MAY change at any time" (semver.org) | Hard commitment: major bump required for breaking change |
| Cargo compat rule | `^0.x` accepts `>=0.x.0, <0.(x+1).0` — so `^0.3.5` means `>=0.3.5, <0.4.0` | Standard semver: `^1.2.3` means `>=1.2.3, <2.0.0` |
| When to commit to 1.0 | When you have a stable, documented API that the ecosystem has come to depend on | N/A |
| Adding a feature | Bump minor (`0.3.5` → `0.4.0`) | Bump minor |
| Bug fix | Bump patch (always safe) | Bump patch |
| Breaking change | Bump minor (`0.x` → `0.(x+1)`) | Bump major |

**Practical decision rule:** If your crate is `0.0.x`, change anything any time, stay there until API is roughly stable. If `0.x.y` (x ≥ 1), you've made a soft commitment to `0.x` API stability — breakages bump `0.x → 0.(x+1)`. Commit to 1.0 when *you* are tired of eating the breaking-change cost AND downstream users would feel the churn.

## §2. The `SemVer trick` (1.0.0 development)

If you want 1.0 signaling (semver commitment) before your API is truly stable:
```toml
# in Cargo.toml
[dependencies]
mycrate = "~1.0.0"     # means exactly 1.0.x; pre-1.1
```

Use this when you want downstream users to commit to your crate but you still want patch-level flexibility. Rare in practice; pre-1.0 with the `0.x` stability signal is usually enough.

## §3. MSRV policy (THE contested decision)

**There is no Rust community consensus.** Two camps:

| Camp | Position | Examples |
|---|---|---|
| **api-guidelines (advisory)** | MSRV bumps are *not* breaking → minor bump post-1.0, patch bump pre-1.0 | The official Rust API Guidelines recommendation |
| **Cornerstone crates (breaking)** | MSRV bumps ARE breaking → major bump post-1.0 | RustCrypto, rust-bitcoin, several large dependency-heavy projects |

**Why it matters now (2026):** Rust 1.84 (Jan 2025) shipped the **MSRV-aware resolver** (RFC 3537) + `incompatible-rust-versions = "fallback"` resolver mode. This makes MSRV enforcement much cheaper than in 2023 — the old "manual Cargo.lock" workaround (BurntSushi 2023) is no longer needed.

**The skill must ask the user which camp they're in.** Don't assume.

**Tools:**
- Document MSRV in `[package].rust-version` (advisory, but consumers respect it)
- CI-test the MSRV (the `msrv` job is part of the canonical 6-job CI workflow: format → test → lint → doc → audit → msrv)
- Use `cargo +1.81 update` (or whatever your MSRV is) to ensure dep tree stays MSRV-compatible

## §4. Workspace lockstep versioning

When all members of a workspace share a version (the cargo, tokio, axum pattern):
```toml
# workspace Cargo.toml
[workspace.package]
version = "0.5.0"   # all members inherit via version.workspace = "true"
```

Bump one number; all members publish together. The release tool (`release-plz`, `cargo-release`) coordinates the version bump + tag + publish across all members. The full workspace versioning + inheritance pattern is in the WORKSPACE mode's `references/workspace-decisions.md`.

## §5. Changelog tooling decision

Three archetypes; pick by workflow, not feature list.

### 5.1 git-cliff (Rust binary, git-driven)
- **Best for:** "I want git history to drive my changelog"
- **Pros:** Super fast (Rust binary), Tera templates, conventional commits parsing, no network
- **Cons:** Git history can be noisy; you need disciplined commit messages
- **Install:** `cargo install git-cliff`
- **Config:** `cliff.toml` at repo root

### 5.2 release-please (Node, Google-built)
- **Best for:** "I want a Release PR workflow that the entire team understands"
- **Pros:** Multi-language, GitHub-native (creates a PR that you review + merge → publish), conventional commits
- **Cons:** Requires Node, less Rust-idiomatic
- **Install:** GitHub Action: `googleapis/release-please-action@v4`

### 5.3 Hand-curated (what serde, tokio, cargo do)
- **Best for:** "Mature project with curated user-facing changelog"
- **Pros:** Polished, user-focused, no noise
- **Cons:** Manual work; reviewer burden; easy to forget

**Decision tree:**
- Greenfield project? → **git-cliff** (or release-please if your team is JS/TS-heavy)
- Want a Release PR workflow? → **release-please**
- Mature Rust project with curated changelog? → hand-written, keep doing it

## Authoritative sources

When a semver classification, the `0.x` compat rule, the MSRV-bump-is-breaking question, or a changelog tool's config is in question, fetch the live canonical source. The triggers below are the *only* reasons to fetch.

| Source | Canonical for | Fetch live when |
|---|---|---|
| `https://doc.rust-lang.org/cargo/reference/semver.html` | Cargo's SemVer compatibility rules (incl. the `^0.x` special case) | Classifying a change as breaking/compatible, or the `0.x` compat rule is in question |
| `https://semver.org/` | The SemVer 2.0 specification | A versioning decision cites semver.org directly |
| `https://doc.rust-lang.org/cargo/reference/rust-version.html` | `rust-version` and the MSRV-aware resolver (RFC 3537, Cargo 1.84+) | Resolving the contested "MSRV bump is breaking" question for this project |
| `https://rust-lang.github.io/api-guidelines/` | API Guidelines MSRV policy (the "advisory, not breaking" camp) | Citing the api-guidelines position vs the RustCrypto/rust-bitcoin "breaking" camp |
| `https://git-cliff.org/` | git-cliff (git-driven changelog generator, `cliff.toml`) | Configuring `cliff.toml` or conventional-commits parsing |
| `https://github.com/googleapis/release-please` | release-please (Release-PR workflow, multi-language) | Setting up the release-please GitHub Action |
