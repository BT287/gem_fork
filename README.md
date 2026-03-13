# GMSM

***G***enome-scale metabolic ***M***odeling with ***S***econdary ***M***etabolism (GMSM) builds a genome-scale metabolic model (GEM) from a microbial genome and can extend that model with secondary-metabolism reactions derived from antiSMASH-annotated GenBank input.

#Development
This project was initiated as a research collaboration between [Metabolic & Biomolecular Eng. Nat’l Research Laboratory (MBEL) & BioInformatics Research Center](http://mbel.kaist.ac.kr/) at KAIST and [Novo Nordisk Foundation Center for Biosustainability](http://www.biosustain.dtu.dk/english) at DTU.

## What This Repository Does

Given a genome input, GMSM can:

1. parse genome features and amino-acid sequences
2. find homologs against a template GEM using DIAMOND
3. prune unsupported template reactions
4. add primary-metabolism reactions from EC annotations and KEGG
5. add secondary-metabolism reactions from antiSMASH BGC annotations
6. export SBML and review tables for downstream analysis

## Recommended Runtime and Installation

Validated on 2026-03-11:

- Python `3.11`
- `cobra==0.30.0`
- `biopython==1.86`
- `python-libsbml==5.21.1`
- `swiglpk==5.0.13`
- `tox -e py311`

1. Clone the repository

       git clone https://github.com/kaist-sbml/gem.git

2. Create the recommended environment:

    2-A) From scratch:

        conda env create -f environment.yml
        conda activate gmsm
        

    2-B) If you already created `gmsm` before this refresh, update it in place:
    
        conda env update -n gmsm -f environment.yml --prune
        conda activate gmsm

    2-C) Fallback without `environment.yml`:

        conda create -n gmsm python=3.11
        conda activate gmsm
        pip install -r requirements.txt


## External Requirements

- `diamond` must be available on `PATH` or in the repo-local `bin/` directory
- On Windows, the executable must be `diamond.exe`; a Unix `bin/diamond` file is not usable
- Git LFS is required if your checkout stores large assets through LFS
- Guorbi is required if you need large-scale and faster optimization
- Internet access is required for primary-model augmentation through KEGG

### DIAMOND

Install DIAMOND after creating the Python environment:

- Linux or macOS:

```bash
conda install -n gmsm -c bioconda -c conda-forge diamond
```

- Windows:
  - download the [official Windows release](https://github.com/bbuchfink/diamond/releases) of DIAMOND and extract `diamond.exe` 
  - place `diamond.exe` on `PATH` or copy it to `bin/diamond.exe`
  - if DIAMOND reports a missing runtime, install the Microsoft Visual C++ Redistributable

Verify DIAMOND before running `tox` or `run_gmsm.py`:

```bash
diamond --version
```

### Git LFS setup

```bash
git lfs install
git lfs pull
```

### Gurobi (optional)

1. install Gurobi Optimizer for Python

       conda install -c gurobi

2. Get a *Free Academic* license. [Gurobi license](https://www.gurobi.com/academia/academic-program-and-licenses/)


### Basic verification

```bash
diamond --version
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
- compartment annotation file via `-C`


## First Run

Primary modeling only:

```bash
python run_gmsm.py \
  -i input/NC_021985.1_antismash8.gbk \
  -e input/NC_021985.1_deepec.txt \
  -p -d \
  -o output_primary
```

Secondary modeling only:

```bash
python run_gmsm.py \
  -i input/NC_021985.1_antismash8.gbk \
  -s -d \
  -o output_secondary
```

Primary + secondary modeling:

```bash
python run_gmsm.py \
  -i input/NC_021985.1_antismash8.gbk \
  -e input/NC_021985.1_deepec.txt \
  -p -s -d -c 4 \
  -o output_e2e
```

Use a fresh `-o` directory name when you want a clean comparison. Reusing an existing output directory overwrites files for the stages you rerun, and an older `4_complete_model/` can remain if you later rerun only `-p`.

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
| `cobrapy.nutrient_uptake_rate` | `2` | nutrient uptake fold change bound used in model setup |
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
  - start with this README
  - run one of the commands in `First Run`
- User who wants the code-level pipeline and supported inputs:
  - read this README
- User who wants output semantics for UI or downstream automation:
  - read [OUTPUTS.md](OUTPUTS.md)
- User who is using an external tutorial workspace:
  - read that workspace's README after finishing the setup in this repo
