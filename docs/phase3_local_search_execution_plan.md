# Phase 3 Local Search Execution Plan

## Purpose

This note defines the first local search after the integrated `Phase 3 + Phase
1C` pilot identified a stable configuration family.

The key idea is:

- do not widen the full search space yet
- first map the neighborhood around the stable family

## Current Best-Known Region

Current preferred family:

- `template_backend = diamond`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`
- `template_diamond_hit_weight` near `0.05`

Reason:

- exact-anchor E2E quality stayed unchanged
- approximate secondary evidence stayed unchanged
- promoted boundary cases stayed biologically consistent

Reference:

- `docs/phase3_phase1c_integrated_pilot_report.md`

## Final Goal For This Turn

Identify whether the stable family is:

- a narrow point
- or a robust interval

for `template_diamond_hit_weight`.

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

### Work Unit 2. Sweep A Narrow Diamond-Hit Band

Search:

- `template_diamond_hit_weight in {0.01, 0.03, 0.05, 0.07, 0.10}`

Manifest:

- `benchmarks/phase3_tuning_manifest.phase1c.yaml`

Why:

- this band is centered on the current stable value
- it is small enough to interpret manually
- it can reveal whether the `actino_cglu_atcc13032` switch threshold is close
  to the current preferred setting

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

### Work Unit 4. Decide Whether To Expand Along BBH Or Stop

If the whole narrow band behaves identically:

- stop diamond-hit search there
- move next to a small `template_bbh_template_weight` sweep

If the band contains a clear degradation boundary:

- keep the safe side
- tighten the next search near that threshold

## Completion Criteria

- one local-search report is produced
- we can name a preferred `template_diamond_hit_weight` interval
- we can say whether the next move should be:
  - finer diamond-hit search
  - or a small BBH-weight search
