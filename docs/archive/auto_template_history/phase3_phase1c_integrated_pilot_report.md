# Phase 3 + Phase 1C Integrated Pilot Report

## Purpose

This note records the first integrated pilot after:

- curating non-legacy `Phase 1C` boundary candidates
- promoting the strongest ones into a runnable screening set
- merging those boundary screens back into the tiered `Phase 3` tuning manifest

The key question was:

- can a weight change alter boundary-case recommendations while leaving the
  exact-anchor and approximate-reference tiers unchanged?

## Intake Summary

Four non-legacy candidates were staged and smoke-tested:

- `actino_cglu_atcc13032`
- `clj_cauto_dsm10061`
- `firmi_blich_dsm13`
- `sco_sven_atcc10712`

Promotion decision after intake:

- promote `actino_cglu_atcc13032`
- promote `clj_cauto_dsm10061`
- promote `sco_sven_atcc10712`
- keep `firmi_blich_dsm13` as lower-priority reserve

Reference:

- `docs/phase1c_boundary_candidate_intake_report.md`

## Boundary-Only Signal

The promoted three-case boundary pilot produced a real ranking switch:

- under one config, `actino_cglu_atcc13032 -> mtu`
- under another config, `actino_cglu_atcc13032 -> sco`

That means:

- the benchmark is no longer completely flat
- at least one promoted boundary case has genuine leverage on template ranking

## Integrated Tiered Pilot Definition

Manifest:

- `benchmarks/phase3_tuning_manifest.phase1c.yaml`

Cases:

- `eco_w3110` as `primary_exact`
- `eco_bw25113` as `secondary_approximate`
- `bsu_py79` as `secondary_approximate`
- `actino_cglu_atcc13032` as `boundary_screening`
- `clj_cauto_dsm10061` as `boundary_screening`
- `sco_sven_atcc10712` as `boundary_screening`

Two compared configurations:

- `diamondhit=0.05, coarse=0.95, topn=3`
- `diamondhit=0.95, coarse=0.95, topn=3`

Output directory:

- `benchmark-results/phase3-tiered-with-phase1c-2cfg/`

## Main Result

The integrated pilot did exactly what we wanted:

- the exact anchor stayed unchanged
- the approximate-reference cases stayed unchanged
- one promoted boundary case switched

Detailed behavior:

- stable config:
  - `eco_w3110 -> eco`
  - `eco_bw25113 -> eco`
  - `bsu_py79 -> bsu`
  - `actino_cglu_atcc13032 -> mtu`
  - `clj_cauto_dsm10061 -> clj`
  - `sco_sven_atcc10712 -> sco`
- stressed config:
  - `eco_w3110 -> eco`
  - `eco_bw25113 -> eco`
  - `bsu_py79 -> bsu`
  - `actino_cglu_atcc13032 -> sco`
  - `clj_cauto_dsm10061 -> clj`
  - `sco_sven_atcc10712 -> sco`

## Objective-Level Interpretation

For both configurations:

- `primary_exact_reaction_f1_mean = 0.912203`
- `secondary_approximate_reaction_f1_mean = 0.993204`

But the boundary-screening tier changed:

- stable config: `top1_expected_template_hit_rate = 1.0`
- stressed config: `top1_expected_template_hit_rate = 0.666667`

This is the first integrated evidence that:

- the E2E anchor is stable
- the benchmark can still penalize a biologically worse ranking behavior

## Decision

Use the stable configuration family as the preferred region for the next search.

Do not spend time on configurations that:

- keep the exact objective unchanged
- but degrade promoted boundary screens

In other words, the tuning loop now has a practical screening rule:

- preserve exact-anchor reaction quality
- preserve approximate secondary evidence
- reject settings that flip promoted boundary cases away from their strict label

## Recommended Next Step

Expand the search **locally** around the stable config family rather than
globally.

The next high-value move is:

1. keep `template_coarse_weight` near `0.95`
2. keep `template_rerank_topn = 3`
3. search a narrower band around `template_diamond_hit_weight = 0.05`
4. add one more strong boundary candidate only if it improves discrimination
