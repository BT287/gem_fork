# Reference Models For E2E Evaluation

This directory is reserved for trusted reference SBML files used in `Phase 2`
end-to-end evaluation.

Recommended layout:

```text
reference_models/
  <case_id>/
    SOURCE.md
    model.xml
```

Admission rule:

- do not add a reference model until its provenance and organism-to-query
  mapping are documented

Current interpretation split:

- `admitted-exact` models may be used in the primary tuning objective
- `candidate-approximate` models may be staged locally for secondary evidence,
  but should not silently replace exact-reference anchors

These reference models are intended for:

- reaction precision / recall / F1
- gene precision / recall / F1
- later pathway-level and phenotype-level evaluation extensions

Current intake planning note:

- `docs/phase2_reference_model_intake_plan.md`
