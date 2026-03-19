# Phase 3 Objective Expansion Execution Plan

## Purpose

This note records the next move after the first local search around the stable
`Phase 3 + Phase 1C` family turned out to be flat.

The current bottleneck is no longer:

- runner plumbing
- boundary-screening support
- micro-search around `template_diamond_hit_weight`

The current bottleneck is:

- objective coverage

In particular, the tuning loop still depends on:

- one `primary_exact` E2E case
- two `secondary_approximate` E2E cases
- three `boundary_screening` recommendation-only cases

That is enough to reject clearly bad settings, but still narrow enough that
nearby settings can look effectively identical.

## Goal

Add one more controlled `secondary_approximate` case before widening the search
grid again.

The preferred candidate is:

- `bsu_ncib3610`

## Why `bsu_ncib3610` Is The Right Next Unit

It is not the highest-fidelity case in the project.

That remains `eco_w3110`.

But it is the best next expansion unit because:

- its query asset already exists and passes recommendation benchmarking
- its biological interpretation is still clear: same species, harder than
  `bsu_py79`
- it costs much less than sourcing a new exact same-strain published GEM
- it broadens the approximate Bacillus axis without mixing in a new soft-label
  taxonomic regime

This is a controlled expansion, not a policy change.

`bsu_ncib3610` should stay:

- `secondary_approximate`

It should not be promoted into:

- `primary_exact`

## Divide-And-Conquer Strategy

### Work Unit 1. Stage The Approximate Reference

Completion criteria:

- `benchmarks/reference_models/bsu_ncib3610/model.xml` exists
- `SOURCE.md` explains why the case is admitted only as secondary evidence

### Work Unit 2. Build An Expanded Tuning Manifest

Completion criteria:

- a runnable manifest exists that adds `bsu_ncib3610` while preserving the
  current exact and boundary tiers

Proposed file:

- `benchmarks/phase3_tuning_manifest.phase1c.expanded.yaml`

### Work Unit 3. Run A Narrow Validation Pilot

Compare at least:

- one stable preferred configuration
- one previously stressed configuration that already harmed a promoted
  boundary case

Why:

- if the new approximate case is stable under the preferred family, it can be
  kept as extra coverage
- if it also reacts to stressed settings, then it adds objective discrimination

### Work Unit 4. Decide The Next Bottleneck

Possible outcomes:

1. the new case stays flat
   - conclusion: approximate coverage improved, but the next bottleneck is
     still benchmark discrimination
2. the new case differentiates stressed settings
   - conclusion: the widened objective should become the new standard search
     manifest

## Expected Decision Rule

Prefer the expanded manifest if it satisfies both:

- the new approximate case runs reproducibly
- it does not destabilize the existing exact anchor or promoted boundary cases

## Immediate Next Action

1. export the staged `bsu` template reference for `bsu_ncib3610`
2. run a two-configuration expanded pilot
3. document whether objective coverage improved, and whether ranking
   discrimination improved
