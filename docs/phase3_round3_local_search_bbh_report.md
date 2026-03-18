# Phase 3 Round 3 Local Search Report: BBH Balance

## Purpose

This note records the BBH-balance rerun after the round-3 integrated benchmark
upgrade.

The question was:

- does the stronger round-3 benchmark create any useful discrimination inside
  the previously stable BBH balance band?

## Fixed Controls

The following settings were held fixed:

- `template_backend = diamond`
- `template_diamond_hit_weight = 0.05`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`

Manifest:

- `benchmarks/phase3_tuning_manifest.phase1c.round3.yaml`

## Search Band

Swept values:

- `template_bbh_template_weight in {0.3, 0.5, 0.7}`

Output directory:

- `benchmark-results/phase3-round3-local-search-bbh-band/`

## Main Result

All three tested settings remained identical at the benchmark level.

For every tested value:

- `primary_exact_reaction_f1_mean = 0.912203`
- `secondary_approximate_reaction_f1_mean = 0.995336`
- overall `top1_expected_template_hit_rate = 1.0`
- boundary `top1_expected_template_hit_rate = 1.0`
- boundary `top1_expected_neighbor_hit_rate = 1.0`

Boundary recommendations were also unchanged across the full BBH band:

- `actino_cglu_atcc13032 -> mtu`
- `clj_cauto_dsm10061 -> clj`
- `sco_sven_atcc10712 -> sco`
- `actino_rjost_rha1 -> mtu`
- `actino_nfar_ifm10152 -> mtu`
- `actino_sery_nrrl23338 -> sco`
- `firmi_cbei_ncimb8052 -> clj`
- `firmi_tsac_jwslys485 -> clj`

## Interpretation

The stronger round-3 benchmark still does not justify micro-tuning inside:

- `template_bbh_template_weight in [0.3, 0.7]`

So both previously tested local axes remain flat even after the benchmark
became stronger.

That means:

- the current stable family is genuinely robust in this neighborhood

not merely:

- under-resolved because the old benchmark was too weak

## Decision

Freeze the following family as the current working safe region:

- `template_backend = diamond`
- `template_diamond_hit_weight in 0.01-0.10`
- `template_bbh_template_weight in 0.3-0.7`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`

## Recommended Next Step

That outward search has now been executed.

See:

- [phase3_round3_diamondhit_degradation_boundary_report.md](phase3_round3_diamondhit_degradation_boundary_report.md)

Current implication:

- the first observed degradation begins between `0.50` and `0.65`
- the next best move is a small refinement near that transition, not another
  broad sweep
