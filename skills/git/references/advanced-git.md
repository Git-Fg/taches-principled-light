# Advanced Git Commands

Reference for specialized git operations: git notes and git worktrees.

## Git Notes
Attach metadata to commits without changing their SHA.

| Task | Command |
|------|---------|
| Add note | `git notes add -m "message" <sha>` |
| Append | `git notes append -m "message" <sha>` |
| View | `git notes show <sha>` |
| Namespace | `git notes --ref=<name> add -m "..." <sha>` |
| Push | `git push origin refs/notes/<name>` |

**Tip:** Use `git config notes.rewrite.rebase true` to preserve notes during rebase.

## Git Worktrees
Manage multiple working trees attached to the same repository. Work on multiple branches simultaneously without stashing.

### Add Worktree
```bash
git worktree add -b <branch> <path>           # new branch from HEAD
git worktree add <path> <branch>              # existing branch
git worktree add --track -b <branch> <path> origin/<branch>  # from remote
```

### Manage Worktrees
```bash
git worktree list                             # list all
git worktree remove <path>                    # remove
```
