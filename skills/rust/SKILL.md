---
name: rust
description: "Load when managing the Rust project lifecycle — scaffolding crates/workspaces, configuring CI/clippy/nextest, auditing dependencies, publishing, or hardening supply chain. Use when the user says 'Rust', 'cargo publish', 'clippy', or 'cargo-deny'. Do NOT use for design reasoning or runtime bugs."
when_to_use: |
  - User wants to scaffold a new Rust crate or workspace
  - User wants to set up CI, clippy, nextest, coverage, or cargo-deny
  - User wants to publish a crate, bump version, write a changelog, or deprecate a feature
  - User wants to harden supply-chain (cargo-deny, cargo-vet, Dependabot)
  - User asks about edition 2024, MSRV, workspace inheritance, or feature flag design
  - User wants a holistic review, audit, or health check of an *existing* Rust project or workspace
license: MIT
---

# rust

You are the Rust project lifecycle hub. You do not execute Rust work yourself; you route to the right mode and let references and subagents carry the mechanism. All mechanism content lives in `references/` and is loaded only on imperative citation below.

## Routing Guidance

- SCAFFOLD: 'scaffold a Rust project', 'new crate', 'Cargo.toml template', 'lib + bin layout', 'feature flag design', 'edition 2024', 'pick an MSRV', 'write rustdoc'
- WORKSPACE: 'set up a Cargo workspace', 'split into a workspace', 'share deps', 'workspace inheritance', 'coordinate MSRV', 'publish a workspace', 'internal features'
- QUALITY: 'set up CI for Rust', 'configure clippy', 'switch to nextest', 'add coverage', 'audit dependencies', 'cargo-deny', 'cargo-vet', 'add benchmarks'
- RELEASE: 'publish my crate', 'release-plz', 'bump version', 'changelog', 'deprecate a feature', 'bump MSRV safely', 'replace a dependency', 'Dependabot for Rust', 'yank a version'
- REVIEW: 'review my rust project', 'audit this crate', 'audit this workspace', 'health check my cargo project', 'critique my rust code', 'find issues in this crate', 'what is wrong with this project', 'rust code review'

## Decision Router

IF scaffolding a new crate or designing features → SCAFFOLD mode
IF splitting a project into a workspace, sharing deps across crates, or coordinating MSRV → WORKSPACE mode
IF setting up CI / clippy / nextest / coverage / audit / dev-experience tooling → QUALITY mode
IF versioning, publishing, writing a changelog, maintaining supply-chain, or deprecating a feature → RELEASE mode
IF reviewing, auditing, or health-checking an *existing* Rust project or workspace → REVIEW mode

---

# Mode: SCAFFOLD

The project-init layer: lib/bin decision, Cargo.toml template, MSRV policy, feature flag design, lib+bin code layout, rustdoc conventions, examples & tests directory, edition migration.

## Process

1. Confirm the user's project shape: pure lib / pure bin / lib+bin (default to lib+bin for anything that may grow — the ripgrep / bat / fd / cargo pattern).
2. Pick MSRV per the N-2 stable policy (current default: `1.81`, which unlocks the MSRV-aware resolver and edition 2024).
3. Draft `Cargo.toml` from the recommended template (edition 2024, MSRV, all metadata, `profile.release`, `[features]` with `default = []`).
4. Design features with the 5-rule playbook (short lowercase names, additive only, `__internal` prefix for non-public, deprecation cycle, `cargo-hack` matrix test).

You MUST read `references/scaffold-cargo-and-features.md` BEFORE writing a new `Cargo.toml` or designing features. It teaches the lib/bin decision tree, the recommended Cargo.toml template (edition 2024, MSRV `1.81`, all metadata, release profile), the MSRV policy (N-2 stable, advisory vs enforced with the 1.81 MSRV-aware resolver cutover), and the 5-rule feature flag playbook (additive, `__internal` prefix, the reqwest pattern, the deprecation cycle).

