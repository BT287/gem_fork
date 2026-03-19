# Auto-Template Release Readiness

## Scope

This note describes what is currently validated strongly enough for merge and
deployment use, and what is still only partially covered.

## What Is Ready

### 1. Recommendation Feature

The auto-template recommendation feature itself is ready for use within the
current intended organism range.

Validated components:

- parameterized template scoring
- recommendation-only benchmark runner
- biologically curated benchmark cases
- SBML-oriented deployment validation set

### 2. Operational Default

The current `v1` operational default is frozen and documented:

- backend: `diamond`
- conservative rerank weighting
- deployment validation performed on the SBML-oriented set

### 3. CI Coverage Intent

The current CI layout is intended to provide:

- `Runtime Stack Matrix`
  - environment and binary availability check
- `Template Recommendation Smoke`
  - recommendation path sanity check across Linux/macOS and Windows
- `Full Reconstruction Integration`
  - auto-template plus primary-model end-to-end check on macOS and Linux

## What Is Not Fully Closed

### 1. Windows Full E2E

Windows currently has runtime-stack and recommendation-smoke coverage, not production-grade full
reconstruction coverage.

Reason:

- the cross-platform dependency path for full GMSM reconstruction is still more
  fragile on Windows than on macOS/Linux

Interpretation:

- recommendation/runtime compatibility is checked on Windows
- full auto-template reconstruction should currently be treated as
  macOS/Linux-validated

### 2. Gene-Level Objective

Gene overlap remains secondary/diagnostic.

Reason:

- namespace mismatch still prevents raw gene metrics from serving as a stable
  primary optimization target

### 3. Universal Generalization

The current merge claim is not:

- "optimal for all microbes"

It is:

- "deployment-ready for the current intended organism mix"

### 4. Runtime Asset Delivery

The two runtime-critical binary assets are no longer intended to be consumed
through Git LFS in CI.

Current direction:

- fetch those assets through the shared external delivery path
- cache them under `.runtime-assets/`
- keep recommendation and reconstruction logic independent from fork-network
  LFS quota

## Merge Recommendation

Merge is justified if the goal is:

- to ship a stable `v1` auto-template workflow for the current lab-oriented
  query range

Merge is not the end of all future work.

It simply marks the point where:

- the recommendation feature is usable
- the default is documented
- the benchmark and deployment rationale are traceable
- the remaining risks are explicit rather than hidden
