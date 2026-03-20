# Clean-Room Onboarding Validation

Use this note when you want to validate whether a fresh user can clone the
repository and get the intended `v1` auto-template workflow running without
hidden local state.

This is stronger than ordinary development testing because it checks the path a
new user would actually follow.

## Validation Levels

### Level A. README-Only Onboarding

Goal:

- verify that a new user can follow the public README and reach a working
  recommendation path

Pass condition:

- environment creates successfully
- `diamond` resolves
- runtime assets materialize successfully
- `run_gmsm.py -h` works
- recommendation-only smoke run succeeds

### Level B. Strong Local Validation

Goal:

- verify that the local machine can also execute a primary or full
  reconstruction path after the README-only onboarding path succeeds

Pass condition:

- primary auto-template run succeeds
- optional full `-p -s` run or `run_full_integration_check.py` succeeds

## Windows PowerShell Checklist

Run these commands in a fresh PowerShell session on a machine that does not
already depend on local repo state.

### 1. Fresh clone

```powershell
git clone https://github.com/Hong-Lavi/gem_fork.git
cd gem_fork
git checkout codex/auto-template-phase1
```

### 2. Create the validated environment

```powershell
conda env create -f environment.yml
conda activate gmsm
```

### 3. Install DIAMOND and runtime assets

```powershell
python scripts/install_diamond_windows.py
python scripts/fetch_runtime_assets.py --json
```

### 4. Basic runtime verification

```powershell
diamond --version
python run_gmsm.py -h
python scripts/check_runtime_stack.py --require-executable diamond --require-module cobra --require-module optlang --require-module libsbml --require-module swiglpk
```

### 5. README-only recommendation smoke

```powershell
python run_gmsm.py `
  -i input/NC_021985.1_antismash8.gbk `
  --auto-template `
  --template-recommendation-only `
  --template-rerank-topn 0 `
  -p -d `
  -o output_auto_template_smoke_windows
```

Expected output:

- `output_auto_template_smoke_windows/0_template_recommendation/template_recommendation.json`

### 6. Cross-check with the shared smoke validator

```powershell
python scripts/run_template_recommendation_smoke.py --expected-backend diamond --template-backend diamond --report-dir smoke-artifacts-windows
```

Expected output:

- `smoke-artifacts-windows/template_recommendation_smoke_summary.json`
- final process exit code `0`

### 7. Strong local primary-path validation

```powershell
python run_gmsm.py `
  -i input/NC_021985.1_antismash8.gbk `
  -e input/NC_021985.1_deepec.txt `
  --auto-template `
  -p -d `
  -o output_primary_auto_windows
```

Expected outputs:

- `output_primary_auto_windows/0_template_recommendation/`
- `output_primary_auto_windows/3_primary_metabolic_model/model.xml`

### 8. Optional strong local full validation

If the local Windows runtime is believed to support full reconstruction, use
either the direct CLI path:

```powershell
python run_gmsm.py `
  -i input/NC_021985.1_antismash8.gbk `
  -e input/NC_021985.1_deepec.txt `
  --auto-template `
  -p -s -d -c 4 `
  -o output_e2e_auto_windows
```

or the validator:

```powershell
python scripts/run_full_integration_check.py --expected-backend diamond --template-backend diamond --report-dir full-integration-artifacts-windows
```

## Interpretation

If Level A passes on Windows, the repository is in good shape for a new user
who wants the current deployment-default recommendation workflow.

If Level B also passes on Windows, then the practical gap between:

- "Windows runtime and smoke are supported"

and

- "Windows local end-to-end is known to work on this machine"

is closed for that machine.

This still does not automatically mean:

- Windows full reconstruction should become a CI merge gate

because CI reproducibility and local success are different claims.
