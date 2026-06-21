# Fix Tests — Repair Failing Tests After Refactoring

Fix failing tests after business logic changes, refactoring, or dependency updates. Preserve test intent — update assertions, not behavior.

## Core Principle

Fix the test, not the business logic — unless the logic itself contains a bug.

## Process

1. **Preparation** — Read project conventions, identify test command, run full suite to establish baseline, parse output for all failing files
2. **Analysis** — For each failing file, determine cause: test expectations outdated (update assertions), test setup broken (fix mocks or fixtures), or business logic bug (rare — confirm before changing)
3. **Fix** — Simple single-file: read the test, identify root cause, fix to match current behavior, run to verify, iterate until passing. Complex multi-file: spawn fix-agent subagents per failing file with context (why it broke), target (specific file), run command, and constraint to preserve test intent.
4. **Verification** — Run full suite, iterate on remaining failures, verify coverage maintained

## Agent Template

"The business logic has changed and test file {FILE_PATH} is now failing. Read the test file and understand what it tests. Read project testing conventions from README for context. Run the test and analyze the failure. Test expectations outdated? Fix test assertions. Test setup broken? Fix mocks or fixtures. Business logic bug? Fix logic (rare case — confirm first). Fix the test and verify it passes. Iterate until the test passes."

## Design Logic

After refactoring, behavior should be the same — only implementation changed. Tests that fail due to implementation details need updating. Tests that fail because behavior actually changed signal a logic bug. Operates after refactoring or dependency updates to restore the test suite to green so the commit workflow can proceed.