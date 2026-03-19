# Phase 3 Boundary Round 3 Change Log

## Summary

This log records what changed in the Firmicute-focused round-3 curation pass
and what the project gained from those changes.

## What Was Added

- shortlist document:
  - `docs/phase3_boundary_round3_candidate_shortlist.md`
- fetch script and test:
  - `scripts/fetch_phase3_boundary_round3_assets.py`
  - `gmsm/tests/test_fetch_phase3_boundary_round3_assets.py`
- draft and promoted manifests:
  - `benchmarks/phase3_boundary_round3_manifest.draft.yaml`
  - `benchmarks/phase3_boundary_round3_manifest.promoted.yaml`
- round-3 integrated manifest:
  - `benchmarks/phase3_tuning_manifest.phase1c.round3.yaml`
- intake, probe, and integrated pilot reports:
  - `docs/phase3_boundary_round3_intake_report.md`
  - `docs/phase3_boundary_round3_probe_report.md`
  - `docs/phase3_round3_integrated_pilot_report.md`

## What Improved

### 1. The project now has a clean Firmicute leverage case

New case:

- `firmi_tsac_jwslys485`

Improvement:

- under the stable setting it selects `clj`
- under the stressed setting it selects `bsu`
- it stays inside the intended `clj`-vs-`bsu` axis instead of drifting to
  `eco`

This is the first clear Firmicute-side analogue of the earlier actinobacterial
leverage cases.

### 2. Integrated screening power increased again

Round-2 integrated pilot:

- stressed overall strict hit `= 0.636364`

Round-3 integrated pilot:

- stressed overall strict hit `= 0.583333`

At the same time:

- `primary_exact_reaction_f1_mean` stayed `0.912203`
- `secondary_approximate_reaction_f1_mean` stayed `0.995336`

So the benchmark became sharper without contaminating the E2E anchor tiers.

### 3. Firmicute curation is now better separated into leverage vs control

Useful stable controls:

- `firmi_cace_atcc824`
- `firmi_cthe_atcc27405`

Useful leverage:

- `firmi_tsac_jwslys485`

This separation matters because strong controls should not be forced into the
integrated working set when they only dilute screening density.

## What Did Not Improve

- the new Bacilli-side candidates did not produce clean `bsu > clj` top-2
  structure
- `firmi_bvelez_fzb42`, `firmi_bamy_dsm7`, and `firmi_ppol_e681` all drifted
  to `eco` as the nearest alternative instead of `clj`
- `firmi_cbei_ncimb8052` is still useful but remains provisional because the
  stressed failure mode still degrades to `eco`

## Current Interpretation

Before round 3:

- boundary leverage existed mainly on the actinobacterial side

After round 3:

- the benchmark has multi-axis leverage
- the main benchmark-design bottleneck is no longer the absence of any clean
  Firmicute signal

## Recommended Next Move

The next optimal move is:

- rerun the narrow local search with the stronger round-3 integrated manifest

Reason:

- the benchmark is now informative enough to justify returning from curation to
  tuning
- another large external curation round would likely cost more than it gains
  right now
