# GitHub Workflow Push Auth

Use this note when a normal code push succeeds but a push that changes `.github/workflows/*` is rejected.

## What Happened

GitHub rejected the workflow update because the current HTTPS credential does not have enough permission to create or modify workflow files.

In this repository the observed error was:

```text
refusing to allow a Personal Access Token to create or update workflow ... without `workflow` scope
```

That means:

- normal code pushes may still work
- workflow-file pushes need a stronger auth path

## Recommended Paths

### Path A: switch this repo to SSH

This is the cleanest maintainer workflow because it avoids repeated PAT scope friction for normal Git pushes.

1. generate an SSH key if you do not already have one
2. add the public key to your GitHub account
3. test the connection
4. switch the remote

Example commands:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
ssh -T git@github.com
git remote set-url origin git@github.com:Hong-Lavi/gem_fork.git
```

### Path B: use a classic PAT with workflow scope

If you want to keep the HTTPS remote, use a classic Personal Access Token that includes:

- `repo`
- `workflow`

Then retry the push with that credential.

## Local Helper

This repository includes a helper that summarizes the current remote mode and workflow-change risk:

```bash
python scripts/check_github_push_auth.py
python scripts/check_github_push_auth.py --json
```

## Maintainer Note

For this repo:

- use SSH if you expect to edit `.github/workflows/*` regularly
- use the smoke/runtime validators before pushing workflow changes
- if a workflow push fails, fix auth first rather than rewriting the workflow out of the commit
