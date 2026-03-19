# Phase 3 Boundary Round 2 Curation Plan

## Purpose

This note defines the next curation round after two facts became clear:

1. expanding the approximate tier improved coverage but not discrimination
2. the current reserve Firmicute case did not add new ranking leverage

So the next bottleneck is now explicit:

- find one more genuinely leverage-bearing boundary candidate from outside the
  current reserve pool

## Target Property

A useful next-round boundary case should satisfy all of the following:

- clean provenance and reproducible downloadable genome asset
- strict template label that is still biologically defensible
- at least one strong soft-neighbor competitor inside the current template panel
- not collapse immediately into an already trivial same-species case
- not rely on repo-local legacy scaffolds

## Preferred Competition Axes

### Axis 1. Actinobacteria

Goal:

- create meaningful competition between `mtu` and `sco`

Why:

- this axis already produced the first real leverage signal through
  `actino_cglu_atcc13032`

### Axis 2. Firmicutes

Goal:

- create meaningful competition between `clj` and `bsu`

Why:

- the current promoted `clj_cauto_dsm10061` is stable but not leverage-bearing
- the reserve `firmi_blich_dsm13` stayed biologically acceptable yet still flat

## Divide-And-Conquer Strategy

### Work Unit 1. Candidate Shortlist Refresh

Completion criteria:

- identify `3-5` new non-legacy candidates
- record organism, accession, strict label, soft neighbors, and intended
  competition axis

### Work Unit 2. Download And Parseability Check

Completion criteria:

- all shortlisted cases are staged under `benchmarks/query_assets/`
- each case runs in recommendation-only mode without parser failure

### Work Unit 3. Competition Audit

Completion criteria:

- each candidate is evaluated for top-2 or top-3 competitor structure
- only candidates with interpretable competition are promoted

### Work Unit 4. Narrow Stable-vs-Stressed Probe

Completion criteria:

- compare the current preferred config against one stressed config
- promote only candidates that create additional discrimination without
  destabilizing existing anchors

## Admission Rule

Do **not** promote a new boundary candidate merely because it is biologically
plausible.

Promote it only if it adds one of the following:

- a new stable-vs-stressed ranking split
- a clearer soft-neighbor competition than the current reserve pool

## Immediate Next Action

1. refresh the boundary shortlist from outside the current reserve set
2. keep `actino_cglu_atcc13032` as the current leverage anchor
3. treat `firmi_blich_dsm13` as a documented negative result, not as a failure
