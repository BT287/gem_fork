# Phase 3 Boundary Round 3 Intake Report

## Purpose

This note records the first recommendation-only intake smoke for the
Firmicute-focused round-3 shortlist.

The key question was:

- which new Firmicute candidates are biologically plausible **and**
  benchmark-useful for the intended `clj`-vs-`bsu` competition axis?

## Intake Manifest

Manifest:

- `benchmarks/phase3_boundary_round3_manifest.draft.yaml`

Output:

- `benchmark-results/phase3-boundary-round3-intake-all6/`

## Main Result

All six candidates passed the basic intake smoke.

Aggregate intake metrics:

- `top1_expected_template_hit_rate = 1.0`
- `top1_expected_neighbor_hit_rate = 1.0`
- `failed_case_count = 0`

So:

- parseability is not the bottleneck
- provenance quality is good enough for recommendation-only screening

## Competition Audit

### Clean promoted `clj`-side cases

These three candidates showed the intended top-3 structure:

- `firmi_cace_atcc824`: `clj > bsu > eco`
- `firmi_cthe_atcc27405`: `clj > bsu > eco`
- `firmi_tsac_jwslys485`: `clj > bsu > eco`

Interpretation:

- all three stay on the clostridial side under the default stable family
- all three retain `bsu` as the nearest Firmicute-side competitor
- these are valid promotion candidates for the next stable-vs-stressed probe

### Reserve `bsu`-side cases

These three candidates passed strict labeling but did **not** show the
intended competition axis:

- `firmi_bvelez_fzb42`: `bsu > eco > sco`
- `firmi_bamy_dsm7`: `bsu > eco > sco`
- `firmi_ppol_e681`: `bsu > eco > sco`

Interpretation:

- these are biologically acceptable `bsu`-side screens
- but they do not yet improve the `clj`-vs-`bsu` story
- promoting them now would add coverage but not the intended discrimination

## Promotion Recommendation

Promote:

- `firmi_cace_atcc824`
- `firmi_cthe_atcc27405`
- `firmi_tsac_jwslys485`

Keep as reserve:

- `firmi_bvelez_fzb42`
- `firmi_bamy_dsm7`
- `firmi_ppol_e681`

## Practical Consequence

Round 3 already improves one thing before any stressed probe:

- the project now has multiple new Firmicute candidates with a clean
  `clj > bsu` ordering at the stable setting

But it still does **not** yet prove:

- that any of these cases create a useful stable-vs-stressed split

That must be established in the next probe run.

## Immediate Next Step

Run the stable-vs-stressed probe on the promoted three-case set and admit only
the candidates that actually penalize the stressed setting in an interpretable
way.
