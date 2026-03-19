# Phase 3 Weight Tuning Execution Plan

## Purpose

This note breaks the first real parameter-tuning loop into concrete work units.

The goal is not to launch a large global search immediately.

The goal is to stand up a **controlled narrow tuning loop** that can already
rank candidate weight settings reproducibly.

## Where Confusion Happens

Two confounders need to be separated:

1. backend choice
2. score-weight choice

If tuning is run with `--template-backend auto`, then a parameter sweep can mix:

- true weight effects
- environment-driven backend fallback effects

So the first tuning loop should fix the backend explicitly.

## Current Tuning Policy

For the first exact-reference loop:

- fixed backend
- narrow grid search
- primary objective: mean reaction F1 over `primary_exact` cases
- secondary evidence: mean reaction F1 over `secondary_approximate` cases
- recommendation hit rates kept as screening metrics

This is intentionally conservative.

## Work Units

### Work Unit 0. Freeze The Experimental Degree Of Freedom

Status:

- completed as a planning decision

Decision:

- tune weights with a fixed recommendation backend
- do not use `auto` for the first tuning loop

Recommended first backend:

- `diamond`

Reason:

- the current `Phase 1B` and `eco_w3110` exact loop are already validated with
  `diamond`

### Work Unit 1. Define The First Search Space

Status:

- completed at planning level

The first grid should be narrow, not exhaustive.

For `diamond`:

- `template_diamond_hit_weight`
- `template_bbh_template_weight`
- `template_coarse_weight`
- `template_rerank_topn`

Derived complements:

- `template_diamond_identity_weight = 1 - template_diamond_hit_weight`
- `template_bbh_target_weight = 1 - template_bbh_template_weight`
- `template_rerank_weight = 1 - template_coarse_weight`

For `skani`, replace `template_diamond_hit_weight` with `template_ani_weight`.

### Work Unit 2. Build The Tuning Orchestrator

Status:

- completed at initial implementation level

Target script:

- `scripts/tune_template_weights.py`

Required behavior:

- generate a backend-specific candidate grid
- run full reconstruction for selected benchmark cases
- collect recommendation reports
- evaluate against reference models when available
- separate exact-anchor and approximate-secondary evidence in the summary
- write a machine-readable tuning summary
- write a sortable TSV table

### Work Unit 3. Define The Aggregate Objective

Status:

- completed at initial implementation level

First objective:

- `primary_exact_reaction_f1_mean`

Supporting summary fields:

- secondary approximate reaction F1 mean
- evaluated reference-case count
- reaction precision/recall means
- expected-template hit rates
- expected-neighbor hit rates
- alias-gene F1 mean, when available

### Work Unit 4. Run A Narrow Exact-Case Pilot

Status:

- completed for the first 4-config `eco_w3110` pilot

Recommended first pilot:

- case set: `eco_w3110`
- backend: `diamond`
- narrow grid only

Reason:

- this is the first admitted exact-reference case
- it minimizes interpretation noise while the runner itself is being validated

Recommended first command:

```bash
conda activate gmsm
python scripts/tune_template_weights.py \
  --manifest benchmarks/phase3_tuning_manifest.yaml \
  --template-backend diamond \
  --template-diamond-hit-weights 0.75,0.85,0.95 \
  --template-bbh-template-weights 0.5,0.7,0.9 \
  --template-coarse-weights 0.4,0.6,0.8 \
  --template-rerank-topn-values 1,3 \
  --label phase3-narrow-diamond-eco_w3110
```

Observed outcome from the first executed pilot:

- the runner completed successfully
- the tested `eco_w3110` 4-config pilot produced identical top-level reaction
  objective values across all four settings

Reference:

- [phase3_eco_w3110_pilot_report.md](phase3_eco_w3110_pilot_report.md)

Observed outcome from the first tiered multi-case pilot:

- the exact+approximate tier split now runs successfully
- but the three-case pilot still produced identical aggregate objective values
  across all four tested settings

Reference:

- [phase3_tiered_multi_case_pilot_report.md](phase3_tiered_multi_case_pilot_report.md)

### Work Unit 5. Expand Only After The Pilot Is Stable

