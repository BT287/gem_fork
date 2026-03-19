# Auto-Template Parameter Plan

## Purpose

This document is the concise briefing version of the current auto-template parameter strategy.

It is meant for fast alignment before implementation, not as the full handoff spec.

For the detailed implementation backlog, see [auto_template_next_steps_plan.md](auto_template_next_steps_plan.md).

For a worked explanation of why final tuning should target end-to-end model
quality rather than template top-1 accuracy alone, see
[e2e_evaluation_rationale.md](e2e_evaluation_rationale.md).

For the short workflow briefing version, see
[parameter_tuning_workflow_briefing.md](parameter_tuning_workflow_briefing.md).

## One-Line Summary

The goal is **not** to maximize template top-1 classification accuracy.

The goal is to choose auto-template scoring weights that improve the quality of the **final reconstructed model** after the full downstream pipeline runs.

## Current Status

Already done:

- auto-template recommendation is implemented
- `skani` coarse ranking, DIAMOND fallback, and BBH reranking are implemented
- score weights are now configurable from the CLI
- the effective score weights are recorded in the recommendation JSON output
- an initial benchmark manifest and recommendation benchmark runner scaffold are implemented

Not done yet:

- there is no benchmark-calibrated evidence that the current default weights are optimal
- there is no downstream reconstruction-quality benchmark yet
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

## Benchmark Design Principle

Do not confuse these two:

- expanding the **template panel**
- expanding the **benchmark query set**

For the next stage, the priority is to expand the **query benchmark set**, not the template panel.

That means:

- keep the current 10 curated templates fixed
- add more biologically meaningful query genomes that should map onto one of those 10 templates

Example:

- non-template *E. coli* strains should usually still be recommended to the `eco` template
- non-template *Streptomyces* query strains may reasonably map to `sco`

This tests whether auto-template recommendation generalizes beyond trivial self-retrieval.

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

Status: initial scaffold implemented; biological benchmark set still incomplete

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

### Phase 1A. Self-Retrieval Sanity Cases

Purpose:

- verify that the recommendation system can recover an exact known template when the query is effectively the template itself

Current status:

- implemented as the current scaffold baseline

What this gives:

- a strong sanity check for DIAMOND ranking and score wiring
- a fast failure detector for regressions in recommendation logic

Limitation:

- this is necessary but not sufficient
- success here does **not** prove useful biological generalization

### Phase 1B. Same-Species / Same-Clade Non-Template Query Cases

Purpose:

- test whether biologically close but non-identical query strains are still mapped to the correct curated template

This is the next highest-value benchmark upgrade.

Examples:

- non-template *E. coli* strains expected to map to `eco`
- non-template *Bacillus subtilis* strains expected to map to `bsu`
- non-template *Streptomyces* strains expected to map to `sco`

Why this matters:

- this is much closer to the real use case than self-retrieval
- it tests generalization while keeping the template panel fixed

### Phase 1C. Harder Generalization Cases

Purpose:

- test recommendation behavior on more ambiguous or boundary cases

Examples:

- same-genus but more distant species
- organisms near a taxonomic boundary between two plausible templates
- cases where top-1 and top-2 templates are both biologically plausible

Use:

- stress-test score margins
- prepare for later confidence calibration

## Query Benchmark Admission Criteria

A query strain should not be added casually.

Minimum criteria:

- genome file is clearly identified and reproducible
- proteome file matches the same strain / assembly
- taxonomic rationale for the expected template is explicit
- the case is not a near-duplicate already present in the benchmark
- file provenance is documented

Preferred criteria:

- complete or high-quality reference genome
- stable RefSeq / GenBank identifiers
- optional EC annotations available
- optional downstream reference model available for later E2E evaluation

Do **not** add a case only because the organism is famous.

Add it when:

- the files are internally consistent
- the expected template assignment is biologically defensible
- the case increases benchmark coverage

## Benchmark Labels To Track

Each benchmark query case should ideally define:

- `expected_template`: the most plausible curated template if known
- `expected_taxonomic_neighbors`: acceptable close templates if ambiguity exists
- `tags`: e.g. `self-retrieval`, `same-species`, `same-genus`, `boundary-case`
- `notes`: brief biological rationale

Interpretation:

- `expected_template` is the strict label
- `expected_taxonomic_neighbors` is the soft biological label

This lets us measure both:

- strict top-1 recovery
- biologically acceptable top-k recovery

### Phase 2. E2E Evaluation Layer

Goal:

- score the final reconstructed model, not only the recommendation stage

Execution scaffold:

- [phase2_e2e_evaluation_execution_plan.md](phase2_e2e_evaluation_execution_plan.md)
- [phase2_reference_model_intake_plan.md](phase2_reference_model_intake_plan.md)
- [phase2_eco_w3110_first_case_report.md](phase2_eco_w3110_first_case_report.md)
- [phase2_gene_harmonization_plan.md](phase2_gene_harmonization_plan.md)
- [phase2_gene_crosswalk_candidate_plan.md](phase2_gene_crosswalk_candidate_plan.md)

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

Execution scaffold:

- [phase3_weight_tuning_execution_plan.md](phase3_weight_tuning_execution_plan.md)

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

- backend-specific coarse score weight:
  - `ani_weight` for `skani`
  - `diamond_hit_weight` for `diamond`
- `bbh_template_cov_weight`
- `coarse_weight`
- `template_rerank_topn`

Current first objective:

- mean reaction F1 over evaluated reference cases

Supporting screening metrics:

- expected-template hit rate
- expected-neighbor hit rate
- alias-harmonized gene F1 as a secondary report-only signal

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
