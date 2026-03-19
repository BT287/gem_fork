# GMSM (`gem_fork`)

GMSM builds a genome-scale metabolic model (GEM) from a microbial genome and can extend that model with secondary-metabolism reactions derived from antiSMASH-annotated GenBank input.

The code and small reference data live in this repository. Two large runtime
assets are fetched on demand through `scripts/fetch_runtime_assets.py` and
cached locally under `.runtime-assets/`.

## Start Here

Use the path that matches your goal:

| Goal | Start here |
| --- | --- |
| Run GMSM once with the sample input | [Quickstart](#quickstart) and [First Run](#first-run) |
| Use automatic template recommendation | [Auto-Template Recommendation](#auto-template-recommendation) |
| Inspect output file semantics | [OUTPUTS.md](OUTPUTS.md) |
| Validate runtime stack, smoke tests, or full integration | [docs/maintainers/runtime_validation.md](docs/maintainers/runtime_validation.md) |
| Read the current auto-template handoff / next work plan | [AUTO_TEMPLATE_BRIEFING.md](AUTO_TEMPLATE_BRIEFING.md) and [docs/auto_template_next_steps_plan.md](docs/auto_template_next_steps_plan.md) |

## Quickstart

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

### External Requirements

- `diamond` must be available on `PATH` or in the repo-local `bin/` directory
- On Windows, the executable must be `diamond.exe`; a Unix `bin/diamond` file is not usable
- `skani` is optional but recommended if you want genome-level automatic template recommendation
- Runtime augmentation assets are fetched on demand through `scripts/fetch_runtime_assets.py`
- Internet access is required for primary-model augmentation through KEGG

Install DIAMOND after creating the Python environment:

- Linux or macOS:

```bash
conda install -n gmsm -c bioconda -c conda-forge diamond
```

- Windows:
  - preferred: run `python scripts/install_diamond_windows.py`
  - or download the official Windows release of DIAMOND and place `diamond.exe` on `PATH` or in `bin/diamond.exe`
  - if DIAMOND reports a missing runtime, install the Microsoft Visual C++ Redistributable

Fetch the runtime assets required for augmentation and full integration:

```bash
python scripts/fetch_runtime_assets.py
```

Basic verification:

```bash
diamond --version
python scripts/fetch_runtime_assets.py --json
python run_gmsm.py -h
```

### Cross-Platform Environment Option

For cross-platform reproducibility work, the environment is also split into a common base file plus per-platform overlays:

```bash
conda env create -n gmsm -f environment.base.yml
conda env update -n gmsm -f envs/environment.linux-64.yml
```

Swap the second file for your platform:

- `envs/environment.linux-64.yml`
- `envs/environment.osx-arm64.yml`
- `envs/environment.win-64.yml`

Platform note for the split overlays:

- Linux and Windows keep `cobra`, `python-libsbml`, `optlang`, and `swiglpk` in conda
- `osx-arm64` keeps `optlang` and `swiglpk` in conda, then installs `cobra` and `python-libsbml` through `pip`
- this split exists because `python-libsbml` is not currently available as a conda package for `osx-arm64`

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

Automatic template recommendation before primary modeling:

```bash
python run_gmsm.py \
  -i input/NC_021985.1_antismash8.gbk \
  -e input/NC_021985.1_deepec.txt \
  --auto-template \
  -p -s -d -c 4 \
  -o output_auto_template
```

Template recommendation-only smoke run:

```bash
python run_gmsm.py \
  -i input/NC_021985.1_antismash8.gbk \
  --auto-template \
  --template-recommendation-only \
  --template-rerank-topn 0 \
  -p -d \
  -o output_auto_template_smoke
```

Use a fresh `-o` directory name when you want a clean comparison. Reusing an existing output directory overwrites files for the stages you rerun, and an older `4_complete_model/` can remain if you later rerun only `-p`.

## What This Repository Does

Given a genome input, GMSM can:

1. parse genome features and amino-acid sequences
2. optionally recommend a template GEM automatically before reconstruction
3. find homologs against a template GEM using DIAMOND
4. prune unsupported template reactions
5. add primary-metabolism reactions from EC annotations and KEGG
6. add secondary-metabolism reactions from antiSMASH BGC annotations
7. export SBML and review tables for downstream analysis

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

### Sample Inputs In This Repo

| File | Meaning |
| --- | --- |
| `input/NC_021985.1_antismash8.gbk` | sample antiSMASH 8 GenBank input |
| `input/NC_021985.1_deepec.txt` | sample EC prediction file |
| `input/sample_compartment_info.txt` | sample compartment annotation file |
| `input/sample_input_ten_CDS.fasta` | minimal FASTA sample |
| `input/sample_input_two_CDS.gb` | minimal GenBank sample |

## Auto-Template Recommendation

The current `v1` operational default for `--auto-template` is `diamond`.

If you explicitly set `--template-backend auto`, GMSM prefers `skani` when both
of these are available:

- a `skani` executable on `PATH`
- a template genome bank, either under `gmsm/io/data/input1/genomes/` using the filenames in `gmsm/io/data/input1/template_catalog.json`, or via `--template-genome-bank <path>`

If those assets are missing, `--template-backend auto` falls back to a
DIAMOND-based proteome ranking using the bundled template proteomes.

Current support note:

- Linux or WSL: install `skani`, install the template genome bank, then use `--auto-template --template-backend auto`
- macOS: `skani`-first recommendation is supported when the executable and genome bank are available and `--template-backend auto` is selected
- Native Windows: the current supported default is DIAMOND-backed recommendation; use `--template-backend auto` only if you have a working `skani` binary

The current recommendation flow is intentionally staged:

1. coarse template ranking with `skani` when a genome bank is available, otherwise DIAMOND proteome coverage
2. optional reciprocal-hit reranking on only the top `--template-rerank-topn` candidates
3. handoff of the selected template into the existing homology, pruning, augmentation, and secondary-modeling pipeline

Biological intuition:

- the template genome bank is the set of reference organisms that GMSM is allowed to compare against
- `skani` asks which reference genome is closest to the target genome at the whole-genome level
- BBH reranking then asks which of the top candidates best preserves the template model genes at the protein level
- the selected template becomes the starting metabolic scaffold for pruning and augmentation

### Template Genome Bank

If you want `--auto-template` to prefer `skani`, verify the runtime path first:

```bash
skani -V
python scripts/check_template_genome_bank.py --allow-missing
```

Install a template genome bank from a bundle:

```bash
python scripts/fetch_template_genome_bank.py --bundle /path/to/template_genome_bank.zip
python scripts/check_template_genome_bank.py
```

The bundle may be a local `.zip` or `.tar.gz` file or an HTTP(S) URL.

If you want GMSM to download every directly available reference genome from the manifest:

```bash
python scripts/fetch_template_genome_bank.py --from-manifest
python scripts/check_template_genome_bank.py --allow-missing
```

To preview which templates are direct-downloadable versus manual-only:

```bash
python scripts/fetch_template_genome_bank.py --from-manifest --plan
```

See the curated source manifest for the reference genomes behind the template bank:

```bash
python scripts/show_template_genome_sources.py
python scripts/show_template_genome_sources.py --template sco
```

The current curated template panel contains `10` genomes:

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

`10` is the current curated template panel, not a hard limit. A larger panel only makes sense when each added organism has a complete template package in GMSM: a template GEM, the matching template proteome, and the metadata needed for template recommendation and downstream reconstruction.

Maintainers can build a curated release bundle from a complete local bank with:

```bash
python scripts/build_template_genome_bank_bundle.py --output dist/template_genome_bank_v1.zip
```

Bundle layout reference: [gmsm/io/data/input1/template_genome_bundle_spec.md](gmsm/io/data/input1/template_genome_bundle_spec.md)

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

Detailed output reference: [OUTPUTS.md](OUTPUTS.md)

## Common CLI Options

| Option | Meaning |
| --- | --- |
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

## Key Config Defaults

Source: `gmsm/config/gmsm.cfg`

| Parameter | Default | Meaning |
| --- | --- | --- |
| `blastp.evalue` | `1e-30` | DIAMOND hit cutoff for homology acceptance |
| `cobrapy.non_zero_flux_cutoff` | `1e-3` | flux threshold for treating production as non-zero |
| `cobrapy.nutrient_uptake_rate` | `2` | nutrient uptake bound used in model setup |
| `cobrapy.gapfill_iter` | `1` | number of SMILEY gap-filling iterations |
| `utils.time_bomb_duration` | `90` | cache lifetime in days for KEGG-derived data |

## Repository Layout

| Path | Meaning |
| --- | --- |
| `run_gmsm.py` | CLI entrypoint |
| `gmsm/` | implementation package |
| `gmsm/tests/` | pytest suite |
| `input/` | sample inputs |
| `bin/` | local executables such as DIAMOND |
| `scripts/` | helper scripts such as genome-bank validation |
| `docs/` | maintainer notes, handoff plans, and workflow docs |
| `environment.yml` | validated conda environment |
| `requirements.txt` | pip fallback dependency list |

## Maintainer Docs

- Runtime stack, smoke tests, platform matrix, and validation flow: [docs/maintainers/runtime_validation.md](docs/maintainers/runtime_validation.md)
- Workflow push auth note: [docs/github_workflow_push_auth.md](docs/github_workflow_push_auth.md)
- Current branch briefing: [AUTO_TEMPLATE_BRIEFING.md](AUTO_TEMPLATE_BRIEFING.md)
- Concise parameter tuning briefing: [docs/parameter_plan.md](docs/parameter_plan.md)
- Current next-step implementation plan: [docs/auto_template_next_steps_plan.md](docs/auto_template_next_steps_plan.md)

## Troubleshooting

- If `diamond` is not found on Windows, install the official `diamond.exe` and place it on `PATH` or in `bin/diamond.exe`
- If primary modeling stalls, verify internet access to KEGG
- If you have an old environment, recreate it from `environment.yml`
- If you are using antiSMASH 4 input, make sure the input is the GenBank export with `cluster` annotations
