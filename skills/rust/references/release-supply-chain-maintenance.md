# Supply-Chain Maintenance and Feature Deprecation for Rust

Reference for ongoing supply-chain maintenance (cargo-vet, Dependabot, RUSTSEC monitoring, dep bump-vs-replace decisions) and the feature deprecation playbook. Read it before changing a dep policy or deprecating a feature.

## §1. cargo-vet maintenance (ongoing)

```bash
# When a new dep is added:
cargo vet            # fails on unaudited deps
cargo vet certify --accept-all -p new-dep    # after human review
# OR
cargo vet suggest --all    # adds it to exemptions (trust-based, no review)
```

## §2. Dependabot setup

`.github/dependabot.yml`:
```yaml
version: 2
updates:
  - package-ecosystem: "cargo"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      rust-dependencies:
        patterns: ["*"]
    labels:
      - "dependencies"
```

## §3. RUSTSEC monitoring

- Subscribe to https://rustsec.org/ RSS
- Watch the rustsec/advisory-db GitHub repo
- `cargo audit` will catch it locally

## §4. When to bump a dep vs replace it

- **Bump:** dep is maintained, has a fix, fix is compatible
- **Replace:** dep is unmaintained, fix is hostile to your use case, or you want to drop the surface area
- **Live with:** dep has a known issue but no fix, and the risk is acceptable for your threat model — document the decision in your security policy

## §5. The 3-step feature deprecation cycle (post-1.0)

```
1.x.0  — add new-feature, keep old-feature working
1.x+1  — old-feature marked deprecated (warns)
1.x+2  — old-feature removed
```

Minimum 2 minor versions of deprecation window. For widely-used crates, consider 3+.

## §6. Deprecation syntax

For an entire feature flag:
```toml
# Cargo.toml — just remove the entry, but warn users first via changelog
```

For an item that's gated by a feature:
```rust
#[cfg_attr(feature = "old-feature", deprecated = "use new-feature instead")]
pub fn old_api() { ... }
```

For a feature itself (warning at compile time):
```rust
#![cfg_attr(feature = "deprecated-foo", deprecated = "use bar instead")]
```

## §7. Pre-1.0 vs post-1.0

- **Pre-1.0:** churn freely. Document in changelog. No deprecation window.
- **Post-1.0:** follow the 3-step cycle. Use `#[deprecated]` liberally. Write the deprecation in `#[doc(hidden)]` notes so it shows in rustdoc.

## §8. Unstable features (the rustc pattern)

For features that may be removed or changed:
```rust
#![feature(unstable_feature)]   // nightly only

#[unstable(feature = "my_unstable", issue = "1234")]
pub fn experimental_api() { ... }
```

Use this when you want a feature to be visible in docs but signal "this is unstable, may change". Stable features don't need this.

## §9. When to ADD a feature vs REMOVE one

- **ADD** when: 2+ users ask for it, the abstraction is real, the dep is acceptable
- **REMOVE** when: zero users for 2 minor versions, the abstraction can be done in user code
- **Never** remove during a 1.x series without a deprecation cycle

## Authoritative sources

When a cargo-vet workflow step, a Dependabot config key, an advisory status, or a deprecation/unstable attribute's syntax is in question, fetch the live canonical source. The triggers below are the *only* reasons to fetch.

| Source | Canonical for | Fetch live when |
|---|---|---|
| `https://mozilla.github.io/cargo-vet/` | cargo-vet Book (certify, suggest, exemptions, imports) | Running the vet certification workflow or auditing coverage |
| `https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file` | `dependabot.yml` schema (ecosystem, schedule, groups, labels) | Authoring or auditing the Dependabot config |
| `https://rustsec.org/` | RUSTSEC advisory database and RSS feed | Monitoring or triaging an advisory |
| `https://github.com/rustsec/advisory-db` | The advisory-db source of truth | Confirming advisory status, affected versions, or backported fixes |
| `https://doc.rust-lang.org/reference/attributes/diagnostics.html#the-deprecated-attribute` | The `#[deprecated]` attribute reference | Authoring the 3-step deprecation cycle syntax |
| `https://doc.rust-lang.org/rustdoc/the-doc-attribute.html` | rustdoc `#[doc(hidden)]` and related doc attributes | Hiding a deprecated item from docs or marking an unstable API |
