#**GMSM**

***G***enome-scale metabolic ***M***odeling with ***S***econdary
***M***etabolism (GMSM) automatically generates secondary metabolite
biosynthetic reactions in a genome-scale metabolic model (GEM) from microbial
genome input, with antiSMASH-annotated GenBank support for secondary
metabolism. GMSM enables high-throughput modeling of both primary and
secondary metabolism, and the current release also supports automatic template
recommendation before primary-model reconstruction.

#Development

This project was initiated as a research collaboration between
[Metabolic & Biomolecular Eng. Nat'l Research Laboratory (MBEL) & BioInformatics Research Center](http://mbel.kaist.ac.kr/)
at KAIST and
[Novo Nordisk Foundation Center for Biosustainability](http://www.biosustain.dtu.dk/english)
at DTU.

#Current features

- Metabolic modeling for primary metabolism
- Metabolic modeling for secondary metabolism
- Automatic template recommendation with `--auto-template`
- Cross-platform runtime validation on Linux, macOS, and Windows
- Full reconstruction integration validated on Linux and macOS

#Installation

###Recommended environment

Create and activate the validated environment:

```bash
conda env create -f environment.yml
conda activate gmsm
```

If you prefer the split platform overlays:

```bash
conda env create -n gmsm -f environment.base.yml
conda env update -n gmsm -f envs/environment.linux-64.yml
```

Swap the second file for your platform:

- `envs/environment.linux-64.yml`
- `envs/environment.osx-arm64.yml`
- `envs/environment.win-64.yml`

###Major runtime requirements

- `diamond` must be available on `PATH` or in `bin/`
- On Windows, the executable must be `diamond.exe`
- `skani` is optional and only needed if you want genome-level auto-template
  retrieval with `--template-backend auto`
- Runtime augmentation assets must be fetched with
  `scripts/fetch_runtime_assets.py`
- Internet access is required for KEGG-based primary-model augmentation

Install DIAMOND after creating the Python environment:

- Linux or macOS:

```bash
conda install -n gmsm -c bioconda -c conda-forge diamond
```

- Windows:

```bash
python scripts/install_diamond_windows.py
```

Fetch runtime assets required for augmentation and full integration:

```bash
python scripts/fetch_runtime_assets.py
```

Basic verification:

```bash
diamond --version
python scripts/fetch_runtime_assets.py --json
python run_gmsm.py -h
```

#Quick start

###Primary metabolism only

```bash
python run_gmsm.py \
  -i input/NC_021985.1_antismash8.gbk \
  -e input/NC_021985.1_deepec.txt \
  -p -d \
  -o output_primary
```

###Primary + secondary metabolism

```bash
python run_gmsm.py \
  -i input/NC_021985.1_antismash8.gbk \
  -e input/NC_021985.1_deepec.txt \
  -p -s -d -c 4 \
  -o output_e2e
```

###Automatic template recommendation

```bash
python run_gmsm.py \
  -i input/NC_021985.1_antismash8.gbk \
  -e input/NC_021985.1_deepec.txt \
  --auto-template \
  -p -s -d -c 4 \
  -o output_auto_template
```

###Recommendation-only smoke run

```bash
python run_gmsm.py \
  -i input/NC_021985.1_antismash8.gbk \
  --auto-template \
  --template-recommendation-only \
  --template-rerank-topn 0 \
  -p -d \
  -o output_auto_template_smoke
```

Use a fresh `-o` directory name when you want a clean comparison. Reusing an
existing directory can leave stale downstream files behind if you rerun only a
subset of stages.

#Auto-template recommendation

The current `v1` operational default is `diamond`.

That means:

- `--auto-template` without extra backend flags uses the DIAMOND-based coarse
  ranking path
- reciprocal-hit reranking is still applied when `--template-rerank-topn > 0`

If you explicitly set `--template-backend auto`, GMSM prefers `skani` when:

- a working `skani` executable is available
- a template genome bank is installed
- the query input is compatible with the genome-level path

Practical support note:

- Linux or macOS: `skani` path is supported when installed explicitly
- Native Windows: use the current DIAMOND-backed default unless you manage
  your own working `skani` binary

Install and validate a template genome bank with:

```bash
python scripts/fetch_template_genome_bank.py --from-manifest
python scripts/check_template_genome_bank.py
```

#Supported inputs

- Recommended genome input: GenBank
- FASTA input: supported for primary modeling only
- Recommended antiSMASH version: `8`
- antiSMASH `4` and `5+` legacy parsing remains supported

Optional companion files:

- EC prediction file via `-e`
- compartment annotation file via `-C`

Automatic EFICAz execution via `-E` is retired in the current supported
workflow. Use an external precomputed EC prediction file with `-e`.

Sample inputs in this repository:

- `input/NC_021985.1_antismash8.gbk`
- `input/NC_021985.1_deepec.txt`
- `input/sample_compartment_info.txt`
- `input/sample_input_ten_CDS.fasta`
- `input/sample_input_two_CDS.gb`

#Platform support

- Linux:
  - runtime stack validated
  - recommendation smoke validated
  - full reconstruction integration validated
- macOS:
  - runtime stack validated
  - recommendation smoke validated
  - full reconstruction integration validated
- Windows:
  - runtime stack validated
  - recommendation smoke validated with `diamond.exe`
  - full reconstruction remains a local/manual target rather than a merge gate

#Repository guide

- Output semantics: [OUTPUTS.md](OUTPUTS.md)
- Release briefing: [docs/briefing/README.md](docs/briefing/README.md)
- Runtime and CI validation notes:
  [docs/maintainers/runtime_validation.md](docs/maintainers/runtime_validation.md)
- Historical phase logs:
  [docs/archive/auto_template_history/README.md](docs/archive/auto_template_history/README.md)

#Troubleshooting

- If `diamond` is missing on Windows, run
  `python scripts/install_diamond_windows.py`
- If primary modeling stalls, verify internet access to KEGG
- If an old environment behaves strangely, recreate it from `environment.yml`
- If you use antiSMASH 4 input, make sure the input file is the GenBank export
  with `cluster` annotations

#Model refinement

Model drafts created by GMSM should still be refined manually. Output files
with prefix `rmc_` provide starting points for manual curation.

#Publication
