# Phase 3 Pilot Report: `eco_w3110` Narrow 4-Config Tuning Run

## Purpose

This note records the first real `Phase 3` tuning pilot after the initial
runner implementation.

The goal of this pilot was not to declare a final best weight setting.

The goal was to answer a narrower operational question:

- does the new tuning runner execute a small exact-case grid end to end and
  produce a sortable summary?

## Run Definition

Case set:

- `eco_w3110`

Backend:

- `diamond`

Search grid:

- `template_diamond_hit_weight in {0.75, 0.95}`
- `template_bbh_template_weight in {0.5, 0.9}`
- `template_coarse_weight = 0.6`
- `template_rerank_topn = 1`

Total configurations:

- `4`

Output directory:

- `benchmark-results/phase3-pilot-eco_w3110-4cfg/`

## What Completed Successfully

- the tuning runner executed all four configurations
- each configuration produced a full reconstruction
- each configuration produced an E2E evaluation entry
- the runner wrote:
  - `tuning_summary.json`
  - `tuning_results.tsv`

## Observed Result

All four configurations produced the same top-level outcome on this one exact
case:

- selected template: `eco`
- reaction F1: `0.912203`
- top1 expected-template hit rate: `1.0`
- alias-gene F1: `0.146108`

So the four configurations were operationally distinguishable as inputs, but
not distinguishable by the current single-case objective.

## Interpretation

This does **not** mean the tuning runner failed.

It means the current pilot was too narrow to separate the tested settings on a
single exact case.

Most likely interpretation:

- all four settings still choose `eco`
- downstream reconstruction then lands on the same primary model
- therefore the reaction-level E2E objective is unchanged

This is exactly the kind of result that should be learned early with a narrow
pilot rather than after launching a large sweep.

## Decision From This Pilot

The next tuning block should **not** immediately scale to a very large grid.

It should first increase discriminative power in one of two ways:

1. add more admitted reference cases
2. widen the search along dimensions more likely to change the selected
   template or BBH structure

## Recommended Next Move

Keep the runner as-is and move to a second pilot with one of these strategies:

- same exact case, but broader search on `template_coarse_weight` and
  `template_rerank_topn`
- or multi-case pilot once another admitted exact reference exists

Do not interpret the first four-config equality as evidence that all weight
settings are globally equivalent.
