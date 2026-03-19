# Phase 3 Provisional `bsu_py79` Primary-Exact Pilot Report

## Purpose

This note records the first policy-limited test in which `bsu_py79` was
promoted only provisionally into the `primary_exact` tier.

The goal was narrow:

- test whether a second common-use exact anchor creates useful discrimination
  inside the currently safe local tuning family

It was not meant to permanently change the official objective policy.

## Policy Setup

This pilot used a separate manifest:

- [phase3_tuning_manifest.round3.provisional_bsu_py79_exact.yaml](/Users/lavi/gem_fork_auto_template/benchmarks/phase3_tuning_manifest.round3.provisional_bsu_py79_exact.yaml)

Tier interpretation:

- `primary_exact`
  - `eco_w3110`
  - `bsu_py79` via `model_exact_candidate.xml`
- `secondary_approximate`
  - `eco_bw25113`
  - `bsu_ncib3610`
- `boundary_screening`
  - current promoted round-1, round-2, and round-3 boundary cases

## Divide-And-Conquer Execution

The rerun was split into two small searches.

### Search 1. Diamond-Hit Local Band

Fixed controls:

- `template_backend = diamond`
- `template_bbh_template_weight = 0.5`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`

Swept values:

- `template_diamond_hit_weight in {0.01, 0.03, 0.05, 0.07, 0.10}`

Output:

- `benchmark-results/phase3-round3-provisional-bsu-py79-diamond-band/`

### Search 2. BBH Local Band

Fixed controls:

- `template_backend = diamond`
- `template_diamond_hit_weight = 0.05`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`

Swept values:

- `template_bbh_template_weight in {0.3, 0.5, 0.7}`

Output:

- `benchmark-results/phase3-round3-provisional-bsu-py79-bbh-band/`

## Main Result

Both searches stayed completely flat.

For every tested setting in both bands:

- `primary_exact_reaction_f1_mean = 0.786513`
- `secondary_approximate_reaction_f1_mean = 0.995617`
- overall `top1_expected_template_hit_rate = 1.0`
- boundary `top1_expected_template_hit_rate = 1.0`
- boundary `top1_expected_neighbor_hit_rate = 1.0`

Primary exact case breakdown also stayed unchanged:

- `eco_w3110 reaction F1 = 0.912203`
- `bsu_py79 reaction F1 = 0.660824`

## Interpretation

This pilot answered the intended question clearly.

Adding `bsu_py79` as a provisional second exact anchor did **not** create local
discrimination inside the already known safe family.

So the current bottleneck is not:

- lack of a second common-use exact anchor alone
- lack of local search resolution on the `diamond_hit_weight` or BBH axis

The current bottleneck is more likely:

- sparse objective diversity even after adding `eco + bsu`
- or a mismatch between the project benchmark distribution and the real
  deployment query distribution

## Decision

Do not spend more budget on safe-family micro-tuning right now.

Keep the current safe family as the operational default region:

- `template_backend = diamond`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`
- `template_diamond_hit_weight <= 0.50`
- `template_bbh_template_weight in 0.3-0.7`

## Best Next Step

The next highest-value action is now deployment-aware validation.

That means:

- build a small manifest of the query GBKs that the project actually expects to
  use most often
- run the current safe family on that set before spending more effort on
  generic benchmark expansion

If such a deployment set is not yet available, the next best fallback is:

- add one more exact or exact-candidate anchor from another common-use chassis
  family rather than from an exotic stress-test family
