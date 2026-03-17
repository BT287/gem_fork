# Phase 1C Boundary Candidate Shortlist

## Purpose

This note upgrades `Phase 1C` from a generic plan into a concrete shortlist of
non-legacy candidate organisms.

The goal is not to admit all of these immediately.

The goal is to define the smallest candidate set that is:

- biologically interpretable
- more difficult than same-species `Phase 1B`
- compatible with the current 10-template panel

## Selection Rule

A useful `Phase 1C` candidate should satisfy all of the following:

- complete genome or stable genome record with clear provenance
- no known dependence on repo-local legacy scaffolds
- a strict label that is still defensible
- at least one biologically meaningful soft-neighbor template
- plausible score competition between a same-lineage template and a nearby
  higher-level alternative

In practice, the best current competition axes in the template panel are:

- `sco` vs `mtu` for Actinobacteria
- `bsu` vs `clj` for Firmicutes

## Recommended Shortlist

### 1. `actino_cglu_atcc13032`

- organism: *Corynebacterium glutamicum* ATCC 13032
- source accession: `GCA_000196335.1`
- strict label: `mtu`
- soft neighbors: `[mtu, sco]`
- competition axis: `mtu` vs `sco`
- admission priority: highest
- why this is useful:
  - it is not same-genus to either curated actinobacterial template
  - it sits in `Mycobacteriales`, so `mtu` is the stricter label
  - `sco` remains a biologically interpretable actinobacterial alternative
- source:
  - NCBI BioProject PRJNA13760 / assembly `GCA_000196335.1`
  - Kalinowski et al., *J Biotechnol* 2003

### 2. `clj_cauto_dsm10061`

- organism: *Clostridium autoethanogenum* DSM 10061
- source accession: `GCA_000484505.2`
- strict label: `clj`
- soft neighbors: `[clj, bsu]`
- competition axis: `clj` vs `bsu`
- admission priority: highest
- why this is useful:
  - it is same-genus or same-lineage adjacent to `clj`, but not the template
    organism itself
  - it remains inside the Firmicute part of the panel, where `bsu` is a
    meaningful alternative family-level competitor
  - industrial gas-fermentation relevance makes the case easy to explain
- source:
  - NCBI BioProject PRJNA219420 / genome record `CP012395.1`
  - Brown et al., *Biotechnol Biofuels* 2014

### 3. `firmi_blich_dsm13`

- organism: *Bacillus licheniformis* DSM 13 = ATCC 14580
- source accession: `GCA_000008425`
- strict label: `bsu`
- soft neighbors: `[bsu, clj]`
- competition axis: `bsu` vs `clj`
- admission priority: medium
- why this is useful:
  - it is same-genus to `bsu` but more distant than the current Phase 1B
    *B. subtilis* strains
  - it is still inside the Firmicute part of the panel, so `clj` is a
    meaningful higher-level alternative
  - it should be harder than the current `bsu` same-species cases while still
    keeping a clear biological explanation
- source:
  - BacDive strain 689 lists complete assembly `GCA_000008425`
  - NCBI genome record `NC_006322.1`

### 4. `sco_sven_atcc10712`

- organism: *Streptomyces venezuelae* ATCC 10712
- source accession: `NC_018750.1`
- strict label: `sco`
- soft neighbors: `[sco, mtu]`
- competition axis: `sco` vs `mtu`
- admission priority: medium
- why this is useful:
  - it is same-genus to `sco`, but more distant than the current
    `sco_sliv_tk24` same-clade case
  - the case stays inside Actinobacteria, where `mtu` is the nearest panel
    alternative
  - this should be a cleaner replacement for low-quality legacy
    `Streptomyces collinus` scaffolds
- source:
  - NCBI RefSeq nucleotide `NC_018750.1`
  - Gomez-Escribano et al., *J Ind Microbiol Biotechnol* 2021

## Recommended Intake Order

1. `actino_cglu_atcc13032`
2. `clj_cauto_dsm10061`
3. `firmi_blich_dsm13`
4. `sco_sven_atcc10712`

Why this order:

- the first two give the cleanest cross-template competition axes
- the third is still valuable but more likely to collapse back to `bsu`
- the fourth is useful, but its accession/provenance should be rechecked during
  intake because multiple public sequence records exist for ATCC 10712

## Admission Policy

Admit these first as:

- `evaluation_tier: boundary_screening`
- recommendation-only cases

Do **not** stage approximate reference SBML for them yet.

That would add cost before we know whether the cases actually differentiate
configurations.

## Immediate Next Action

1. download the four query inputs
2. verify parseability with recommendation-only mode
3. promote the cleanest `2-3` into the runnable boundary-screening manifest
4. rerun a narrow `Phase 1C` pilot before widening the search grid
