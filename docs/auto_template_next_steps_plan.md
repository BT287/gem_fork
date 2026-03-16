# Auto-Template Next Steps Plan

## Purpose

This document is the hand-off plan for the next Codex session.

For a concise lab-briefing version of the parameter strategy, see [parameter_plan.md](parameter_plan.md).
For the immediate next-session implementation plan, see [phase1b_query_benchmark_plan.md](phase1b_query_benchmark_plan.md).

Implementation update on 2026-03-16:

- score-weight parameterization is implemented
- an initial benchmark manifest and recommendation benchmark runner scaffold are implemented
- the next work is to expand query benchmark cases beyond self-retrieval, then connect downstream evaluation

Current branch:

- `codex/auto-template-phase1`

Current state:

- auto-template recommendation is implemented
- cross-platform runtime/env scaffolding is implemented
- GitHub Actions for runtime stack, recommendation smoke, and full reconstruction integration are implemented
- Linux/macOS CI and Windows local fallback validation have been completed

This document defines:

- what is already done
- what remains limited
- what should be implemented next
- which files should be touched
- what the acceptance criteria are

The next Codex should read this file first and continue from `Phase 1` unless the user explicitly reprioritizes.


## What Is Already Done

- `skani`-first automatic template recommendation is implemented in [gmsm/template_recommendation.py](../gmsm/template_recommendation.py)
- `diamond` fallback recommendation is implemented
- BBH reranking for top-N candidates is implemented
- recommendation-only execution mode is implemented in [run_gmsm.py](../run_gmsm.py)
- PATH-first executable resolution and OS-compatible binary filtering are implemented in [gmsm/utils.py](../gmsm/utils.py)
- split environments are implemented:
  - [environment.base.yml](../environment.base.yml)
  - [envs/environment.linux-64.yml](../envs/environment.linux-64.yml)
  - [envs/environment.osx-arm64.yml](../envs/environment.osx-arm64.yml)
  - [envs/environment.win-64.yml](../envs/environment.win-64.yml)
- runtime/smoke/full-integration validators are implemented:
  - [scripts/check_runtime_stack.py](../scripts/check_runtime_stack.py)
  - [scripts/run_template_recommendation_smoke.py](../scripts/run_template_recommendation_smoke.py)
  - [scripts/run_full_integration_check.py](../scripts/run_full_integration_check.py)
- workflows are implemented:
  - [.github/workflows/runtime-stack-matrix.yml](../.github/workflows/runtime-stack-matrix.yml)
  - [.github/workflows/template-recommendation-smoke.yml](../.github/workflows/template-recommendation-smoke.yml)
  - [.github/workflows/full-reconstruction-integration.yml](../.github/workflows/full-reconstruction-integration.yml)


## Current Recommendation Logic

The current scoring logic is heuristic and hard-coded.

Coarse genome-level score for `skani`:

- `g = 0.7 * normalize_ani(ANI) + 0.3 * aligned_fraction`

Coarse proteome-level score for `diamond` fallback:

- `d = 0.85 * hit_coverage + 0.15 * mean_identity`

BBH rerank score:

- `p = 0.7 * bbh_template_coverage + 0.3 * bbh_target_coverage`

Final reranked score:

- `s = 0.6 * coarse_score + 0.4 * rerank_score`

Important clarification:

- this is `single-template auto-selection`
- this is **not** multi-template reconstruction
- `template_rerank_topn = 3` means the top 3 candidates are reranked, not that 3 templates are used to build the model


## Current Limitations

### 1. Heuristic weights are not calibrated

- the current weights are biologically motivated but not benchmark-calibrated
- there is no evidence yet that `0.6/0.4` or `0.7/0.3` are optimal for downstream GEM quality

### 2. Current validation is software-first, not biology-first

- current checks prove that the software runs correctly
- they do not yet prove that the recommended template is biologically optimal

### 3. Confidence is heuristic

- current `high/medium/low` confidence comes from score gap heuristics
- it is not calibrated as a probability of recommendation correctness

### 4. Template panel is still small

- current curated panel is limited
- recommendation quality is upper-bounded by template diversity and panel coverage

### 5. Current implementation is single-template only

- after ranking, the pipeline chooses exactly one template
- no reaction-level or evidence-level multi-template aggregation exists

