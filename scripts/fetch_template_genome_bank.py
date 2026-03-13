#!/usr/bin/env python

import argparse
import http.client
import json
import os
import shutil
import sys
import tarfile
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile
from urllib.error import HTTPError, URLError

from check_template_genome_bank import (
    collect_bank_status,
    get_default_bank,
    get_default_input1_root,
    get_repo_root,
    load_catalog,
    print_status_table,
    resolve_expected_relative_path,
)


def is_url(value):
    parsed = urllib.parse.urlparse(value)
    return parsed.scheme in ('http', 'https')


def fetch_bundle(source, workdir, default_name='template_genome_bank.bundle'):
    if is_url(source):
        filename = os.path.basename(urllib.parse.urlparse(source).path) or default_name
        destination = os.path.join(workdir, filename)
        download_url(source, destination)
        return destination

    source = os.path.abspath(source)
    if not os.path.isfile(source):
        raise FileNotFoundError('Bundle not found: %s' % source)
    return source


def download_url(source, destination, max_attempts=4, chunk_size=1024 * 1024):
    last_error = None
    request = urllib.request.Request(source, headers={'User-Agent': 'gem_fork-template-bank/1.0'})

    for attempt in range(1, max_attempts + 1):
        try:
            with urllib.request.urlopen(request) as response, open(destination, 'wb') as handle:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    handle.write(chunk)
            return
        except (HTTPError, URLError, http.client.IncompleteRead, ConnectionError, TimeoutError, OSError) as exc:
            last_error = exc
            if os.path.exists(destination):
                os.remove(destination)
            if attempt == max_attempts:
                break
            time.sleep(min(5 * attempt, 20))

    raise RuntimeError('Failed to download %s after %d attempts: %s' % (source, max_attempts, last_error))


def extract_bundle(bundle_path, extract_dir):
    lower_name = bundle_path.lower()
    if zipfile.is_zipfile(bundle_path):
        with zipfile.ZipFile(bundle_path, 'r') as archive:
            archive.extractall(extract_dir)
        return

    if lower_name.endswith(('.tar.gz', '.tgz', '.tar', '.tar.bz2', '.tar.xz')):
        with tarfile.open(bundle_path, 'r:*') as archive:
            archive.extractall(extract_dir)
        return

    raise RuntimeError('Unsupported bundle format: %s' % bundle_path)


def find_candidate_file(extract_dir, relative_path):
    normalized_relative = os.path.normpath(relative_path)
    direct_candidate = os.path.join(extract_dir, normalized_relative)
    if os.path.isfile(direct_candidate):
        return direct_candidate

    basename = os.path.basename(normalized_relative)
    matches = []
    for root, _dirs, files in os.walk(extract_dir):
        for filename in files:
            if filename == basename:
                matches.append(os.path.join(root, filename))

    if len(matches) == 1:
        return matches[0]

    return None


def find_single_genome_fasta(extract_dir, accession=None):
    fasta_candidates = []
    for root, _dirs, files in os.walk(extract_dir):
        for filename in files:
            lower_name = filename.lower()
            if lower_name.endswith(('.fna', '.fa', '.fasta')):
                fasta_candidates.append(os.path.join(root, filename))

    if not fasta_candidates:
        return None

    if accession:
        accession_matches = [path for path in fasta_candidates if accession in os.path.basename(path)]
        if len(accession_matches) == 1:
            return accession_matches[0]

    genomic_matches = [path for path in fasta_candidates if os.path.basename(path).lower() == 'genomic.fna']
    if len(genomic_matches) == 1:
        return genomic_matches[0]

    if len(fasta_candidates) == 1:
        return fasta_candidates[0]

    return None


def normalize_relative_path(relative_path):
    normalized = os.path.normpath(relative_path)
    if normalized.startswith('genomes' + os.sep):
        normalized = os.path.relpath(normalized, 'genomes')
    return normalized


def install_bundle(bundle_path, dest_root, input1_root, force=False):
    catalog = load_catalog(input1_root)

    with tempfile.TemporaryDirectory(prefix='gmsm-template-bank-') as temp_dir:
        extract_dir = os.path.join(temp_dir, 'extract')
        os.makedirs(extract_dir, exist_ok=True)
        extract_bundle(bundle_path, extract_dir)

        os.makedirs(dest_root, exist_ok=True)

        for template_id in sorted(catalog):
            metadata = catalog[template_id]
            relative_path = resolve_expected_relative_path(template_id, metadata)
            if os.path.isabs(relative_path):
                raise RuntimeError('Absolute genome_fasta paths are not supported in bundle installation')

            normalized_relative = normalize_relative_path(relative_path)

            source_path = find_candidate_file(extract_dir, relative_path)
            if source_path is None and normalized_relative != relative_path:
                source_path = find_candidate_file(extract_dir, normalized_relative)
            if source_path is None:
                continue

            destination_path = os.path.join(dest_root, normalized_relative)
            copy_into_bank(source_path, destination_path, force=force)

    rows, missing = collect_bank_status(catalog, input1_root, dest_root)
    print_status_table(rows)
    if missing:
        raise RuntimeError('Installed bundle is incomplete; missing templates: %s' % ', '.join(missing))


