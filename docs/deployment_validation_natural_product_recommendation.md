# Deployment Validation Recommendation for Natural-Product Queries

## Purpose

This note recommends a literature-backed deployment validation set for the
auto-template workflow.

The target use case is not generic microbial benchmarking.

It is:

- actinomycete-centered natural-product work
- with limited but deliberate inclusion of broader microbial chassis that are
  repeatedly used for natural-product biosynthesis or heterologous expression

## Important Distinction

Two organism roles should not be mixed:

- native industrial producers
  - examples: erythromycin, rifamycin, avermectin producers
- heterologous chassis strains
  - examples: engineered Streptomyces, Bacillus, E. coli, Pseudomonas

For deployment validation, both matter.

However, because the current project goal is actinomycete-based, the deployment
set should overweight actinomycete-native producers and Streptomyces-class
hosts, then use non-actinomycete hosts only as secondary controls.

## Selection Rule

Each candidate was scored qualitatively against four criteria:

1. literature importance in natural-product drug or precursor production
2. closeness to the current project deployment goal
3. compatibility with the current 10-template panel
4. immediate usability with already staged local assets

This yields three tiers:

- `deployment-primary`
  - actinomycete queries that best reflect the intended real workload
- `deployment-secondary`
  - realistic but lower-priority or broader chassis controls
- `future-intake`
  - literature-high-value candidates not yet staged locally

## Recommended Immediate Deployment Set

This is the recommended `v1` deployment set for immediate use because each case
already has a staged GBK and a defensible expected template family inside the
current panel.

### Priority 1. `sco_sliv_tk24`

- organism: `Streptomyces lividans TK24`
- query path:
  - `benchmarks/query_assets/phase1b_first_batch/sco_sliv_tk24/input.gbk`
- expected template: `sco`
- acceptable neighbors: `[sco, mtu]`
- rationale:
  - classic Streptomyces heterologous host
  - very close to the current `sco` template family
  - directly relevant to actinomycete natural-product expression workflows

Why it is first:

- it is the cleanest actinomycete deployment case already available locally
- it matches the current research direction better than generic bacterial hosts

### Priority 2. `actino_sery_nrrl23338`

- organism: `Saccharopolyspora erythraea NRRL 23338`
- query path:
  - `benchmarks/query_assets/phase3_boundary_round2_candidates/actino_sery_nrrl23338/input.gbk`
- expected template: `sco`
- acceptable neighbors: `[sco, mtu]`
- rationale:
  - industrial erythromycin producer
  - strong pharmaceutical relevance
  - broadens actinomycete deployment validation beyond the Streptomyces genus

Why it is second:

- it is a true industrial natural-product producer rather than only a chassis
- it tests whether the `sco` side of the panel generalizes to a closely related,
  but non-Streptomyces, actinomycete producer

### Priority 3. `sco_sven_atcc10712`

- organism: `Streptomyces venezuelae ATCC 10712`
- query path:
  - `benchmarks/query_assets/phase1c_boundary_candidates/sco_sven_atcc10712/input.gbk`
- expected template: `sco`
- acceptable neighbors: `[sco, mtu]`
- rationale:
  - fast-growing Streptomyces model
  - useful for synthetic-biology and natural-product engineering workflows
  - adds a second Streptomyces lineage that is not as trivial as `TK24`

Why it is not above `TK24`:

- recent host surveys still place it below `S. lividans` and especially below
  `S. albus` in mainstream heterologous-host usage
- its value here is as a secondary actinomycete deployment probe, not the main
  deployment anchor

### Priority 4. `bsu_py79`

- organism: `Bacillus subtilis PY79`
- query path:
  - `benchmarks/query_assets/phase1b_first_batch/bsu_py79/input.gbk`
- expected template: `bsu`
- acceptable neighbors: `[bsu]`
- rationale:
  - non-actinomycete but literature-supported natural-product chassis
  - useful as a broader bacterial control without shifting the deployment set
    away from its actinomycete center

Why it stays secondary:

- the project goal is not Bacillus-first
- it should be used as a robustness check, not as the primary deployment driver

## Optional Immediate Reserve

### `eco_w3110`

- organism: `Escherichia coli K-12 W3110`
- query path:
  - `benchmarks/query_assets/phase1b_first_batch/eco_w3110/input.gbk`
- expected template: `eco`
- rationale:
  - highly important engineered chassis for heterologous therapeutic natural
    product biosynthesis
  - already well supported in the current repo

Why it is not in the core actinomycete deployment set:

- it is too far from the intended actinomycete deployment distribution
- it is better treated as an optional cross-platform sanity control

## High-Value Future Intake Candidates

These are the best next candidates from the literature, but they are not yet
the immediate deployment set because local query assets are not staged.

### 1. `Streptomyces albus J1074`

