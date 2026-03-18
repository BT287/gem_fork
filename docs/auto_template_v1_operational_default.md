# Auto-Template V1 Operational Default

## Purpose

This note freezes the current operational default for `--auto-template`.

It is not a claim that the project has found a globally unique optimum.

It is a practical decision:

- the current benchmark can reject clearly bad settings
- the safe family remains flat inside the currently tested neighborhood
- so deployment validation should now use one conservative canonical setting

## Frozen V1 Default

Use the following values as the operational default:

- `template_backend = diamond`
- `template_diamond_hit_weight = 0.05`
- `template_diamond_identity_weight = 0.95`
- `template_bbh_template_weight = 0.5`
- `template_bbh_target_weight = 0.5`
- `template_coarse_weight = 0.95`
- `template_rerank_weight = 0.05`
- `template_rerank_topn = 3`

## Why This Setting

- it stays well inside the known safe region
- it is far from the first observed degradation threshold
- it has already survived exact, approximate, and boundary screening
- it is simple enough to use as one canonical deployment baseline

## Recommended Command Pattern

Single run:

```bash
conda activate gmsm
python run_gmsm.py \
  -i <query.gbk> \
  --auto-template \
  -p -d
```

The current code defaults now resolve to the frozen V1 setting above.

Deployment validation run:

```bash
conda activate gmsm
python scripts/run_auto_template_benchmark.py \
  --manifest benchmarks/deployment_validation_manifest.template.yaml \
  --label deployment-validation-v1
```

Copy the template manifest first and replace placeholder query paths before
running the deployment benchmark.

## What This Does Not Mean

- it does not prove global optimality
- it does not replace future deployment-specific retuning
- it does not remove the need for boundary screening as a safety filter
