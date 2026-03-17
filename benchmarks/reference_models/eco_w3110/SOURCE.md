# eco_w3110 reference model

- status: admitted-exact
- query benchmark case: `eco_w3110`
- query organism: *Escherichia coli* str. K-12 substr. W3110
- admitted reference model: `iEC1372_W3110`
- source repository: BiGG Models
- source model URL: http://bigg.ucsd.edu/static/models/iEC1372_W3110.xml
- source metadata URL: http://bigg.ucsd.edu/api/v2/models/iEC1372_W3110
- reference PMID: `27667363`
- BiGG genome accession: `NC_007779.1`
- local staged file: `model.xml`
- mapping rationale:
  - exact same-strain reference model for the `eco_w3110` benchmark query
  - this is the first admitted `Phase 2` E2E reference because it avoids the
    strain-mismatch noise present in approximate cases
- admission note:
  - use this case first for primary-model E2E validation before promoting
    approximate references
