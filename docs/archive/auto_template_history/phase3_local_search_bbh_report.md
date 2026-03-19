# Phase 3 Local Search Report: BBH Balance

## Purpose

This note records the next local search after the diamond-hit band turned out
to be robust.

The question was:

- does changing the BBH template-vs-target balance create any useful
  discrimination inside the current stable family?

## Fixed Controls

The following settings were held fixed:

- `template_backend = diamond`
- `template_diamond_hit_weight = 0.05`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`

Manifest:

- `benchmarks/phase3_tuning_manifest.phase1c.yaml`

## Search Band

Swept values:

- `template_bbh_template_weight in {0.3, 0.5, 0.7}`

Output directory:

- `benchmark-results/phase3-local-search-bbh-band/`

## Main Result

All three tested settings behaved identically at the benchmark level.

For every tested value:

- `primary_exact_reaction_f1_mean = 0.912203`
- `secondary_approximate_reaction_f1_mean = 0.993204`
- boundary `top1_expected_template_hit_rate = 1.0`
- boundary `top1_expected_neighbor_hit_rate = 1.0`

Boundary recommendations were stable across the full BBH band:

- `actino_cglu_atcc13032 -> mtu`
- `clj_cauto_dsm10061 -> clj`
- `sco_sven_atcc10712 -> sco`

## Interpretation

Under the currently preferred family:

- `diamond_hit_weight = 0.05`
- `coarse_weight = 0.95`
- `topn = 3`

the tested BBH template-coverage balance is also flat over:

- `template_bbh_template_weight in [0.3, 0.7]`

So the current benchmark does not justify spending more search budget on this
axis right now.

## Decision

Freeze the following family as the current working default region:

- `template_backend = diamond`
- `template_diamond_hit_weight` anywhere in `0.01-0.10`
- `template_bbh_template_weight` anywhere in `0.3-0.7`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`

## Recommended Next Step

The next highest-value move is no longer micro-tuning these weights.

It is one of the following:

1. add one more strong promoted boundary case that can create additional
   discrimination, or
2. improve the objective layer, for example by expanding the admitted exact or
   approximate reference set

At the current stage, benchmark design is a bigger bottleneck than local weight
resolution.
