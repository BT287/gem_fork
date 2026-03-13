import csv
import json
import logging
import os
import shutil
from types import SimpleNamespace
from statistics import mean

from Bio import SeqIO

from gmsm import utils
from gmsm.homology.blastp_utils import getBBH, makeBestHits_dict


_TEMPLATE_METADATA = {
    'bsu': {'organism': 'Bacillus subtilis subsp. subtilis str. 168', 'model': 'iYO844'},
    'clj': {'organism': 'Clostridium ljungdahlii DSM 13528', 'model': 'iHN637'},
    'cre': {'organism': 'Chlamydomonas reinhardtii', 'model': 'iCre1355'},
    'eco': {'organism': 'Escherichia coli str. K-12 substr. MG1655', 'model': 'iML1515'},
    'hpy': {'organism': 'Helicobacter pylori 26695', 'model': 'iIT341'},
    'mtu': {'organism': 'Mycobacterium tuberculosis H37Rv', 'model': 'iNJ661'},
    'nsal': {'organism': 'Nannochloropsis salina', 'model': 'iNS934'},
    'ppu': {'organism': 'Pseudomonas putida KT2440', 'model': 'iJN746'},
    'sce': {'organism': 'Saccharomyces cerevisiae S288C', 'model': 'iMM904'},
    'sco': {'organism': 'Streptomyces coelicolor A3(2)', 'model': 'iKS1317'},
}

_NUCLEOTIDE_CHARS = set("ACGTUNWSMKRYBDHV-")


def recommend_template(filetype, run_ns, io_ns):
    catalog = discover_template_catalog(run_ns=run_ns)
    if not catalog:
        raise RuntimeError("No template catalog entries were discovered under gmsm/io/data/input1")

    backend = resolve_template_backend(filetype, run_ns, catalog)
    logging.info("Running automatic template recommendation via '%s'", backend)

    if backend == 'skani':
        candidates = score_templates_with_skani(filetype, run_ns, io_ns, catalog)
    elif backend == 'diamond':
        candidates = score_templates_with_diamond(run_ns, io_ns, catalog)
    else:
        raise RuntimeError("Unsupported template recommendation backend: %s" % backend)

    if not candidates:
        raise RuntimeError("Automatic template recommendation did not produce any candidates")

    candidates = rerank_templates_with_bbh(run_ns, io_ns, candidates, catalog)
    sorted_candidates = sorted(
        candidates,
        key=lambda item: (
            -float(item.get('score', 0.0)),
            -float(item.get('primary_metric', 0.0)),
            -float(item.get('secondary_metric', 0.0)),
            item['template_id'],
        ),
    )

    topk = max(1, int(getattr(run_ns, 'template_topk', 3)))
    selected_candidates = sorted_candidates[:topk]
    selected_template = selected_candidates[0]['template_id']
    confidence = classify_recommendation_confidence(sorted_candidates)
    rerank_applied = any(candidate.get('rerank_applied') for candidate in sorted_candidates)

    result = {
        'selection_mode': 'auto',
        'backend': backend,
        'selection_strategy': 'coarse_plus_bbh' if rerank_applied else 'coarse_only',
        'rerank_topn': int(getattr(run_ns, 'template_rerank_topn', 3)),
        'recommended_template': selected_template,
        'previous_template': getattr(run_ns, 'orgName', None),
        'confidence': confidence,
        'candidates': selected_candidates,
    }

    run_ns.orgName = selected_template
    run_ns.template_selection_mode = 'auto'
    run_ns.template_selection_backend = backend
    run_ns.template_selection_confidence = confidence
    run_ns.template_selection_strategy = result['selection_strategy']
    run_ns.template_selection_topk = topk
    run_ns.template_selection_result = result

    write_template_recommendation_outputs(io_ns.outputfolder0, result)
    logging.info(
        "Selected template '%s' via '%s' backend (confidence: %s)",
        selected_template,
        backend,
        confidence,
    )
    return result


