# Phase 3 / Phase 1C Change Log

## Purpose

This note is the compact progress log for the recent auto-template parameter
tuning upgrades.

It answers two questions:

1. what changed in the code and benchmark workflow?
2. what capability or performance improved because of those changes?

## Summary

The main outcome is:

- the tuning workflow is no longer limited to flat same-species validation
- the benchmark now contains a usable boundary-screening lane
- at least one promoted boundary case can switch under stressed settings while
  the exact-anchor E2E objective stays unchanged

That means the project now has a practical way to reject biologically worse
weight settings even when the exact reaction-F1 objective is unchanged.

## Change Group 1. Tiered Tuning Runner

What changed:

- `scripts/tune_template_weights.py` now separates:
  - `primary_exact`
  - `secondary_approximate`
  - `boundary_screening`
- result summaries now report tier-specific screening metrics
- ranking can still prioritize the exact-anchor objective while keeping
  approximate and boundary behavior visible

Implementation gain:

- one runner can now support E2E exact scoring, approximate secondary evidence,
  and cheap recommendation-only screens in the same framework

Why this matters:

- before this, the loop could only tell us whether exact or same-species cases
  stayed good
- now it can also tell us whether a setting breaks biologically interpretable
  boundary cases

## Change Group 2. Approximate Secondary-Evidence Layer

What changed:

- local SBML references were staged for `eco_bw25113` and `bsu_py79`
- `benchmarks/phase3_tuning_manifest.yaml` was added to separate exact and
  approximate evidence
- `benchmarks/no_ec_override.tsv` was added to suppress embedded GenBank EC
  annotations during offline tuning runs

Implementation gain:

- approximate-reference cases can now be evaluated reproducibly without forcing
  them into the primary objective

Performance or measurement gain:

- the tiered multi-case pilot confirmed:
  - `primary_exact_reaction_f1_mean = 0.912203`
  - `secondary_approximate_reaction_f1_mean = 0.993204`
- this preserved useful secondary signal without contaminating the exact-anchor
  objective

## Change Group 3. Boundary-Screening Execution Path

What changed:

- `boundary_screening` cases now run with
  `--template-recommendation-only`
- this path was added to the tuning runner and covered by tests

Implementation gain:

- harder benchmark cases can now be iterated without paying full reconstruction
  cost

Operational gain:

- boundary-only pilots now complete in recommendation mode in a few seconds per
  case rather than requiring E2E reconstruction
- this lowers the cost of candidate intake and benchmark debugging

## Change Group 4. Non-Legacy Phase 1C Candidate Intake

What changed:

- a new shortlist of four non-legacy boundary candidates was curated
- download automation was added with
  `scripts/fetch_phase1c_boundary_assets.py`
- the staged candidates were smoke-tested in recommendation-only mode

Candidates staged:

- `actino_cglu_atcc13032`
- `clj_cauto_dsm10061`
- `firmi_blich_dsm13`
- `sco_sven_atcc10712`

Implementation gain:

- `Phase 1C` is no longer blocked on weak legacy `Streptomyces collinus`
  scaffolds
- candidate intake is now reproducible and scriptable

Measurement gain:

- all four new candidates parsed successfully
- smoke intake benchmark:
  - `top1_expected_template_hit_rate = 1.0`
  - `top1_expected_neighbor_hit_rate = 1.0`
  - `failed_case_count = 0`

## Change Group 5. Promoted Boundary Set

What changed:

- three candidates were promoted into the runnable boundary manifest:
  - `actino_cglu_atcc13032`
  - `clj_cauto_dsm10061`
  - `sco_sven_atcc10712`
- `firmi_blich_dsm13` was retained as reserve only

Why these three were promoted:

- each one produced the intended strict label
- each one also exposed an interpretable second-best competitor

Capability gain:

- the benchmark now contains boundary cases with explicit biological
  competition axes:
  - `mtu` vs `sco`
  - `clj` vs `bsu`

## Change Group 6. First Real Boundary Signal

What changed:

- the promoted three-case boundary-only pilot was run under stressed settings

Key result:

- `actino_cglu_atcc13032` switched:
  - stable side: `mtu`
  - stressed side: `sco`

Performance gain:

- this was the first evidence that the benchmark is no longer flat
- the workflow can now detect a ranking change caused by weight variation

## Change Group 7. Integrated Phase 3 + Phase 1C Pilot

What changed:

- promoted boundary cases were merged back into the tiered Phase 3 manifest
- a two-config integrated pilot compared:
  - stable config family
  - stressed config family

Key result:

- exact anchor stayed unchanged:
  - `eco_w3110 -> eco`
  - `primary_exact_reaction_f1_mean = 0.912203`
- approximate secondary evidence stayed unchanged:
  - `eco_bw25113 -> eco`
  - `bsu_py79 -> bsu`
  - `secondary_approximate_reaction_f1_mean = 0.993204`
- one boundary case switched:
  - `actino_cglu_atcc13032 : mtu -> sco`

Why this is important:

- before this, different settings often looked identical
- now two settings can be separated even when the exact E2E objective is tied

Practical screening gain:

- stable config family:
  - boundary `top1_expected_template_hit_rate = 1.0`
- stressed config family:
  - boundary `top1_expected_template_hit_rate = 0.666667`

So the tuning loop now has an actionable rejection rule:

- keep settings that preserve exact-anchor quality and boundary strict labels
- reject settings that preserve exact F1 but degrade promoted boundary cases

## Net Effect

Before these changes:

- the workflow mostly answered:
  - "does the system still work on easy cases?"

After these changes:

- the workflow can now answer:
  - "does a weight setting keep exact-anchor E2E quality while also preserving
    biologically better behavior on harder boundary cases?"

That is a qualitative upgrade in tuning capability, not just an incremental
code cleanup.

## Reference Files

- `docs/phase1c_boundary_candidate_shortlist.md`
- `docs/phase1c_boundary_candidate_intake_report.md`
- `docs/phase1c_boundary_screening_pilot_report.md`
- `docs/phase3_phase1c_integrated_pilot_report.md`
