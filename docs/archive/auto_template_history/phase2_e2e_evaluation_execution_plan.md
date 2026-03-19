# Phase 2 E2E Evaluation Execution Plan

## Purpose

This document breaks the `Phase 2` end-to-end evaluation layer into concrete
work units.

The goal of `Phase 2` is to move from:

- recommendation-only benchmark results

to:

- final reconstructed model quality measurements

## Current State

Already prepared:

- `Phase 1B` recommendation benchmark cases now exist
- the benchmark runner already records `reference_model` fields
- GMSM already writes canonical model outputs such as `model.xml`,
  `summary_report.json`, and `reactions.tsv`
- a reusable evaluator script now exists
- one exact `Phase 1B` reference model is staged for `eco_w3110`
- one real primary E2E case has already produced both single-case and batch
  evaluation JSON files

Still missing:

- more admitted reference models beyond `eco_w3110`
- a gene-identifier harmonization policy for meaningful gene-level E2E metrics
- broader multi-case E2E coverage across the new `Phase 1B` cases

## Work Breakdown

### Work Unit 0. Freeze The Objective

Status:

- completed

Decision:

- recommendation accuracy is the screening metric
- end-to-end model quality is the optimization metric

Reference:

- `docs/e2e_evaluation_rationale.md`
- `docs/phase2_reference_model_intake_plan.md`

### Work Unit 1. Define The First E2E Metrics

Status:

- completed at scaffold level

First metrics to support:

- reaction precision / recall / F1
- gene precision / recall / F1

Why these first:

- easy to compute reproducibly from SBML
- directly aligned with model content quality
- enough to stand up the first evaluator scaffold

Observed caveat from the first real case:

- reaction overlap is already interpretable
- raw gene overlap is not yet robust across differing gene-ID namespaces
- alias-based harmonized gene matching now exists as a first-pass bridge layer

Reference:

- `docs/phase2_eco_w3110_first_case_report.md`
- `docs/phase2_gene_harmonization_plan.md`
- `docs/phase2_gene_crosswalk_candidate_plan.md`

Defer for later:

- pathway retention
- phenotype agreement
- confidence calibration

### Work Unit 2. Build A Single-Case Evaluator

Status:

- completed at scaffold level

Target script:

- `scripts/evaluate_reconstruction_quality.py`

Required behavior:

- accept a predicted model path or output directory
- accept a reference SBML path
- resolve `model.xml` automatically when given a run directory
- compute reaction and gene overlap metrics
- write a machine-readable evaluation JSON

### Work Unit 3. Add Batch Evaluation Mode

Status:

- completed at scaffold level

Required behavior:

- read a benchmark manifest
- use each case's `reference_model` if present
- locate the predicted case output under a benchmark run directory
- emit one JSON summary for the batch

Completion criteria:

- missing `reference_model` does not crash the entire batch
- skipped cases are explicitly reported

### Work Unit 4. Create Reference-Model Staging Rules

Status:

- completed for the first exact case

Target location:

- `benchmarks/reference_models/`

Per-case requirement:

- stable SBML file
- provenance note
- clear mapping from query organism to reference model

Completion criteria:

- at least one `Phase 1B` case has a trusted reference SBML

Current progress:

- `eco_w3110` is the first admitted exact-reference target
- the remaining four `Phase 1B` cases are now triaged explicitly as
  approximate-candidate or pending-source cases

### Work Unit 5. Run The First Real E2E Case

Status:

- completed for the first primary-only case

Example flow:

1. run full reconstruction for a selected benchmark case
2. evaluate predicted `model.xml` against the trusted reference SBML
3. inspect reaction/gene metrics

Completion criteria:

- one case produces an evaluation JSON successfully

Current result:

- `eco_w3110` now has a real primary reconstruction output and evaluation JSON
- reaction metrics are already informative
- raw gene metrics exposed an identifier-namespace blocker, not a biological
  failure
- alias-based harmonized gene metrics now recover a non-trivial signal from the
  same case

Reference:

- `docs/phase2_eco_w3110_first_case_report.md`

### Work Unit 6. Promote E2E Evaluation Into The Benchmark Loop

Status:

- in progress

Target:

- recommendation benchmark remains the cheap front-end screen
- E2E evaluator becomes the metric layer for later weight tuning

Completion criteria:

- one benchmark run can map:
  - query input
  - selected template
  - final model
  - evaluation JSON

Current progress:

- batch-mode evaluation already works with the main manifest
- the current run evaluates `eco_w3110` and skips the other cases cleanly
  because their `reference_model` fields are still unset

## Immediate Next Practical Blocker

The next real bottlenecks are now:

- staging more trusted reference models under `benchmarks/reference_models/`
- strengthening the current alias-based gene harmonization into a more
  orthology-aware comparison layer before gene-level metrics are used for tuning

## Recommended Next Command

Inspect the first real case report:

```bash
conda activate gmsm
sed -n '1,220p' docs/phase2_eco_w3110_first_case_report.md
```
