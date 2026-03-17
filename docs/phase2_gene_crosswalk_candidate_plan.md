# Phase 2 Gene Crosswalk Candidate Plan

## Purpose

This note defines the next step after the first alias-based gene harmonization
layer.

The goal is not to pretend that we already have a validated orthology map.

The goal is to generate a **reviewable candidate crosswalk** for the admitted
exact-reference cases.

## Why This Step Exists

There is a gap between:

- alias-based matched gene pairs

and:

- a trusted crosswalk that we would be comfortable using as a stronger
  gene-level benchmark target

So the next practical bridge is:

- export candidate predicted-to-reference gene pairs
- inspect them case by case
- only then promote reviewed pairs into a stronger exact-case crosswalk

## Current Tool

Script:

- `scripts/export_gene_crosswalk_candidates.py`

Outputs:

- TSV with:
  - `predicted_gene_id`
  - `reference_gene_id`
  - `shared_alias_count`
  - `shared_aliases`

This output is meant for human review.

## Recommended First Workflow

For the exact `eco_w3110` case:

```bash
conda activate gmsm
python scripts/export_gene_crosswalk_candidates.py \
  --evaluation-json benchmark-results/phase2-eco_w3110-primary-e2e-rerun/eco_w3110/evaluation_harmonized.json \
  --output-tsv benchmark-results/phase2-eco_w3110-primary-e2e-rerun/eco_w3110/gene_crosswalk_candidates.tsv
```

Optional stricter pass:

```bash
conda activate gmsm
python scripts/export_gene_crosswalk_candidates.py \
  --evaluation-json benchmark-results/phase2-eco_w3110-primary-e2e-rerun/eco_w3110/evaluation_harmonized.json \
  --min-shared-aliases 2 \
  --output-tsv benchmark-results/phase2-eco_w3110-primary-e2e-rerun/eco_w3110/gene_crosswalk_candidates_strict.tsv
```

## Work Units

### Work Unit 1. Export Candidate Pairs

Status:

- completed at scaffold level

### Work Unit 2. Review Exact-Case Pairs

Status:

- pending

Review target:

- start with `eco_w3110`

What to inspect:

- whether shared aliases are gene symbols only
- whether the pair looks biologically plausible
- whether repeated transport / complex subunit names create false positives

### Work Unit 3. Define Promotion Criteria

Status:

- pending

Suggested first rule:

- only promote reviewed exact-case pairs into a stronger crosswalk file

### Work Unit 4. Recompute Gene Metrics With Reviewed Crosswalks

Status:

- pending

Goal:

- compare:
  - raw gene metrics
  - alias-based harmonized metrics
  - reviewed-crosswalk metrics

## Current Recommendation

Use candidate crosswalk export as the next manual-review bridge for exact cases.

Do not skip directly from alias overlap to "final gene truth".
