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


def resolve_expected_path(template_id, metadata, input1_root, bank_root):
    configured = metadata.get('genome_fasta')
    if configured:
        if os.path.isabs(configured):
            return configured
        return os.path.abspath(os.path.join(input1_root, configured))
    return os.path.join(bank_root, '%s.fna' % template_id)


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

    print('template_id\torganism\texpected_path\tstatus')
    missing = []
    for template_id in sorted(catalog):
        metadata = catalog[template_id]
        expected_path = resolve_expected_path(template_id, metadata, input1_root, bank_root)
        status = 'present' if os.path.isfile(expected_path) else 'missing'
        if status == 'missing':
            missing.append(template_id)
        print('%s\t%s\t%s\t%s' % (
            template_id,
            metadata.get('organism', template_id),
            expected_path,
            status,
        ))

    if missing:
        print('\nMissing templates: %s' % ', '.join(missing), file=sys.stderr)
        if not args.allow_missing:
            return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
