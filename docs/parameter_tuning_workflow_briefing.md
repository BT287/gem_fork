# Auto-Template Parameter Tuning Workflow Briefing

## Purpose

This note is the short briefing version of the current parameter-tuning
workflow.

It is meant to answer four practical questions:

1. what information each stage extracts
2. what function is being tuned
3. what objective function is currently valid
4. what has changed from the original plan

For the more detailed planning backlog, see
[parameter_plan.md](parameter_plan.md).

For a fuller report-style explanation of the whole estimation workflow, see
[auto_template_parameter_estimation_report.md](auto_template_parameter_estimation_report.md).

## One-Line Summary

We are **not** fitting a learned regression model for template choice.

We are running a **benchmark-driven search over a weight vector** `theta`, then
keeping the setting that gives the best **end-to-end reconstructed-model
quality**.

## The Object Being Tuned

For a query genome `x` and template candidate `m`, the recommendation stage
computes a template score:

- coarse similarity score
- BBH rerank score
- final weighted template score

The parameter vector is:

```text
theta = {
  ANI/AF weights or DIAMOND hit/identity weights,
  BBH template/target coverage weights,
  coarse/rerank combination weights,
  rerank_topn
}
```

Code references:

- [template_recommendation.py](/Users/lavi/gem_fork_auto_template/gmsm/template_recommendation.py#L32)
- [run_gmsm.py](/Users/lavi/gem_fork_auto_template/run_gmsm.py#L94)
- [utils.py](/Users/lavi/gem_fork_auto_template/gmsm/utils.py#L22)

## Stage-By-Stage Workflow

### Phase 0. Parameterization

Input:

- query genome
- fixed template panel
- CLI-configured score weights

Output:

- explicit `theta`
- validated paired weights
- recommendation JSON recording the effective weights

Why this stage exists:

- without explicit `theta`, no reproducible tuning experiment is possible

### Phase 1. Recommendation Benchmark

Input:

- benchmark manifest of biologically meaningful query cases

Extracted information:

- recommended template
- top-k candidate list
- strict expected-template hit
- soft expected-neighbor hit

This stage answers:

- "does the recommendation logic generalize beyond self-retrieval?"

It does **not** answer:

- "did the final reconstructed model improve?"

### Phase 2. End-To-End Evaluation

Input:

- selected template from the recommendation stage
- full reconstruction output
- trusted reference SBML for admitted cases

Extracted information:

- reaction overlap metrics
- raw gene overlap metrics
- alias-harmonized gene overlap metrics

Current evaluator:

- [evaluate_reconstruction_quality.py](/Users/lavi/gem_fork_auto_template/scripts/evaluate_reconstruction_quality.py#L1)

This stage answers:

- "did this `theta` produce a better final model?"

### Phase 3. Weight Tuning

Input:

- a small search set of candidate `theta` values
- Phase 1 recommendation summaries
- Phase 2 E2E evaluation summaries

Operation:

- run the same benchmark under each `theta`
- score the resulting models
- rank the tried settings

This is black-box hyperparameter search, not differentiable supervised learning.

## The Actual Functions

The current template-scoring equations in code are:

For skani coarse ranking:

```text
C_skani = w_ani * normalized_ani + w_af * aligned_fraction
```

For DIAMOND coarse ranking:

```text
C_diamond = w_hit * hit_coverage + w_id * mean_identity_fraction
```

For BBH reranking:

```text
R_bbh = w_bbh_template * template_coverage + w_bbh_target * target_coverage
```

Final recommendation score:

```text
S_theta = w_coarse * C + w_rerank * R_bbh
```

Selected template:

```text
m_hat_i(theta) = argmax_m S_theta(x_i, m)
```

Final pipeline:

```text
x_i -> m_hat_i(theta) -> GMSM reconstruction -> G_hat_i(theta)
```

## Current Objective Function

The original plan listed reaction and gene metrics as co-equal early targets.

That is no longer the best interpretation.

After the first exact `eco_w3110` case, the current safe objective is:

```text
J(theta) = mean reaction F1 over evaluated reference cases
```

In notation:

```text
J(theta) = (1 / |E|) * sum_i reaction_F1_i(theta)
```

where `E` is the set of benchmark cases with admitted reference models that
successfully evaluate.

Current metric policy:

- primary optimization metric: reaction F1 mean over exact-anchor cases
- secondary evidence metric: reaction F1 mean over approximate-reference cases
- screening metric: expected-template / expected-neighbor hit behavior
  including recommendation-only `boundary_screening` cases
- secondary diagnostic: alias-harmonized gene metrics
- raw gene overlap: diagnostic only

## Why The Objective Changed

The first real exact case was `eco_w3110`.

Observed values:

- reaction F1: `0.912203`
- raw gene F1: `0.000455`
- alias-harmonized gene F1: `0.146108`

Interpretation:

- reaction IDs are already comparable across the predicted and reference models
- raw gene IDs are not yet directly comparable because the namespaces differ
- alias harmonization recovers real signal, but it is still not orthology-grade

So tuning directly against raw gene overlap would optimize a namespace artifact,
not model quality.

Reference:

- [phase2_eco_w3110_first_case_report.md](/Users/lavi/gem_fork_auto_template/docs/phase2_eco_w3110_first_case_report.md#L52)
- [phase2_gene_harmonization_plan.md](/Users/lavi/gem_fork_auto_template/docs/phase2_gene_harmonization_plan.md#L79)

## What Is Completed

- score weights are parameterized and validated
- recommendation benchmark runner exists
- first `Phase 1B` benchmark batch exists
- exact `eco_w3110` reference intake exists
- public same-strain Bacillus exact-candidate reconstructions now exist for
  `bsu_py79` and `bsu_ncib3610`, but they are still below `admitted-exact`
  status pending source-policy review
- a provisional `bsu_py79` primary-exact pilot has now been executed, and it
  still leaves the current local safe family completely flat
- E2E evaluator exists
- alias-based gene harmonization exists as a bridge metric
- the integrated screening set now contains a clean Firmicute leverage case
  (`firmi_tsac_jwslys485`) in addition to the earlier actinobacterial
  leverage set
- the stronger round-3 benchmark still leaves the tested local diamond-hit and
  BBH bands flat, so the safe family appears genuinely robust in that region
- outward search plus refinement now show that the first practical degradation
  begins at `template_diamond_hit_weight = 0.55`, so the current safe upper
  bound is `0.50`

## What Is Not Completed

- multi-case exact-reference E2E benchmark coverage
- reviewed gene crosswalks for exact cases
- confidence calibration
- explicit promotion policy for public pan-model-derived exact candidates
- a deployment-validation set built from the query GBKs the project actually
  expects to use most often

## What Changed From The Original Plan

### Original expectation

- recommendation benchmark first
- then generic downstream evaluator
- then weight tuning
- reaction and gene metrics treated similarly

### Current updated plan

- recommendation benchmark remains the cheap regression screen
- exact-reference E2E reaction metrics become the first true tuning objective
- approximate-reference E2E metrics become secondary evidence, not the main objective
- raw gene metrics stay diagnostic-only
- alias-based gene metrics stay supplementary until stronger crosswalks exist
- after the round-3 Firmicute curation pass, the next immediate action is a
  rerun of the narrow local search rather than another broad benchmark hunt
- after completing that rerun, the next immediate action becomes an outward
  degradation-boundary search rather than finer tuning inside the safe band
- after completing the outward search and refinement, the next immediate action
  becomes exact-reference expansion rather than more search on the same axis
- after the first Bacillus exact-source expansion, the next immediate action
  becomes exact-candidate policy review rather than immediate promotion into the
  primary exact objective
- after the provisional `bsu_py79` primary-exact rerun remained flat, the next
  immediate action becomes deployment-aware validation rather than more
  safe-family micro-tuning

## Practical Rule For The Next Block

For the first real tuning loop:

- fix the recommendation backend instead of leaving it on `auto`
- search a narrow grid of `theta`
- rank candidates by reaction F1 on admitted reference cases
- keep recommendation hit rates as a regression screen

Reason:

- if backend choice changes implicitly, the experiment mixes "weight effects"
  with "backend availability effects"

## Next Step

The most reasonable next implementation is now exact-reference expansion for
the primary objective:

1. keep the current default family below `template_diamond_hit_weight = 0.50`
2. expand exact-reference E2E coverage
3. strengthen the primary optimization objective
4. return to cross-axis tuning only after the exact tier is less sparse

Detailed breakdown:

- [phase3_weight_tuning_execution_plan.md](phase3_weight_tuning_execution_plan.md)
- [phase3_round3_diamondhit_degradation_boundary_report.md](phase3_round3_diamondhit_degradation_boundary_report.md)
- [phase2_bacillus_exact_candidate_intake_report.md](phase2_bacillus_exact_candidate_intake_report.md)
- [phase3_provisional_bsu_py79_primary_exact_report.md](phase3_provisional_bsu_py79_primary_exact_report.md)
- [deployment_validation_set_plan.md](deployment_validation_set_plan.md)
