# Future Intake Smoke Report for Actinomycete Deployment Candidates

## Purpose

This note records the first real staging and recommendation-only smoke pass for
the two actinomycete future-intake candidates:

- `actino_salbus_j1074`
- `actino_amed_s699`

## What Was Done

1. staged both GenBank records into
   `benchmarks/query_assets/deployment_future_intake_candidates/`
2. ran `run_gmsm.py` with:
   - `--auto-template`
   - `--template-recommendation-only`
   - `-p`
3. inspected the resulting recommendation JSON and candidate TSV outputs

## Candidate 1. `actino_salbus_j1074`

- source accession: `CP004370.1`
- current NCBI name: `Streptomyces albidoflavus J1074`
- literature-facing name: `Streptomyces albus J1074`

Observed recommendation:

- top-1: `sco`
- top-2: `mtu`
- top-3: `ppu`
- confidence: `medium`
- final score gap:
  - `sco 0.659849`
  - `mtu 0.482700`
  - gap `= 0.177149`

Interpretation:

- this is a clean promotion result
- the intended actinomycete axis is present
- the top-1 assignment is biologically interpretable
- the score gap is large enough that this is not only a near-tie artifact

Decision:

- promote `actino_salbus_j1074` into the active deployment set

## Candidate 2. `actino_amed_s699`

- source accession: `NC_017186.1`
- organism: `Amycolatopsis mediterranei S699`

Observed recommendation:

- top-1: `sco`
- top-2: `mtu`
- top-3: `eco`
- confidence: `low`
- final score gap:
  - `sco 0.485185`
  - `mtu 0.483893`
  - gap `= 0.001292`

Interpretation:

- the desired actinomycete competition axis is present
- but the top-1 result is almost a tie
- this is good enough for provisional neighbor-based evaluation
- it is not yet strong enough for a strict-template deployment promotion

Decision:

- keep `actino_amed_s699` as a provisional future-intake case
- evaluate it with `expected_taxonomic_neighbors = [mtu, sco]`
- do not assign a strict template yet

## Deployment Set Update

The immediate active deployment set should now move from the original v1 core
to a v2 actinomycete-heavy working set:

1. `sco_sliv_tk24`
2. `actino_sery_nrrl23338`
3. `actino_salbus_j1074`
4. `bsu_py79`

Reserve:

- `sco_sven_atcc10712`
- `eco_w3110`

## V2 Deployment Benchmark Check

The promoted v2 manifest was then benchmarked end-to-end in recommendation-only
mode.

Manifest:

- `benchmarks/deployment_validation_manifest.natural_products_v2.yaml`

Observed aggregate result:

- `passed_case_count = 4`
- `failed_case_count = 0`
- `top1_expected_template_hit_rate = 1.0`
- `top1_expected_neighbor_hit_rate = 1.0`
- `topk_expected_template_hit_rate = 1.0`

Interpretation:

- the active v2 set is internally consistent
- promoting `actino_salbus_j1074` did not destabilize the deployment core
- the deployment core can now be treated as a validated working set

## Why `S. albus` Replaces `S. venezuelae`

- recent literature places `S. albus J1074` closer to mainstream
  Streptomyces-host practice
- the smoke result for `S. albus` is cleaner than the still-literature-only
  status it had before staging
- the deployment set should prioritize the best real-use representative, not
  preserve older placeholders just because they were staged earlier

## Next Recommended Action

1. run the full deployment benchmark on
   `deployment_validation_manifest.natural_products_v2.yaml`
2. keep `actino_amed_s699` as the next provisional actinomycete expansion case
3. only promote `actino_amed_s699` further after repeated stable template
   behavior is confirmed
