#!/usr/bin/env python

import argparse
import hashlib
import json
import os
import shutil
import sys
import zipfile

from check_template_genome_bank import (
    collect_bank_status,
    get_default_bank,
    get_default_input1_root,
    get_repo_root,
    load_catalog,
)


def get_default_source_manifest(input1_root):
    return os.path.join(input1_root, 'template_genome_sources.json')


def sha256sum(path, chunk_size=1024 * 1024):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        while True:
            chunk = handle.read(chunk_size)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def load_source_manifest(path):
    with open(path, 'r') as handle:
        payload = json.load(handle)
    return payload


def build_bundle_payload(catalog, source_manifest, input1_root, bank_root):
    rows, missing = collect_bank_status(catalog, input1_root, bank_root)
    if missing:
        manual_missing = [
            template_id
            for template_id in missing
            if source_manifest.get('templates', {}).get(template_id, {}).get('source_type') == 'manual_source'
        ]
        message = (
            'Cannot build a curated bundle because the local bank is incomplete. Missing templates: %s'
            % ', '.join(missing)
        )
        if manual_missing:
            message += (
                '. The current manual-source templates are: %s. Add those FASTA files to the local bank first.'
                % ', '.join(manual_missing)
            )
        raise RuntimeError(
            message
        )

    templates = {}
    checksums = []
    for row in rows:
        template_id = row['template_id']
        relative_path = os.path.basename(row['expected_path'])
        absolute_path = row['expected_path']
        checksum = sha256sum(absolute_path)
        templates[template_id] = {
            'organism': row['organism'],
            'bundle_relative_path': os.path.join('genomes', relative_path).replace('\\', '/'),
            'sha256': checksum,
        }
        if template_id in source_manifest.get('templates', {}):
            templates[template_id]['source'] = source_manifest['templates'][template_id]
        checksums.append(
            {
                'template_id': template_id,
                'relative_path': os.path.join('genomes', relative_path).replace('\\', '/'),
                'sha256': checksum,
            }
        )
    return templates, checksums


def write_checksums(path, checksums):
    with open(path, 'w', newline='') as handle:
        handle.write('template_id\trelative_path\tsha256\n')
        for row in sorted(checksums, key=lambda item: item['template_id']):
            handle.write('%s\t%s\t%s\n' % (row['template_id'], row['relative_path'], row['sha256']))


def add_tree_to_zip(archive, source_root):
    for root, _dirs, files in os.walk(source_root):
        for filename in sorted(files):
            absolute_path = os.path.join(root, filename)
            relative_path = os.path.relpath(absolute_path, source_root)
            archive.write(absolute_path, relative_path)


def main():
    repo_root = get_repo_root()
    input1_root = get_default_input1_root(repo_root)
    default_bank = get_default_bank(input1_root)
    default_manifest = get_default_source_manifest(input1_root)

    parser = argparse.ArgumentParser(
        description='Build a curated template genome bank bundle from a complete local genome bank.'
    )
    parser.add_argument(
        '--bank',
        default=default_bank,
        help='Directory containing a complete local template genome bank',
    )
    parser.add_argument(
        '--manifest',
        default=default_manifest,
        help='Template genome source manifest to embed in the bundle',
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Path to the output .zip bundle',
    )
    parser.add_argument(
        '--bundle-version',
        default='v1',
        help='Bundle version label recorded in bundle_manifest.json',
    )
    args = parser.parse_args()

    bank_root = os.path.abspath(args.bank)
    output_path = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    catalog = load_catalog(input1_root)
    source_manifest = load_source_manifest(os.path.abspath(args.manifest))
    templates, checksums = build_bundle_payload(catalog, source_manifest, input1_root, bank_root)

    staging_parent = os.path.dirname(output_path) or os.getcwd()
    bundle_stem = os.path.splitext(os.path.basename(output_path))[0]
    staging_root = os.path.join(staging_parent, '.%s_staging' % bundle_stem)
    genomes_root = os.path.join(staging_root, 'genomes')

    if os.path.isdir(staging_root):
        shutil.rmtree(staging_root)

    try:
        os.makedirs(genomes_root, exist_ok=True)

        for template_id in sorted(catalog):
            source_path = os.path.join(bank_root, '%s.fna' % template_id)
            if not os.path.isfile(source_path):
                raise RuntimeError('Expected genome file is missing from the local bank: %s' % source_path)
            destination_path = os.path.join(genomes_root, '%s.fna' % template_id)
            shutil.copyfile(source_path, destination_path)

        bundle_manifest = {
            'description': 'Curated template genome bank bundle for skani-first auto-template recommendation.',
            'bundle_version': args.bundle_version,
            'template_count': len(templates),
            'templates': templates,
        }

        with open(os.path.join(staging_root, 'bundle_manifest.json'), 'w') as handle:
            json.dump(bundle_manifest, handle, indent=2, sort_keys=True)

        write_checksums(os.path.join(staging_root, 'checksums.tsv'), checksums)

        with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            add_tree_to_zip(archive, staging_root)
    finally:
        if os.path.isdir(staging_root):
            shutil.rmtree(staging_root, ignore_errors=True)

    print('Bundle written to: %s' % output_path)
    print('Templates included: %d' % len(templates))
    return 0


if __name__ == '__main__':
    sys.exit(main())
