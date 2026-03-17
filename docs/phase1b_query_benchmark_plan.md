# Phase 1B Query Benchmark Plan

## Purpose

This document is the immediate implementation plan for the next session.

Its scope is narrow:

- do **not** expand the template panel
- do **not** start downstream E2E scoring yet
- do **not** start weight tuning yet

The goal is to strengthen the benchmark by adding **non-template query strains** that should still map to one of the existing 10 curated templates.

For the concrete first-batch candidates and execution breakdown, see:

- [phase1b_first_batch_candidates.md](phase1b_first_batch_candidates.md)
- [phase1b_first_batch_execution_plan.md](phase1b_first_batch_execution_plan.md)

## Why This Is The Right Next Step

Current status:

- score parameterization is implemented
- recommendation benchmark scaffold is implemented
- self-retrieval sanity cases are implemented

Current bottleneck:

- the benchmark still does not test biologically meaningful generalization

Therefore, the highest-value next step is:

- add same-species / same-clade non-template query cases

This is the shortest path from "sanity scaffold" to "useful biological benchmark."

## What We Want To Prove In Phase 1B

We want to test whether a query strain that is **not itself a template** is still mapped to the biologically appropriate existing curated template.

Examples:

- non-template *E. coli* strain -> `eco`
- non-template *B. subtilis* strain -> `bsu`
- non-template *Streptomyces* strain -> `sco`

This gives us a much better signal than self-retrieval alone.

## Scope

### In Scope

- add curated query benchmark cases
- keep using recommendation-only benchmark mode
- record `expected_template`
- record `expected_taxonomic_neighbors`
- document provenance and biological rationale per case

### Out Of Scope

- adding new templates
- claiming biological optimality from a tiny benchmark
- downstream reconstruction-quality scoring
- confidence calibration

## Immediate Deliverables

### 1. Benchmark Case Intake Rule

Each new query case should define:

- `case_id`
- `query_input`
- `ec_file`
- `reference_model`
- `expected_template`
- `expected_taxonomic_neighbors`
- `exclude_templates`
- `tags`
- `notes`

Additional recommended metadata to add if available:

- `source_accession`
- `assembly_id`
- `organism_name`
- `strain_name`
- `provenance`

### 2. Candidate Query Priority

Priority order for the next implementation block:

1. `eco`-mapped non-template *E. coli* strains
2. `bsu`-mapped non-template *B. subtilis* strains
3. `sco`-mapped non-template *Streptomyces* strains

Reason:

- these are biologically intuitive
- expected-template rationale is relatively easy to explain
- they give immediate benchmark diversity without changing the template panel

### 3. Asset Validity Rule

A query case is admissible only if:

- genome file is reproducible and clearly identified
- proteome/genome belong to the same strain or assembly
- expected-template rationale is explicit
- provenance is documented

If any of these are unclear:

- do not add the case yet

## Recommended File Changes For The Next Session

Primary files to touch:

- `benchmarks/auto_template_benchmark_manifest.yaml`
- `scripts/run_auto_template_benchmark.py`
- `gmsm/tests/test_auto_template_benchmark_runner.py`

Optional supporting additions:

- `benchmarks/query_assets/` if query benchmark files are vendored into the repo
- a short provenance note under `docs/` if multiple cases are added at once

## Exact Divide And Conquer Steps

### Step 1. Pick A Tiny Curated First Batch

Target:

- `3-6` same-species or same-clade non-template query cases

Completion criteria:

- each case has a defensible `expected_template`
- each case has usable input files

### Step 2. Normalize File Layout

Choose one consistent way to store query benchmark assets.

Preferred options:

- keep small benchmark assets under a dedicated benchmark asset directory in the repo
- or point the manifest to stable local paths if the repo is intentionally not tracking the files

Completion criteria:

- the manifest paths are reproducible for the next run

### Step 3. Extend The Manifest

For each selected case:

- add `expected_template`
- add `expected_taxonomic_neighbors`
- add `tags`
- add a one-line biological rationale in `notes`

Completion criteria:

- the manifest remains machine-readable
- strict and soft labels are both present when appropriate

### Step 4. Extend Summary Logic Only If Needed

The current runner already records:

- strict expected-template hit
- soft expected-neighbor hit
- aggregate rates

Only change the runner if the new cases require extra metadata in the benchmark summary.

Completion criteria:

- avoid unnecessary benchmark-runner refactors

### Step 5. Run And Review

Run:

```bash
python scripts/run_auto_template_benchmark.py --label phase1b-first-batch
```

Review:

- top-1 expected-template hit rate
- top-k expected-template hit rate
- failures by case
- suspicious cases where the recommendation is biologically arguable but not identical to the strict label

Completion criteria:

- benchmark summary is generated
- failures are diagnosable from logs and metadata

## Acceptance Criteria For Phase 1B

- benchmark includes at least a few non-template query strains
- each case has explicit provenance and expected-template rationale
- benchmark summary reports strict and soft hit behavior
- at least one same-species / same-clade non-template case runs successfully end-to-end through recommendation-only mode

## Expected Risks

### 1. Asset Mismatch

- genome and proteome may come from different strains or assemblies

Mitigation:

- record accession / provenance before adding the case

### 2. Overconfident Labels

- some cases may have more than one biologically plausible template

Mitigation:

- keep both `expected_template` and `expected_taxonomic_neighbors`

### 3. Benchmark Pollution

- adding low-quality or poorly documented cases too early can make later tuning noisy

Mitigation:

- prefer fewer, cleaner cases over many weak cases

## First Command To Run Tomorrow

If new query assets are already prepared:

```bash
python scripts/run_auto_template_benchmark.py --label phase1b-baseline
```

If new query assets are **not** yet prepared:

- do not start tuning
- first build the curated first batch of non-template query cases

## Final Instruction For The Next Session

The next session should not jump to Phase 2 or Phase 3 until Phase 1B produces a benchmark set that is biologically more meaningful than self-retrieval alone.
