# Phase 1C Boundary Candidate Intake Report

## Purpose

This note records the first real intake pass for newly curated non-legacy
`Phase 1C` candidates.

The practical questions were:

- can the shortlisted candidates be downloaded reproducibly?
- do they parse cleanly in recommendation-only mode?
- which candidates should be promoted into the runnable boundary set first?

## Intake Scope

The shortlisted candidates were:

- `actino_cglu_atcc13032`
- `clj_cauto_dsm10061`
- `firmi_blich_dsm13`
- `sco_sven_atcc10712`

Reference shortlist:

- `docs/phase1c_boundary_candidate_shortlist.md`

## What Completed Successfully

- all four candidate inputs were staged under
  `benchmarks/query_assets/phase1c_boundary_candidates/`
- all four parsed successfully in recommendation-only benchmark mode
- no case failed during the intake smoke benchmark

Runnable files:

- `benchmarks/phase1c_boundary_manifest.draft.yaml`
- `benchmarks/phase1c_boundary_manifest.promoted.yaml`

## Intake Smoke Result

The recommendation-only smoke benchmark over all four candidates produced:

- `top1_expected_template_hit_rate = 1.0`
- `top1_expected_neighbor_hit_rate = 1.0`
- `failed_case_count = 0`

Output directory:

- `benchmark-results/phase1c-candidate-intake-all4/`

## Per-Case Interpretation

### 1. `actino_cglu_atcc13032`

- recommended template: `mtu`
- top-2 competition observed: `mtu` then `sco`
- interpretation:
  - strong promoted candidate
  - this is exactly the intended `mtu` vs `sco` Actinobacteria axis

### 2. `clj_cauto_dsm10061`

- recommended template: `clj`
- top-2 competition observed: `clj` then `bsu`
- interpretation:
  - strong promoted candidate
  - this is exactly the intended `clj` vs `bsu` Firmicute axis

### 3. `firmi_blich_dsm13`

- recommended template: `bsu`
- top-2 competition observed: `bsu` then `eco`, with `sco` also above `clj`
- interpretation:
  - parseable and biologically acceptable as a `bsu` hard-generalization case
  - weaker as a boundary candidate because the expected `clj` competitor did
    not emerge in the top-2

### 4. `sco_sven_atcc10712`

- recommended template: `sco`
- top-2 competition observed: `sco` then `mtu`
- interpretation:
  - strong promoted candidate
  - clean replacement for weaker legacy `Streptomyces` scaffolds

## Promotion Decision

Promote immediately:

- `actino_cglu_atcc13032`
- `clj_cauto_dsm10061`
- `sco_sven_atcc10712`

Keep as lower-priority reserve:

- `firmi_blich_dsm13`

Reason:

- the promoted three each show the intended strict label plus an interpretable
  second-best competitor
- `firmi_blich_dsm13` is still usable, but it is not yet a strong boundary
  discriminator

## Immediate Next Step

Run a narrow boundary-only pilot on the promoted three-case set to test whether
extreme but still controlled weight settings can change any ranking behavior.
