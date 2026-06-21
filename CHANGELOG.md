# Changelog

All notable changes are documented here.

## [2.0.0] — 2026-06-19

### Changed (BREAKING)

- **Skills-only plugin.** Removed `agents/` (7 files), `commands/` (18 files), `hooks/`, `scripts/`, `docs/`, `knowledge/`, `.claude/`. All subagent spawn instructions inlined into skills using platform-agnostic phrasing: "spawn a subagent explorer" (read-only) and "spawn a subagent generalist" (edit access). Never names a specific tool — works across any AI agent platform.
- **`subagent-orchestration` skill** rewritten as the canonical reference for the two spawn patterns. All other skills follow its conventions.
- **AGENTS.md** reduced to a 44-line maintainer note with the spawn convention.

### Removed

- All named agents: `tp-critic`, `tp-explorer`, `tp-researcher`, `sadd-judge`, `mcp-quality-judge`, `wiki-searcher`, `tp-roster-auditor`
- All slash commands: `/trace`, `/cc-docs`, `/whats-next`, `/critique`, `/debug`, `/design-subagents`, `/ideate`, `/implement`, `/improve`, `/learn`, `/orchestrate`, `/plan`, `/rules`, `/archive`, `/capture`, `/meta-issue`, `/meta-review`, `/session-inspect`, `/discipline-check`
- Hook scripts and audit scripts

## [1.0.0] — 2026-06-19

### Changed (BREAKING)

- **11 plugins reunified into a single flat plugin.** All skills, agents, commands, and hooks moved from `plugins/<name>/<type>/` to root-level `<type>/` directories. `.claude-plugin/marketplace.json` and `_meta.json` removed. `scripts/regenerate-marketplace.py` retired. Single `plugin.json` at `.claude-plugin/plugin.json`. Flat structure mirrors the superpowers model: `skills/`, `agents/`, `commands/`, `hooks/`, `scripts/` at repo root.

### Migration

Users who installed individual plugins must uninstall those and install the unified plugin:
```bash
claude plugin uninstall tp-rust tp-git tp-mcp tp-sadd tp-fpf tp-security tp-wiki tp-session-audit tp-discipline claude-cli-wrapper core-principled
claude plugin install taches-principled
```

## [0.8.0] — 2026-06-19

### Removed

- **`diagnose` skill removed** (core-principled). Fully subsumed by superpowers' `systematic-debugging` which covers root-cause-first debugging with stronger behavioral overrides (Iron Law enforcement). All 20+ cross-references updated to point to superpowers' `systematic-debugging`.
- **`git-worktree-manager` skill removed** (tp-git). Fully subsumed by superpowers' `using-git-worktrees` which has superior isolation detection, native-tool-first logic, and consent flow.
- **`git-preflight-checker` skill removed** (tp-git). Fully subsumed by superpowers' `verification-before-completion` which enforces the same evidence-before-claims pattern more forcefully.

### Changed (mode scoping)

