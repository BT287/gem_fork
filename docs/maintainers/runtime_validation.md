# Runtime Validation And Platform Notes

Use this note when you are validating the runtime stack, the recommendation smoke path, or the full reconstruction path.

## Basic Verification

```bash
diamond --version
python run_gmsm.py -h
tox -e py311
```

## Runtime Stack Diagnostics

```bash
python scripts/check_runtime_stack.py
python scripts/check_runtime_stack.py --require-executable diamond --require-module cobra
python scripts/check_runtime_stack.py --json --output runtime-stack.json
```

## Recommendation Smoke Validation

Cross-platform recommendation smoke validator:

```bash
python scripts/run_template_recommendation_smoke.py --expected-backend diamond --template-backend diamond --report-dir smoke-artifacts
```

The validator runs recommendation-only cases for `--template-rerank-topn 0` and `3`, stores logs and outputs under the report directory, and writes a summary JSON file at `template_recommendation_smoke_summary.json`.

## Windows Local Fallback Validation

```bash
python scripts/check_runtime_stack.py --require-module cobra --require-module optlang --require-module libsbml --require-module swiglpk
python scripts/install_diamond_windows.py
python scripts/run_template_recommendation_smoke.py --expected-backend diamond --template-backend diamond --report-dir smoke-artifacts-windows
```

Before running the Windows fallback validator, install the official `diamond.exe`
with `python scripts/install_diamond_windows.py` or place it on `PATH` / in
`bin/diamond.exe`.

## Full Reconstruction Validation

Manual full-integration validator:

```bash
python scripts/run_full_integration_check.py --expected-backend diamond --template-backend diamond --report-dir full-integration-artifacts
```

This validator runs `run_gmsm.py` through the full `-p -s --auto-template` path, captures the log, and validates the key outputs in:

- `0_template_recommendation`
- `3_primary_metabolic_model`
- `4_complete_model`

## Platform Support

The current divide-and-conquer support plan separates recommendation smoke from full reconstruction:

| Capability | Linux | macOS arm64 | Windows |
| --- | --- | --- | --- |
| Split-environment scaffold | `envs/environment.linux-64.yml` | `envs/environment.osx-arm64.yml` | `envs/environment.win-64.yml` |
| Runtime stack validation | yes | yes | yes |
| Recommendation smoke CI | yes | yes | yes (`diamond`) |
| `--auto-template` fallback without `skani` | yes | yes | yes |
| Full reconstruction integration | manual workflow | manual workflow | not yet |

Interpretation:

- Linux and macOS are the default platforms for `skani`-capable recommendation smoke
- Native Windows is supported for runtime validation and DIAMOND-backed recommendation smoke
- Full reconstruction compatibility is still tracked separately from template recommendation smoke because solver and package compatibility can fail after the recommendation stage

## Maintainer Workflow

Recommended development workflow for maintainers:

1. implement features and quick smoke checks on macOS or Linux
2. validate onboarding and executable resolution on native Windows
3. use CI to keep Linux/macOS `skani` smoke and Windows `diamond` smoke reproducible

This split keeps platform-specific installation failures separate from recommendation logic failures:

- `template-recommendation-smoke.yml` verifies the `skani` path on Linux/macOS and the `diamond` path on Windows
- `scripts/run_template_recommendation_smoke.py` provides a shared local validator for recommendation-only smoke checks
- `scripts/check_runtime_stack.py` provides a shared local validator for the runtime stack across Linux, macOS, and Windows
- `scripts/install_diamond_windows.py` provides a shared installation path for native Windows and Windows CI
- `full-reconstruction-integration.yml` is the manual P2 workflow for Linux and macOS full reconstruction validation

## Repository Positioning

- `gem_fork` should remain the clean source repo to release under the final SBML account
- beginner walkthroughs, rendered examples, and teaching material should not dominate this repo
- this repo should keep a concise quickstart and output reference, not a large tutorial corpus

## Related Docs

- workflow auth note: [../github_workflow_push_auth.md](../github_workflow_push_auth.md)
- release briefing: [../briefing/README.md](../briefing/README.md)
- historical auto-template archive: [../archive/auto_template_history/README.md](../archive/auto_template_history/README.md)
