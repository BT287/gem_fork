# Auto-Template Parameter Plan

## Purpose

This document is the concise briefing version of the current auto-template parameter strategy.

It is meant for fast alignment before implementation, not as the full handoff spec.

For the detailed implementation backlog, see [auto_template_next_steps_plan.md](auto_template_next_steps_plan.md).

## One-Line Summary

The goal is **not** to maximize template top-1 classification accuracy.

The goal is to choose auto-template scoring weights that improve the quality of the **final reconstructed model** after the full downstream pipeline runs.

## Current Status

Already done:

- auto-template recommendation is implemented
- `skani` coarse ranking, DIAMOND fallback, and BBH reranking are implemented
- score weights are now configurable from the CLI
- the effective score weights are recorded in the recommendation JSON output

Not done yet:

- there is no benchmark-calibrated evidence that the current default weights are optimal
- there is no reconstruction-quality benchmark yet
- confidence labels are still heuristic

## Final Objective

For a benchmark set of query genomes with known biological references, we want to find weight parameters `theta` that maximize downstream reconstruction quality.

Conceptually:

- input: query genome, optional EC file, optional compartment file
- parameter: `theta = {ANI/AF weights, DIAMOND weights, BBH weights, coarse/rerank weights}`
- pipeline: auto-template selection -> GMSM reconstruction -> final model
- objective: maximize average reconstruction quality over the benchmark set

Recommended primary metrics:

- reaction precision / recall / F1
- gene precision / recall / F1
- pathway retention or known-function recovery
- phenotype agreement, if phenotype truth exists

Secondary metrics:

- recommended template rank quality
- score margin stability
- runtime

## Important Clarification

This is closer to **black-box hyperparameter tuning** than to ordinary direct supervised learning.

Reason:

- the pipeline includes ranking, discrete template selection, and downstream reconstruction
- the end-to-end path is not naturally differentiable
- the initial benchmark will likely be small
- we do not directly observe a "correct coefficient label"

So the practical first approach is:

- build a benchmark
- run the pipeline under multiple weight settings
- score the final outputs
- keep the weight setting that gives the best benchmark performance

Not recommended for the first implementation:

- jumping directly to a learned regression/classification model for the weights
- optimizing only for template identity accuracy

## Divide And Conquer Plan

### Phase 0. Parameterization Prerequisite

Status: completed

What was done:

- expose score weights as CLI parameters
- validate that paired weights sum to `1.0`
- record effective weights in output JSON

Why this matters:

- without this step, no reproducible tuning experiment is possible

### Phase 1. Benchmark Scaffold

Goal:

- define a small reproducible benchmark set and a runner

Files:

- `benchmarks/auto_template_benchmark_manifest.yaml`
- `scripts/run_auto_template_benchmark.py`
- `gmsm/tests/test_auto_template_benchmark_runner.py`

Minimum benchmark case fields:

- `case_id`
- `query_input`
- `ec_file`
- `reference_model`
- `expected_taxonomic_neighbors`
- `exclude_templates`
- `tags`
- `notes`

Output:

- `benchmark-results/<label>/benchmark_summary.json`
- per-case copied recommendation outputs

Acceptance:

- all listed cases run through recommendation mode
- one failed case does not destroy the whole batch
- results are saved in a machine-readable summary

### Phase 2. E2E Evaluation Layer

Goal:

- score the final reconstructed model, not only the recommendation stage

Files:

- `scripts/evaluate_reconstruction_quality.py`
- `benchmarks/reference_models/`
- `gmsm/tests/test_reconstruction_quality_eval.py`

Output per case:

- selected template
- reaction metrics
- gene metrics
- optional phenotype/pathway metrics

Acceptance:

- a benchmark case can be mapped from input -> final model -> evaluation JSON

### Phase 3. Weight Tuning Runner

Goal:

- search for a better `theta` using the benchmark

Files:

- `scripts/tune_template_weights.py`
- `gmsm/tests/test_tune_template_weights.py`

Recommended first strategy:

- simple grid search

Why:

- transparent
- easy to debug
- appropriate for a small initial benchmark

Recommended early search dimensions:

- `ani_weight`
- `bbh_template_cov_weight`
- `coarse_weight`
- `template_rerank_topn`

Acceptance:

- all tried parameter sets are logged
- the best parameter set is clearly reported
- results are reproducible from saved outputs

### Phase 4. Confidence Calibration

Goal:

- replace heuristic confidence labels with calibrated estimates

Possible features:

- top-1 score
- top-2 score
- score gap
- ANI
- aligned fraction
- BBH template coverage
- BBH target coverage

Possible methods:

- logistic calibration
- isotonic regression

This phase should come **after** benchmark and tuning, not before.

## Scope Control

Out of scope for the next implementation block:

- multi-template reconstruction
- metagenome/community support
- large rewrites of primary/secondary modeling

## What Needs Senior Buy-In

1. The optimization target should be downstream reconstruction quality, not only template classification accuracy.
2. The first optimization method should be benchmark-driven tuning, not immediate direct ML on the coefficients.
3. The first benchmark can be small (`5-10` cases) if it is reproducible and biologically interpretable.

## Immediate Next Step After Approval

Implement Phase 1 only:

- create benchmark manifest
- create recommendation benchmark runner
- add focused tests

Then review the benchmark outputs before moving to the full E2E evaluation and tuning phases.
