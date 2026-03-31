#!/usr/bin/env python

import argparse
import json
import os
import sys


def get_repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def get_default_input1_root(repo_root):
    return os.path.join(repo_root, 'gmsm', 'io', 'data', 'input1')


def get_default_bank(input1_root):
    return os.path.join(input1_root, 'genomes')


def load_catalog(input1_root):
    catalog_path = os.path.join(input1_root, 'template_catalog.json')
    with open(catalog_path, 'r') as handle:
        payload = json.load(handle)
    return payload.get('templates', {})


def resolve_expected_relative_path(template_id, metadata):
    configured = metadata.get('genome_fasta')
    if configured:
        return configured
    return os.path.join('genomes', '%s.fna' % template_id)


def resolve_expected_path(template_id, metadata, input1_root, bank_root):
    relative_path = resolve_expected_relative_path(template_id, metadata)
    if os.path.isabs(relative_path):
        return relative_path

    relative_path = os.path.normpath(relative_path)
    if relative_path.startswith('genomes' + os.sep) or relative_path == 'genomes':
        relative_path = os.path.relpath(relative_path, 'genomes')
    return os.path.abspath(os.path.join(bank_root, relative_path))


def collect_bank_status(catalog, input1_root, bank_root):
    rows = []
    missing = []
    for template_id in sorted(catalog):
        metadata = catalog[template_id]
        expected_path = resolve_expected_path(template_id, metadata, input1_root, bank_root)
        status = 'present' if os.path.isfile(expected_path) else 'missing'
        if status == 'missing':
            missing.append(template_id)
        rows.append(
            {
                'template_id': template_id,
                'organism': metadata.get('organism', template_id),
                'expected_path': expected_path,
                'status': status,
            }
        )
    return rows, missing


def print_status_table(rows):
    print('template_id\torganism\texpected_path\tstatus')
    for row in rows:
        print('%s\t%s\t%s\t%s' % (
            row['template_id'],
            row['organism'],
            row['expected_path'],
            row['status'],
        ))


def main():
    repo_root = get_repo_root()
    input1_root = get_default_input1_root(repo_root)
    default_bank = get_default_bank(input1_root)

    parser = argparse.ArgumentParser(description='Validate the local template genome bank for skani-based auto-template recommendation.')
    parser.add_argument('--bank', default=default_bank, help='Directory containing template genome FASTA files')
    parser.add_argument('--allow-missing', action='store_true', help='Exit successfully even when some templates are missing')
    args = parser.parse_args()

    catalog = load_catalog(input1_root)
    bank_root = os.path.abspath(args.bank)

    rows, missing = collect_bank_status(catalog, input1_root, bank_root)
    print_status_table(rows)

    if missing:
        print('\nMissing templates: %s' % ', '.join(missing), file=sys.stderr)
        if not args.allow_missing:
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
