# GMSM Output Reference

GMSM keeps legacy text outputs for backward compatibility and now also writes canonical files for UI layers and downstream pipelines.

When automatic template recommendation is enabled, GMSM also writes a `0_template_recommendation/` stage before the primary-model output directories.

## Design Rules

- legacy files are preserved
- new automation should prefer `summary_report.json`, `manifest.json`, and canonical `*.tsv`
- `model.xml` remains the main SBML artifact

## Core Files

| File | Format | Meaning |
|---|---|---|
| `model.xml` | SBML | exported metabolic model |
| `summary_report.txt` | key-value text | legacy summary |
| `summary_report.json` | JSON | machine-readable summary |
| `report.md` | Markdown | human-readable output report |
| `manifest.json` | JSON | inventory of generated files |

## Template Recommendation Stage

These files appear in `0_template_recommendation/` when `--auto-template` is enabled.

| File | Format | Meaning |
|---|---|---|
| `template_candidates.tsv` | TSV | ranked template candidates with coarse metrics, optional BBH rerank metrics, and the final recommendation score |
| `template_recommendation.json` | JSON | selected template, confidence, backend, strategy, and the retained top-k candidates |

Key columns in `template_candidates.tsv`:

- `coarse_backend`: initial retrieval backend used for ranking
- `coarse_score`: score before any reciprocal-hit reranking
- `primary_metric` / `secondary_metric`: the metrics that actually determined the final ranking
- `bbh_template_coverage`: fraction of template genes supported by reciprocal best hits
- `bbh_target_coverage`: fraction of target genes participating in reciprocal best hits
- `selection_stage`: `coarse` or `coarse+bbh`

## Canonical Tables

| File | Meaning |
|---|---|
| `reactions.tsv` | all reactions in the exported model |
| `metabolites.tsv` | all metabolites in the exported model |
| `template_remaining_reactions.tsv` | template reactions that remained after pruning |
| `kegg_added_reactions.tsv` | reactions added from KEGG |
| `gpr_notes.tsv` | template gene carryover and duplicate-gene notes |
| `bgc_fluxes.tsv` | per-BGC export fluxes in complete-model output only |
| `gapfilling_needed.tsv` | metabolites still blocking secondary production in complete-model output only |

## Legacy Compatibility Files

These are still produced:

- `model_reactions.txt`
- `model_metabolites.txt`
- `rmc_remaining_essential_reactions_from_template_model.txt`
- `rmc_reactions_added_from_kegg.txt`
- `rmc_gpr_associations_from_homology_analysis.txt`
- `rmc_BGCs_fluxes.txt`
- `rmc_metabolites_gapfilling_needed.txt`

## Best File by Use Case

| Use case | Recommended file |
|---|---|
| load model in COBRA tools | `model.xml` |
| show a quick run summary in UI | `summary_report.json` |
| let a human inspect a run in GitHub or VS Code | `report.md` |
| join reactions into another workflow | `reactions.tsv` |
| programmatically discover all outputs | `manifest.json` |
