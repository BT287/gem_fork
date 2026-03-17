# Phase 2 First Real E2E Case Report: `eco_w3110`

## Purpose

This report records the first real `Phase 2` end-to-end evaluation case.

The goal was not to solve all E2E evaluation questions at once.

The goal was to prove that the following loop can run on a real `Phase 1B`
benchmark case:

1. query genome
2. auto-template selection
3. primary reconstruction
4. predicted-vs-reference evaluation JSON

## Case Definition

- benchmark case: `eco_w3110`
- query genome: `benchmarks/query_assets/phase1b_first_batch/eco_w3110/input.gbk`
- admitted reference model: `benchmarks/reference_models/eco_w3110/model.xml`
- reference model ID: `iEC1372_W3110`
- reconstruction output:
  `benchmark-results/phase2-eco_w3110-primary-e2e-rerun/eco_w3110/run-output`
- single-case evaluation JSON:
  `benchmark-results/phase2-eco_w3110-primary-e2e-rerun/eco_w3110/evaluation.json`
- batch evaluation JSON:
  `benchmark-results/phase2-eco_w3110-primary-e2e-rerun/evaluation_summary.json`

## What Completed Successfully

- exact reference-model staging for `eco_w3110`
- automatic template selection from the query genome
- primary model export under `3_primary_metabolic_model/model.xml`
- single-case E2E evaluation
- batch-mode E2E evaluation with one evaluated case and the remaining cases
  skipped cleanly

## Observed Reconstruction Summary

From `summary_report.json`:

- template selection mode: `auto`
- template backend: `diamond`
- selection strategy: `coarse_plus_bbh`
- selected template: `eco`
- predicted model ID: `iML1515`
- reaction count: `2675`
- metabolite count: `1877`
- gene count: `3022`

## E2E Metrics

### Reaction Metrics

- precision: `0.926355`
- recall: `0.898477`
- F1: `0.912203`

Interpretation:

- the first exact-reference E2E run already gives a strong reaction-level
  overlap signal
- this is good enough to justify keeping reaction metrics in the early `Phase 2`
  objective

### Gene Metrics

- precision: `0.000331`
- recall: `0.000729`
- F1: `0.000455`
- overlap count: `1`

Interpretation:

- these values are **not** evidence that the reconstructed model is useless
- they show that raw gene-ID overlap is not yet a trustworthy cross-model
  metric in the current pipeline

Why this happened:

- the predicted model carries target-side gene identifiers inherited from the
  homology and pruning workflow
- the BiGG reference model carries its own curated gene identifier namespace
- direct set overlap therefore underestimates biological agreement

Example:

- reaction IDs can match because both models use BiGG-style reaction IDs
- gene IDs can fail to match even when the underlying homologous genes are
  biologically corresponding

This is the same type of issue as comparing two reactor datasets after one file
uses SI units and the other uses mixed engineering units:

- the physical system may match reasonably well
- the raw columns still cannot be compared directly until the namespaces are
  harmonized

## Decision From This First Case

For the next `Phase 2` step:

- reaction overlap is an admissible early E2E metric
- raw gene overlap should be treated as a **diagnostic only**, not yet as a
  tuning objective

## Next Practical Tasks

1. add a gene-identifier harmonization policy before using gene F1 for tuning
2. keep the exact `eco_w3110` reaction metric as the first real E2E anchor
3. only then expand approximate references in this order:
   - `eco_bw25113`
   - `bsu_py79`
   - `bsu_ncib3610`
   - `sco_sliv_tk24`
