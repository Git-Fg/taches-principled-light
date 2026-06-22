# config — runtime tuning

There is no "set config" command in the CLI. The model, effort, permission mode, and settings are all set as per-invocation flags, then re-invoked with different values as needed.

## Model

```bash
claude -p "Quick classification" --model haiku      # cheap, fast
claude -p "Hard reasoning task" --model opus --effort max
claude -p "Default work" --model sonnet --effort high
```

## Effort

```bash
claude -p "..." --effort low      # fast, cheap, may be wrong
claude -p "..." --effort medium   # default
claude -p "..." --effort high     # more reasoning
claude -p "..." --effort xhigh    # significantly more reasoning
claude -p "..." --effort max      # the most reasoning the model will do
```

## Permission mode

```bash
claude -p "..." --permission-mode acceptEdits       # auto-accept file edits
claude -p "..." --permission-mode plan              # enter plan mode first
claude -p "..." --permission-mode dontAsk           # don't ask; reject by default
claude -p "..." --permission-mode bypassPermissions  # bypass all checks
```

For agent-driven invocations, `acceptEdits` is almost always what you want — it lets Claude edit files without prompting the user (who isn't there to respond).

## Settings file

```bash
claude -p "..." --settings /path/to/settings.json
claude -p "..." --settings '{"permissions":{"allow":["Bash"]}}'   # inline JSON
```

`--settings` accepts either a path to a JSON file or an inline JSON string. The settings merge with the user/project/local settings per `--setting-sources`.

## Control which setting sources are loaded

```bash
claude -p "..." --setting-sources user,project
claude -p "..." --setting-sources project                    # only project settings
claude -p "..." --setting-sources ""                          # no settings
```

By default, all three sources (user, project, local) are loaded. Use this flag to scope which sources apply for a given invocation.

## Verbose / debug

```bash
claude -p "..." --verbose
claude -p "..." --debug api,hooks          # enable debug mode with category filter
claude -p "..." --debug-file /tmp/debug.log
```

`--debug` with no value enables all categories; with a value, filters to those categories. `--debug-file` writes debug logs to a file (implicitly enables debug mode).
