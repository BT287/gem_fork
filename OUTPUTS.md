# GMSM Output Reference

GMSM keeps legacy text outputs for backward compatibility and now also writes canonical files for UI layers and downstream pipelines.

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
