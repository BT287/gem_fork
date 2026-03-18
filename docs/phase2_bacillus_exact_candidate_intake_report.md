# Phase 2 Bacillus Exact-Candidate Intake Report

## Purpose

This report records the first exact-source expansion attempt after the
`eco_w3110` anchor.

The target was not to promote new exact cases immediately.

The target was to answer a narrower question:

- can we build reproducible same-strain Bacillus reference candidates from a
  public source without breaking the current evaluation pipeline?

## Divide-And-Conquer Strategy

The intake was split into four cheaper-to-more-expensive steps.

### Step 1. Source Validation

Goal:

- verify that a public upstream source actually contains the exact Bacillus
  benchmark strains

Result:

- the public `Bacillus_Pan_Genome_Model` repository contains a
  `strain_list.mat`
- `GCF_000497485_1` (`bsu_py79`)
- `GCF_006088795_1` (`bsu_ncib3610`)

This removed the biggest source-risk first.

### Step 2. Export-Path Recovery

Goal:

- convert the Bacillus pan-model MATLAB assets into clean SBML without manual
  editing

Problem found:

- raw `grRules` contained function-like terms such as `strain_GAP ( 5 )`
- `cobra` interpreted these as AST `Call` nodes, which blocked SBML export

Implemented fix:

- `x ( n )` is rewritten to `ogc_n`
- `strain_GAP ( n )` is rewritten to `strain_GAP_n`
- malformed bare numeric terms such as `( 495 )` are rewritten to `ogc_495`
- missing pseudo-gene identifiers are added back into the gene list before
  loading the model

Implementation:

- [reconstruct_bsubtilis_panmodel_reference.py](/Users/lavi/gem_fork_auto_template/scripts/reconstruct_bsubtilis_panmodel_reference.py)
- [test_reconstruct_bsubtilis_panmodel_reference.py](/Users/lavi/gem_fork_auto_template/gmsm/tests/test_reconstruct_bsubtilis_panmodel_reference.py)

### Step 3. Same-Strain Candidate Reconstruction

Goal:

- produce one local exact-candidate SBML for each Bacillus benchmark case

Outputs:

- [model_exact_candidate.xml](/Users/lavi/gem_fork_auto_template/benchmarks/reference_models/bsu_py79/model_exact_candidate.xml)
- [model_exact_candidate.summary.json](/Users/lavi/gem_fork_auto_template/benchmarks/reference_models/bsu_py79/model_exact_candidate.summary.json)
- [model_exact_candidate.xml](/Users/lavi/gem_fork_auto_template/benchmarks/reference_models/bsu_ncib3610/model_exact_candidate.xml)
- [model_exact_candidate.summary.json](/Users/lavi/gem_fork_auto_template/benchmarks/reference_models/bsu_ncib3610/model_exact_candidate.summary.json)

Observed sizes:

- `bsu_py79`: `2186` reactions, `2391` genes
- `bsu_ncib3610`: `2188` reactions, `2398` genes

### Step 4. Evaluator Smoke Against Existing Stable Predictions

Goal:

- check whether the new exact candidates can already be used in the current
  E2E evaluator

Predicted models used:

- stable `diamond_hit_weight = 0.05`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`

Observed reaction metrics:

- `bsu_py79`
  - precision: `0.914309`
  - recall: `0.517383`
  - F1: `0.660824`
- `bsu_ncib3610`
  - precision: `0.915132`
  - recall: `0.522395`
  - F1: `0.665115`

Observed gene metrics:

- raw gene F1: `0.0` for both cases
- alias-harmonized gene F1: `0.0` for both cases

Interpretation:

- the reaction layer is already usable
- the gene layer is currently disconnected because the new reference candidates
  expose `ogc_*` / `strain_GAP_*` namespaces rather than the existing BiGG-like
  aliases used by the current harmonization bridge

## What Improved

- exact-source coverage is no longer limited to `eco_w3110`
- Bacillus now has reproducible same-strain reference candidates instead of
  only the old `iYO844` same-species fallback
- the project now has a working public-source reconstruction path for expanding
  exact-reference intake

## What Did Not Improve Yet

- these Bacillus models are not yet `admitted-exact`
- the current gene-evaluation layer does not connect to the new `ogc_*`
  namespace
- the primary exact objective is still anchored operationally by `eco_w3110`

## Current Status

- `bsu_py79`: `candidate-exact-reconstructed`
- `bsu_ncib3610`: `candidate-exact-reconstructed`

This means:

- same-strain mapping is now plausible and reproducible
- source-policy review is still required before these cases enter the primary
  exact objective

## Recommended Next Step

Do not jump directly to full multi-case exact tuning yet.

First do one explicit policy step:

- decide whether public pan-model-derived same-strain reconstructions are
  acceptable as `primary_exact` references or only as a new `secondary_exact`
  tier

After that decision:

- if accepted as `primary_exact`, rerun the narrow local search with
  `eco_w3110 + bsu_py79`
- if kept below `primary_exact`, add a separate `candidate-exact` reporting tier
  without changing the current objective
