# context — workspace

Tell Claude about the working directory and any additional context it should have access to.

## Add directories to the tool access list

```bash
claude -p "Refactor this" --add-dir /path/to/lib --add-dir /path/to/tests
```

`--add-dir` is repeatable. The CLI grants tool access to each additional directory. Without it, Claude is sandboxed to the current working directory.

For the common case of "let Claude read the current directory", `claude -p` in the target dir is enough — `--add-dir` is for adding extras.

## Use a git worktree

```bash
claude -p "Refactor in a clean worktree" --worktree
# or with a name:
claude -p "Refactor in a clean worktree" --worktree auth-refactor
```

`--worktree` creates a new git worktree for the session. The session runs in the worktree; changes are isolated until you merge. Optional `[name]` for the worktree branch.

Combine with `--tmux` to run the work in a tmux session (or iTerm2 native panes):

```bash
claude -p "Refactor in a worktree" --worktree --tmux
```

## Diagnose the Claude Code installation

```bash
claude doctor
```

Runs health checks on the Claude Code auto-updater. Reports whether updates are available, and whether the installation is healthy. The workspace trust dialog is skipped; stdio servers from `.mcp.json` are spawned for health checks. Use only in directories you trust.

For deeper diagnostics (session analytics, hook events), use the marketplace's analyzing-sessions skill.
