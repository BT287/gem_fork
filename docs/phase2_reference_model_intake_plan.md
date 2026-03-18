# Phase 2 Reference Model Intake Plan

## Purpose

This note turns the `Phase 2` reference-model bottleneck into concrete work
units.

Current execution report:

- `docs/phase2_eco_w3110_first_case_report.md`
- `docs/phase2_gene_harmonization_plan.md`

The key decision is:

- do not treat all five `Phase 1B` benchmark cases as equally ready for E2E
  evaluation

Instead, classify each case by how trustworthy its current reference-model
mapping is.

## Why This Needs A Separate Intake Step

`reference_model` is not just another metadata field.

It defines the object against which later reaction and gene metrics are
computed.

So a weak reference mapping can create a misleading optimization target.

Example:

- `eco_w3110` -> BiGG `iEC1372_W3110`
  This is an exact same-strain mapping, so reaction/gene overlap is a
  defensible first E2E target.
- `eco_bw25113` -> BiGG `iML1515`
  This is only a same-lineage approximation because `iML1515` is MG1655, not
  BW25113. The score is still informative, but it should not be treated as the
  same type of signal as the exact W3110 case.

This is analogous to benchmarking a reactor model:

- exact geometry + exact feed = strong validation target
- similar geometry + similar feed = useful sensitivity check
- vaguely related setup = exploratory only

## Status Labels

Use these labels when staging `benchmarks/reference_models/<case_id>/SOURCE.md`.

- `admitted-exact`
  The reference strain matches the query strain closely enough to use for
  primary E2E evaluation.
- `candidate-exact-reconstructed`
  The reference strain matches the query strain and can be reconstructed from a
  reproducible public source, but the source policy is not yet strong enough to
  promote it directly into the primary exact objective.
- `candidate-approximate`
  The reference is biologically related and may be useful later, but should not
  be the first tuning target.
- `pending-source`
  No stable and well-documented SBML source has been admitted yet.

## Case Triage

### Tier 1. Immediate E2E Intake

#### `eco_w3110`

- status: `admitted-exact`
- query organism: *Escherichia coli* str. K-12 substr. W3110
- admitted reference: BiGG `iEC1372_W3110`
- why first:
  - exact same-strain mapping
  - stable BiGG SBML endpoint
  - `eco` auto-template recommendation already validated in `Phase 1B`

### Tier 2. Exact Candidates With Public Reconstruction Paths

#### `bsu_py79`

- status: `candidate-exact-reconstructed`
- exact-source direction:
  - Bacillus pan-model strain reconstruction from the public
    `Bacillus_Pan_Genome_Model` repository
- accession evidence:
  - `GCF_000497485_1` is present in the published `strain_list.mat`
- current local staging:
  - `benchmarks/reference_models/bsu_py79/model_exact_candidate.xml`
- why not admitted yet:
  - this is an automatically reconstructed same-strain model, not yet a
    separately curated trusted GEM
  - reaction overlap is already informative, but source-policy review should
    happen before it enters the primary exact objective

#### `bsu_ncib3610`

- status: `candidate-exact-reconstructed`
- exact-source direction:
  - Bacillus pan-model strain reconstruction from the public
    `Bacillus_Pan_Genome_Model` repository
- accession evidence:
  - `GCF_006088795_1` is present in the published `strain_list.mat`
- current local staging:
  - `benchmarks/reference_models/bsu_ncib3610/model_exact_candidate.xml`
- why not admitted yet:
  - same reason as `bsu_py79`, with the additional interpretation risk that
    NCIB 3610 is already a more divergent Bacillus benchmark case
  - this makes it a useful exact-source candidate, but not yet a safe primary
    anchor

### Tier 3. Useful Later, But Approximate

#### `eco_bw25113`

- status: `candidate-approximate`
- current candidate: BiGG `iML1515`
- why approximate:
  - `iML1515` is MG1655, not BW25113
  - still useful as a K-12 lineage comparison after the exact W3110 loop works

