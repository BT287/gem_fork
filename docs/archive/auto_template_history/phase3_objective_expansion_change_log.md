# Phase 3 Objective Expansion Change Log

## Scope

This log summarizes the latest changes after the `Phase 3 + Phase 1C`
integrated pilot and local-search follow-up.

It focuses on two questions:

1. what changed in the benchmark/tuning workflow?
2. what capability improved because of those changes?

## What Changed

### 1. `bsu_ncib3610` secondary-evidence staging

Added:

- `benchmarks/reference_models/bsu_ncib3610/model.xml`
- `benchmarks/phase3_tuning_manifest.phase1c.expanded.yaml`

Supporting policy updates:

- `benchmarks/reference_models/bsu_ncib3610/SOURCE.md`
- `docs/phase2_reference_model_intake_plan.md`

Meaning:

- the Bacillus approximate tier now contains a harder same-species follow-up
  case beyond `bsu_py79`

### 2. Objective-expansion validation pilot

Added result set:

- `benchmark-results/phase3-objective-expansion-bsu3610-2cfg/`

Meaning:

- the widened manifest was executed under both a stable preferred config and a
  previously stressed config

### 3. Reserve boundary probe

Added:

- `benchmarks/phase3_tuning_manifest.phase1c.expanded_with_firmi.yaml`
- `benchmark-results/phase3-firmi-reserve-probe-2cfg/`

Meaning:

- `firmi_blich_dsm13` can now be tested as a provisional boundary case without
  changing the promoted set

## What Improved

### Improved objective coverage

Before:

- exact E2E count = `1`
- approximate E2E count = `2`

After:

- exact E2E count = `1`
- approximate E2E count = `3`

Capability gain:

- the tuning loop now checks whether the preferred config family remains stable
  across one more Bacillus same-species but harder-background case

### Improved admission discipline

Before:

- `bsu_ncib3610` existed only as backlog

After:

- it is explicitly staged as `secondary_approximate`, not silently treated as a
  primary target

Capability gain:

- broader coverage without confusing approximate evidence with exact-reference
  validation

### Improved boundary-case probing workflow

Before:

- reserve boundary candidates were described, but not wired into a reusable
  probe manifest

After:

- a reserve-case probe manifest exists and can be executed directly

Capability gain:

- the project can test whether a reserve candidate adds discrimination before
  promoting it into the standard boundary set

## What Did Not Improve

### The primary objective is still flat

- `primary_exact_reaction_f1_mean` stayed `0.912203`

This means:

- micro-tuning around the current preferred family is still not the best use of
  time

### The reserve Firmicute probe did not add discrimination

`firmi_blich_dsm13` stayed:

- `bsu` under the stable config
- `bsu` under the stressed config

This means:

- it is acceptable biologically
- but it is still weak as a boundary discriminator

## Current Best Interpretation

The recent work improved:

- robustness
- coverage
- admission hygiene

It did **not** yet improve:

- ranking discrimination beyond the already-promoted
  `actino_cglu_atcc13032` signal

## Practical Conclusion

The current preferred family remains:

- `template_backend = diamond`
- `template_coarse_weight = 0.95`
- `template_rerank_topn = 3`
- narrow `template_diamond_hit_weight` and `template_bbh_template_weight`
  neighborhoods inside the already-tested stable band

The next bottleneck is now clear:

- curate one more truly leverage-bearing boundary candidate from outside the
  current reserve pool
