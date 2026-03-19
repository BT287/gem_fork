# Phase 1B First Batch Execution Plan

## Purpose

This document breaks the first `Phase 1B` benchmark addition into small,
executable work units.

It is meant to answer:

- what has already been prepared
- what is still blocked
- what should be done next in order

## Current State

Already prepared:

- the recommendation benchmark runner exists
- the current seed manifest exists
- the first five candidate organisms are selected
- the staging directory structure for those five cases is created
- a draft manifest with target paths is prepared
- all five source assets have been downloaded into the staging tree
- all five cases have now passed a recommendation-only benchmark run

Still blocked:

- no Phase 1B first-batch asset blocker remains at the recommendation-only stage
- future work should move from recommendation-only benchmarking to richer evaluation, not more intake debugging

## Work Breakdown

### Work Unit 0. Freeze The Working Environment

Status:

- completed

Completion criteria:

- use `conda activate gmsm`
- `run_gmsm.py -h` works
- benchmark runner unit tests pass

### Work Unit 1. Create A Stable Staging Layout

Status:

- completed

Output location:

- `benchmarks/query_assets/phase1b_first_batch/`

Completion criteria:

- one directory per benchmark case
- one provenance note per case
- standard target filenames agreed in advance

### Work Unit 2. Download Source Assets

Status:

- completed for all five first-batch cases

Per-case target:

- preferably one parseable GenBank file as `input.gbk`
- optional EC companion file only if later needed

Completion criteria:

- local file exists
- source accession is recorded
- file belongs to the intended strain / assembly

Helper script:

- `scripts/fetch_phase1b_benchmark_assets.py`

### Work Unit 3. Validate Asset Identity

Status:

- completed for all five first-batch cases

Checks:

- accession and organism name match the case note
- no obvious strain mismatch
- file is parseable by Biopython / `run_gmsm.py`
- if `locus_tag` is missing, the current parser now falls back to `protein_id`, then `gene`

Completion criteria:

- each file passes provenance review
- each file is accepted for benchmark use

### Work Unit 4. Fill The Draft Manifest

Status:

- completed for all five first-batch cases

Target file:

- `benchmarks/phase1b_first_batch_manifest.draft.yaml`

Completion criteria:

- placeholder paths replaced with real local paths
- strict and soft labels are present
- notes remain biologically defensible

### Work Unit 5. Promote Validated Cases Into The Main Benchmark

Status:

- partially completed

Target file:

- `benchmarks/auto_template_benchmark_manifest.yaml`

Promotion rule:

- do not add a case until its local file exists and has been validated
- keep the draft manifest as the richer staging layer, but the validated cases are now promoted

Completion criteria:

- only runnable cases are added
- the main benchmark manifest stays executable

### Work Unit 6. Run The First Batch

Status:

- completed once for the draft batch

Command:

```bash
conda activate gmsm
python scripts/run_auto_template_benchmark.py \
  --manifest benchmarks/phase1b_first_batch_manifest.draft.yaml \
  --label phase1b-first-batch
```

Completion criteria:

- benchmark summary is written
- each failure is diagnosable
- strict and soft hit behavior are visible
- blocked cases are explicitly named and explained

## Per-Case Task Board

### `eco_w3110`

- status: validated-and-promoted
- target template: `eco`
- risk: low
- next action: keep in the main benchmark manifest

### `eco_bw25113`

- status: validated-and-promoted
- target template: `eco`
- risk: low
- next action: keep in the main benchmark manifest

### `bsu_py79`

- status: validated-and-promoted
- target template: `bsu`
- risk: low
- next action: keep in the main benchmark manifest

### `bsu_ncib3610`

- status: validated-and-promoted
- target template: `bsu`
- risk: medium
- next action: keep in the main benchmark manifest and keep provenance note explicit

### `sco_sliv_tk24`

- status: validated-and-promoted
- target template: `sco`
- risk: medium
- next action: keep in the main benchmark manifest with soft-label caution

## Recommended Immediate Next Command

The next useful action is to run the full first batch together whenever you want a clean Phase 1B baseline snapshot.

The main benchmark manifest now contains all five validated first-batch cases.

Suggested command:

```bash
conda activate gmsm
python scripts/run_auto_template_benchmark.py \
  --label phase1b-promoted \
  --case-id eco_w3110 \
  --case-id eco_bw25113 \
  --case-id bsu_py79 \
  --case-id bsu_ncib3610 \
  --case-id sco_sliv_tk24
```