def discover_template_catalog(input1_root=None, run_ns=None):
    if input1_root is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        input1_root = os.path.join(repo_root, 'gmsm', 'io', 'data', 'input1')
    genome_bank_root = resolve_template_genome_bank(input1_root, run_ns)
    catalog_metadata = load_template_catalog_metadata(input1_root)

    catalog = []
    if not os.path.isdir(input1_root):
        return catalog

    for template_id in sorted(os.listdir(input1_root)):
        template_dir = os.path.join(input1_root, template_id)
        if not os.path.isdir(template_dir):
            continue

        proteome_fasta = os.path.join(template_dir, 'tempModel_locusTag_aaSeq.fa')
        if not os.path.isfile(proteome_fasta):
            continue

        metadata = dict(_TEMPLATE_METADATA.get(template_id, {}))
        metadata.update(catalog_metadata.get(template_id, {}))
        genome_fasta = resolve_template_genome_path(template_dir, metadata, input1_root, genome_bank_root)
        catalog.append(
            {
                'template_id': template_id,
                'template_dir': template_dir,
                'proteome_fasta': proteome_fasta,
                'genome_fasta': genome_fasta,
                'genome_bank_root': genome_bank_root,
                'organism': metadata.get('organism', template_id),
                'model': metadata.get('model', template_id),
            }
        )

    return catalog


def resolve_template_backend(filetype, run_ns, catalog):
    backend = getattr(run_ns, 'template_backend', 'auto')
    if backend == 'diamond':
        return backend

    if backend == 'skani':
        if not skani_backend_ready(filetype, run_ns, catalog):
            raise RuntimeError(
                "Template backend 'skani' requires a skani executable and template genome FASTA files"
            )
        return backend

    if skani_backend_ready(filetype, run_ns, catalog):
        return 'skani'

    log_skani_fallback_reason(filetype, run_ns, catalog)
    return 'diamond'


def skani_backend_ready(filetype, run_ns, catalog):
    if utils.locate_executable('skani') is None:
        return False

    if not any(entry.get('genome_fasta') for entry in catalog):
        return False

    return target_input_supports_skani(filetype, run_ns)


def log_skani_fallback_reason(filetype, run_ns, catalog):
    if utils.locate_executable('skani') is None:
        logging.info("Automatic template recommendation is falling back to DIAMOND because 'skani' was not found")
        return

    if not any(entry.get('genome_fasta') for entry in catalog):
        genome_bank = resolve_template_genome_bank(run_ns=run_ns)
        logging.info(
            "Automatic template recommendation is falling back to DIAMOND because no template genome FASTA files were found"
        )
        logging.info(
            "Install template genomes under '%s' or pass '--template-genome-bank <path>' to enable skani-first ranking",
            genome_bank,
        )
        return

    if not target_input_supports_skani(filetype, run_ns):
        logging.info(
            "Automatic template recommendation is falling back to DIAMOND because skani requires GenBank input or nucleotide FASTA input"
        )


def resolve_template_genome_bank(input1_root=None, run_ns=None):
    requested = getattr(run_ns, 'template_genome_bank', None) or os.environ.get('GMSM_TEMPLATE_GENOME_BANK')
    if input1_root is None:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        input1_root = os.path.join(repo_root, 'gmsm', 'io', 'data', 'input1')

    if requested:
        return os.path.abspath(requested)

    return os.path.join(input1_root, 'genomes')


def load_template_catalog_metadata(input1_root):
    metadata_path = os.path.join(input1_root, 'template_catalog.json')
    if not os.path.isfile(metadata_path):
        return {}

    with open(metadata_path, 'r') as handle:
        payload = json.load(handle)
    return payload.get('templates', {})


def resolve_template_genome_path(template_dir, metadata, input1_root, genome_bank_root):
    configured = metadata.get('genome_fasta')
    if configured:
        configured_candidates = []
        if os.path.isabs(configured):
            configured_candidates.append(configured)
        else:
            configured_candidates.extend(
                [
                    os.path.join(input1_root, configured),
                    os.path.join(genome_bank_root, configured),
                    os.path.join(template_dir, configured),
                ]
            )
        for candidate_path in configured_candidates:
            if os.path.isfile(candidate_path):
                return candidate_path

    for candidate_name in (
        'template_genome.fna',
        'template_genome.fa',
        'template_genome.fasta',
        'genome.fna',
        'genome.fa',
        'genome.fasta',
    ):
        candidate_path = os.path.join(template_dir, candidate_name)
        if os.path.isfile(candidate_path):
            return candidate_path

    for candidate_name in (
        '%s.fna' % os.path.basename(template_dir),
        '%s.fa' % os.path.basename(template_dir),
        '%s.fasta' % os.path.basename(template_dir),
    ):
        candidate_path = os.path.join(genome_bank_root, candidate_name)
        if os.path.isfile(candidate_path):
            return candidate_path

    return None


