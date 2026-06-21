# Write Tests — Post-Hoc Coverage for Existing Code

Systematically add test coverage for existing local changes. For when code already exists and needs coverage after the fact.

## Process

1. **Preparation** — Read project testing conventions, identify test command and coverage tools, run full suite for baseline
2. **Analysis** — Identify changed files via git status (uncommitted) or latest commit if everything committed. Filter non-code files. Assess complexity.
3. **Direct Writing** (simple single-file) — Read changed file, review existing test patterns for style and conventions, create tests for all identified cases, run and iterate until passing
4. **Agent Dispatch** (complex multi-file) — Spawn analysis subagents per file to identify test cases, then spawn developer subagents per file to create tests, then spawn verification subagents per file to confirm coverage. Coordinate through shared test case lists.

## Agent Templates

**Analysis:** "Analyze {FILE_PATH} for test coverage needs. The diff shows: {GIT_DIFF}. Read the file and understand its business logic. Identify code paths needing tests: new functions, modified logic, edge cases, error handling. Review existing tests to avoid duplication. Output prioritized test cases (CRITICAL, IMPORTANT, NICE_TO_HAVE)."

**Development:** "Create tests for {FILE_PATH}. Required test cases: {TEST_CASES}. Review project testing conventions from README. Read the target file and existing test files for patterns. Create comprehensive tests for all cases. Run tests with: {TEST_COMMAND}. Iterate until all pass."

**Verification:** "Verify test coverage for {FILE_PATH}. Tests were added at: {TEST_FILES}. Read the changed file and the new test files. Confirm all critical business logic is covered. Report PASS or list specific gaps."

## Design Logic

Operates after implementation but before commit. Ensures changes are tested before entering the commit workflow. For multi-file changes, separate agents analyze each file in parallel and coordinate through shared test case lists — faster and more thorough than sequential manual work.