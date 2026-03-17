# Why Auto-Template Tuning Must Be Evaluated End-to-End

## Purpose

This note explains why the final parameter objective for auto-template tuning
should be **end-to-end reconstruction quality**, not only template-selection
accuracy.

This is the evaluation rationale behind the later `Phase 2` and `Phase 3`
steps in the parameter plan.

For the concrete `Phase 1B` candidate organisms, see
[phase1b_first_batch_candidates.md](phase1b_first_batch_candidates.md).

## Short Answer

The auto-template system chooses a starting scaffold.

What we actually care about is **the quality of the final reconstructed model**
after homology, pruning, augmentation, optional secondary modeling, and export.

So:

- template-selection accuracy is a useful proxy
- final reconstruction quality is the real objective

## The Core Distinction

These two questions are related, but they are not the same:

1. Did the recommendation stage pick the expected template?
2. Did the full pipeline produce the best final model?

The first question is cheap and useful.

The second question is the real scientific target.

## Why Template Accuracy Alone Is Not Enough

### 1. The "correct" template is not always unique

Some queries have one very clean answer.

Example:

- a non-template *E. coli* K-12 strain such as W3110 is a strong `eco` case

In those cases, strict top-1 template recovery and final model quality often
point in the same direction.

But some queries are less clean.

Example:

- *Streptomyces lividans* TK24 is biologically close to `sco`, but it is not the
  same species as *Streptomyces coelicolor* A3(2)

In a case like that, a strict label such as "must be `sco`" may be a reasonable
benchmark convention, but it is still only a convention.

The true question is whether the chosen template leads to a better reconstructed
model.

### 2. The downstream pipeline is nonlinear

Auto-template selection is only the first stage.

After template choice, GMSM still runs:

- homology search
- pruning
- primary augmentation
- optional secondary-model generation
- optional gapfilling and export

This means a small difference at the recommendation stage does not map
linearly onto final model quality.

Example:

- template A has slightly higher ANI and wins top-1 template ranking
- template B preserves more metabolically relevant genes or pathways
- after pruning and augmentation, template B can yield a better final model

If we optimize only for "pick template A more often," we can improve the proxy
metric while hurting the real objective.

### 3. Template identity is an intermediate decision, not the final product

The user does not ultimately want a template label.

The user wants:

- a better reaction set
- a better gene-reaction mapping
- better pathway retention
- better phenotype agreement, if truth data exist

So the tuning objective should match the delivered artifact.

## Worked Examples

### Example A. Proxy And Final Objective Likely Align

Query:

- non-template *E. coli* W3110

Expected recommendation:

- `eco`

Why this case is useful:

- same-species and same-lineage intuition is strong
- recommendation correctness is easy to interpret
- this is a good `Phase 1B` benchmark case

What it tells us:

- recommendation logic generalizes beyond trivial self-retrieval

What it does **not** prove by itself:

- that the chosen weights are globally best for final reconstruction quality

### Example B. The Strict Label Is Less Stable Than The Biological Goal

Query:

- *Streptomyces lividans* TK24

Benchmark convention:

- likely map to `sco`

Why this case is useful:

- it is a realistic same-clade generalization case

Why strict template accuracy is weaker here:

- the biological question is not only "did we say `sco`?"
- it is also "did the selected scaffold lead to a defensible downstream model?"

This is exactly the kind of case where E2E scoring becomes more important than
a rigid template label.

### Example C. A Better Ranked Template Can Still Produce A Worse Final Model

Suppose two templates are close:

- template A wins the recommendation score by a small margin
- template B has slightly lower coarse similarity, but better retained
  metabolic coverage after homology and pruning

Then:

- recommendation-only tuning may prefer A
- E2E tuning may correctly prefer B

This is why recommendation ranking should be treated as an intermediate signal,
not the final optimization target.

## Practical Evaluation Policy

The recommended policy is layered.

### Layer 1. Recommendation Benchmark

Use recommendation-only benchmark cases to check:

- self-retrieval sanity
- same-species / same-clade generalization
- strict and soft hit behavior
- score-margin behavior

This is what `Phase 1A` and `Phase 1B` are for.

### Layer 2. End-to-End Reconstruction Evaluation

Use final reconstructed models to score:

- reaction precision / recall / F1
- gene precision / recall / F1
- pathway retention or known-function recovery
- phenotype agreement, if available

This is what later `Phase 2` is for.

### Layer 3. Parameter Search

Tune the weights against the **Layer 2** objective.

Use Layer 1 as:

- a regression screen
- a debugging aid
- a sanity check that the recommendation stage is not obviously broken

This is what later `Phase 3` is for.

## Decision Rule

Use template-selection accuracy as a **screening metric**.

Use end-to-end reconstruction quality as the **optimization metric**.

That is the correct split because:

- template choice is an intermediate decision
- final model quality is the real scientific output

## Implication For Current Work

The immediate next step is still `Phase 1B`, not E2E tuning.

Reason:

- there is no point optimizing the final objective until the benchmark query set
  is biologically meaningful

So the correct order is:

1. strengthen the benchmark with non-template query strains
2. add E2E evaluation
3. tune weights against E2E quality

## References

- [parameter_plan.md](parameter_plan.md)
- [phase1b_query_benchmark_plan.md](phase1b_query_benchmark_plan.md)
- [phase1b_first_batch_candidates.md](phase1b_first_batch_candidates.md)