### 6. Metagenome/community support is out of scope for now

- current pipeline assumes a single target genome
- do not try to solve metagenome/community modeling in the next phase


## Next Objective

The next objective is not another platform feature.

The next objective is:

- build a benchmark for biological validation
- expose the scoring weights as configurable parameters
- tune the weights against downstream reconstruction quality
- calibrate recommendation confidence

In short:

- move from `heuristic auto-template` to `benchmark-calibrated auto-template`


## Guiding Principle

Do **not** optimize only for "correct template classification".

Optimize for downstream reconstruction quality.

Recommended objective:

- choose weights that improve the quality of the resulting reconstructed model

Candidate metrics:

- reaction-level precision/recall/F1 against a trusted reference model
- gene-level precision/recall/F1
- pathway retention / known function recovery
- phenotype agreement, if phenotype truth is available
- recommendation rank quality as a secondary metric


## Phase Breakdown

## Phase 1. Benchmark Scaffold

### Goal

Create a reproducible benchmark dataset and runner for auto-template calibration.

### Files to Add

- `benchmarks/auto_template_benchmark_manifest.yaml`
- `scripts/run_auto_template_benchmark.py`
- `gmsm/tests/test_auto_template_benchmark_runner.py`

### Manifest Requirements

Each benchmark case should include:

- `case_id`
- `query_input`
- `ec_file`
- `expected_taxonomic_neighbors`
- `reference_model`
- `notes`
- `exclude_templates`
- `tags`

The benchmark manifest should be small at first.

Target initial size:

- `5-10` benchmark cases

### Runner Requirements

The runner should:

- load the manifest
- run recommendation-only mode for each case
- store recommendation JSON and candidate TSV outputs per case
- optionally run full reconstruction for selected cases later
- write a machine-readable benchmark summary JSON

### Output Requirements

Store results under:

- `benchmark-results/<timestamp-or-label>/`

Required outputs:

- `benchmark_summary.json`
- one subfolder per case
- copied `template_recommendation.json`
- copied `template_candidates.tsv`

### Acceptance Criteria

- benchmark runner executes all listed cases
- one failing case does not destroy all other outputs
- benchmark summary reports pass/fail per case
- tests cover manifest parsing and summary writing


## Phase 2. Score Config Extraction

### Goal

Make recommendation weights configurable instead of hard-coded.

### Files to Modify

- [gmsm/template_recommendation.py](../gmsm/template_recommendation.py)
- [run_gmsm.py](../run_gmsm.py)
- [gmsm/utils.py](../gmsm/utils.py)
- [gmsm/tests/test_template_recommendation.py](../gmsm/tests/test_template_recommendation.py)

### Required Refactor

Introduce a score config object, for example:

```python
from dataclasses import dataclass

@dataclass
class TemplateScoreConfig:
    ani_weight: float = 0.7
    af_weight: float = 0.3
    diamond_hit_weight: float = 0.85
    diamond_identity_weight: float = 0.15
    bbh_template_cov_weight: float = 0.7
    bbh_target_cov_weight: float = 0.3
    coarse_weight: float = 0.6
    rerank_weight: float = 0.4
```

### CLI Requirements

Add CLI knobs to `run_gmsm.py`, such as:

- `--template-ani-weight`
- `--template-af-weight`
- `--template-diamond-hit-weight`
- `--template-diamond-identity-weight`
- `--template-bbh-template-weight`
- `--template-bbh-target-weight`
- `--template-coarse-weight`
- `--template-rerank-weight`

### Validation Requirements

Add validation rules:

- paired weights must sum to `1.0` within tolerance
- all weights must be within `[0, 1]`
- invalid combinations must exit early with a clear message

### Acceptance Criteria

- defaults preserve current behavior
- tests cover custom weights and validation errors
- recommendation JSON records the effective weights used


## Phase 3. Weight Tuning Runner

### Goal

Run systematic weight tuning against the benchmark.

### Files to Add

- `scripts/tune_template_weights.py`
- `gmsm/tests/test_tune_template_weights.py`

### First Tuning Strategy

Use simple grid search first.

Do not jump to complex ML immediately.

Recommended search dimensions:

