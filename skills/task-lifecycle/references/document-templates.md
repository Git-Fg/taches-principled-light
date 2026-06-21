# Agent Instruction Templates

### Documentation Analysis Agent (Haiku)

```markdown
Analyze documentation needs for changes in {DOCUMENTATION_AREA}.

Context: These files were modified:
{CHANGED_FILES_LIST}

Git diff summary:
{GIT_DIFF_SUMMARY}

Your task:
1. Review the changes and understand their documentation impact
2. Identify what documentation needs to be created or updated
3. Identify index documents requiring updates
4. Create prioritized list: CRITICAL / IMPORTANT / NICE_TO_HAVE
```

### Tech Writer Agent (Documentation Creation)

```markdown
Create/update documentation for {DOCUMENTATION_AREA}.

Documentation requirements:
{DOCUMENTATION_TASKS_LIST}

Your task:
1. Read the changed files and understand the impact
2. Read @README.md for project context
3. Create/update documentation following project conventions
4. Ensure: clear language, working examples, valid links
```

### Quality Review Agent (Verification)

```markdown
Review documentation quality for {DOCUMENTATION_AREA}.

Files to review:
{DOCUMENTATION_FILES}

Your task:
1. Verify all user-facing changes are covered
2. Check code examples are accurate
3. Verify links and references are valid
4. Check for conflicts with existing documentation
```
