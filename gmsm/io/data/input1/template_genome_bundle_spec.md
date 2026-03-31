# Template Genome Bank Bundle Spec

`template_genome_bank_v1.zip` is the curated reference panel used by `--auto-template` when users want a reproducible local template genome bank.

Biological meaning:

- each FASTA is the canonical reference genome for one template GEM organism
- the bundle therefore defines the finite set of organisms that GMSM can compare against during automatic template recommendation
- `skani` uses these genomes for whole-genome similarity ranking
- BBH reranking then tests which of the top candidates better preserves template model genes at the protein level

Current template panel size: `10` genomes

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

Expected archive layout:

```text
template_genome_bank_v1.zip
├── bundle_manifest.json
├── checksums.tsv
└── genomes/
    ├── bsu.fna
    ├── clj.fna
    ├── cre.fna
    ├── eco.fna
    ├── hpy.fna
    ├── mtu.fna
    ├── nsal.fna
    ├── ppu.fna
    ├── sce.fna
    └── sco.fna
```

Rules:

- all `10` template genomes are included in the curated release bundle
- `checksums.tsv` records the SHA-256 checksum for each FASTA
- `bundle_manifest.json` records the bundle version, template count, per-template relative path, and source metadata snapshot
- `10` is the current curated panel size, not a hard ceiling; the panel should only grow when a new organism has a full template package in GMSM, meaning a template GEM plus the template proteome and metadata needed for pruning and augmentation
- users install the bundle from inside `gem_fork` with:

```bash
python scripts/fetch_template_genome_bank.py --bundle /path/to/template_genome_bank_v1.zip
python scripts/check_template_genome_bank.py
```

Maintainer flow:

```bash
python scripts/build_template_genome_bank_bundle.py --output dist/template_genome_bank_v1.zip
```
