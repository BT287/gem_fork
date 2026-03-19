# Phase 3 Round 3 Local Search Report: Diamond-Hit Band

## Purpose

This note records the first rerun of the local diamond-hit search after the
round-3 integrated benchmark upgrade.

The question was:

- does the stronger round-3 benchmark finally create discrimination inside the
  previously stable `diamond_hit_weight` neighborhood?

## Fixed Controls

The following settings were held fixed:

- `template_backend = diamond`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`
- `template_bbh_template_weight = 0.5`

Manifest:

- `benchmarks/phase3_tuning_manifest.phase1c.round3.yaml`

## Search Band

Swept values:

- `template_diamond_hit_weight in {0.01, 0.03, 0.05, 0.07, 0.10}`

Output directory:

- `benchmark-results/phase3-round3-local-search-diamondhit-band/`

## Main Result

All five tested settings remained identical at the benchmark level, even after
the round-3 Firmicute leverage upgrade.

For every tested value:

- `primary_exact_reaction_f1_mean = 0.912203`
- `secondary_approximate_reaction_f1_mean = 0.995336`
- overall `top1_expected_template_hit_rate = 1.0`
- boundary `top1_expected_template_hit_rate = 1.0`
- boundary `top1_expected_neighbor_hit_rate = 1.0`

Boundary recommendations were also unchanged across the full band:

- `actino_cglu_atcc13032 -> mtu`
- `clj_cauto_dsm10061 -> clj`
- `sco_sven_atcc10712 -> sco`
- `actino_rjost_rha1 -> mtu`
- `actino_nfar_ifm10152 -> mtu`
- `actino_sery_nrrl23338 -> sco`
- `firmi_cbei_ncimb8052 -> clj`
- `firmi_tsac_jwslys485 -> clj`

## Interpretation

The stronger benchmark did **not** create a local threshold inside:

- `template_diamond_hit_weight in [0.01, 0.10]`

So the earlier conclusion still holds:

- this neighborhood is operationally robust

What changed is not the local geometry.

What changed is the confidence of the claim:

- the claim now holds on a benchmark that includes a clean Firmicute leverage
  case, not only the earlier actinobacterial-heavy set

## Decision

Do **not** spend more search budget on finer resolution inside `0.01-0.10`.

If we want to learn more from this axis, the next move should be:

- an outward boundary search toward the degradation region

for example:

- `template_diamond_hit_weight in {0.15, 0.20, 0.30, 0.50}`

## Immediate Next Step

That BBH rerun and the follow-up outward search have now been executed.

See:

- [phase3_round3_local_search_bbh_report.md](phase3_round3_local_search_bbh_report.md)
- [phase3_round3_diamondhit_degradation_boundary_report.md](phase3_round3_diamondhit_degradation_boundary_report.md)
