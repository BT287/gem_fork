# Phase 3 Local Search Report: Diamond-Hit Band

## Purpose

This note records the first local search around the stable `Phase 3` family.

The question was:

- is the preferred region near `template_diamond_hit_weight = 0.05` a narrow
  point or a robust interval?

## Fixed Controls

The following settings were held fixed:

- `template_backend = diamond`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`
- `template_bbh_template_weight = 0.5`

Manifest:

- `benchmarks/phase3_tuning_manifest.phase1c.yaml`

## Search Band

Swept values:

- `template_diamond_hit_weight in {0.01, 0.03, 0.05, 0.07, 0.10}`

Output directory:

- `benchmark-results/phase3-local-search-diamondhit-band/`

## Main Result

All five tested settings behaved identically at the benchmark level.

For every tested value:

- `primary_exact_reaction_f1_mean = 0.912203`
- `secondary_approximate_reaction_f1_mean = 0.993204`
- boundary `top1_expected_template_hit_rate = 1.0`
- boundary `top1_expected_neighbor_hit_rate = 1.0`

Boundary recommendations were also stable across the full band:

- `actino_cglu_atcc13032 -> mtu`
- `clj_cauto_dsm10061 -> clj`
- `sco_sven_atcc10712 -> sco`

## Interpretation

This means the current preferred family is not a narrow point.

At least under:

- `coarse = 0.95`
- `topn = 3`
- `bbh_template_weight = 0.5`

the interval

- `template_diamond_hit_weight in [0.01, 0.10]`

is operationally robust on the current benchmark.

## Decision

Stop spending local-search budget on `template_diamond_hit_weight` for now.

Reason:

- this axis is flat over the tested neighborhood
- further refinement here is unlikely to add information

The next useful search axis is:

- `template_bbh_template_weight`

while keeping:

- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`

## Recommended Next Step

Run a small BBH-balance sweep such as:

- `template_bbh_template_weight in {0.3, 0.5, 0.7}`

with the rest of the stable family held fixed.
