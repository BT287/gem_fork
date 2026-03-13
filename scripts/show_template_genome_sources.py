#!/usr/bin/env python

import argparse
import json
import os
import sys


def get_repo_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def get_default_manifest(repo_root):
    return os.path.join(repo_root, 'gmsm', 'io', 'data', 'input1', 'template_genome_sources.json')


def load_manifest(path):
    with open(path, 'r') as handle:
        return json.load(handle)


def print_table(templates):
    print('template_id\torganism\ttemplate_model\tsource_type\taccession\texpected_relative_path')
    for template_id in sorted(templates):
        entry = templates[template_id]
        print('%s\t%s\t%s\t%s\t%s\t%s' % (
            template_id,
            entry.get('organism', template_id),
            entry.get('template_model', ''),
            entry.get('source_type', ''),
            entry.get('accession', ''),
            entry.get('expected_relative_path', ''),
        ))


def print_details(template_id, entry):
    print('template_id: %s' % template_id)
    for key in (
        'organism',
        'template_model',
        'source_type',
        'accession',
        'expected_relative_path',
        'source_page',
        'download_url',
        'selection_note',
    ):
        print('%s: %s' % (key, entry.get(key)))


def main():
    repo_root = get_repo_root()
    parser = argparse.ArgumentParser(description='Show the curated source manifest for the skani template genome bank.')
    parser.add_argument('--manifest', default=get_default_manifest(repo_root), help='Path to the template genome source manifest')
    parser.add_argument('--template', default=None, help='Show details for a single template ID')
    args = parser.parse_args()

    manifest = load_manifest(os.path.abspath(args.manifest))
    templates = manifest.get('templates', {})

    if args.template:
        entry = templates.get(args.template)
        if entry is None:
            print('Unknown template ID: %s' % args.template, file=sys.stderr)
            return 1
        print_details(args.template, entry)
        return 0

    print_table(templates)
    return 0


if __name__ == '__main__':
    sys.exit(main())
