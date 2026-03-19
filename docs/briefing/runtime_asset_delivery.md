# Runtime Asset Delivery

## Why This Exists

The repository currently sits inside a fork network rooted at
`kaist-sbml/gem`. GitHub's LFS billing model for forks means LFS usage can be
charged and blocked at the root network level rather than at the personal fork
level.

That makes Git LFS a poor delivery path for the two runtime-critical binary
assets used by augmentation and full integration:

- `gmsm/io/data/input2/mnxm_compoundInfo_dict.p`
- `scripts/input2_data/mnxref.zip`

## Current Strategy

Short-term delivery path:

- store the two binary assets outside Git LFS
- fetch them with `scripts/fetch_runtime_assets.py`
- cache them under `.runtime-assets/`
- let runtime code prefer the cache when the checked-in file is only an LFS
  pointer

This avoids dirtying the working tree while still letting CI and local users
materialize the assets on demand.

## Why Google Drive Now

Google Drive is the immediate unblock path because the two files already exist
there and are publicly shared.

Analogy:

- Git LFS in the current fork network is a blocked supply line
- Google Drive is a temporary bypass pipe
- `.runtime-assets/` is the local buffer tank

The fetch script pulls the material into the buffer tank and the runtime code
reads from there instead of depending on the blocked line.

## Why Release Assets Later

GitHub Release assets are the longer-term versioned distribution path.

Analogy:

- Google Drive is a workable warehouse shelf
- Release assets are a tagged warehouse bin tied to a software version

With Release assets, a release such as `runtime-assets-v1` can carry the exact
binary files associated with a code version. The fetch manifest can then switch
from Drive file IDs to release URLs without changing the rest of the runtime
logic.

## When To Switch From Drive To Release Assets

Drive is good enough now if:

- the immediate goal is to unblock CI and first-time users
- only a small number of binary assets need to be fetched

Release assets become the better choice when one or more of the following
becomes true:

- the current Drive links become an operational risk
- the project is close to merge and needs a cleaner maintainer story
- multiple versions of the runtime assets need to be tracked explicitly
- the lab wants versioned provenance tied to repository releases

Practical trigger:

- once the Drive-based fetch path is validated in CI and local use, the next
  maintenance cycle should move the same two assets to GitHub Release assets
  and update only the manifest source entries

## Maintainer Rule

The delivery host may change.
The runtime contract should not.

That means:

- keep the fetch script stable
- keep cache paths stable
- keep checksum verification mandatory
- change only the manifest source metadata when moving from Drive to Release
  assets
