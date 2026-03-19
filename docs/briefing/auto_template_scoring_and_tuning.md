# Auto-Template Scoring And Tuning

## Purpose

This note summarizes the final intended logic of the current auto-template
workflow:

- what score is computed
- what parameters were tuned
- what datasets were used
- what objective was considered valid
- what default is currently recommended for deployment

This is the shortest report that still preserves the exact mathematical logic.

## What Problem Is Being Solved

The project is not training a supervised classifier over templates.

It is choosing a weight vector `theta` for the recommendation score so that:

- template choice stays biologically interpretable
- the final reconstructed metabolic model remains good end-to-end
- clearly pathological ranking behavior is rejected before deployment

The pipeline is:

```text
query genome x
-> template score S_theta(x, m) over template candidates m
-> selected template m_hat(theta)
-> GMSM reconstruction
-> reconstructed model G_hat(theta)
```

So the real objective is not:

```text
maximize template top-1 accuracy
```

It is closer to:

```text
maximize quality(G_hat(theta))
```

with template ranking used as an upstream control signal.

## Template Score

### Coarse Score

When the coarse backend is `skani`:

```text
C_skani(x, m) = w_ani * ANI_norm(x, m) + w_af * AF(x, m)
```

where:

- `ANI_norm` is the normalized average nucleotide identity term used in the
  current implementation
- `AF` is aligned fraction
- `w_ani + w_af = 1`

When the coarse backend is `diamond`:

```text
C_diamond(x, m) = w_hit * HitCoverage(x, m) + w_id * MeanIdentityFrac(x, m)
```

where:

- `HitCoverage` is the matched-query coverage term
- `MeanIdentityFrac` is the mean identity term converted to fraction scale
- `w_hit + w_id = 1`

### BBH Rerank Score

For the BBH rerank layer:

```text
R_bbh(x, m) = w_bbh_template * TemplateCoverage(x, m)
            + w_bbh_target * TargetCoverage(x, m)
```

with:

```text
w_bbh_template + w_bbh_target = 1
```

### Final Recommendation Score

The final score used for ranking is:

```text
S_theta(x, m) = w_coarse * C(x, m) + w_rerank * R_bbh(x, m)
```

with:

```text
w_coarse + w_rerank = 1
```

The selected template is:

```text
m_hat(theta) = argmax_m S_theta(x, m)
```

`rerank_topn` determines how many top coarse candidates are re-evaluated by the
BBH stage before the final ranking is finalized.

## Tuned Parameter Family

The implemented tunable family is:

```text
theta = {
  template_backend,
  template_ani_weight,
  template_af_weight,
  template_diamond_hit_weight,
  template_diamond_identity_weight,
  template_bbh_template_weight,
  template_bbh_target_weight,
  template_coarse_weight,
  template_rerank_weight,
  template_rerank_topn
}
```

In practice, the deployed `v1` family is backend-fixed and focuses on:

- `template_backend = diamond`
- `template_diamond_hit_weight`
- `template_diamond_identity_weight`
- `template_bbh_template_weight`
- `template_bbh_target_weight`
- `template_coarse_weight`
- `template_rerank_weight`
- `template_rerank_topn`

## Dataset Design

The datasets were intentionally split by role instead of forcing one benchmark
to do every job.

### 1. Broad Tuning Benchmark

Role:

- reject obviously bad parameter regions

Contents:

- exact-anchor cases
- approximate-reference cases
- recommendation-only boundary cases

Interpretation:

- this layer is the safety filter
- it is not the final proxy for the real deployment distribution

### 2. Deployment Validation Set

Role:

- check whether the frozen default behaves sensibly on the organisms that are
  realistically likely to appear in project use

Current SBML-oriented deployment set:

- `actino_salbus_j1074`
- `sco_sliv_tk24`
- `actino_sery_nrrl23338`
- `sco_sven_atcc10712`
- `eco_w3110`

Interpretation:

- this layer is the deployment reality check
- it is intentionally narrower than a "universal microbe" benchmark

### 3. Future Intake Pool

Role:

- keep literature-important organisms that are not yet stable enough to promote
  into the active deployment set

Current example:

- `actino_amed_s699`

## Objective Function

The original idea treated reaction and gene metrics more symmetrically.

The actual implementation history showed that this was too optimistic.

The first exact anchor `eco_w3110` gave:

- reaction F1 `0.912203`
- raw gene F1 `0.000455`
- alias-harmonized gene F1 `0.146108`

This means:

- reaction IDs are already usable as a primary quality signal
- raw gene overlap is dominated by namespace mismatch
- harmonized gene overlap is useful diagnostically but is not yet a safe
  primary optimization target

So the current valid tuning logic is:

### Primary Objective

```text
J_primary(theta) = mean reaction_F1_i(theta)
```

over admitted exact-anchor cases.

### Secondary Evidence

- mean reaction F1 over approximate-reference cases

### Screening Constraints

- expected-template hit behavior
- expected-neighbor hit behavior
- boundary-screening stability

### Diagnostic Only

- raw gene overlap
- alias-harmonized gene overlap

## How The Search Was Actually Done

This was not gradient-based fitting.

It was a black-box, benchmark-driven parameter search with repeated narrowing.

### Stage A. Broad Rejection

- remove clearly bad regions using boundary cases
- example: very large `diamond_hit_weight` values degraded boundary behavior

### Stage B. Local Safe-Band Search

- search inside the surviving parameter family
- outcome: many nearby settings were effectively flat under the benchmark

### Stage C. Deployment-Oriented Freeze

- once the broad benchmark stopped separating nearby safe settings,
  the practical question became:
  "does the current safe default behave well on our likely query GBKs?"
- this led to freezing a conservative `v1` default and validating it on the
  SBML-oriented deployment set

## Current V1 Operational Default

The frozen `v1` default is:

```text
template_backend = diamond
template_diamond_hit_weight = 0.05
template_diamond_identity_weight = 0.95
template_bbh_template_weight = 0.50
template_bbh_target_weight = 0.50
template_coarse_weight = 0.95
template_rerank_weight = 0.05
template_rerank_topn = 3
```

## Why This Default Was Frozen

Because:

- broad tuning already rejected obviously bad settings
- the surviving local family was largely flat under the benchmark
- deployment validation on the SBML-oriented set remained clean

So continuing generic micro-tuning had low information value.

The more rational move was:

- freeze the conservative safe default
- validate it on the likely deployment distribution
- collect real failure cases only after usage starts

## Current Practical Interpretation

This `v1` default should be read as:

- a deployment-ready working default for the current intended query range

It should **not** be read as:

- a globally proven optimum for all microbes

That is the right level of claim for merge and deployment.
