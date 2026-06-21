# Public API Surface and Documentation Audit Reference

Used by the `"audit public API surface"` lens (Lens 4 of REVIEW). Audits documentation coverage, public-visibility hazards (items leaking through signatures), seal-trait discipline, semver consistency, and public-type ergonomics. Distinct from the release lens's `"pre-publish review"` lens: that lens gates a *specific version bump*; this lens audits the *current state* of the API surface, regardless of release timing.

Lens 4 spawns with the contract defined in `references/review-orchestration.md` and produces findings in that schema. Semver rules come from `references/release-versioning-and-changelog.md`; this reference applies them.

## §1. Documentation coverage

1. **Module-level `//!`** — every public module should have a module-level doc comment. Missing on a top-level module (`mod foo;` without a `//!` for `foo`) is a WARN; missing on a deep public module is a NIT.
2. **`#![warn(missing_docs)]` on library crates** — should be present. Missing on any library crate (NOT a binary) is a WARN; missing on a `pub use` re-export that surfaces a non-trivial API is BLOCKER (downstream cannot discover it via `cargo doc`).
3. **Item-level docs on public items** — every `pub fn`, `pub struct`, `pub enum`, `pub trait`, `pub type`, `pub const` should have a `///` doc comment. A blanket `#[allow(missing_docs)]` at the module or crate level is BLOCKER (defeats the warning).
4. **Required sections** — public items that panic should have a `# Panics` section; items returning `Result` should have an `# Errors` section; `unsafe` items should have a `# Safety` section. Missing required section is a WARN.
5. **Doctests** — public API examples should be runnable as doctests. Non-runnable examples should be marked ` ```no_run ` (compile-checked) or ` ```text ` (not compiled). `ignore` should be reserved for genuinely un-runnable code; over-use is a WARN.

## §2. Public-visibility hazards

