#!/usr/bin/env python

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile


CASE_SPECS = {
    "actino_cglu_atcc13032": {
        "assembly_accession": "GCA_000196335.1",
        "strict_label": "mtu",
        "soft_neighbors": ["mtu", "sco"],
        "organism_name": "Corynebacterium glutamicum ATCC 13032",
    },
    "clj_cauto_dsm10061": {
        "assembly_accession": "GCA_000484505.2",
        "strict_label": "clj",
        "soft_neighbors": ["clj", "bsu"],
        "organism_name": "Clostridium autoethanogenum DSM 10061",
    },
    "firmi_blich_dsm13": {
        "assembly_accession": "GCA_000008425",
        "strict_label": "bsu",
        "soft_neighbors": ["bsu", "clj"],
        "organism_name": "Bacillus licheniformis DSM 13",
    },
    "sco_sven_atcc10712": {
        "nucleotide_accession": "NC_018750.1",
        "strict_label": "sco",
        "soft_neighbors": ["sco", "mtu"],
        "organism_name": "Streptomyces venezuelae ATCC 10712",
    },
}


def get_repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def get_default_output_root(repo_root):
    return os.path.join(repo_root, "benchmarks", "query_assets", "phase1c_boundary_candidates")


def resolve_case_ids(requested_case_ids):
    if not requested_case_ids:
        return sorted(CASE_SPECS)
    missing = [case_id for case_id in requested_case_ids if case_id not in CASE_SPECS]
    if missing:
        raise RuntimeError("Unknown case IDs: %s" % ", ".join(sorted(missing)))
    return requested_case_ids


def locate_datasets_executable(requested=None):
    if requested:
        return requested
    located = shutil.which("datasets")
    if located:
        return located
    raise RuntimeError("Could not find the 'datasets' CLI. Install the official NCBI Datasets CLI first.")


def extract_zip(archive_path, extract_dir):
    if not zipfile.is_zipfile(archive_path):
        raise RuntimeError("Downloaded archive is not a valid zip file: %s" % archive_path)
    with zipfile.ZipFile(archive_path, "r") as archive:
        archive.extractall(extract_dir)


def find_single_gbff(extract_dir, accession=None):
    gbff_candidates = []
    for root, _dirs, files in os.walk(extract_dir):
        for filename in files:
            lower_name = filename.lower()
            if lower_name.endswith((".gbff", ".gbk", ".gb")):
                gbff_candidates.append(os.path.join(root, filename))

    if not gbff_candidates:
        return None

    if accession:
        accession_matches = [path for path in gbff_candidates if accession in os.path.basename(path)]
        if len(accession_matches) == 1:
            return accession_matches[0]

    genomic_matches = [path for path in gbff_candidates if os.path.basename(path).lower() == "genomic.gbff"]
    if len(genomic_matches) == 1:
        return genomic_matches[0]

    if len(gbff_candidates) == 1:
        return gbff_candidates[0]
    return None


def build_efetch_url(nucleotide_accession):
    return (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        "?db=nuccore&id=%s&rettype=gbwithparts&retmode=text"
    ) % nucleotide_accession


def write_download_metadata(destination_dir, case_id, spec, source_note):
    payload = {
        "case_id": case_id,
        "organism_name": spec["organism_name"],
        "strict_label": spec["strict_label"],
        "soft_neighbors": spec["soft_neighbors"],
        "assembly_accession": spec.get("assembly_accession"),
        "nucleotide_accession": spec.get("nucleotide_accession"),
        "source_note": source_note,
    }
    metadata_path = os.path.join(destination_dir, "download_metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def download_via_datasets(spec, destination_path, datasets_executable, case_id):
    assembly_accession = spec["assembly_accession"]
    with tempfile.TemporaryDirectory(prefix="phase1c-%s-" % case_id) as temp_dir:
        archive_path = os.path.join(temp_dir, "%s.zip" % case_id)
        extract_dir = os.path.join(temp_dir, "extract")
        os.makedirs(extract_dir, exist_ok=True)
        command = [
            datasets_executable,
            "download",
            "genome",
            "accession",
            assembly_accession,
            "--include",
            "gbff",
            "--filename",
            archive_path,
            "--no-progressbar",
        ]
        subprocess.run(command, check=True)
        extract_zip(archive_path, extract_dir)
        source_gbff = find_single_gbff(extract_dir, accession=assembly_accession)
        if source_gbff is None:
            raise RuntimeError(
                "Could not locate a unique GBFF/GenBank file in the downloaded package for %s" % case_id
            )
        shutil.copyfile(source_gbff, destination_path)
        return {
            "download_method": "datasets",
            "datasets_command": command,
            "source_gbff": source_gbff,
        }


def download_via_efetch(spec, destination_path):
    nucleotide_accession = spec["nucleotide_accession"]
    request = urllib.request.Request(
        build_efetch_url(nucleotide_accession),
        headers={"User-Agent": "gmsm-phase1c-boundary-intake/1.0"},
    )
    with urllib.request.urlopen(request) as response:
        payload = response.read()
    if not payload:
        raise RuntimeError("Empty response while downloading %s" % nucleotide_accession)
    with open(destination_path, "wb") as handle:
        handle.write(payload)
    return {
        "download_method": "efetch",
        "efetch_url": build_efetch_url(nucleotide_accession),
    }


def download_case(case_id, spec, output_root, datasets_executable=None, overwrite=False):
    case_dir = os.path.join(output_root, case_id)
    os.makedirs(case_dir, exist_ok=True)
    destination_path = os.path.join(case_dir, "input.gbk")
    if os.path.exists(destination_path) and not overwrite:
        print("Skipping existing case: %s" % case_id)
        return destination_path

    if spec.get("assembly_accession"):
        source_note = download_via_datasets(spec, destination_path, datasets_executable, case_id)
    elif spec.get("nucleotide_accession"):
        source_note = download_via_efetch(spec, destination_path)
    else:
        raise RuntimeError("Case '%s' is missing both assembly and nucleotide accessions" % case_id)

    write_download_metadata(case_dir, case_id, spec, source_note)
    return destination_path


def main():
    repo_root = get_repo_root()
    parser = argparse.ArgumentParser(
        description="Download and stage Phase 1C boundary candidate GenBank assets."
    )
    parser.add_argument(
        "--case-id",
        action="append",
        default=[],
        help="Specific benchmark case ID to fetch (repeatable). Default: all known cases.",
    )
    parser.add_argument(
        "--output-root",
        default=get_default_output_root(repo_root),
        help="Directory where the staged case directories will be written.",
    )
    parser.add_argument(
        "--datasets",
        default=None,
        help="Path to the 'datasets' executable. Default: resolve from PATH.",
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

    datasets_executable = None
    if any(CASE_SPECS[case_id].get("assembly_accession") for case_id in case_ids):
        datasets_executable = locate_datasets_executable(args.datasets)

    for case_id in case_ids:
        spec = CASE_SPECS[case_id]
        source_accession = spec.get("assembly_accession") or spec.get("nucleotide_accession")
        print("Fetching %s (%s)" % (case_id, source_accession))
        destination_path = download_case(
            case_id=case_id,
            spec=spec,
            output_root=output_root,
            datasets_executable=datasets_executable,
            overwrite=args.overwrite,
        )
        print("  staged -> %s" % destination_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
