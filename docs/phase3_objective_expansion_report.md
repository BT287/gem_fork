# Phase 3 Objective Expansion Report

## Purpose

This note records the first `Phase 3` objective-expansion pass after the
post-pilot local search showed that the currently preferred weight family is
flat over the tested neighborhood.

The practical question was:

- can one more controlled `secondary_approximate` case increase objective
  coverage without destabilizing the current tuning loop?

## Change Introduced

Added:

- `bsu_ncib3610` as a new `secondary_approximate` case

Supporting files:

- `benchmarks/reference_models/bsu_ncib3610/model.xml`
- `benchmarks/phase3_tuning_manifest.phase1c.expanded.yaml`

Policy:

- this case is admitted only as secondary evidence
- it is not promoted into the primary exact-reference objective

## Why This Was The Right Next Move

The project already had:

- one exact anchor: `eco_w3110`
- two secondary approximate cases: `eco_bw25113`, `bsu_py79`
- three promoted boundary screens

That setup was enough to reject clearly bad settings, but still narrow enough
that nearby stable settings looked identical.

`bsu_ncib3610` was the best low-cost expansion unit because:

- its query asset already existed
- its biology stays interpretable within the same `bsu` axis
- it broadens the Bacillus approximate tier without introducing a new soft-label
  taxonomic regime

## Validation Pilot

Manifest:

- `benchmarks/phase3_tuning_manifest.phase1c.expanded.yaml`

Compared configurations:

1. `diamondhit=0.05, bbh=0.5, coarse=0.95, topn=3`
2. `diamondhit=0.95, bbh=0.5, coarse=0.95, topn=3`

Output:

- `benchmark-results/phase3-objective-expansion-bsu3610-2cfg/`

## Main Result

The new approximate case ran successfully and stayed stable.

Per-case template behavior:

- stable config:
  - `eco_w3110 -> eco`
  - `eco_bw25113 -> eco`
  - `bsu_py79 -> bsu`
  - `bsu_ncib3610 -> bsu`
  - `actino_cglu_atcc13032 -> mtu`
  - `clj_cauto_dsm10061 -> clj`
  - `sco_sven_atcc10712 -> sco`
- stressed config:
  - `eco_w3110 -> eco`
  - `eco_bw25113 -> eco`
  - `bsu_py79 -> bsu`
  - `bsu_ncib3610 -> bsu`
  - `actino_cglu_atcc13032 -> sco`
  - `clj_cauto_dsm10061 -> clj`
  - `sco_sven_atcc10712 -> sco`

Objective-level summary:

- `primary_exact_reaction_f1_mean = 0.912203`
- `secondary_approximate_reaction_f1_mean = 0.995336`
- `secondary_approximate_reference_case_count = 3`

What changed relative to the earlier manifest:

- approximate evidence count increased from `2` to `3`
- the approximate mean became slightly more robust numerically because it is now
  averaged over one more same-species Bacillus follow-up case

What did **not** change:

- the primary exact objective stayed flat
- the biologically bad stressed configuration was still rejected only because
  the promoted `actino_cglu_atcc13032` boundary case flipped away from its
  strict label

## Interpretation

This expansion was still worth doing.

It improved:

- objective coverage
- confidence that the preferred family is not overfit to a single Bacillus
  follow-up
- implementation readiness for wider secondary-evidence manifests

But it did **not** solve the next bottleneck.

The next bottleneck remains:

- benchmark discrimination

The current loop still depends on one genuinely leverage-bearing promoted
boundary case.

## Next Decision

Do not keep widening the approximate tier blindly.

The next highest-value move is:

1. probe reserve boundary cases one by one
2. keep only those that add real discrimination
3. if reserves stay flat, curate a new external boundary candidate set