def copy_into_bank(source_path, destination_path, force=False):
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    if os.path.exists(destination_path) and not force:
        raise RuntimeError(
            'Destination file already exists: %s (use --force to overwrite)' % destination_path
        )
    shutil.copyfile(source_path, destination_path)


def get_default_source_manifest(input1_root):
    return os.path.join(input1_root, 'template_genome_sources.json')


def load_source_manifest(path):
    with open(path, 'r') as handle:
        payload = json.load(handle)
    return payload.get('templates', {})


def select_template_entries(entries, requested_templates):
    if not requested_templates:
        return entries
    missing = [template_id for template_id in requested_templates if template_id not in entries]
    if missing:
        raise RuntimeError('Unknown template IDs: %s' % ', '.join(sorted(missing)))
    return {template_id: entries[template_id] for template_id in requested_templates}


def split_entries_by_downloadability(entries):
    direct = {}
    manual = {}
    for template_id, entry in entries.items():
        if entry.get('download_url'):
            direct[template_id] = entry
        else:
            manual[template_id] = entry
    return direct, manual


def print_manifest_plan(entries, direct_entries, manual_entries):
    print('template_id\tsource_type\taccession\tdownload_mode\texpected_relative_path')
    for template_id in sorted(entries):
        entry = entries[template_id]
        mode = 'direct' if template_id in direct_entries else 'manual'
        print('%s\t%s\t%s\t%s\t%s' % (
            template_id,
            entry.get('source_type'),
            entry.get('accession'),
            mode,
            entry.get('expected_relative_path'),
        ))


def install_from_manifest(entries, dest_root, input1_root, force=False):
    direct_entries, manual_entries = split_entries_by_downloadability(entries)
    os.makedirs(dest_root, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix='gmsm-template-manifest-') as temp_dir:
        for template_id in sorted(direct_entries):
            entry = direct_entries[template_id]
            print('Downloading template genome: %s (%s)' % (template_id, entry.get('accession')))
            bundle_path = fetch_bundle(
                entry['download_url'],
                temp_dir,
                default_name='%s_download.bundle' % template_id,
            )
            extract_dir = os.path.join(temp_dir, template_id)
            os.makedirs(extract_dir, exist_ok=True)
            extract_bundle(bundle_path, extract_dir)

            source_path = find_single_genome_fasta(extract_dir, accession=entry.get('accession'))
            if source_path is None:
                raise RuntimeError(
                    'Could not locate a unique genome FASTA inside the downloaded bundle for template %s' % template_id
                )

            relative_path = normalize_relative_path(entry['expected_relative_path'])
            destination_path = os.path.join(dest_root, relative_path)
            copy_into_bank(source_path, destination_path, force=force)

    catalog = load_catalog(input1_root)
    rows, missing = collect_bank_status(catalog, input1_root, dest_root)
    print_status_table(rows)

    unresolved_direct = [template_id for template_id in direct_entries if template_id in missing]
    if unresolved_direct:
        raise RuntimeError(
            'Direct-download installation is incomplete; missing direct templates: %s' % ', '.join(unresolved_direct)
        )

    if manual_entries:
        print(
            '\nManual-source templates still require a separate bundle or file copy: %s'
            % ', '.join(sorted(manual_entries)),
            file=sys.stderr,
        )


def main():
    repo_root = get_repo_root()
    input1_root = get_default_input1_root(repo_root)
    default_bank = get_default_bank(input1_root)
    default_manifest = get_default_source_manifest(input1_root)

    parser = argparse.ArgumentParser(
        description='Install a template genome bank bundle for skani-based auto-template recommendation.'
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        '--bundle',
        help='Path or URL to a zip/tar archive containing template genome FASTA files',
    )
    source_group.add_argument(
        '--from-manifest',
        action='store_true',
        help='Download all directly available template genomes from the curated source manifest',
    )
    parser.add_argument(
        '--manifest',
        default=default_manifest,
        help='Path to the template genome source manifest used with --from-manifest',
    )
    parser.add_argument(
        '--template',
        action='append',
        dest='templates',
        default=[],
        help='Template ID to install from the source manifest (repeatable)',
    )
    parser.add_argument(
        '--plan',
        action='store_true',
        help='Show the direct/manual installation plan without downloading anything',
    )
    parser.add_argument(
        '--dest',
        default=default_bank,
        help='Destination directory for the installed template genome bank',
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing destination files if present',
    )
    args = parser.parse_args()

    destination = os.path.abspath(args.dest)

    if args.bundle:
        if args.plan:
            print('Bundle installation plan')
            print('source: %s' % args.bundle)
            print('dest: %s' % destination)
            return 0
        with tempfile.TemporaryDirectory(prefix='gmsm-template-download-') as temp_dir:
            bundle_path = fetch_bundle(args.bundle, temp_dir)
            install_bundle(bundle_path, destination, input1_root, force=args.force)
        print('\nTemplate genome bank installed in: %s' % destination)
        return 0

    entries = load_source_manifest(os.path.abspath(args.manifest))
    entries = select_template_entries(entries, args.templates)
    direct_entries, manual_entries = split_entries_by_downloadability(entries)

    if args.plan:
        print_manifest_plan(entries, direct_entries, manual_entries)
        return 0

    install_from_manifest(entries, destination, input1_root, force=args.force)
    print('\nTemplate genome bank installed in: %s' % destination)
    return 0


if __name__ == '__main__':
    sys.exit(main())
