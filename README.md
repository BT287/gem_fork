# GMSM (`gem_fork`)

GMSM builds a genome-scale metabolic model (GEM) from a microbial genome and can extend that model with secondary-metabolism reactions derived from antiSMASH-annotated GenBank input.

This repository is the source-of-truth codebase. Tutorial materials and workspace-level setup belong in `gmsm-workspace`.

## What This Repository Does

Given a genome input, GMSM can:

1. parse genome features and amino-acid sequences
2. find homologs against a template GEM using DIAMOND
3. prune unsupported template reactions
4. add primary-metabolism reactions from EC annotations and KEGG
5. add secondary-metabolism reactions from antiSMASH BGC annotations
6. export SBML and review tables for downstream analysis

## Recommended Runtime

Validated on 2026-03-11:

- Python `3.11`
- `cobra==0.30.0`
- `biopython==1.86`
- `python-libsbml==5.21.1`
- `swiglpk==5.0.13`
- `tox -e py311`

Create the recommended environment:

```bash
conda env create -f environment.yml
conda activate gmsm
```

Fallback without `environment.yml`:

```bash
conda create -n gmsm python=3.11
conda activate gmsm
pip install -r requirements.txt
```

## External Requirements

- `diamond` must be available on `PATH` or in the repo-local `bin/` directory
- Git LFS is required if your checkout stores large assets through LFS
- Internet access is required for primary-model augmentation through KEGG

Git LFS setup:

```bash
git lfs install
git lfs pull
```

Basic verification:

```bash
python run_gmsm.py -h
tox -e py311
```

## Supported Inputs

### antiSMASH versions

- Recommended input version: antiSMASH `8`
- Supported formats:
  - antiSMASH `4` via legacy `cluster` features
  - antiSMASH `5+` via `region` features

### File types

- GenBank: recommended
- FASTA: supported for primary modeling only

### Optional companion inputs

- EC prediction file via `-e`
- EFICAz run via `-E`
- compartment annotation file via `-C`

## First Run

Primary modeling only:

```bash
python run_gmsm.py \
  -i input/NC_021985.1_antismash8.gbk \
  -e input/NC_021985.1_deepec.txt \
  -p -d
```

Secondary modeling only:

```bash
python run_gmsm.py \
  -i input/NC_021985.1_antismash8.gbk \
  -s -d
```

Primary + secondary modeling:

```bash
python run_gmsm.py \
  -i input/NC_021985.1_antismash8.gbk \
  -e input/NC_021985.1_deepec.txt \
  -p -s -d
```

## At-a-Glance Workflow

Use this mental model when reading the repo:

1. prepare genome input and optional EC annotations
2. parse CDS and antiSMASH features
3. run DIAMOND homology against the template GEM
4. prune unsupported template reactions
5. add primary-metabolism reactions from EC and KEGG
6. optionally add secondary-metabolism reactions from BGC annotations
7. export SBML, summaries, and canonical tables

Short form:

`input -> homology -> prune -> primary augmentation -> secondary augmentation -> SBML and reports`

## Pipeline Architecture

| Stage | Main module | Purpose |
|---|---|---|
| Input parsing | `gmsm/io/input_file_manager.py` | load genome records, CDS, EC annotations, BGC counts |
| Homology | `gmsm/homology/` | build DIAMOND databases and reciprocal best hits |
| Primary pruning | `gmsm/primary_model/prunPhase_utils.py` | remove unsupported template reactions and swap GPRs |
| Primary augmentation | `gmsm/primary_model/augPhase_utils.py` | query KEGG and add EC-supported reactions |
| Secondary modeling | `gmsm/secondary_model/` | convert antiSMASH BGC signals into biosynthetic reactions |
| Output export | `gmsm/io/output_file_manager.py` | write SBML, tables, summaries, and review artifacts |

## Input Files

