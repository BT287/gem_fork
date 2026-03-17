# Phase 1C Boundary Query Assets

This directory stages GenBank query inputs for harder `Phase 1C`
recommendation-only screening cases.

Recommended intake flow:

1. fetch candidates with `scripts/fetch_phase1c_boundary_assets.py`
2. verify that each `input.gbk` parses with `run_gmsm.py --auto-template`
3. promote only the cleanest candidates into the runnable boundary manifest
