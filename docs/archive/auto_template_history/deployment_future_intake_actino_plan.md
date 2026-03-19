# Future Intake Plan for Actinomycete Deployment Cases

## Purpose

This note turns the literature-backed recommendation into the next executable
intake unit.

The immediate deployment set is already defined in
`deployment_validation_manifest.natural_products_v1.yaml`.

The next gap is not another generic benchmark case.

It is a better actinomycete deployment representative than the currently staged
secondary actino cases.

## Chosen Intake Pair

### 1. `actino_salbus_j1074`

- preferred literature name: `Streptomyces albus J1074`
- current NCBI naming: `Streptomyces albidoflavus J1074`
- preferred nucleotide accession: `CP004370.1`
- intended template family: `sco`
- acceptable neighbors: `[sco, mtu]`

Why this is first:

- the current deployment set already has `S. lividans` and `S. venezuelae`
- what it still lacks is the most widely used modern Streptomyces expression
  host from the current literature
- this is the cleanest high-value actinomycete intake now that the immediate
  deployment set exists

Naming policy:

- keep the case ID as `actino_salbus_j1074` because the natural-product
  literature still overwhelmingly uses `S. albus J1074`
- record the NCBI current name in metadata to avoid provenance ambiguity

### 2. `actino_amed_s699`

- organism: `Amycolatopsis mediterranei S699`
- preferred nucleotide accession: `NC_017186.1`
- intended template family: provisional `mtu`
- acceptable neighbors: `[mtu, sco]`

Why this is second:

- it is the strongest missing industrial-producer actinomycete after the
  immediate set
- it complements the `sco`-side Streptomyces / Saccharopolyspora cases with a
  rifamycin-lineage producer

Label policy:

- do not force a strict template label before intake smoke
- first promotion step should use neighbor-based evaluation
- assign a strict template only if the recommendation behavior is stable across
  repeated smoke checks

## Execution Strategy

### Step 1. Source lock

Use complete nucleotide records first:

- `actino_salbus_j1074 -> CP004370.1`
- `actino_amed_s699 -> NC_017186.1`

Completion criteria:

- each case has one preferred accession in repo metadata
- naming ambiguity is resolved in writing before download

### Step 2. Asset staging

Use:

- `scripts/fetch_deployment_future_intake_assets.py`

Output root:

- `benchmarks/query_assets/deployment_future_intake_candidates/`

Completion criteria:

- each case directory contains `input.gbk`
- each case directory contains `download_metadata.json`

### Step 3. Recommendation-only smoke

Run each case with the frozen v1 default:

```bash
conda activate gmsm
python run_gmsm.py \
  -i benchmarks/query_assets/deployment_future_intake_candidates/<case_id>/input.gbk \
  --auto-template \
  --template-recommendation-only \
  -o output_<case_id>
```

Completion criteria:

- parsing succeeds
- recommendation JSON exists
- top-k candidates are interpretable inside the current template panel

### Step 4. Competition audit

Audit:

- top-1 template
- top-2 template
- score margin
- whether the biological axis is interpretable

Desired outcomes:

- `actino_salbus_j1074`: ideally `sco` top-1 and `mtu` top-2
- `actino_amed_s699`: ideally `mtu` or `sco` top-1 with the other actino
  family present in top-2

Failure modes:

- drift to `eco`
- drift to non-actino templates without a plausible biological reason
- large unstable margins between repeated runs

### Step 5. Promotion policy

Promotion target if smoke succeeds:

- `actino_salbus_j1074`
  - promote into `deployment-primary` or `deployment-secondary`
- `actino_amed_s699`
  - first promote into `deployment-secondary` with neighbor-based evaluation
  - promote to strict-label deployment only after stable template behavior is
    confirmed

## Deliverables Added In This Pass

- fetch script:
  - `scripts/fetch_deployment_future_intake_assets.py`
- test file:
  - `gmsm/tests/test_fetch_deployment_future_intake_assets.py`
- draft manifest:
  - `benchmarks/deployment_validation_manifest.future_intake.actino_candidates.yaml`

## Next Recommended Action

Once these assets are staged, the next concrete move is:

1. recommendation-only smoke on both candidates
2. competition audit
3. promote `actino_salbus_j1074` first if it behaves cleanly

This keeps the deployment validation set aligned with actual actinomycete
natural-product work instead of expanding sideways into less relevant species.
