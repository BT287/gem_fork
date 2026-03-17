# Phase 3 Boundary Round 2 Intake Report

## Purpose

This note records the first real intake pass for the new round-2 boundary
candidate shortlist.

The practical questions were:

- can the new candidates be staged reproducibly?
- do they parse cleanly in recommendation-only mode?
- which candidates actually show the intended panel competition structure?

## Intake Scope

The shortlisted cases were:

- `actino_rjost_rha1`
- `actino_nfar_ifm10152`
- `actino_sery_nrrl23338`
- `firmi_cbei_ncimb8052`
- `firmi_gkau_hta426`
- `firmi_bhal_c125`

Reference shortlist:

- `docs/phase3_boundary_round2_candidate_shortlist.md`

## What Completed Successfully

- all six query assets were staged under
  `benchmarks/query_assets/phase3_boundary_round2_candidates/`
- all six parsed successfully in recommendation-only benchmark mode
- no case failed during the intake smoke benchmark

Runnable file:

- `benchmarks/phase3_boundary_round2_manifest.draft.yaml`

Output directory:

- `benchmark-results/phase3-boundary-round2-intake-all6/`

## Aggregate Intake Result

The recommendation-only smoke benchmark over all six candidates produced:

- `top1_expected_template_hit_rate = 1.0`
- `top1_expected_neighbor_hit_rate = 1.0`
- `failed_case_count = 0`

This means the shortlist is operationally clean.

But the more important question is:

- do the candidates create the intended competition axis?

## Per-Case Interpretation

### 1. `actino_rjost_rha1`

- recommended template: `mtu`
- top-3 competitors: `mtu`, `sco`, `eco`
- interpretation:
  - strong promoted candidate
  - the intended `mtu` vs `sco` actinobacterial axis is present
  - the `mtu`-`sco` score gap is not excessively large, so this is a good probe

### 2. `actino_nfar_ifm10152`

- recommended template: `mtu`
- top-3 competitors: `mtu`, `sco`, `eco`
- interpretation:
  - strong promoted candidate
  - this is a second valid `mtu`-side actinobacterial probe
  - useful because it is taxonomically distinct from the Rhodococcus case

### 3. `actino_sery_nrrl23338`

- recommended template: `sco`
- top-3 competitors: `sco`, `mtu`, `eco`
- interpretation:
  - strong promoted candidate
  - this gives a clean `sco`-side counterpart to the `mtu`-side actinobacterial
    probes
  - the very small `sco`-vs-`mtu` margin makes it especially interesting for
    stressed-setting probes

### 4. `firmi_cbei_ncimb8052`

- recommended template: `clj`
- top-3 competitors: `clj`, `bsu`, `eco`
- interpretation:
  - strong promoted candidate
  - this is the cleanest new Firmicute candidate in the round-2 shortlist
  - it should be probed because it provides the intended `clj` vs `bsu` axis

### 5. `firmi_gkau_hta426`

- recommended template: `bsu`
- top-3 competitors: `bsu`, `sco`, `eco`
- interpretation:
  - operationally valid but not promoted
  - it did not produce the intended `bsu` vs `clj` competition structure
  - keep as reserve only if later evidence suggests the Firmicute axis should be
    broadened beyond the current clostridial framing

### 6. `firmi_bhal_c125`

- recommended template: `bsu`
- top-3 competitors: `bsu`, `sco`, `eco`
- interpretation:
  - operationally valid but not promoted
  - like the Geobacillus case, it failed to recover `clj` as the soft-neighbor
    competitor
  - this is useful negative evidence, but it is not a good next boundary probe

## Promotion Decision

Promote immediately:

- `actino_rjost_rha1`
- `actino_nfar_ifm10152`
- `actino_sery_nrrl23338`
- `firmi_cbei_ncimb8052`

Keep as reserve / negative evidence:

- `firmi_gkau_hta426`
- `firmi_bhal_c125`

Reason:

- the promoted four each show the intended strict label plus an interpretable
  second-best competitor inside the panel
- the two rejected Firmicute probes stayed biologically plausible, but their
  competitor structure does not serve the current `clj`-vs-`bsu` objective

## Immediate Next Step

Run a stable-vs-stressed boundary-only probe on the promoted four-case set.

If at least one newly promoted case flips while the others remain stable, that
case becomes a strong candidate for promotion into the standard `Phase 3`
screening manifest.
