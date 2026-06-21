# REVIEW Mode — Orchestration, Synthesis, and Dedup Protocol

Single source of truth for the 5-lens parallel audit. Defines the spawn contract, the output shape every lens must return, the severity rubric, and the dedup/synthesis protocol the orchestrator applies after all lenses report.

Read it BEFORE invoking REVIEW mode or spawning any audit lens.

## §1. The 5-lens fan-out

REVIEW audits a Rust project across five independent dimensions. Spawn one a subagent generalist instance per lens, all five in parallel (same `Agent` call, no barrier). Each lens runs in its own isolated context to prevent diagnostic crosstalk.

| # | Lens prompt (passed verbatim to a subagent generalist) | Dimension | Primary reference(s) |
|---|---|---|---|
| 1 | `"audit source-code health and idioms"` | source-code | `references/review-source-code.md` (+ `references/quality-clippy-and-fmt.md`, `references/rust-idiom-polish.md`) |
| 2 | `"audit dependency hygiene"` | dependency-hygiene | `references/review-dependency-hygiene.md` (+ `references/quality-supply-chain-ladder.md` for the `deny.toml` contract only) |
| 3 | `"audit build & test health"` | build-test | `references/quality-ci-template.md`, `references/quality-testing-and-coverage.md`, `references/quality-dev-experience.md` |
| 4 | `"audit public API surface"` | public-api | `references/review-public-api.md` (+ `references/release-versioning-and-changelog.md` for semver rules) |
| 5 | `"audit supply chain"` | supply-chain | `references/quality-supply-chain-ladder.md`, `references/release-supply-chain-maintenance.md` |

Lens 5 reuses the existing `"audit supply chain"` lens string. No new specialization.

## §2. Spawn contract

When spawning each a subagent generalist instance, pass:

1. **Lens prompt** — the exact string from §1's table.
2. **Target** — the absolute path to the Rust project (or workspace root) to audit.
3. **Output Contract** — verbatim: "Return findings as a JSON array of `{ severity, location, dimension, finding, consequence, fix }` objects, sorted by severity (BLOCKER → WARN → NIT). Tag every `location` you have not physically Read or Grep'd as `(unverified)`. Do not modify any file."

The third item enforces the output shape in §3 across all five lenses regardless of lens body. The orchestrator parses each lens's JSON return into a unified finding set.

## §3. Output shape — required field schema

Every finding MUST have all six fields:

```json
{
  "severity": "BLOCKER | WARN | NIT",
  "location": "path/to/file.rs:LINE | (unverified) marker if not Read/Grep'd",
  "dimension": "source-code | dependency-hygiene | build-test | public-api | supply-chain",
  "finding": "<one-line description of what is wrong>",
  "consequence": "<one-line: what breaks or degrades if unfixed>",
  "fix": "<one-line: concrete remediation>"
}
```

`severity`, `location`, `dimension` are the sort keys. `finding`, `consequence`, `fix` are the human-readable payload.

If a finding is based on inference (lockfile parsing, manifest heuristics, codebase-wide grep) without a `Read`/`Grep`/`Bash` invocation confirming the exact local state, append ` (unverified)` to `location`. The P6 ground truth rule (§5) is non-negotiable.

## §4. Severity rubric

Every finding's `severity` MUST be assigned per the rubric below. Lenses do not invent severities; they apply this rubric.

**BLOCKER** — must fix before any merge or release:
- Code fails to compile or tests fail on the active branch (verified, not inferred).
- Active unpatched RUSTSEC advisory affecting a `Cargo.lock` entry.
- Verified or strongly-suspected unsound `unsafe` block (missing `// SAFETY:` comment, raw pointer without bounds check, FFI invariant violation).
- Post-1.0 breaking public-API change without a major version bump.
- Active unmaintained dependency with a known security advisory and no maintained successor.

**WARN** — should fix in the next sprint:
- `deny.toml` license / version / source violations.
- Wildcard or unconstrained dependency range; outdated or archived dep with a maintained successor available.
- Missing `#![warn(missing_docs)]` on a library crate; standard clippy violations across more than a handful of sites.
- Missing CI cache or `concurrency.cancel-in-progress`; nextest not adopted when test suite > 200 tests.
- Public type leaks (`pub(crate)` items in public signatures); missing seal traits on non-implementable traits.

**NIT** — polish; address in code review:
- Redundant `.clone()` on a `Copy` type; `.cloned()` where `.copied()` would do; `&String` in a function signature.
- Nested `match` that `?` would flatten; manual index loops that iterator chains would simplify.
- Unpinned toolchain (no `rust-toolchain.toml`); inconsistent identifier casing; missing helper comments.
- Single clippy violation that is borderline intentional.

When in doubt, downgrade (NIT over WARN over BLOCKER). Severity inflation desensitizes reviewers.

## §5. P6 ground truth rule

Every `location` field that names a specific `path:line` MUST be backed by a `Read`, `Grep`, `Bash`, or equivalent tool call the lens actually executed in the current session. If the lens has only inferred the location (e.g. via lockfile analysis, manifest parsing, or codebase-wide grep that did not open the file), it MUST append ` (unverified)` to the `location` value.

The orchestrator MUST NOT promote `(unverified)` findings to BLOCKER. Treat them as WARN at most until verified. If verification is impossible in the current session, drop the finding with a `dimension: "meta"` note explaining why it was dropped.

## §6. Dedup and synthesis protocol

After all five lenses return:

1. **Merge by `location`**: if two lenses flag the exact same `path:line` (with or without the `(unverified)` suffix), keep one row and concatenate `dimension` values with `+`. Keep the highest `severity`.
2. **Conceptual merge**: if the dependency-hygiene lens flags a crate as outdated AND the supply-chain lens flags the same crate as unmaintained, merge into one finding citing both dimensions.
3. **Sort**: strictly BLOCKER → WARN → NIT, then by `location` ascending.
4. **Emit final report** as markdown:

```
# Rust Project Health Audit — <project name>
<date>
<Lenses run: 5> <Coverage: BLOCKER=n, WARN=n, NIT=n>

## BLOCKER
| location | dimension | finding | consequence | fix |

## WARN
| location | dimension | finding | consequence | fix |

## NIT
| location | dimension | finding | consequence | fix |
```

Empty severity buckets are omitted. The orchestrator (main agent) presents the report; it does not modify any file.

## §7. Scope boundary

REVIEW produces a report only. It NEVER modifies files, runs `cargo fix`, applies clippy suggestions automatically, or bumps versions. The user (human or downstream skill) decides what to fix. If the user says "fix the BLOCKERs", invoke SCAFFOLD / WORKSPACE / QUALITY / RELEASE depending on the dimension of the fix; do not extend REVIEW into a fix-it mode.

## §8. Out of scope

- **Compile/run verification** — the orchestrator does not run `cargo check` / `cargo test`. Lenses may invoke `cargo` commands as part of their audit (e.g. `cargo deny check`), but the orchestrator itself does not require a build to produce a report. If the user wants a build-verified audit, say so explicitly and pair REVIEW with the QUALITY mode's CI template.
- **Architecture-level critique** ("should this be an actor model?") — use `fpf` (PROPOSE mode) for design reasoning. REVIEW audits the existing code against existing standards, not against alternative designs.
- **Performance regression analysis** without benchmarks — REVIEW can flag benchmark absence and run `cargo bench` results if present, but a true regression analysis requires a baseline commit and benchmark history that REVIEW does not own.