# Template Genome Bank

This directory is the default local genome bank for `--auto-template` when `skani` is available.

Expected filenames are defined in [`../template_catalog.json`](../template_catalog.json).

Current expected files:

- `bsu.fna`
- `clj.fna`
- `cre.fna`
- `eco.fna`
- `hpy.fna`
- `mtu.fna`
- `nsal.fna`
- `ppu.fna`
- `sce.fna`
- `sco.fna`

These genome FASTA files are intentionally not tracked in Git by default because they can be large and are better managed as external data assets.

Two supported ways to use a genome bank:

1. Place the expected FASTA files in this directory.
2. Keep the files elsewhere and pass `--template-genome-bank <path>` to `run_gmsm.py`.

You can validate a genome bank with:

```bash
python scripts/check_template_genome_bank.py
python scripts/check_template_genome_bank.py --bank /path/to/template_genomes
```

You can also install a prepared bundle into this directory with:

```bash
python scripts/fetch_template_genome_bank.py --bundle /path/to/template_genome_bank.zip
```

The bundle can be a local archive or an HTTP(S) URL.
