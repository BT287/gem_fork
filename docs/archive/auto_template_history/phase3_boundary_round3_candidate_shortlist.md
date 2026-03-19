# Phase 3 Boundary Round 3 Candidate Shortlist

## Purpose

This note defines the next Firmicute-focused curation round after round 2
made one bottleneck explicit:

- the project now has enough actinobacterial leverage
- it still lacks a second clean Firmicute-side leverage case that fails along
  the intended `clj`-vs-`bsu` axis

So the round-3 goal is not:

- add more boundary cases in general

The round-3 goal is:

- find `3-6` Firmicute candidates with a realistic chance of producing a
  cleaner `clj`-vs-`bsu` competition story

## Selection Rule

A round-3 Firmicute candidate should satisfy all of the following:

- complete genome or stable complete genomic record
- reproducible public accession
- strict label that is still biologically defensible within the current
  template panel
- at least one plausible `clj`-or-`bsu` soft-neighbor competitor already
  present in the panel
- no dependence on repo-local legacy scaffolds

Additional round-3 bias:

- prefer candidates that remain clearly inside Firmicutes while avoiding the
  previously observed `eco` drift whenever possible

## Recommended Shortlist

### 1. `firmi_cace_atcc824`

- organism: *Clostridium acetobutylicum* ATCC 824
- source accession: `GCA_000008765.1`
- strict label: `clj`
- soft neighbors: `[clj, bsu]`
- competition axis: `clj` vs `bsu`
- admission priority: highest
- why this is useful:
  - it is a classic solventogenic clostridial genome with a complete assembly
  - it sits cleanly on the clostridial side of the panel while still remaining
    inside the broad Firmicute competition space
  - unlike the current provisional *C. beijerinckii* case, it is a stronger
    legacy benchmark organism with well-understood provenance
- provenance:
  - NCBI Datasets reports complete assembly `GCA_000008765.1`
  - type-material strain `ATCC 824`
  - BioProject `PRJNA77`

### 2. `firmi_cthe_atcc27405`

- organism: *Acetivibrio thermocellus* ATCC 27405
- legacy name: *Clostridium thermocellum* ATCC 27405
- source accession: `GCA_000015865.1`
- strict label: `clj`
- soft neighbors: `[clj, bsu]`
- competition axis: `clj` vs `bsu`
- admission priority: high
- why this is useful:
  - it adds a cellulolytic clostridial genome that is clearly distinct from
    the solventogenic clostridia already screened
  - it remains interpretable on the clostridial side while testing whether the
    Firmicute axis can generalize beyond acetogen-like or solventogen-like
    candidates
  - it is taxonomically stable enough for a screening benchmark despite the
    updated genus name
- provenance:
  - NCBI Datasets reports complete assembly `GCA_000015865.1`
  - type-material strain `ATCC 27405`
  - BioProject `PRJNA314`

### 3. `firmi_tsac_jwslys485`

- organism: *Thermoanaerobacterium saccharolyticum* JW/SL-YS485
- source accession: `GCA_000307585.2`
- strict label: `clj`
- soft neighbors: `[clj, bsu]`
- competition axis: `clj` vs `bsu`
- admission priority: high
- why this is useful:
  - it broadens the clostridial-side search away from the currently promoted
    *Clostridium* candidates
  - it is a complete genome with industrially interpretable lignocellulose
    relevance
  - if it still fails cleanly, that provides useful negative evidence about the
    current Firmicute axis rather than just repeating the same genus story
- provenance:
  - NCBI Datasets reports complete assembly `GCA_000307585.2`
  - strain `JW/SL-YS485`
  - BioProject `PRJNA73961`

### 4. `firmi_bvelez_fzb42`

- organism: *Bacillus velezensis* FZB42
- source accession: `GCA_000015785.2`
- strict label: `bsu`
- soft neighbors: `[bsu, clj]`
- competition axis: `bsu` vs `clj`
- admission priority: highest
- why this is useful:
  - it stays close enough to the Bacillus side that `bsu` should remain a
    defensible strict label
  - it is more informative than another *B. subtilis* same-species case while
    still avoiding the overly distant Bacilli candidates that previously drifted
    toward non-Firmicute alternatives
  - it is a high-quality reference-grade complete genome with strong
    provenance
- provenance:
  - NCBI Datasets reports reference assembly `GCA_000015785.2`
  - strain `FZB42`
  - BioProject `PRJNA13403`

### 5. `firmi_bamy_dsm7`

- organism: *Bacillus amyloliquefaciens* DSM 7 = ATCC 23350
- source accession: `GCA_000196735.1`
- strict label: `bsu`
- soft neighbors: `[bsu, clj]`
- competition axis: `bsu` vs `clj`
- admission priority: high
- why this is useful:
  - it is a type-material Bacillus genome that should remain close to the
    `bsu` side without collapsing into a trivial same-species benchmark
  - it offers a clean companion to `firmi_bvelez_fzb42`, letting us test
    whether Bacillus-side leverage depends on one strain family or generalizes
  - it is a complete genome with stable provenance
- provenance:
  - NCBI Datasets reports complete assembly `GCA_000196735.1`
  - type-material strain `DSM 7 = ATCC 23350`
  - BioProject `PRJEA41719`

### 6. `firmi_ppol_e681`

- organism: *Paenibacillus polymyxa* E681
- source accession: `GCF_000146875.3`
- strict label: `bsu`
- soft neighbors: `[bsu, clj]`
- competition axis: `bsu` vs `clj`
- admission priority: medium
- why this is useful:
  - it stretches the Bacilli-side search beyond the *Bacillus* genus while
    staying within an interpretable low-GC Gram-positive neighborhood
  - it is a complete genome that can test whether a slightly more distant
    Bacilli-side organism creates cleaner leverage than the previously screened
    reserve cases
  - it also serves as a useful negative-control candidate if it collapses away
    from the intended axis
- provenance:
  - NCBI Datasets reports complete assembly `GCF_000146875.3`
  - strain `E681`
  - BioProject `PRJNA16065`

## Recommended Intake Order

1. `firmi_cace_atcc824`
2. `firmi_bvelez_fzb42`
3. `firmi_bamy_dsm7`
4. `firmi_cthe_atcc27405`
5. `firmi_tsac_jwslys485`
6. `firmi_ppol_e681`

Why this order:

- the first three have the best combination of strong provenance and cleaner
  expected `clj`-vs-`bsu` interpretability
- the next two broaden the clostridial side without relying on one genus
- the last candidate is useful, but its more distant Bacilli-side placement may
  still drift to an unintended competitor

## Practical Admission Policy

Admit all round-3 candidates first only as:

- `evaluation_tier: boundary_screening`
- recommendation-only cases

Do **not** add reference SBML for them yet.

The immediate goal is to improve ranking discrimination, not to increase
approximate E2E baggage.

## Immediate Next Action

1. stage the six query inputs
2. run recommendation-only intake smoke
3. promote only candidates with interpretable `clj`-vs-`bsu` top-2 or top-3
   competition
4. probe the promoted subset under stable vs stressed settings
