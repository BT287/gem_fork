import json
from os.path import isfile, join

import pytest

from gmsm import template_recommendation


class TestTemplateRecommendation:

    def test_discover_template_catalog_includes_known_templates(self):
        catalog = template_recommendation.discover_template_catalog()
        template_ids = {entry['template_id'] for entry in catalog}

        assert 'sco' in template_ids
        assert 'mtu' in template_ids

    def test_resolve_template_backend_falls_back_to_diamond_without_skani_assets(self, options, monkeypatch):
        options.template_backend = 'auto'
        options.input = 'input.gbk'

        monkeypatch.setattr(
            template_recommendation.utils,
            'locate_executable',
            lambda name: None if name == 'skani' else 'diamond',
        )

        backend = template_recommendation.resolve_template_backend(
            'genbank',
            options,
            [
                {
                    'template_id': 'sco',
                    'proteome_fasta': 'sco.fa',
                    'genome_fasta': None,
                }
            ],
        )

        assert backend == 'diamond'

    def test_resolve_template_backend_requires_genome_bank_for_skani(self, options, monkeypatch):
        options.template_backend = 'skani'
        options.input = 'input.gbk'

        monkeypatch.setattr(
            template_recommendation.utils,
            'locate_executable',
            lambda name: 'skani' if name == 'skani' else None,
        )

        with pytest.raises(RuntimeError):
            template_recommendation.resolve_template_backend(
                'genbank',
                options,
                [{'template_id': 'sco', 'proteome_fasta': 'sco.fa', 'genome_fasta': None}],
            )

    def test_recommend_template_updates_namespace_and_writes_outputs(self, options, tmp_test_dir, monkeypatch):
        options.outputfolder = tmp_test_dir
        options.outputfolder0 = join(tmp_test_dir, '0_template_recommendation')
        options.outputfolder6 = join(tmp_test_dir, 'tmp_data_files')
        options.auto_template = True
        options.template_backend = 'auto'
        options.template_topk = 2
        options.orgName = 'sco'
        options.input = 'input.gbk'

        catalog = [
            {
                'template_id': 'mtu',
                'proteome_fasta': 'mtu.fa',
                'genome_fasta': None,
                'organism': 'Mycobacterium tuberculosis H37Rv',
                'model': 'iNJ661',
            },
            {
                'template_id': 'sco',
                'proteome_fasta': 'sco.fa',
                'genome_fasta': None,
                'organism': 'Streptomyces coelicolor A3(2)',
                'model': 'iKS1317',
            },
        ]

        monkeypatch.setattr(
            template_recommendation,
            'discover_template_catalog',
            lambda input1_root=None: catalog,
        )
        monkeypatch.setattr(
            template_recommendation,
            'resolve_template_backend',
            lambda filetype, run_ns, entries: 'diamond',
        )
        monkeypatch.setattr(
            template_recommendation,
            'score_templates_with_diamond',
            lambda run_ns, io_ns, entries: [
                {
                    'template_id': 'mtu',
                    'organism': 'Mycobacterium tuberculosis H37Rv',
                    'model': 'iNJ661',
                    'backend': 'diamond',
                    'score': 0.92,
                    'primary_metric': 0.90,
                    'secondary_metric': 88.0,
                    'ani': None,
                    'aligned_fraction': None,
                    'aligned_fraction_ref': None,
                    'aligned_fraction_query': None,
                    'matched_queries': 90,
                    'total_queries': 100,
                    'hit_coverage': 0.90,
                    'mean_identity': 88.0,
                    'mean_bitscore': 240.0,
                },
                {
                    'template_id': 'sco',
                    'organism': 'Streptomyces coelicolor A3(2)',
                    'model': 'iKS1317',
                    'backend': 'diamond',
                    'score': 0.80,
                    'primary_metric': 0.78,
                    'secondary_metric': 84.0,
                    'ani': None,
                    'aligned_fraction': None,
                    'aligned_fraction_ref': None,
                    'aligned_fraction_query': None,
                    'matched_queries': 78,
                    'total_queries': 100,
                    'hit_coverage': 0.78,
                    'mean_identity': 84.0,
                    'mean_bitscore': 210.0,
                },
            ],
        )

        result = template_recommendation.recommend_template('genbank', options, options)

        assert options.orgName == 'mtu'
        assert options.template_selection_mode == 'auto'
        assert options.template_selection_backend == 'diamond'
        assert result['recommended_template'] == 'mtu'
        assert isfile(join(options.outputfolder0, 'template_candidates.tsv'))
        assert isfile(join(options.outputfolder0, 'template_recommendation.json'))

        with open(join(options.outputfolder0, 'template_recommendation.json')) as handle:
            saved = json.load(handle)

        assert saved['recommended_template'] == 'mtu'
        assert saved['candidates'][0]['template_id'] == 'mtu'
