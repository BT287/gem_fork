# Phase 3 Boundary Round 2 Probe Report

## Purpose

This note records the first stable-vs-stressed probe on the newly promoted
round-2 boundary candidates.

The key question was:

- did the new shortlist add real ranking leverage beyond the original boundary
  set?

## Probe Definition

Manifest:

- `benchmarks/phase3_boundary_round2_manifest.promoted.yaml`

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

- `benchmark-results/phase3-boundary-round2-promoted-2cfg/`

## Main Result

The round-2 promoted set added strong new discrimination.

Stable config:

- `actino_rjost_rha1 -> mtu`
- `actino_nfar_ifm10152 -> mtu`
- `actino_sery_nrrl23338 -> sco`
- `firmi_cbei_ncimb8052 -> clj`

Stressed config:

- `actino_rjost_rha1 -> sco`
- `actino_nfar_ifm10152 -> sco`
- `actino_sery_nrrl23338 -> sco`
- `firmi_cbei_ncimb8052 -> eco`

Aggregate screening effect:

- stable `top1_expected_template_hit_rate = 1.0`
- stressed `top1_expected_template_hit_rate = 0.25`

## Interpretation

This is a strong signal.

What clearly improved:

- the benchmark no longer depends only on the original
  `actino_cglu_atcc13032` leverage case
- two new actinobacterial cases (`actino_rjost_rha1`,
  `actino_nfar_ifm10152`) now independently penalize the stressed setting

What remained stable:

- `actino_sery_nrrl23338` stayed on the `sco` side under both settings

This makes it useful as:

- a high-quality actinobacterial control

What remains provisional:

- `firmi_cbei_ncimb8052` does discriminate, but the stressed setting degrades
  it to `eco`, not to the intended `bsu` soft neighbor

So its current value is:

- useful screening evidence

But not yet:

- a clean Firmicute boundary anchor

## Promotion Recommendation

Strong new leverage cases:

- `actino_rjost_rha1`
- `actino_nfar_ifm10152`

Stable control case:

- `actino_sery_nrrl23338`

Provisional case requiring later recheck:

- `firmi_cbei_ncimb8052`

## Immediate Next Step

Integrate the round-2 promoted actinobacterial cases into the full tiered
`Phase 3` manifest and verify that:

- exact and approximate anchors remain stable
- the stressed setting is penalized more strongly than before
