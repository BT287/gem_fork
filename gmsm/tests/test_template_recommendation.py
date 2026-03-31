import csv
import json
from os.path import isfile, join

import pytest

from gmsm import template_recommendation


class TestTemplateRecommendation:

    def test_template_score_config_uses_defaults_when_namespace_is_missing_fields(self, options):
        score_config = template_recommendation.TemplateScoreConfig.from_namespace(options)

        assert score_config.ani_weight == 0.7
        assert score_config.af_weight == 0.3
        assert score_config.coarse_weight == 0.6
        assert score_config.rerank_weight == 0.4

    def test_template_score_helpers_use_custom_weights(self):
        score_config = template_recommendation.TemplateScoreConfig(
            ani_weight=0.2,
            af_weight=0.8,
            diamond_hit_weight=0.1,
            diamond_identity_weight=0.9,
            bbh_template_cov_weight=0.25,
            bbh_target_cov_weight=0.75,
            coarse_weight=0.3,
            rerank_weight=0.7,
        )

        assert template_recommendation.compute_skani_coarse_score(95.0, 0.25, score_config) == 0.4
        assert template_recommendation.compute_diamond_coarse_score(0.8, 50.0, score_config) == 0.53
        assert template_recommendation.compute_bbh_rerank_score(0.9, 0.5, score_config) == 0.6
        assert template_recommendation.combine_template_scores(0.4, 0.6, score_config) == 0.54

    def test_discover_template_catalog_includes_known_templates(self):
        catalog = template_recommendation.discover_template_catalog()
        template_ids = {entry['template_id'] for entry in catalog}

        assert 'sco' in template_ids
        assert 'mtu' in template_ids

    def test_discover_template_catalog_reads_template_genome_bank(self, tmp_path):
        input1_root = tmp_path / 'input1'
        template_dir = input1_root / 'sco'
        genome_bank = input1_root / 'genomes'
        template_dir.mkdir(parents=True)
        genome_bank.mkdir(parents=True)
        (template_dir / 'tempModel_locusTag_aaSeq.fa').write_text('>gene1\nMPEPTIDE\n')
        (genome_bank / 'sco.fna').write_text('>chr1\nATGC\n')
        (input1_root / 'template_catalog.json').write_text(
            json.dumps(
                {
                    'templates': {
                        'sco': {
                            'organism': 'Streptomyces coelicolor A3(2)',
                            'model': 'iKS1317',
                            'genome_fasta': 'genomes/sco.fna',
                        }
                    }
                }
            )
        )

        catalog = template_recommendation.discover_template_catalog(str(input1_root))

        assert len(catalog) == 1
        assert catalog[0]['template_id'] == 'sco'
        assert catalog[0]['genome_fasta'] == str(genome_bank / 'sco.fna')

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

    def test_resolve_template_backend_prefers_skani_when_assets_exist(self, options, monkeypatch):
        options.template_backend = 'auto'
        options.input = 'input.gbk'

        monkeypatch.setattr(
            template_recommendation.utils,
            'locate_executable',
            lambda name: 'skani' if name == 'skani' else None,
        )

        backend = template_recommendation.resolve_template_backend(
            'genbank',
            options,
            [
                {
                    'template_id': 'sco',
                    'proteome_fasta': 'sco.fa',
                    'genome_fasta': 'sco.fna',
                }
            ],
        )

        assert backend == 'skani'

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
        options.outputfolder5 = join(tmp_test_dir, 'tmp_data_files')
        options.auto_template = True
        options.template_backend = 'auto'
        options.template_topk = 2
        options.template_genome_bank = False
        options.template_rerank_topn = 3
        options.template_ani_weight = 0.55
        options.template_af_weight = 0.45
        options.template_diamond_hit_weight = 0.9
        options.template_diamond_identity_weight = 0.1
        options.template_bbh_template_weight = 0.65
        options.template_bbh_target_weight = 0.35
        options.template_coarse_weight = 0.2
        options.template_rerank_weight = 0.8
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
            lambda input1_root=None, run_ns=None: catalog,
        )
        monkeypatch.setattr(
            template_recommendation,
            'resolve_template_backend',
            lambda filetype, run_ns, entries: 'diamond',
        )
        monkeypatch.setattr(
            template_recommendation,
            'score_templates_with_diamond',
            lambda run_ns, io_ns, entries, score_config=None: [
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
        monkeypatch.setattr(
            template_recommendation,
            'rerank_templates_with_bbh',
            lambda run_ns, io_ns, candidates, catalog, score_config=None: candidates,
        )

        result = template_recommendation.recommend_template('genbank', options, options)

        assert options.orgName == 'mtu'
        assert options.template_selection_mode == 'auto'
        assert options.template_selection_backend == 'diamond'
        assert result['recommended_template'] == 'mtu'
        assert result['selection_strategy'] == 'coarse_only'
        assert isfile(join(options.outputfolder0, 'template_candidates.tsv'))
        assert isfile(join(options.outputfolder0, 'template_recommendation.json'))

        with open(join(options.outputfolder0, 'template_recommendation.json')) as handle:
            saved = json.load(handle)

        assert saved['recommended_template'] == 'mtu'
        assert saved['score_config']['ani_weight'] == 0.55
        assert saved['score_config']['coarse_weight'] == 0.2
        assert saved['candidates'][0]['template_id'] == 'mtu'

        with open(join(options.outputfolder0, 'template_candidates.tsv'), newline='') as handle:
            reader = csv.DictReader(handle, delimiter='\t')
            rows = list(reader)

        assert reader.fieldnames is not None
        assert 'primary_metric' in reader.fieldnames
        assert 'secondary_metric' in reader.fieldnames
        assert 'coarse_score' in reader.fieldnames
        assert 'selection_stage' in reader.fieldnames
        assert rows[0]['template_id'] == 'mtu'

    def test_rerank_templates_with_bbh_updates_top_candidates(self, options, monkeypatch):
        options.template_rerank_topn = 1
        options.targetGenome_locusTag_aaSeq_dict = {'gene1': 'MPEPTIDE', 'gene2': 'MPEPTIDE'}
        options.outputfolder5 = 'tmp'

        candidates = [
            {
                'template_id': 'sco',
                'organism': 'Streptomyces coelicolor A3(2)',
                'model': 'iKS1317',
                'backend': 'diamond',
                'coarse_backend': 'diamond',
                'score': 0.80,
                'coarse_score': 0.80,
                'primary_metric': 0.80,
                'secondary_metric': 85.0,
                'coarse_primary_metric': 0.80,
                'coarse_secondary_metric': 85.0,
                'ani': None,
                'aligned_fraction': None,
                'aligned_fraction_ref': None,
                'aligned_fraction_query': None,
                'matched_queries': 8,
                'total_queries': 10,
                'hit_coverage': 0.8,
                'mean_identity': 85.0,
                'mean_bitscore': 200.0,
                'rerank_score': None,
                'rerank_applied': False,
                'coarse_rank': None,
                'bbh_pairs': None,
                'bbh_target_hits': None,
                'bbh_template_gene_count': None,
                'bbh_target_coverage': None,
                'bbh_template_coverage': None,
                'selection_stage': 'coarse',
            },
            {
                'template_id': 'mtu',
                'organism': 'Mycobacterium tuberculosis H37Rv',
                'model': 'iNJ661',
                'backend': 'diamond',
                'coarse_backend': 'diamond',
                'score': 0.70,
                'coarse_score': 0.70,
                'primary_metric': 0.70,
                'secondary_metric': 82.0,
                'coarse_primary_metric': 0.70,
                'coarse_secondary_metric': 82.0,
                'ani': None,
                'aligned_fraction': None,
                'aligned_fraction_ref': None,
                'aligned_fraction_query': None,
                'matched_queries': 7,
                'total_queries': 10,
                'hit_coverage': 0.7,
                'mean_identity': 82.0,
                'mean_bitscore': 180.0,
                'rerank_score': None,
                'rerank_applied': False,
                'coarse_rank': None,
                'bbh_pairs': None,
                'bbh_target_hits': None,
                'bbh_template_gene_count': None,
                'bbh_target_coverage': None,
                'bbh_template_coverage': None,
                'selection_stage': 'coarse',
            },
        ]
        catalog = [
            {'template_id': 'sco', 'proteome_fasta': 'sco.fa'},
            {'template_id': 'mtu', 'proteome_fasta': 'mtu.fa'},
        ]

        monkeypatch.setattr(
            template_recommendation,
            'prepare_target_proteome_fasta',
            lambda io_ns, output_dir: 'target.faa',
        )
        monkeypatch.setattr(
            template_recommendation,
            'ensure_tmp_template_dir',
            lambda io_ns: 'tmp',
        )
        monkeypatch.setattr(
            template_recommendation,
            'compute_bbh_rerank_metrics',
            lambda io_ns, target_fasta, template_entry, score_config=None: {
                'bbh_pairs': 9 if template_entry['template_id'] == 'sco' else 5,
                'bbh_target_hits': 8 if template_entry['template_id'] == 'sco' else 4,
                'bbh_template_gene_count': 10,
                'bbh_template_coverage': 0.9 if template_entry['template_id'] == 'sco' else 0.5,
                'bbh_target_coverage': 0.8 if template_entry['template_id'] == 'sco' else 0.4,
                'rerank_score': 0.87 if template_entry['template_id'] == 'sco' else 0.47,
            },
        )

        reranked = template_recommendation.rerank_templates_with_bbh(options, options, candidates, catalog)

        assert reranked[0]['template_id'] == 'sco'
        assert reranked[0]['rerank_applied'] is True
        assert reranked[0]['bbh_template_coverage'] == 0.9
        assert reranked[0]['score'] > reranked[1]['score']
        assert reranked[1]['rerank_applied'] is False

    def test_rerank_templates_with_bbh_uses_custom_final_weights(self, options, monkeypatch):
        options.template_rerank_topn = 1
        options.template_coarse_weight = 0.2
        options.template_rerank_weight = 0.8
        options.targetGenome_locusTag_aaSeq_dict = {'gene1': 'MPEPTIDE', 'gene2': 'MPEPTIDE'}
        options.outputfolder5 = 'tmp'

        candidates = [
            {
                'template_id': 'sco',
                'organism': 'Streptomyces coelicolor A3(2)',
                'model': 'iKS1317',
                'backend': 'diamond',
                'coarse_backend': 'diamond',
                'score': 0.80,
                'coarse_score': 0.80,
                'primary_metric': 0.80,
                'secondary_metric': 85.0,
                'coarse_primary_metric': 0.80,
                'coarse_secondary_metric': 85.0,
                'ani': None,
                'aligned_fraction': None,
                'aligned_fraction_ref': None,
                'aligned_fraction_query': None,
                'matched_queries': 8,
                'total_queries': 10,
                'hit_coverage': 0.8,
                'mean_identity': 85.0,
                'mean_bitscore': 200.0,
                'rerank_score': None,
                'rerank_applied': False,
                'coarse_rank': None,
                'bbh_pairs': None,
                'bbh_target_hits': None,
                'bbh_template_gene_count': None,
                'bbh_target_coverage': None,
                'bbh_template_coverage': None,
                'selection_stage': 'coarse',
            }
        ]
        catalog = [{'template_id': 'sco', 'proteome_fasta': 'sco.fa'}]

        monkeypatch.setattr(
            template_recommendation,
            'prepare_target_proteome_fasta',
            lambda io_ns, output_dir: 'target.faa',
        )
        monkeypatch.setattr(
            template_recommendation,
            'ensure_tmp_template_dir',
            lambda io_ns: 'tmp',
        )
        monkeypatch.setattr(
            template_recommendation,
            'compute_bbh_rerank_metrics',
            lambda io_ns, target_fasta, template_entry, score_config=None: {
                'bbh_pairs': 9,
                'bbh_target_hits': 8,
                'bbh_template_gene_count': 10,
                'bbh_template_coverage': 0.9,
                'bbh_target_coverage': 0.8,
                'rerank_score': 0.87,
            },
        )

        reranked = template_recommendation.rerank_templates_with_bbh(options, options, candidates, catalog)

        assert reranked[0]['score'] == 0.856
        assert reranked[0]['rerank_score'] == 0.87

    def test_recommendation_confidence_does_not_depend_on_topk(self):
        candidates = [
            {'template_id': 'sco', 'score': 0.61},
            {'template_id': 'mtu', 'score': 0.60},
        ]

        confidence = template_recommendation.classify_recommendation_confidence(candidates)

        assert confidence == 'low'
