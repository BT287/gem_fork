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

## Follow-Up Observation

After the checkout/LFS fix, the observed CI state changed:

- `Runtime Stack Matrix`: passed
- `Template Recommendation Smoke`: passed
- `Full Reconstruction Integration`: still failed

The remaining failure no longer occurs at checkout.

It occurs at:

- `Run full reconstruction integration validator`

## Remaining Full-Integration Failure Cause

The workflow step currently launches:

- `python scripts/run_full_integration_check.py --template-backend "${{ matrix.expected_backend }}" ...`

But the workflow matrix did not define `expected_backend`.

That means the shell expands the argument to an empty string, which becomes:

- `--template-backend ""`

The validator CLI only accepts:

- `auto`
- `skani`
- `diamond`

So the step fails before reconstruction validation begins.

## Practical Fix For The Remaining Failure

Two changes were needed.

### 1. Fix The Immediate Workflow Bug

Define `expected_backend` in the matrix so the validator does not receive an
empty backend string.

### 2. Align Full Integration With The Current V1 Default

For merge-ready validation, `Full Reconstruction Integration` should validate
the currently deployed recommendation path rather than a non-default backend.

The current production-oriented default is:

- `template_backend = diamond`

So the workflow should now:

- use `expected_backend: diamond`
- pass `--template-backend diamond`
- pass `--expected-backend diamond`
- require only `diamond` in the runtime check

`skani` remains covered by:

- `Template Recommendation Smoke`

This keeps CI responsibilities separated cleanly:

- runtime portability matrix
- explicit skani recommendation smoke
- diamond-based production full integration

## Current State After Alignment

Local reproduction with:

- `--template-backend diamond`
- `--expected-backend diamond`
- `--skip-secondary`

now passes on the maintainer machine.

So the remaining red `Full Reconstruction Integration` status should currently
be interpreted as:

- a CI-specific failure that still needs direct log visibility

not automatically as:

- a confirmed algorithmic failure of the production default

## Debugging Change

The workflow should emit the following directly into the job log even when the
validator fails:

- `full_integration_summary.json`
- the tail of `full_integration.log`

This makes the next remaining failure directly inspectable without relying only
on downloaded artifacts.
