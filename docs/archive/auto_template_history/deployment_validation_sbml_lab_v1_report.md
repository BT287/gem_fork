# SBML-Oriented Deployment Validation Set v1 Report

## Purpose

This report records the first runnable deployment-oriented query set designed to
match the organism mix repeatedly seen in KAIST SBML papers and adjacent
medicinal / natural-product studies.

This is not a generic benchmark.

It is a deployment reality check for the frozen `v1` auto-template default.

## Active Set

Manifest:

- `benchmarks/deployment_validation_manifest.sbml_lab_v1.yaml`

Cases:

1. `actino_salbus_j1074`
2. `sco_sliv_tk24`
3. `actino_sery_nrrl23338`
4. `sco_sven_atcc10712`
5. `eco_w3110`

## Why These Cases

- `actino_salbus_j1074`
  - modern Streptomyces expression host repeatedly used in natural-product
    engineering
- `sco_sliv_tk24`
  - classic heterologous Streptomyces host
- `actino_sery_nrrl23338`
  - industrial erythromycin producer
- `sco_sven_atcc10712`
  - directly aligned with the 2022 SBML-related pikromycin engineering paper
- `eco_w3110`
  - directly aligned with the 2024 SBML medicinal-molecule production paper

Together these cover:

- actinomycete medicinal hosts
- industrial actinomycete producers
- one real non-actinomycete medicinal chassis used in the lab-adjacent
  literature

## Execution Result

Command class used:

- recommendation-only deployment benchmark with frozen `v1` defaults

Output root:

- `benchmark-results/deployment-sbml-lab-v1/`

Aggregate metrics:

- `passed_case_count = 5`
- `failed_case_count = 0`
- `top1_expected_template_hit_rate = 1.0`
- `top1_expected_neighbor_hit_rate = 1.0`
- `topk_expected_template_hit_rate = 1.0`
- `topk_expected_neighbor_hit_rate = 1.0`

## What This Means

This result does **not** prove that the current template panel is globally
optimal for all medicinal microbes.

It does show that:

- the frozen `v1` default remains sensible on an SBML-oriented organism mix
- the current `sco` actinomycete family can still absorb the most central
  Streptomyces / actinomycete deployment queries in this set
- `eco` remains a stable medicinal-side chassis anchor

## Outstanding Items

### `actino_amed_s699`

Keep provisional only.

Reason:

- medicinally important
- but still unstable between `sco` and `mtu` under small safe-family parameter
  changes

### `Streptomyces rapamycinicus NRRL 5491`

Keep as the next highest-priority SBML-specific future intake.

Reason:

- directly supported by the 2022 rapamycin-related SBML paper
- not yet staged locally

## Recommendation

For project-facing deployment validation, prefer this SBML-oriented set over a
maximally broad organism collection.

That matches the actual goal:

- good recommendations for the organisms the project is realistically likely to
  use
- not artificial generalization toward organisms that do not drive the expected
  workload
