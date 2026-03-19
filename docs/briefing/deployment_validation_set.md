# Deployment Validation Set

## Purpose

This note defines the current deployment-facing validation set for the
auto-template `v1` release.

Its role is narrower than the broad tuning benchmark.

The broad benchmark rejects obviously bad parameter regions.
The deployment validation set checks whether the frozen default behaves
sensibly on the organism mix that is currently most relevant for intended lab
use.

## Active Manifest

Current active deployment manifest:

- `benchmarks/deployment_validation_manifest.sbml_lab_v1.yaml`

Template manifest skeleton for future project-specific additions:

- `benchmarks/deployment_validation_manifest.template.yaml`

## Current Organism Mix

The current SBML-oriented deployment set contains:

- `actino_salbus_j1074`
- `sco_sliv_tk24`
- `actino_sery_nrrl23338`
- `sco_sven_atcc10712`
- `eco_w3110`

Interpretation:

- the set is actinomycete-heavy because the intended natural-product use case
  is actinomycete-centered
- `eco_w3110` remains as a stable cross-check because it is a strong exact
  anchor and a common engineering chassis

## Why This Set Was Chosen

Selection criteria were:

- strong literature relevance for natural-product or drug-related microbial work
- compatibility with the existing template panel
- stable expected-template interpretation under the current deployment default
- usefulness as a real-use sanity check rather than as an adversarial boundary
  screen

This means the deployment set is intentionally not the same as:

- the full exploratory benchmark
- the boundary-screening set
- the future-intake candidate pool

## Current Result

Under the frozen `v1` default:

- `template_backend = diamond`
- `template_diamond_hit_weight = 0.05`
- `template_diamond_identity_weight = 0.95`
- `template_bbh_template_weight = 0.5`
- `template_bbh_target_weight = 0.5`
- `template_coarse_weight = 0.95`
- `template_rerank_weight = 0.05`
- `template_rerank_topn = 3`

the current deployment set passed cleanly.

Operational interpretation:

- this is sufficient for `v1` deployment readiness within the current intended
  organism mix
- future project-specific query GBKs should extend this manifest rather than
  replace the benchmark history

## Relation To Archived Files

The following remain useful historical records but are no longer the canonical
entry point:

- archived deployment recommendation notes
- natural-products `v1` and `v2` exploratory manifests
- future-intake actinomycete candidate manifests

Those records are now kept under:

- `docs/archive/auto_template_history/`
- `benchmarks/archive/auto_template_history/`
