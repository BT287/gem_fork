# bsu_ncib3610 reference model intake

- status: candidate-exact-reconstructed
- query benchmark case: `bsu_ncib3610`
- query organism: *Bacillus subtilis* subsp. subtilis NCIB 3610
- exact-source repository: `https://github.com/jhyun95/Bacillus_Pan_Genome_Model`
- exact-source assets:
  - `Models/pan_model.mat`
  - `Models/rxn_strain_matrix.mat`
  - `Models/strain_list.mat`
- exact-source accession evidence:
  - `GCF_006088795_1` is present in the published `strain_list.mat`
- locally reconstructed exact candidate:
  - `benchmarks/reference_models/bsu_ncib3610/model_exact_candidate.xml`
  - `benchmarks/reference_models/bsu_ncib3610/model_exact_candidate.summary.json`
- exact-candidate summary:
  - pan-model reactions: `2239`
  - strain reactions: `2188`
  - pan-model genes: `2424`
  - strain genes: `2398`
- why not admitted yet:
  - same-strain exactness is now stronger than the old `iYO844` fallback
  - however, this SBML is reconstructed from a public pan-model source rather
    than taken from an already-admitted curated GEM release
  - NCIB 3610 is also a more divergent Bacillus case than `bsu_py79`, so source
    trust and interpretation policy should be explicit before promotion
- priority note:
  - keep behind `bsu_py79` in the Phase 2 exact-source review queue
- approximate fallback SBML:
  - `benchmarks/reference_models/bsu_ncib3610/model.xml`
  - exported locally from the shipped `bsu` template pickle for controlled
    approximate-reference tuning runs
- promotion rule:
  - use only as `secondary_approximate` or `candidate-exact-reconstructed`
    evidence until the project explicitly accepts this public source into the
    primary exact-reference objective
