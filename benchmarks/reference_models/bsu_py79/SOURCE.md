# bsu_py79 reference model intake

- status: candidate-exact-reconstructed
- query benchmark case: `bsu_py79`
- query organism: *Bacillus subtilis* PY79
- exact-source repository: `https://github.com/jhyun95/Bacillus_Pan_Genome_Model`
- exact-source assets:
  - `Models/pan_model.mat`
  - `Models/rxn_strain_matrix.mat`
  - `Models/strain_list.mat`
- exact-source accession evidence:
  - `GCF_000497485_1` is present in the published `strain_list.mat`
- locally reconstructed exact candidate:
  - `benchmarks/reference_models/bsu_py79/model_exact_candidate.xml`
  - `benchmarks/reference_models/bsu_py79/model_exact_candidate.summary.json`
- exact-candidate summary:
  - pan-model reactions: `2239`
  - strain reactions: `2186`
  - pan-model genes: `2424`
  - strain genes: `2391`
- why not admitted yet:
  - same-strain exactness is now stronger than the old `iYO844` fallback
  - however, this SBML is reconstructed from a public pan-model source rather
    than taken from an already-admitted curated GEM release
  - source-policy review should therefore happen before promotion into the
    primary exact objective
- approximate fallback SBML:
  - `benchmarks/reference_models/bsu_py79/model.xml`
  - exported locally from the shipped `bsu` template pickle for controlled
    approximate-reference tuning runs
- priority note:
  - this is now the first Bacillus case with a public exact-source candidate
