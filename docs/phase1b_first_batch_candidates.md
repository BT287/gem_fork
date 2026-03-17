# Phase 1B First Batch Candidates

## Purpose

This file is a working draft for the first biologically meaningful `Phase 1B`
benchmark batch.

It is intentionally **not** the runnable benchmark manifest yet.

Reason:

- the recommended organisms are selected
- the expected-template rationale is documented
- the local query asset paths still need to be populated after download and validation

Use this file to curate the first batch before editing
`benchmarks/auto_template_benchmark_manifest.yaml`.

## Selection Rule

The first batch should favor:

- same-species, non-template strains with clean provenance
- complete genomes with stable assembly accessions
- simple expected-template arguments

The target shape is:

- `4` strict same-species cases
- `1` softer same-clade case

This gives a better first biological benchmark than adding many weaker cases.

## Recommended First Batch

### 1. `eco_w3110`

- organism: *Escherichia coli* str. K-12 substr. W3110
- assembly accession: `GCA_000010245.1`
- expected template: `eco`
- confidence of label: strong
- rationale: same K-12 lineage as the curated `eco` template strain MG1655
- source:
  - https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_000010245.1
  - https://pubmed.ncbi.nlm.nih.gov/16738553/

### 2. `eco_bw25113`

- organism: *Escherichia coli* BW25113
- assembly accession: `GCA_000750555.1`
- expected template: `eco`
- confidence of label: strong
- rationale: well-known K-12 derivative and a defensible non-template `eco` benchmark case
- source:
  - https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_000750555.1
  - https://pubmed.ncbi.nlm.nih.gov/25323716/

### 3. `bsu_py79`

- organism: *Bacillus subtilis* PY79
- assembly accession: `GCA_000497485.1`
- expected template: `bsu`
- confidence of label: strong
- rationale: widely used laboratory strain with complete genome and clear same-species mapping to `bsu`
- source:
  - https://www.ncbi.nlm.nih.gov/bioproject/225627
  - https://pubmed.ncbi.nlm.nih.gov/24356846/

### 4. `bsu_ncib3610`

- organism: *Bacillus subtilis* subsp. subtilis NCIB 3610
- assembly accession: `GCA_006088795.1`
- expected template: `bsu`
- confidence of label: medium to strong
- rationale: same species as `bsu`, but less domesticated than strain 168, making it a useful non-trivial generalization case
- source:
  - https://www.ncbi.nlm.nih.gov/datasets/genome/GCA_006088795.1
  - https://pubmed.ncbi.nlm.nih.gov/28522717/

### 5. `sco_sliv_tk24`

- organism: *Streptomyces lividans* TK24
- assembly accession: `GCA_000739105.1`
- expected template: `sco`
- confidence of label: medium
- rationale: not same-species; keep as a same-clade case because TK24 is a close genetic relative of *Streptomyces coelicolor* A3(2)
- source:
  - https://www.ncbi.nlm.nih.gov/bioproject/257077
  - https://pubmed.ncbi.nlm.nih.gov/33935985/

## Provisional Manifest Entry Draft

Replace `TODO_LOCAL_PATH` only after the downloaded input files are checked for:

- correct strain / assembly provenance
- matching genome and optional EC companion file
- parseability by `run_gmsm.py`

```yaml
manifest_version: 1
description: >
  Draft Phase 1B first batch. Do not run until local query asset paths are populated
  and provenance has been rechecked.
cases:
  - case_id: eco_w3110
    query_input: TODO_LOCAL_PATH/eco_w3110/input.gbk
    ec_file: null
    reference_model: null
    expected_template: eco
    expected_taxonomic_neighbors: [eco]
    exclude_templates: []
    tags: [phase1b, same-species, ecoli, strict-label]
    notes: Non-template E. coli K-12 W3110 case expected to map to eco.
    source_accession: GCA_000010245.1
    organism_name: Escherichia coli str. K-12 substr. W3110
    strain_name: W3110
    provenance: NCBI Datasets assembly GCA_000010245.1

  - case_id: eco_bw25113
    query_input: TODO_LOCAL_PATH/eco_bw25113/input.gbk
    ec_file: null
    reference_model: null
    expected_template: eco
    expected_taxonomic_neighbors: [eco]
    exclude_templates: []
    tags: [phase1b, same-species, ecoli, strict-label]
    notes: Non-template E. coli BW25113 case expected to map to eco.
    source_accession: GCA_000750555.1
    organism_name: Escherichia coli BW25113
    strain_name: BW25113
    provenance: NCBI Datasets assembly GCA_000750555.1

  - case_id: bsu_py79
    query_input: TODO_LOCAL_PATH/bsu_py79/input.gbk
    ec_file: null
    reference_model: null
    expected_template: bsu
    expected_taxonomic_neighbors: [bsu]
    exclude_templates: []
    tags: [phase1b, same-species, bacillus, strict-label]
    notes: Non-template Bacillus subtilis PY79 case expected to map to bsu.
    source_accession: GCA_000497485.1
    organism_name: Bacillus subtilis PY79
    strain_name: PY79
    provenance: NCBI Datasets assembly GCA_000497485.1

  - case_id: bsu_ncib3610
    query_input: TODO_LOCAL_PATH/bsu_ncib3610/input.gbk
    ec_file: null
    reference_model: null
    expected_template: bsu
    expected_taxonomic_neighbors: [bsu]
    exclude_templates: []
    tags: [phase1b, same-species, bacillus, strict-label]
    notes: Non-template Bacillus subtilis NCIB 3610 case expected to map to bsu.
    source_accession: GCA_006088795.1
    organism_name: Bacillus subtilis subsp. subtilis NCIB 3610
    strain_name: NCIB 3610
    provenance: NCBI Datasets assembly GCA_006088795.1

  - case_id: sco_sliv_tk24
    query_input: TODO_LOCAL_PATH/sco_sliv_tk24/input.gbk
    ec_file: null
    reference_model: null
    expected_template: sco
    expected_taxonomic_neighbors: [sco]
    exclude_templates: []
    tags: [phase1b, same-clade, streptomyces, soft-label-priority]
    notes: Streptomyces lividans TK24 same-clade case expected to map to sco.
    source_accession: GCA_000739105.1
    organism_name: Streptomyces lividans TK24
    strain_name: TK24
    provenance: NCBI BioProject 257077 / assembly GCA_000739105.1
```

## Immediate Action List

1. Download and stage the five query assets under a reproducible local directory.
2. Verify that each file matches the documented strain and assembly.
3. Replace `TODO_LOCAL_PATH` with real repo-local or stable local paths.
4. Copy the validated entries into `benchmarks/auto_template_benchmark_manifest.yaml`.
5. Run:

```bash
conda activate gmsm
python scripts/run_auto_template_benchmark.py --label phase1b-first-batch
```

## Interpretation Rule

Interpret the first batch in two layers:

- strict layer: does top-1 equal `expected_template`?
- biological layer: is the result inside `expected_taxonomic_neighbors`?

For `sco_sliv_tk24`, the biological layer matters more than a rigid same-species interpretation.