- `ani_weight in {0.5, 0.6, 0.7, 0.8}`
- `bbh_template_cov_weight in {0.5, 0.6, 0.7, 0.8}`
- `coarse_weight in {0.4, 0.5, 0.6, 0.7, 0.8}`
- `template_rerank_topn in {1, 3, 5}`

Derived complementary weights should be computed automatically.

### Objective for First Version

The first version may optimize a simplified benchmark score, for example:

- `benchmark_score = 0.5 * rank_metric + 0.5 * downstream_proxy`

If full curated GEM comparisons are not ready yet, use temporary proxies such as:

- whether the expected taxonomic neighbor appears in top-k
- top1/top2 score margin stability
- consistency across rerank settings

### Acceptance Criteria

- tuning runner writes sortable result tables
- best parameter set is clearly reported
- results can be reproduced from saved JSON/CSV outputs


## Phase 4. Downstream Reconstruction Benchmark

### Goal

Move from proxy ranking metrics to actual reconstruction-quality metrics.

### Files to Add

- `scripts/evaluate_reconstruction_quality.py`
- `benchmarks/reference_models/`
- `gmsm/tests/test_reconstruction_quality_eval.py`

### Required Metrics

For each benchmark case:

- reaction precision
- reaction recall
- reaction F1
- gene precision
- gene recall
- gene F1

Optional if data exists:

- growth phenotype accuracy
- gene essentiality agreement

### Acceptance Criteria

- benchmark score can be computed from reconstruction artifacts
- tuning runner can consume these metrics
- summary report ranks weight sets by downstream model quality


## Phase 5. Confidence Calibration

### Goal

Replace heuristic confidence labels with calibrated confidence estimates.

### Files to Add

- `scripts/calibrate_template_confidence.py`
- `gmsm/tests/test_template_confidence_calibration.py`

### Inputs for Calibration

Potential calibration features:

- top1 score
- top2 score
- score margin
- ANI
- aligned fraction
- BBH template coverage
- BBH target coverage
- rerank changed top1 or not

### Recommended Methods

Start simple:

- logistic calibration
- isotonic regression

### Acceptance Criteria

- calibration artifact is saved in a reproducible format
- runtime code can load the calibrator optionally
- report can include:
  - `confidence_probability`
  - calibrated `confidence_label`


## Phase 6. Template Panel Expansion

### Goal

Increase the biological coverage of the template panel.

### Files to Modify

- [gmsm/io/data/input1/template_catalog.json](../gmsm/io/data/input1/template_catalog.json)
- [gmsm/io/data/input1/template_genome_sources.json](../gmsm/io/data/input1/template_genome_sources.json)
- [scripts/fetch_template_genome_bank.py](../scripts/fetch_template_genome_bank.py)
- [scripts/build_template_genome_bank_bundle.py](../scripts/build_template_genome_bank_bundle.py)

### Constraints

Do not add templates casually.

Each new template should include:

- a reliable GEM
- proteome FASTA
- genome FASTA
- source metadata
- compatibility with current input1 layout

### Acceptance Criteria

- expanded panel is reproducible through fetch/bundle scripts
- benchmark mean performance improves or remains stable


## Explicit Non-Goals For The Next Codex

Do not prioritize these unless the user explicitly asks:

- multi-template reconstruction
- metagenome/community modeling
- large architectural rewrites of primary/secondary modeling
- master merge

If the user later asks for multi-template support, that should be treated as a new phase and documented separately.


## Suggested Implementation Order

The next Codex should proceed in this order:

1. implement Phase 1 benchmark scaffold
2. implement Phase 2 score config extraction
3. implement Phase 3 weight tuning runner
4. stop and review results with the user
5. only then proceed to Phases 4 and 5


## Operational Rules For The Next Codex

- do not break existing CI
- keep current default behavior backward-compatible
- keep Linux/macOS `skani` smoke and Windows fallback smoke working
- use `apply_patch` for edits
- verify with focused tests after each phase
- update this document if the implementation plan changes materially


## Minimal Deliverable For The Next Session

If time is limited, the minimum valuable next deliverable is:

- benchmark manifest
- benchmark runner
- configurable score weights

That alone will turn the current system from a fixed heuristic into a tunable experimental framework.


## Final Status Note

As of the end of the current session:

- auto-template implementation is complete for the current scope
- platform validation is complete for the current scope
- biological calibration is the main remaining research-engineering task
