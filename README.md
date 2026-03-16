# GMSM (`gem_fork`)

GMSM builds a genome-scale metabolic model (GEM) from a microbial genome and can extend that model with secondary-metabolism reactions derived from antiSMASH-annotated GenBank input.

This repository is self-contained. A first-time user should be able to create the environment, run GMSM end-to-end, and inspect outputs from this repo alone.

## What This Repository Does

Given a genome input, GMSM can:

1. parse genome features and amino-acid sequences
2. optionally recommend a template GEM automatically before reconstruction
3. find homologs against a template GEM using DIAMOND
4. prune unsupported template reactions
5. add primary-metabolism reactions from EC annotations and KEGG
6. add secondary-metabolism reactions from antiSMASH BGC annotations
7. export SBML and review tables for downstream analysis

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

For cross-platform reproducibility work, the environment is now also split into a common base file plus per-platform overlays:

```bash
conda env create -n gmsm -f environment.base.yml
conda env update -n gmsm -f envs/environment.linux-64.yml
```

Swap the second file for your platform:

- `envs/environment.linux-64.yml`
- `envs/environment.osx-arm64.yml`
- `envs/environment.win-64.yml`

If you already created `gmsm` before this refresh, update it in place:

```bash
conda env update -n gmsm -f environment.yml --prune
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
- On Windows, the executable must be `diamond.exe`; a Unix `bin/diamond` file is not usable
- `skani` is recommended if you want genome-level automatic template recommendation
- Git LFS is required if your checkout stores large assets through LFS
- Internet access is required for primary-model augmentation through KEGG

Current platform note for `skani`:

- The validated `skani`-first path is Linux or WSL.
- On native Windows, `--auto-template` still works, but it typically falls back to DIAMOND unless you install a working `skani` executable yourself.

Install DIAMOND after creating the Python environment:

- Linux or macOS:

```bash
conda install -n gmsm -c bioconda -c conda-forge diamond
```

- Windows:
  - download the official Windows release of DIAMOND and extract `diamond.exe`
  - place `diamond.exe` on `PATH` or copy it to `bin/diamond.exe`
  - if DIAMOND reports a missing runtime, install the Microsoft Visual C++ Redistributable

Verify DIAMOND before running `tox` or `run_gmsm.py`:

```bash
diamond --version
```

If you want `--auto-template` to prefer `skani`, also verify:

```bash
skani -V
python scripts/check_template_genome_bank.py --allow-missing
```

If `skani` is not available, `--auto-template` will still run with DIAMOND-based coarse ranking and BBH reranking.

Install a template genome bank from a bundle when you are ready to use `skani`-first recommendation:

```bash
python scripts/fetch_template_genome_bank.py --bundle /path/to/template_genome_bank.zip
python scripts/check_template_genome_bank.py
```

The curated release bundle is intended to contain the full template panel as a single reproducible asset. In the current design that panel contains `10` genomes:

- `bsu`
- `clj`
- `cre`
- `eco`
- `hpy`
- `mtu`
- `nsal`
- `ppu`
- `sce`
- `sco`

See the bundle spec in [`gmsm/io/data/input1/template_genome_bundle_spec.md`](gmsm/io/data/input1/template_genome_bundle_spec.md) if you need the exact archive layout.

`10` is the current curated template panel, not a hard limit. A larger panel only makes sense when each added organism has a complete template package in GMSM: a template GEM, the matching template proteome, and the metadata needed for template recommendation and downstream reconstruction. Adding arbitrary reference genomes without those matching template assets does not improve the actual reconstruction pipeline.

See the curated source manifest for the reference genomes behind the template bank:

```bash
python scripts/show_template_genome_sources.py
python scripts/show_template_genome_sources.py --template sco
```

If you want GMSM to download every directly available reference genome from the manifest:

```bash
python scripts/fetch_template_genome_bank.py --from-manifest
python scripts/check_template_genome_bank.py --allow-missing
```

This currently installs all `10` curated templates directly from the manifest. The current direct-download set is `bsu`, `clj`, `cre`, `eco`, `hpy`, `mtu`, `nsal`, `ppu`, `sce`, and `sco`.

Maintainers can build a curated release bundle from a complete local bank with:

```bash
python scripts/build_template_genome_bank_bundle.py --output dist/template_genome_bank_v1.zip
```

Git LFS setup:

```bash
git lfs install
git lfs pull
```

Basic verification:

```bash
diamond --version
python run_gmsm.py -h
tox -e py311
```

Runtime stack diagnostics:

```bash
python scripts/check_runtime_stack.py
python scripts/check_runtime_stack.py --require-executable diamond --require-module cobra
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

Automatic EFICAz execution via `-E` is retired in the current supported workflow. Use a precomputed external EC prediction file with `-e` instead.

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

Automatic template recommendation before primary modeling:

```bash
python run_gmsm.py \
  -i input/NC_021985.1_antismash8.gbk \
  -e input/NC_021985.1_deepec.txt \
  --auto-template \
  -p -s -d -c 4 \
  -o output_auto_template
```

Template recommendation-only smoke test:

