# Dependency Hygiene and Manifest Audit Reference

Used by the `"audit dependency hygiene"` lens (Lens 2 of REVIEW). Audits `Cargo.toml` version constraints, the dependency tree for duplicates and bloat, and manifest consistency. Distinct from the supply-chain lens (Lens 5): this lens audits graph **hygiene** (predictability, bloat, drift), not trust/CVEs. For trust and CVE scanning, the `"audit supply chain"` lens reads `references/quality-supply-chain-ladder.md` and the deny.toml contract.

Lens 2 spawns with the contract defined in `references/review-orchestration.md` and produces findings in that schema.

## §1. Cargo.toml version-constraint audit

1. **Wildcard versions** — `"*"` (with or without `default-features = false`) is a BLOCKER. Breaks reproducibility; downstream cannot compute a unique resolution; bypasses the entire Cargo semver contract. Replace with a floor range (`"1.2"`) or a caret range (`"1.2.3"`).
2. **Path dependencies without version fallback** — in any crate intended to be published, a `path = "..."` dep MUST also have `version = "..."` (a registry-published version). Without it, downstream users cannot resolve the dep from crates.io. BLOCKER.
3. **Floats and `git` deps in published crates** — `git = "..."` in a published crate is a BLOCKER for the same reason. Path is acceptable for workspace-internal members; `git` is not.
4. **Overly wide ranges** — `"0.1"` and `"0.1.*"` are acceptable for pre-1.0 deps; `"1"` (no minor) is a smell (means "any 1.x.y"); `"2.*"` is a smell. Use a caret range.
5. **Unmaintained deps with maintained successors** — flag any dep whose repo has not had a release in > 2 years AND has a maintained successor. Examples (not exhaustive): `lazy_static` → `std::sync::LazyLock` (1.80+) or `once_cell::sync::Lazy`; `failure` → `thiserror` (library) or `anyhow` (binary); `rand` 0.7 → 0.8 (deprecation of `OsRng::new()` etc.); `tokio` 0.2 → 0.3 (massive API overhaul). WARN; BLOCKER if the crate has a known unmaintained-security-advisory link.

## §2. Dependency-tree and duplicate-version detection

1. **Multiple major versions of the same crate** — `cargo tree -i <crate>` is the canonical tool. Multiple majors of `tokio`, `serde`, `syn`, `bytes`, `hyper`, `http`, `hashbrown`, `parking_lot`, `rustls-webpki` are the usual suspects. WARN unless the major-version collision is in a feature flag combination that excludes a chunk of the dep tree (in which case document the reason in the manifest).
2. **Multiple minor versions across the tree** — usually indicates indirect-dep drift. Run `cargo update -p <crate>@<old>` or pin in the workspace's `[workspace.dependencies]`. WARN.
3. **Heavy dep for trivial use** — `reqwest` + `openssl` for a CLI flag fetch; `clap` 4 derive for a 2-flag CLI (use `pico-args` or `lexopt`); `serde` + `serde_json` for a single config-file read (use `toml` or a manual parse); `ndarray` for a 4×4 matrix (write the math). WARN with concrete substitution.
4. **Cyclic or self-referential workspace deps** — usually caught by cargo at build time. If the audit finds one, it's a BLOCKER (workspace structure error).
5. **Optional dep with no users** — `cargo machete` (or `cargo udeps`) is the tool. An optional dep listed in `[dependencies]` that is never used in any feature combination is dead weight in the lockfile. WARN.

## §3. Manifest consistency

1. **`rust-version` vs `clippy.toml` MSRV** — must match. `clippy.toml`'s `msrv` is the floor for MSRV-aware lints; `Cargo.toml`'s `rust-version` is the floor for edition-aware lints and resolver behavior. A drift is a WARN (false positives in clippy).
2. **`[features]` discipline** —
   - Default features must be additive (the `additive-defaults` pitfall in `workspace-decisions.md` does not apply to single-crate `default`, but the principle does).
   - `__internal` prefix for non-public sub-features.
   - `#[doc(hidden)]` on items gated behind `__internal` (otherwise they appear in `cargo doc` and on docs.rs as if public).
