# Phase 3 Tiered Multi-Case Pilot Report

## Purpose

This note records the first tiered `Phase 3` pilot after adding:

- exact-anchor vs approximate-secondary evaluation tiers
- locally staged approximate reference SBML files
- offline-friendly no-EC overrides for embedded GenBank EC annotations

The practical question for this pilot was:

- can the tuning loop evaluate one exact case and two approximate cases in a
  single run without network or reference-tier confounding?

## Run Definition

Manifest:

- `benchmarks/phase3_tuning_manifest.yaml`

Cases:

- `eco_w3110` as `primary_exact`
- `eco_bw25113` as `secondary_approximate`
- `bsu_py79` as `secondary_approximate`

Backend:

- `diamond`

Pilot grid:

- `template_diamond_hit_weight in {0.55, 0.95}`
- `template_bbh_template_weight = 0.5`
- `template_coarse_weight = 0.2`
- `template_rerank_topn in {0, 3}`

Total configurations:

- `4`

Output directory:

- `benchmark-results/phase3-tiered-pilot-3case-4cfg-noec/`

## What Completed Successfully

- all four configurations completed
- all three cases completed in each configuration
- no case failed
- exact and approximate tiers were reported separately in the tuning summary

## Per-Case Observations

For the representative top-ranked configuration:

- `eco_w3110`
  - selected template: `eco`
  - reaction F1: `0.912203`
  - tier: `primary_exact`
- `eco_bw25113`
  - selected template: `eco`
  - reaction F1: `0.991634`
  - tier: `secondary_approximate`
- `bsu_py79`
  - selected template: `bsu`
  - reaction F1: `0.994773`
  - tier: `secondary_approximate`

## Aggregate Result

All four tested configurations produced the same summary values:

- `primary_exact_reaction_f1_mean = 0.912203`
- `secondary_approximate_reaction_f1_mean = 0.993204`
- `overall_reaction_f1_mean = 0.966203`
- `top1_expected_template_hit_rate = 1.0`
- `top1_expected_neighbor_hit_rate = 1.0`

## Interpretation

This pilot was operationally successful but informationally flat.

That means:

- the tiered runner now works as intended
- the no-EC override removed the earlier offline confounder
- but the current three-case set is still too easy to distinguish weight
  settings

Most likely reason:

- all tested configurations still select the same expected template for all
  three cases
- once the selected template is unchanged, the downstream model stays unchanged
  as well

So the bottleneck is no longer runner implementation.

The bottleneck is benchmark discriminative power.

## Decision From This Pilot

Do **not** scale immediately to a larger same-species/same-lineage grid search.

That would spend more compute without adding much information.

The next highest-value move is:

- curate boundary or harder-generalization cases that can actually switch the
  selected template under different weight settings

Reference next step:

- `docs/phase1c_boundary_case_execution_plan.md`