```bash
python run_gmsm.py \
  -i input/NC_021985.1_antismash8.gbk \
  --auto-template \
  --template-recommendation-only \
  --template-rerank-topn 0 \
  -p -d \
  -o output_auto_template_smoke
```

Use this mode when you want to verify only the recommendation stage without continuing into homology, pruning, or augmentation.

`--auto-template` now prefers `skani` by default when both of these are available:

- a `skani` executable on `PATH`
- a template genome bank, either under `gmsm/io/data/input1/genomes/` using the filenames in `gmsm/io/data/input1/template_catalog.json`, or via `--template-genome-bank <path>`

If those assets are missing, GMSM falls back to a DIAMOND-based proteome ranking using the bundled template proteomes.

Recommended usage by platform:

- Linux or WSL: install `skani`, install the template genome bank, then use `--auto-template`
- Native Windows: `--auto-template` is still useful, but expect DIAMOND fallback unless you have a working `skani` binary

Current support strategy:

- recommendation-only smoke is the minimum release gate
- `skani`-first recommendation is currently targeted at Linux/WSL and macOS
- Windows remains a supported runtime for DIAMOND-based recommendation and local full runs, but cross-platform CI is being added incrementally

The current recommendation flow is intentionally staged for runtime safety:

1. coarse template ranking with `skani` when a genome bank is available, otherwise DIAMOND proteome coverage
2. optional reciprocal-hit reranking on only the top `--template-rerank-topn` candidates
3. handoff of the selected template into the existing homology, pruning, augmentation, and secondary-modeling pipeline

Biological intuition:

- the template genome bank is the set of reference organisms that GMSM is allowed to compare against
- `skani` asks which reference genome is closest to the target genome at the whole-genome level
- BBH reranking then asks which of the top candidates best preserves the template model genes at the protein level
- the selected template becomes the starting metabolic scaffold for pruning and augmentation

## At-a-Glance Workflow

Use this mental model when reading the repo:

1. prepare genome input and optional EC annotations
2. optionally rank bundled template GEMs and pick the best starting template
3. parse CDS and antiSMASH features
4. run DIAMOND homology against the selected template GEM
5. prune unsupported template reactions
6. add primary-metabolism reactions from EC and KEGG
7. optionally add secondary-metabolism reactions from BGC annotations
8. export SBML, summaries, and canonical tables

Short form:

`input -> optional template recommendation -> homology -> prune -> primary augmentation -> secondary augmentation -> SBML and reports`

## Pipeline Architecture

| Stage | Main module | Purpose |
|---|---|---|
| Template recommendation | `gmsm/template_recommendation.py` | rank template GEM candidates before primary modeling |
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

- `0_template_recommendation/` for optional automatic template ranking
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

When `--auto-template` is enabled, `0_template_recommendation/` contains:

- `template_candidates.tsv`: ranked template candidates with coarse metrics, optional BBH rerank metrics, and the final score
- `template_recommendation.json`: selected template, confidence, and the top-k candidate list

Template genome assets for `skani` are configured through:

- `gmsm/io/data/input1/template_catalog.json`
- `gmsm/io/data/input1/genomes/` by default
- or `--template-genome-bank <path>` for an external genome bank

To validate that a genome bank is complete before running GMSM:

```bash
python scripts/check_template_genome_bank.py
python scripts/check_template_genome_bank.py --bank /path/to/template_genomes
```

To install a bank bundle into the default location:

```bash
python scripts/fetch_template_genome_bank.py --bundle /path/to/template_genome_bank.zip
```

The bundle may be a local `.zip`/`.tar.gz` file or an HTTP(S) URL.

To preview which templates are direct-downloadable versus manual-only:

```bash
python scripts/fetch_template_genome_bank.py --from-manifest --plan
```

Detailed output reference: [OUTPUTS.md](OUTPUTS.md)

## Canonical Output Files

| File | Purpose |
|---|---|
| `0_template_recommendation/template_candidates.tsv` | ranking evidence for the selected template |
| `0_template_recommendation/template_recommendation.json` | machine-readable template recommendation result |
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
| `--auto-template` | automatically rank and select a starting template before primary modeling |
| `--template-backend` | template-ranking backend: `auto`, `skani`, or `diamond` |
| `--template-topk` | number of ranked template candidates to keep in the recommendation output |
| `--template-genome-bank` | external directory containing template genome FASTA files for skani |
| `--template-rerank-topn` | rerank only the top N coarse candidates with reciprocal hits; set `0` to disable reranking |
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
| `scripts/` | helper scripts such as genome-bank validation |
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

## Release Positioning

- `gem_fork` should remain the clean source repo to release under the final SBML account
- beginner walkthroughs, rendered examples, and teaching material should not dominate this repo
- this repo should keep a concise quickstart and output reference, not a large tutorial corpus

## Troubleshooting

- If `diamond` is not found on Windows, install the official `diamond.exe` and place it on `PATH` or in `bin/diamond.exe`
- If primary modeling stalls, verify internet access to KEGG
- If you have an old environment, recreate it from `environment.yml`
- If you are using antiSMASH 4 input, make sure the input is the GenBank export with `cluster` annotations