3. **Workspace inheritance (1.64+)** — if the project is a workspace, `[workspace.package]`, `[workspace.dependencies]`, and `[workspace.lints]` should be used for any value shared across ≥ 2 members. A single-crate `[lints]` table is fine for non-workspace crates. WARN if duplicated.
4. **`[lints.clippy]` table (1.74+)** — preferred over the legacy `#![warn(clippy::...)]` pragmas. Verify it exists and is the single source of lint config.
5. **`[package]` metadata completeness** — `description`, `license`, `repository`, `readme`, `keywords`, `categories`. Missing metadata is a WARN for published crates; BLOCKER for crates about to publish (zero crates.io search rank).
6. **`publish = false`** on workspace-internal-only members. A workspace member published to crates.io by accident leaks the internal API surface. BLOCKER if the member is genuinely internal.

## §4. `deny.toml` shape check

The `"audit dependency hygiene"` lens reads `deny.toml` only for its **shape** (config correctness). The `"audit supply chain"` lens reads it for its **policy** (license/source/version enforcement). Boundaries:

- This lens checks: schema is current (cargo-deny 0.19+, no removed keys like top-level `vulnerability` or `unlicensed` — see `quality-supply-chain-ladder.md` §2 for the verified schema); all required sections present.
- This lens does NOT check: whether the configured license allow-list is appropriate; whether the bans list is comprehensive; whether ignored advisories are still valid.

## §5. Lockfile hygiene

1. **`Cargo.lock` commit policy** — committed for binaries, applications, and any workspace with a binary member; NOT committed for pure libraries (per `workspace-lockfile-and-cross-crate.md`). Drift from the policy is a WARN.
2. **`Cargo.lock` freshness** — if the manifest changed without a `Cargo.lock` regen, `cargo metadata` will detect it at build time. For audit purposes, run `cargo metadata --format-version 1` and confirm `lock_file` is not stale.
3. **Checksum/source URL in lockfile** — every entry has `checksum`. The `source` field should be a real registry URL or a `git+` URL. Unknown sources are the supply-chain lens's job, not this one.

## §6. Out of scope

- **CVE / advisory detection** — the supply-chain lens (Lens 5) reads `quality-supply-chain-ladder.md` and `release-supply-chain-maintenance.md`. Do not duplicate.
- **License compatibility review** — supply-chain lens.
- **Crate health (last release date, open issues)** — supply-chain lens (cargo-vet covers it).
- **Internal-only features leaking to public** — the public-API lens (Lens 4) reads `review-public-api.md`.

## Authoritative sources

| Source | Canonical for | Fetch live when |
|---|---|---|
| `https://doc.rust-lang.org/cargo/` | The Cargo Book — full reference | Cargo feature/manifest/workspace/resolver semantics are unclear (e.g. `resolver = "3"`, MSRV-aware resolver, `cargo install --locked`) |
| `https://doc.rust-lang.org/cargo/reference/manifest.html` | The Manifest schema — every `Cargo.toml` field | Auditing a `Cargo.toml` field's correctness, deprecation, or schema (e.g. `rust-version` vs `edition`, `[lints]` table syntax, `default-run`) |
| `https://rustsec.org/advisories/` | RUSTSEC advisory listing | A `Cargo.lock` entry is flagged by cargo-deny and you need the advisory ID, affected versions, or the "yanked" status |
| `https://github.com/rustsec/advisory-db` | The RustSec advisory-db repo (authoritative source for advisories) | Confirming whether an advisory is active, withdrawn, or whether a backported fix exists for an older version |
| `https://embarkstudios.github.io/cargo-deny/checks/cfg.html` | cargo-deny `deny.toml` schema | Auditing or authoring `deny.toml` — verify keys against the current schema (the 0.18+ removed-key callout lives in `quality-supply-chain-ladder.md` §2; the live schema is the source of truth) |