def target_input_supports_skani(filetype, run_ns):
    if filetype == 'genbank':
        return True
    if filetype != 'fasta':
        return False
    return is_probably_nucleotide_fasta(run_ns.input)


def is_probably_nucleotide_fasta(path, max_records=20):
    examined = 0
    for record in SeqIO.parse(path, 'fasta'):
        seq = str(record.seq).upper()
        if not seq:
            continue
        examined += 1
        residue_set = {char for char in seq if char.isalpha() or char == '-'}
        if residue_set and not residue_set.issubset(_NUCLEOTIDE_CHARS):
            return False
        if examined >= max_records:
            break
    return examined > 0


def prepare_target_proteome_fasta(io_ns, output_dir):
    target_fasta = os.path.join(output_dir, 'target_proteome_for_template_recommendation.faa')
    with open(target_fasta, 'w') as handle:
        for locus_tag, aa_seq in sorted(io_ns.targetGenome_locusTag_aaSeq_dict.items()):
            handle.write('>%s\n%s\n' % (locus_tag, aa_seq))
    return target_fasta


def prepare_target_genome_fasta(filetype, run_ns, output_dir):
    target_fasta = os.path.join(output_dir, 'target_genome_for_template_recommendation.fna')

    if filetype == 'genbank':
        records = list(SeqIO.parse(run_ns.input, 'genbank'))
        with open(target_fasta, 'w') as handle:
            SeqIO.write(records, handle, 'fasta')
        return target_fasta

    if filetype == 'fasta' and is_probably_nucleotide_fasta(run_ns.input):
        shutil.copyfile(run_ns.input, target_fasta)
        return target_fasta

    raise RuntimeError(
        "skani-based template recommendation requires GenBank input or a nucleotide FASTA input"
    )


