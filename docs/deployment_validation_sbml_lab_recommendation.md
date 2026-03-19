# Deployment Validation Recommendation for KAIST SBML-Oriented Medicinal-Microbe Queries

## Purpose

This note builds a deployment-oriented query set that is closer to the actual
organisms repeatedly used in KAIST SBML publications and adjacent medicinal /
natural-product studies.

This is intentionally different from a generic all-microbe benchmark.

The goal is:

- prioritize organisms that are genuinely likely to appear in the project's
  real query distribution
- keep the set interpretable inside the current 10-template panel
- avoid over-generalizing toward organisms that are biologically interesting
  but not central to the expected workload

## Selection Logic

An organism enters the SBML-oriented deployment set only when it satisfies both
of the following:

1. there is direct SBML-lab or closely adjacent medicinal / natural-product
   literature support
2. the organism can be mapped to the current template panel with an
   interpretable expected template family

This produces three tiers:

- `sbml-primary`
  - directly aligned with medicinal / natural-product organisms repeatedly used
    in SBML publications or near-adjacent literature
- `sbml-secondary`
  - important but slightly less central cases, or cases that are already useful
    as reserves
- `sbml-future-intake`
  - highly relevant organisms not yet fully promoted into the active deployment
    core

## Literature Basis Used

### SBML / lab-adjacent papers

1. SBML publications page:
   - https://sbml.kaist.ac.kr/publications
2. `Streptomyces venezuelae` for enhanced pikromycin production:
   - https://pubmed.ncbi.nlm.nih.gov/35445397/
3. `Streptomyces rapamycinicus NRRL 5491` comparative genomics / rapamycin:
   - https://pubmed.ncbi.nlm.nih.gov/35717543/
4. `Escherichia coli` for actinocin and other medicinal molecules:
   - https://pubmed.ncbi.nlm.nih.gov/38043641/
5. `Corynebacterium glutamicum` systems metabolic engineering example:
   - https://pubmed.ncbi.nlm.nih.gov/36341775/

### Broader field references used to fill the actinomycete host side

6. Streptomycete systems-metabolic-engineering review:
   - https://pubmed.ncbi.nlm.nih.gov/29076639/
7. Actinomycete GEM reconstruction for antibiotics production:
   - https://pubmed.ncbi.nlm.nih.gov/30269028/
8. Prokaryotic secondary-metabolite systems-metabolic-engineering review:
   - https://pubs.rsc.org/en/content/articlelanding/2016/np/c6np00019c
9. Streptomyces host-platform review:
   - https://pubs.rsc.org/en/content/articlehtml/2025/np/d5np00036j

## Recommended Active SBML-Oriented Deployment Set

This is the recommended working set because every case below is already staged
locally and is both literature-supported and template-compatible.

### 1. `actino_salbus_j1074`

- organism: `Streptomyces albus J1074` (current NCBI naming:
  `Streptomyces albidoflavus J1074`)
- expected template: `sco`
- acceptable neighbors: `[sco, mtu]`
- reason:
  - widely used modern Streptomyces expression host in the literature
  - currently the strongest high-value actinomycete host that we have already
    staged and smoke-tested successfully

### 2. `sco_sliv_tk24`

- organism: `Streptomyces lividans TK24`
- expected template: `sco`
- acceptable neighbors: `[sco, mtu]`
- reason:
  - classic heterologous Streptomyces host
  - strong fit to the actinomycete natural-product side of the workload

### 3. `actino_sery_nrrl23338`

- organism: `Saccharopolyspora erythraea NRRL 23338`
- expected template: `sco`
- acceptable neighbors: `[sco, mtu]`
- reason:
  - erythromycin producer
  - keeps a true industrial medicinal actinomycete in the active set

### 4. `sco_sven_atcc10712`

- organism: `Streptomyces venezuelae ATCC 10712`
- expected template: `sco`
- acceptable neighbors: `[sco, mtu]`
- reason:
  - directly supported by the 2022 SBML-related pikromycin engineering paper
  - should be kept in the SBML-oriented set even if it is no longer in the
    narrower natural-product v2 set

### 5. `eco_w3110`

- organism: `Escherichia coli K-12 W3110`
- expected template: `eco`
- acceptable neighbors: `[eco]`
- reason:
  - directly supported by the 2024 SBML actinocin / medicinal-molecule paper
  - provides the non-actinomycete medicinal chassis that is genuinely used in
    the lab-adjacent literature

## Why This Set Differs From The Natural-Product V2 Set

The natural-product `v2` set optimized for an actinomycete-heavy deployment
distribution is:

- `sco_sliv_tk24`
- `actino_sery_nrrl23338`
- `actino_salbus_j1074`
- `bsu_py79`

The SBML-oriented set changes this because the lab-adjacent publication record
points to a different "real workload" mix:

- `sco_sven_atcc10712` is added back because it is explicitly used in the 2022
  pikromycin engineering work
- `eco_w3110` replaces `bsu_py79` because `E. coli` has direct medicinal
  production evidence in the recent SBML publication stream

In short:

- natural-product `v2` = field-oriented actinomycete production mix
- SBML-oriented deployment set = lab-usage-oriented medicinal-microbe mix

## What Stays Out Of The Active Core

### `actino_amed_s699`

- keep as `sbml-future-intake`
- reason:
  - medicinally important, but still unstable between `sco` and `mtu` under
    small safe-family parameter changes

### `Streptomyces rapamycinicus NRRL 5491`

- keep as the next highest-priority lab-specific future intake
- reason:
  - directly supported by the 2022 SBML-related rapamycin paper
  - not yet staged locally

### `Corynebacterium glutamicum`

- reserve only
- reason:
  - heavily used in SBML systems-metabolic-engineering work, but less directly
    aligned with medicinal / natural-product deployment than the five active
    cases above

## Recommended SBML-Oriented Working Composition

Use this `5-case` set as the SBML-oriented deployment reality check:

1. `actino_salbus_j1074`
2. `sco_sliv_tk24`
3. `actino_sery_nrrl23338`
4. `sco_sven_atcc10712`
5. `eco_w3110`

Reserve:

- `actino_amed_s699`
- `Streptomyces rapamycinicus NRRL 5491`
- `Corynebacterium glutamicum ATCC 13032`

## Validation Status

The runnable manifest for this set is:

- `benchmarks/deployment_validation_manifest.sbml_lab_v1.yaml`

This manifest was executed with the frozen `v1` auto-template default via the
recommendation-only benchmark runner.

Observed aggregate result:

- `passed_case_count = 5`
- `failed_case_count = 0`
- `top1_expected_template_hit_rate = 1.0`
- `top1_expected_neighbor_hit_rate = 1.0`

Interpretation:

- the set is not only literature-backed, but also currently compatible with the
  deployed auto-template logic
- `Streptomyces`-centered medicinal cases map cleanly to the current `sco`
  template family
- `E. coli W3110` remains a stable non-actinomycete medicinal chassis anchor
  for this SBML-oriented deployment layer

## Final Recommendation

If the question is "what should represent the query GBKs that are most likely
to matter for this project and this lab context?", the best answer is not a
maximally general set.

It is a literature-backed, SBML-oriented set centered on:

- Streptomyces medicinal hosts
- industrial actinomycete producers
- one real lab-used medicinal `E. coli` chassis

That is the right distribution for deployment validation of the current
auto-template workflow.
