# Auto-Template Briefing

Date: 2026-03-13
Branch: `codex/auto-template-phase1`

## 1. What This Branch Changes

This branch adds an automatic template recommendation layer in front of the existing GMSM reconstruction pipeline.

Before this work:
- the user manually chose a template with `-m sco` or a similar option
- the downstream pipeline then ran homology, pruning, augmentation, and optional secondary modeling

After this work:
- the user can run `--auto-template`
- GMSM ranks the available template organisms automatically
- the selected template is then handed off to the existing downstream pipeline

Important design principle:
- the downstream reconstruction engine was intentionally kept intact
- this branch only changes how the starting template is selected

## 2. Biological Intuition

The template is the metabolic starting scaffold.

Biologically, the question is:
- which known reference organism is the target genome most similar to?
- among the close candidates, which one preserves the template model genes most convincingly?

This is why the new system uses two stages:
- whole-genome similarity for coarse filtering
- protein-level reciprocal best hits for metabolic suitability reranking

In short:
- `skani` asks: "Which reference genome is globally closest to the target genome?"
- BBH reranking asks: "Among those close references, which one is the better metabolic template?"

## 3. Current Template Panel

The current curated template panel contains 10 organisms:

- `bsu`
- `clj`
- `cre`
- `eco`
- `hpy`
- `mtu`
- `nsal`
- `ppu`
- `sce`
- `sco`

This is not a hard ceiling.

However, a new template cannot be added by dropping in a genome FASTA alone.
Each template organism must have a complete GMSM template package:
- template GEM
- template proteome
- template metadata
- template genome reference for auto-template ranking

Therefore, the current value `10` means:
- these are the 10 organisms that GMSM can currently use as full template packages

## 4. Implemented Runtime Logic

### Stage 0: Template asset discovery

Code:
- `gmsm/template_recommendation.py`
- `gmsm/io/data/input1/template_catalog.json`
- `gmsm/io/data/input1/template_genome_sources.json`

GMSM discovers:
- template proteome FASTA for each template organism
- template genome FASTA if a local genome bank is installed

### Stage 1: Coarse ranking

CLI:
- `--auto-template`
- `--template-backend {auto,skani,diamond}`
- `--template-topk`
- `--template-genome-bank <path>`

Backend selection:
- if `skani` is available and a template genome bank exists, use `skani`
- otherwise fall back to DIAMOND-based proteome ranking

Current score implementation:
- skani coarse score:
  - `0.7 * normalized ANI + 0.3 * mean aligned fraction`
- DIAMOND fallback coarse score:
  - `0.85 * hit coverage + 0.15 * mean identity`

Why this stage exists:
- it cheaply narrows the candidate set before any more expensive reranking

### Stage 2: BBH reranking

CLI:
- `--template-rerank-topn`

Current tool:
- `DIAMOND`

Current logic:
- only the top-N coarse candidates are reranked
- target proteome vs template proteome is searched both directions
- reciprocal best hits are computed

Current rerank score:
- `0.7 * bbh_template_coverage + 0.3 * bbh_target_coverage`

Final score:
- `0.6 * coarse_score + 0.4 * rerank_score`

Biological meaning:
- `bbh_template_coverage` asks how much of the template model gene space is preserved
- `bbh_target_coverage` asks how much of the target proteome maps back into that template

### Stage 3: Handoff into existing GMSM

Once the final template is selected:
- `run_ns.orgName` is updated
- the existing GMSM flow continues unchanged

Unchanged downstream flow:
- homology
- pruning
- primary augmentation
- secondary modeling
- output export

## 5. Why These Tools Were Chosen

### `skani` for coarse ranking

Why:
- the first problem is genome-level candidate retrieval
- `skani` was designed for fast ANI and aligned-fraction estimation
- ANI alone can overstate similarity when only a small fraction aligns
- AF helps filter those misleading cases

Practical advantage:
- fast candidate narrowing before protein-level reranking

Current caveat:
- in our current Windows environment, `skani` is not available
- therefore native Windows currently uses DIAMOND fallback unless `skani` is installed separately
- the intended validated `skani-first` path is Linux or WSL

Sources:
- `skani` paper: https://www.nature.com/articles/s41592-023-02018-3
- `skani` GitHub: https://github.com/bluenote-1577/skani

### `DIAMOND` for fallback and BBH rerank

Why:
- existing GMSM homology logic already uses DIAMOND
- DIAMOND has strong practical support, especially on Windows
- RBH-style comparison fits the metabolic-template suitability question well

Practical advantage:
- stable integration with the current codebase
- native Windows binary support
- suitable for reciprocal best hit reranking

Sources:
- DIAMOND 2021 paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC8026399/
- DIAMOND install docs: https://github.com/bbuchfink/diamond/wiki/2.-Installation
- RBH comparison paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC7585182/

### Direct template-bank installation

Why:
- users should stay inside `gem_fork`
- they should not have to manually visit another repository to assemble the template bank

Implemented tools:
- `scripts/fetch_template_genome_bank.py`
- `scripts/check_template_genome_bank.py`
- `scripts/build_template_genome_bank_bundle.py`

Source documentation:
- NCBI Datasets genome download docs:
  - https://www.ncbi.nlm.nih.gov/datasets/docs/v2/reference-docs/command-line/datasets/download/genome/

## 6. New User-Facing Outputs

When `--auto-template` is enabled, GMSM writes:
- `0_template_recommendation/template_candidates.tsv`
- `0_template_recommendation/template_recommendation.json`

Meaning:
- `template_candidates.tsv` is the ranking evidence
- `template_recommendation.json` is the machine-readable final decision

These outputs explain:
- which templates were considered
- which backend was used
- whether BBH reranking was applied
- which template was finally selected

## 7. Template Bank and Bundle Status

Implemented:
- curated source manifest
- direct install flow from manifest
- local template bank validator
- curated bundle builder

Current local validation status:
- all 10 template genomes were installed successfully into the local bank
- a curated bundle was generated successfully:
  - `dist/template_genome_bank_v1.zip`

Current bundle spec:
- `gmsm/io/data/input1/template_genome_bundle_spec.md`

## 8. What Has Been Completed So Far

Completed on this branch:
- auto-template CLI and recommendation layer
- skani-first architecture with DIAMOND fallback
- DIAMOND BBH reranking
- recommendation outputs in `0_template_recommendation/`
- template genome source manifest
- template genome bank installer and validator
- curated bundle builder
- completion of the full 10-template bank, including `nsal`

## 9. What Still Needs To Be Done

### Immediate next step

Validate the actual `skani` runtime path on Linux or WSL.

Reason:
- the current Windows machine does not provide a working native `skani`
- therefore Windows is still validating the DIAMOND fallback path, not the intended skani-first path

### Next benchmark step

Compare:
- manual `-m`
- `--auto-template` with DIAMOND fallback
- `--auto-template` with `skani + BBH rerank`

Metrics:
- selected template
- final reaction count
- BGC flux
- gap-filling targets
- runtime

### After that

- decide whether the current 10-template panel should remain the curated core panel
- define whether an additional extended panel is worth maintaining
- consider taxonomy guardrails and multi-template mode in later phases

## 10. Practical Conclusion

This branch does not replace the GMSM reconstruction engine.
It upgrades the template-selection step into a reproducible, explainable, and installable system.

The main remaining technical validation is not the template-bank code.
It is the Linux/WSL benchmark that confirms whether `skani + BBH rerank` improves template choice and runtime enough to become the preferred production path.
