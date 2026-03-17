# Phase 1B Query Asset Staging

This directory is the staging area for the first biologically meaningful
`Phase 1B` benchmark batch.

Each case directory should eventually contain:

- `SOURCE.md`
- `input.gbk`
- optional companion files if later needed

Standard layout:

```text
phase1b_first_batch/
  eco_w3110/
    SOURCE.md
    input.gbk
  eco_bw25113/
    SOURCE.md
    input.gbk
  bsu_py79/
    SOURCE.md
    input.gbk
  bsu_ncib3610/
    SOURCE.md
    input.gbk
  sco_sliv_tk24/
    SOURCE.md
    input.gbk
```

The main benchmark manifest should not reference these paths until the files are
actually downloaded and validated.
