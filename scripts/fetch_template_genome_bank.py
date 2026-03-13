#!/usr/bin/env python

import argparse
import os
import shutil
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request
import zipfile

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


def fetch_bundle(source, workdir):
    if is_url(source):
        filename = os.path.basename(urllib.parse.urlparse(source).path) or 'template_genome_bank.bundle'
        destination = os.path.join(workdir, filename)
        urllib.request.urlretrieve(source, destination)
        return destination

    source = os.path.abspath(source)
    if not os.path.isfile(source):
        raise FileNotFoundError('Bundle not found: %s' % source)
    return source


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

            normalized_relative = os.path.normpath(relative_path)
            if normalized_relative.startswith('genomes' + os.sep):
                normalized_relative = os.path.relpath(normalized_relative, 'genomes')

            source_path = find_candidate_file(extract_dir, relative_path)
            if source_path is None and normalized_relative != relative_path:
                source_path = find_candidate_file(extract_dir, normalized_relative)
            if source_path is None:
                continue

            destination_path = os.path.join(dest_root, normalized_relative)
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)

            if os.path.exists(destination_path) and not force:
                raise RuntimeError(
                    'Destination file already exists: %s (use --force to overwrite)' % destination_path
                )
            shutil.copyfile(source_path, destination_path)

    rows, missing = collect_bank_status(catalog, input1_root, dest_root)
    print_status_table(rows)
    if missing:
        raise RuntimeError('Installed bundle is incomplete; missing templates: %s' % ', '.join(missing))


def main():
    repo_root = get_repo_root()
    input1_root = get_default_input1_root(repo_root)
    default_bank = get_default_bank(input1_root)

    parser = argparse.ArgumentParser(
        description='Install a template genome bank bundle for skani-based auto-template recommendation.'
    )
    parser.add_argument(
        '--bundle',
        required=True,
        help='Path or URL to a zip/tar archive containing template genome FASTA files',
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

    with tempfile.TemporaryDirectory(prefix='gmsm-template-download-') as temp_dir:
        bundle_path = fetch_bundle(args.bundle, temp_dir)
        install_bundle(bundle_path, destination, input1_root, force=args.force)

    print('\nTemplate genome bank installed in: %s' % destination)
    return 0


if __name__ == '__main__':
    sys.exit(main())
