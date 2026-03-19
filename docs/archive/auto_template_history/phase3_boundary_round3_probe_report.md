# Phase 3 Boundary Round 3 Probe Report

## Purpose

This note records the stable-vs-stressed probe on the promoted round-3
Firmicute candidates.

The key question was:

- did any of the new clean `clj > bsu` intake candidates produce a useful
  stable-vs-stressed split along the intended Firmicute axis?

## Probe Definition

Manifest:

- `benchmarks/phase3_boundary_round3_manifest.promoted.yaml`

Compared configurations:

1. stable family:
   - `diamondhit=0.05`
   - `bbh=0.5`
   - `coarse=0.95`
   - `topn=3`
2. stressed family:
   - `diamondhit=0.95`
   - `bbh=0.5`
   - `coarse=0.95`
   - `topn=3`

Output:

- `benchmark-results/phase3-boundary-round3-promoted-2cfg/`

## Main Result

The probe produced exactly one new clean Firmicute leverage case.

Stable config:

- `firmi_cace_atcc824 -> clj`
- `firmi_cthe_atcc27405 -> clj`
- `firmi_tsac_jwslys485 -> clj`

Stressed config:

- `firmi_cace_atcc824 -> clj`
- `firmi_cthe_atcc27405 -> clj`
- `firmi_tsac_jwslys485 -> bsu`

Aggregate screening effect:

- stable `top1_expected_template_hit_rate = 1.0`
- stressed `top1_expected_template_hit_rate = 0.666667`
- stressed `top1_expected_neighbor_hit_rate = 1.0`

## Interpretation

This is the first clean Firmicute-side split we wanted.

What improved:

- `firmi_tsac_jwslys485` flips from `clj` to `bsu`, not to `eco`
- the project now has at least one interpretable Firmicute leverage case that
  stays entirely within the intended competition axis

What stayed useful but not leverage-bearing:

- `firmi_cace_atcc824`
- `firmi_cthe_atcc27405`

These two are still valuable as:

- high-quality Firmicute-side controls

But not yet as:

- strong discriminators

## Promotion Recommendation

Promote into the integrated working screening set:

- `firmi_tsac_jwslys485`

Keep as documented stable controls:

- `firmi_cace_atcc824`
- `firmi_cthe_atcc27405`

Reason:

- adding the leverage case improves screening power
- adding the two stable controls to the integrated set would dilute the
  screening density without changing the stable-vs-stressed split

## Immediate Next Step

Add only `firmi_tsac_jwslys485` to the integrated `Phase 3` manifest and
rerun the stable-vs-stressed tiered pilot.