Status:

- pending

Expansion order:

1. exact-case reruns with reviewed settings
2. additional admitted exact cases, if available
3. approximate-reference cases as secondary evidence

Do **not** expand approximate references into the primary objective too early.

## First Failure Modes To Watch

- using `auto` backend and accidentally tuning fallback behavior
- using too wide a grid before the runner is operationally stable
- treating raw gene overlap as an optimization target
- comparing approximate-reference cases as if they were exact cases

## Current Recommendation

The first real `Phase 3` loop should be treated like a reactor shakedown run:

- control the manipulated variables tightly
- keep the objective simple
- expand complexity only after the measurement loop is trustworthy

Current implication after the tiered multi-case pilot:

- the measurement loop is now trustworthy enough
- the next bottleneck is benchmark discriminative power
- the next upgrade should therefore be `Phase 1C` boundary-case curation rather
  than a much larger same-species grid sweep
- boundary-screening cases can now run in recommendation-only mode inside
  `scripts/tune_template_weights.py`
- the first operational boundary-only pilot is recorded in
  [phase1c_boundary_screening_pilot_report.md](phase1c_boundary_screening_pilot_report.md)
- a later integrated pilot now shows the desired pattern:
  exact/approximate anchors remain stable while a promoted boundary case can
  still switch under stressed settings
- see [phase3_phase1c_integrated_pilot_report.md](phase3_phase1c_integrated_pilot_report.md)
- later local-search reports show that, inside the current preferred family,
  both the tested diamond-hit band and the tested BBH-balance band are flat
- see [phase3_local_search_diamondhit_report.md](phase3_local_search_diamondhit_report.md)
  and [phase3_local_search_bbh_report.md](phase3_local_search_bbh_report.md)
- the later objective-expansion pass widened the secondary-evidence tier with
  `bsu_ncib3610`, improving coverage without changing the main bottleneck
- see [phase3_objective_expansion_report.md](phase3_objective_expansion_report.md)
- a reserve-boundary probe then showed that `firmi_blich_dsm13` is biologically
  acceptable but still weak as a ranking discriminator
- see [phase3_objective_expansion_change_log.md](phase3_objective_expansion_change_log.md)
- round-2 external boundary curation then added multiple new actinobacterial
  leverage cases and strengthened integrated screening power
- see [phase3_boundary_round2_intake_report.md](phase3_boundary_round2_intake_report.md)
  and [phase3_round2_integrated_pilot_report.md](phase3_round2_integrated_pilot_report.md)
- round-3 Firmicute-focused curation then added the first clean Firmicute
  leverage case (`firmi_tsac_jwslys485`) that flips from `clj` to `bsu`
  instead of drifting to `eco`
- see [phase3_boundary_round3_probe_report.md](phase3_boundary_round3_probe_report.md)
  and [phase3_round3_integrated_pilot_report.md](phase3_round3_integrated_pilot_report.md)
- after that round-3 upgrade, the local-search rerun on the stronger manifest
  showed that both the safe diamond-hit band and the safe BBH band remain flat
- see [phase3_round3_local_search_diamondhit_report.md](phase3_round3_local_search_diamondhit_report.md)
  and [phase3_round3_local_search_bbh_report.md](phase3_round3_local_search_bbh_report.md)
- that outward search has now been executed in two passes
- see [phase3_round3_diamondhit_degradation_boundary_report.md](phase3_round3_diamondhit_degradation_boundary_report.md)
- the safe region now extends through `template_diamond_hit_weight = 0.50`
- refinement then showed that the first practical degradation begins at `0.55`
- so the next best move is no longer more search on this axis but stronger
  exact-reference coverage for the primary objective
- a provisional `bsu_py79` primary-exact pilot has now been executed on the
  round-3 manifest, using the new exact-candidate Bacillus reference
- that pilot still left both the local diamond-hit band and the local BBH band
  completely flat
- see [phase3_provisional_bsu_py79_primary_exact_report.md](phase3_provisional_bsu_py79_primary_exact_report.md)
- so the next best move is now deployment-aware validation rather than more
  safe-family micro-tuning
