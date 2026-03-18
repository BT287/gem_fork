# Auto-Template Parameter Estimation Report

## Purpose

This report consolidates the current state of the auto-template parameter
estimation workflow into one place.

It is meant to answer five practical questions:

1. what problem the project is actually trying to solve
2. what strategy was intended originally
3. what has already been implemented and how the logic works
4. where the project currently stands
5. what the next strategy should be

For the shorter briefing version, see
`docs/parameter_tuning_workflow_briefing.md`.

## Executive Summary

The project is **not** trying to learn a supervised classifier that directly
predicts the "correct" template.

The project is trying to estimate a weight vector `theta` for the
auto-template recommendation system such that:

- recommendation behavior remains biologically defensible
- the final reconstructed metabolic model improves end-to-end

So the actual workflow is:

1. parameterize the recommendation score
2. benchmark recommendation behavior
3. benchmark end-to-end reconstruction quality
4. search over a small set of candidate `theta`
5. keep the region that preserves exact-anchor quality while rejecting
   biologically worse ranking behavior

## Problem Definition

For a query genome `x` and a template candidate `m`, the recommendation stage
produces a score `S_theta(x, m)`.

The selected template is:

```text
m_hat(theta) = argmax_m S_theta(x, m)
```

The selected template is then passed through the downstream GMSM pipeline:

```text
x -> m_hat(theta) -> homology/pruning/augmentation/export -> G_hat(theta)
```

The real project objective is therefore not:

```text
maximize template top-1 accuracy
```

but:

```text
maximize quality(G_hat(theta))
```

This matters because template choice is only an intermediate decision, while
the final reconstructed model is the scientific product.

## Original Intended Strategy

The original intended approach was a staged divide-and-conquer strategy.

### Stage 0. Parameterization

Expose the recommendation weights explicitly so that tuning is reproducible.

### Stage 1. Recommendation Benchmark

Build a biologically meaningful benchmark set and use it to test whether
auto-template recommendation generalizes beyond self-retrieval.

### Stage 2. End-To-End Evaluation

Compare final reconstructed models against trusted reference models so that
parameter tuning targets final model quality rather than only recommendation
accuracy.

### Stage 3. Parameter Search

Run a small black-box search over candidate `theta` values and rank them by the
end-to-end objective.

This was always closer to:

- black-box hyperparameter search

than to:

- direct differentiable learning
- ordinary supervised regression over weight labels

## What Was Actually Implemented

The workflow is now implemented as a layered system.

### 1. Parameterized Recommendation Scoring

The scoring system was exposed through CLI-configurable paired weights.

The current tunable family includes:

- `template_ani_weight` / `template_af_weight`
- `template_diamond_hit_weight` / `template_diamond_identity_weight`
- `template_bbh_template_weight` / `template_bbh_target_weight`
- `template_coarse_weight` / `template_rerank_weight`
- `template_rerank_topn`

Implementation anchors:

- `run_gmsm.py`
- `gmsm/template_recommendation.py`
- `gmsm/utils.py`

### 2. Recommendation Benchmark Runner

The benchmark runner was implemented to execute manifest-driven recommendation
evaluation and summarize:

- strict expected-template hits
- soft expected-neighbor hits
- per-case recommendation reports

This created the operational basis for:

- `Phase 1A` self-retrieval sanity checks
- `Phase 1B` same-species / same-clade generalization
- later `Phase 1C` boundary screening

### 3. Phase 1B Biological Benchmark Batch

The first non-trivial biological benchmark batch was admitted and validated.

This moved the project beyond:

- "can the system recover the template from itself?"

to:

- "can the system generalize to nearby but non-identical query genomes?"

### 4. Phase 2 End-To-End Evaluator

An end-to-end evaluator was implemented to compare predicted models against
reference SBML models.

The evaluator currently computes:

- reaction precision / recall / F1
- raw gene precision / recall / F1
- alias-harmonized gene precision / recall / F1

The first exact-reference anchor was:

- `eco_w3110`

This was the first case that made the end-to-end objective concrete.

### 5. Phase 3 Tuning Runner

A tuning orchestrator was implemented to:

- generate a backend-fixed search grid
- run the benchmark under each configuration
- evaluate reference-backed cases end-to-end
- aggregate exact, approximate, and boundary-screening evidence
- rank candidate settings

This is the first real executable parameter-estimation loop.

## Current Logic

The current recommendation score is a layered weighted score.

### Coarse Ranking

For `skani`:

```text
C_skani = w_ani * normalized_ani + w_af * aligned_fraction
```

For `diamond`:

```text
C_diamond = w_hit * hit_coverage + w_id * mean_identity_fraction
```

### BBH Reranking

```text
R_bbh = w_bbh_template * template_coverage + w_bbh_target * target_coverage
```

### Final Recommendation Score

```text
S_theta = w_coarse * C + w_rerank * R_bbh
```

Then:

```text
m_hat(theta) = argmax_m S_theta(x, m)
```

### End-To-End Objective Logic

The current safe objective policy is layered.

Primary optimization target:

```text
J_primary(theta) = mean reaction F1 over primary_exact cases
```

Secondary evidence:

- mean reaction F1 over `secondary_approximate` cases

Screening metrics:

- expected-template hit rate
- expected-neighbor hit rate
- boundary-screening recommendation behavior

Supplementary diagnostics:

- alias-harmonized gene metrics

Diagnostic-only:

- raw gene overlap

This logic is necessary because gene identifiers are still not harmonized
strongly enough to serve as a stable primary objective.

## Why The Objective Was Updated

