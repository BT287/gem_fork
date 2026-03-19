# Phase 2 Gene Harmonization Plan

## Purpose

This note turns the `gene metric` blocker in `Phase 2` into concrete work
units.

The central point is:

- raw gene-ID overlap and biologically meaningful gene agreement are not the
  same object

So the first job is not to "improve gene F1" directly.

It is to define a comparison namespace that is less brittle than raw SBML gene
IDs.

## Where The Confusion Happened

The earlier raw metric compared:

- predicted model gene IDs from the GMSM reconstruction output

against:

- reference SBML gene IDs from the admitted reference model

For `eco_w3110`, those namespaces are different:

- predicted model genes mix target-side protein IDs such as `BAA...` / `BAB...`
  and template carryover IDs such as `b0002`
- the W3110 reference model uses IDs such as `Y7U_RS00010`

So raw set overlap was almost zero even though the models were clearly related.

## First Implemented Harmonization Layer

The first implemented layer is intentionally conservative.

It does **not** claim to solve orthology fully.

It uses an alias-based one-to-one matching rule:

1. extract query aliases from the input GenBank
   - `gene`
   - `protein_id`
   - `locus_tag`
   - compact identifier tokens from `note`
2. project template carryover genes through
   `2_blastp_results/temp_target_BBH_dict.txt`
3. extract reference aliases from the SBML gene annotations
   - raw gene ID
   - `refseq_name`
   - `refseq_locus_tag`
   - `refseq_old_locus_tag`
4. connect a predicted gene to a reference gene if their alias sets intersect
5. compute a maximum bipartite matching so that one predicted gene cannot claim
   multiple reference genes

This is a metadata harmonization layer, not yet an orthology engine.

## Why This Is Better Than Raw Overlap

Example:

- predicted gene: `BAB96579.2`
- query GenBank aliases: `BAB96579.2`, `thrA`, `JW0001`, `b0002`
- reference gene: `Y7U_RS00010`
- reference aliases: `Y7U_RS00010`, `thrA`, `Y75_p0002`, `Y75_RS00010`

Raw IDs do not match:

- `BAB96579.2` != `Y7U_RS00010`

But alias overlap shows a biologically plausible match:

- both contain `thrA`

## First Real Result On `eco_w3110`

Report:

- `docs/phase2_eco_w3110_first_case_report.md`

Observed values:

- raw gene overlap:
  - overlap count: `1`
  - precision: `0.000331`
  - recall: `0.000729`
  - F1: `0.000455`
- alias-based harmonized gene overlap:
  - overlap count: `321`
  - precision: `0.106221`
  - recall: `0.233965`
  - F1: `0.146108`

Interpretation:

- the raw metric was dominated by namespace mismatch
- the alias-based metric recovers a real, non-trivial gene-level signal
- but it is still conservative and incomplete

## Work Units

### Work Unit 1. Keep Raw And Harmonized Metrics Separate

Status:

- completed

Reason:

- raw metrics are still useful as a debugging signal
- harmonized metrics should not silently replace them

### Work Unit 2. Implement A First Alias-Based Matching Layer

Status:

- completed

Implementation:

- `scripts/evaluate_reconstruction_quality.py`

Current strategy name:

- `query_alias_intersection_max_matching`

### Work Unit 3. Validate On One Real Case

Status:

- completed

Validated case:

- `eco_w3110`

### Work Unit 4. Define The Next Upgrade Path

Status:

- pending

Next upgrade target:

- move from alias matching to stronger orthology-aware gene comparison

Candidate directions:

1. explicit target-to-reference crosswalk files for admitted benchmark cases
2. reference-specific locus-tag crosswalk recovery when the query GenBank
   exposes old locus tags
3. stricter BBH-derived one-to-one gene projection for cases where protein IDs
   and locus tags are well behaved

Current bridge scaffold:

- `docs/phase2_gene_crosswalk_candidate_plan.md`
- `scripts/export_gene_crosswalk_candidates.py`

## Current Recommendation

For now:

- keep `reaction_metrics` as the most trustworthy early `Phase 2` objective
- keep `gene_metrics` as raw-diagnostic output
- use `gene_alias_metrics` as the first non-trivial harmonized gene signal

Do **not** tune final weights against raw gene overlap alone.
