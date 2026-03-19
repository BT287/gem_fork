# Phase 3 Round 3 Integrated Pilot Report

## Purpose

This note records the first integrated pilot after adding the round-3 clean
Firmicute leverage case.

The key question was:

- can we strengthen the stressed-setting penalty further without changing the
  exact and approximate E2E anchors?

## Integrated Manifest

Manifest:

- `benchmarks/phase3_tuning_manifest.phase1c.round3.yaml`

Case policy:

- keep the previous exact and approximate tiers unchanged
- keep the round-2 actinobacterial leverage set
- retain the provisional `firmi_cbei_ncimb8052` case
- add only `firmi_tsac_jwslys485` from round 3

Reason:

- `firmi_tsac_jwslys485` is the only new clean leverage case
- the two new stable controls are documented but not integrated, to avoid
  diluting the screening signal

Compared configurations:

1. stable family:
   - `diamondhit=0.05`
   - `bbh=0.5`
   - `coarse=0.95`
   - `topn=3`
2. stressed family:
   - `diamondhit=0.95`
   - `bbh=0.5`
   - `coarse=0.95`
   - `topn=3`

Output:

- `benchmark-results/phase3-round3-integrated-2cfg/`

## Main Result

The integrated pilot improved discrimination again while keeping the E2E
anchors unchanged.

What stayed unchanged:

- `primary_exact_reaction_f1_mean = 0.912203`
- `secondary_approximate_reaction_f1_mean = 0.995336`

So:

- the exact anchor stayed stable
- the approximate secondary evidence stayed stable

What changed:

- stable overall `top1_expected_template_hit_rate = 1.0`
- stressed overall `top1_expected_template_hit_rate = 0.583333`
- stable boundary `top1_expected_template_hit_rate = 1.0`
- stressed boundary `top1_expected_template_hit_rate = 0.375`

Compared with the previous round-2 integrated pilot:

- earlier stressed overall strict hit was `0.636364`
- round-3 stressed overall strict hit is now `0.583333`

So the new clean Firmicute leverage case increases screening power further.

## Case-Level Interpretation

Stable boundary recommendations:

- `actino_cglu_atcc13032 -> mtu`
- `clj_cauto_dsm10061 -> clj`
- `sco_sven_atcc10712 -> sco`
- `actino_rjost_rha1 -> mtu`
- `actino_nfar_ifm10152 -> mtu`
- `actino_sery_nrrl23338 -> sco`
- `firmi_cbei_ncimb8052 -> clj`
- `firmi_tsac_jwslys485 -> clj`

Stressed boundary recommendations:

- `actino_cglu_atcc13032 -> sco`
- `clj_cauto_dsm10061 -> clj`
- `sco_sven_atcc10712 -> sco`
- `actino_rjost_rha1 -> sco`
- `actino_nfar_ifm10152 -> sco`
- `actino_sery_nrrl23338 -> sco`
- `firmi_cbei_ncimb8052 -> eco`
- `firmi_tsac_jwslys485 -> bsu`

Interpretation:

- the new round-3 case contributes a clean Firmicute-side failure mode
- the exact and approximate tiers remain unaffected
- the benchmark no longer depends on actinobacterial leverage alone

## Practical Consequence

The major benchmark-design bottleneck has shifted again.

The project no longer lacks:

- general boundary screening power
- clean Firmicute leverage entirely

What remains weaker than desired:

- a second clean Bacilli-side leverage case

But that is no longer the immediate blocker for tuning.

## Recommended Next Step

Do not launch another broad curation round immediately.

Instead:

1. rerun the narrow local search with the round-3 integrated manifest
2. test whether the current preferred `diamondhit` neighborhood remains stable
   under the stronger benchmark
3. only return to external curation if the local-search surface remains too
   flat
