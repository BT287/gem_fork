# Briefing Docs

This directory is the merge-review entry point for the auto-template work.

## Read In This Order

1. `auto_template_scoring_and_tuning.md`
   - exact scoring equations
   - parameter-tuning logic
   - benchmark / deployment dataset structure
   - current `v1` operational default

2. `deployment_validation_set.md`
   - current deployment-facing organism mix
   - active deployment manifest
   - relation to archived exploratory manifests

3. `release_readiness.md`
   - what is validated
   - what is still limited
   - what CI is supposed to guarantee

4. `runtime_asset_delivery.md`
   - why runtime assets moved out of Git LFS
   - why Google Drive is the short-term delivery path
   - when to switch to GitHub Release assets

## Historical Context

Detailed phase-by-phase working history now lives in:

- `../archive/auto_template_history/`

Those are still useful for auditability, but they are not the best first read
for merge review.
