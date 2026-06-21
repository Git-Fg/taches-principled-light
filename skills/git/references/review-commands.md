# GitHub Review Commands

Reference for raw GitHub API commands using the `gh` CLI for pull request reviews.

### Single Inline Comment
```bash
gh api repos/{owner}/{repo}/pulls/{pr}/comments \
  -f body='...' \
  -f commit_id='<sha>' \
  -f path='<file>' \
  -F line=<n> \
  -f side='RIGHT'
```

### Multi-Comment Review (Batch)
```bash
echo '{ "event": "COMMENT", "body": "...", "comments": [...] }' | \
  gh api repos/{owner}/{repo}/pulls/{pr}/reviews --input -
```

### Get Latest Commit SHA
```bash
gh api repos/{owner}/{repo}/pulls/{pr} --jq '.head.sha'
```

### Review Events
- `COMMENT`: General feedback without approval.
- `APPROVE`: Approve the changes.
- `REQUEST_CHANGES`: Explicitly request changes before merging.
