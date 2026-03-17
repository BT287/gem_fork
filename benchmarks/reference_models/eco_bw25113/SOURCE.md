# eco_bw25113 reference model intake

- status: candidate-approximate
- query benchmark case: `eco_bw25113`
- query organism: *Escherichia coli* BW25113
- current candidate reference model: `iML1515`
- candidate source repository: BiGG Models
- candidate model URL: http://bigg.ucsd.edu/static/models/iML1515.xml
- candidate metadata URL: http://bigg.ucsd.edu/api/v2/models/iML1515
- reference PMID: `29020004`
- candidate organism: *Escherichia coli* str. K-12 substr. MG1655
- why not admitted yet:
  - strong same-lineage approximation, but not the same strain
  - this is useful for later sensitivity analysis, not the first exact E2E
    anchor
- promotion rule:
  - do not set `reference_model` in the main benchmark manifest until the exact
    W3110 loop is stable and the project explicitly accepts approximate
    same-lineage references