#### `bsu_py79` approximate fallback

- status: `candidate-approximate`
- fallback candidate: BiGG `iYO844`
- why still keep it:
  - useful lineage-level comparison if the pan-model exact candidate is not yet
    admitted

#### `bsu_ncib3610` approximate fallback

- status: `candidate-approximate`
- fallback candidate: BiGG `iYO844`
- why still keep it:
  - useful for controlled `secondary_approximate` tuning runs, even if the
    exact-source candidate remains under review

### Tier 4. Hold Until Source Policy Is Clearer

#### `sco_sliv_tk24`

- status: `pending-source`
- current direction: evaluate whether a stable published `Sco-GEM` /
  `iKS1317`-family SBML should be admitted as a same-clade reference
- why not first:
  - not same-species
  - label is intentionally soft already at the template-selection stage
  - using this case too early would mix intake uncertainty with evaluation
    uncertainty

## Work Units

### Work Unit 1. Admit One Exact Reference

Goal:

- stage exactly one strong `reference_model`

Completion criteria:

- `benchmarks/reference_models/eco_w3110/model.xml` exists
- provenance is documented in `SOURCE.md`
- main benchmark manifest points `eco_w3110.reference_model` at that file

Status:

- completed

### Work Unit 2. Run One Real Primary E2E Case

Goal:

- produce one real reconstructed primary model from a `Phase 1B` query genome

Recommended first command:

```bash
conda activate gmsm
python run_gmsm.py \
  -i benchmarks/query_assets/phase1b_first_batch/eco_w3110/input.gbk \
  --auto-template \
  --template-backend diamond \
  -p -d -c 4 \
  -o benchmark-results/phase2-eco_w3110-primary-e2e/eco_w3110/run-output
```

Completion criteria:

- `3_primary_metabolic_model/model.xml` exists
- template recommendation report exists

Status:

- completed

### Work Unit 3. Evaluate Predicted Vs Reference

Goal:

- compute the first real reaction/gene overlap metrics

Recommended command:

```bash
conda activate gmsm
python scripts/evaluate_reconstruction_quality.py \
  --predicted benchmark-results/phase2-eco_w3110-primary-e2e/eco_w3110/run-output \
  --reference benchmarks/reference_models/eco_w3110/model.xml \
  --model-kind primary \
  --label eco_w3110
```

Completion criteria:

- one machine-readable evaluation JSON exists

Status:

- completed

### Work Unit 4. Expand Only After The Exact Loop Is Stable

Do not immediately promote all approximate references.

Expand in this order:

1. `eco_bw25113`
2. `bsu_py79`
3. `bsu_ncib3610`
4. `sco_sliv_tk24`

Reason:

- exact-case noise should be minimized before approximate-case interpretation is
  added

## Current Recommendation

Use `eco_w3110` as the first true `Phase 2` reference-model case.

Treat the remaining four cases as staged backlog, not as equally mature E2E
targets.

Update after the first `Phase 3` tiered-tuning setup:

- `eco_bw25113` and `bsu_py79` now also have locally staged template-derived
  SBML files for controlled secondary-evidence runs
- they still remain approximate references and should not be merged into the
  main exact-reference objective without an explicit policy change

Update after the Bacillus exact-source intake:

- `bsu_py79` and `bsu_ncib3610` now also have public same-strain
  `candidate-exact-reconstructed` SBML files built from the published Bacillus
  pan-model reconstruction assets
- these candidates are stronger than the old `iYO844` fallback for exactness,
  but they still should not silently become `admitted-exact` until their source
  policy and E2E role are explicitly accepted

Additional note from the first executed case:

- reaction overlap is already useful
- raw gene overlap should remain diagnostic-only
- a first alias-based harmonization layer now exists, but it should still be
  treated as a bridge metric rather than a final orthology-grade target