| File | Meaning |
|---|---|
| `input/NC_021985.1_antismash8.gbk` | sample antiSMASH 8 GenBank input |
| `input/NC_021985.1_deepec.txt` | sample EC prediction file |
| `input/sample_compartment_info.txt` | sample compartment annotation file |
| `input/sample_eficaz_output.txt` | sample EFICAz output |
| `input/sample_input_ten_CDS.fasta` | minimal FASTA sample |
| `input/sample_input_two_CDS.gb` | minimal GenBank sample |

## Output Layout

GMSM writes:

- `3_primary_metabolic_model/` for the primary-model stage
- `4_complete_model/` for the final model with secondary metabolism

Each output folder now contains:

- `model.xml`: SBML model
- `summary_report.txt`: legacy text summary
- `summary_report.json`: machine-readable run summary
- `report.md`: human-readable output overview
- `manifest.json`: file inventory for automation
- canonical TSV tables such as `reactions.tsv` and `metabolites.tsv`
- legacy `rmc_*.txt` review files for backward compatibility

Detailed output reference: [OUTPUTS.md](OUTPUTS.md)

## Canonical Output Files

| File | Purpose |
|---|---|
| `summary_report.json` | compact metadata for pipelines and UI layers |
| `report.md` | quick human-readable run report |
| `reactions.tsv` | all reactions |
| `metabolites.tsv` | all metabolites |
| `template_remaining_reactions.tsv` | reactions kept from the template after pruning |
| `kegg_added_reactions.tsv` | reactions added during KEGG augmentation |
| `gpr_notes.tsv` | template-gene carryover and duplicate-gene notes |
| `bgc_fluxes.tsv` | per-BGC export fluxes in complete-model output |
| `gapfilling_needed.tsv` | metabolites still blocking secondary production |

## Key Hyperparameters

Source: `gmsm/config/gmsm.cfg`

| Parameter | Default | Meaning |
|---|---|---|
| `blastp.evalue` | `1e-30` | DIAMOND hit cutoff for homology acceptance |
| `cobrapy.non_zero_flux_cutoff` | `1e-3` | flux threshold for treating production as non-zero |
| `cobrapy.nutrient_uptake_rate` | `2` | nutrient uptake bound used in model setup |
| `cobrapy.gapfill_iter` | `1` | number of SMILEY gap-filling iterations |
| `utils.time_bomb_duration` | `90` | cache lifetime in days for KEGG-derived data |

## CLI Options You Will Actually Use

| Option | Meaning |
|---|---|
| `-i` | input GenBank or FASTA |
| `-o` | output directory |
| `-m` | template GEM organism |
| `-e` | EC prediction file |
| `-p` | primary modeling |
| `-s` | secondary modeling |
| `-E` | run EFICAz |
| `-C` | compartment annotation file |
| `-c` | CPU count |
| `-d` | debug logging |
| `-v` | verbose logging |

## Repository Structure

| Path | Meaning |
|---|---|
| `run_gmsm.py` | CLI entrypoint |
| `gmsm/` | implementation package |
| `gmsm/tests/` | pytest suite |
| `input/` | sample inputs |
| `bin/` | local executables such as DIAMOND |
| `environment.yml` | validated conda environment |
| `requirements.txt` | pip fallback dependency list |

## Which Document to Read First

- New user who just wants to run GMSM once:
  - start in `gmsm-workspace/README.md`
  - then read `gmsm-workspace/gmsm_setup_guide.md`
- User who wants the code-level pipeline and supported inputs:
  - read this README
- User who wants output semantics for UI or downstream automation:
  - read [OUTPUTS.md](OUTPUTS.md)
- User who wants repository-role guidance:
  - read `gmsm-workspace/REPOSITORY_STRATEGY.md`

## Release Positioning

- `gem_fork` should remain the clean source repo to release under the final SBML account
- beginner walkthroughs, rendered examples, and teaching material should not dominate this repo
- this repo should keep a concise quickstart and output reference, not a large tutorial corpus

## Troubleshooting

- If `diamond` is not found, install it or use the local `bin/diamond*` binary
- If primary modeling stalls, verify internet access to KEGG
- If you have an old environment, recreate it from `environment.yml`
- If you are using antiSMASH 4 input, make sure the input is the GenBank export with `cluster` annotations
