# Phase 1C Boundary-Case Execution Plan

## Purpose

This note defines the next highest-value benchmark upgrade after the tiered
multi-case pilot remained flat.

The key point is:

- same-species and same-lineage cases are good for validation
- they are often too easy for weight tuning

So the next benchmark upgrade should target cases where different weight
settings can plausibly change the selected template.

Current status update:

- `boundary_screening` cases can now run inside the tuning loop in
  recommendation-only mode
- the first operational pilot is recorded in
  `docs/phase1c_boundary_screening_pilot_report.md`
- a new curated shortlist of non-legacy candidates is recorded in
  `docs/phase1c_boundary_candidate_shortlist.md`
- the first real intake and promotion decision are recorded in
  `docs/phase1c_boundary_candidate_intake_report.md`
- current local seeds are useful for plumbing, but one legacy scaffold is not a
  trustworthy biological benchmark

## Why This Is Now The Priority

The latest tiered pilot showed:

- exact-anchor loop works
- approximate-secondary loop works
- offline confounders can be controlled
- but the tested cases remain too easy to separate parameter settings

So the current bottleneck is not software plumbing.

It is benchmark discriminative power.

## What A Useful Boundary Case Looks Like

A case is useful for `Phase 1C` if:

- more than one curated template is biologically plausible
- top-1 vs top-2 ranking could change under different `theta`
- the case is still interpretable enough to explain why a switch happened

Good examples:

- same-genus but more distant species
- same-clade cases with soft labels
- near-boundary organisms where top-2 templates are both defensible

Less useful examples for tuning:

- exact self-retrieval
- very easy same-strain or same-lineage cases that always return the same
  template

## Work Units

### Work Unit 1. Define Candidate Boundary Cases

Goal:

- shortlist `3-5` non-trivial cases with explicit biological rationale

Completion criteria:

- each candidate has:
  - accession / source file provenance
  - expected strict label if available
  - acceptable soft neighbor labels
  - one-sentence explanation of why the case is ambiguous enough to be useful

Current note:

- `sco_sliv_tk24` and `streptomyces_collinus_antismash8` are acceptable
  provisional seeds
- `streptomyces_collinus_refseq_genbank` should stay quarantined as a legacy
  debug artifact unless its biological rationale is repaired

### Work Unit 2. Add Screening-Only Cases First

Goal:

- admit the candidates first as recommendation-screening cases

Reason:

- we do not need exact reference SBML for every boundary case at the start
- recommendation-stage switches alone can already reveal whether the weight
  search has any leverage

### Work Unit 3. Re-Run A Narrow Pilot

Goal:

- combine:
  - one exact anchor
  - current approximate secondary cases
  - new boundary screening cases

Completion criteria:

- at least one candidate configuration changes ranking behavior on one boundary
  case without breaking the exact anchor

### Work Unit 4. Only Then Expand The Search Grid

Goal:

- widen `theta` search only after the benchmark can actually distinguish
  settings

Reason:

- otherwise larger sweeps mostly burn compute on a flat objective surface

## Recommended Immediate Next Command

Start by reviewing the current flat-pilot report:

```bash
conda activate gmsm
sed -n '1,220p' docs/phase3_tiered_multi_case_pilot_report.md
```

Then review the first boundary-screening report:

```bash
sed -n '1,220p' docs/phase1c_boundary_screening_pilot_report.md
```

Then review the new shortlist and draft manifest:

```bash
sed -n '1,260p' docs/phase1c_boundary_candidate_shortlist.md
sed -n '1,220p' benchmarks/phase1c_boundary_manifest.draft.yaml
```

Then identify candidate `Phase 1C` organisms before changing the tuning grid.
