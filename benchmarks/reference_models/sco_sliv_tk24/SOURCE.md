# sco_sliv_tk24 reference model intake

- status: pending-source
- query benchmark case: `sco_sliv_tk24`
- query organism: *Streptomyces lividans* TK24
- current direction:
  - evaluate whether a stable published `Sco-GEM` / `iKS1317`-family SBML
    should be staged as a same-clade reference
- candidate upstream project:
  - https://github.com/SysBioChalmers/Sco-GEM
- why not admitted yet:
  - this benchmark case is same-clade, not same-species
  - the template-stage label is already soft
  - admitting a clade-level reference too early would mix biological ambiguity
    with evaluator debugging
- promotion rule:
  - revisit only after at least one exact same-strain E2E case is complete and
    approximate-case policy is explicit