The original plan treated reaction and gene metrics more symmetrically.

The first exact `eco_w3110` run showed that this was too optimistic.

Observed values from the first exact anchor:

- reaction F1: `0.912203`
- raw gene F1: `0.000455`
- alias-harmonized gene F1: `0.146108`

Interpretation:

- reaction-level comparison is already meaningful
- raw gene overlap is dominated by namespace mismatch
- alias harmonization recovers useful signal, but it is still not strong enough
  to replace reaction-level objective functions

So the objective policy was updated from:

- reaction and gene metrics as co-equal early targets

to:

- reaction F1 as the primary early tuning objective
- approximate-reference reaction metrics as secondary evidence
- gene metrics as supplementary / diagnostic signals

## Current Progress By Stage

### Stage 0. Parameterization

Status:

- completed

Meaning:

- the score function is now experimentally controllable

### Stage 1A. Self-Retrieval Sanity

Status:

- completed

Meaning:

- the basic recommendation wiring is operational

### Stage 1B. Same-Species / Same-Clade Generalization

Status:

- completed for the first promoted batch

Meaning:

- the benchmark now tests real biological generalization rather than only
  trivial self-recovery

### Stage 1C. Boundary Screening

Status:

- operational

Meaning:

- promoted boundary cases can now run recommendation-only inside the tuning loop
- the project now has at least one leverage-bearing boundary case:
  `actino_cglu_atcc13032`

### Stage 2. End-To-End Evaluation

Status:

- operational, but still limited in exact-reference coverage

Meaning:

- the project has one strong exact anchor: `eco_w3110`
- approximate-reference coverage now includes:
  - `eco_bw25113`
  - `bsu_py79`
  - `bsu_ncib3610`

### Stage 3. Parameter Search

Status:

- operational narrow-loop implementation exists

Meaning:

- candidate parameter sets can be generated, executed, evaluated, and ranked

## What The Project Learned So Far

Three important findings are now established.

### Finding 1. The Tuning Loop Is Real

The project is no longer at the "design only" stage.

The tuning runner, benchmark manifests, E2E evaluator, and admission policy are
all wired together.

### Finding 2. The Current Preferred Weight Family Is Flat Only Inside A Real Safe Region

Inside the currently preferred region:

- `template_backend = diamond`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`
- narrow neighborhoods of `template_diamond_hit_weight`
- narrow neighborhoods of `template_bbh_template_weight`

the tested local search was operationally flat.

This means:

- nearby micro-adjustments are not currently producing informative separation
- but the flatness is not unbounded

Later outward search now shows:

- the safe region extends through `template_diamond_hit_weight = 0.50`
- refinement then shows that the first practical degradation begins at `0.55`
- the earliest failures occur in leverage-bearing actinobacterial boundary
  cases

### Finding 3. Benchmark Discrimination Is No Longer The Main Bottleneck

The project can reject a clearly stressed setting because:

- exact and approximate anchors stay stable
- a promoted boundary case can flip away from its strict label

After the round-2 and round-3 boundary curation passes, the benchmark gained
enough leverage to show a real degradation ladder as `diamond_hit_weight`
increases.

So the current bottleneck is now:

- not benchmark discrimination alone
- not optimizer sophistication
- but sparse exact-reference coverage in the primary objective

## Current Best Interpretation

The auto-template parameter-estimation workflow is now in a good engineering
state but not yet in a final scientific-optimization state.

In practical terms:

- the score function is parameterized
- the benchmark runner works
- the E2E evaluator works
- the tuning runner works
- one exact anchor exists
- approximate-reference evidence has been widened
- multiple strong boundary discriminators now exist
- the first degradation boundary on the `diamond_hit_weight` axis has been
  bracketed

What is still missing is:

- broader exact-reference coverage
- a stronger gene harmonization policy
- multi-case exact-reference support for deciding between otherwise safe
  parameter families

## Strategy Going Forward

The next strategy should **not** be "run a much larger global grid now."

That would be premature because the first informative threshold has already
been localized well enough for a practical default, and the next gain comes
from a stronger primary objective rather than from more search on the same
axis.

The next strategy should be:

### Strategy 1. Keep The Current Preferred Family As The Working Default

Operational default region:

- `diamond` backend
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`
- keep `template_diamond_hit_weight <= 0.50` as the current safe region
- keep the previously validated BBH balance neighborhood for the remaining
  local score weights

### Strategy 2. Expand The Exact-Reference Tier

The highest-value next action is:

- exact-reference expansion for the `primary_exact` tier

The goal is to determine:

- whether otherwise safe parameter families differ in end-to-end quality on
  more than one exact anchor

without destabilizing:

- the exact anchor
- the current approximate tier

### Strategy 3. Continue To Separate Evidence Tiers

Do not merge everything into one scalar objective too early.

Keep the interpretation layered:

- `primary_exact`: optimization target
- `secondary_approximate`: controlled support evidence
- `boundary_screening`: biological rejection screen

### Strategy 4. Upgrade Gene-Level Objectives Only After Better Crosswalks

Gene-level metrics should remain:

- supplementary

until there is stronger orthology-aware harmonization.

## Practical Conclusion

The project has moved from:

- "parameter tuning should exist"

to:

- "parameter tuning now exists as a real executable workflow"

The main remaining challenge is no longer wiring or first-pass benchmark
construction.

The main remaining challenge is:

- making the primary objective less sparse so that otherwise safe parameter
  families can be compared on more than one exact anchor

That is why the next step should focus on:

- expanding the exact-reference tier

rather than:

- larger blind parameter sweeps
- another broad boundary-hunt cycle
