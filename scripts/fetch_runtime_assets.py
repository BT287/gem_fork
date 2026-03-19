#!/usr/bin/env python

import argparse
import json
import sys
from os.path import abspath, dirname, join

sys.path.insert(0, abspath(join(dirname(__file__), "..")))

from gmsm import runtime_assets


def build_parser():
    parser = argparse.ArgumentParser(
        description="Fetch runtime assets that are distributed outside Git LFS."
    )
    parser.add_argument(
        "--manifest",
        default=str(runtime_assets.get_default_manifest_path()),
        help="Path to the runtime asset manifest JSON file.",
    )
    parser.add_argument(
        "--asset-root",
        default=str(runtime_assets.get_runtime_asset_root()),
        help="Directory where fetched runtime assets should be stored.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download assets even if a valid cached copy already exists.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the fetch result as JSON.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    result = runtime_assets.fetch_runtime_assets(
        manifest_path=args.manifest,
        asset_root=args.asset_root,
        force=args.force,
    )

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Runtime asset root: {result['asset_root']}")
        for asset in result["assets"]:
            print(f"[{asset['status']}] {asset['name']} -> {asset['path']}")


if __name__ == "__main__":
    main()
