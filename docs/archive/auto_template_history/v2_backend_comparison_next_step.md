# V2 Next Step: Backend Comparison

## Purpose

Once `Full Reconstruction Integration` becomes green, the next highest-value
question is no longer generic micro-tuning inside the current `diamond` family.

It is:

- whether a matched `skani` family performs better than the current `diamond`
  `v1` operational default under the same benchmark and deployment setting

## Why This Is The Right Next Step

Current status:

- `diamond` has already been pushed to a deployment-ready `v1` default
- `skani` remains implemented and supported
- but `skani` has not yet been tuned and compared under the same evidence stack

So the next scientific question is not:

- "can we perturb `diamond_hit_weight` a little more?"

It is:

- "under the same benchmark, same deployment set, and same objective policy,
  does the best `skani` family beat, match, or lose to the current `diamond`
  default?"

## Fixed Comparison Conditions

To keep the comparison interpretable, the following must stay fixed:

- same benchmark manifests
- same deployment validation set
- same reference-backed objective policy
- same rerank logic
- same `template_rerank_topn` candidate family unless a narrow justification is
  documented

This avoids backend comparison being confounded by benchmark drift.

## Candidate Comparison Design

### Arm A. Current Diamond Baseline

Use the current frozen `v1` default:

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

### Arm B. Tuned Skani Family

Search over:

- `template_backend = skani`
- `template_ani_weight`
- `template_af_weight`
- `template_bbh_template_weight`
- `template_bbh_target_weight`
- `template_coarse_weight`
- `template_rerank_weight`
- `template_rerank_topn`

using the same exact / approximate / boundary evidence policy already used for
the `diamond` family.

## Recommended Initial Search Space

Use a narrow first-pass `skani` search:

- `template_ani_weight in {0.5, 0.7, 0.9}`
- `template_bbh_template_weight in {0.3, 0.5, 0.7}`
- `template_coarse_weight in {0.95}`
- `template_rerank_topn in {3}`

Reason:

- this matches the current search philosophy used for `diamond`
- it keeps the first comparison interpretable and cheap

## Evaluation Rule

Primary comparison target:

- exact-anchor reaction F1 mean

Secondary comparison targets:

- approximate reaction F1 mean
- deployment validation hit behavior
- boundary-screening stability

Diagnostic-only:

- gene alias metrics

## Decision Rule

### Keep Diamond V1 If

- best `skani` does not beat `diamond v1` on the primary objective
- or `skani` improves one metric but destabilizes deployment/boundary behavior

### Promote Skani If

- best `skani` beats `diamond v1` on the primary objective
- and does not regress deployment validation materially
- and does not worsen boundary-screening behavior unacceptably

### Introduce Backend Policy Split If

- `skani` is better on Linux/macOS deployment-like cases
- but `diamond` remains the more robust operational default across environments

Then a policy such as:

- Linux/macOS: `auto` or `skani-first`
- Windows: `diamond`

may become justifiable.

## Suggested Execution

1. wait for current `v1` CI closure
2. run matched `skani` tuning with the existing tuning runner
3. compare best `skani` result against frozen `diamond v1`
4. document the backend policy decision explicitly

## Reference Files

- `docs/briefing/auto_template_scoring_and_tuning.md`
- `docs/briefing/release_readiness.md`
- `docs/auto_template_v1_operational_default.md`
- `scripts/tune_template_weights.py`
