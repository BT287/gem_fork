# Phase 3 Boundary Round 2 Candidate Shortlist

## Purpose

This note turns the round-2 boundary-curation strategy into a concrete
shortlist of new non-legacy candidates.

The selection goal is not:

- add many more cases

The selection goal is:

- find `3-6` new candidates that have a realistic chance of adding
  discrimination beyond the currently promoted boundary set

## Selection Rule

A round-2 candidate should satisfy all of the following:

- complete genome or stable complete genomic record
- reproducible public accession
- strict label that is still biologically defensible within the current
  template panel
- at least one plausible soft-neighbor competitor already present in the panel
- no dependence on repo-local legacy scaffolds

Current preferred competition axes remain:

- `mtu` vs `sco`
- `clj` vs `bsu`

## Recommended Shortlist

### 1. `actino_rjost_rha1`

- organism: *Rhodococcus jostii* RHA1
- source accession: `GCA_000014565.1`
- strict label: `mtu`
- soft neighbors: `[mtu, sco]`
- competition axis: `mtu` vs `sco`
- admission priority: highest
- why this is useful:
  - it stays inside the Mycobacteriales branch, so `mtu` remains the stricter
    label
  - it is more distant than the current *Corynebacterium glutamicum* case,
    which gives it a chance to produce a different ranking structure
  - `sco` is still the nearest alternative actinobacterial panel template
- provenance:
  - KEGG genome entry for *R. jostii* RHA1 lists complete assembly
    `GCA_000014565.1`
  - chromosome RefSeq/GenBank record `NC_008268.1` / `CP000431.1`
  - reference PMID: `17030794`

### 2. `actino_nfar_ifm10152`

- organism: *Nocardia farcinica* IFM 10152
- source accession: `NC_006361.1`
- strict label: `mtu`
- soft neighbors: `[mtu, sco]`
- competition axis: `mtu` vs `sco`
- admission priority: high
- why this is useful:
  - it is a second non-*Mycobacterium* Mycobacteriales candidate, which helps
    test whether the `mtu` preference generalizes beyond a single lineage
  - it is taxonomically interpretable and biologically distinct from the current
    *Rhodococcus* and *Corynebacterium* cases
  - if both `Rhodococcus` and `Nocardia` collapse the same way, that tells us
    the actinobacterial boundary is still under-sampled
- provenance:
  - NCBI Gene pages for strain IFM 10152 point to reference chromosome
    `NC_006361.1`
  - complete genome paper PMID: `15466710`

### 3. `actino_sery_nrrl23338`

- organism: *Saccharopolyspora erythraea* NRRL 23338
- source accession: `GCA_000062885.1`
- strict label: `sco`
- soft neighbors: `[sco, mtu]`
- competition axis: `sco` vs `mtu`
- admission priority: high
- why this is useful:
  - it adds a non-*Streptomyces* actinomycete on the `sco` side of the panel
  - it is a secondary-metabolism-rich actinomycete, which makes the `sco`
    label biologically explainable
  - it may create a cleaner `sco`-side complement to the already-promoted
    `actino_cglu_atcc13032` `mtu`-side signal
- provenance:
  - KEGG genome entry lists complete assembly `GCA_000062885.1`
  - chromosome GenBank record `AM420293`
  - reference PMID: `17369815`

### 4. `firmi_cbei_ncimb8052`

- organism: *Clostridium beijerinckii* NCIMB 8052
- source accession: `GCA_000016965.1`
- strict label: `clj`
- soft neighbors: `[clj, bsu]`
- competition axis: `clj` vs `bsu`
- admission priority: highest
- why this is useful:
  - it adds a second solventogenic clostridial candidate that is distinct from
    the already-promoted *C. autoethanogenum* case
  - it stays inside the clostridial side of the panel, so `clj` remains a
    defensible strict label
  - it offers a chance to see whether the Firmicute boundary can become more
    discriminative without relying on Bacillus-side candidates only
- provenance:
  - KEGG genome entry lists complete assembly `GCA_000016965.1`
  - chromosome GenBank record `CP000721`

### 5. `firmi_gkau_hta426`

- organism: *Geobacillus kaustophilus* HTA426
- source accession: `GCA_000009785.1`
- strict label: `bsu`
- soft neighbors: `[bsu, clj]`
- competition axis: `bsu` vs `clj`
- admission priority: medium
- why this is useful:
  - it is more distant than the Bacillus reserve case but still clearly inside
    the Bacilli side of the panel
  - it may provide a harder `bsu`-side comparison than same-genus Bacillus
    strains
  - if it still stays stable, that is useful negative evidence about the limits
    of the current Firmicute axis
- provenance:
  - KEGG genome entry lists complete assembly `GCA_000009785.1`
  - chromosome GenBank record `BA000043`
  - reference PMID: `15576355`

### 6. `firmi_bhal_c125`

- organism: *Halalkalibacterium halodurans* C-125
- source accession: `GCA_000011145.1`
- strict label: `bsu`
- soft neighbors: `[bsu, clj]`
- competition axis: `bsu` vs `clj`
- admission priority: medium
- why this is useful:
  - it gives a second non-*Bacillus subtilis* Bacillales-side candidate
  - it is historically well characterized and directly compared against
    *B. subtilis* in the original genome paper
  - it is a good test of whether the Firmicute boundary can be improved by
    better Bacilli-side diversity rather than more same-genus Bacillus strains
- provenance:
  - KEGG genome entry lists complete assembly `GCA_000011145.1`
  - chromosome GenBank record `BA000004`
  - reference PMID: `11058132`

## Recommended Intake Order

1. `actino_rjost_rha1`
2. `firmi_cbei_ncimb8052`
3. `actino_sery_nrrl23338`
4. `actino_nfar_ifm10152`
5. `firmi_gkau_hta426`
6. `firmi_bhal_c125`

Why this order:

- the first three give the highest chance of adding a genuinely new ranking
  split
- the fourth is still high-value but uses a nucleotide-accession path rather
  than an assembly package path
- the last two are useful Bacilli-side probes, but they may still remain stable
  under both preferred and stressed settings

## Practical Admission Policy

Admit these first only as:

- `evaluation_tier: boundary_screening`
- recommendation-only cases

Do **not** stage reference SBML for them yet.

The first goal is to find leverage-bearing ranking behavior, not to create more
approximate E2E baggage.

## Immediate Next Action

1. stage all six query inputs
2. run recommendation-only intake smoke
3. audit top-2/top-3 competitor structure
4. probe only the best `2-4` candidates under stable vs stressed settings
