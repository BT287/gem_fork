#!/usr/bin/env python

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile


CASE_SPECS = {
    'eco_w3110': {
        'assembly_accession': 'GCA_000010245.1',
        'expected_template': 'eco',
        'organism_name': 'Escherichia coli str. K-12 substr. W3110',
    },
    'eco_bw25113': {
        'assembly_accession': 'GCA_000750555.1',
        'expected_template': 'eco',
        'organism_name': 'Escherichia coli BW25113',
    },
    'bsu_py79': {
        'assembly_accession': 'GCA_000497485.1',
        'expected_template': 'bsu',
        'organism_name': 'Bacillus subtilis PY79',
    },
    'bsu_ncib3610': {
        'assembly_accession': 'GCA_006088795.1',
        'expected_template': 'bsu',
        'organism_name': 'Bacillus subtilis subsp. subtilis NCIB 3610',
    },
    'sco_sliv_tk24': {
        'assembly_accession': 'GCA_000739105.1',
        'expected_template': 'sco',
        'organism_name': 'Streptomyces lividans TK24',
    },
}


def get_repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def get_default_output_root(repo_root):
    return os.path.join(repo_root, 'benchmarks', 'query_assets', 'phase1b_first_batch')


def resolve_case_ids(requested_case_ids):
    if not requested_case_ids:
        return sorted(CASE_SPECS)

    missing = [case_id for case_id in requested_case_ids if case_id not in CASE_SPECS]
    if missing:
        raise RuntimeError('Unknown case IDs: %s' % ', '.join(sorted(missing)))
    return requested_case_ids


def locate_datasets_executable(requested=None):
    if requested:
        return requested
    located = shutil.which('datasets')
    if located:
        return located
    raise RuntimeError(
        "Could not find the 'datasets' CLI. Install the official NCBI Datasets CLI first."
    )


def extract_zip(archive_path, extract_dir):
    if not zipfile.is_zipfile(archive_path):
        raise RuntimeError('Downloaded archive is not a valid zip file: %s' % archive_path)
    with zipfile.ZipFile(archive_path, 'r') as archive:
        archive.extractall(extract_dir)


def find_single_gbff(extract_dir, accession=None):
    gbff_candidates = []
    for root, _dirs, files in os.walk(extract_dir):
        for filename in files:
            lower_name = filename.lower()
            if lower_name.endswith(('.gbff', '.gbk', '.gb')):
                gbff_candidates.append(os.path.join(root, filename))

    if not gbff_candidates:
        return None

    if accession:
        accession_matches = [path for path in gbff_candidates if accession in os.path.basename(path)]
        if len(accession_matches) == 1:
            return accession_matches[0]

    genomic_matches = [path for path in gbff_candidates if os.path.basename(path).lower() == 'genomic.gbff']
    if len(genomic_matches) == 1:
        return genomic_matches[0]

    if len(gbff_candidates) == 1:
        return gbff_candidates[0]

    return None


def write_download_metadata(destination_dir, case_id, spec, datasets_command, source_gbff):
    payload = {
        'case_id': case_id,
        'assembly_accession': spec['assembly_accession'],
        'expected_template': spec['expected_template'],
        'organism_name': spec['organism_name'],
        'datasets_command': datasets_command,
        'source_gbff': source_gbff,
    }
    metadata_path = os.path.join(destination_dir, 'download_metadata.json')
    with open(metadata_path, 'w', encoding='utf-8') as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write('\n')


def download_case(case_id, spec, output_root, datasets_executable, overwrite=False):
    case_dir = os.path.join(output_root, case_id)
    os.makedirs(case_dir, exist_ok=True)
    destination_path = os.path.join(case_dir, 'input.gbk')
    if os.path.exists(destination_path) and not overwrite:
        print('Skipping existing case: %s' % case_id)
        return destination_path

    with tempfile.TemporaryDirectory(prefix='phase1b-%s-' % case_id) as temp_dir:
        archive_path = os.path.join(temp_dir, '%s.zip' % case_id)
        extract_dir = os.path.join(temp_dir, 'extract')
        os.makedirs(extract_dir, exist_ok=True)
        command = [
            datasets_executable,
            'download',
            'genome',
            'accession',
            spec['assembly_accession'],
            '--include',
            'gbff',
            '--filename',
            archive_path,
            '--no-progressbar',
        ]
        subprocess.run(command, check=True)
        extract_zip(archive_path, extract_dir)
        source_gbff = find_single_gbff(extract_dir, accession=spec['assembly_accession'])
        if source_gbff is None:
            raise RuntimeError(
                'Could not locate a unique GBFF/GenBank file in the downloaded package for %s'
                % case_id
            )
        shutil.copyfile(source_gbff, destination_path)
        write_download_metadata(case_dir, case_id, spec, command, source_gbff)
        return destination_path


def main():
    repo_root = get_repo_root()
    parser = argparse.ArgumentParser(
        description='Download and stage the first Phase 1B query benchmark assets via the official NCBI Datasets CLI.'
    )
    parser.add_argument(
        '--case-id',
        action='append',
        default=[],
        help='Specific benchmark case ID to fetch (repeatable). Default: all known cases.',
    )
    parser.add_argument(
        '--output-root',
        default=get_default_output_root(repo_root),
        help='Directory where the staged case directories will be written.',
    )
    parser.add_argument(
        '--datasets',
        default=None,
        help="Path to the 'datasets' executable. Default: resolve from PATH.",
    )
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite an existing staged input.gbk file.',
    )
    args = parser.parse_args()

    case_ids = resolve_case_ids(args.case_id)
    datasets_executable = locate_datasets_executable(args.datasets)
    output_root = os.path.abspath(args.output_root)
    os.makedirs(output_root, exist_ok=True)

    for case_id in case_ids:
        spec = CASE_SPECS[case_id]
        print('Fetching %s (%s)' % (case_id, spec['assembly_accession']))
        destination_path = download_case(
            case_id=case_id,
            spec=spec,
            output_root=output_root,
            datasets_executable=datasets_executable,
            overwrite=args.overwrite,
        )
        print('  staged -> %s' % destination_path)

    return 0


if __name__ == '__main__':
    sys.exit(main())
