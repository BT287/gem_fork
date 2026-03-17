# Phase 3 Round 2 Integrated Pilot Report

## Purpose

This note records the first full tiered pilot after adding the promoted
round-2 boundary candidates.

The key question was:

- can the new round-2 boundary set increase screening power while leaving the
  exact and approximate E2E anchors unchanged?

## Integrated Manifest

Manifest:

- `benchmarks/phase3_tuning_manifest.phase1c.round2.yaml`

Cases:

- `eco_w3110` as `primary_exact`
- `eco_bw25113`, `bsu_py79`, `bsu_ncib3610` as `secondary_approximate`
- original promoted boundary set:
  - `actino_cglu_atcc13032`
  - `clj_cauto_dsm10061`
  - `sco_sven_atcc10712`
- round-2 added boundary set:
  - `actino_rjost_rha1`
  - `actino_nfar_ifm10152`
  - `actino_sery_nrrl23338`
  - `firmi_cbei_ncimb8052`

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

- `benchmark-results/phase3-round2-integrated-2cfg/`

## Main Result

The integrated pilot shows the exact pattern we wanted.

What stayed unchanged:

- `primary_exact_reaction_f1_mean = 0.912203`
- `secondary_approximate_reaction_f1_mean = 0.995336`

So:

- the exact anchor stayed stable
- the approximate secondary evidence stayed stable

What changed:

- stable config: `top1_expected_template_hit_rate = 1.0`
- stressed config: `top1_expected_template_hit_rate = 0.636364`

This is substantially stronger discrimination than the earlier integrated
round, where the stressed config dropped only to `0.857143`.

## Case-Level Interpretation

Under the stable config:

- all exact, approximate, and boundary cases stayed on their expected strict
  label

Under the stressed config:

- `actino_cglu_atcc13032 -> sco`
- `actino_rjost_rha1 -> sco`
- `actino_nfar_ifm10152 -> sco`
- `firmi_cbei_ncimb8052 -> eco`

While:

- `clj_cauto_dsm10061` stayed `clj`
- `sco_sven_atcc10712` stayed `sco`
- `actino_sery_nrrl23338` stayed `sco`

Interpretation:

- the benchmark now has multiple independent actinobacterial leverage cases
- the stressed setting is penalized more sharply than before
- the new round-2 set improved discriminative power without contaminating the
  E2E objective

## Promotion Recommendation

Promote into the standard working `Phase 3` screening interpretation:

- `actino_rjost_rha1`
- `actino_nfar_ifm10152`
- `actino_sery_nrrl23338`

Keep as provisional:

- `firmi_cbei_ncimb8052`

Reason:

- it adds useful discrimination
- but the stressed-setting failure mode currently degrades to `eco`, which is
  harder to interpret as a clean `clj`-vs-`bsu` boundary story

## Practical Consequence

The current bottleneck is now clearer.

The project no longer lacks:

- boundary screening power in general

It now specifically lacks:

- a second clean Firmicute-side leverage case that fails along the intended
  `clj`-vs-`bsu` axis rather than drifting toward `eco`

## Immediate Next Step

Keep the round-2 actinobacterial cases in the working screening set and shift
the next external curation effort toward a cleaner Firmicute-side round-3
search.