You MUST read `references/scaffold-lib-bin-rustdoc.md` BEFORE designing the code layout or writing rustdoc. It teaches the lib+bin pattern (logic in `src/lib.rs`, thin `src/main.rs`, ripgrep/bat/fd/cargo precedent), the feature-gated binary pattern (bat's `application` feature), rustdoc conventions (Examples → Errors → Panics → Safety, module-level `//!`, `#![warn(missing_docs)]`), the examples-vs-tests directory structure, and the edition-2021-to-2024 migration playbook (`cargo fix --edition` + sharp edges: `gen` keyword, `expr_2021`, lifetime capture rules).

**Spawn Directives:**
- ALWAYS spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." to verify the draft `Cargo.toml`.
- Apply Rust idiomatic-polish inline after non-trivial chunks of code in the scaffolded layout — see `references/rust-idiom-polish.md` (the inline polish checklist).

## Output

A scaffolded crate or workspace with: recommended `Cargo.toml`, lib+bin code layout, `src/lib.rs` + `src/main.rs` (or both), `#![warn(missing_docs)]` / `#![forbid(unsafe_code)]` pragmas as appropriate, and an `examples/` + `tests/` directory.

---

# Mode: WORKSPACE

The workspace structure layer: when to split into a workspace, virtual / single-package / multi-workspace templates, workspace inheritance, `Cargo.lock` policy, MSRV coordination, cross-crate patterns (internal features, path deps, shared dev-deps, feature unification), and workspace publishing.

## Process

1. Decide single-crate vs workspace vs multi-workspace (signals: `main.rs` >500 lines, two binaries sharing logic, build time dominated by heavy deps, complex `#[cfg(feature)]` matrices).
2. Apply the virtual workspace template (no `[package]` in the root, `[workspace.package]` for shared metadata, `[workspace.dependencies]` for shared deps, `[workspace.lints]` for centralized lints) and inheritance (1.64+, with the `additive-defaults` pitfall in mind).
3. Configure `Cargo.lock` policy (commit for apps, don't commit for pure libs, `--locked` in CI).
4. Coordinate MSRV: workspace MSRV = most restrictive member's MSRV; override only with explicit per-member `rust-version`.

You MUST read `references/workspace-decisions.md` BEFORE splitting a project into a workspace or restructuring an existing one. It teaches the single-crate vs workspace vs multi-workspace decision tree (with "should you NOT split" anti-signals), the virtual workspace template (no `[package]` in the root, `[workspace.package]` / `[workspace.dependencies]` / `[workspace.lints]`), and the workspace inheritance playbook (1.64+) including the `additive-defaults` pitfall (cargo #12162).

You MUST read `references/workspace-lockfile-and-cross-crate.md` BEFORE publishing a workspace or adding a member crate. It teaches the `Cargo.lock` commit policy (commit for apps/binaries, don't commit for pure libraries), the MSRV coordination across members, the internal features pattern (`__` prefix, the reqwest pattern), the path-dependency auto-detection, the shared dev-dependencies inheritance, the feature unification behavior, and the workspace publishing policy (Cargo 1.90+ native `cargo publish --workspace`, internal-only crates with `publish = false`).

**Spawn Directives:**
- ALWAYS spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." to verify the workspace `Cargo.toml`.

## Output

A virtual workspace root + member crates with: shared metadata, shared deps, centralized lints, lockfile policy applied, and an explicit `publish = false` on internal-only members.

---

# Mode: QUALITY

The quality pipeline: CI, linting, testing, coverage, audit, benchmarks, and the supply-chain ladder. Dev-experience tooling (bacon, sccache, mold, rust-toolchain pinning) lives here too.

## Process

1. Adopt the canonical 6-job CI on day 1: format → test → lint → doc → audit → msrv, with `concurrency.cancel-in-progress` on PR branches only, `RUSTFLAGS: "-D warnings"`, and `actions-rust-lang/setup-rust-toolchain` (or `dtolnay/rust-toolchain` + `Swatinem/rust-cache@v2`).
2. Configure per-project clippy (`clippy.toml` with MSRV for MSRV-aware lints, `disallowed-types`) and rustfmt (`rustfmt.toml` with edition 2024), plus library-level pragmas (`#![warn(missing_docs)]`, `#![forbid(unsafe_code)]` if safe-Rust).
3. Adopt `cargo-nextest` when the test suite > 200 tests OR CI > 5 min (`.config/nextest.toml` default + ci profile, `--retries 2`, JUnit XML for CI).
4. Collapse `tests/` into a single-binary multi-suite structure once ≥10-20 root-level integration test files accumulate: a single `tests/main.rs` mounting each suite as `tests/suites/<name>.rs`. 10-20× faster incremental link; absolute dead-code accuracy on shared helpers (no more `#![allow(dead_code)]`). See `references/quality-testing-and-coverage.md` §4 for the migration playbook.
5. Set up coverage with `cargo-llvm-cov` (preferred for Linux/macOS) only after 2-3 months of data — start with line, add branch when there's a coverage target.
6. Climb the supply-chain ladder: cargo-deny (Day 1 of published crate) → cargo-vet (security-critical) → Dependabot / RSS (always-on monitoring).

You MUST read `references/quality-ci-template.md` BEFORE writing `.github/workflows/ci.yml`. It teaches the canonical 6-job CI (format → test → lint → doc → audit → msrv), the concurrency cancel-in-progress rule (PR branches only, never main), the `RUSTFLAGS: "-D warnings"` discipline, the `actions-rust-lang/setup-rust-toolchain` alternative, and the Forgejo/Gitea compatibility note.

You MUST read `references/quality-clippy-and-fmt.md` BEFORE configuring per-project lint policy. It teaches the per-project `clippy.toml` (MSRV for MSRV-aware lints, `disallowed-types`), the `rustfmt.toml` configuration, the library-level pragmas (`#![warn(missing_docs)]`, `#![forbid(unsafe_code)]`), the lint group selection per use case (binary / library / embedded / no_std), and the `#![deny(warnings)]` anti-pattern.

You MUST read `references/quality-testing-and-coverage.md` BEFORE switching test runners or adding coverage. It teaches the cargo-nextest adoption criteria (>200 tests OR CI > 5 min), the `.config/nextest.toml` profile (default + ci), **the single-binary multi-suite pattern** (collapse ≥10-20 root-level integration tests into a single `tests/main.rs` binary for 10-20× faster incremental link and dead-code accuracy on shared helpers), the cargo-hack feature matrix pattern, cargo-llvm-cov over cargo-tarpaulin, line vs branch coverage scope, and the Criterion/divan/iai-callgrind benchmark toolkit.

You MUST read `references/quality-supply-chain-ladder.md` BEFORE publishing a crate or hardening a security-critical project. It teaches the 4-stage ladder (cargo-audit → cargo-deny → cargo-vet → Dependabot/RSS), the verified 2026 `deny.toml` schema (with the 0.18+ removed-key callout), the cargo-vet bootstrap from Mozilla + Google audits, and the SBOM path.

You MUST read `references/quality-dev-experience.md` BEFORE optimizing local dev loops or adding more tooling. It teaches the bacon file-watcher, the `.cargo/config.toml` build-speed tweaks (mold, sccache), the `rust-toolchain.toml` pinning, the CI cache, and the consolidated tool matrix.

**Spawn Directives:**
- ALWAYS spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." (one per `.github/workflows/*.yml` file, in parallel).
- ALWAYS spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." for supply-chain audit.
- Apply Rust idiomatic-polish inline after non-trivial chunks — see `references/rust-idiom-polish.md`.

## Output

A `.github/workflows/ci.yml` with the 6 canonical jobs, a `clippy.toml` + `rustfmt.toml` with the per-project policy, a `.config/nextest.toml` with default + ci profiles, a `deny.toml` (cargo-deny) with current-schema config, and a dev-experience setup (bacon, sccache, rust-toolchain.toml pinning).

---

# Mode: RELEASE

The release / publishing pipeline: Cargo semver (with the contested MSRV policy), changelog tooling, the `cargo publish` playbook, supply-chain maintenance (cargo-vet, Dependabot, RUSTSEC), and feature deprecation.

## Process

1. Pick a versioning stance: pre-1.0 (churn freely, document in changelog, no deprecation window) vs post-1.0 (the 3-step feature deprecation cycle: warn → deprecated → removed, minimum 2 minor versions, often 3+).
2. Pick a changelog tool: git-cliff (Rust binary, git-driven, fast) for greenfield, release-please (Node, GitHub-native Release PR workflow) for JS/TS-heavy teams, hand-curated for mature projects (serde, tokio, cargo).
3. Run the first-publish playbook: build → test → clippy → `--dry-run` → login → publish. For workspaces, use `cargo publish --workspace` (Cargo 1.90+) or `release-plz` with `publish = false` on internal crates.
4. Maintain supply-chain: re-run `cargo vet` for new deps, monitor RUSTSEC (https://rustsec.org/ RSS), Dependabot weekly with grouped updates, bump-vs-replace-vs-live-with decision per dep.

You MUST read `references/release-versioning-and-changelog.md` BEFORE tagging a release or choosing a changelog generator. It teaches the Cargo semver rules for pre-1.0 vs 1.0+, the SemVer trick for 1.0.0 development, the contested MSRV policy (api-guidelines vs RustCrypto camps, and the 2026 MSRV-aware resolver that obsoletes BurntSushi's 2023 workaround), the workspace lockstep versioning pattern, and the changelog tooling decision tree (git-cliff vs release-please vs hand-curated).

You MUST read `references/release-publishing-and-deps.md` BEFORE your first `cargo publish` and before changing your dependency policy. It teaches the first-publish playbook (build → test → clippy → dry-run → login → publish), the Cargo 1.90+ native workspace publishing, the yank-not-delete rule, the MSRV-aware resolver configuration (`incompatible-rust-versions = "fallback"`), and the vendoring decision.

You MUST read `references/release-supply-chain-maintenance.md` BEFORE changing a dep policy or deprecating a feature. It teaches the cargo-vet certification workflow, the Dependabot config, the RUSTSEC monitoring channels, the bump-vs-replace-vs-live-with decision, the 3-step feature deprecation cycle (post-1.0), the `#[deprecated]` syntax, the pre-1.0 vs post-1.0 discipline, the rustc unstable-feature pattern, and the ADD-vs-REMOVE decision for features.

**Spawn Directives:**
- ALWAYS spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." before any version bump tagged as a security release.
- ALWAYS spawn a subagent generalist with the prompt:
  "You are an isolated reviewer. Review through this lens: ''.
  Return findings with severity (HIGH/MEDIUM/LOW), file:line, and fix.
  Do NOT implement — identify what to change and why." before `cargo publish` on 1.x crates.

## Output

A new published version with a CHANGELOG entry, a git tag, a `cargo publish` log, and (for 1.x) a `cargo semver-checks` verdict in the PR description.

---

# Mode: REVIEW

The holistic-audit layer for an *existing* Rust project or workspace. Fans out 5 parallel a subagent generalist lenses (source-code, dependency-hygiene, build-test, public-api, supply-chain) and synthesizes a deduplicated, severity-ranked report. REVIEW is read-only — it never modifies files; the user (or a downstream mode) decides what to fix.

## Process

1. Confirm the target — an absolute path to a Rust project or workspace root. If the user supplies a relative path or a glob, resolve it before spawning.
2. ALWAYS spawn 5 a subagent generalist instances in parallel, one per lens (see Subagent Index below for the exact lens strings and primary references). All 5 run in the same `Agent` call (no barrier between them).
3. Each lens returns findings in the contract defined in `references/review-orchestration.md` (`{ severity, location, dimension, finding, consequence, fix }` JSON array, `(unverified)`-tagged locations for unverified claims).
4. Apply the dedup/synthesis protocol from §6 of `references/review-orchestration.md` (merge by `location`; concatenate `dimension`; keep the highest `severity`; sort BLOCKER → WARN → NIT).
5. Emit the final markdown report (the table format from §6 of the orchestration reference). Empty severity buckets are omitted.

You MUST read `references/review-orchestration.md` BEFORE invoking REVIEW mode or spawning any audit lens. It is the contract: the 5-lens fan-out, the output shape every lens must return, the severity rubric (BLOCKER/WARN/NIT), the P6 ground truth rule, the dedup/synthesis protocol, and the report format. Without it, lenses return heterogeneous prose and synthesis fails.

You MUST read `references/review-source-code.md` BEFORE spawning the `"audit source-code health and idioms"` lens. It teaches the idiomatic-pattern checklist, the clippy profile evaluation, the `unsafe` and soundness guardrails, the error-handling discipline, and the async/concurrency hazard list — plus the "Authoritative sources" URL card with the per-URL trigger conditions.

You MUST read `references/review-dependency-hygiene.md` BEFORE spawning the `"audit dependency hygiene"` lens. It teaches the Cargo.toml version-constraint audit, the dependency-tree duplicate detection, the manifest consistency checks, the `deny.toml` *shape* audit (this lens does not check policy — that is the supply-chain lens), the lockfile hygiene checks, and the explicit boundary with the supply-chain lens.

You MUST read `references/review-public-api.md` BEFORE spawning the `"audit public API surface"` lens. It teaches the doc-coverage rules, the public-visibility hazards (including the seal-trait pattern), the semver consistency check (applying `release-versioning-and-changelog.md` rules), the public-type ergonomics smell-test, and the explicit boundary with the release-mode `"pre-publish review"` lens.

**Spawn Directives:**
- ALWAYS spawn 5 a subagent generalist instances in parallel — one per lens, all five at once. Pass each instance: (a) the lens string from the Subagent Index, (b) the target path, (c) the Output Contract from `references/review-orchestration.md` §2 verbatim.
- After all 5 return, run the dedup/synthesis protocol from `references/review-orchestration.md` §6 inline. Do NOT delegate synthesis to a subagent — it is a deterministic merge and the orchestrator owns the final report.

## Output

A deduplicated, severity-ranked markdown report with the table format defined in `references/review-orchestration.md` §6: a header (project name, date, lens coverage count, finding counts by severity), then BLOCKER / WARN / NIT tables with `{ location, dimension, finding, consequence, fix }` columns. The report is the entire output — REVIEW does not produce code, diffs, or fix suggestions beyond the per-row `fix` field.

---

## Failure Handling

| Mode | Failure | Action |
|---|---|---|
| SCAFFOLD | `cargo fix --edition` leaves compile errors after migration | Walk the breaking-change checklist (gen keyword, expr_2021, lifetime capture) one error at a time; rerun clippy |
| WORKSPACE | `additive-defaults` build error (cargo #12162) | Pin the workspace default features explicitly with the feature-wrapper pattern from the inheritance reference |
| QUALITY | `cargo deny check` fails on the 0.18+ removed-key schema | Replace `vulnerability` and `unlicensed` keys with the `[advisories]` and `[licenses]` sections per the current schema |
| RELEASE | `cargo publish` fails mid-workspace | Yank the partially-published version, fix `release-plz.toml` ordering, retry — never `--allow-dirty` without a `--dry-run` first |
| REVIEW | Lenses return overlapping findings on the same `path:line`, or a lens returns prose instead of the JSON contract | Re-apply the dedup protocol from `references/review-orchestration.md` §6 (merge by `location`, keep highest severity, concatenate `dimension`); for the prose-return lens, re-spawn with the Output Contract pasted verbatim in the spawn prompt |
| Any | MSRV bump decision is contested | ASK the user which camp (api-guidelines advisory vs RustCrypto breaking) — the policy has no community consensus |

---

## Reference Index

**SCAFFOLD mode**
- `references/scaffold-cargo-and-features.md` — lib/bin decision tree, Cargo.toml template, MSRV policy, feature flag playbook
- `references/scaffold-lib-bin-rustdoc.md` — lib+bin code layout, rustdoc conventions, examples/tests directory, edition-2021-to-2024 migration

**WORKSPACE mode**
- `references/workspace-decisions.md` — single-crate vs workspace decision, virtual workspace template, inheritance playbook, `additive-defaults` pitfall
- `references/workspace-lockfile-and-cross-crate.md` — `Cargo.lock` policy, MSRV coordination, internal features, path deps, shared dev-deps, feature unification, workspace publishing

**QUALITY mode**
- `references/quality-ci-template.md` — canonical 6-job GitHub Actions CI, concurrency rules, `RUSTFLAGS="-D warnings"`, Forgejo/Gitea compatibility
- `references/quality-clippy-and-fmt.md` — per-project clippy.toml + rustfmt.toml, library-level pragmas, lint group selection per use case
- `references/quality-testing-and-coverage.md` — cargo-nextest adoption, `.config/nextest.toml`, **single-binary multi-suite pattern (§4)**, cargo-hack feature matrix, cargo-llvm-cov, Criterion/divan/iai-callgrind
- `references/quality-supply-chain-ladder.md` — 4-stage ladder (audit → deny → vet → Dependabot), 2026 deny.toml schema, cargo-vet bootstrap, SBOM
- `references/quality-dev-experience.md` — bacon, `.cargo/config.toml` (mold, sccache), `rust-toolchain.toml` pinning, CI cache, consolidated tool matrix

**RELEASE mode**
- `references/release-versioning-and-changelog.md` — Cargo semver pre-1.0 vs 1.0+, contested MSRV policy, workspace lockstep, changelog tooling decision tree
- `references/release-publishing-and-deps.md` — first-publish playbook, Cargo 1.90+ native workspace publishing, yank-not-delete, MSRV-aware resolver, vendoring decision
- `references/release-supply-chain-maintenance.md` — cargo-vet maintenance, Dependabot, RUSTSEC, bump-vs-replace-vs-live-with, 3-step feature deprecation cycle, `#[deprecated]` syntax, ADD-vs-REMOVE for features

**REVIEW mode**
- `references/review-orchestration.md` — the contract: 5-lens fan-out, output schema (`severity | location | dimension | finding | consequence | fix`), severity rubric, dedup/synthesis protocol, P6 ground truth rule, report format
- `references/review-source-code.md` — source-code health & idioms lens checklist: idiomatic patterns, clippy profile evaluation, `unsafe` and soundness guardrails, error handling, async/concurrency hazards, perf smell-tests; URL card for clippy / Rust Reference / Nomicon / unsafe-code-guidelines / rustdoc / edition guide / perf book / RFCs
- `references/review-dependency-hygiene.md` — dependency-hygiene lens: Cargo.toml version-constraint audit, tree duplicate detection, manifest consistency, `deny.toml` shape check, lockfile hygiene; URL card for Cargo Book / manifest reference / RUSTSEC / advisory-db / cargo-deny schema
- `references/review-public-api.md` — public-API surface lens: doc coverage, visibility hazards, seal-trait pattern, semver consistency, public-type ergonomics; URL card for rustdoc book / API Guidelines / Cargo semver / edition guide

---

## Subagent Index

- **subagent generalist, lens "audit Cargo.toml"** — `SCAFFOLD` and `WORKSPACE` modes. Reviews a `Cargo.toml` (single crate or workspace root) against the lib/bin decision, edition 2024, MSRV, feature flag playbook, workspace inheritance, the `additive-defaults` pitfall, and shared dev-deps policy. Returns findings with file:line, severity, consequence, and a concrete fix.
- **subagent generalist, lens "audit CI configuration"** — `QUALITY` mode. Audits `.github/workflows/*.yml` + `clippy.toml` + `rustfmt.toml` + `.config/nextest.toml` for the 6-job canonical CI, `RUSTFLAGS=-D warnings` discipline, nextest adoption criteria, and dev-experience tooling. Fan out one a subagent generalist per CI workflow file in parallel.
- **subagent generalist, lens "audit supply chain"** — `QUALITY` (initial setup) and `RELEASE` (ongoing maintenance) modes. Audits `deny.toml` against the 0.19+ schema, `Cargo.lock` for RUSTSEC advisories, `cargo vet` audit coverage, Dependabot config, and `.cargo/config.toml` for the MSRV-aware resolver. Returns the stage (0-3) the project is at on the supply-chain ladder with the gaps blocking promotion.
- **subagent generalist, lens "pre-publish review"** — `RELEASE` mode. Pre-publish review: runs a mental `cargo semver-checks` against the public API delta, checks CHANGELOG for the new version, verifies `Cargo.toml` version + edition + MSRV + workspace lockstep, surfaces breaking-change signal.
- **subagent generalist, lens "audit source-code health and idioms"** — `REVIEW` mode (Lens 1 of 5). Audits `.rs` files for idiomatic patterns, clippy profile soundness, `unsafe` correctness, error-handling discipline, and async/concurrency hazards. Primary reference: `references/review-source-code.md` (with `references/quality-clippy-and-fmt.md` and `references/rust-idiom-polish.md`).
- **subagent generalist, lens "audit dependency hygiene"** — `REVIEW` mode (Lens 2 of 5). Audits `Cargo.toml` version constraints (wildcards, path-deps without version, `git` deps in published crates), dependency-tree duplicates and bloat, manifest consistency (`rust-version` vs `clippy.toml` MSRV, `[lints]` table, workspace inheritance), and the `deny.toml` *shape* (not policy — that's the supply-chain lens). Primary reference: `references/review-dependency-hygiene.md`.
- **subagent generalist, lens "audit build & test health"** — `REVIEW` mode (Lens 3 of 5). Audits `.github/workflows/*.yml` + `clippy.toml` + `rustfmt.toml` + `.config/nextest.toml` + `.cargo/config.toml` against the canonical 6-job CI, `RUSTFLAGS=-D warnings` discipline, nextest adoption criteria (>200 tests OR CI > 5 min), dev-experience tooling, and the **single-binary multi-suite test pattern** (≥10-20 root-level `tests/*.rs` files should be collapsed into one `tests/main.rs` binary; absence is a WARN with `fix: <migration steps from references/quality-testing-and-coverage.md §4>`). Reuses the `QUALITY` mode references (`quality-ci-template.md`, `quality-testing-and-coverage.md`, `quality-dev-experience.md`); no new lens reference file.
- **subagent generalist, lens "audit public API surface"** — `REVIEW` mode (Lens 4 of 5). Audits documentation coverage, public-visibility hazards (`pub(crate)` in public signatures, missing seal traits, `pub use` re-exports), semver consistency against `release-versioning-and-changelog.md`, and public-type ergonomics. Primary reference: `references/review-public-api.md`.
- **Inline Rust idiom-polish** — `SCAFFOLD` and `QUALITY` modes. Post-implementation cleanup of recently-written `.rs` code for idiomatic Rust (ownership/borrowing, error handling, iterator chains, clone elimination) without changing behavior or borrow-checker compliance. Apply inline; see `references/rust-idiom-polish.md` for the checklist.

---

## Anti-patterns (consolidated across modes)

- **SCAFFOLD** — `#![deny(warnings)]` in lib.rs (breaks on transitive-dep warnings); `src/main.rs` doing real work (kills testability); wildcard `*` dependency version (breaks reproducibility); missing `[package].description` (zero crates.io search rank); `publish = true` on internal-only crates
- **WORKSPACE** — Premature workspace split (wait for a real signal: binary+lib, multi-bin, shared types >100 lines); `path = "..."` in a published crate (breaks for downstream users); sharing `dev-dependencies` at workspace level when members are heterogeneous (binary's test deps pollute the lib); nested workspace dirs when flat would do
- **QUALITY** — `cargo-audit` and `cargo-deny` run redundantly (deny subsumes audit); `cargo test --release` (slower build, no perf signal); `RUSTFLAGS=-D warnings` for workspace members (denies warnings in transitive deps too); coverage target on day 1 (measure first, target after 2-3 months); pre-optimizing benchmarks; keeping N separate integration test binaries once `tests/` grows past 10-20 files (collapse into the single-binary multi-suite structure from `quality-testing-and-coverage.md` §4)
- **RELEASE** — Publishing without `--dry-run`; deleting a version from CI history (only yank); using `cargo-release` to publish a workspace without testing the order; yanking for "minor" bugs (publish a new patch); removing a feature in the same release that deprecates it; `cargo publish --allow-dirty` without a `--dry-run` first; long-lived crates.io API tokens (use OIDC trusted publishing)
- **REVIEW** — Spawning lenses sequentially (one a subagent generalist at a time, waiting for each to finish) instead of in parallel — destroys the isolation benefit and serializes a 5× slowdown; promoting an `(unverified)` finding to BLOCKER without reading the file — violates the P6 ground truth rule; modifying files mid-audit (REVIEW is read-only — if the user asks for fixes, route back to SCAFFOLD/WORKSPACE/QUALITY/RELEASE per dimension); using REVIEW for performance-regression analysis against a baseline commit (REVIEW does a smell-test, not a regression delta); using REVIEW to design alternative architectures (use reasoning-from-principles for design reasoning — REVIEW audits the existing code against existing standards)

---

## CONTRAST

- NOT for: design / architecture reasoning across competing options — use reasoning-from-principles (PROPOSE mode)
- NOT for: investigating a runtime bug / root cause analysis — use superpowers' `systematic-debugging`
- NOT for: improving an existing artifact (polish, clarity, structure) — use reviewing-and-polishing
- NOT for: non-Rust project init (use a language-specific scaffold or `generating-ideas`)
- NOT for: cross-language polyglot workspace (one Cargo workspace + npm/pip/etc.) — handle the non-Rust halves with their own language skills
- NOT for (REVIEW vs QUALITY): setting up CI / clippy / nextest / coverage / cargo-deny / cargo-vet from scratch — use `QUALITY`. REVIEW audits the existing setup; it does not author it.
- NOT for (REVIEW vs RELEASE `pre-publish review`): gating a specific version bump or running `cargo semver-checks` against the API delta since the last tag — use `RELEASE`. REVIEW audits the current state of the public API regardless of release timing.
- NOT for (REVIEW vs language-agnostic security audit): general threat modeling, secrets scanning, OWASP-class vulnerabilities — use the core security skill. REVIEW is deep, Rust-idiomatic, Cargo-specific (clippy lint semantics, MSRV resolver, cargo-deny/vet, unsafe soundness). For language-agnostic security, cite the security skill by its role.
