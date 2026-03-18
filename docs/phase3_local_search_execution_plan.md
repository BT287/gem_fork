# Phase 3 Local Search Execution Plan

## Purpose

This note originally defined the first local search after the integrated
`Phase 3 + Phase 1C` pilot identified a stable configuration family.

It now also serves as the handoff note for what happened next:

- the round-3 local safe band was confirmed
- the outward degradation search was executed
- the next task is now threshold refinement, not another broad sweep

## Current Best-Known Region

Current structural family:

- `template_backend = diamond`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`
- `template_bbh_template_weight` in the already-validated local safe band

Current `diamond_hit_weight` interpretation:

- safe through `0.50`
- first observed degradation between `0.50` and `0.65`

Reason:

- exact-anchor E2E quality stayed unchanged
- approximate secondary evidence stayed unchanged
- promoted boundary cases stayed biologically consistent through `0.50`
- leverage-bearing boundary cases begin to fail from `0.65`

Reference:

- `docs/phase3_round3_diamondhit_degradation_boundary_report.md`

## Final Goal For The Next Turn

Refine the first observed transition band so that we can state a practical
upper safe bound for `template_diamond_hit_weight`.

## Divide And Conquer Strategy

### Work Unit 1. Lock Structural Controls

Keep fixed:

- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`
- `template_bbh_template_weight = 0.5`

Why:

- the integrated pilot already showed these settings can preserve anchor tiers
- changing several structural parameters at once would hide the local effect of
  `template_diamond_hit_weight`

### Work Unit 2. Narrow The Transition Band

Completed searches:

- local safe-band check:
  `template_diamond_hit_weight in {0.01, 0.03, 0.05, 0.07, 0.10}`
- coarse outward sweep:
  `template_diamond_hit_weight in {0.15, 0.20, 0.30, 0.50}`
- bracket sweep:
  `template_diamond_hit_weight in {0.65, 0.75, 0.85}`

Next refinement search:

- `template_diamond_hit_weight in {0.55, 0.60, 0.65}`

Original manifest:

- `benchmarks/phase3_tuning_manifest.phase1c.yaml`

Current stronger rerun manifest:

- `benchmarks/phase3_tuning_manifest.phase1c.round3.yaml`

Why:

- `0.50` is still safe
- `0.65` already shows the first strict-label degradation
- this is now the highest-information interval on the axis

### Work Unit 3. Read Results In Three Layers

Layer 1:

- exact-anchor objective

Layer 2:

- approximate-reference secondary evidence

Layer 3:

- promoted boundary strict and neighbor behavior

Acceptance rule:

- keep only settings that preserve Layer 1
- among those, prefer settings that preserve Layer 2 and Layer 3

### Work Unit 4. Decide The Practical Upper Safe Bound

If `0.55` and `0.60` are still safe:

- the practical upper safe region may extend above `0.50`
- do one final confirmation run near the first failing point

If `0.55` already degrades:

- freeze `0.50` as the conservative upper bound
- stop spending more search budget on this axis for now

## Completion Criteria

- the first failing interval is narrowed below width `0.15`
- we can state a practical safe upper bound for the default family
- we can decide whether any further search budget should remain on the
  `diamond_hit_weight` axis
