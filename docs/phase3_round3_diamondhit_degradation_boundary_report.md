# Phase 3 Round 3 Degradation-Boundary Report: Diamond-Hit Weight

## Purpose

This note records the first outward search after the round-3 local safe band
was shown to be flat.

The question was no longer:

- which setting is best inside the already-safe local band?

The question became:

- where does the current safe region stop?
- which benchmark tier fails first as `template_diamond_hit_weight` grows?

## Fixed Controls

The following structural settings were held fixed:

- `template_backend = diamond`
- `template_bbh_template_weight = 0.5`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`

Manifest:

- `benchmarks/phase3_tuning_manifest.phase1c.round3.yaml`

Reference safe-band result:

- [phase3_round3_local_search_diamondhit_report.md](phase3_round3_local_search_diamondhit_report.md)

## Divide-And-Conquer Search Design

### Pass 1. Coarse Outward Sweep

Search:

- `template_diamond_hit_weight in {0.15, 0.20, 0.30, 0.50}`

Output:

- `benchmark-results/phase3-round3-diamondhit-boundary-search/`

Purpose:

- test whether degradation begins immediately above the old safe band
- cheaply reject the possibility that the transition starts near `0.15`

### Pass 2. Bracket Search Inside The Remaining Unknown Region

Search:

- `template_diamond_hit_weight in {0.65, 0.75, 0.85}`

Output:

- `benchmark-results/phase3-round3-diamondhit-boundary-bracket2/`

Purpose:

- locate the first real degradation point between the still-safe `0.50` and
  the previously known stressed `0.95`

## Main Results

### Pass 1 Result: Still Safe Through `0.50`

For every tested value in `{0.15, 0.20, 0.30, 0.50}`:

- `primary_exact_reaction_f1_mean = 0.912203`
- `secondary_approximate_reaction_f1_mean = 0.995336`
- boundary `top1_expected_template_hit_rate = 1.0`
- boundary `top1_expected_neighbor_hit_rate = 1.0`

Interpretation:

- the old safe region extends much farther than `0.10`
- no degradation begins before `0.50`

### Pass 2 Result: First Degradation Begins At `0.65`

For all tested values in `{0.65, 0.75, 0.85}`:

- `primary_exact_reaction_f1_mean = 0.912203`
- `secondary_approximate_reaction_f1_mean = 0.995336`
- boundary `top1_expected_neighbor_hit_rate = 1.0`

But boundary strict hits now drop monotonically:

- `0.65 -> 0.75`
- `0.75 -> 0.625`
- `0.85 -> 0.50`

This means:

- the degradation starts in the `boundary_screening` tier first
- exact and approximate E2E anchors remain insensitive across the tested range

### Pass 3 Result: Refinement Confirms A Practical Upper Safe Bound At `0.50`

Refinement search:

- `template_diamond_hit_weight in {0.55, 0.60, 0.65}`

Output:

- `benchmark-results/phase3-round3-diamondhit-threshold-refine/`

Observed values:

- `0.55 -> boundary strict hit rate 0.875`
- `0.60 -> boundary strict hit rate 0.75`
- `0.65 -> boundary strict hit rate 0.75`

Again:

- `primary_exact_reaction_f1_mean = 0.912203`
- `secondary_approximate_reaction_f1_mean = 0.995336`
- boundary `top1_expected_neighbor_hit_rate = 1.0`

Interpretation:

- the first strict-label degradation already begins at `0.55`
- the first practical upper safe bound for perfect promoted-boundary behavior
  is therefore `0.50`

## Case-Level Transition Pattern

### Safe Reference

At `0.50`, all promoted boundary cases still match the stable family:

- `actino_cglu_atcc13032 -> mtu`
- `clj_cauto_dsm10061 -> clj`
- `sco_sven_atcc10712 -> sco`
- `actino_rjost_rha1 -> mtu`
- `actino_nfar_ifm10152 -> mtu`
- `actino_sery_nrrl23338 -> sco`
- `firmi_cbei_ncimb8052 -> clj`
- `firmi_tsac_jwslys485 -> clj`

### First Failures At `0.65`

The first strict-label degradations are actinobacterial:

- `actino_cglu_atcc13032: mtu -> sco`
- `actino_rjost_rha1: mtu -> sco`

### Refinement Clarifies The Order Of First Failure

At `0.55`, only one promoted boundary case fails:

- `actino_rjost_rha1: mtu -> sco`

At `0.60`, the second actinobacterial case joins it:

- `actino_cglu_atcc13032: mtu -> sco`

### Additional Failure At `0.75`

One more actinobacterial leverage case flips:

- `actino_nfar_ifm10152: mtu -> sco`

### Additional Failure At `0.85`

The Firmicute leverage tier begins to degrade:

- `firmi_tsac_jwslys485: clj -> bsu`

### Comparison To The Earlier Stressed Case

At `0.95`, the earlier stressed pilot had:

- boundary strict hit rate `0.375`
- `firmi_cbei_ncimb8052: clj -> eco`

So the full degradation ladder is now clearer:

1. actinobacterial boundary cases fail first
2. then the clean Firmicute leverage case fails
3. only later does the worse Firmicute drift toward `eco`

## Interpretation

The safe band is no longer just "somewhere below `0.95`."

We can now state a stronger claim:

- `template_diamond_hit_weight <= 0.50` is still operationally safe on the
  current round-3 integrated benchmark
- the first observed degradation begins between `0.50` and `0.65`
- the earliest failures are biologically interpretable actinobacterial
  boundary cases, not exact-reference anchors

That is a good sign.

It means the benchmark is now sensitive in the intended order:

1. rejection screen fails first
2. support evidence stays stable
3. exact E2E anchor stays stable longest

## Decision

Use the following as the current working policy:

- keep `diamond` as the backend
- keep `template_coarse_weight = 0.95`
- keep `template_rerank_topn = 3`
- treat `template_diamond_hit_weight <= 0.50` as the practical safe upper
  region
- avoid `template_diamond_hit_weight >= 0.55` for the default family

## Recommended Next Step

Do **not** spend more search budget on this axis for now.

The next informative move for the overall parameter-estimation workflow is:

- expand exact-reference E2E coverage

Reason:

- the `diamond_hit_weight` axis now has a practical guardrail
- the main primary objective is still based on very limited exact coverage
- further optimization needs more informative `primary_exact` cases, not more
  resolution on an already-bounded axis