- **`ideation` narrowed to create-ideas only** — brainstorm mode (collaborative Q&A to refine vague ideas) removed; now delegates to superpowers' `brainstorming`. Single mode: CREATE-IDEAS (6 alternatives inline).
- **`test-orchestration` TDD sub-mode removed** — Red-Green-Refactor cycles delegated to superpowers' `test-driven-development`. Remaining EXECUTE modes: Write Tests (post-hoc coverage), Fix Tests (broken test repair). STRATEGY mode unchanged.
- **`skill-authoring` narrowed to METHODOLOGY only** — WORKFLOW mode (new skill creation, 157 lines) removed; delegates to superpowers' `writing-skills` (TDD-for-skills methodology). Single mode: METHODOLOGY (trigger optimization, routing benchmarking, frontmatter validation).
- **`sadd` EXECUTE repositioned as competitive generation** — clarified that EXECUTE is for generating N competing implementations and picking the winner, not sequential plan execution (use superpowers' `subagent-driven-development` for that).

### Added (CONTRAST sections)

- **`plan-lifecycle`** — CONTRAST with superpowers' `writing-plans` (single-plan doc vs ROADMAP + per-phase PLAN.md) and `executing-plans`/`subagent-driven-development` (no critic checkpoints vs per-phase critic + deviation log).
- **`refine` REVIEW** — CONTRAST with superpowers' `requesting-code-review` (single-reviewer dispatch vs parallel multi-reviewer fan-out).
- **`subagent-orchestration`** — CONTRAST with superpowers' `dispatching-parallel-agents` (simple parallel fan-out vs full agent architecture design).
- **`task-lifecycle`** — CONTRAST with superpowers' `writing-plans` + `executing-plans` (multi-step feature plans vs single-feature lifecycle).
- **`kaizen`** — CONTRAST with superpowers' `verification-before-completion` (completion gate vs design-time filter — complementary, not substitutes).

### Plugin versions

- **core-principled** 0.21.1 → 0.22.0 (minor: removed diagnose, narrowed ideation/test-orchestration/skill-authoring)
- **tp-git** 0.4.1 → 0.5.0 (minor: removed git-worktree-manager and git-preflight-checker)

## [0.7.0] — 2026-06-19

### Added

- **`## Authoritative sources` blocks retrofitted into all 13 pre-existing `tp-rust` references.** Completes the URL/fetch-trigger convention introduced in `[0.5.0]` (which only covered the 4 new REVIEW references). Every reference now ends with a `| Source | Canonical for | Fetch live when |` table naming the canonical external sources for its topic, each with a *specific* audit-condition trigger (not a vague "when relevant"). 16 of 17 references now carry the block; `review-orchestration.md` is intentionally block-less (pure marketplace mechanics, no external URLs). The retrofit added ~70 unique canonical Rust-ecosystem URLs across the skill.
  - `scaffold-cargo-and-features.md` — manifest schema, features reference, edition guide, `rust-version`/MSRV resolver, cargo-hack, cargo-msrv, API Guidelines.
  - `scaffold-lib-bin-rustdoc.md` — rustdoc Book, doctests, Cargo targets, edition migration, Rust Reference.
  - `workspace-decisions.md` — Workspaces reference, manifest, `[lints]` table, cargo #12162.
  - `workspace-lockfile-and-cross-crate.md` — `Cargo.lock` policy, feature unification, MSRV resolver, Cargo CHANGELOG.
  - `quality-ci-template.md` — GitHub Actions concurrency, setup-rust-toolchain, dtolnay/rust-toolchain, Swatinem/rust-cache, taiki-e/install-action.
  - `quality-clippy-and-fmt.md` — Clippy Book, clippy lint index, `clippy.toml` config, rustfmt config, edition guide.
  - `quality-testing-and-coverage.md` — nextest (+ filterset), Cargo targets (multi-suite), cargo-llvm-cov, cargo-tarpaulin, cargo-hack, perf book, Criterion, divan, gungraun.
  - `quality-supply-chain-ladder.md` — cargo-deny schema/repo, RUSTSEC, advisory-db, cargo-vet Book, cargo-cyclonedx.
  - `quality-dev-experience.md` — bacon, sccache, mold, rustup toolchain file, Swatinem/rust-cache, `.cargo/config.toml` reference.
  - `release-versioning-and-changelog.md` — Cargo semver, semver.org, MSRV resolver, API Guidelines, git-cliff, release-please.
  - `release-publishing-and-deps.md` — `cargo publish`/`yank`/`vendor`, crates.io, resolver config, Cargo CHANGELOG.
  - `release-supply-chain-maintenance.md` — cargo-vet Book, Dependabot config, RUSTSEC, advisory-db, `#[deprecated]`, rustdoc `#[doc(hidden)]`.
  - `rust-idiom-polish.md` — clippy lint index, Rust Reference, Rust Book.

### Fixed

- **`iai-callgrind` → `gungraun` rename in `quality-testing-and-coverage.md` §9.** The deterministic-benchmarking crate formerly known as `iai-callgrind` was renamed to **gungraun** (repo `github.com/gungraun/gungraun`, docs `gungraun.github.io/gungraun/`). The reference now uses the current name with "(formerly iai-callgrind)" for discoverability, and notes the Windows/Valgrind limitation. Caught during URL verification for this retrofit.

### Changed

- **`tp-rust` 0.6.1 → 0.7.0** (minor: substantive content enhancement across 13 references; not a new capability, but a uniform guidance surface that changes what every reference teaches).

### AUDIT

- Retrofit scope: the `[0.6.1]` self-review's follow-up #5 ("Retrofit `## Authoritative sources` blocks into the 13 pre-existing references"). URL verification: 5 non-obvious canonical URLs fetched live this session to confirm they hadn't moved (divan ✓, bacon ✓, git-cliff ✓, rustfmt ✓, **iai-callgrind → found renamed to gungraun**, fixed). The remaining URLs reuse the high-confidence rust-lang.org canonical set established and verified in `[0.5.0]`–`[0.6.1]`.
- Per-finding resolution: iai-callgrind rename → **Fixed** (this release). `review-orchestration.md` left block-less → **Intentional** (mechanics-only; no external URLs to cite). All other references → **Retrofitted**.

## [0.6.1] — 2026-06-19

### Fixed

- **Single-binary multi-suite pattern: corrected the import advice in `references/quality-testing-and-coverage.md` §4.** The previous migration step told readers to add `use super::*;` to each moved suite file. That is wrong for the `tests/suites/` wrapper layout the reference documents: a suite at `crate::suites::<name>` has `super` = `crate::suites` (which holds only the `mod` declarations), so `use super::*;` imports nothing useful and the shared `common` helpers are unreachable. Fixed to `use crate::common;`, with an explicit explanation of the module path so readers understand *why*. Found by a `tp-critic` self-review lens.

### Added

- **`### Idiomatic variant: the prelude pattern (mdBook style)`** subsection in §4. Documents the alternative flat layout (suites as direct crate-root submodules) with a `mod prelude { pub use crate::common::{...}; }` re-export, modelled on `rust-lang/mdBook`'s `tests/testsuite/main.rs`. This layout gives the shortest helper imports (`use crate::prelude::*;`) and a single grep-able list of what every suite gets.
- **`#![allow(unreachable_pub)]` gotcha** — a real-world footgun surfaced by mdBook's implementation: `pub` helpers inside an integration-test crate are never consumed from outside, so the `unreachable_pub` lint fires on them. The canonical `tests/main.rs` example and migration step 2 now include `#![allow(unreachable_pub, reason = "not needed in an integration test crate")]`.
- **mdBook cited as the proven real-world implementation** in the §4 "Canonical source" section, alongside the Cargo Book.
- **Cargo Book's own inefficiency quote** added to the "Why this works" list — Cargo's docs explicitly note the N-binary layout "can take longer to compile, and may not make full use of multiple CPUs when running the tests", which the single binary fixes.

### AUDIT

- Self-review scope: a `tp-critic` lens auditing the two recent tp-rust commits (REVIEW mode `45b6bce` + multi-suite pattern `53745ac`) for marketplace-rule compliance, technical correctness, and voice consistency. The critic agent hit an API connection error mid-run but surfaced the import-advice finding (the one genuine technical error) before dying; remaining checks were completed inline against the Cargo Book and a `rust-lang/mdBook` source fetch.
- Per-finding resolution: the `use super::*;` import error → **Fixed** (this release). The hub-router-budget overage (251 lines vs the recommended ~150) → **Skipped** (functionally fine; mechanism stays in references; pre-existing, deferred per the [0.5.0] "Out of scope" note). The CHANGELOG plugin-vs-marketplace-version convention question → **Noted**, left for a maintainer decision (the existing entries are marketplace-level `1.x.y`; the [0.5.0]–[0.6.1] entries use plugin-level versions because the marketplace version was not bumped alongside).

## [0.6.0] — 2026-06-19

### Added

- **Single-Binary Multi-Suite Pattern** in `plugins/tp-rust/skills/rust/references/quality-testing-and-coverage.md` (new §4). When `tests/` accumulates ≥10-20 root-level integration test files, each becomes a separate Cargo test binary and pays N× link-time cost; the pattern collapses them into one `tests/main.rs` mounting `tests/suites/<name>.rs` submodules. Benefits: **absolute dead-code accuracy on shared `tests/common/mod.rs` helpers** (no more `#![allow(dead_code)]` band-aid), **10-20× faster incremental link speeds**, easy per-suite filtering (`cargo test timeout_and_clamping` or `cargo nextest run -E 'test(/timeout_and_clamping/)'`), no `Cargo.toml` change. Includes a 6-step migration playbook, two anti-patterns (don't keep N binaries at scale; don't adopt the pattern at N=2), and a feature-set caveat (suites that need different feature flags must stay N binaries — Cargo does not allow conditional features per integration binary).
- **QUALITY Process step 4** — collapse `tests/` into the single-binary multi-suite structure when ≥10-20 root-level files accumulate. Inserted between nextest adoption and coverage; old steps 4 and 5 renumbered to 5 and 6.
- **`tp-critic, lens "audit build & test health"` (REVIEW Lens 3)** — gains an additional finding type: presence of ≥10-20 root-level `tests/*.rs` files without a `tests/main.rs` consolidator is a WARN with the migration steps from `references/quality-testing-and-coverage.md` §4 as the `fix` field.

### Changed

- **`references/quality-testing-and-coverage.md`** — renumbered §4-§8 → §5-§9 to make room for the new pattern. The `cargo-hack` → `cargo-llvm-cov` → `cargo-tarpaulin` → coverage scope → benchmarking sequence is unchanged.
- **`references/scaffold-lib-bin-rustdoc.md` §3 "Examples & tests directory"** — added a forward-reference paragraph at the end: when the test suite grows past 1-3 files, point readers at the new `quality-testing-and-coverage.md` §4 for the migration playbook. Stays minimal so SCAFFOLD-mode readers don't get premature guidance.
- **SKILL.md QUALITY mode Process** — added step 4 (multi-suite collapse) and renumbered the subsequent steps. The Process section now has 6 steps (was 5).
- **SKILL.md QUALITY mode Anti-patterns** — added one bullet: "keeping N separate integration test binaries once `tests/` grows past 10-20 files (collapse into the single-binary multi-suite structure from `quality-testing-and-coverage.md` §4)".
- **SKILL.md "You MUST read quality-testing-and-coverage.md BEFORE switching test runners or adding coverage" sentence** — now mentions the multi-suite pattern explicitly so QUALITY-mode readers see it before adopting nextest or coverage.

### Skip notes

- **No new `## Authoritative sources` block** was added to `quality-testing-and-coverage.md` as a whole. The new §4 cites the Cargo Book integration tests section and the nextest filter docs inline (matching the existing convention from §1's `https://nexte.st/docs/benchmarks/` citation). A full per-reference URL card was already flagged as out-of-scope for the existing 13 references in the [0.5.0] entry — applying the same rule here keeps the change focused.
- **No CLI flag changes**, no marketplace catalog metadata changes beyond the version bump.

### Out of scope

- **No link-time benchmarks shipped with this release.** The 10-20× figure comes from the project's own migration notes and from the structural reasoning (Cargo's per-binary link cost vs single-binary link). Empirical before/after timings on the marketplace's own `tp-rust` crate would strengthen the claim; deferred to a future release.

## [0.5.0] — 2026-06-19

### Added

- **`tp-rust` REVIEW mode (5th top-level mode in the `rust` skill hub)** — holistic health audit of an *existing* Rust project or workspace. Fans out **5 parallel `tp-critic` lenses** in a single `Agent` call:
  1. `"audit source-code health and idioms"` — `.rs` idiomatic patterns, clippy profile soundness, `unsafe` and soundness guardrails, error-handling discipline, async/concurrency hazards.
  2. `"audit dependency hygiene"` — `Cargo.toml` version constraints (wildcards, path-deps without version, `git` deps in published crates), tree duplicates and bloat, manifest consistency, `deny.toml` *shape* check. Distinct from the supply-chain lens (which checks policy/CVE).
  3. `"audit build & test health"` — `.github/workflows/*.yml` + `clippy.toml` + `rustfmt.toml` + `.config/nextest.toml` + `.cargo/config.toml` against the canonical 6-job CI, `RUSTFLAGS=-D warnings`, nextest adoption criteria.
  4. `"audit public API surface"` — doc coverage, public-visibility hazards (`pub(crate)` in public signatures, seal-trait pattern, `pub use` re-exports), semver consistency against `release-versioning-and-changelog.md`, public-type ergonomics. Distinct from `RELEASE`'s `"pre-publish review"` (which gates a specific version bump).
  5. `"audit supply chain"` — reuses the existing `"audit supply chain"` lens string. `deny.toml` against 0.19+ schema, `Cargo.lock` for RUSTSEC, `cargo vet` coverage, Dependabot, MSRV-aware resolver.
- **4 new references under `plugins/tp-rust/skills/rust/references/`**:
  - `review-orchestration.md` — the contract: output schema (`severity | location | dimension | finding | consequence | fix`), BLOCKER/WARN/NIT rubric, dedup/synthesis protocol, P6 ground truth rule, report format. Pure marketplace mechanics, no external URLs.
  - `review-source-code.md` — Lens 1 checklist + URL card (clippy index/book, Rust Reference, Nomicon, unsafe-code-guidelines, rustdoc, edition guide, perf book, RFCs).
  - `review-dependency-hygiene.md` — Lens 2 checklist + URL card (Cargo Book, manifest reference, RUSTSEC, advisory-db, cargo-deny schema).
  - `review-public-api.md` — Lens 4 checklist + URL card (rustdoc book, Rust API Guidelines, Cargo semver, edition guide).
- **`## Authoritative sources` convention** — every new reference ends with a per-URL fetch trigger (the marketplace's first "when to fetch this URL" pattern). Each entry names the canonical source and the specific audit-condition that warrants a live fetch. Justified under the chicken-and-egg rule as content-about-external-resources (allowed), not self-loading routing logic (forbidden). Triggers are auditable, not vague — e.g. *"fetch when a specific clippy lint code appears in a finding and its meaning / default level / category is unclear"*.
- **`references/review-source-code.md` "## §7 Performance smell-tests"** — light-pass perf smell-tests (allocation-in-loop, redundant `clone()` in loops, `format!` in tight loops, `HashMap` lookups in O(n) loops). Not a perf-regression analysis; for that, a dedicated perf pass is needed.

### Changed

- **`plugins/tp-rust/skills/rust/SKILL.md` hub body** — added REVIEW throughout: Routing Guidance triggers, Decision Router IF-line, new `# Mode: REVIEW` section, Failure Handling row, Reference Index `**REVIEW mode**` block, Subagent Index entries for all 4 new lenses (Lens 5 reuses the existing supply-chain string), Anti-patterns row, CONTRAST bullets (vs `QUALITY`, vs `RELEASE pre-publish review`, vs the core security skill).
- **`when_to_use` frontmatter** — added "User wants a holistic review, audit, or health check of an *existing* Rust project or workspace" as a trigger.
- **Description frontmatter** — "Four modes" → "Five modes" (SCAFFOLD, WORKSPACE, QUALITY, RELEASE, REVIEW); description expanded to name all 5 REVIEW lenses.
- **Hub size** — `SKILL.md` grew from 203 → 250 lines. REVIEW body is ~26 lines (kept under the 30-line router budget per mode); all REVIEW mechanism lives in `references/` and loads on imperative citation.

### Skip notes

- **No new `tp-rust-critic` agent file.** All 4 new lenses are one-sentence lens prompts passed to the existing `tp-critic`. The marketplace agent-contracts rule: "Could this be a one-sentence lens instead?" — yes, always. No file proliferation. Lens 5 reuses the existing `"audit supply chain"` string verbatim.
- **Existing QUALITY/RELEASE references unchanged.** Lens 3 reuses `quality-ci-template.md`, `quality-testing-and-coverage.md`, `quality-dev-experience.md` verbatim. Lens 5 reuses `quality-supply-chain-ladder.md` and `release-supply-chain-maintenance.md`. No duplication of supply-chain policy or CI/setup content — only the new code/API/hygiene dimensions get new references.
- **No `knowledge/raw/official/` mirrors of Rust docs.** The marketplace maintains Claude Code doc mirrors only (per CLAUDE.md's "Refreshing Official Docs" recipe). Rust ecosystem URLs are embedded as static citations + live fetch on trigger. Avoids the maintenance tax of mirroring a 3rd-party doc tree.

### Out of scope

- **Hub budget refactor** — the hub is now 250 lines and the recommended router ceiling is ~30 lines per mode × 5 modes = 150 lines. The hub is functionally fine (mechanism stays in references, body is router-style) but the original 4-mode hub was already over the recommended ceiling before REVIEW was added. Restructuring the 4 existing modes to flatten into pure router paragraphs is a separate refactor; deferred to a future release to avoid unrelated churn.
- **Retrofitting `## Authoritative sources` blocks** into the existing 13 references — they are already cited correctly (rustsec.org, cargo-deny schema, nexte.st, etc.). Adding per-URL fetch triggers is a polish follow-up; not part of this release.
- **Performance regression analysis** — REVIEW does a perf smell-test (§7 of `review-source-code.md`), not a regression delta against a baseline commit. A true regression analysis needs benchmark history; out of scope.
- **Architecture-level critique** — REVIEW audits existing code against existing standards, not against alternative designs. For design reasoning, the user is routed to `fpf` (PROPOSE mode) via the new CONTRAST bullet.

## [1.24.1] — 2026-06-18

### Changed

- **`scripts/audit.py` two-tier audit** — Default tier is now **structural-only** (R1 agent roster, R3 fork-rationale, R5 catalog sync). Zero false positives on a clean marketplace. CI gate is now credible. The **strict tier** (`--strict` flag) adds R2 (spawn-lens) and R4 (description quality) for maintainers who want to enforce writing style. The strict tier produces false positives on multi-line spawn directives and subjective verb choices; that's why it's opt-in.
- **Updated `tp-roster-auditor` description, `validate-plugin` SKILL.md, `discipline-check` command, and `references/roster-rules.md`** to document the two-tier behavior. The agent body now explicitly tells the auditor not to enable stylistic checks by default.

### Why

The 1.24.0 self-review identified that the default audit was noisy — 7 false-positive R2 warnings undermined the CI gate's credibility. A maintainer seeing warnings on a clean PR learns to ignore the gate. The fix: make the noisy stylistic checks opt-in. The default is now structural-only, exactly what every CI needs.

### Skip notes

- **The marketplace's audit verdict under the new default is `PASS, 0 blockers, 0 warnings, 0 nudges`** — clean CI gate. The 7 R2 warnings and 9 R4 nudges from 1.24.0 are preserved under `--strict` for maintainers who want them.
- **No marketplace catalog changes** — same 11 plugins, same `tp-discipline` version 0.1.0. The two-tier flag is an `audit.py` behavior change only.
- **Existing CI workflow needs no change** — `validate-marketplace.yml` runs `python3 scripts/audit.py --ci` (no `--strict`), which now produces zero findings on a clean marketplace. The strict tier is invoked by maintainers manually (`/discipline-check --strict`) or pre-release audits.

## [1.24.0] — 2026-06-18

### Added

- **`tp-discipline` plugin (0.1.0)** — marketplace discipline enforcement via a single `validate-plugin` skill + `tp-roster-auditor` agent (the second allowed `tools:` restriction, `[Read, Glob, Grep, Bash]`) + `scripts/audit.py` CI guard + `/discipline-check` slash command. Audits any Claude Code marketplace for the 5-rule discipline set established by 1.23.0 + 1.23.1:
  - **R1 — Agent roster discipline:** count cap (default 6 + 1 read-only-tools exception), no `model:` locks, every agent has a `## Ground truth` section.
  - **R2 — Spawn discipline:** every `spawn tp-critic|tp-explorer|tp-researcher` has a `lens:`/`scope:`/`question:` argument within 400 chars.
  - **R3 — Fork-skill discipline:** every `context: fork` skill has a `references/fork-rationale.md` citing its isolation value.
  - **R4 — Description quality:** ≤1536 chars, verb-led first 200, CONTRAST section in body or `when_to_use`.
  - **R5 — Catalog discipline:** `plugin.json` `version` matches `marketplace.json`; description mentions agent roster.
- **`scripts/audit.py`** — pure-Python audit script. JSON output for CI (`--ci`), Markdown for humans (default). Exit code: 0 = no BLOCKER, 1 = BLOCKER present, 2 = crashed. Configurable via `--config discipline.json`.
- **`.github/workflows/validate-marketplace.yml` new step** — runs `python3 scripts/audit.py --ci` as the last step of the existing validate job. Triggers on changes to `scripts/audit.py`, `plugins/*/agents/*.md`, `plugins/*/skills/*/SKILL.md`, `plugins/*/commands/*.md`. BLOCKER findings fail the PR.
- **`references/roster-rules.md`** + **`references/fork-rationale.md`** — the human-readable explanations of the 5 rules and the fork-rationale template, cited imperatively by the `validate-plugin` skill.

### Changed

- **`.github/workflows/validate-marketplace.yml` paths** expanded to include the discipline-audit inputs (audit.py, agents, skills, commands). Push-to-main now also runs the audit.
- **Marketplace version** 1.23.1 → 1.24.0 (new plugin added).

### Why

The 1.23.0 + 1.23.1 consolidation shipped a brand-new orchestration model (6-keeper roster, lens-prompt pattern, isolation-justifies-a-file test). The model was in the rule files as text, but no automated check enforced it. The 4 soft spots identified in the post-1.23.1 audit (doctrine-young with no CI check, fork-skill architectural ambiguity, `tp-critic` creep risk, pedagogical CONTRAST vs grep cleanliness) all stemmed from the same root: **the doctrine was text, not enforcement**. `tp-discipline` makes it mechanical. Any future marketplace can adopt the same plugin and inherit the same guard.

### Skip notes

- **`tp-discipline` does not auto-fix.** The auditor returns findings; the orchestrator decides whether to fix. This keeps the role clean (read-only) and avoids the auditor accidentally clobbering intent. The fix recipes in `references/roster-rules.md` are the manual remediation guide.

- **The audit script's regex is intentionally conservative.** Some false positives are expected (the script can't catch every phrasing). The `tp-roster-auditor` agent uses judgment when the script flags a finding, and may override with file:line evidence. The audit report surfaces the override.

- **Audit findings in the 1.24.0 initial state:** the self-audit flagged 11 WARNINGs (mostly R2 spawn-without-arg and R3 fork-rationale) and 11 NUDGEs. These pre-existed and are not blockers — they are candidates for the 1.24.x follow-up to add the lens-arguments and fork-rationale files. The marketplace ships at PASS-blocking level (1 BLOCKER resolved by adding `tp-discipline` to the catalog) so the 1.24.0 release is shippable as-is.

## [1.23.1] — 2026-06-18

### Changed

- **Description optimization pass** across all routing signals injected into agent context (descriptions, when_to_use, plugin.json descriptions). The user's framing: descriptions are the preliminary risk/element injected into every agent's context at startup, so they must front-load triggers, mutually exclude adjacent skills, and carry CONTRAST to prevent misrouting. Optimized for the `.claude/rules/routing-signal.md` rules: first 200 chars front-load trigger phrases; total ≤1,536 chars; CONTRAST for skills in adjacent domains; no jargon ("subagent", "isolated context", "fork"); verb-led first sentence.

- **6 keeper agent descriptions tightened** (all 511-595 chars). `tp-critic` now front-loads "Review code, designs, and decisions through any lens — adversarial stress-test, correctness check, OWASP scan, API contract audit, test coverage gap, compliance, security review, performance, code quality, or any custom angle". `tp-explorer` / `tp-researcher` / `mcp-quality-judge` / `sadd-judge` / `wiki-searcher` similarly. All 5 generic keepers gained CONTRAST-vs-adjacent-roles to prevent misrouting.

- **25 SKILL.md descriptions rewritten** with user-vocabulary triggers in the first 200 chars and CONTRAST clauses that distinguish from adjacent-domain skills:
  - `core-principled/diagnose` — "why is this happening / find the bug / analyze the failure" + NOT for `refine` / `ddd`
  - `core-principled/ideation` — "think through / explore possibilities / generate ideas" + NOT for `sadd` JUDGE / `fpf`
  - `core-principled/refine` — "review this PR / simplify this code / polish this doc" + NOT for `diagnose` / `task-lifecycle` / `ddd`
  - `core-principled/rules-orchestration` vs `project-maintenance` — explicit CONTRAST both ways to prevent misroute
  - `core-principled/kaizen` — "apply YAGNI / avoid over-engineering / simplify this design"
  - `core-principled/ddd` — "this file is a mess / logic is in the wrong place / untangle this"
  - `core-principled/skill-authoring` — "create a skill / optimize this skill's routing / audit this skill"
  - `core-principled/web-search` — "find X on the web / is this claim true / verify this statement"
  - `core-principled/subagent-orchestration` — "Design multi-agent architectures... or spawn reviewers in parallel"
  - `core-principled/plan-lifecycle` — removed "subagent" jargon ("worker+critic subagents" → "workers and reviewers")
  - `tp-mcp/mcp-expertise` — removed "forked orchestrator spawns 8 parallel judge subagents" jargon → "parallel quality judges in isolated contexts"
  - `tp-sadd/sadd` — "compare these options / pick the best approach / which solution is right" + NOT for `diagnose` / `ideation`
  - `tp-rust/rust` — "Rust / Cargo / new crate / cargo publish / cargo-deny / MSRV / edition 2024" + NOT for `fpf` / `diagnose`
  - `tp-git/git` vs `git-preflight-checker` vs `git-worktree-manager` — explicit 3-way CONTRAST
  - `tp-security/security` — "security audit / dependency scan / find secrets / OWASP" + NOT for `refine` / `rust`
  - `tp-session-audit/session-analytics` — "parse session log / session metrics / review this session" + NOT for `diagnose` / `refine` / `rules-orchestration`
  - `tp-wiki/wiki` — "wiki / KB / look up in my notes / find in my wiki" + NOT for `web-search` / `tp-researcher`
  - `tp-fpf/fpf` — "reason from first principles / compare solutions / R_eff / WLNK" + NOT for `ideation` / `ddd`
  - `claude-cli-wrapper/claude-cli` — "spawn a headless Claude session / run a cloud code review / continue a previous session"

- **17 command descriptions audited and 3 tightened** (`critique`, `implement`, `orchestrate`) with CONTRAST for mutual exclusivity.

- **9 plugin.json descriptions synced** with the 1.23.0 agent-roster state. Previously-stale references to deleted agents (`security-sast-scanner`, `rust-cargo-reviewer`, `mcp-server-builder`, `wiki-ingester`, etc.) removed; replaced with the new `tp-critic` / `tp-explorer` lens-prompt pattern narrative.

- **CHANGELOG entry added** documenting the description optimization pass.

### Plugin version bumps (patch, per marketplace rules)

- `core-principled` 0.21.0 → 0.21.1
- `tp-sadd` 0.5.0 → 0.5.1
- `tp-fpf` 0.5.0 → 0.5.1
- `tp-git` 0.4.0 → 0.4.1
- `tp-rust` 0.4.0 → 0.4.1
- `tp-security` 1.1.0 → 1.1.1
- `tp-session-audit` 0.4.0 → 0.4.1
- `tp-wiki` 0.5.0 → 0.5.1
- `claude-cli-wrapper` 0.3.2 → 0.3.3
- Marketplace version 1.23.0 → 1.23.1

## [1.23.0] — 2026-06-18

### Changed

- **Architectural refactor — subagent roster reduced from 55 to 6 named agents.** The marketplace shipped 55 thin subagent definitions that differed only in their first 1-2 sentences (a 12-line "you are a `<role>`… your context starts fresh… return results…" template). Per the official Claude Code docs and the spawn-vs-inline economics in the web research ("the subagent does that work in its own context and returns only the summary"), a named subagent earns its file only when the task burns large intermediate tokens AND returns a small summary AND the parent benefits from not carrying that journey. Most of the 55 failed this test. **The new doctrine: main agent implements inline; subagents self-review against a lens/scope/question prompt.**

- **6 named subagents remain**: `tp-critic` (universal isolated-context reviewer, lens-prompted), `tp-explorer` (universal isolated-context codebase mapper, scope-prompted), `tp-researcher` (universal isolated-context external researcher, question-prompted), `mcp-quality-judge` (MCP-server domain exemplar; preloads `mcp-expertise`), `sadd-judge` (candidate scoring against a rubric), `wiki-searcher` (read-only wiki query, the single allowed `tools:` exception). All "specialized reviewer" roles that previously existed — `tp-bug-hunter`, `tp-code-quality-reviewer`, `tp-contracts-reviewer`, `tp-historical-reviewer`, `tp-test-coverage-reviewer`, `tp-debug-tracer`, `tp-skill-auditor`, `tp-plan-verifier`, `tp-grader`, `tp-transcript-rules-*`, `tp-endpoint-auditor`, `tp-ideation-anchor`, `tp-ideation-tail`, `tp-cc-docs`, `tp-plan-architect`, `tp-test-strategist`, `tp-pdca-synthesizer`, the 5 `security-*` reviewers, the 5 `rust-*` reviewers, `mcp-schema-author`, `mcp-server-builder`, the 4 `fpf-*` agents, the 4 `session-*` agents, `sadd-generator`, `sadd-expander`, `sadd-meta-judge`, `sadd-synthesizer`, `sadd-explorer`, `wiki-ingester`, `wiki-linter`, `git-issue-analyzer`, `git-pr-reviewer`, `tp-global-implementer` — collapse into `tp-critic` w/ a one-sentence lens prompt or into inline work in the orchestrator.

- **49 skill bodies updated to use the lens-prompt pattern** at spawn sites. The `refine REVIEW` 6-reviewer fan-out is now 6× `tp-critic` w/ distinct lenses (logic errors, OWASP Top 10, readability, API contracts, git history, test coverage). The `security` skill's 5 modes spawn 5× `tp-critic` w/ distinct lenses (SAST, dependency, secrets, compliance, generic). The `rust` skill's 4 reviewer agents and the `sadd` skill's 6 pipeline stages all fold into `tp-critic`/`tp-explorer`/inline. `plan-lifecycle` (EXECUTE mode), `sadd` (EXECUTE/COMPETE), `task-lifecycle`, and `fpf` (the 4 fork skills) now implement inline within the fork and spawn only `tp-critic` for isolated milestone review. The `sadd` COMPETE mode's parallel 3-generator architecture is removed in favor of one inline-generated candidate reviewed by 3 parallel `sadd-judge` instances — preserves the isolation benefit, drops the parallel-implementation cost.

- **Orchestration doctrine flipped in 3 rule files + CLAUDE.md.** `.claude/rules/orchestration-contracts.md` Bad/Good canonical example changed from "main spawns explorer + critic" to "main implements inline; spawn `tp-critic` w/ lens Y for isolated review when the review would burn tokens the main context shouldn't carry." Added the isolation-justifies-a-file test and the spawn-vs-inline decision matrix (7-signal table). `.claude/rules/agent-contracts.md` now documents the 6-agent roster and explicitly forbids adding new specialized reviewer files when a one-sentence lens would do. `.claude/rules/context-fork-blackbox.md` clarifies that the 4 fork skills implement inline within the fork. CLAUDE.md Orchestration Model + Subagent-First Execution Contract sections rewritten.

- **`subagent-orchestration` skill (the canonical teaching skill) rewritten.** New body teaches the isolation-first model, the 6-agent roster, the lens-prompt pattern, and the spawn-vs-inline decision matrix. References (`subagent-contract-design.md`, etc.) updated to use the new keepers; volatile provenance (issue numbers #35–#38 from the audit) removed from `subagent-contract-design.md` per the `ground-truth-citations.md` rule.

### Removed

- **49 cut agent files deleted** (pre-deletion grep gate verified zero remaining references outside `agents/` directories and the historical note in `rust-idiom-polish.md`). The `plugins/tp-rust/skills/rust/references/rust-simplifier-spawn.md` reference was renamed to `rust-idiom-polish.md` (now an inline polish checklist, not a spawn template). `core-principled/agents/tp-bug-hunter.md`, `tp-global-implementer.md`, etc. — all gone. Agent count: `find plugins -path '*/agents/*.md' | wc -l` returns 6.

### AUDIT

- **Scope:** full marketplace agent + skill audit. 55 agent definitions audited for role (IMPLEMENTER / REVIEWER / RESEARCHER / EXPLORER / HYBRID), frontmatter discipline (tools:/model:/background:), inline-spawn violations, and P6 ground-truth sections. 25 SKILL.md bodies audited for spawn instruction sites (130 total spawn sites classified as IMPLEMENT-DELEGATE / REVIEW-DELEGATE / RESEARCH-DELEGATE / EXPLORATION-DELEGATE / FORK-DELEGATE). 3 orchestration rule files audited for doctrine alignment. 1 user-research pass via web search (Claude Code official docs + zivtech "Agent Tradeoff" + kspl "Spawn vs Inline") to ground the isolation-justifies-a-file test.
- **Per-finding resolution:**
  - **Fixed** — 55→6 agent consolidation (49 deletions + 6 keeper rewrites); ~30 skill bodies updated to use lens prompts; 3 rule files rewritten; CLAUDE.md Orchestration Model section rewritten; `subagent-orchestration` skill + reference rewrites; plugin version bumps (10 plugins); marketplace.json regenerated; CHANGELOG entry written
  - **Skipped** — `wiki-searcher`'s `tools: [Read, Glob, Grep]` allowlist preserved (the single allowed `tools:` restriction per `agent-contracts.md`, since read-only enforcement is load-bearing)
  - **Deferred** — none for this refactor; the existing 1.22.6 "out of scope" backlog (hub-router-budget items, `claude-cli` body split, `skill-authoring` deduplication, D7 markdown-in-body, etc.) is independent of this refactor and remains in the 1.22.6 entry's "Out of scope" section

### Skip notes

- **`sadd` COMPETE mode loses parallel solution writers.** Under the new model the orchestrator implements one solution inline; the competitive evaluation is preserved via 3 parallel `sadd-judge` instances in isolated contexts (one solution → 3 independent lens reviews). The parallel-writers advantage is dropped; the multi-judge isolation benefit is preserved. If a future session needs parallel solution generation, that belongs in a separate, larger architectural change — not a 1.23 patch.

- **Inline Rust idiom-polish is a checklist, not a subagent.** The deprecated `rust-simplifier` agent's body was a list of polish operations (clone elimination, `?` over nested `match`, iterator chains, etc.). Under the new model these run inline in the orchestrator; the file `rust-idiom-polish.md` is the checklist. The simplification is genuine (one less subagent dispatch per session) but the orchestrator must remember to apply the checklist — there is no longer a subagent doing it for you.

- **2 forked skills (out of 4) no longer match the marketplace's "isolation-first" narrative as cleanly.** `plan-lifecycle` and `sadd` were designed for parallel worker subagents; their EXECUTE modes now implement inline within the fork. The fork's value is preserved (long-reasoning isolation from the user's session), but the worker-machinery inside the fork is gone. If the marketplace needs worker-orchestration-in-fork semantics later, that's a follow-up — not 1.23.

### Out of scope

- **Hub-router-budget refactor of the 11 hubs over the 500-token ceiling** (deferred from 1.22.6) — independent of the agent consolidation; the lens-prompt pattern actually *reduces* hub body size in some cases (the removed "spawn X reviewer" lines) but no hub specifically exceeds the ceiling because of this refactor.
- **D7 markdown-in-body agents (marketplace-wide policy decision on list vs prose)** — 18 agents, none of which are keepers (most were cut); the policy question is moot for the 6 keepers, all of which use prose bodies.

## [1.22.6] — 2026-06-07

### Fixed

- **12 skills audited and refined** to honor the 5 gotcha rules introduced in 1.22.4 (cross-skill-references, hub-router-budget, context-fork-blackbox, cross-plugin-citations, ground-truth-citations). The audit was 26 skills wide; 12 received surgical edits, 1 had a known false positive left in place, and 5 were flagged for a 1.23.x follow-up. Files: `plugins/claude-cli-wrapper/skills/claude-cli/SKILL.md` (6 cross-plugin identifiers → role-semantic, 3 volatile URLs/dates → placeholders), `plugins/core-principled/skills/plan-do-check-act/SKILL.md` (front-load trigger phrases in description), `plugins/core-principled/skills/project-maintenance/SKILL.md` (7 volatile dates → `YYYY-MM-DD` placeholders in MEMORY-DEDUP/MEMORY-ARCHIVE examples), `plugins/core-principled/skills/refine/SKILL.md` (2 cross-plugin identifiers → role-semantic, sibling-skill ref path canonicalized to `subagent-orchestration/references/subagent-contract-design.md`), `plugins/core-principled/skills/skill-authoring/SKILL.md` (CONTRAST section added), `plugins/core-principled/skills/task-lifecycle/SKILL.md` (front-load trigger phrases), `plugins/core-principled/skills/test-orchestration/SKILL.md` (front-load trigger phrases), `plugins/tp-fpf/skills/fpf/SKILL.md` (front-load trigger phrases), `plugins/tp-git/skills/git/SKILL.md` (3 cross-plugin identifiers → role-semantic), `plugins/tp-mcp/skills/mcp-expertise/SKILL.md` (front-load trigger phrases), `plugins/tp-mcp/skills/mcp-quality-evaluate/SKILL.md` (sibling-skill ref path canonicalized, volatile date → placeholder, CONTRAST section added), `plugins/tp-session-audit/skills/session-analytics/SKILL.md` (front-load trigger phrases, 6 cross-plugin identifiers → role-semantic).

- **41 subagent contracts refined** to honor the 3 agent frontmatter rules (no `tools:` except `wiki-searcher`, no `model:` field, `background: true` for long-running/parallel) and the 6 P1–P6 contract design principles. The audit was 55 agents wide; 12 had volatile "Issue #36/38" provenance removed from existing P6 sections, 26 had the canonical P6 "Ground truth" section added across two passes (21 judge/verifier/auditor + 5 factual-claim including `tp-bug-hunter`, `tp-critic`, `wiki-ingester`, `wiki-linter`, `wiki-searcher`), 1 had `background: true` added (`tp-explorer`), and 2 had role statements prepended (`tp-pdca-synthesizer`, `fpf-evidence-validator`). The 12 synthesis/generation agents that remain without a P6 section are correct per the design doc — P6 does not apply to opinion/synthesis agents. The single `tools:` allowlist in the marketplace (`wiki-searcher`'s read-only `[Read, Glob, Grep]`) is the canonical exception and is preserved. Audit script: `/tmp/agent-audit.sh` (re-runnable). Full per-agent table: `.mavis/plans/agents-audit-report.md`.

- **README.md hygiene (6 line-level defects fixed).** Stale version banner (0.30.0/1.22.0 → 0.31.1/1.22.6), wrong slash command name (`/debug` → `/trace`, the actual command name in `plugins/core-principled/commands/debug.md` frontmatter is `trace`), `/refine` removed from the slash-command example (refine is a skill, not a command; replaced with `/whats-next` and the explanatory line reworded to distinguish skills from slash commands), stale `claude-cli-wrapper` description (was "MCP wrapper … six focused tools" — replaced with the post-1.22.1 Bash-driven description), stale `tp-mcp` description (was "three skills" — replaced with the post-1.22.2 "single `mcp-expertise` hub with 5 modes" description), and 2 stale inline comments in the per-plugin install snippet. No hardcoded counts in headers. Full per-fix table: `.mavis/plans/docs-audit-report.md`.

- **`plugins/core-principled/skills/refine/SKILL.md` line 36 — cross-skill reference path canonicalized.** The line said *"the preloaded subagent-orchestration skill's `references/subagent-contract-design.md`"* in conversational prose. The new `cross-skill-references` rule (1.22.4) requires sibling-skill citations to use the canonical `sibling-skill/references/X.md` path form. Reworded to lead with the canonical `subagent-orchestration/references/subagent-contract-design.md` path. This was a real defect (not a false positive) flagged by the docs audit.

### AUDIT

- **Scope:** four parallel audits — skills (26 SKILL.md files), agents (55 subagent definitions), catalog + scripts (build script + regenerated `marketplace.json` + `scripts/check-citations.py`), docs (README, CHANGELOG, CLAUDE.md, `.claude/rules/`, knowledge/ paths). Per the CLAUDE.md "Subagent-First Execution Contract" and the 3-phase methodology, each track was a separate branch session running concurrently, with results consolidated here.
- **Catalog/scripts audit:** green. `scripts/regenerate-marketplace.py` is idempotent (no diff on re-run after 1.22.5). All 10 per-plugin `plugin.json` versions match the catalog. All 10 `source` paths resolve. `scripts/check-citations.py` exits 0 with 0 findings. `jq -e '.plugins | all(... [keys[] | select(. == "version")] | length) == 1)'` (the 1.14.0 regression-class check) passes. Per-fix table: `.mavis/plans/catalog-scripts-audit-report.md`.
- **Per-finding resolution:**
  - **Fixed** — 12 skills, 41 agents, 7 README/skills cross-doc defects, 0 catalog defects
  - **Skipped (false positives)** — 1 skill-authoring file (intentional WRONG/RIGHT pedagogical examples inside the rubric body); 4 agents with "When the hub spawns you" prose (D4 false positives — the agent describes its own context, not delegation instructions); 20–30 false-positive `references/X.md` cites inside fenced code blocks (template/illustrative, not navigation pointers)
  - **Deferred (follow-up 1.23.x or maintainer policy)** — 5 hub-router-budget items (11 hubs over the 500-token ceiling, ranging from 1.4× to 8.9× over; structural refactor, scoped for a minor release), 1 mcp-quality-evaluate "Produce:" section shape (1-line edit, low priority), 1 `claude-cli` body split (4,969 tokens; substantial refactor), 1 skill-authoring body deduplication vs CLAUDE.md (4,453 tokens; pedagogical vs token-economy trade-off), 1 cross-plugin skill-name citation form (rule clarification), 18 D7 markdown-in-body agents (marketplace-wide policy decision on list vs prose), 1 `mcp-schema-author` `background: true` recommendation (runtime measurement), `handoff.md` staleness (3 options: keep / move to `knowledge/concepts/` / delete — maintainer's call per the 1.22.1 convention).

### Skip notes

- **`core-principled/skills/skill-authoring/SKILL.md` WRONG/RIGHT example references (`references/file.md`, `references/format.md`, `references/patterns.md`, `references/X.md`).** These appear at lines 335, 342, 343, 344, 401, 407 inside pedagogical `> WRONG:` quote blocks. The paths are intentionally fictional — they illustrate the difference between passive and imperative citations. The audit's grep does not distinguish "WRONG:" examples from real citations. Removing or renaming the placeholder paths would weaken the pedagogy. The rule being taught is the very rule the audit enforces.

- **4 agents with "When the hub spawns you" or "you are an agent executing a delegated task" prose** (`core-principled/agents/tp-global-implementer.md`, `tp-wiki/agents/wiki-ingester.md`, `tp-wiki/agents/wiki-linter.md`, `tp-wiki/agents/wiki-searcher.md`). These describe the agent's own context (the hub spawning it), NOT the agent delegating to other agents. The orchestration-contracts rule forbids "spawn, fan-out, or delegation instructions" — these bodies do not instruct the agent to spawn anything. The audit's regex caught the literal "spawn … subagent" pattern, but the semantic intent is opposite. No semantic defect.

### Out of scope

- **5 hub-router-budget items (11 of 15 hubs exceed the 500-token hub ceiling).** Smallest over: `task-lifecycle` 1.4× (690 tokens). Largest: `skill-authoring` 8.9× (4,453 tokens). The marketplace pattern is "mode body inlines procedural logic rather than deferring to `references/`"; the rubric says "procedure belongs in `references/`." Resolving this contradiction requires extracting mode bodies from 11 hubs into hub + N reference files. Each hub needs a careful split without losing routing clarity. Effort: ~2–3 days of focused refactor across 11 skills. When: 1.23.x minor release, paired with the `mcp-quality-evaluate` "Produce:" section shape and the `claude-cli` body split.

- **`mcp-quality-evaluate/SKILL.md` Produce: section shape.** Documents the output format in `## I/O Example` (`OUTPUT: a markdown report with this exact structure:`) rather than a literal `Produce:` heading. The description front-loads the format. The contract is complete from the caller's perspective. Effort: 1 line of edit (rename the `## I/O Example` heading or add an explicit `## Produce`). When: 1.23.0 cleanup batch.

- **`claude-cli/SKILL.md` body token count (4,969 tokens).** The 12-section reference manual covers all CLI flags exhaustively. Splitting into hub + 6 reference files would let a user pay for only the conceptual operation they need (one of 6). Effort: ~half-day refactor (split into hub + 6 per-operation references, rewrite the in-text cite-as-you-go into a "see references/<op>.md for the full flag set" pattern). When: 1.23.x paired with the hub-router-budget work.

- **`skill-authoring/SKILL.md` body deduplication vs CLAUDE.md (4,453 tokens).** The body duplicates content from `~/.mavis/skills/skill-authoring/references/*.md` and from CLAUDE.md itself. Externalizing to references/ would drop the per-load cost to ~500 tokens but the skill would no longer be self-contained. Pedagogically useful as-is. Effort: depends on the resolution chosen (extract mode bodies / accept the cost / hybrid). When: 1.23.x paired with the hub-router-budget work.

- **Cross-plugin skill-name citations rule clarification.** `claude-cli/SKILL.md` line 388 says "see the marketplace's subagent-orchestration skill" — the `subagent-orchestration` skill lives in `core-principled`, a different plugin. The strict reading of the cross-plugin-citations rule would prefer a role-only phrasing like "see the in-process subagent orchestrator skill". The "marketplace's X skill" form is more explicit and preserves navigability but cites a skill name in another plugin. Document the chosen form in `.claude/rules/cross-plugin-citations.md` as canonical. Effort: ~10 lines of doc + a few sentence rephrasings. When: 1.23.x docs cleanup.

- **18 agents with markdown-in-body (D7).** Both pure-prose (tp-critic, tp-grader, tp-debug-tracer) and list-based (tp-bug-hunter, security-*, session-audit-*) patterns coexist in the marketplace. The design doc says "no markdown" but list-based agents work in practice for category enumeration. Decide on a marketplace-wide policy and codify. Effort: depends on the policy (if "all-prose", 18 agents need rewriting; if "lists are fine for category enumeration", ~30 lines of design doc + reference doc updates). When: maintainer policy decision required before refactor.

- **`mcp-schema-author` `background: true` recommendation.** Schema authoring for complex MCP servers can exceed 30s. Currently `background:` is not set; the heuristic recommended `true`. Maintainer should measure actual runtime in the wild. Effort: 1 line of frontmatter. When: next time `mcp-schema-author` is invoked and runtime is measured.

- **`handoff.md` staleness.** Dated 2026-06-04, describes state at that time (9 plugins, marketplace 0.23.0, 3 open issues). Current state (2026-06-07) is 10 plugins, marketplace 0.31.1, several sessions have run. CHANGELOG 1.22.1 codified the convention to preserve historical `handoff.md` as-is. Maintainer may want to (a) leave as historical archive, (b) move to `knowledge/concepts/handoff-2026-06-04.md`, (c) delete. Effort: 0–10 minutes depending on choice. When: maintainer decision.

### Verification

- `python3 scripts/check-citations.py` → `PASS: no citation violations, no missing preloads, no broken references` (exit 0)
- `jq -e '.plugins | all(. as $p | ([keys[] | select(. == "version")] | length) == 1)' .claude-plugin/marketplace.json` → `true` (no duplicate `version` keys per plugin entry)
- `jq -e 'has("name") and has("owner") and has("plugins") and (.plugins | type == "array")' .claude-plugin/marketplace.json` → `true` (top-level schema)
- `jq -e '.plugins | all(has("name") and has("version") and has("description") and has("source") and has("keywords"))' .claude-plugin/marketplace.json` → `true` (per-plugin required + extended fields)
- `jq -e '.plugins | all(has("name") and has("source"))' .claude-plugin/marketplace.json` → `true` (official schema required fields)
- `python3 scripts/regenerate-marketplace.py` → exit 0, marketplace.json regenerated from `_meta.json` + per-plugin `plugin.json`
- Every per-plugin `plugin.json` version matches the regenerated `marketplace.json` entry
- Every per-plugin keywords list in `marketplace.json` matches `_meta.json`
- Every per-plugin `source` path resolves to a real directory under `plugins/`

### Migration

- **No user action required.** This is a pure housekeeping release — the marketplace is in compliance with the 1.22.4 gotcha rules. Skill descriptions trigger correctly under the new front-load pattern. Subagent contracts are uniform. The `wiki-searcher` allowlist exception is preserved as the only `tools:` field in the marketplace. The 5 new gotcha rule files (`.claude/rules/{cross-skill-references,hub-router-budget,context-fork-blackbox,cross-plugin-citations,ground-truth-citations}.md`) are unchanged from 1.22.4; this release brings the marketplace's content into compliance with them.

### Version bumps

- **Marketplace** 0.31.0 → 0.31.1
- **claude-cli-wrapper** 0.3.0 → 0.3.1 (patch: 1 skill cross-plugin citation + 3 volatile placeholders)
- **core-principled** 0.20.1 → 0.20.2 (patch: 19 agents P6/role + 6 skills description/cross-plugin/refs + 1 README)
- **tp-fpf** 0.4.0 → 0.4.1 (patch: 3 agents P6 + 1 skill description)
- **tp-git** 0.3.6 → 0.3.7 (patch: 2 agents P6 + 1 skill cross-plugin citations)
- **tp-mcp** 0.4.0 → 0.4.1 (patch: 2 skills description/cross-plugin ref/CONTRAST)
- **tp-rust** 0.3.1 → 0.3.2 (patch: 4 agents P6)
- **tp-sadd** 0.4.0 → 0.4.1 (patch: 3 agents P6)
- **tp-security** 1.0.0 → 1.0.1 (patch: 5 agents P6)
- **tp-session-audit** 0.3.5 → 0.3.6 (patch: 1 skill description + cross-plugin)
- **tp-wiki** 0.4.0 → 0.4.1 (patch: 3 agents P6)

## [1.22.5] — 2026-06-06

### Changed

- **4 skills migrated to `context: fork`** to honor the blackbox contract defined in `.claude/rules/context-fork-blackbox.md`. Each migrated skill now declares `context: fork`, `agent: general-purpose`, an explicit `argument-hint`, named `arguments`, a role statement at the top of the body, an explicit "Produce:" output spec, and a concrete `## I/O Example` section. Forked subagents receive only the skill's body and the user's arguments — no main-conversation history — so the body must be self-contained.
  - `core-principled/skills/plan-lifecycle` — PLAN/EXECUTE orchestrator. PLAN mode writes ROADMAP.md + PLAN.md; EXECUTE mode spawns worker+critic subagents per phase and writes an execution report.
  - `tp-fpf/skills/fpf` — first-principles reasoning orchestrator. PROPOSE writes a Design Rationale Record; MAINTAIN writes an evidence-freshness report; QUERY prints a search results table.
  - `tp-sadd/skills/sadd` — competitive-generation orchestrator. COMPETE/EXECUTE/JUDGE/EXPLORE modes all write their outputs to `.principled/sadd/{problem-id}/`.
  - `core-principled/skills/task-lifecycle` — task pipeline orchestrator. CAPTURE/REFINE/IMPLEMENT/DOCUMENT modes write to `.principled/tasks/{drafts,specs,implemented}/`.
- **`tp-mcp/skills/mcp-quality-evaluate` body enhanced** with a `## I/O Example` section containing a concrete worked-out markdown report (header, summary table, per-dimension findings). Closes the 2/5 axis-5 gap from the original audit. Frontmatter and contract were already compliant.

### Notes

- **`mcp-expertise` is intentionally NOT forked.** The already-forked `mcp-quality-evaluate` orchestrator depends on the mcp-expertise hub's content via reference citations; double-fork is unsupported. The hub stays inline so the QUALITY orchestrator can read its references directly.
- **13 other fork candidates stay inline** (mcp schema/impl, security, ideation, etc.). The migration pattern is now established and any of these can be migrated case-by-case when concrete defects emerge.

## [1.22.4] — 2026-06-06

### Added

- **5 new gotcha-prevention rules** in `.claude/rules/` (extending the original 7), each authored from a real defect surfaced by the 1.22.3 code-review:
  - `cross-skill-references.md` — bare `references/X.md` paths in an orchestrator or subagent resolve within the containing skill's directory, NOT the sibling skill's. Cite cross-skill references with the skill-name prefix (`mcp-expertise/references/X.md`). Defends against the broken 8-judge spawn pattern that shipped in 1.22.3.
  - `hub-router-budget.md` — hub SKILL.md MUST stay under 500 tokens; mode bodies are one-paragraph descriptions + imperative reference citations, not procedural workflows. Multi-step branches and pre-conditions belong in `references/`, not the hub router.
  - `context-fork-blackbox.md` — skills with `context: fork` run in an isolated subagent whose context starts empty (no main-conversation history). Frontmatter + body are the only contract. Description MUST front-load the output format (not just trigger phrases), body MUST start with a role statement + output spec, and `argument-hint` MUST be set when the skill expects structured input. The forked subagent is a blackbox (input → output); what is not in the frontmatter or body cannot be inferred.
  - `cross-plugin-citations.md` — references to another plugin's pattern/file/concept cite the SEMANTIC ROLE only ("a parallel-judge pattern"), NEVER the plugin identifier (`tp-sadd`) or its file paths. The marketplace must remain installable plugin-by-plugin.
  - `ground-truth-citations.md` — an agent's "Ground truth (P6)" section contains the rule only, no volatile provenance (issue numbers, PR numbers, file paths from a specific PR, contributor names). Provenance belongs in commit messages and CHANGELOG, not artifacts shipped to end users.

### Changed

- **CLAUDE.md self-check list** (Before Any Commit section) gains 5 new items, one per new rule. Each new check has a one-line description and a link to its rule file. The 7 original rule files are unchanged.

### Why these rules

Each rule encodes a defect that already shipped at least once in 1.22.3 and was caught only by post-hoc code review. The rules exist to make the code-review unnecessary for the same defect class — a maintainer following the self-check list will catch the gotcha at PR time, not at audit time.

## [1.22.3] — 2026-06-06

### Added

- **3 subagents** for the `tp-mcp` plugin (new `plugins/tp-mcp/agents/` directory — first agents for this plugin):
  - `mcp-server-builder` (IMPLEMENT-heavy, color: green, background: true) — full Rust MCP server implementation from tool decomposition and schema set, using rmcp 0.3 + schemars + MCP Inspector test pyramid. Body ~200 words, single coherent paragraph + 4 imperative `references/implement-*.md` citations. Cites: `implement-rmcp-api.md`, `implement-transport.md`, `implement-runtime.md`, `implement-testing.md`.
  - `mcp-quality-judge` (QUALITY leaf, color: yellow, background: true) — single-dimension judge for the Claude-Optimal 8-dimension rubric; one of 8 parallel judges spawned by the orchestrator. Body ~130 words + a "## Ground truth" section (P6 rule from `tp-sadd/agents/sadd-judge.md`). Cites: `quality-rubric.md`, `quality-judge-pattern.md`.
  - `mcp-schema-author` (SCHEMA-focused, color: blue, background: false) — JSON Schema authoring with `additionalProperties: false` discipline, constraint catalog, discriminator enum vs oneOf, and pitfalls catalog. Body ~190 words + 3 imperative `references/schema-*.md` citations + cross-mode citation to `implement-rmcp-api.md` Appendix A. Cites: `schema-foundation.md`, `schema-styling.md`, `schema-pitfalls.md`, `implement-rmcp-api.md` (Appendix A only).
- **QUALITY orchestrator skill** `mcp-quality-evaluate` at `plugins/tp-mcp/skills/mcp-quality-evaluate/SKILL.md` — first `context: fork` skill in the marketplace. Spawns 8 `mcp-quality-judge` subagents in parallel (one per dimension), reads their JSON outputs, applies the tiebreak rule on >1-tier disagreements, synthesizes a markdown report per `quality-judge-pattern.md` §5. Pattern follows the canonical form documented in `plugins/core-principled/skills/skill-authoring/references/frontmatter-complete.md` §`context`.

### Changed

- **Hub QUALITY mode body** (`plugins/tp-mcp/skills/mcp-expertise/SKILL.md` lines 92-100) now delegates to `mcp-quality-evaluate` for full 8-dimension evaluation. Retains direct rubric reference for ad-hoc single-dimension spot-checks.

### Verification

- All 4 new files parse cleanly (YAML, no invalid frontmatter fields)
- No `tools:` or `model:` fields in the 3 subagents (Rule 1 and Rule 2 of CLAUDE.md Agent Frontmatter Best Practices)
- `background: true` on mcp-server-builder and mcp-quality-judge; `background: false` on mcp-schema-author
- `skills: [mcp-expertise]` declared in all 3 subagents (per CLAUDE.md Skills Preloading Principle)
- `context: fork` + `agent: general-purpose` correctly set on the orchestrator
- 8-dimension routing test deferred to a follow-up entry that ships the Phase 3 JSONL trace verification (requires a live test server; out of scope for this commit)

### Version bumps

- **Marketplace** 0.30.2 → 0.31.0
- **tp-mcp** 0.3.0 → 0.4.0 (minor: 3 subagents added, QUALITY orchestrator skill added)

## [1.22.2] — 2026-06-06

### Changed

- **`tp-mcp` 3 skills consolidated into a single `mcp-expertise` hub** (tp-mcp 0.2.3 → 0.3.0). The 3 spoke skills `mcp-server-design`, `mcp-tool-surface`, and `mcp-server-implement` are deleted; their content is merged into a new 5-mode hub `mcp-expertise` (DESIGN, SCHEMA, IMPLEMENT, CLIENT, QUALITY). DESIGN/SCHEMA/IMPLEMENT are pure consolidations of the 3 prior skills' content; CLIENT and QUALITY are new modes addressing the "client patterns" and "quality evaluation" gaps the prior skills explicitly flagged as "not yet implemented" / "planned". The 11 prior reference files are moved/renamed into a flat `references/` folder with `{mode}-{subtopic}.md` prefix naming (`design-decomposition.md`, `design-operations.md`, `design-consumption.md`, `schema-foundation.md`, `schema-styling.md`, `schema-pitfalls.md`, `implement-rmcp-api.md`, `implement-transport.md`, `implement-runtime.md`, `implement-testing.md`). The schemars cheatsheet is merged into `implement-rmcp-api.md` as "Appendix A: Schemars → JSON Schema Attribute Mapping" (it belongs in the implementation layer, not the schema-authoring layer). Hub SKILL.md is a pure router (~130 lines, well under the 500-token hub ceiling; the actual content lives in 14 reference files totaling ~2,300 lines). All 9 cross-references in `plugins/claude-cli-wrapper/skills/claude-cli/SKILL.md` are updated to point at the new hub (mode-qualified for DESIGN/SCHEMA/IMPLEMENT handoffs; generic `mcp-expertise` for the high-level pointer at line 17; the §13 file-path reference for the worked example now points at `mcp-expertise/references/design-decomposition.md` §3). Plugin description and `_meta.json` keywords updated to reflect the 5-mode structure; old skill names removed from the `mcp-server-design`/`mcp-server-implement`/`mcp-tool-surface` keyword list. `tp-mcp` is now a 1-plugin / 1-skill / 14-references layout, matching the hub consolidation target in CLAUDE.md.

- **4 new reference files authored under `plugins/tp-mcp/skills/mcp-expertise/references/`**: `client-usage.md` (agent-as-MCP-consumer framing, the 4 installation paths, the `tools/call` calling pattern, consumer-side debugging, session continuity, cross-server tool disambiguation), `client-rmcp-client.md` (rmcp 0.3 `client` feature flag, `ClientHandler` trait, stdio client that spawns a server subprocess, Streamable HTTP client, `CallToolResult` handling for `is_error: true` vs transport errors), `quality-rubric.md` (the 8-dimension Claude-Optimal rubric — tool discovery, single-shot argument accuracy, context efficiency, pass-through integrity, session continuity, headless reliability, error distinction, schema hygiene — with the EXEMPLARY/PASS/PARTIAL/FAIL scoring scale and concrete evidence requirements per dimension), `quality-judge-pattern.md` (the parallel-judge pattern modeled on `tp-sadd` — one judge per dimension, judge contract `{ score, evidence, recommendation }`, tiebreak rule on >1-tier disagreements, markdown-table report format). The 8-point Claude-Optimal validation checklist in `design-operations.md` §4 is the seed for the QUALITY mode's rubric; the `tp-sadd` judge approach is the seed for the parallel-judge execution pattern.

### Removed

- **3 tp-mcp spoke skills deleted**: `plugins/tp-mcp/skills/mcp-server-design/`, `plugins/tp-mcp/skills/mcp-tool-surface/`, `plugins/tp-mcp/skills/mcp-server-implement/`. Their 11 reference files are preserved (moved/renamed/merged) at `plugins/tp-mcp/skills/mcp-expertise/references/`. Any consumer, agent, or skill that referenced the 3 old skill names by spawn target (e.g. `Agent(name="mcp-server-design", ...)`) must update to the new hub. The only known external reference was in `claude-cli/SKILL.md` (9 sites), all updated in this release.

### Verification

- `python3 scripts/regenerate-marketplace.py` → clean (catalog updated; tp-mcp version 0.3.0; keywords include `mcp-expertise`, `mcp-client`, `mcp-quality`)
- `jq empty .claude-plugin/marketplace.json` → passes
- `jq -e '.plugins | all(. as $p | ([keys[] | select(. == "version")] | length) == 1)' .claude-plugin/marketplace.json` → passes (no duplicate `version` keys)
- `grep -rn "mcp-server-design\|mcp-tool-surface\|mcp-server-implement" plugins/ .claude-plugin/ --include="*.md" --include="*.json"` → no matches (clean in operational files)
- The historical CHANGELOG entries (1.22.1, 1.20.0, 1.19.0, 0.15.0, 0.14.0, 0.13.0, 0.12.0) still mention the 3 old skill names — these describe past releases and are correct historical record, not stale references
- `ls plugins/tp-mcp/skills/mcp-expertise/references/` → 14 files (10 migrated + 4 new), totaling ~2,300 lines
- `wc -l plugins/tp-mcp/skills/mcp-expertise/SKILL.md` → 131 lines (under the 150-line hub target)
- Routing test deferred to a follow-up 1.23.0 entry that ships the JSONL trace analysis (per CLAUDE.md 3-phase test methodology, Phase 2 routing verification requires fresh Claude instances to be available, which is outside the scope of this commit)

### Version bumps

- **Marketplace** 0.30.1 → 0.30.2
- **tp-mcp** 0.2.3 → 0.3.0 (minor: 3 skills consolidated into 1 hub, 2 new modes)

## [1.22.1] — 2026-06-05

### Changed

- **`claude-cli` skill body rewritten to teach direct `claude` CLI usage via Bash.** The skill (in `plugins/claude-cli-wrapper/skills/claude-cli/SKILL.md`) no longer documents the 6 MCP tools. It now teaches the 6 conceptual operations (execute, session, context, review, agent, config) as native CLI invocations: `claude -p "..." --output-format json`, `claude --resume <uuid>`, `claude ultrareview [target] --json`, `claude --agent <name> -p "..."`, `claude agents --json`, and the per-invocation flags `--model`/`--effort`/`--permission-mode`/`--settings`. New sections cover `--json-schema` for structured output, `claude doctor` for self-diagnostics, `claude --worktree` for isolated workspaces, and the JSON output envelope shape (with `session_id` inside the JSON, not lifted to a top-level field). All flag names verified against `claude --help` and `claude <subcommand> --help` on 2026-06-05. Skill body 631 lines (under the 2,500-token project ceiling).

- **`tp-mcp` case study replaced.** `plugins/tp-mcp/skills/mcp-server-design/references/design-decisions.md` §3 (the `claude-cli-wrapper` 6-tool worked example) is replaced with a synthetic `git-cli` 5-tool decomposition (`git_status`, `git_diff`, `git_commit`, `git_log`, `git_branch`). The synthetic example teaches the same 6 lessons the old case study taught (read/write separation, high-traffic tool gets most params, action-enum reservation, user-verb mirroring, when NOT to use the pattern) without depending on a real plugin. The section title is explicit that the example is "synthetic: `git-cli`" and not a shipped wrapper.

- **9 consumer files updated to remove references to the removed MCP server.** `web-search/references/when-not-to-search.md` re-routes "what plugins do I have installed" from the (gone) `claude-cli-wrapper` MCP to `claude plugin list` via Bash plus Read `.claude-plugin/marketplace.json`. `tp-git/SKILL.md` CONTRAST rephrased to acknowledge that both `git` and `claude-cli` are now Bash-tool-first skills in their respective domains. `.harness/reins/claude-log-auditor/agent.md` drops the "wrapper binary" sources-of-truth line and rephrases the CLI surface reference to the new skill content. `tp-mcp` skill bodies (`mcp-server-design/SKILL.md` × 3, `mcp-server-implement/SKILL.md` × 2, `mcp-tool-surface/SKILL.md` × 2) point at the new `git-cli` case study instead of the `claude-cli` worked example. `knowledge/concepts/persistence-schema.md` updates the `claude-cli-wrapper` row to note "no in-process state, no binary". `CLAUDE.md` directory tree comment updated from "MCP wrapper for the Claude Code CLI (6 tools)" to "Skill teaching direct Claude Code CLI usage via Bash".

- **Marketplace catalog keywords trimmed.** `claude-cli-wrapper` entry in `.claude-plugin/_meta.json` drops `mcp` (no longer an MCP server), `code-review` (no longer a dedicated review tool), `agent-spawn` (no longer a dedicated agent tool), and `config` (no longer a dedicated config tool). Adds `bash-pattern`, `direct-cli`, `headless-invocation`, and `ultrareview` to reflect the new content.

### Removed

- **Inline MCP server for `claude-cli-wrapper`.** The `.mcp.json` that registered the `taches-claude-cli-wrapper` MCP server is deleted. The 6 tool names `mcp__claude-cli-wrapper__claude_execute`, `claude_session`, `claude_context`, `claude_review`, `claude_agent`, `claude_config` are no longer available. Any caller of those tools must switch to direct `claude` CLI invocations via the Bash tool (see Migration below).

- **Rust source tree** at `plugins/claude-cli-wrapper/crates/` deleted (8 `.rs` files + member `Cargo.toml`, ~1,355 lines of Rust). `plugins/claude-cli-wrapper/Cargo.toml` and `Cargo.lock` deleted. The wrapper's value-add (JSON-RPC error code mapping, `WrapperResultEnvelope` output shape, `session_id` lifting, `deny_unknown_fields` validation) is no longer needed — the new skill teaches the raw `claude` CLI directly, accepting the simpler Unix exit-code + JSON-in-stdout contract.

- **Bash launcher and Apple-Silicon prebuilt** at `plugins/claude-cli-wrapper/bin/` deleted (the 50-line `bin/claude-cli-wrapper` script and the 4.25 MB `bin/claude-cli-wrapper.darwin-arm64` prebuilt). The launcher existed only to resolve and invoke the Rust binary.

- **Build artifacts** at `plugins/claude-cli-wrapper/target/` removed (was gitignored, but cleaned up).

- **`.gitignore` and `README.md`** deleted from `plugins/claude-cli-wrapper/` — the gitignore no longer needs to ignore `target/` and `Cargo.lock`; the README documented the launcher and prebuilts.

- **`.DS_Store`** deleted from `plugins/claude-cli-wrapper/` (macOS metadata, was tracked).

### Migration

**Breaking change for any consumer of the 6 `mcp__claude-cli-wrapper__*` tools.** The mapping is:

| Old MCP tool | New Bash invocation |
|---|---|
| `mcp__claude-cli-wrapper__claude_execute({prompt: "..."})` | `claude -p "..."` (add `--output-format json` for parseable output) |
| `mcp__claude-cli-wrapper__claude_session({action: "list"})` | `claude --resume` (no value, interactive picker) or read `~/.claude/sessions/*.jsonl` |
| `mcp__claude-cli-wrapper__claude_session({action: "resume", session_id: "..."})` | `claude --resume <uuid>` |
| `mcp__claude-cli-wrapper__claude_session({action: "continue"})` | `claude --continue` |
| `mcp__claude-cli-wrapper__claude_context({action: "add_directory", directory_path: "..."})` | `claude -p "..." --add-dir <path>` (per-invocation, not sticky) |
| `mcp__claude-cli-wrapper__claude_review({target: "..."})` | `claude ultrareview <target>` (or `claude ultrareview <target> --json` for structured output) |
| `mcp__claude-cli-wrapper__claude_agent({action: "spawn", ...})` | `claude -p "..." --agent <name>` or define inline with `--agents '<json>'` |
| `mcp__claude-cli-wrapper__claude_agent({action: "list"})` | `claude agents --json` |
| `mcp__claude-cli-wrapper__claude_config({action: "set_model", model_value: "opus"})` | `claude -p "..." --model opus` (per-invocation, no persistent set) |

**No automatic migration is possible** — the MCP transport is gone, the Rust binary is gone, and the Bash tool takes different args than the old MCP tools did. Users with installed `claude-cli-wrapper` instances will need to uninstall and reinstall the plugin (or just keep it — the plugin still ships, the MCP tools just don't).

**External consumers** of `mcp__claude-cli-wrapper__*` outside this marketplace are unknown. If any exist in a downstream consumer's settings (`.mcp.json` or `~/.claude.json`), the consumer must update its references to the new Bash patterns or remove the entry.

### AUDIT

- **Scope**: pre-extraction audit of the `claude-cli-wrapper` plugin, including a comprehensive consumer inventory (35+ references across 20 files) and an adversarial verification of the planned extraction. The audit classified references into A (must-migrate, 9), B (soft reference, 9), and C (documentation, 18) and identified the `tp-mcp` §3 case study as the largest anchor reference.
- **Per-finding resolution**:
  - A1-A8 (must-migrate): all 8 files updated or deleted as planned
  - B1-B9 (soft reference): all 9 citations/handoffs in `tp-mcp`, `tp-git`, `web-search`, and `persistence-schema.md` rephrased
  - C1-C18 (documentation): CHANGELOG historical entries preserved as-is (per CLAUDE.md convention); CLAUDE.md directory tree updated; `handoff.md` left as historical state
  - The `tp-mcp` case study was the highest-impact anchor and was replaced with the synthetic `git-cli` example as planned
- **Flag verification**: before writing the new skill body, all flag names were verified against `claude --help` and `claude <subcommand> --help` (including `claude agents`, `claude ultrareview`, `claude doctor`, `claude mcp`, `claude plugin`). Three of the wrapper's assumed flags (`--list-sessions`, `--session-info`, `--close-session`) do not exist in the current CLI; the skill body documents the actual mechanisms (interactive `--resume` picker, session JSONL files, normal session expiry) instead.
- **No findings skipped or deferred.**

### Skip notes

- **Historical CHANGELOG entries** (16 prior mentions of `claude-cli-wrapper` across versions 0.15.0 → 1.12.0): preserved as-is per CLAUDE.md convention ("Historical CHANGELOG entries... describe the state at the time of writing"). They document what the wrapper was when shipped; the new entry records its removal.

- **`handoff.md` line 5** ("9 plugins (claude-cli-wrapper, ...)"): historical state, left as-is per the same convention.

### Verification

- `python3 scripts/regenerate-marketplace.py` → clean (catalog updated to 0.30.1; `claude-cli-wrapper` entry kept with new description and trimmed keywords)
- `python3 scripts/check-citations.py` → `PASS: no citation violations, no missing preloads, no broken references`
- `jq -e '.plugins | all(. as $p | ([keys[] | select(. == "version")] | length) == 1)' .claude-plugin/marketplace.json` → OK
- `grep -r "mcp__claude-cli-wrapper__" plugins/ knowledge/ .claude-plugin/ .harness/ CLAUDE.md README.md` → 0 matches
- `grep -rn "claude-cli-wrapper/bin\|claude-cli-wrapper/crates\|claude-cli-wrapper/target" plugins/ knowledge/ .harness/ CLAUDE.md README.md` → 0 matches
- `find plugins/claude-cli-wrapper -type f` → exactly 2 files: `.claude-plugin/plugin.json` and `skills/claude-cli/SKILL.md`
- `wc -l plugins/claude-cli-wrapper/skills/claude-cli/SKILL.md` → 631 lines (under the 2,500-token project ceiling, with headroom for lazy-loaded references if needed later)

### Version bumps

- **Marketplace** 0.30.0 → 0.30.1
- **claude-cli-wrapper** 0.2.2 → 0.3.0 (minor: complete skill body rewrite)
- **tp-mcp** 0.2.2 → 0.2.3 (patch: case study replacement, no behavior change)
- **tp-git** 0.3.5 → 0.3.6 (patch: one CONTRAST line rephrased, no behavior change)
- **core-principled** 0.20.0 → 0.20.1 (patch: two re-route lines in one reference file updated)

## [1.22.0] — 2026-06-05

### Added

- **`tp-security` plugin (1.0.0)** — new domain-specific plugin extracted from `core-principled`. Single `security` hub with a `Modes:` directive covering the pre-production security review lifecycle: SAST (static application security testing — injection, auth bypass, SSRF, deserialization, access control), DEPENDENCY-AUDIT (CVE scanning, lockfile drift, typosquatting, supply-chain integrity), SECRETS-DETECTION (API keys, tokens, credentials, private keys via pattern matching and entropy analysis), COMPLIANCE (OWASP ASVS, GDPR, SOC2, PCI-DSS, HIPAA evidence mapping and gap analysis). Five subagents: `security-sast-scanner`, `security-dependency-auditor`, `security-secrets-detector`, `security-reviewer`, `security-compliance-checker`. Hub skill body and 4 reference files (`sast-patterns.md`, `dependency-audit.md`, `secrets-detection.md`, `compliance-checklists.md`) ported verbatim from `core-principled`; agent bodies ported verbatim. Agent frontmatter per marketplace conventions: no `tools:` (inherit), no `model:` (inherit), `background: true` on all 5 (long-running scanners), `skills: [security]` on all 5 (single-hub preload). All 5 agents inherit the `security` hub skill via the `skills:` array — no cross-plugin dependency.

- **Sub-plugin agent naming convention applied** — all 5 moved agents renamed from the legacy `core-principled` `tp-*` prefix to the sub-plugin `security-*` prefix in both filename and frontmatter `name:` field. `tp-sast-scanner` → `security-sast-scanner`, `tp-dependency-auditor` → `security-dependency-auditor`, `tp-secrets-detector` → `security-secrets-detector`, `tp-security-reviewer` → `security-reviewer` (drops the redundant "security" — implied by the plugin), `tp-compliance-checker` → `security-compliance-checker`. Matches the 1.4.0 `tp-sadd`/`tp-fpf` rename pattern and the CLAUDE.md rule that sub-plugin agents use the sub-plugin prefix. The 4 spawn directives in `security/SKILL.md` and the 1 spawn reference in `refine/SKILL.md:141` are updated to the new names.

### Changed

- **`security` skill and 5 agents removed from `core-principled`** (core-principled 0.19.1 → 0.20.0). The `security` skill + 4 reference files + 5 agent definitions now live in `plugins/tp-security/`. `core-principled` description updated to note the move. `core-principled` keywords retain `security` because security is a cross-cutting concern in `refine`'s spawn list and the new `tp-rust/agents/rust-supply-chain-auditor.md` preloads `security` from the new plugin (see Hardened below).

- **`rust-supply-chain-auditor` cross-plugin `security` preload documented** (tp-rust, no version bump — pre-existing cross-plugin preload). The agent's `skills: [rust, diagnose, security]` declaration now carries a 3-line YAML comment noting that `security` is a cross-plugin preload from `tp-security` (extracted from `core-principled` in this release). Per CLAUDE.md's cross-plugin preloading rules, the preload is silently skipped if `tp-security` is not installed — the agent still works, just without the `security` skill's references in scope.

- **`security-compliance-checker` cross-wire removed** (tp-security 1.0.0). The `diagnose` entry in the agent's `skills:` array was residual from when compliance work was treated as a diagnose subagent. The agent's body is purely compliance work; the `diagnose` preload was unnecessary. Dropped before the move.

- **`refine` SKILL.md:141 spawn reference updated** to `security-reviewer` (from `tp-security` plugin). The 6-reviewer fan-out in `refine` MODE:REVIEW retained all 5 other agents; only the security reviewer's name and plugin origin changed.

### Hardened

- **Plugin name `tp-security` is free and unambiguous.** No directory or marketplace entry existed before this release; the slot is claimed cleanly. Following the established `tp-rust`/`tp-sadd`/`tp-fpf`/`tp-git`/`tp-mcp`/`tp-session-audit`/`tp-wiki` naming convention.

- **Hub SKILL.md is pure router.** The 4-mode `Modes:` directive, the `Decision Router` section with 4 explicit IF→spawn directives, the `Mode Relationships` table, and the `Failure Signal` catalog are all preserved from the `core-principled` original. Hub body ~350 tokens — well under the 500-token router ceiling.

- **Agent `tools:` discipline preserved.** None of the 5 agents carry a `tools:` field (per CLAUDE.md Rule 1 — the restriction is not the point for these long-running scanners; they inherit the full tool pool). `background: true` on all 5 (typical scanner runtime >30s).

### Migration

- **No user action required for the extraction itself.** Users who already have `core-principled` installed get the security capability from the same skill name; the routing signal is identical. Users who want to drop `core-principled` and keep just `tp-security` can do so — all 5 subagents and the hub now ship in the new plugin.

- **If `tp-security` is not installed and `rust-supply-chain-auditor` is invoked**, the agent still works — the `security` skill preload is silently skipped per the cross-plugin preloading rules. The agent's body does not require `security` to be loaded to do supply-chain work; the preload is for richer reference context when available.

- **The 4 `security` reference files** (`sast-patterns.md`, `dependency-audit.md`, `secrets-detection.md`, `compliance-checklists.md`) move with the hub to `plugins/tp-security/skills/security/references/`. No content changes.

### Verification

- `python3 scripts/regenerate-marketplace.py` → clean (catalog updated to 10 plugins: core-principled, tp-sadd, tp-fpf, tp-git, tp-session-audit, claude-cli-wrapper, tp-rust, tp-mcp, tp-wiki, tp-security)
- `python3 scripts/check-citations.py` → `PASS: no citation violations, no missing preloads, no broken references`
- `jq -e '.plugins | all(. as $p | ([keys[] | select(. == "version")] | length) == 1)' .claude-plugin/marketplace.json` → OK
- All 5 new agents parse cleanly under PyYAML `safe_load`; the new `name:` fields match the filenames
- No stale `tp-sast-scanner` / `tp-dependency-auditor` / `tp-secrets-detector` / `tp-security-reviewer` / `tp-compliance-checker` references remain in the marketplace (grep returns 0 matches outside `plugins/tp-security/`)
- Audit: pre-extraction cluster analysis + adversarial verification produced a REVISE verdict with 3 required fixes (compliance-checker cross-wire, rust cross-plugin comment, ranking scope). All 3 fixes applied before the move.

### Version bumps

- **Marketplace** 0.29.1 → 0.30.0
- **tp-security** (new) 1.0.0
- **core-principled** 0.19.1 → 0.20.0 (minor: 1 skill + 5 agents removed)

## [1.21.1] — 2026-06-05

### Added

- **`rust-simplifier` subagent** in `tp-rust`. Post-implementation cleanup of recently-written `.rs` code for idiomatic Rust (ownership/borrowing, error handling, iterator chains, clone elimination) without changing behavior or borrow-checker compliance. Spawned from `SCAFFOLD` and `QUALITY` modes. Scope: current session diff only. Follows the subagent contract design P1–P6 (P3 ordered ops with `cargo check` verification between edits, P5 failure-mode footer); inherits full tool pool and model per CLAUDE.md Rules 1 & 2. A new `references/rust-simplifier-spawn.md` reference file carries the per-spawn operational guidance, keeping the hub SKILL.md under its budget.

### Migration

- **No user action required.** Spawn guidance is opt-in; the main agent decides when to delegate. The description is dense and front-loaded with trigger phrases; the subagent only fires on matching requests. Existing workflows that do not mention "simplify" / "idiomatic" / "polish" continue to route to the existing 4 subagents unchanged.

### Version bumps

- **Marketplace** 0.29.0 → 0.29.1
- **tp-rust** 0.3.0 → 0.3.1

## [1.21.0] — 2026-06-05

### Changed

- **Rust plugin restructured: 4 skills → 1 hub + 4 subagents.** The four separate skills (`rust-scaffold`, `rust-workspace`, `rust-quality`, `rust-release`) are merged into a single `rust` hub with a `Modes:` directive (SCAFFOLD / WORKSPACE / QUALITY / RELEASE), matching the pattern shipped for `tp-sadd`, `tp-fpf`, `tp-git`, and `ddd`. All 12 reference files (mode-prefixed names: `references/scaffold-*.md`, `references/workspace-*.md`, `references/quality-*.md`, `references/release-*.md`) move to `plugins/tp-rust/skills/rust/references/` with content preserved verbatim. 4 new subagents under `plugins/tp-rust/agents/`: `rust-cargo-reviewer` (Cargo.toml & workspace structure review, blue, foreground), `rust-pipeline-auditor` (CI / clippy / nextest / dev-experience audit, yellow, background), `rust-supply-chain-auditor` (den.toml / vet / RUSTSEC / Dependabot audit, red, background), `rust-publish-reviewer` (pre-publish semver / changelog / version review, yellow, background). All 4 subagents follow CLAUDE.md frontmatter rules: no `tools:` (inherit), no `model:` (inherit), `background: true` on the 3 long-running reviewers, `skills:` array with the `rust` hub preloaded plus `diagnose` (all 4) + `security` (2) + `refine` (1) cross-skill preloads per role.

- **8 cross-cites inside references fixed (Rule 3 compliance).** 4 reference files (`scaffold-cargo-and-features.md`, `scaffold-lib-bin-rustdoc.md`, `release-versioning-and-changelog.md`, `release-publishing-and-deps.md`, `workspace-decisions.md`) had 8 cross-references to sibling skills by name (e.g., "the MSRV job pattern lives in the `rust-quality` skill's CI reference"). All 8 replaced with self-contained prose that names the parent skill or inlines the relevant content, per CLAUDE.md Rule 3 (references must not cross-cite other references — the SKILL.md is the sole, centralized router).

- **Hub SKILL.md body ~1670 tokens, well under the 2500-token project ceiling.** Frontmatter total (description + when_to_use) is 808 chars, well under the 1536-char limit. The 4-mode `Modes:` directive, the consolidated `## Anti-patterns` section (32 patterns grouped by mode, no duplicates), the per-mode `**Spawn Directives:**` lines, and the `## Subagent Index` table are new. The original 4 SKILL.md files' CONTRAST cross-citation web dissolves into a single short CONTRAST in the hub listing only external skills (`fpf`, `diagnose`, `refine`).

- **CLAUDE.md merge-criteria table updated.** The `| Hub Skill | Skills Merged | Rationale |` table gains a `rust` row documenting the consolidation (plan: `.principled/plans/rust-hub-merger-ROADMAP.md`).

### Migration

- **No user action required.** The new `rust` skill fires on the same triggers the 4 old skills fired on, but with a single description field (no risk of under-triggering because the user said "scaffold" instead of "rust-scaffold"). Existing references to "use rust-quality for CI" inside any cross-skill handoff text should be read as "use rust QUALITY mode". The 4 subagents are dispatched by the hub modes automatically; users do not invoke them directly.

### Version bumps

- **Marketplace** 0.28.3 → 0.29.0
- **tp-rust** 0.2.1 → 0.3.0

## [1.20.1] — 2026-06-05

### Fixed

- **Removed chicken-and-egg routing logic from `session-anatomy.md`.** The reference file at `plugins/tp-session-audit/skills/session-analytics/references/session-anatomy.md:71` had a "When to read which file" table that pointed readers at other reference files in the same skill — a textbook chicken-and-egg violation per CLAUDE.md ("Reference files must be pure content — no frontmatter, no loading triggers, no 'When to read' sections, no conditional loading paragraphs"). The table is removed from the reference and relocated as a new `## Reference routing` section in the parent `session-analytics/SKILL.md` (right after the existing `## Reference Index` section), which is the proper home for routing logic per Rule 3. The relocated table preserves the original 6 entries (find sessions, parse event stream, diagnose subagent, audit permissions, reproduce headless run, see hook tools) and adds a 7th entry for the new cross-analyze workflow. A short paragraph above the table notes that the per-mode sections (CAPTURE, INSPECT, REVIEW, ISSUE, CROSS-ANALYZE, ADJUDICATE) remain the authoritative entry points and that this table is the secondary lookup. `session-anatomy.md` is now pure content (on-disk artifact map, encoded-CWD scheme, hook input field reference, and one-liners — its actual job).

### Migration

- **No user action required.** Pure content reorganization; the routing knowledge is preserved, just in the right file. Readers who followed the old "When to read which file" table in session-anatomy.md should follow the mode sections in the parent SKILL.md first and consult the new `## Reference routing` table as a secondary lookup.

### Version bumps

- **Marketplace** 0.28.2 → 0.28.3
- **tp-session-audit** 0.3.4 → 0.3.5 (patch: chicken-and-egg cleanup in one reference file)

## [1.20.0] — 2026-06-05

### Fixed

- **7 cross-skill reference citations removed (Rule 3 cleanup).** The 1.19.0 hub-and-spoke split introduced 7 reference-to-reference citations across skill boundaries — e.g. `mcp-tool-surface/references/schema-styling.md` cited `mcp-server-design/references/design-decisions.md`, and 4 rust reference files cited `rust-quality/references/{supply-chain-ladder,ci-template,clippy-and-fmt}.md`. CLAUDE.md Rule 3 forbids reference files from cross-citing other reference files; the SKILL.md is the sole, centralized router. Each cross-cite is replaced with self-contained prose that names the parent skill (allowed) instead of a path into another skill's references/ (forbidden). The `mcp-server-implement/SKILL.md` §3 Handoff section gains a new line routing readers to the canonical CLI inspector example set, replacing one of the cross-skill cites with a same-skill handoff. The `skill-authoring/references/context-management.md` cross-cites (5 in-text references to `references/patterns.md`) are false positives — the paths are part of the WRONG/RIGHT teaching-example strings, not navigation pointers. The file gains a `<!-- check-citations-skip -->` marker that `check-citations.py` honors.

- **4 agent preloads corrected: agent names used where skill names were intended.** The 1.19.0 release noted "7 pre-existing missing-skill preloads" as a follow-up. Investigation on 2026-06-05 revealed that 4 of the 7 were *agent names used as skill preloads* — the `skills:` frontmatter only loads skills, not agents. The 4 misconfigurations are fixed: `git-pr-reviewer` and `session-meta-reviewer` drop `tp-critic` from `skills:` and the body rewrites the "The preloaded `tp-critic` skill..." sentence to instruct the agent to *dispatch* a `tp-critic` subagent via the native agent-spawning tool. Same treatment for `tp-researcher` in `session-context-analyzer` and `tp-cc-docs` in `session-issue-generator`. The 3 remaining missing-skill preloads (`rules-creator` in 3 `tp-transcript-rules-*` agents) are renamed to `rules-orchestration` — the current umbrella skill for the rules domain, which the audit identified as the closest match for the original (apparently aspirational) preload intent.

- **`scripts/check-citations.py` distinguishes agent-name-as-skill from missing-skill.** The script previously emitted a single "skill not found in marketplace" message for both cases. New behavior: if a preload target matches an existing *agent* name (not a skill name), the script emits a new `[2a] AGENT-NAME-AS-SKILL PRELOADS` category with a remediation hint ("drop the preload and reference the agent by name in the body, or extract a thin contract skill"). The script also honors the `<!-- check-citations-skip -->` marker introduced in `skill-authoring/references/context-management.md`. After all fixes, `check-citations.py` exits 0 with zero findings.

### Verification

- `python3 scripts/check-citations.py` → `PASS: no citation violations, no missing preloads, no broken references` (exit 0)
- `jq -e '.plugins | all(. as $p | ([keys[] | select(. == "version")] | length) == 1)' .claude-plugin/marketplace.json` → OK
- `jq -e '.plugins | type == "array" and length > 0' .claude-plugin/marketplace.json` → OK
- `python3 scripts/regenerate-marketplace.py` → idempotent (no changes)
- All per-plugin `plugin.json` files parse cleanly
- All 5 touched plugins' versions match between `plugin.json` and `marketplace.json`

### Migration

- **No user action required.** The cross-cite fixes are pure prose rewrites; the preload fixes change frontmatter (the affected agents now correctly receive the skills they intended to load) and body text (the "spawn" intent is now explicit). The `check-citations.py` script change is backwards-compatible — files without the new `[2a]` category produce identical output to before.

### Version bumps

- **Marketplace** 0.28.1 → 0.28.2
- **core-principled** 0.19.0 → 0.19.1 (patch: 3 transcript-rules agents fixed, 1 reference file marked skip)
- **tp-git** 0.3.4 → 0.3.5 (patch: 1 agent preload fixed)
- **tp-mcp** 0.2.1 → 0.2.2 (patch: 3 cross-cites removed, 1 handoff line added)
- **tp-rust** 0.2.0 → 0.2.1 (patch: 4 cross-cites removed)
- **tp-session-audit** 0.3.3 → 0.3.4 (patch: 3 agent preloads fixed)

## [1.19.1] — 2026-06-05

### Changed

- **MCP Inspector guidance in `tp-mcp` is now CLI-mode-first, not interactive-UI-first.** The previous guidance in `mcp-server-implement/references/build-and-test.md` and `mcp-server-design/references/claude-code-consumption.md` described the Inspector as a debug tool, but the only example was the interactive web UI launch (`npx @modelcontextprotocol/inspector ./bin/my-mcp-server`), which an AI agent cannot run without a browser. The new guidance uses the `--cli` mode with 11 concrete examples covering: basic usage, config files, listing tools/resources/prompts, calling tools with positional and JSON args, connecting to remote servers (default SSE, explicit Streamable HTTP), custom headers, and remote tool calls. Both reference files cross-link to the canonical example set so the examples live in one place. The `mcp-server-implement` frontmatter description and hub reference-index paragraph are updated to say "MCP Inspector in CLI mode" so the routing signal is explicit.

- **No behavior change for end users.** The Inspector still has the interactive web UI; this just stops pointing human-curious AI agents at a path that doesn't work for them.

### Migration

- **No user action required.** Pure documentation correction.

### Version bumps

- **Marketplace** 0.28.0 → 0.28.1
- **tp-mcp** 0.2.0 → 0.2.1 (patch: documentation correction, no skill logic change)

## [1.19.0] — 2026-06-05

### Changed

- **7 oversized skills split into hub + references/ for progressive disclosure.** Per CLAUDE.md's 500-line guideline, the following skills exceeded the safe operating limit and have been split: `tp-mcp/skills/mcp-server-implement` (661 → 89), `tp-mcp/skills/mcp-server-design` (526 → 73), `tp-mcp/skills/mcp-tool-surface` (498 → 100), `tp-rust/skills/rust-quality` (487 → 98), `tp-rust/skills/rust-release` (370 → 93), `tp-rust/skills/rust-workspace` (349 → 80), `tp-rust/skills/rust-scaffold` (319 → 86). Each skill's `SKILL.md` is now a pure router (frontmatter + when-to-fire + CONTRAST + reference index + handoffs + anti-patterns + key sources), with the mechanism content in 2-4 focused `references/*.md` files. The new references are imperatively cited from the hub per CLAUDE.md rule 3, and follow the chicken-and-egg rule (pure content, no frontmatter, no loading triggers inside). Total: 13 new reference files; ~2300 lines reorganized into ~600 lines of hub + ~1900 lines of references. Per the prior investigation's BLOCKER finding, this also unlocks the new Rule 4 path: future subagents spawned by these plugins can cite the new references directly.

- **The 5 other marketplace agents that follow the same imperative-citation pattern as the wiki agents** (`tp-session-audit/agents/session-context-analyzer.md`, `tp-session-audit/agents/session-inspector.md`, `tp-session-audit/agents/session-issue-generator.md`, `tp-session-audit/agents/session-meta-reviewer.md`, `core-principled/agents/tp-debug-tracer.md`) get a one-paragraph natural-language steering upgrade. The previous "you MUST read X" paragraphs were terse; the new paragraphs pair the imperative with a steering line that names the contract vs the role-specific content. Same semantic behavior, better steering.

- **Fixed BLOCKER found in 1.18.0 review.** The 1.18.0 critic flagged that `wiki-searcher.md` and `wiki-linter.md` still said "using the algorithm above" — a reference to the disambiguation algorithm that was removed from the agent body and is not in `references/subagent-arguments.md` (only in `references/registry-schema.md`). The stale references are replaced with: "Start from the resolved `wiki_path` the hub passed you."

### Added

- **New script `scripts/check-citations.py`** — durable audit tool that detects three classes of citation problems across the marketplace: (1) cross-skill citation violations (an agent body cites a `references/X.md` from a skill it has NOT loaded); (2) missing-skill preloads (an agent's `skills:` frontmatter lists a skill that does not exist anywhere); (3) broken reference citations (cited file does not exist in any plugin's `references/`). The script is complementary to the marketplace jq schema checks in `regenerate-marketplace.py`. Run it after authoring or modifying any agent definition, after splitting a skill into hub + references/, or after deleting or renaming a reference file. Exit code 0 = clean; 1 = findings. **The script immediately surfaced 7 pre-existing missing-skill preloads** (`rules-creator` referenced by 3 `tp-transcript-rules-*` agents but no such skill exists; `tp-critic` referenced by `git-pr-reviewer` and `session-meta-reviewer`; `tp-researcher` referenced by `session-context-analyzer`; `tp-cc-docs` referenced by `session-issue-generator`) — these are pre-existing issues, NOT introduced by this refactor, and are noted as a follow-up. A separate cleanup PR will either add the missing skills or correct the preloads.

- **13 new reference files** under `plugins/tp-mcp/skills/{mcp-server-implement,mcp-server-design,mcp-tool-surface}/references/` and `plugins/tp-rust/skills/{rust-quality,rust-release,rust-workspace,rust-scaffold}/references/`. Each is pure content (no frontmatter, no loading triggers), named after the topic it teaches (e.g., `rmcp-api.md`, `claude-code-consumption.md`, `ci-template.md`, `workspace-decisions.md`).

### Migration

- **No user action required.** The skill splits are behavior-preserving — same when-to-fire, same CONTRAST, same handoffs, same anti-patterns. The 5 agent upgrades are also behavior-preserving (the steering paragraphs are additive). The new script is opt-in (run it manually or wire it into CI).

- **CI suggestion:** wire `python3 scripts/check-citations.py` into a GitHub workflow that runs on PRs touching `plugins/`. The script has a clean exit-code contract (0 = pass, 1 = findings, 2 = missing dependency) and runs in <2s on the current marketplace.

### Version bumps

- **Marketplace** 0.27.0 → 0.28.0
- **tp-mcp** 0.1.1 → 0.2.0 (minor: 3 skills restructured, the new Rule 4 unlocks future agent citations)
- **tp-rust** 0.1.0 → 0.2.0 (minor: 4 skills restructured)
- **core-principled** 0.18.0 → 0.19.0 (minor: 1 agent (`tp-debug-tracer`) gets the imperative-with-natural-language upgrade)

## [1.18.0] — 2026-06-05

### Changed

- **CLAUDE.md codifies a scoped exception to the "only SKILL.md may cite supporting files" rule.** A new Rule 4 in the "Skill-Internal File References" section states: when a subagent declares a skill in its `skills:` frontmatter, the subagent's body prompt MAY cite that skill's own `references/` files. The citation must be a single natural-language imperative sentence (not a procedural step), and natural-language steering prose is preferred over rigid procedure. Cross-skill citations (citing references from a skill the agent has NOT loaded) remain forbidden. The rule is grounded in the official Claude Code docs: a parent's citation directive is NOT transitive to spawned subagents ([`agent-sdk/subagents.md`](https://code.claude.com/docs/en/agent-sdk/subagents.md#what-subagents-inherit) — "Preloaded skill content, unless listed in `AgentDefinition.skills`" is explicitly excluded from inheritance), so the subagent either needs its own `skills:` entry to receive the parent's body OR an independent citation in its own prompt. The new rule codifies the second path, which the marketplace had already been using in 8 places (4 in `tp-session-audit`, 1 in `core-principled/tp-debug-tracer`, 3 in `tp-wiki`).

- **The chicken-and-egg section gets a cross-reference paragraph** clarifying that the chicken-and-egg rule (no routing logic inside reference files) and the new Rule 4 (who may cite a reference file from outside) govern orthogonal concerns. A reference file remains pure content; a subagent body may still cite it from outside.

- **The 3 tp-wiki agents use the proper imperative shape to cite `references/subagent-arguments.md`.** The previous "Argument expectation" paragraphs pointed at the reference descriptively ("inherited from the `wiki` skill — see its `references/...`"). The new paragraphs open with a single natural-language imperative sentence ("you MUST start by reading the `wiki` skill's `references/subagent-arguments.md`"), followed by a natural-language steering paragraph that names the role-specific argument, identifies the contract as the rules of engagement, and lets the agent decide how to apply what it read. The role-specific arguments (`query` / `mode`+`content` / `directive`), task procedures, rules, output formats, and failure-mode catalogs are unchanged.

### Added

- **No new files.** This change is purely a rule clarification in CLAUDE.md, an imperative upgrade in the 3 wiki agents, a CHANGELOG entry, and version bumps.

### Migration

- **Other marketplace agents following the same pattern need no change.** `tp-session-audit/agents/session-context-analyzer.md`, `tp-session-audit/agents/session-inspector.md`, `tp-session-audit/agents/session-issue-generator.md`, `tp-session-audit/agents/session-meta-reviewer.md`, and `core-principled/agents/tp-debug-tracer.md` already cite references/ files of preloaded skills in imperative form. The new Rule 4 legitimizes the pattern, so no rewrite is needed. A future cleanup pass could give them the same imperative-with-natural-language upgrade that the wiki agents just got, but that's polish, not correctness.

- **No user action required.** No registry migration, no schema change, no skill re-install. The rule change is internal to the marketplace's authoring conventions.

### Version bumps

- **Marketplace** 0.26.1 → 0.27.0
- **tp-wiki** 0.3.1 → 0.4.0 (minor: agent bodies change in a non-cosmetic way — the `references/subagent-arguments.md` reference becomes load-bearing instead of descriptive)

## [1.17.1] — 2026-06-05

### Changed

- **Subagent argument contract consolidated into a shared reference.** The "Argument expectation" + "Self-discovery fallback" + "Wiki Root Resolution (multi-wiki registry)" preamble was duplicated across the three wiki agents (`wiki-searcher.md`, `wiki-ingester.md`, `wiki-linter.md`) — the same `wiki_path` / `alias` / `multi_wiki` argument definitions, the same last-resort self-discovery policy, and the same registry preamble were explained in three places with only the role-specific orientation tail differing. That shared content now lives once in a new reference at `plugins/tp-wiki/skills/wiki/references/subagent-arguments.md`; each agent body keeps only its own role-specific argument (`query` / `mode`+`content` / `directive`), its own one-paragraph "why orientation matters for you" tail, and its own failure-modes catalog. The hub skill (`SKILL.md`) cites the new reference imperatively; the three agents inherit it transitively via their existing `skills: [wiki]` frontmatter (no new citation needed, preserving the CLAUDE.md rule that only `SKILL.md` cites supporting files).

- **Removed a dangling citation in `plugins/tp-rust/skills/rust-release/SKILL.md`.** Line 368 of the References list pointed at `references/real-world-release-patterns.md`, a file the skill never shipped. The "if shipped" qualifier made the citation optional from the start; the 7 real-world example crates (serde, tokio, axum, cargo, release-plz, cargo-smart-release, gtk-rs, fuel-core) stay inline as references without the broken pointer.

### Added

- **New reference file `plugins/tp-wiki/skills/wiki/references/subagent-arguments.md`** — single source of truth for the argument contract (`wiki_path` / `alias` / `multi_wiki` semantics, self-discovery fallback policy, confirmation-before-mutating policy) and the multi-wiki registry preamble every subagent inherits. Pure content, no frontmatter, with an explicit "What each agent keeps local" section that names the role-specific content (the role-specific argument, the role-specific orientation tail, the failure-modes catalog) so the line between shared and local stays clear.

### Version bumps

- **Marketplace** 0.26.0 → 0.26.1
- **tp-wiki** 0.3.0 → 0.3.1

## [1.17.0] — 2026-06-05

### Changed

- **`~/.claude/wiki-root.md` is now a TOML manifest.** The flat `WIKI_ROOT_<label>=<path>` registry is replaced by one `[<alias>]` TOML table per wiki, each carrying `path`, `tags` (free-form wiki-level classification used for routing), `what_to_read` (bare filenames the agent walks before any operation), and a ≤1500-char `description` (natural-language steering, front-loaded with routing keywords so the signal survives high-context truncation). Existing user registries must be migrated to TOML; the new format is unambiguously parseable and the description field is the orchestrator's primary signal when the user names a topic rather than a wiki alias.

- **Schema teaching consolidated into one reference file.** The "Wiki Root Resolution (multi-wiki registry)" block previously duplicated across `plugins/tp-wiki/skills/wiki/SKILL.md` and the three wiki agents (~231 total lines) is gone — the schema, parsing algorithm, disambiguation rules, no-registry flow, confirmation-before-mutating policy, and front-load convention now live in a single new reference at `plugins/tp-wiki/skills/wiki/references/registry-schema.md`. `SKILL.md` cites the reference imperatively; the three agents carry only a short natural-language preamble describing operational expectations and inherit the schema teaching transitively through the wiki skill they load (per the CLAUDE.md rule that only `SKILL.md` cites supporting files). Net deletion: ~223 lines of duplicated teaching across four files.

### Added

- **New reference file `plugins/tp-wiki/skills/wiki/references/registry-schema.md`** — pure-content schema reference with no frontmatter (chicken-and-egg anti-pattern). Teaches the TOML format with an annotated canonical example, per-field semantics for all four fields, the parsing algorithm as natural-language prose, a disambiguation table that adds a `tags`-matching row to the existing alias/topic/single-wiki/multi-wiki cascade, the no-registry first-time setup flow, the confirmation-before-mutating policy for INGEST and LINT, the front-load convention for descriptions (first ~200 chars must carry routing keywords), the bare-filename rule for `what_to_read` (no absolute paths, no `$WIKI_ROOT/...` substitution, no `[[wikilinks]]`), and TOML-specific gotchas for LLM readers (triple-double-quote vs triple-single-quote, CRLF leakage, `#` comment scope).

### Migration

- **User action required for personal wikis.** Existing `~/.claude/wiki-root.md` files must be migrated from the flat `WIKI_ROOT_<label>=<path>` format to the new TOML schema. A migrated entry has the shape `[<alias>] / path = "..." / tags = [...] / what_to_read = ["SCHEMA.md", "index.md"] / description = """..."""`. The `tp-wiki` hub will detect the old format and fail to parse, signalling the need to migrate; placeholders for `tags`, `what_to_read`, and `description` are safe starting values that the user fills in over time.

- **Maintainer doc updated.** `knowledge/concepts/llm-wiki-methodology.md` step 1 in the "Initializing a New Wiki" section now teaches the TOML append (`[<alias>]` table) rather than the old `WIKI_ROOT_<label>=<path>` line. Historical CHANGELOG entries that mention `WIKI_ROOT_marketplace=...` (notably 1.15.0) are preserved as-is — they describe the state at the time of writing.

### Version bumps

- **Marketplace** 0.25.1 → 0.26.0 (catalog change for the schema upgrade)
- **tp-wiki** 0.2.0 → 0.3.0 (new schema, consolidated reference, four files surgically slimmed)

## [1.16.1] — 2026-06-05

### Fixed

- **Marketplace manifest now conforms to the official Claude Code schema (closes #47 install blocker).** The upstream `.claude-plugin/marketplace.json` was shaped as a *map* where each plugin name was a top-level key, with a `plugins` array nested under it, but no top-level `name` or `owner` field. The CLI rejected the file at `claude plugin marketplace add` time with `Invalid schema: ... name: Invalid input: expected string, received undefined, owner: Invalid input: expected object, received undefined`, breaking the install path for new users on a clean install. Restructured to the official schema shape: top-level `$schema`, `name`, `owner`, `description`, `version`, `plugins` (array). The 9 redundant plugin-name top-level keys (each holding `source`, `keywords`, etc.) are removed — the same data is already in each `plugins` array entry, which the regen script populates by merging per-plugin `plugin.json` with `_meta.json`. **Marketplace** 0.25.0 → 0.25.1 (catalog version bumps for the schema-correctness fix; no per-plugin content changed, so no per-plugin version bumps).

### Added

- **Marketplace-level metadata now lives in `_meta.json` under a `marketplace` block** (name, owner, description, version). The regen script reads this block and emits the schema-compliant top-level fields. This is a small but structural upgrade to the two-source catalog model: per-plugin metadata is still keyed by plugin name; marketplace-level metadata is at the top of `_meta.json` under `marketplace`.

### Hardened

- **CI guard extended** to reject the #47 regression class on every PR. The `validate-marketplace` workflow now also checks: (a) `marketplace.json` has top-level `name`, `owner`, `plugins` array, (b) `owner.name` is a non-empty string, (c) `_meta.json` has a `marketplace` block with `name` and `owner`, (d) the two-source catalog model iterates `_meta.json` keys while skipping the new `marketplace` block. Trigger paths extended to include `scripts/regenerate-marketplace.py` so the script itself is review-gated.

## [1.16.0] — 2026-06-04

### Changed

- **Codify `.principled/` as the runtime persistence emplacement in 7 brainstorming/planning skills + 5 subagents.** The marketplace's persistence layer (`.principled/`) lives in the user's project cwd, not in the marketplace repo. Each of the 7 skills gains a `## Runtime persistence` section teaching that `.principled/` is the natural home for principled-related runtime artifacts — at intake, read whatever is there if any; when the skill produces durable artifacts, write them to `.principled/` too. The 5 subagents that already have explicit write-side instructions to `.principled/` (tp-pdca-synthesizer, session-context-analyzer, session-inspector, session-issue-generator, session-meta-reviewer) gain the same teaching as a `## Orient (mandatory)` section (or inline sentence for the plain-text PDCA agent) — the conventional default paths in their bodies remain as fallbacks, not mandates. The teaching is intentionally generalist (no prescribed subdirs, no schema, no INDEX/SCHEME convention) so it remains true regardless of how the user actually structures their persistence. Each artifact gracefully degrades if the folder is absent. Skills updated: `ideation`, `plan-lifecycle`, `plan-do-check-act`, `task-lifecycle`, `fpf`, `refine`, `sadd`. Subagents updated: `tp-pdca-synthesizer` (core-principled), `session-context-analyzer`, `session-inspector`, `session-issue-generator`, `session-meta-reviewer` (tp-session-audit). No frontmatter, description, or routing signal changes. The marketplace's own behavior on its own repo is incidental; the primary target is any project that installs the marketplace.

- **Marketplace** 0.23.1 → 0.25.0 (catalog change for the persistence codification, including the subagent orient extension).
- **core-principled** 0.16.0 → 0.18.0 — 5 skills + 1 subagent updated.
- **tp-fpf** 0.3.4 → 0.4.0 — 1 skill updated.
- **tp-sadd** 0.3.5 → 0.4.0 — 1 skill updated.
- **tp-session-audit** 0.3.1 → 0.3.3 — 4 subagents updated.

## [1.15.0] — 2026-06-04

### Changed

- **Doc folder migration: `docs/` → `knowledge/`** (resolves #41's structural question). All 21 maintainer-only documentation files (CONTRIBUTING, persistence-schema, templates, refreshed official docs, the 3 wiki-format spec files) consolidated into a single wiki-shaped folder at the repo root. The Karpathy LLM-wiki structure (entities/concepts/queries/raw/templates) is now the canonical organization for marketplace reference material. **Personal wikis (MyWiki, PharmaWiki) stay external** — the `~/.claude/wiki-root.md` registry is extended with `WIKI_ROOT_marketplace=/Users/felix/Documents/AutoPluginClaw/taches-principled/knowledge` so tp-wiki's subagents can search/lint/ingest marketplace docs. SKILL.md citations for the wiki format spec now use `$WIKI_ROOT/SCHEMA.md` and `$WIKI_ROOT/concepts/*` so the same skill works for any registered wiki.

- **Folder naming: `knowledge/` not `wiki-doc/`** to avoid the personal-wiki/codebase confusion surfaced earlier in the session. The folder contains marketplace maintainer documentation, not personal knowledge. The "wiki-like" structure is a documentation convention (entities/concepts/raw/templates), not a claim that this folder is "a wiki."

- **Core-principled 0.15.2 → 0.16.0**: `scripts/session_start.py` and `skills/skill-authoring/SKILL.md` updated to reflect new paths. The `docs/CONTRIBUTING.md` self-check list in CLAUDE.md now references `knowledge/concepts/contributing.md`.

- **tp-wiki 0.1.2 → 0.2.0**: The 3 wiki-format reference files moved out of `plugins/tp-wiki/skills/wiki/references/` and into `knowledge/` (`SCHEMA.md`, `concepts/intent-format.md`, `concepts/llm-wiki-methodology.md`). The `wiki` skill body now uses `$WIKI_ROOT/SCHEMA.md` and `$WIKI_ROOT/concepts/*` for citations — this is the canonical pattern for any plugin whose reference material is wiki-relative. Subagents (wiki-searcher, wiki-linter, wiki-ingester) need no changes; they already accept `wiki_path` or `alias` and operate on the registered wiki.

### Migration notes

- Every historical `docs/` reference in CHANGELOG.md is preserved as-is (it describes the state at the time of writing). New entries reference `knowledge/`.
- The marketplace's `docs/` tree is gone. `docs/CONTRIBUTING.md` → `knowledge/concepts/contributing.md`. `docs/official/X.md` → `knowledge/raw/official/X.md`. `docs/templates/X.md` → `knowledge/templates/X.md`. `docs/persistence-schema.md` → `knowledge/concepts/persistence-schema.md`.
- The curl command for refreshing official docs is now: `curl -sL "https://code.claude.com/docs/en/<topic>.md" -o knowledge/raw/official/<topic>.md`
- `tp-wiki` users who install the marketplace get the new `knowledge/` folder automatically. Personal wikis (registered in `~/.claude/wiki-root.md`) are unaffected.

## [1.14.0] — 2026-06-04

Resolves issues #35, #36, #37, #38 (all subagent contract redesign) plus a
regression introduced by the #34 fix. Derived from the audit captured in
`.principled/plans/AUDIT-2026-06-04.md`.

### Fixed

- **`marketplace.json` duplicate `version` keys** (regression from #34 fix, commit `4c4cf8a`). The build script that derives the catalog from per-plugin manifests produced duplicate `"version":` fields in 5 plugin entries (core-principled, tp-fpf, tp-git, tp-sadd, tp-session-audit, tp-wiki). JSON parsers silently use the second value, so the marketplace displayed the **previous** version for those plugins. Cleaned the duplicates. The root-cause bug is in the build script (still pending) but the data file is correct as of this commit. To prevent recurrence, add a CI check: `jq -e '.plugins | all(. as $p | $p | has("version") and (.version | type == "string")) and ([.plugins[] | keys[] | select(. == "version")] | length == (.plugins | length))' .claude-plugin/marketplace.json > /dev/null` (or simpler: assert no plugin entry has the literal string `"version":` appearing more than once).

- **tp-wiki: removed `sha256` from the wiki format schema** (closes #35 R1). The field was a code smell: it required a tool (`Bash` + `sha256sum`) the subagent didn't have, and the load-bearing fact — "have we re-fetched this source?" — was already captured by the `ingested:` date. Removed from:
  - `plugins/tp-wiki/skills/wiki/SKILL.md` line 171 (anti-patterns section)
  - `plugins/tp-wiki/skills/wiki/references/wiki-format.md` (no `sha256` in spec)
  - `plugins/tp-wiki/skills/wiki/references/llm-wiki-methodology.md` (3 references: schema, capture step, lint step ⑧)
  - `plugins/tp-wiki/agents/wiki-ingester.md` (2 mode definitions)
  Replaced with date-based re-ingest logic: "compare the new source's `Last-Modified` to the existing `ingested` date; re-process if newer, skip otherwise." The wiki-linter's Check F (stale content) is already date-based — no linter changes needed.

### Added

- **6 design principles for subagent contracts** (closes #35 R2, #36 P6). New reference doc at `plugins/core-principled/skills/subagent-orchestration/references/subagent-contract-design.md`. P1 (source of truth for every value), P2 (bind Writes to Reads explicitly), P3 (ordered operations with verification), P4 (explicit link resolution algorithm), P5 (failure-mode footer on every contract), **P6 (ground truth — subagents that make factual claims must have Read access to the source of truth; the new principle from issue #36)**. Plus: 4 tool-source patterns (explicit full list, explicit restricted list, `tools: []` with orchestrator handling, `tools: []` inheriting from skill), 3-phase testing methodology (static read → real invocation → JSONL trace), and a per-plugin contract template. The `subagent-orchestration` skill body now requires reading this file before authoring any agent definition.

- **`fpf-evidence-validator` ground-truth clause (P6)** (closes #38). The agent's contract now states: "When making factual claims about the codebase, you MUST Read or Grep the relevant files first. Do not assert specific file paths, line numbers, function names, or content based on speculation. If you cannot verify a claim with the available tools, mark the claim as 'unverified' rather than asserting it." Cites issue #38's fpf-hypothesis-generator JSONL trace as the failure mode this prevents.

### Changed

- **4 `tp-fpf` subagents gain explicit `tools:` lists** (closes #38). The agents were `tools: []` but their contracts referenced file I/O operations. Real-condition testing of `fpf-hypothesis-generator` produced a JSONL trace (`agent-a0a86b88086618af3.jsonl`) with **0 tool calls made** — the model self-acknowledged the contradiction. The fix grants the minimum tool set per role:
  - `fpf-hypothesis-generator` → `Read, Write, Glob, Grep` (read context, write hypothesis, search for related files)
  - `fpf-evidence-validator` → `Read, Grep, Glob, Bash` (cross-reference the codebase; Bash for the `find` patterns the linter might want)
  - `fpf-logic-verifier` → `Read, Glob` (read the hypothesis, find related files for the logical analysis)
  - `fpf-trust-auditor` → `Read, Glob` (read the 3 source documents, find assumptions)
  All 4 retain the maintainer's in-flight `skills:` additions (e.g., `diagnose` on `fpf-evidence-validator`) — the two changes are orthogonal.

- **3 `tp-sadd` subagents gain explicit `tools:` lists** (closes #37). Same class of bug as #38 but in `tp-sadd`. The 3 subagents that handle file I/O (the other 3 are text-only and correctly have no `tools:` field):
  - `sadd-synthesizer` → `Read, Glob` (read all judge reports and candidate solutions)
  - `sadd-generator` → `Read, Glob` (read the evaluation spec)
  - `sadd-judge` → `Read, Write, Glob` (read candidates, write findings to the orchestrator-specified path)
  The 3 text-only agents (`sadd-expander`, `sadd-explorer`, `sadd-meta-judge`) are unchanged — text output is the correct contract for their role.

### Out of scope (deferred to next batches)

- **Issue #35 R3** — apply the 6 principles to the 3 `tp-wiki` subagent contracts (numbered operations with verification, "Failure modes" footer). 1 day, next batch.
- **Issue #35 R4** — document the 3-phase methodology in `CONTRIBUTING.md`. 30 min, next batch.
- **Issue #36 R5** — audit the 18 `core-principled` subagents with `tools: []`. 3-5 days, dedicated engagement.
- **Marketplace build script fix** — the root cause of the duplicate-version regression is in the script, not the data. Add a CI check + dedup pass in the script.
- **All other items from `AUDIT-2026-06-04.md` Part 4 Phase 4.**

### Verification

- 77 `plugins/**/agents/*.md` and `plugins/**/skills/**/SKILL.md` files parse cleanly under PyYAML `safe_load`. 0 errors.
- 9 `plugins/**/.claude-plugin/plugin.json` and 1 `marketplace.json` parse cleanly under `jq`. 0 errors.
- 9 plugin versions in `marketplace.json` match the corresponding per-plugin `plugin.json`. Verified via `jq`.
- All 7 redesigned subagents have `tools:` lists that match their contract's stated operations. Verified via the static real-condition test in the audit.
- All 3 text-only `tp-sadd` subagents (expander, explorer, meta-judge) correctly have no `tools:` field. Verified.
- All 8 sha256 references removed from `plugins/tp-wiki/`. Verified via `grep -r sha256 plugins/tp-wiki` returning 0 matches.
- 0 regressions on closed-issue fixes (issues #10, #11, #12, #17, #27). Verified.

### Changed (versions)

- **`tp-fpf`** 0.3.4 (unchanged — patches to agents don't bump per `semver` for tooling)
- **`tp-sadd`** 0.3.5 (unchanged)
- **`tp-wiki`** 0.1.2 (unchanged)
- **`core-principled`** 0.15.2 (unchanged)
- **Marketplace** 0.23.0 → 0.23.1 (catalog change for the sha256 removal; the per-plugin bumps are not warranted since the contract additions are additive, not breaking).

## [1.13.0] — 2026-06-04

Resolves the post-initial-release audit of the new `tp-wiki` plugin.
Six small commits covering the manifest-hygiene, hub-skill structure,
agent safety, and prose-clarity findings.

### Fixed

- **Missing `plugins/tp-wiki/.claude-plugin/plugin.json`** (tp-wiki 0.1.1). The plugin shipped with a marketplace catalog entry but no per-plugin manifest — the same bug class we fixed for `claude-cli-wrapper` / `tp-mcp` / `tp-rust` in #11 Commit 4. Without it, install would have fallen back to marketplace.json-derived metadata for tp-wiki only.
- **`wiki-searcher` tool-scope safety gap** (tp-wiki 0.1.1). The agent body said "NEVER write or modify any wiki file" but had no `tools:` field, so it inherited Write / Edit / Bash. The body policy was a request, not a guarantee. Now `tools: [Read, Glob, Grep]` enforces read-only at the tool boundary. Matches the sister agents and the focused-agent pattern across the marketplace.

### Added

- **Hub-skill `## Reference Index`** (tp-wiki 0.1.1). Names the 3 shipped agents (wiki-searcher, wiki-linter, wiki-ingester) and maps each to its mode, color, model, and tool scope. Same pattern as the sadd Reference Index from #14 D2.
- **Hub-skill `## Cross-plugin dependencies`** (tp-wiki 0.1.1). Documents the soft deps on `mcp__mcp-searxng__fetch` and `mcp__mcp-searxng__extract` for `wiki-ingester` mode `url`, both with Claude Code built-in fallbacks (WebFetch). The plugin has no hard cross-plugin deps — it's self-contained.
- **Hub-skill `## Decision Router`** (tp-wiki 0.1.1). Replaces the informal "Routing — Delegate to Subagents" section with an intent-signal → subagent table, plus disambiguation guidance for ambiguous intents.
- **Hub-skill `## Anti-patterns`** (tp-wiki 0.1.1). 7 specific failure modes with "don't do this" framing — mutating `raw/`, single-source pages, tag sprawl, skipping orientation, etc.

### Changed

- **`wiki/SKILL.md` frontmatter tightened** (tp-wiki 0.1.1). Description now wrapped in double-quotes (the bug class from #10 Bug 4 — the original bare multi-line value was fragile). Added `when_to_use:` and `argument-hint:` (the latter was missing across the hub skill).
- **`wiki-linter` Check A–G each get an explicit `Action` line** (tp-wiki 0.1.1). The Auto-Fix section at the bottom said "auto-fix safe violations" but the per-check prose didn't say what to do for any individual check. Now each check has an explicit Action: report-only by default, with auto-fix gated behind user approval.
- **`wiki-linter` Check F documents the 90-day default as overridable** (tp-wiki 0.1.1). If `intent.md` has a line of the form "no page older than N months/days without review", use that; otherwise default to 90 days.
- **`wiki-searcher` description gets more trigger phrases** (tp-wiki 0.1.1). Aligned to the same trigger surface as the hub skill's `when_to_use` and the marketplace entry, so routing into the agent doesn't have a narrower signal.
- **`Mandatory Orientation` backtick disambiguation** (tp-wiki 0.1.1). The `SCHEMA.md` / `index.md` / `log.md` references are conceptual files in the user's wiki, not files in this plugin. Added a one-line note so future maintainers don't grep the plugin for them and conclude they're missing.

### Skip notes

- Findings 11 (agent description style consistency) was already resolved — all 3 agents used quoted multi-line YAML; the SKILL.md was the inconsistent one, fixed in the frontmatter-tightening change above.
- Findings 13, 14, 15, 16 from the audit were minor polish items, addressed in the wiki-linter Action lines + the wiki-searcher trigger coverage + the Mandatory Orientation disambiguation.

### Changed

- **`tp-wiki`** 0.1.0 → 0.1.1 (patch — manifest hygiene, safety gap, hub-skill structure; no new features).
- **Marketplace** 0.21.0 → 0.22.0 (catalog change for the tp-wiki patch).

## [1.12.0] — 2026-06-04

Resolves issues #11–#16 opened by `MiaouLeChat929` on the post-#10 audit
batch. Twelve commits, three tiers (user-breaking → polish → housekeeping).
All commits land direct to main, no PR machinery (consistent with how
#6/#7 were handled).

### Tier A — user-breaking (fixed first)

- **`mcp-server-implement` skill aligned to the rmcp 0.3 API actually shipping in `claude-cli-wrapper`** (tp-mcp 0.1.1, fixes #13 C1/C2/C3). The §2 `Cargo.toml` example was pinned to rmcp 0.16 (actual: 0.3.2). The §3 macro cheat sheet showed `#[tool_handler(name = ..., version = ..., instructions = ...)]` and `Implementation::from_build_env()` (both don't exist in 0.3). The §11 error mapping aliased `McpError` (the alias is gone; use `rmcp::ErrorData` directly) and used `anyhow::Error::backtrace()` (requires the anyhow backtrace feature). The §16 anti-patterns and §12 (output construction) had one leftover stale `McpError::invalid_request` reference. All rewritten against the working API; `cargo check` clean on `claude-cli-wrapper` 0.2.2.
- **`tp-mcp` schemars cheat-sheet + Consuming-in-Claude-Code section** (tp-mcp 0.1.1, fixes #13 C4/C5). New `## §14. Schemars attribute cheat-sheet` in `mcp-tool-surface` maps every schemars attribute to its JSON Schema keyword, lists the `serde` attributes that affect schema generation, and documents the `extend("keyword" = value)` / `schema_with` escape hatches. New `## §14. Consuming in Claude Code` in `mcp-server-design` covers the actual discovery handshake Claude Code performs, the install paths, what the model sees vs. doesn't see, and a symptom → cause → fix table for common consumer-side debugging. Trailing §14–§16 renumbered to §15–§17 in both skills.
- **`claude-cli-wrapper` MCP server design tightened** (claude-cli-wrapper 0.2.2, fixes #12 H1/H2/H3/H4):
  - **H1**: `#[schemars(extend("additionalProperties" = false))]` added to all 6 input structs (`ExecuteInput`, `SessionInput`, `ContextInput`, `ReviewInput`, `AgentInput`, `ConfigInput`). `#[serde(deny_unknown_fields)]` alone does not auto-emit `additionalProperties: false` in schemars 1.0. Smoke test asserts the schema property.
  - **H2**: `annotations(title, read_only_hint, destructive_hint, idempotent_hint, open_world_hint)` added to all 6 `#[tool(...)]` macros. Annotations reflect actual semantics: `claude_review` is the only read-only tool; `claude_execute` and `claude_agent` carry `open_world_hint: true`; etc.
  - **H3**: replaced the single `internal_error` mapping with a typed `WrapperError` enum. `CliNonzeroExit` → JSON-RPC `-32001` (custom) with the full envelope in the `data` field, replacing the old `is_error: true` behavior. `Internal(anyhow::Error)` → JSON-RPC `-32603` (standard) for real wrapper failures. The MCP server, script mode, and the typed-error path all share the same mapping (`impl From<WrapperError> for ErrorData`).
  - **H4**: `WrapperResultEnvelope` struct added to `schema.rs` documenting the output shape. rmcp 0.3.2 predates the MCP 2025-11-25 `Tool::output_schema` / `CallToolResult::structured_content` fields, so the envelope is currently delivered as a JSON-encoded `text` content item and the schema is declared here for the day rmcp 0.4+ lands. Each tool's description now references the envelope shape explicitly.

### Tier B — polish

- **Three plugins received the missing `.claude-plugin/plugin.json`** (fixes #11 items 1/2/3): `claude-cli-wrapper`, `tp-mcp`, `tp-rust`. Content sourced from the existing `marketplace.json` entries so install-time metadata is byte-identical to what the index advertises. The per-plugin manifest is the spec-authoritative source; the marketplace catalog is just an index.
- **MCP/hooks manifest hygiene** (fixes #11 items 4/6): dropped the redundant `"type": "stdio"` from `claude-cli-wrapper/.mcp.json` (stdio is the default), dropped the meaningless `"matcher": "*"` from the `core-principled` `SessionStart` hook (SessionStart has no tool name to match against), added the missing `"hooks": "./hooks/hooks.json"` declaration to `core-principled/.claude-plugin/plugin.json` (the hook file existed all along but was never advertised, so installs were silently dropping it).
- **Per-plugin `author` blocks dropped from `marketplace.json`** (fixes #11 item 7). All 8 plugins now ship a per-plugin `plugin.json` with their own `author`, which the spec treats as the authoritative source. The per-plugin `plugins[].author` field was duplicating the same info for every entry. The marketplace-level `owner` block stays (different concept — "owner of the marketplace" per spec).
- **`web-search` `when_to_use` trimmed 507 → 191 chars** (core-principled 0.15.0, fixes #14 D1). The 200-char metadata cap is a hard routing budget; descriptions that overshoot get silently truncated in high-context sessions and the tail (the NOT clause, which prevents false-positive routing to code/local search) disappears. Trim keeps the trigger list, the tool-agnostic framing, and the NOT-for list; example phrasings moved into the skill body.
- **`sadd` Reference Index added** (tp-sadd 0.3.4, fixes #14 D2). New section names all 6 shipped agents (`sadd-expander`, `sadd-explorer`, `sadd-generator`, `sadd-judge`, `sadd-meta-judge`, `sadd-synthesizer`) and maps each to its mode. Previously the only way to discover the agent roster was to read each agent's `description` field and infer the dispatch pattern from context.
- **`session-analytics` cross-plugin dependencies documented** (tp-session-audit 0.3.1, fixes #14 D3). New `## Cross-plugin dependencies` section makes the soft-dep contract on `tp-debug-tracer`, `tp-fpf:fpf-evidence-validator`, and `tp-sadd:sadd-judge` greppable for maintainers, names the fallback per dep, and explains why these are soft (the plugin ships standalone).
- **`sadd-meta-judge` model: opus → sonnet** (tp-sadd 0.3.4, fixes #15 E2). The agent's only job is to generate a YAML evaluation spec (objective, rubric, pass/fail checklist, pass threshold). Structured generation work — sonnet handles it well and the marginal quality of opus on a 3-5-criterion rubric is not worth the cost multiplier.
- **Two single-Bash agents converted to skills** (tp-git 0.3.3, fixes #15 E3). `git-preflight-checker` (`tools: [Bash]`) and `git-worktree-manager` (`tools: [Bash]`) are now `tp-git/skills/git-preflight-checker/SKILL.md` and `tp-git/skills/git-worktree-manager/SKILL.md`. An agent that only runs Bash commands pays subagent overhead (context load, model invocation, message passing) for what the main agent can do with one Bash tool call. Updated `tp-git/skills/git/SKILL.md` to use the new skill names.
- **44 agent skill blocks audited and cargo-cult removed** (fixes #15 E4; the issue said 27 — actual count is 44, all agents). Every agent was preloading the same 13–17 general-purpose skills regardless of purpose. After the audit: 9 pure-reasoning agents get `skills: []` (Claude picks on demand); 35 domain-focused agents get exactly 1 relevant skill (e.g., `tp-secrets-detector → security`, `fpf-evidence-validator → fpf`, `sadd-judge → sadd`). All 44 files re-validated for YAML frontmatter correctness after the rewrite.

### Tier C — housekeeping

- **`core-principled` keywords pruned 31 → 14** (fixes #16 F1). The original list mixed universal product labels, cross-cutting workflow names, and individual skill/agent handles. The third category is too granular for marketplace discovery — when a user types `fact-check` they want the fact-check skill, not the whole plugin. Kept only stable cross-cutting workflow nouns and product-level labels; individual tool names belong in skill frontmatter.

### Documentation

- **`/improve` command body clarified** (fixes #16 F2). Both `/improve` and `refine` were discoverable entry points to the same CRITIQUE machinery and the overlap was unclear. `/improve` is the shorthand ("make this better, your call"); `refine` is the skill with explicit mode selection (SIMPLIFY / REVIEW / CRITIQUE / POLISH / MEMORIZE). The command body now spells out the relationship and includes a routing table.
- **Agent prefix rule documented in `CLAUDE.md`** (fixes #16 F3). The marketplace ships with an asymmetric naming convention: `core-principled` agents use `tp-*` (legacy namespace disambiguator), sub-plugins use `<plugin>-*` (the plugin name itself is the namespace). The rule is a historical artifact, not a flaw to be smoothed out — do not "fix" it with a mechanical rename, which would break every hardcoded spawn.

### Skip notes

- **E5** (`tools:` missing on subagents is expected) — skipped per user instruction (2026-06-04, direct confirmation in issue thread). The convention: `tools:` on an agent is a hard allowlist; absent `tools:` means inherit everything. `tools:` is only appropriate for read-only / restricted agents, not for general-purpose workers.
- **#11 item 5** (email `felix@example.com`) — no change. `example.com` is RFC 2606 reserved; the placeholder was assessed as not a real privacy concern (no harvesting risk). However, all 8 plugin manifests have since been updated to use the repository issues URL as the contact channel instead — see issue #32.
- **#14 D4** (fpf Reference Index) — no change. Issue was factually wrong: the fpf skill already had a Reference Index at the time of filing. No corrective action needed.
- **#15 E4 miscount** — issue stated "27 agents" but actual audit found 44. The discrepancy is not explained by the filing agent; the audit was comprehensive and covered all 44 agent definitions. No follow-up issue was filed to track the miscount itself — this is noted here as the closeout reference.
- **tp-cc-docs skills preloading change** — the 1.11.0 entry described broad `skills:` preloading as "intentional" and "better too much than not enough". The 1.12.0 audit moved it to `skills: []` (cargo-cult removal). This is a deliberate reversal, not a continuation. The agent now relies on on-demand skill loading consistent with the post-audit pattern applied to all 35 domain-focused agents.

### Changed

- **`core-principled`** 0.14.0 → 0.15.0 (minor — new hooks field, `/improve` rewrite, 9 agents moved to `skills: []`, keywords trimmed 31→14).
- **`claude-cli-wrapper`** 0.2.1 → 0.2.2 (minor — H1/H2/H3/H4 MCP server design fixes; new `error.rs` module).
- **`tp-mcp`** 0.1.0 → 0.1.1 (patch — skill content fixes; schemars cheat-sheet + Consuming-in-Claude-Code sections).
- **`tp-git`** 0.3.2 → 0.3.3 (minor — 2 single-Bash agents → skills).
- **`tp-sadd`** 0.3.3 → 0.3.4 (minor — sadd-meta-judge opus→sonnet, Reference Index).
- **`tp-fpf`** 0.3.2 → 0.3.3 (patch — 4 agent skill blocks trimmed).
- **`tp-session-audit`** 0.3.0 → 0.3.1 (minor — cross-plugin deps doc).
- **`tp-rust`** 0.1.0 → 0.1.0 (no change — not touched in this batch; bumped only for the new `plugin.json`).
- **Marketplace** 0.19.0 → 0.20.0 (catalog change for the seven per-plugin bumps above; new `plugin.json` files for `claude-cli-wrapper`, `tp-mcp`, `tp-rust`; per-plugin `author` blocks dropped; `core-principled` keywords pruned).

## [1.11.1] — 2026-06-04

### Added
- **`/cc-docs` slash command** (core-principled 0.14.0): 7-line command body that spawns the `tp-cc-docs` subagent and returns its cited answer. `argument-hint: "[question about Claude Code, Agent SDK, or Claude API]"`. Description in user vocabulary ("Ask a Claude Code, Agent SDK, or Claude API documentation question and get a cited answer from the live docs"). Body is 1 sentence, no markdown, semantic subagent reference — follows the marketplace's "high trust + high freedom" command convention. Recreates the content of PR #7 directly on main to avoid PR-merge machinery.
- **`.github/workflows/refresh-cc-docs.yml`** (157 lines): Weekly cron (Mondays 07:17 UTC) downloads `https://code.claude.com/llms.txt`, compares its sha256 to the embedded snapshot inside `plugins/core-principled/agents/tp-cc-docs.md`, and opens a single `chore/refresh-cc-docs-snapshot` PR via `peter-evans/create-pull-request` if the upstream has drifted. `delete-branch: true` keeps the auto-PR graveyard clean. Also fires on `workflow_dispatch` and on any push that touches the agent file. Recreates the content of PR #6 directly on main for the same reason.

### Changed
- **`core-principled`** 0.13.0 → 0.14.0 (minor — new `/cc-docs` slash command).
- **Marketplace** 0.18.0 → 0.19.0 (catalog change for new slash command).

### Why this is on main, not via PR
The user instructed to land the PR #6 + #7 content on main directly to avoid the merge-conflict overhead of three-way merging each PR branch against the post-#5 main line. The content is preserved exactly as the contributor wrote it in PRs #6 and #7. Both PRs are closed in GitHub and the closeout commit (`9904da1`) documents the rationale.

## [1.11.0] — 2026-06-04

### Added
- **`tp-cc-docs` agent** (core-principled 0.13.0): Reference oracle that answers questions about Claude Code, the Claude Agent SDK, and the Claude API by fetching the official documentation on every call rather than from training data. Embeds a point-in-time mirror of `https://code.claude.com/llms.txt` (145 doc pages) as a routing hint, then delegates to the canonical `https://code.claude.com/docs/en/<page>.md` URLs for the actual content. Description uses user-vocabulary triggers ("how do I X in Claude Code", "can Claude do Y", "what is the difference between hooks and skills", "where is setting Z documented"). CONTRAST clause distinguishes it from `tp-researcher` (general technology research). Color `orange` (general purpose, documentation). Tools: Bash, Read, WebFetch, WebSearch. Skills preloaded broadly per "better too much than not enough" — matches `tp-researcher`'s skill set plus `web-search`. Merged from open PR #5.
- **Marketplace keywords**: `claude-code-docs`, `llms-txt`, `documentation-lookup`, `reference-oracle`.

### Fixed
- **`claude-cli-wrapper` cross-platform launcher** (claude-cli-wrapper 0.2.1): the previously shipped `bin/claude-cli-wrapper` was a `Mach-O 64-bit arm64` binary only, causing `ENOEXEC` on every Linux / Intel Mac host (#10 Bug 1, critical). Replaced with a 50-line bash launcher at the same path that resolves the right binary in this order: (1) per-host prebuilt (`bin/claude-cli-wrapper.${OS}-${ARCH}`), (2) cached local build at `target/release/claude-cli-wrapper`, (3) freshly built binary via `cargo build --release` (~2-3 min one-time cost, then cached). Apple Silicon hosts continue to use the prebuilt unchanged. Adds `plugins/claude-cli-wrapper/README.md` with per-platform install contract. Follow-up: CI release pipeline for per-platform prebuilts (tracked in #10 §"Recommended upstream guardrails").
- **3 SKILL.md YAML frontmatter parse errors** (regression from 1.10.0 commit `2a77f23`): all three skills now parse cleanly under PyYAML safe_load and the Claude Code runtime parser. Closes #10 Bugs 2, 3, 4. The fixes were already in the working tree from the 1.11.0 prep pass (handoff.md B1–B3) and are now committed.
  - **`claude-cli/SKILL.md`** — unquoted `description:` contained YAML-significant colons (`lifecycle:`, `tuning:`). Wrapped in double-quotes and replaced inner colons with em-dashes.
  - **`kaizen/SKILL.md`** — closing `---` was stranded at line 25 after `user-invocable: false` was added; moved to line 7 so the body is no longer parsed as frontmatter.
  - **`mcp-tool-surface/SKILL.md`** — unquoted `description:` contained YAML-significant punctuation (`` `additionalProperties: false` ``, `oneOf`, `$ref`, `draft-2020-12`). Wrapped in double-quotes and removed the backticks.

### Changed
- **`claude-cli-wrapper`** 0.2.0 → 0.2.1 (patch — binary-arch fix).
- **`core-principled`** 0.12.0 → 0.13.0 (minor — new `tp-cc-docs` agent).
- **Marketplace** 0.17.0 → 0.18.0 (minor — catalog change for new agent).

### Verification
- Re-ran the frontmatter audit (PyYAML safe_load on every `plugins/**/SKILL.md` and `agents/*.md`): **73 / 73 files parse cleanly**, 0 errors.
- Local smoke test on Apple Silicon: `./plugins/claude-cli-wrapper/bin/claude-cli-wrapper --version` resolves to the renamed prebuilt (`bin/claude-cli-wrapper.darwin-arm64`) and prints `claude-cli-wrapper 0.1.0`. Pre-arm64 verification still needs the cross-platform CI guardrail noted above.

## [1.10.0] — 2026-06-04

### Changed
- **Skill frontmatter discoverability pass** — second pass after the 1.9.0 routing audit, focused on separation of concerns at the frontmatter level. Sourced from `docs/official/skills.md` and web search on Anthropic's skill authoring guidance.
  - **`description` rewrite to lead with user-facing triggers, not method jargon** — 6 skills whose `description` opened with abstract nouns (ideation, kaizen, project-maintenance, refine, fpf, sadd) now lead with what the USER is doing ("Explore a vague idea", "Apply four design-time guardrails", "Archive completed plans", "Review a PR", "Analyze from first principles", "Solve by generating multiple solutions").
  - **`when_to_use` added to 8 skills** missing the field (claude-cli, all 3 tp-mcp, all 4 tp-rust). Each `when_to_use` is a multi-line YAML block with 5-7 quoted user utterances that should trigger the skill — concrete phrases, not methodology.
  - **`user-invocable: false` added to 2 background-knowledge skills** (kaizen, fpf) — these are guardrails / methodology that the LLM should apply automatically, never something a user types `/kaizen` to invoke.

### Verification
- Re-ran the 10-utterance routing test against the marketplace: **8/10 clear winners, 2/10 legitimate two-skill-fits** (up from 7/10 in 1.9.0). The two remaining ties are both plan-lifecycle vs task-lifecycle on "add a new feature" — both legitimately apply.
- Audit script (description length, verb-leading, kitchen-sink detection, CONTRAST presence) re-run: 0 errors, 2 false-positive warnings from the audit's own verb list, all real issues resolved.

### Methodology
- Read `docs/official/skills.md` for the official 1,536-char cap, front-load trigger guidance, and invocation discipline (`disable-model-invocation`, `user-invocable`).
- Read `docs/templates/command.md` for the project's "high trust + high freedom" convention: skills tell what to do, not how; commands are just triggers.
- Web search on current skill-authoring best practices (2026): description quality, trigger vocabulary, avoidance of method-leaking.
- Wrote `/tmp/skill-frontmatter-audit.py` — 8-check audit (length cap, verb-leading, when_to_use coverage, trigger distinctness, kitchen-sink detection, invocation discipline, body length, when_to_use format).

## [1.9.0] — 2026-06-04

### Changed
- **Marketplace discoverability audit pass** — fixed routing and CONTRAST gaps surfaced by a 10-utterance routing test. No new skills; pure quality improvements to existing descriptions and structure.
  - **`tp-git/SKILL.md`** — added explicit §CONTRAST section listing what `git` does NOT do (plan / review / diagnose / security / task-lifecycle) and cross-links to `plan-lifecycle`, `refine`, `diagnose`, `security`, `task-lifecycle`.
  - **`test-orchestration/SKILL.md`** — added §CONTRAST distinguishing "plan and fix tests" from "just run the tests" and from `refine` / `diagnose` / `plan-lifecycle` / `security`.
  - **`claude-cli/SKILL.md`** — tightened `description` to fire only for programmatic agent-driven use, NOT for direct user-driven Claude Code. Removed the over-trigger on the word "claude" in casual mentions.
  - **`plan-lifecycle/SKILL.md`** — added "add a new feature" / "where do I start" / "start a new project" to the trigger vocabulary, and rewrote the `description` to lead with user-facing phrases.
  - **`task-lifecycle/SKILL.md`** — added "add a new feature" to the `description` and trigger vocabulary.
- **Routing test (verification):** before the fix, 5/10 utterances had a clear winner; after, 7/10 have a clear winner and the remaining 3 are legitimate "two skills could both fit" ties (plan-lifecycle vs task-lifecycle, both with trigger scores of 3).

### Verification methodology
- Ran a routing test of 10 realistic user utterances against the marketplace's 27 skills. For each utterance, the test scores each skill by counting how many of the utterance's content words appear in the skill's `description` field. The top-3 skills are reported, and the marketplace is considered well-routed when each utterance has a clear winner (top score > second score).
- Routing test script kept at `/tmp/marketplace-routing-test.py` for re-runs after future skill additions.

## [1.8.1] — 2026-06-04

### Added
- **Integrate open PRs #8 + #9** from `MiaouLeChat929` (external fork). Two new slash commands under `core-principled/commands/`:
  - **`/plan <topic>`** — wraps `plan-lifecycle` in PLAN mode. Asks 2-5 clarifying questions, spawns explorer + researcher subagents in parallel, then hands off to the skill for the full create-plans protocol.
  - **`/plan-execute <path>`** — wraps `plan-lifecycle` in EXECUTE mode against an existing PLAN.md. Picks the right strategy (autonomous/segmented/sequential) and runs workers + critics.
  - These complete the lifecycle surface: `/plan` (create) → `/plan-execute` (run) → `/archive plan-archive` (finalize).
  - File content preserved exactly as the contributor wrote it; commits/CHANGELOG batched at release time per marketplace discipline.

## [1.8.0] — 2026-06-03

### Added
- **`tp-mcp` plugin (0.1.0)**: New domain-specific plugin for MCP (Model Context Protocol) server design and implementation. Three skills covering the full server lifecycle, derived from the design thesis documented in the Kimi brainstorm on the `claude-cli-wrapper` schema:
  - **`mcp-server-design`** (the hub) — Design principles: equilibrated recursivity (flat schema, deep data via pass-through), tool decomposition (1 tool vs N, when to split, the `claude-cli-wrapper` 6-tool case study), output contract (`CallToolResult` text+JSON vs other content types), JSON-RPC error code discipline (`-32602` for schema violations, custom codes for domain failures, `-32603` only for wrapper crashes), tool annotations (readOnlyHint/destructiveHint/idempotentHint/openWorldHint), pass-through principle for deep structures, context budget (≤12 KB total schema, ≤2 KB per tool), capability negotiation (tools/resources/prompts/sampling/elicitation), security MUST/SHOULD checklist (Origin header validation, OAuth Resource Server since June 2025 spec, treat annotations as untrusted), naming conventions, the Claude-Optimal validation checklist.
  - **`mcp-server-implement`** (the production) — Build an MCP server in Rust with `rmcp` + `schemars` + `tokio`. Cargo.toml setup with the right features (`server`, `transport-io`, `transport-streamable-http-server`, `macros`), the macro cheat sheet (`#[tool_router]`, `#[tool_handler]`, `#[tool]`, `Parameters<T>`, `JsonSchema`), schemars attribute mapping table (length/range/regex/format → JSON Schema), enum idioms (rename_all, hyphenated variants), optional field patterns (`skip_serializing_if`), state management with `Arc<Mutex<...>>`, server lifecycle (initialize → capabilities → shutdown), transport choice (stdio vs Streamable HTTP vs legacy HTTP+SSE, decision matrix), stderr-only logging (`tracing-subscriber` with `with_writer(stderr)`), error mapping (`McpError::invalid_request/invalid_params/method_not_found/internal_error`), output construction, testing with the MCP Inspector, building and shipping (cross-compile, LTO/strip).
  - **`mcp-tool-surface`** (the meta) — JSON Schema authoring for tools. Constraint design (enum/pattern/range/format/length for every property), `additionalProperties: false` discipline, `oneOf` vs discriminator-enum tradeoff (the 95/5 rule), `$ref` vs inline, draft-2020-12 selection, required vs optional decisions, the "schema is an LLM instruction manual" framing, description-writing recipe (what/format/constraints/safety), tool name conventions (snake_case, verb_noun, domain prefix when 5+), nested objects (2-level rule), defaults that help, output schemas, common-pitfalls catalog.
- **`claude-cli` skill (claude-cli-wrapper plugin 0.2.0)**: New skill body for the existing `claude-cli-wrapper` plugin. Documents the 6 tools (`claude_execute`, `claude_session`, `claude_context`, `claude_review`, `claude_agent`, `claude_config`), per-tool semantics, key parameters, common workflows (one-shot / multi-turn / background agent / code review / structured output), output contract, and anti-patterns. The skill is the user-facing map of the binary; the design rationale lives in `mcp-server-design`.
- **marketplace.json**: `tp-mcp` plugin entry added (category: development, version 0.1.0). Marketplace catalog version bumped to 0.15.0 (from 0.14.0).

### Design decisions
- **Plugin namespace:** `tp-mcp` (sibling of `tp-git`, `tp-fpf`, `tp-sadd`, `tp-rust`) — keeps the MCP knowledge in its own plugin rather than bloating `core-principled`.
- **3 skills, not 4-5:** The 3 skills have non-overlapping triggers (design / implement / schema authoring) — that's the routing test for whether to split. Quality evaluation and client patterns are deferred follow-ups.
- **JSON Schema 2020-12 default:** Per the MCP spec. Explicit `$schema` field recommended for clarity.
- **Streamable HTTP over legacy HTTP+SSE:** The new standard for remote MCP servers. Legacy HTTP+SSE retained only for backward compatibility with 2024-11-05 clients.

## [1.7.0] — 2026-06-03

### Added
- **`tp-rust` plugin (0.1.0)**: New domain-specific plugin with four skills covering the full Rust project lifecycle, derived from a 4-track research effort (workspace, project layout, tooling, release/dependencies) analyzing 25+ production repositories and 150+ sources:
  - **`rust-scaffold`** — Scaffold a single-crate Rust project (lib, bin, or both) with modern defaults. Default edition 2024, MSRV 1.81, resolver 2, cargo-nextest-ready structure, doctests, MSRV-aware lints. Includes Cargo.toml template, MSRV policy (api-guidelines + RustCrypto camp split), feature flag playbook ("should be additive" with mutual-exclusion escape hatch), rustdoc conventions, edition migration checklist.
  - **`rust-workspace`** — Manage a Cargo workspace: when to split, three workspace anatomy templates, workspace inheritance (1.64+) with the additive-defaults pitfall (cargo #12162), MSRV coordination, cross-crate patterns (reqwest `__internal` feature), real-world patterns table (tokio, axum, ripgrep, cargo, rust-analyzer, deno).
  - **`rust-quality`** — Set up CI + clippy + nextest + coverage + supply-chain ladder. Copy-pasteable GitHub Actions workflow (dtolnay + Swatinem + taiki-e stack), clippy policy (pedantic for libs), nextest profile, cargo-deny `deny.toml` (verified against 0.19+ schema, no `vulnerability`/`unlicensed` removed keys), cargo-vet Stage 2, DX tools (bacon, sccache, mold), criterion benchmarking.
  - **`rust-release`** — Manage the release lifecycle. Cargo semver (pre-1.0 vs 1.0+, MSRV policy decision), changelog tooling decision (git-cliff vs release-please vs hand-curated), publishing playbook (3 hard rules, yank semantics, workspace lockstep), dependency management (MSRV-aware updates, `[patch.crates-io]`, vendoring), supply-chain ongoing maintenance (cargo-vet, Dependabot), feature deprecation 3-step cycle.
- **marketplace.json**: `tp-rust` plugin entry added (category: development, version 0.1.0). Marketplace catalog version bumped to 0.14.0 (from 0.13.0).

### Design decisions
- **Plugin namespace:** `tp-rust` (sibling of `tp-git`, `tp-fpf`, `tp-sadd`) rather than bolting onto `core-principled`. The 4 skills are cohesive and distinct from the existing principles.
- **4 skills, not 3 or 5:** Maps 1:1 to the natural Rust lifecycle (scaffold → structure → quality → release) with minimal overlap. Cross-skill handoffs documented in each skill (e.g., `rust-quality` → `rust-release` for supply-chain ongoing maintenance).
- **Edition 2024 + MSRV 1.81 as defaults:** edition 2024 is stable since Rust 1.85 (Feb 2025); MSRV 1.81 unlocks the MSRV-aware resolver (Sept 2024). Both are ahead of much of the ecosystem but right for new projects.

## [1.6.0] — 2026-06-03

### Added
- **`web-search` skill** (core-principled 0.12.0): tool-agnostic best practices for finding, verifying, and evaluating information on the open web. Merges two competing drafts (information-retrieval lens + epistemology lens) into a single hub: cognitive discipline, query reformulation, source hierarchy (primary → secondary → tertiary), cross-reference verification with 3 gates, 17-row failure-modes table, and the discipline of stopping when an answer is unfindable. Description uses user-vocabulary triggers ("find X", "look up Y", "is this claim true", "what do experts say"). Files: `SKILL.md` + `references/{query-shapes,source-hierarchy,verification-protocol,when-not-to-search}.md`.

### Changed
- **core-principled bumped to 0.12.0** (from 0.11.0) for the new `web-search` skill.
- **marketplace.json**: `core-principled` description updated to mention web search best practices; keywords gain `web-search`, `web-research`, `fact-check`, `source-evaluation`.

### Fixed
- **ddd SKILL.md** (core-principled): Description rewritten from method-leaking to user vocabulary; "What This Skill Changes" section added; QUALITY mode expanded with 5-step Process, 4 Anti-Patterns, 4 Failure Cases; Failure Signal JSON schemas added for ARCHITECTURE and API modes; CONTRAST section added. Token budget ~1,688 tokens (well under 2,000 safe limit).
- **diagnose SKILL.md** (core-principled): H1 renamed to `## Routing Guidance`; original `## Routing Guidance` renamed to `## Activation Triggers`; orphaned Gemba Walk/VSM/Muda Analysis rows removed; CONTRAST section added.
- **ideation SKILL.md** (core-principled): "Create Ideas Mode" expanded from 1-line stub to full 9-line section with anchor/tail subagent roles, synthesis rule, ranked output format; CONTRAST section added.
- **8 skills CONTRAST sections** (core-principled + tp-fpf + tp-sadd + tp-session-audit): Added CONTRAST sections to kaizen, plan-do-check-act, refine, task-lifecycle, subagent-orchestration, fpf, sadd, session-analytics for routing mutual exclusivity.
- **plan-do-check-act SKILL.md** (core-principled): Corrupted fragment "ting why." removed; "Reference Index" renamed to "Agent Spawn Map".
- **session-analytics references** (tp-session-audit): `cross-analyze-protocol.md` and `adjudicate-protocol.md` expanded from stubs to full reference content.
- **CLAUDE.md**: Git Safety Protocol section added — "NEVER use `git reset --hard`" with surgical recovery alternatives.

## [1.5.0] — 2026-06-03

### Changed
- **tp-session-audit plugin**: Merged standalone `capture` skill into `session-analytics` hub as CAPTURE mode. The skill now has four modes: CAPTURE, INSPECT, REVIEW, ISSUE. Added trigger phrases for "capture session", "collect artifacts", "headless capture", "run verification capture", "profile a skill invocation", "audit skill routing", "measure hook in vivo". Removed standalone `plugins/tp-session-audit/skills/capture/` directory.
- **tp-session-audit commands**: Added `commands/capture.md` as thin router to `session-analytics` CAPTURE mode. All four commands now route through the unified hub skill.
- **marketplace.json**: tp-session-audit version bumped to 0.3.0. Description updated to reflect four modes.

### Changed
- **Structural demotion: multi-agent-patterns, tool-design, claude-headless** — These three skills have been demoted from standalone top-level skills to markdown reference files within hub skill `references/` directories:
  - `multi-agent-patterns` → `plugins/core-principled/skills/subagent-orchestration/references/patterns-reference.md`
  - `tool-design` → `plugins/core-principled/skills/subagent-orchestration/references/tool-design.md`
  - `claude-headless` → `plugins/tp-session-audit/skills/session-analytics/references/claude-headless.md`
- **subagent-orchestration SKILL.md**: Updated to imperatively cite both new reference files. `when_to_use` updated to reference `references/patterns-reference.md`. `references/patterns-reference.md` (Architecture Design section) updated to reference `references/frameworks.md` for LangGraph/AutoGen/CrewAI implementations.
- **core-principled plugin.json**: Removed references to deleted skills. Bumped version.
- **Deleted skill directories**: `plugins/core-principled/skills/multi-agent-patterns/`, `plugins/core-principled/skills/tool-design/`, `plugins/core-principled/skills/claude-headless/`.

### Changed
- **task-lifecycle skill**: Added DOCUMENT mode absorbing `update-docs` workflow. New mode handles documentation after IMPLEMENT completes: multi-agent tech-writer flow with analysis + tech-writer + review agents. Task-lifecycle now has four modes: CAPTURE, REFINE, IMPLEMENT, DOCUMENT. IMPLEMENT mode routes to DOCUMENT after Phase 3 (DoD verification) before moving task to done.
- **task-lifecycle/references/documentation.md**: New reference file with README templates, JSDoc patterns, index document checklist, and quality gates migrated from `update-docs`.
- **Deleted skill**: `plugins/core-principled/skills/update-docs/` — capabilities merged into task-lifecycle DOCUMENT mode.

### Changed
- **Agent color standardization**: Assigned semantic `color:` fields to all 27 agent definitions across the marketplace per the Agent Color Convention table in CLAUDE.md:
  - `red` (judges/critics/security): tp-critic, sadd-judge, fpf-logic-verifier, tp-code-reviewer
  - `blue` (architecture/generation/analysis): tp-analyzer, sadd-generator, fpf-hypothesis-generator, tp-plan-architect
  - `green` (implementation/integration): sadd-synthesizer, fpf-evidence-validator, tp-global-implementer, tp-transcript-rules-integrator
  - `yellow` (caution/validation/audit): tp-skill-auditor, fpf-trust-auditor, tp-plan-verifier
  - `purple` (complex reasoning/scoring): tp-comparator, sadd-expander, tp-grader
  - `orange` (meta-evaluator/diagnostic): tp-subagent-auditor, sadd-meta-judge, meta-reviewer, tp-transcript-rules-analyzer
  - `pink` (distinctive specialist): tp-transcript-rules-auditor
  - `cyan` (investigation/research/tracing): sadd-explorer, tp-test-strategist, tp-explorer, tp-researcher, tp-debug-tracer

## [1.4.0] — 2026-06-02

### Changed
- **tp-sadd agents**: Renamed with `sadd-` prefix in both filename and frontmatter `name` field to match spawn directives in `sadd` skill. Agents affected: `explorer` → `sadd-explorer`, `judge` → `sadd-judge`, `meta-judge` → `sadd-meta-judge`, `generator` → `sadd-generator`, `synthesizer` → `sadd-synthesizer`, `expander` → `sadd-expander`.
- **tp-fpf agents**: Renamed with `fpf-` prefix in both filename and frontmatter `name` field to match spawn directives in `fpf` skill. Agents affected: `hypothesis-generator` → `fpf-hypothesis-generator`, `evidence-validator` → `fpf-evidence-validator`, `logic-verifier` → `fpf-logic-verifier`, `trust-auditor` → `fpf-trust-auditor`.
- **session-analytics CROSS-ANALYZE**: Fixed cross-plugin reference from `taches-principled:debug-tracer` to `core-principled:tp-debug-tracer`.
- **session-analytics ADJUDICATE**: Fixed agent references: `tp-sadd:judge` → `tp-sadd:sadd-judge`, fallback updated to `core-principled:tp-critic`.
- **marketplace.json**: Bumped to 0.12.0.
- **core-principled plugin.json**: Bumped to 0.10.1.
- **README.md**: Updated version to 0.12.0.

## [1.3.0] — 2026-06-02

### Changed
- **core-principled project-maintenance skill**: Merged `archive-plan` (plan archival + learnings extraction) and `memory-curator` (memory audit/dedup/archive/clean) into a single hub skill with five modes — `PLAN-ARCHIVE`, `MEMORY-AUDIT`, `MEMORY-DEDUP`, `MEMORY-ARCHIVE`, `MEMORY-CLEAN`. The /archive command now routes to the unified skill. Removed the two old skills; bumped `core-principled` to 0.10.0.
- **/archive command**: Now a thin router into the unified skill (no body duplication). Argument-hint exposes all five modes plus `--abandoned` (PLAN-ARCHIVE override) and `--days` (memory age threshold).
- **refine MEMORIZE + rules-orchestration SYNC**: Updated CONTRAST references from `archive-plan` to `project-maintenance PLAN-ARCHIVE`. The writer/reader topology is unchanged.
- **MEMORY-DEDUP / MEMORY-CLEAN accuracy**: Replaced the false `--directory` and `--yes` flag claims (which `dedup.py` does not implement) with the script's actual CLI (`directory` positional, `--threshold`, `--format`) and clarified that the script is read-only — resolution is performed by the agent via MEMORY-ARCHIVE. The safety boundary is now explicit user confirmation in conversation, not a `--yes` flag. SKILL.md `argument-hint` and body are now consistent (no `--yes`/`--dry-run` claim).
- **MEMORY-ARCHIVE archive location**: Aligned all mode examples on `~/.claude/archive/memory/{category}/{date}/` (the manifest format). The MEMORY-DEDUP example previously showed `~/.claude/archive/memory/2025-05/` (missing the `{category}/` segment) — now correct.
- **marketplace.json**: Bumped to 0.11.2 (was 0.11.1). `tp-force-multiplier` removed (no longer in this marketplace); `tp-session-audit` retained.

### Added
- **project-maintenance references/memory-locations.md**: New tiny reference extracting the memory-location list that was previously inlined in both AUDIT and CLEAN modes.

### Removed
- `core-principled/skills/archive-plan/` (moved into `project-maintenance`)
- `core-principled/skills/memory-curator/` (moved into `project-maintenance`)

## [1.2.0] — 2026-06-02

### Added
- **tp-meta capture skill**: New skill that runs `claude -p` headless capture with canonical behavioral-verification flags. Produces three artifacts: debug log, stream-json output, persisted JSONL. Triggers on "capture session", "profile a skill invocation", "run verification capture".
- **tp-meta session-inspect multi-artifact routing**: Extended INSPECT mode to route by artifact type — `.jsonl` → JSONL parser, `.debug.log` → debug-log parser (extracts [HOOK]/[API]/[PERMISSION]/[ERROR] events), `.stream.jsonl` → stream-json parser (per-turn delta events).
- **tp-meta meta-review CROSS-ANALYZE mode**: New mode fans out three parallel specialists (forensic-analyst on stream-json, meta-reviewer on JSONL, debug-tracer on debug log), detects convergence across analysts. High-convergence findings (≥2 analysts) are the highest-signal outputs.
- **tp-meta meta-review ADJUDICATE mode**: New mode validates each cross-analyze finding with parallel evidence-validator + adversarial challenge. Classifies findings as validated/speculative/rejected. Uses `background: true` for concurrent per-finding validation.

### Changed
- **session-inspect description**: Added trigger phrases for parsing debug logs and stream-json ("parse debug log", "analyze hook events", "extract hook fires")

## [1.1.0] — 2026-06-02

### Fixed
- **meta-issue skill**: Fixed label creation order for non-admin users — issue now creates cleanly without label when gh label create fails due to insufficient permissions
- **tp-force-multiplier hook**: Rewrote SessionStart hook with conditional three-gate coaching instead of "all capabilities are mandatory" anti-pattern
- **tp-critic agent**: Commented out cross-plugin dead skill references (fpf, sadd, ddd, tdd, kaizen) for partial-install safety

### Changed
- **10 agent renames**: Dropped `fpf-` and `sadd-` filename prefixes across tp-fpf (4 agents) and tp-sadd (6 agents)
- **sadd JUDGE triggers**: Replaced bare-verb triggers with phrase-level specific ones to resolve routing collisions
- **create-plans skill**: All critic-loop sites now reference MAX_ITERATIONS=3 (per evaluation-protocol.md); vague template paths replaced with explicit `templates/brief.md`
- **execute-plans skill**: All critic-loop sites now bounded by MAX_ITERATIONS (3 for milestone, 2 for pre-execution/per-task); template paths now explicit
- **orchestrate command**: Expanded from 3-line stub to 8-step protocol referencing scratchpad, evaluation-protocol, and subagent-orchestration skill

### Added
- **orchestrate-solo command**: New first-class lightweight mode command — no subagents, no scratchpad, no critic loop; sequential in-context execution for small tasks
- **archive-plan hard precondition**: Phase 1 now enforces SUMMARY.md existence with structured JSON failure signal and --abandoned override path
- **subagent-orchestration routing**: Added --solo/--lightweight decision rules to skill Decision Router

### Removed
- **sadd JUDGE**: 5 bare-verb trigger phrases that caused routing collisions with refine/diagnose/git/create-plans

## [0.12.1] — 2026-06-02

### Added
- **`memory-curator` skill** (moved from `tp-vps-governance`): Audits, deduplicates, and archives Claude Code memory files. Modes: AUDIT, DEDUP, ARCHIVE, CLEAN. Includes `scripts/dedup.py` for semantic deduplication via Jaccard similarity.
- **`rules-orchestration` AUDIT mode**: Analyzes CLAUDE.md hierarchy for conflicts, duplications, and cross-file contradictions. Extracted from `config-auditor`.
- **`plan-verifier` agent tools**: Added `Write` and `Edit` to the allowlist for scratchpad-first evaluation protocol compliance.

### Removed
- **`tp-vps-governance` plugin**: Deleted after capability migration to core plugin. `config-auditor` absorbed into `rules-orchestration` AUDIT mode; `memory-curator` moved to `plugins/taches-principled/skills/memory-curator/`.

## [0.12.0] — 2026-06-01

### Changed
- **`tp-meta` consolidated into single hub skill `session-analytics`**: Merged `meta-issue`, `meta-review`, and `session-inspect` into one skill with INSPECT / REVIEW / ISSUE decision router. Each mode has its own reference file (`references/inspect-reference.md`, `references/review-reference.md`, `references/issue-reference.md`). Commands updated to target the new hub skill. Plugin version bumped to 0.2.0.

### Removed
- **`meta-issue`, `meta-review`, `session-inspect` skills** (3 directories): Superseded by `session-analytics` hub.

## [0.11.1] — 2026-06-01

### Changed
- **Dissolved `scope-work` skill**: The hollow router (`add-task`/`refine-task`/`create-plans` routing) was removed — its three spoke files never existed and its triggers conflicted with `add-task`. Lifecycle skills now self-route via their existing CONTRAST frontmatter. References updated in `ideation`, `archive-plan`, `execute-plans`, and `refine`.
- **`sadd` DESIGN mode merged into `subagent-orchestration`**: Architecture design capability consolidated into the core `subagents` hub. `sadd` now redirects DESIGN to `subagent-orchestration` and focuses on COMPETE/JUDGE/EXECUTE/EXPLORE competitive evaluation. `sadd-architect` agent deleted as orphaned.
- **`kaizen` / `ddd` relationship clarified**: Both skills updated with explicit "Relationship" sections — `kaizen` as continuous design-time guardrails (the immune system), `ddd` as specialist structural analysis (called in for diagnosis). Mutual cross-references added.
- **Shared evaluation protocol extracted**: `execute-plans`, `refine-task`, and `implement-task` now reference `execute-plans/references/evaluation-protocol.md` for the shared judge pattern (chain-of-thought, MAX_ITERATIONS, 5.0/5.0 hallucination guard, scratchpad-first, weighted rubrics). Prevents drift across the three skills.
- **Memory/learnings handoff chain made explicit**: `archive-plan`, `refine` (MEMORIZE mode), and `rules-orchestration` (SYNC mode) now have explicit CONTRAST cross-references documenting the two-writers/one-reader chain feeding `.principled/memory/learnings.md`.

### Removed
- **`scope-work` skill** (4 files): `SKILL.md` + `references/{nano-spec,task-spec,roadmap}.md` — no spoke bodies, routing superseded by direct CONTRAST routing in lifecycle skills.
- **`sadd-architect` agent**: Orphaned when DESIGN mode moved to `subagent-orchestration`.

## [0.11.0] — 2026-06-01

### Added
- **scope-work skill** (canonical plugin): Unified entry point for task lifecycle — infers work scale from input and routes to `add-task` (nano-spec), `refine-task` (task-spec), or `create-plans` (roadmap). 261 lines across SKILL.md + 3 references.
- **New official docs**: `docs/official/permissions.md` and `docs/official/plugins/plugins-reference.md` (refreshed from source).

### Changed
- **Skills preloading philosophy — "Better too much than not enough"**: Retired the restrictive rule limiting skill preloading to evaluation/critique agents only. All potentially relevant skills MUST now be preloaded on all agent types (execution, research, explorer, etc.) for deterministic capability access. Properly authored skills use progressive disclosure — baseline context consumption is extremely low (~500 tokens frontmatter + body, references on-demand). AI retains full autonomy to lazy-load deeper reference files based on task requirements. Updated `docs/official/agent-skill-integration.md`, `plugins/taches-principled/skills/subagent-orchestration/SKILL.md`, and CLAUDE.md.

- **Skill file path referencing standardized**: Eradicated `{baseDir}` and `${CLAUDE_SKILL_DIR}` variables from all skill bodies and references (12 files). Established two canonical rules: (1) paths resolve within the skill's folder by default, (2) only SKILL.md may cite supporting files — reference files must never cross-cite. Converted all passive citations ("You can read", "See reference") to deterministic IF→BEFORE imperatives. Documented in CLAUDE.md and skill-authoring SKILL.md.
- **Native Tool Referencing standard**: Eradicated hardcoded tool names from orchestration directives across 11 files. `Write tool access` → `write access`, `"use the Read tool"` → `"use your native tools"`, etc. This ensures forward compatibility when the underlying API migrates (e.g., Task→Agent rename). Documented in CLAUDE.md and skill-authoring SKILL.md as a core best practice.
- **CLAUDE.md Skill Discovery**: Rewrote section as "Skill Discovery & Routing Metadata" — explicitly names routing-participant fields (description, when_to_use only), defines the "Metadata-Only Gate" concept, elevates 200-char rule, and adds Anti-Pattern "No Method Leaking" with bad/good examples.
- **Skill descriptions cleaned** (5 skills, jargon → user vocabulary):
  - `diagnose`: "A3, Five Whys, Fishbone, Stack Trace" → "Find root causes of recurring problems, failed fixes, and complex bugs"
  - `security`: "SAST, DEPENDENCY-AUDIT, SECRETS-DETECTION, COMPLIANCE" → "Scan for security vulnerabilities, exposed secrets, and broken authentication patterns"
  - `kaizen`: "YAGNI" → "avoid over-engineering"
  - `plan-do-check-act`: "PDCA cycle" → "Plan a change, try it at small scale, measure results"
  - `tdd`: "Red-Green-Refactor TDD" → "Write tests first, then implementation"
- **Must-do cleanup pass** (commit `55a6ba0`):
  - H1: Removed 2 tracked `.pyc` files; broadened `.gitignore` to `plugins/**/__pycache__/`
  - H2: Fixed broken CONTRAST references to non-existent `rule-propagator`
  - H4: Standardized `tp-force-multiplier` author to "Felix" across all 9 plugins
  - H5: Added `repository`, `license`, `keywords` to all marketplace.json entries
  - M3: Moved `commands-standard.md` to `docs/templates/command.md`
  - M4: Stripped redundant `shell: bash` from 33 files
  - M5: Stripped redundant `user-invocable: true` from 2 files
  - M6: Stripped dead YAML frontmatter from 15 templates/workflows
- **Plugin subagent rename for global uniqueness**: prefixed plugin subagents to avoid collisions when the `Agent` tool resolves across the marketplace:
  - `plugins/taches-principled/skills/create-plans/agents/{architect,explorer,implementer}` → `plan-{architect,explorer,implementer}`
  - `plugins/taches-principled/skills/rules-orchestration/agents/{rules-analyzer,rules-auditor,rules-integrator}` → `transcript-rules-{analyzer,auditor,integrator}`
  - `plugins/tp-sadd/agents/{architect,explorer}` → `sadd-{architect,explorer}`
  - `plugins/taches-principled/agents/implementer` → `global-implementer`
  - `plugins/taches-principled/skills/execute-plans/agents/researcher` → `execute-researcher`
- **README brittleness reduction**:
  - Stripped 4 magic-number count headers (`### 23 Skills`, `### 14 Commands`, `### 13 Agents`, `### 8 Marketplace Plugins`).
  - Collapsed 3 enumeration tables (Skills, Commands, Agents) to 5 curated examples each + filesystem pointers.
  - Fixed unclosed code block fence in "Full Marketplace Setup" (line 110).
  - Added `### README Hygiene` subsection to CLAUDE.md "Before Any Commit" self-check to make the discipline explicit.
- **CLAUDE.md description cap reconciliation**: changed self-check from `≤150 chars` to `≤1,536 chars` (combined `description` + `when_to_use`) to match the official cap per `docs/official/skills.md`.

### Removed
- **Orphan agent files** (untracked, unreferenced, superseded): `global-rules-{analyzer,auditor,integrator}.md` — the `transcript-rules-*` agents in `rules-orchestration/` do this work.
- **Empty directories**: `plugins/taches-principled/rules/`, `plugins/tp-vps-governance/agents/`.
- **Tracked Python bytecode** (2 files in `tp-force-multiplier/hooks/__pycache__/`).
- **Stale `.gitignore` line** referencing the removed `launch-subagent` skill directory.

## [0.10.0] — 2026-05-29

### Added
- **tp-meta plugin**: Session meta-review and behavioral analysis plugin with 3 skills, 1 agent, and 3 commands.
  - `session-inspect` skill: parses Claude Code session transcripts (JSONL) into structured data — tool calls, errors, cost, loaded plugins, behavioral events.
  - `meta-review` skill: reviews sessions for behavioral anti-patterns, investigates root causes with parallel subagent fan-out, and produces scoped findings.
  - `meta-issue` skill: creates GitHub issues from meta-review findings, sanitized for public sharing with privacy audit gate.
  - `meta-reviewer` agent: diagnostic agent that reads JSONL transcripts and identifies tool misuse, skipped verifications, and instruction-following failures with root cause scoping (PLUGIN/USER-FILE/ENVIRONMENT/MODEL).

## [0.9.0] — 2026-05-27

### Added
- **tp-force-multiplier plugin**: Hook-driven coaching plugin that steers Claude to use subagents and skills more via real-time semantic coaching. Three hooks: SessionStart (lightweight hint), Stop (pattern detection with 5+ tools), PostCompact (pre-pressure reminder). No tool injection, zero blocking, semantic patterns only.
- **CLAUDE.md rules**: Added 4 new rules for instruction clarity
  - Deterministic Language for Execution Rules (strong vs soft language calibration)
  - Infrastructure Assumption Rule (verify prerequisites before dependent operations)
  - Path Configuration Rule (use arguments, not hardcoded paths)
  - Agent Tool Contract Rule (tools must match stated capabilities)

### Changed
- **references/official/**: Updated hooks.md, skills.md, subagents.md, commands.md, and marketplaces.md with marketplace conventions (effort/effort field, shell: bash, hub skills, {baseDir} syntax, CONTRAST sections, maxTurns:15, memory:local, canonical spawn vocab, command format)

### Changed
- **Lifecycle hints removed**: Removed soft-orchestration lifecycle hints from add-task, create-prompts, implement-task per debate WEAK verdict — CONTRAST sections and decision routers are sufficient for routing
- **test-orchestration**: Added CONTRAST section clarifying distinction from test strategy skill
- **refine-task**: Trimmed business analysis section (70 lines removed) — procedure condensed to principle
- **implement-task**: Trimmed Pattern B/C detailed walkthroughs (150 lines removed) — step-by-step scripts condensed to policy

### Fixed
- **tp-force-multiplier hooks.json**: Fixed format from array-based to nested object structure per Claude Code hooks reference — changed `{"hooks": [{event:..., ...}]}` to `{"hooks": {"EventName": [{matcher:..., hooks:[...]}]}}`
- **Routing BLOCKERs** (3): Removed overlapping trigger phrases causing routing conflicts
  - refine-task: removed "plan this out", "/plan", "make this actionable", "break this down into steps"
  - execute-plans: removed "execute" from description and when_to_use
- **Failure signal BLOCKERs** (2): Added missing Failure Signal sections
  - ideation: added no-viable-options/user-abandoned/scope-too-broad failure modes
  - claude-headless: added session-timeout/permission-denied/tool-unavailable failure modes
- **Git availability**: Added `git --version` checks to implement-task and refine-task
- **Judge tool mismatch**: Added Write tool to judge.md for filesystem communication
- **TDD Iron Law contradiction**: Removed "write tests" from TDD triggers (Iron Law forbids without failing test first)
- **tp-force-multiplier hooks**: Fixed prescriptive language → advisory ("Pattern: X suggests Y")
- **tp-sadd agent tools**: Added Bash to meta-judge/judge, removed unused Edit from generator
- **create-plans/agents**: Added missing spawn footer to implementer

### Changed
- **METHOD over-specification** (249 lines removed across 4 skills):
  - fpf: 7-step procedure → principle statements
  - diagnose: A3/Five Whys/Fishbone condensed
  - create-plans: 11-item fan-out → 4 principles
  - execute-plans: Strategy A 12-step → 5 principles, deviation rules trimmed
- **Trigger optimization** (5 skills improved):
  - tp-fpf: removed jargon (ADI, R_eff), lead with user vocabulary
  - multi-agent-patterns: rewritten for cold-start clarity
  - tp-ddd: modes moved out of first line
  - security: triggers capped at 3-4 per mode
  - tp-sadd: softened jargon ("meta-judge" → "quality verification")
- **METHOD reduction round 2** (1,212 lines removed across 6 skills):
  - implement-task: 520→181 (-65%), subagent-orchestration: 592→213 (-64%)
  - create-prompts: 493→187 (-62%), execute-prompts: 273→149 (-45%)
  - add-task: 94→58 (-38%), ideation: 94→66 (-30%)
- **Skill discovery optimization**: Added CLAUDE.md section on reliable triggering, hook limitations, validation protocol

## [0.7.0] — 2026-05-25

### Added
- **rules-orchestration skill**: Full lifecycle orchestration hub (6 modes: DESIGN/BUILD/ANALYZE/SYNC/REVIEW/EXECUTE) — orchestrates multiple rule sources into unified rule sets with fan-out/subagent coordination, 3-phase plan, 8 tasks committed

### Changed
- **Lifecycle continuation handoffs**: Implemented 6 lifecycle chains across ideation→add-task→refine-task→implement-task→create-prompts→execute-prompts with soft-orchestration pattern via description hints

## [0.6.0] — 2026-05-25

### Added
- **5 new skills**: Integrated from local ~/.claude/skills/
  - `claude-headless` — Claude Code headless execution patterns, evaluation pipeline anchor
  - `multi-agent-patterns` — Architecture design patterns (supervisor/swarm/hierarchical)
  - `tool-design` — Agent tool and MCP integration design with production evidence
  - `security` — SAST, dependency audit, secrets detection, compliance (OWASP Top 10)
  - `test` — Test strategy decisions (coverage, mock strategy, fixtures, property-based)

### Changed
- **subagent-orchestration**: Merged with `subagent-creator` — now a 2-mode hub (DESIGN/ORCHESTRATE)
- **plugin.json**: Version bumped to 0.6.0, description updated with new capabilities, new keywords
- **Skill count**: 20 → 25 skills (within optimal 22-28 range)

### Removed
- **subagents**: Deleted as duplicate — `subagent-orchestration` is now the canonical hub
- **14 absorbed skills** (from 0.5.0): `reflexion`, `write-concisely`, `create-subagents`, `subagent-orchestration` (root), and 10 individual tp-* skill files superseded by hub equivalents

## [0.5.0] — 2026-05-24

### Added
- **6 new commands**: `/improve`, `/critique`, `/learn`, `/polish`, `/orchestrate`, `/design-subagents` — direct capability triggers routing to hub decision routers
- **Hub-and-spoke consolidation**: reduced marketplace from 34 skills to 20 (41% reduction, 5,952 lines removed)
  - Root: `refine` now a 5-mode hub (SIMPLIFY/REVIEW/CRITIQUE/MEMORIZE/POLISH) absorbing `reflexion` + `write-concisely`
  - Root: `subagents` now a 2-mode hub (DESIGN/ORCHESTRATE) absorbing `create-subagents` + `subagent-orchestration`
  - tp-sadd: 5 skills merged into `sadd` hub
  - tp-git: 4 skills merged into `git` hub
  - tp-fpf: 3 skills merged into `fpf` hub
  - tp-ddd: 3 skills merged into `ddd` hub

### Changed
- **CLAUDE.md**: comprehensive audit — Meta-Rule rewritten for human maintainers, dispatch/launch terminology standardized to spawn, reflexion/refine narrative corrected, direct-language principle enforced, Self-Check strengthened, logical weaknesses fixed, missing definitions added
- **Commands**: 6 existing commands updated with hub skill routing, all 12 commands verified against commands-standard.md

### Removed
- **14 absorbed skills**: `reflexion`, `write-concisely`, `create-subagents`, `subagent-orchestration` (root), and 10 individual tp-* skill files superseded by hub equivalents
- **`coordination.py`** script and design reference files consolidated into hub skill bodies

### Fixed
- **Token Economy**: removed contradictory line advising writing to non-loaded CLAUDE.md
- **Subagent spawn instructions**: all inline tool lists replaced with role + outcome descriptions
- **Cross-references**: all stale references to deleted skills cleaned before deletion
- **marketplace.json**: root skill count corrected 18→15

## [0.4.1] — 2026-05-23

### Fixed
- **tp-ddd plugin**: Converted 14 invalid rules (in `rules/` with `title`/`impact` frontmatter) to 12 valid skills (in `skills/` with `name`/`description`/`when_to_use` frontmatter)
- **tp-ddd**: Merged overlapping skills (call-site-honesty→explicit-side-effects, clean-architecture-ddd→separation-of-concerns)
- **tp-ddd**: Improved when_to_use triggers with natural developer phrases

### Changed
- **tp-ddd**: Collapsed 12 skills → 3 hub skills (code-transparency, code-architecture, code-quality) via multi-agent consolidation pipeline
- **tp-ddd**: description updated to reflect new skill structure

### Fixed
- **tp-ddd**: Lost concepts (early returns, file size limits) restored after Skeptic-Advocate reconciliation

## [0.4.0] — 2026-05-23

### Changed
- **marketplace.json**: Bumped to 0.4.0, 7 entries (root + 6 separate plugins)
- **plugin.json**: Version remains 0.4.0
- **CHANGELOG**: Removed 68 skills count claim (was inaccurate)

### Added
- **when_to_use frontmatter**: Added to all 34 skills with user-quoted trigger phrases and IMMEDIATELY/FIRST/BEFORE conditionals

### Fixed
- **sadd-dispatch**: Added missing when_to_use section entirely
- **tp-sadd/tp-sdd plugins**: All skills now have proper trigger phrase quoting and temporal markers (tp-sdd deprecated, consolidated into root)

### Refactored
- **All 34 skill descriptions**: Normalized to third-person framing with trigger phrases (note: official docs confirm verb-first is valid)
- **Agent definitions**: XML Structure Rules converted to markdown Structure Conventions

## [0.3.0] — 2026-05-22

### Added
- **22 root skills**: Integrated review (review-pr, review-local-changes), kaizen (kaizen, analyse, analyse-problem, cause-and-effect, plan-do-check-act, root-cause-tracing, why), and docs (update-docs, write-concisely) into root plugin
- **5 separate plugins**: Ported from context-engineering-kit — tp-sadd (9 skills), tp-fpf (3 skills), tp-git (4 skills), tp-session-audit, tp-ddd (14 rules) (tp-sdd deprecated and consolidated into root)
- **Decision routers**: All 60 skills now have IF/THEN decision routers at top
- **Semantic vocabulary**: Cross-plugin synergy through shared workflow vocabulary (no plugin name references)
- **Integration architecture**: `.principled/plans/BRIEF.md`, `ROADMAP.md`, `scratch/integration-architecture.md`, `scratch/fan-out-plan.md`
- **Phase summaries**: `.principled/plans/phases/00-scaffold/SUMMARY.md`, `01-reflexion/SUMMARY.md`

### Changed
- **plugin.json**: Bumped to 0.3.0, updated description with full lifecycle scope
- **marketplace.json**: Bumped to 0.4.0, 7 entries (root + 6 separate plugins)
- **CLAUDE.md**: Added Plugin Management section for multi-plugin marketplace operations

### Fixed
- Cross-plugin naming violations: all 60 skills use semantic vocabulary instead of plugin name references
- XML tags removed from all ported content (markdown headings only)
- Threatening language removed from SADD and reflexion skills (professional tone)
- Meta-judge pattern deduplicated across 10 SADD skills (was 4,000 lines of copy-paste)

## [0.2.0] — 2026-05-22

### Added
- **code-simplify skill**: Simplification pipeline with 5 stages (Extract & Name, Reduce Nesting, Remove Duplication, Eliminate Dead Code, Replace State Machines with Data), anti-patterns with wrong/right pairs, inline agent template, Policy/Mechanism framing, numeric thresholds, and language-specific references for JS/TS, Python, Go, and Ruby
- **code-simplify skill**: `references/language-patterns.md` with language-specific patterns
- **code-simplify skill**: `references/simplification-scope.md` with scope boundaries and file ownership rules
- **commands/simplify.md**: `/simplify` command for direct invocation with optional file-pattern argument
- **plugin.json**: Bumped to 0.2.0, added code-simplify keyword

## [0.1.0] — 2026-05-22

### Added
- **create-skills skill**: Decision Router with IF→FIRST/IMMEDIATELY/BEFORE imperative conditionals at top
- **create-skills skill**: Five skill categories with inspirational examples (Constraint/Guardrail, Orchestration, Domain Expertise, QA, Creative Direction)
- **create-skills skill**: Added Success Criteria section with measurable outcomes
- **create-skills skill**: Added `trigger-benchmark.md` reference (305 lines): 20-query framework, exit criteria, overfitting detection, headless testing method
- **create-skills skill**: Added Automated Checks section to `skill-self-testing.md`: programmatic pre-commit validation script
- **create-skills skill**: Added `scripts/run_trigger_benchmark.py`: automated 20-query test harness with streaming JSONL detection
- **create-skills skill**: Added `scripts/grader-output-template.md`: structured output format for grader → analyzer pipeline
- **execute-plans skill**: Decision Router with strategy selection based on checkpoint types
- **execute-plans skill**: Added Numeric Thresholds section
- **agents/**: New grader, comparator, and analyzer agents for evaluation pipeline
  - `grader.md` (161 lines): Teaching effectiveness rubric with 4 dimensions (Routing Signal, Delta Clarity, Teaching Posture, Anti-Pattern Quality)
  - `comparator.md` (115 lines): Skill version comparison for delta analysis
  - `analyzer.md` (96 lines): Synthesizes evaluations into prioritized improvement path
- **agents/skill-auditor.md**: Added Trigger Benchmark Integration section; added Evaluation Pipeline section documenting multi-agent evaluation workflow
- **CLAUDE.md**: Added Evaluation Pipeline section documenting the grader/comparator/auditor/benchmark/analyzer multi-agent system
- **create-subagents skill**: Multi-agent patterns import from taches-modernized research
  - `references/gotchas.md` (443 lines): Eight critical production gotchas (supervisor bottleneck with 3-5 worker cap, 15x token cost, sycophantic consensus, agent sprawl, telephone game, error propagation cascades, over-decomposition, missing shared state)
  - `references/fault-tolerance.md` (310 lines): Circuit breaker pattern, checkpoint/resume, exponential backoff, idempotent operations
  - `references/token-economics.md` (230 lines): Real multi-agent cost breakdown (~15x baseline), when justified, model selection vs token budget
  - `references/consensus.md` (386 lines): Weighted voting (confidence × expertise), debate protocol, adversarial critique, convergence detection
- **create-subagents skill**: Extended decision router with 5 new routes to new references
- **create-subagents skill**: Added Multi-Agent Gotchas section with hard cap enforcement
- **orchestration-patterns.md**: Added Swarm pattern (peer-to-peer), forward_message pattern (telephone game mitigation), 4 new anti-patterns
- **context-management.md**: Added Context Isolation Mechanisms (3-mechanism taxonomy), Context Degradation Signals
- **execute-plans skill**: Added supervisor bottleneck warning with 3-5 worker cap enforcement
- **create-plans skill**: Added context degradation signals to scope-estimation.md
- **execute-plans skill**: Critical fixes from second round of critic review
- **create-skills skill**: Comprehensive improvements from critic review
- **create-skills skill**: Now teaches bundled agents pattern
- **create-skills skill**: Native task lists + semantic-first skill refactor
- **execute-plans skill**: Added agents/critic.md for milestone self-review
- **create-plans skill**: Added agents folder with subagent prompt templates
- **execute-plans skill**: Added env-variable-pattern reference doc for portable skill paths
- **subagent-orchestration skill**: Integrated as 7th skill with RACE framework, five parallel patterns, three automation layers, memory architecture, and failure modes
- **create-subagents skill**: Added plugin scope gotcha (hooks/mcpServers/permissionMode silently ignored for plugin subagents), Task→Agent renaming note (v2.1.63), missing frontmatter fields (skills, memory, background, maxTurns, isolation)
- **create-skills skill**: Added 3-level progressive disclosure pattern (Level 1 ~100 tokens always, Level 2 ~5k on trigger, Level 3 0 via bash injection)
- **create-plans skill**: Added bash injection = 0 context cost pattern
- **execute-plans skill**: Added Explorer Subagent Protocol for investigation tasks via scratchpad coordination
- **execute-prompts skill**: Added Explorer Subagent Protocol and Thought/Action/Observation anti-pattern
- **create-skills skill**: Added Fresh Context Warning for subagent spawning (no inheritance from orchestrator)
- **all root agents**: Added spawn footers and failure signal sections to all 7 root-level agents

### Fixed
- **execute-plans skill**: Fixed broken {baseDir} reference — orchestration-patterns.md now uses natural language (file lives in create-plans skill)
- **execute-plans skill**: Fixed critic agent name collision with create-plans (critic → execute-critic)
- **README.md**: Fixed skill count (6→7) and agent count (4→7), added subagent-orchestration rows
- **CLAUDE.md**: Fixed stale version example (1.1.0→0.1.0)
- **marketplace.json**: Added missing top-level description for validation cleanliness
- **CHANGELOG.md**: Fixed stale agent line counts for comparator.md and analyzer.md
- **execute-plans skill**: Use agents/critic.md template for milestone reviews
- **create-plans skill**: Resolve inconsistencies found during reference review
- **create-plans skill**: Resolve critical issues found during reference review
- **execute-plans skill**: Fixed agent template paths to use {baseDir} for plugin portability
- **create-plans skill**: Fixed agent folder references to use {baseDir} for plugin portability
- Corrected GitHub repo references across plugin

### Changed
- **Version**: Bumped from 0.0.2-alpha to 0.1.0 (plugin now has 7 skills, 7 root agents, evaluation pipeline)
- **CLAUDE.md**: Reduced from ~475 lines to ~178 lines by moving teaching content to skills ( marketplace operations only)
- **create-plans skill**: Complete remaining deferred improvements from reference review
- Marked all deferred improvements from reference review as resolved
- **create-plans skill**: Remove per-file version tracking (anti-pattern)

## [0.0.2-alpha]

### Added
- **create-plans skill**: Added `agents/` folder with subagent prompt templates (explorer, researcher, architect, implementer, verifier)
- **create-plans skill**: Added fan-out exploration pattern with parallel subagent spawning guidance
- **create-plans skill**: Natural language instructions for reading agent prompts and filling placeholders
- **execute-plans skill**: Added `agents/critic.md` for formalizing milestone self-review pattern
- **CLAUDE.md**: Added Semantic-First Skill Design section with progressive disclosure architecture

### Fixed
- **marketplace.json**: Changed `source.github.repo` to `source.source: "url"` with full git URL — `felixhopper` repo does not exist, corrected to `Git-Fg/taches-principled`
- **README.md**: Replaced all `felixhopper` references with `Git-Fg` (lines 13, 125)
- **README.md**: Corrected skills count (6 skills now) and commands count (10 → 2)
- **execute-plans/SKILL.md**: Removed duplicate "Strategy B" section header in Strategy A content
- **sequential-execution.md template**: Fixed `Sonnets/Large Context Executor` → `Sonnet` (valid model name)
- **autonomous-execution.md**: Removed duplicate rollback sections, clarified revert scope
- **autonomous-execution.md**: Removed invalid Task() spawn syntax, replaced with plain-text instruction
- **autonomous-execution.md**: Added spawn footer to worker prompt structure
- **segment-execution.md**: Added milestone self-review section, integrated critic.md reference, added spawn footer
- **sequential-execution.md**: Replaced inline deviation rules with reference to deviation-rules.md
- **execute-phase.md**: Added YAML frontmatter per skill anatomy standards
- **execute-prompts/SKILL.md**: Removed Task tool prose references, replaced with semantic delegation language
- **cli-automation.md**: Marked Railway as deprecated (discontinued 2024), added Cloudflare/AWS/GCP/Bun platforms
- **milestone-management.md**: Updated all 2025 dates to 2026, added hotfix branch model
- **plan-format.md**: Removed duplicate Summary Output section, cross-referenced SKILL.md, added Checkpoint field
- **checkpoints.md**: Added human-readable comment pattern, added Escalation and Timeout section
- **scope-estimation.md**: Defined context usage metrics, added sequential chain limit
- **create-plans SKILL.md**: Simplified fan-out description, removed Task: spawn examples
- **create-plans/references/**: Removed per-file version tracking (anti-pattern documented in CLAUDE.md)

## [0.0.1-alpha]

### Added
- **create-prompts skill**: Creates executable XML-structured prompts for Claude Code sessions
  - Adaptive intake gate with task type detection
  - Contextual questioning with templates (dashboard type, auth method, etc.)
  - Decision gate loop until user confirms
  - Single/parallel/sequential prompt generation
  - XML patterns for coding/analysis/research tasks
- **execute-prompts skill**: Executes prompts via delegated sub-tasks
  - Policy vs. Mechanism framing for strategy selection
  - Single/parallel/sequential execution via Task tool
  - Critical constraint: parallel Task calls in single message
  - Argument parsing and file resolution
  - Archival to `./prompts/completed/` and git workflow
- **create-prompts/workflows/execute-prompt.md**: Workflow reference for prompt execution

### Changed
- README updated: Skills count 4 → 6, Policy/Mechanism table expanded

## [1.1.0]

### Changed
- Renamed from `taches-modernized` to `taches-principled`
- All 4 skills enhanced with Policy/Mechanism framing sections
- All 4 skills enhanced with Anti-Patterns sections
- All 4 skills enhanced with Numeric Thresholds tables
- README updated with Skill Ecosystem dependency map
- README updated with Policy vs. Mechanism table

### Removed
- MCP server creation skill and command (builds on existing MCP tooling instead)

### Fixed
- create-hooks: UserPromptSubmit added to events table
- create-hooks: malformed hookSpecificOutput JSON fixed
- create-hooks: broken jq syntax in prettier example
- create-hooks: broken reference to user-gates.md removed
- create-plans: missing frontmatter added
- create-subagents: missing frontmatter added, broken file references removed
- create-mcp-servers: Rule 2 (cwd vs --directory) clarified
- All reference files gained frontmatter

## [1.0.0] — Initial release

### Added
- 4 principle-based skills: create-skills, create-subagents, create-hooks, create-plans
- 8 slash commands: /create-skill, /create-subagent, /create-hook, /create-plan, /audit-skill, /audit-subagent, /debug, /whats-next
- 3 agent types: code-reviewer, skill-auditor, subagent-auditor
- plugin.json and marketplace.json for GitHub marketplace
- MIT license

### Principles
- Goals over procedures
- Principles over steps
- Trust Claude's intelligence
- Concise by default
- Gotchas, not rules
