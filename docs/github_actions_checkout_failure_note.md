# GitHub Actions Checkout Failure Note

## What Was Observed

Recent public GitHub Actions runs on branch `codex/auto-template-phase1`
consistently failed at:

- step `2 Checkout`

The failure pattern was shared by:

- `Runtime Stack Matrix`
- `Template Recommendation Smoke`
- `Full Reconstruction Integration`

This means the runs were failing before project code execution started.

## Why This Matters

When multiple workflows on different operating systems fail at the same
`actions/checkout` step, the problem is usually not:

- Python code
- Conda environment solve
- DIAMOND / skani runtime

It is usually repository checkout policy itself.

## Most Plausible Cause In This Repository

These workflows currently request:

- `actions/checkout@v4`
- `lfs: true`

This repository also contains Git LFS-tracked files:

- `gmsm/io/data/input2/mnxm_compoundInfo_dict.p`
- `scripts/input2_data/mnxref.zip`

The recent failures occurred even on workflows that do not need these LFS
assets at all, for example:

- runtime-stack checks
- recommendation-only smoke

So the most plausible cause is:

- `actions/checkout` is failing during the LFS fetch stage
- the workflows are therefore dying before any repo logic runs

## Practical Fix

For workflows that do not require the LFS-backed secondary-model data:

- disable `lfs: true`

For the current `Full Reconstruction Integration` workflow:

- also avoid secondary-model execution in CI by passing `--skip-secondary`
- this keeps the integration validator aligned with the current auto-template
  scope while removing the hard dependency on LFS-backed secondary assets

## Expected Effect

After this change:

- checkout should stop failing immediately on runtime-stack and smoke workflows
- integration should validate the auto-template plus primary-model path instead
  of blocking on secondary-model LFS assets
