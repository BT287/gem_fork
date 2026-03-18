# Deployment Validation Set Plan

## Purpose

The benchmark stack has now reached the point where generic safe-family tuning
is no longer the highest-information next step.

The next step should reflect the actual query GBKs that the project expects to
use in practice.

## Why This Is Now The Best Next Step

Current evidence already established:

- the broad benchmark can reject clearly bad settings
- the current safe family survives exact, approximate, and boundary screening
- even after adding a provisional second exact anchor (`bsu_py79`), the local
  safe family stays flat

So more generic micro-tuning is unlikely to teach much unless the objective is
moved closer to the real deployment distribution.

## Recommended Set Size

Start small:

- `3-5` real query GBKs

That is enough to test whether the current default behaves sensibly on the
organisms the project actually cares about, without creating a long curation
project.

## What Should Enter The Set

Prefer cases that match all of the following:

- likely to appear in real project use
- biologically important to the target workflow
- have a defensible expected template family
- are not already just copies of the benchmark promotion set

## Suggested Tiering

- `deployment-primary`
  - the most common or highest-value query GBKs
- `deployment-secondary`
  - less frequent but still realistic project queries

This deployment set does not need to replace the existing benchmark tiers.

It should sit on top of them as a reality check.

## What To Record For Each Case

- query GBK path
- intended use context
- expected template
- acceptable neighbor templates
- brief reason why this case matters for deployment

## Evaluation Rule

Use the deployment set only after the current benchmark has already rejected
pathological settings.

That means:

- keep boundary screening as the rejection filter
- then compare the surviving safe-family settings on deployment cases

## Completion Criteria

- one deployment manifest exists
- the current default family has been run on it
- the project can state whether the benchmark-tuned default also looks sensible
  on real expected workloads