def score_templates_with_skani(filetype, run_ns, io_ns, catalog):
    skani = utils.locate_executable('skani')
    if skani is None:
        raise RuntimeError("skani executable not found")

    tmp_dir = ensure_tmp_template_dir(io_ns)
    query_fasta = prepare_target_genome_fasta(filetype, run_ns, tmp_dir)

    references = [entry for entry in catalog if entry.get('genome_fasta')]
    output_path = os.path.join(tmp_dir, 'skani_template_candidates.tsv')
    command = [skani, 'dist', '-q', query_fasta, '-o', output_path]
    for entry in references:
        command.extend(['-r', entry['genome_fasta']])

    run_command(command, "skani template recommendation failed")

    parsed_rows = parse_skani_output(output_path)
    rows_by_template = {}
    for row in parsed_rows:
        template_id = infer_template_id_from_path(row.get('Ref_file'), catalog)
        if template_id is None:
            continue
        ani = safe_float(row.get('ANI'))
        af_ref = safe_float(row.get('Align_fraction_ref'))
        af_query = safe_float(row.get('Align_fraction_query'))
        af_mean = mean([value for value in (af_ref, af_query) if value is not None]) if any(
            value is not None for value in (af_ref, af_query)
        ) else 0.0
        score = round((0.7 * normalize_ani(ani)) + (0.3 * af_mean), 6)
        rows_by_template[template_id] = {
            'template_id': template_id,
            'organism': get_template_metadata(template_id, catalog).get('organism', template_id),
            'model': get_template_metadata(template_id, catalog).get('model', template_id),
            'backend': 'skani',
            'coarse_backend': 'skani',
            'score': score,
            'coarse_score': score,
            'primary_metric': ani or 0.0,
            'secondary_metric': af_mean or 0.0,
            'coarse_primary_metric': ani or 0.0,
            'coarse_secondary_metric': af_mean or 0.0,
            'ani': ani,
            'aligned_fraction': af_mean,
            'aligned_fraction_ref': af_ref,
            'aligned_fraction_query': af_query,
            'matched_queries': None,
            'total_queries': None,
            'hit_coverage': None,
            'mean_identity': None,
            'mean_bitscore': None,
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

    candidates = []
    for entry in catalog:
        candidate = rows_by_template.get(
            entry['template_id'],
            {
                'template_id': entry['template_id'],
                'organism': entry['organism'],
                'model': entry['model'],
                'backend': 'skani',
                'score': 0.0,
                'coarse_backend': 'skani',
                'coarse_score': 0.0,
                'primary_metric': 0.0,
                'secondary_metric': 0.0,
                'coarse_primary_metric': 0.0,
                'coarse_secondary_metric': 0.0,
                'ani': None,
                'aligned_fraction': 0.0,
                'aligned_fraction_ref': None,
                'aligned_fraction_query': None,
                'matched_queries': None,
                'total_queries': None,
                'hit_coverage': None,
                'mean_identity': None,
                'mean_bitscore': None,
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
        )
        candidates.append(candidate)
    return candidates


def score_templates_with_diamond(run_ns, io_ns, catalog):
    diamond = utils.locate_executable('diamond')
    if diamond is None:
        raise RuntimeError("diamond executable not found")

    tmp_dir = ensure_tmp_template_dir(io_ns)
    target_fasta = prepare_target_proteome_fasta(io_ns, tmp_dir)
    total_queries = max(1, len(io_ns.targetGenome_locusTag_aaSeq_dict))
    candidates = []

    for entry in catalog:
        db_prefix = os.path.join(tmp_dir, '%s_db' % entry['template_id'])
        blast_output = os.path.join(tmp_dir, '%s_hits.tsv' % entry['template_id'])

        run_command(
            [diamond, 'makedb', '--in', entry['proteome_fasta'], '-d', db_prefix],
            "DIAMOND database creation failed for template '%s'" % entry['template_id'],
        )
        run_command(
            [
                diamond,
                'blastp',
                '-d',
                db_prefix,
                '-q',
                target_fasta,
                '-o',
                blast_output,
                '--evalue',
                '1e-20',
                '--id',
                '30',
                '--max-target-seqs',
                '1',
                '--outfmt',
                '6',
                'qseqid',
                'bitscore',
                'pident',
            ],
            "DIAMOND template scoring failed for template '%s'" % entry['template_id'],
        )

        matched_queries, mean_bitscore, mean_identity = parse_diamond_template_hits(blast_output)
        hit_coverage = matched_queries / float(total_queries)
        score = round((0.85 * hit_coverage) + (0.15 * ((mean_identity or 0.0) / 100.0)), 6)
        candidates.append(
            {
                'template_id': entry['template_id'],
                'organism': entry['organism'],
                'model': entry['model'],
                'backend': 'diamond',
                'coarse_backend': 'diamond',
                'score': score,
                'coarse_score': score,
                'primary_metric': hit_coverage,
                'secondary_metric': mean_identity or 0.0,
                'coarse_primary_metric': hit_coverage,
                'coarse_secondary_metric': mean_identity or 0.0,
                'ani': None,
                'aligned_fraction': None,
                'aligned_fraction_ref': None,
                'aligned_fraction_query': None,
                'matched_queries': matched_queries,
                'total_queries': total_queries,
                'hit_coverage': round(hit_coverage, 6),
                'mean_identity': round(mean_identity, 6) if mean_identity is not None else None,
                'mean_bitscore': round(mean_bitscore, 6) if mean_bitscore is not None else None,
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
        )

    return candidates


def rerank_templates_with_bbh(run_ns, io_ns, candidates, catalog):
    topn = max(0, int(getattr(run_ns, 'template_rerank_topn', 3)))
    if topn == 0 or not io_ns.targetGenome_locusTag_aaSeq_dict:
        return candidates

    catalog_by_id = {entry['template_id']: entry for entry in catalog}
    ranked = sorted(
        candidates,
        key=lambda item: (
            -float(item.get('score', 0.0)),
            -float(item.get('primary_metric', 0.0)),
            -float(item.get('secondary_metric', 0.0)),
            item['template_id'],
        ),
    )

    for index, candidate in enumerate(ranked, start=1):
        candidate['coarse_rank'] = index

    rerank_candidates = ranked[:topn]
    if not rerank_candidates:
        return candidates

    target_fasta = prepare_target_proteome_fasta(io_ns, ensure_tmp_template_dir(io_ns))
    for candidate in rerank_candidates:
        template_entry = catalog_by_id.get(candidate['template_id'])
        if template_entry is None:
            continue
        metrics = compute_bbh_rerank_metrics(io_ns, target_fasta, template_entry)
        candidate['rerank_applied'] = True
        candidate['selection_stage'] = 'coarse+bbh'
        candidate['bbh_pairs'] = metrics['bbh_pairs']
        candidate['bbh_target_hits'] = metrics['bbh_target_hits']
        candidate['bbh_template_gene_count'] = metrics['bbh_template_gene_count']
        candidate['bbh_target_coverage'] = metrics['bbh_target_coverage']
        candidate['bbh_template_coverage'] = metrics['bbh_template_coverage']
        candidate['rerank_score'] = metrics['rerank_score']
        candidate['primary_metric'] = metrics['bbh_template_coverage']
        candidate['secondary_metric'] = metrics['bbh_target_coverage']
        candidate['score'] = round((0.6 * candidate['coarse_score']) + (0.4 * metrics['rerank_score']), 6)

    return ranked


def compute_bbh_rerank_metrics(io_ns, target_fasta, template_entry):
    tmp_dir = ensure_tmp_template_dir(io_ns)
    diamond = utils.locate_executable('diamond')
    if diamond is None:
        raise RuntimeError("diamond executable not found for template BBH reranking")

    target_db = os.path.join(tmp_dir, 'target_rerank_db')
    if not os.path.isfile(target_db + '.dmnd'):
        run_command(
            [diamond, 'makedb', '--in', target_fasta, '-d', target_db],
            "DIAMOND database creation failed for target rerank database",
        )

    template_db = os.path.join(tmp_dir, '%s_rerank_db' % template_entry['template_id'])
    run_command(
        [diamond, 'makedb', '--in', template_entry['proteome_fasta'], '-d', template_db],
        "DIAMOND database creation failed for template '%s'" % template_entry['template_id'],
    )

    forward_output = os.path.join(tmp_dir, '%s_target_vs_template.tsv' % template_entry['template_id'])
    reverse_output = os.path.join(tmp_dir, '%s_template_vs_target.tsv' % template_entry['template_id'])

    run_command(
        [
            diamond,
            'blastp',
            '-d',
            template_db,
            '-q',
            target_fasta,
            '-o',
            forward_output,
            '--evalue',
            '1e-30',
            '--id',
            '30',
            '--max-target-seqs',
            '5',
            '--outfmt',
            '6',
            'qseqid',
            'sseqid',
            'evalue',
            'score',
            'length',
            'pident',
        ],
        "DIAMOND forward BBH search failed for template '%s'" % template_entry['template_id'],
    )
    run_command(
        [
            diamond,
            'blastp',
            '-d',
            target_db,
            '-q',
            template_entry['proteome_fasta'],
            '-o',
            reverse_output,
            '--evalue',
            '1e-30',
            '--id',
            '30',
            '--max-target-seqs',
            '5',
            '--outfmt',
            '6',
            'qseqid',
            'sseqid',
            'evalue',
            'score',
            'length',
            'pident',
        ],
        "DIAMOND reverse BBH search failed for template '%s'" % template_entry['template_id'],
    )

    best_hits_forward = makeBestHits_dict(forward_output)
    best_hits_reverse = makeBestHits_dict(reverse_output)
    homology_ns = SimpleNamespace()
    getBBH(best_hits_forward, best_hits_reverse, homology_ns)

    template_gene_count = count_fasta_records(template_entry['proteome_fasta'])
    target_gene_count = max(1, len(io_ns.targetGenome_locusTag_aaSeq_dict))
    bbh_pairs = len(getattr(homology_ns, 'temp_target_BBH_dict', {}))
    bbh_target_hits = len(getattr(homology_ns, 'targetBBH_list', []))
    bbh_template_coverage = round(bbh_pairs / float(max(1, template_gene_count)), 6)
    bbh_target_coverage = round(bbh_target_hits / float(target_gene_count), 6)
    rerank_score = round((0.7 * bbh_template_coverage) + (0.3 * bbh_target_coverage), 6)

    return {
        'bbh_pairs': bbh_pairs,
        'bbh_target_hits': bbh_target_hits,
        'bbh_template_gene_count': template_gene_count,
        'bbh_template_coverage': bbh_template_coverage,
        'bbh_target_coverage': bbh_target_coverage,
        'rerank_score': rerank_score,
    }


def count_fasta_records(path):
    count = 0
    for _record in SeqIO.parse(path, 'fasta'):
        count += 1
    return count


def parse_diamond_template_hits(path):
    best_hits = {}
    with open(path, 'r') as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            query_id, bitscore, identity = line.split('\t')
            bitscore = float(bitscore)
            identity = float(identity)
            previous = best_hits.get(query_id)
            if previous is None or bitscore > previous[0]:
                best_hits[query_id] = (bitscore, identity)

    if not best_hits:
        return 0, None, None

    bit_scores = [values[0] for values in best_hits.values()]
    identities = [values[1] for values in best_hits.values()]
    return len(best_hits), mean(bit_scores), mean(identities)


def parse_skani_output(path):
    with open(path, 'r', newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        return list(reader)


def infer_template_id_from_path(path, catalog):
    if not path:
        return None
    normalized = os.path.normcase(os.path.abspath(path))
    for entry in catalog:
        genome_fasta = entry.get('genome_fasta')
        if genome_fasta and normalized == os.path.normcase(os.path.abspath(genome_fasta)):
            return entry['template_id']
    return None


def get_template_metadata(template_id, catalog):
    for entry in catalog:
        if entry['template_id'] == template_id:
            return entry
    return {}


def normalize_ani(value):
    if value is None:
        return 0.0
    return max(0.0, min(1.0, (value - 80.0) / 15.0))


def safe_float(value):
    if value in (None, ''):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def classify_recommendation_confidence(candidates):
    if not candidates:
        return 'low'
    if len(candidates) == 1:
        return 'high'

    score_gap = float(candidates[0].get('score', 0.0)) - float(candidates[1].get('score', 0.0))
    top_score = float(candidates[0].get('score', 0.0))

    if top_score >= 0.85 and score_gap >= 0.10:
        return 'high'
    if top_score >= 0.60 and score_gap >= 0.03:
        return 'medium'
    return 'low'


def write_template_recommendation_outputs(folder, result):
    os.makedirs(folder, exist_ok=True)
    write_template_candidates_tsv(folder, result)
    with open(os.path.join(folder, 'template_recommendation.json'), 'w') as handle:
        json.dump(result, handle, indent=2, sort_keys=True)


def write_template_candidates_tsv(folder, result):
    fields = [
        'rank',
        'template_id',
        'organism',
        'model',
        'backend',
        'score',
        'primary_metric',
        'secondary_metric',
        'coarse_backend',
        'coarse_score',
        'coarse_primary_metric',
        'coarse_secondary_metric',
        'coarse_rank',
        'rerank_applied',
        'rerank_score',
        'bbh_pairs',
        'bbh_target_hits',
        'bbh_template_gene_count',
        'bbh_template_coverage',
        'bbh_target_coverage',
        'selection_stage',
        'ani',
        'aligned_fraction',
        'aligned_fraction_ref',
        'aligned_fraction_query',
        'matched_queries',
        'total_queries',
        'hit_coverage',
        'mean_identity',
        'mean_bitscore',
    ]
    with open(os.path.join(folder, 'template_candidates.tsv'), 'w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter='\t')
        writer.writeheader()
        for rank, candidate in enumerate(result['candidates'], start=1):
            row = dict(candidate)
            row['rank'] = rank
            writer.writerow(row)


def ensure_tmp_template_dir(io_ns):
    tmp_dir = os.path.join(io_ns.outputfolder6, 'auto_template')
    os.makedirs(tmp_dir, exist_ok=True)
    return tmp_dir


def run_command(command, failure_message):
    out, err, retcode = utils.execute(command)
    if retcode != 0:
        stdout = out.decode('utf-8', errors='replace') if isinstance(out, bytes) else str(out)
        stderr = err.decode('utf-8', errors='replace') if isinstance(err, bytes) else str(err)
        raise RuntimeError("%s\nSTDOUT:\n%s\nSTDERR:\n%s" % (failure_message, stdout, stderr))
