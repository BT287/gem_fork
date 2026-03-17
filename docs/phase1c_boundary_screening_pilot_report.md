# Phase 1C Boundary-Screening Pilot Report

## Purpose

This note records the first `Phase 1C` pilot after teaching the tuning runner
to treat `boundary_screening` cases as recommendation-only runs.

The practical question was:

- can we add harder or softer-label benchmark cases to the tuning loop without
  paying full reconstruction cost for every candidate configuration?

## What Changed

The tuning runner now sends `boundary_screening` cases through:

- `--auto-template`
- `--template-recommendation-only`

instead of running the full reconstruction path.

Why this matters:

- exact and approximate-reference cases still provide the E2E objective
- boundary cases can now probe ranking behavior much more cheaply
- this lowers the cost of benchmark curation loops

## Pilot Definition

Manifest:

- `benchmarks/phase1c_boundary_screening_manifest.yaml`

Cases used in this boundary-only pilot:

- `sco_sliv_tk24`
- `streptomyces_collinus_antismash8`
- `streptomyces_collinus_refseq_genbank`

Backend:

- `diamond`

Pilot grid:

- `template_diamond_hit_weight in {0.05, 0.95}`
- `template_bbh_template_weight = 0.5`
- `template_coarse_weight in {0.05, 0.95}`
- `template_rerank_topn = 0`

Total configurations:

- `4`

Output directory:

- `benchmark-results/phase1c-boundary-screening-only-pilot/`

## What Completed Successfully

- all four configurations completed
- all three boundary-screening cases completed
- all three cases ran in recommendation-only mode
- no case failed

Operationally, this closes the main plumbing question for `Phase 1C`.

## Per-Case Result

Across all four configurations:

- `sco_sliv_tk24 -> sco`
- `streptomyces_collinus_antismash8 -> sco`
- `streptomyces_collinus_refseq_genbank -> eco`

Interpretation:

- the first two cases are biologically consistent with the current soft label
- the legacy two-CDS `streptomyces_collinus_refseq_genbank` scaffold is not
  behaving like a usable `sco`-neighbor screening case

## Aggregate Boundary Metrics

Best-configuration boundary metrics were:

- `top1_expected_template_hit_rate = 1.0`
- `top1_expected_neighbor_hit_rate = 0.666667`
- `topk_expected_neighbor_hit_rate = 1.0`
- `failed_case_count = 0`

Important nuance:

- only `sco_sliv_tk24` has a strict `expected_template`
- the two `Streptomyces collinus` scaffolds are soft-label cases only

So the key signal here is the neighbor-hit rate, not the strict-hit rate.

## Interpretation

This pilot was operationally successful and scientifically useful.

Operational result:

- `Phase 1C` boundary-screening can now be iterated quickly inside the tuning
  workflow

Scientific result:

- the current local boundary set is still not sufficient to separate weight
  settings
- one legacy scaffold looks more like an admission-quality problem than a good
  benchmark case

So the bottleneck has shifted again.

It is no longer runner implementation.

It is now `boundary-case quality`.

## Decision From This Pilot

Do not promote `streptomyces_collinus_refseq_genbank` into a trusted tuning
screen.

Treat it as:

- a legacy debug artifact
- not a high-confidence biological benchmark

Keep using:

- `sco_sliv_tk24`
- `streptomyces_collinus_antismash8`

as provisional boundary-screening seeds until better curated organisms are
added.

## Recommended Next Step

Curate `2-4` new non-legacy boundary candidates with:

- full genome provenance
- interpretable soft labels
- plausible competition between at least two template-scoring modes

Reference plan:

- `docs/phase1c_boundary_case_execution_plan.md`
