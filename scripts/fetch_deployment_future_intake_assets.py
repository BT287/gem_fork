#!/usr/bin/env python

import argparse
import json
import os
import sys
import urllib.request


CASE_SPECS = {
    "actino_salbus_j1074": {
        "nucleotide_accession": "CP004370.1",
        "organism_name": "Streptomyces albidoflavus J1074",
        "legacy_literature_name": "Streptomyces albus J1074",
        "expected_template": "sco",
        "soft_neighbors": ["sco", "mtu"],
    },
    "actino_amed_s699": {
        "nucleotide_accession": "NC_017186.1",
        "organism_name": "Amycolatopsis mediterranei S699",
        "legacy_literature_name": None,
        "expected_template": None,
        "soft_neighbors": ["mtu", "sco"],
    },
}


def get_repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def get_default_output_root(repo_root):
    return os.path.join(repo_root, "benchmarks", "query_assets", "deployment_future_intake_candidates")


def resolve_case_ids(requested_case_ids):
    if not requested_case_ids:
        return sorted(CASE_SPECS)
    missing = [case_id for case_id in requested_case_ids if case_id not in CASE_SPECS]
    if missing:
        raise RuntimeError("Unknown case IDs: %s" % ", ".join(sorted(missing)))
    return requested_case_ids


def build_efetch_url(nucleotide_accession):
    return (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        "?db=nuccore&id=%s&rettype=gbwithparts&retmode=text"
    ) % nucleotide_accession


def write_download_metadata(destination_dir, case_id, spec):
    payload = {
        "case_id": case_id,
        "nucleotide_accession": spec["nucleotide_accession"],
        "organism_name": spec["organism_name"],
        "legacy_literature_name": spec.get("legacy_literature_name"),
        "expected_template": spec.get("expected_template"),
        "soft_neighbors": spec["soft_neighbors"],
        "source_note": {
            "download_method": "efetch",
            "efetch_url": build_efetch_url(spec["nucleotide_accession"]),
        },
    }
    metadata_path = os.path.join(destination_dir, "download_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def download_case(case_id, spec, output_root, overwrite=False):
    case_dir = os.path.join(output_root, case_id)
    os.makedirs(case_dir, exist_ok=True)
    destination_path = os.path.join(case_dir, "input.gbk")
    if os.path.exists(destination_path) and not overwrite:
        print("Skipping existing case: %s" % case_id)
        return destination_path

    request = urllib.request.Request(
        build_efetch_url(spec["nucleotide_accession"]),
        headers={"User-Agent": "gmsm-deployment-future-intake/1.0"},
    )
    with urllib.request.urlopen(request) as response:
        payload = response.read()
    if not payload:
        raise RuntimeError("Empty response while downloading %s" % spec["nucleotide_accession"])
    with open(destination_path, "wb") as handle:
        handle.write(payload)
    write_download_metadata(case_dir, case_id, spec)
    return destination_path


def main():
    repo_root = get_repo_root()
    parser = argparse.ArgumentParser(
        description="Download and stage the next actinomycete deployment-intake candidates."
    )
    parser.add_argument(
        "--case-id",
        action="append",
        default=[],
        help="Specific future-intake case ID to fetch (repeatable). Default: all known cases.",
    )
    parser.add_argument(
        "--output-root",
        default=get_default_output_root(repo_root),
        help="Directory where the staged case directories will be written.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing staged input.gbk file.",
    )
    args = parser.parse_args()

    case_ids = resolve_case_ids(args.case_id)
    output_root = os.path.abspath(args.output_root)
    os.makedirs(output_root, exist_ok=True)

    for case_id in case_ids:
        spec = CASE_SPECS[case_id]
        print("Fetching %s (%s)" % (case_id, spec["nucleotide_accession"]))
        destination_path = download_case(
            case_id=case_id,
            spec=spec,
            output_root=output_root,
            overwrite=args.overwrite,
        )
        print("  staged -> %s" % destination_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