1. **`pub(crate)` items in public signatures** — a public function returning a `pub(crate)` type, or accepting one as a parameter, makes the type effectively public (downstream cannot name it, but they have to deal with the type's API). BLOCKER. The fix is either to make the type fully `pub` (with documentation and semver commitment) or to hide the parameter (e.g. take a `&dyn Trait` or a generic).
2. **Missing seal traits** — traits that should not be implementable by downstream (e.g. marker traits, internal extension points) MUST use the seal-trait pattern: a public trait with a `Sealed` super-trait, where the `Sealed` trait is private to the crate. Without the seal, downstream can implement the trait and break invariants. BLOCKER for marker traits, WARN for "internal but technically implementable" traits.
3. **`pub use` re-exports of internal items** — `pub use crate::internal::Foo;` re-exports an item the consumer never asked for. Each re-export is a public-API commitment. WARN for benign re-exports, BLOCKER for re-exports that expose undocumented or unstable types.
4. **Public fields on `pub struct`** — every public field is a semver commitment. For data structs, this is normal; for "internal" structs (e.g. builders with public `state` fields), it leaks invariants. WARN.
5. **`#[non_exhaustive]` on enums and structs** — adding a variant to a `pub enum` is normally a breaking change. `#[non_exhaustive]` lets you add variants in a non-breaking way. Missing on a public enum you intend to grow is a WARN; missing on a public enum that *cannot* grow (sealed set) is fine.

## §3. Semver consistency

The lens reads `references/release-versioning-and-changelog.md` for the actual semver rules. The lens applies them — it does not duplicate them.

What this lens checks:

1. **Breaking public-API changes vs declared version** — read the current `Cargo.toml` version, read the public API surface, and verify that the most recent set of changes is consistent with the version bump that accompanied them. If the version is `0.x.y` (pre-1.0), breaking changes are permitted on minor bumps (but must be in CHANGELOG). If the version is `1.x.y` or `2.x.y`, breaking changes require a major bump. A breaking change shipped on a minor/patch bump is BLOCKER.
2. **Type signature changes** — `pub fn foo(x: u32) -> String` becoming `pub fn foo(x: &str) -> String` is a breaking change. Removing a public field is a breaking change. Tightening a generic bound is a breaking change. Each is BLOCKER if not paired with a major bump (post-1.0).
3. **Trait changes** — adding a required method to a public trait (without a default impl) is BLOCKER post-1.0. Adding a provided method is fine. Removing a method is BLOCKER.
4. **Re-exports** — removing a `pub use` re-export is BLOCKER post-1.0. The lens cannot always determine this from a single commit; the release-lens does the per-bump check; this lens flags *standing* re-exports that look like dead/accidental exports.
5. **Feature-flag exposure** — a public type gated behind a feature that the type's doc-comment doesn't mention is a documentation hazard (WARN). A public type behind a feature that the CHANGELOG never announced is a BLOCKER (silently introduced API).

## §4. Public-type ergonomics (light pass)

This is a smell-test, not a full API-review. For a full design pass, use `fpf` (PROPOSE mode). This lens flags only the most common ergonomic smells:

1. **Constructor naming** — flag any `pub fn` whose name is neither `new`, `with_*`, `from_*`, nor the operation it performs (e.g. `pub fn open(...)` for opening a file is fine; `pub fn make_buffer(...)` should be `Buffer::new` or `Buffer::with_capacity`).
2. **Missing `Default`** — types with all-default-constructible state should implement `Default`. Flag types that take no constructor args but have no `Default` impl.
3. **Missing `From` impls** — a `pub struct UserId(pub u64)` with no `From<u64>` impl is a smell. Newtype wrappers should expose at least the trivial conversions.
4. **`Clone` and `Copy` discipline** — `Copy` only for ≤ 16 bytes and obvious value types. `Clone` on a type that allocates should be a deliberate decision; flag `#[derive(Clone)]` on a type that holds a non-trivial `Vec`/`String`/`Box` without a comment.
5. **Trait coherence** — flag any `impl ForeignTrait for LocalType` that does not use a newtype (this is a coherence violation cargo will reject, but the build will fail — flag as a WARN if the file is mid-edit).

## §5. The `pre-publish` lens vs the `public API surface` lens

The two lenses look similar but differ in scope:

- **public API surface (this lens, Lens 4 of REVIEW)** — audits the *current* state of the API. Used any time, on any commit, on any branch. Does not check the CHANGELOG or version bump specifically.
- **pre-publish review (RELEASE mode)** — gates a *specific version bump*. Mentally runs `cargo semver-checks` against the API delta since the last tag. Verifies CHANGELOG matches new version. Checks `Cargo.toml` version + edition + MSRV + workspace lockstep. This is the lens to use *before* `cargo publish` on a 1.x crate.

If the user says "review my public API", this lens. If the user says "review before I publish", RELEASE mode's lens.

## Authoritative sources

| Source | Canonical for | Fetch live when |
|---|---|---|
| `https://doc.rust-lang.org/rustdoc/` | The rustdoc Book — doc-comments, doctests, intra-doc links, lint attributes | Auditing doc-comment conventions, doctest setup, `#[doc = "..."]` attributes, intra-doc link resolution, `missing_docs` / `missing_doc_code_examples` / `rustdoc::broken_intra_doc_links` behavior |
| `https://rust-lang.github.io/api-guidelines/` | Rust API Guidelines Checklist (C-numbers: C-CASE, C-GOOD-ERR, C-SEND-SYNC, etc.) | Auditing public-API ergonomics, naming, trait design, interop, or the `#[must_use]` / `From` / `Default` discipline |
| `https://doc.rust-lang.org/cargo/reference/semver.html` | Cargo's SemVer rules | Classifying a public-API change as breaking vs compatible for the version bump, or checking the `#[non_exhaustive]` / `pub use` rules |
| `https://doc.rust-lang.org/edition-guide/` | The Rust Edition Guide | A finding hinges on edition-2024-specific rules (e.g. `pub use` re-export rules changed in 2018; `IntoIterator` for arrays changed in 2021; lifetime capture tightened in 2024) |