- recommended family: `sco`
- status: highest-priority future intake
- why:
  - the most important gap in the current immediate set
  - recent host surveys identify `S. albus` as the most widely used
    Streptomyces heterologous host in current practice
  - it is a better long-term deployment representative than `S. venezuelae`

### 2. `Amycolatopsis mediterranei U32` or `S699`

- recommended family: `mtu` with `sco` as acceptable neighbor
- status: highest-priority industrial-producer intake
- why:
  - classic rifamycin producer with direct pharmaceutical importance
  - expands actinomycete coverage beyond the Streptomyces /
    Saccharopolyspora side
- note:
  - strict expected-template assignment should remain provisional until intake
    smoke confirms the current panel behavior

### 3. `Streptomyces avermitilis MA-4680`

- recommended family: `sco`
- status: high-priority future intake
- why:
  - classic industrial producer of avermectins
  - very strong natural-product relevance
  - also relevant as a chassis lineage in the Streptomyces host literature

### 4. `Pseudomonas putida KT2440`

- recommended family: `ppu`
- status: broader-chassis future intake
- why:
  - not actinomycete-centered, but a strong modern bacterial chassis for
    heterologous natural-product production
  - useful if the project later expands toward non-actinomycete industrial
    validation

## What Should Not Enter The Deployment Core

The following currently staged actinobacterial cases should remain benchmark or
boundary material, not deployment-core cases:

- `actino_rjost_rha1`
- `actino_nfar_ifm10152`
- `actino_cglu_atcc13032`

Reason:

- they are useful for ranking discrimination or boundary screening
- but they are not strong representatives of the intended real deployment
  distribution for natural-product pharmaceutical work

## Recommended V1 Deployment Composition

Use a `4-case` actinomycete-heavy deployment set first:

1. `sco_sliv_tk24`
2. `actino_sery_nrrl23338`
3. `sco_sven_atcc10712`
4. `bsu_py79`

Optional add-on:

5. `eco_w3110`

This composition is the best compromise between:

- literature relevance
- current project goal
- current template-panel compatibility
- immediate local executability

## Literature Basis

### Traditional / foundation references

1. Bérdy, 2005. "Bioactive microbial metabolites."
   - https://pubmed.ncbi.nlm.nih.gov/15813176/
2. Newman and Cragg, 2020. "Natural Products as Sources of New Drugs over the
   Nearly Four Decades from 01/1981 to 09/2019."
   - https://pubmed.ncbi.nlm.nih.gov/32162523/
3. Oliynyk et al., 2007. `S. erythraea NRRL23338` genome and erythromycin
   producer context.
   - https://pubmed.ncbi.nlm.nih.gov/17369815/
4. Zhao et al., 2010. `Amycolatopsis mediterranei U32` genome and rifamycin
   producer context.
   - https://pubmed.ncbi.nlm.nih.gov/20567260/
5. Ikeda et al., 2003. `Streptomyces avermitilis` genome and industrial
   avermectin producer context.
   - https://www.nature.com/articles/nbt820

### Recent / current-practice references

6. Lasch et al., 2025/2026 advance article. Streptomyces host-platform review
   covering 2004-2024.
   - https://pubs.rsc.org/en/content/articlehtml/2025/np/d5np00036j
7. 2020 study on engineering `Streptomyces lividans` for heterologous
   expression of secondary-metabolite gene clusters.
   - https://pubmed.ncbi.nlm.nih.gov/31918711/
8. 2024 comparative host study including `S. lividans`, `S. albus`, and
   `S. venezuelae`.
   - https://pubmed.ncbi.nlm.nih.gov/38790014/
9. 2024 review on `Bacillus subtilis` as a host for natural-product discovery
   and biosynthetic-gene-cluster engineering.
   - https://pubs.rsc.org/en/content/articlehtml/2024/np/d3np00065f
10. 2021 `Pseudomonas putida` study showing robust heterologous production of
    prodigiosin and glidobactin A.
   - https://pubmed.ncbi.nlm.nih.gov/34175462/
11. 2016 review on therapeutic natural-product biosynthesis using `E. coli`.
   - https://pubmed.ncbi.nlm.nih.gov/26942861/
12. 2020 review on metabolic engineering of `E. coli` for natural-product
    biosynthesis.
   - https://pubmed.ncbi.nlm.nih.gov/31924345/

## Final Recommendation

For the current project, the correct immediate move is:

- deploy with an actinomycete-heavy `4-case` set
- keep `bsu_py79` as the one broader bacterial control
- keep `eco_w3110` optional rather than core
- make `Streptomyces albus J1074` the next highest-priority future intake
- make `Amycolatopsis mediterranei` the next industrial-producer intake

This keeps the deployment objective aligned with the actual research goal
instead of drifting toward a generic all-microbe average.
